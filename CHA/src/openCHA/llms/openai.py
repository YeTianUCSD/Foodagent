from typing import Any, Dict, List, Optional, Union, Set, ClassVar
from pathlib import Path
import base64
import mimetypes

from openCHA.llms import BaseLLM
from openCHA.utils import get_from_dict_or_env
from pydantic import model_validator


class OpenAILLM(BaseLLM):
    """
    **Description:**
        An implementation of the OpenAI APIs. `OpenAI API <https://platform.openai.com/docs/libraries>`_

    Added:
        - images param: accept URL or local file path to build multimodal prompts
        - system_prompt: optional system instruction
        - image_detail: 'low' | 'high' | 'auto' (default 'auto')
    """

    models: ClassVar[Dict[str, int]] = {
        "gpt-4o": 8192,
        "gpt-4o-mini": 8192,
        "gpt-4-0314": 8192,
        "gpt-4-0613": 8192,
        "gpt-4-32k": 32768,
        "gpt-4-32k-0314": 32768,
        "gpt-4-32k-0613": 32768,
        "gpt-3.5-turbo": 4096,
        "gpt-3.5-turbo-0301": 4096,
        "gpt-3.5-turbo-0613": 4096,
        "gpt-3.5-turbo-16k": 16385,
        "gpt-3.5-turbo-1106": 16385,
        "gpt-3.5-turbo-16k-0613": 16385,
        "text-ada-001": 2049,
        "ada": 2049,
        "text-babbage-001": 2040,
        "babbage": 2049,
        "text-curie-001": 2049,
        "curie": 2049,
        "davinci": 2049,
        "text-davinci-003": 4097,
        "text-davinci-002": 4097,
        "code-davinci-002": 8001,
        "code-davinci-001": 8001,
        "code-cushman-002": 2048,
        "code-cushman-001": 2048,
    }

   
    vision_models: ClassVar[Set[str]] = {"gpt-4o", "gpt-4o-mini"}

    api_key: str = ""
    llm_model: Any = None
    max_tokens: int = 150

    def _prepare_prompt(self, prompt: str) -> Any:
        """
        Backward-compatible text-only message builder required by BaseLLM.
        Returns a single system message, matching the original behavior.
        """
        return [{"role": "system", "content": prompt}]


    @model_validator(mode="before")
    def validate_environment(cls, values: Dict) -> Dict:
        """
        Validate that API key and python package exist in the environment.
        """
        openai_api_key = get_from_dict_or_env(
            values, "openai_api_key", "OPENAI_API_KEY"
        )
        values["api_key"] = openai_api_key
        try:
            from openai import OpenAI
            values["llm_model"] = OpenAI()
        except ImportError:
            raise ValueError(
                "Could not import openai python package. "
                "Please install it with `pip install openai`."
            )
        return values

    def get_model_names(self) -> List[str]:
        return list(self.models.keys())

    def is_max_token(self, model_name, query) -> bool:
        """
        Token estimation for text prompts. When images are included,
        this check is skipped (images are not tokenized via tiktoken).
        """
        model_max_token = self.models[model_name]
        try:
            import tiktoken
        except ImportError:
            raise ValueError(
                "Could not import tiktoken python package. "
                "This is needed in order to calculate get_num_tokens. "
                "Please install it with `pip install tiktoken`."
            )
        encoder = "gpt2"
        if model_name in ("text-davinci-003", "text-davinci-002") or model_name.startswith("code"):
            encoder = "p50k_base"

        enc = tiktoken.get_encoding(encoder)
        tokenized_text = enc.encode(query)
        return model_max_token < len(tokenized_text)

    def _parse_response(self, response) -> str:
        return response.choices[0].message.content

    # ---------- Helpers for image handling and message construction ----------
    def _file_to_data_url(self, path: Union[str, Path]) -> str:
        """Convert a local image file to a data URL with inferred MIME type."""
        p = Path(path)
        if not p.exists() or not p.is_file():
            raise ValueError(f"Image path not found: {path}")
        mime, _ = mimetypes.guess_type(p.name)
        if not mime:
            # Default to PNG if MIME cannot be inferred
            mime = "image/png"
        data = p.read_bytes()
        b64 = base64.b64encode(data).decode("utf-8")
        return f"data:{mime};base64,{b64}"

    def _build_image_content(
        self,
        images: List[Union[str, Path]],
        detail: str = "auto",
    ) -> List[Dict[str, Any]]:
        """
        Normalize URL / local file paths into the image_url structure
        required by chat.completions.
        """
        contents: List[Dict[str, Any]] = []
        for img in images:
            if isinstance(img, (str, Path)):
                s = str(img)
                if s.startswith("http://") or s.startswith("https://") or s.startswith("data:"):
                    url = s
                else:
                    url = self._file_to_data_url(s)
            else:
                raise ValueError("Each image must be a URL string or local file path/Path.")
            contents.append(
                {
                    "type": "image_url",
                    "image_url": {"url": url, "detail": detail},
                }
            )
        return contents

    def _prepare_messages(
        self,
        prompt: str,
        images: Optional[List[Union[str, Path]]] = None,
        system_prompt: Optional[str] = None,
        image_detail: str = "auto",
    ) -> List[Dict[str, Any]]:
        """
        Build messages depending on whether images are included.
        - Text only: keep backward compatibility (single system message).
        - Text + images: use user message with multimodal content array.
        """
        if images:
            content: List[Dict[str, Any]] = [{"type": "text", "text": prompt}]
            content.extend(self._build_image_content(images, image_detail))
            messages: List[Dict[str, Any]] = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": content})
            return messages
        else:
            # Preserve original behavior for text-only (single system message)
            return [{"role": "system", "content": prompt}]

    # ---------- Public API ----------
    def generate(
        self,
        query: str,
        **kwargs: Any,
    ) -> str:
        """
        Generate a response.

        New optional kwargs:
            images: List[str | Path]  # image URLs or local paths
            system_prompt: str        # optional system instruction
            image_detail: str         # 'low' | 'high' | 'auto' (default 'auto')
        """
        model_name = kwargs.get("model_name", "gpt-4o")
        if model_name not in self.get_model_names():
            raise ValueError(
                "model_name is not specified or OpenAI does not support provided model_name"
            )

        images = kwargs.get("images")
        system_prompt = kwargs.get("system_prompt")
        image_detail = kwargs.get("image_detail", "auto")

        # If images are provided but model does not support vision, fail early
        if images and model_name not in self.vision_models:
            raise ValueError(
                f"Model '{model_name}' does not support image understanding. "
                f"Please use one of: {sorted(self.vision_models)}"
            )

        stop = kwargs.get("stop")
        max_tokens = kwargs.get("max_tokens", self.max_tokens)

        # For text-only prompts, optionally enforce token limit check
        # (skip when images are present, because tiktoken doesn't count images)
        if not images:
            try:
                if self.is_max_token(model_name, query):
                    raise ValueError(
                        f"Your prompt exceeds the max token limit for model '{model_name}'."
                    )
            except Exception:
                # Do not block the call if tiktoken isn't available
                pass

        self.llm_model.api_key = self.api_key
        messages = self._prepare_messages(
            prompt=query,
            images=images,
            system_prompt=system_prompt,
            image_detail=image_detail,
        )

        response = self.llm_model.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=max_tokens,
            stop=stop,
        )
        return self._parse_response(response)
