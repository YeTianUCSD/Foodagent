import os
from typing import List
from typing import Tuple
from typing import Optional

from openCHA.datapipes import DatapipeType
from openCHA.interface import Interface
from openCHA.llms import LLMType
from openCHA.orchestrator import Orchestrator
from openCHA.planners import Action
from openCHA.planners import PlannerType
from openCHA.response_generators import (
    ResponseGeneratorType,
)
from openCHA.tasks import TASK_TO_CLASS
from openCHA.tasks import TaskType
from openCHA.utils import parse_addresses
from pydantic import BaseModel


class openCHA(BaseModel):
    name: str = "openCHA"
    previous_actions: List[Action] = []
    orchestrator: Optional[Orchestrator] = None
    planner_llm: str = LLMType.OPENAI
    planner: str = PlannerType.TREE_OF_THOUGHT_STEP
    datapipe: str = DatapipeType.MEMORY
    promptist: str = ""
    response_generator_llm: str = LLMType.OPENAI
    response_generator: str = ResponseGeneratorType.BASE_GENERATOR
    meta: List[str] = []
    verbose: bool = False

    def _generate_history(
        self, chat_history: Optional[List[Tuple[str, str]]] = None
    ) -> str:
        if chat_history is None:
            chat_history = []

        history = "".join(
            [
                f"\n------------\nUser: {chat[0]}\nCHA: {chat[1]}\n------------\n"
                for chat in chat_history
            ]
        )
        return history

    def _run(
        self,
        query: str,
        chat_history: Optional[List[Tuple[str, str]]] = None,
        tasks_list: Optional[List[str]] = None,
        use_history: bool = False,
        **kwargs,
    ) -> str:
        if chat_history is None:
            chat_history = []
        if tasks_list is None:
            tasks_list = []

        history = self._generate_history(chat_history=chat_history)
        # query += f"User: {message}"
        # print(orchestrator.run("what is the name of the girlfriend of Leonardo Dicaperio?"))

        if self.orchestrator is None:
            self.orchestrator = Orchestrator.initialize(
                planner_llm=self.planner_llm,
                planner_name=self.planner,
                datapipe_name=self.datapipe,
                promptist_name=self.promptist,
                response_generator_llm=self.response_generator_llm,
                response_generator_name=self.response_generator,
                available_tasks=tasks_list,
                previous_actions=self.previous_actions,
                verbose=self.verbose,
                **kwargs,
            )

        response = self.orchestrator.run(
            query=query,
            meta=self.meta,
            history=history,
            use_history=use_history,
            **kwargs,
        )

        return response

    def respond(
        self,
        message,
        openai_api_key_input,
        serp_api_key_input,
        chat_history: Optional[List[Tuple[str, str]]],
        check_box,
        tasks_list: Optional[List[str]],
    ):
        """
        Handle user input for both text and image.

        Priority:
          1) If there is an uploaded image recorded in self.meta, send BOTH the user's text (question)
             and the image (as a data URL) to GPT-4o.
          2) Else if the message contains an image URL (http/https/data), send both text and image URL.
          3) Else if the message contains a local image path, convert to data URL and send both.
          4) Otherwise, use the default orchestrator pipeline.

        Notes:
          - OpenAI servers cannot access local files via file://. I convert local files to data URLs.
          - Gradio uploads store a temp file path in `file.name`; upload_meta() appends that to self.meta.
        """
        import os
        import re
        import base64
        import mimetypes
        import openai
        from typing import Optional

        if chat_history is None:
            chat_history = []
        if tasks_list is None:
            tasks_list = []

        # Preserve the original behavior for env vars
        os.environ["OPENAI_API_KEY"] = openai_api_key_input
        os.environ["SEPR_API_KEY"] = serp_api_key_input  # (typo kept to match existing code)

        # ---------- helpers ----------
        def extract_url(text: str) -> Optional[str]:
            """Return the first http/https/data image URL found in the text."""
            if not text:
                return None
            m = re.search(r"(https?://\S+|data:image/\w+;base64,[A-Za-z0-9+/=]+)", text, re.IGNORECASE)
            if m:
                return m.group(1).rstrip(').,;\'"')
            return None

        def extract_local_path(text: str) -> Optional[str]:
            """Return a local image path starting at BOL or after whitespace (avoid matching https://...)."""
            if not text:
                return None
            m = re.search(r"(?:(?<=\s)|^)(/[^ \n\t]+\.(?:jpg|jpeg|png|webp|gif|bmp))", text, re.IGNORECASE)
            if m:
                return m.group(1)
            return None

        def to_data_url(local_path: str) -> Optional[str]:
            """Convert a local image file to a data URL; return None if unreadable."""
            try:
                if not os.path.exists(local_path):
                    return None
                mime, _ = mimetypes.guess_type(local_path)
                if mime is None:
                    mime = "image/jpeg"
                with open(local_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                return f"data:{mime};base64,{b64}"
            except Exception:
                return None

        def strip_image_refs(text: str) -> str:
            """Remove URLs and local paths so only the user's question remains."""
            if not text:
                return ""
            t = re.sub(r"https?://\S+", "", text)  # remove URLs
            t = re.sub(r"(?:(?<=\s)|^)(/[^ \n\t]+\.(?:jpg|jpeg|png|webp|gif|bmp))", "", t, flags=re.IGNORECASE)  # remove paths
            return " ".join(t.split()).strip()

        # ---------- gather possible image sources ----------
        text = message or ""
        url_in_text = extract_url(text)
        path_in_text = extract_local_path(text)

        # Also look at recently uploaded files recorded by upload_meta()
        # We will use the *latest* image-looking path if present.
        uploaded_path = None
        if self.meta:
            # take the most recent path that looks like an image file
            for p in reversed(self.meta):
                if isinstance(p, str) and re.search(r"\.(?:jpg|jpeg|png|webp|gif|bmp)$", p, re.IGNORECASE):
                    uploaded_path = p
                    break

        # Build the user's question (text without raw URL/path). If empty, provide a default instruction.
        user_question = strip_image_refs(text)
        if not user_question:
            user_question = "Please answer my question about this image (e.g., healthiness, ingredients, nutrition)."

        client = openai.OpenAI(api_key=openai_api_key_input)

        # ---------- Case 1: Prefer uploaded image (from self.meta) ----------
        if uploaded_path:
            data_url = to_data_url(uploaded_path)
            if data_url is not None:
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",  # or "gpt-4o"
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": f"{user_question}\nAnswer based on the image."},
                                {"type": "image_url", "image_url": {"url": data_url}},
                            ],
                        }
                    ],
                )
                answer = resp.choices[0].message.content
                chat_history.append((f"[Uploaded Image] {uploaded_path}", answer))
                # consume the used path once, to avoid reusing it on the next turn
                try:
                    self.meta.remove(uploaded_path)
                except ValueError:
                    pass
                return "", chat_history
            else:
                # If upload path is unreadable, silently continue to other cases.
                try:
                    self.meta.remove(uploaded_path)
                except ValueError:
                    pass

        # ---------- Case 2: Image URL in text ----------
        if url_in_text:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"{user_question}\nAnswer based on the image."},
                            {"type": "image_url", "image_url": {"url": url_in_text}},
                        ],
                    }
                ],
            )
            answer = resp.choices[0].message.content
            chat_history.append((message, answer))
            return "", chat_history

        # ---------- Case 3: Local image path in text ----------
        if path_in_text:
            data_url = to_data_url(path_in_text)
            if data_url is not None:
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": f"{user_question}\nAnswer based on the image."},
                                {"type": "image_url", "image_url": {"url": data_url}},
                            ],
                        }
                    ],
                )
                answer = resp.choices[0].message.content
                chat_history.append((message, answer))
                return "", chat_history
            # If we couldn't read/encode the file, fall through to text-only pipeline.

        # ---------- Case 4: Default text-only pipeline ----------
        response = self._run(
            query=text,
            chat_history=chat_history,
            tasks_list=tasks_list,
            use_history=check_box,
        )

        files = parse_addresses(response)

        if len(files) == 0:
            chat_history.append((text, response))
        else:
            for i in range(len(files)):
                chat_history.append(
                    (
                        text if i == 0 else "",
                        response[: files[i][1]],
                    )
                )
                chat_history.append(("", str(files[i][0])))
                response = response[files[i][2] :]

        return "", chat_history


    def reset(self):
        self.previous_actions = []

    def run_with_interface(self):
        available_tasks = [key.value for key in TASK_TO_CLASS.keys()]
        interface = Interface()
        interface.prepare_interface(
            respond=self.respond,
            reset=self.reset,
            upload_meta=self.upload_meta,
            available_tasks=available_tasks,
        )

    def upload_meta(self, history, file):
        history = history + [((file.name,), None)]
        self.meta.append(file.name)
        return history

    def run(
        self,
        query: str,
        chat_history: Optional[List[Tuple[str, str]]] = None,
        available_tasks: Optional[List[str]] = None,
        use_history: bool = False,
        **kwargs,
    ) -> str:
        if chat_history is None:
            chat_history = []
        if available_tasks is None:
            available_tasks = []

        return self._run(
            query=query,
            chat_history=chat_history,
            tasks_list=available_tasks,
            use_history=use_history,
            **kwargs,
        )
