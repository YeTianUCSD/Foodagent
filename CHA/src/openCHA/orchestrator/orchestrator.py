from __future__ import annotations

from ast import Continue
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from openCHA.CustomDebugFormatter import CustomDebugFormatter
from openCHA.datapipes import DataPipe
from openCHA.datapipes import DatapipeType
from openCHA.datapipes import initialize_datapipe
from openCHA.llms import LLMType
from openCHA.orchestrator import Action
from openCHA.planners import BasePlanner
from openCHA.planners import initialize_planner
from openCHA.planners import PlanFinish
from openCHA.planners import PlannerType
from openCHA.response_generators import (
    BaseResponseGenerator,
)
from openCHA.response_generators import (
    initialize_response_generator,
)
from openCHA.response_generators import (
    ResponseGeneratorType,
)
from openCHA.tasks import BaseTask
from openCHA.tasks import initialize_task
from openCHA.tasks import TaskType
from pydantic import BaseModel
import re

class Orchestrator(BaseModel):
    """
    **Description:**

        The Orchestrator class is the main execution heart of the CHA. All the components of the Orchestrator are initialized and executed here.
        The Orchestrator will start a new answering cycle by calling the `run` method. From there, the planning is started,
        then tasks will be executed one by one till the **Task Planner** decides that no more information is needed.
        Finally the **Task Planner** final answer will be routed to the **Final Response Generator** to generate an empathic final
        response that is returned to the user.
    """

    planner: BasePlanner = None
    datapipe: DataPipe = None
    promptist: Any = None
    response_generator: BaseResponseGenerator = None
    available_tasks: Dict[str, BaseTask] = {}
    max_retries: int = 5
    max_task_execute_retries: int = 3
    max_planner_execute_retries: int = 16
    max_final_answer_execute_retries: int = 3
    role: int = 0
    verbose: bool = False
    planner_logger: Optional[logging.Logger] = None
    tasks_logger: Optional[logging.Logger] = None
    orchestrator_logger: Optional[logging.Logger] = None
    final_answer_generator_logger: Optional[logging.Logger] = None
    promptist_logger: Optional[logging.Logger] = None
    error_logger: Optional[logging.Logger] = None
    previous_actions: List[str] = []
    current_actions: List[Optional[Action]] = []
    current_actions_inputs: str = ""
    current_failed_actions: List[str] = []
    current_failed_actions_inputs: List[str] = []
    succeed_inputs: List[str] = []
    succeed_actions: List[str] = []
    runtime: Dict[str, bool] = {}
    strategy: str = ""
    vars: Dict[str, Any] = {}

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    def print_log(self, log_name: str, message: str):
        if self.verbose:
            if log_name == "planner":
                self.planner_logger.debug(message)
            if log_name == "task":
                self.tasks_logger.debug(message)
            if log_name == "orchestrator":
                self.orchestrator_logger.debug(message)
            if log_name == "response_generator":
                self.final_answer_generator_logger.debug(message)
            if log_name == "promptist":
                self.promptist_logger.debug(message)
            if log_name == "error":
                self.error_logger.debug(message)

    @classmethod
    def initialize(
        self,
        planner_llm: str = LLMType.OPENAI,
        planner_name: str = PlannerType.ZERO_SHOT_REACT_PLANNER,
        datapipe_name: str = DatapipeType.MEMORY,
        promptist_name: str = "",
        response_generator_llm: str = LLMType.OPENAI,
        response_generator_name: str = ResponseGeneratorType.BASE_GENERATOR,
        available_tasks: Optional[List[str]] = None,
        previous_actions: List[Action] = None,
        verbose: bool = False,
        **kwargs,
    ) -> Orchestrator:
        """
            This class method initializes the Orchestrator by setting up the planner, datapipe, promptist, response generator,
            and available tasks.

        Args:
            planner_llm (str): LLMType to be used as LLM for planner.
            planner_name (str): PlannerType to be used as task planner.
            datapipe_name (str): DatapipeType to be used as data pipe.
            promptist_name (str): Not implemented yet!
            response_generator_llm (str): LLMType to be used as LLM for response generator.
            response_generator_name (str): ResponseGeneratorType to be used as response generator.
            available_tasks (List[str]): List of available task using TaskType.
            previous_actions (List[Action]): List of previous actions.
            verbose (bool): Specifies if the debugging logs be printed or not.
            **kwargs (Any): Additional keyword arguments.
        Return:
            Orchestrator: Initialized Orchestrator instance.



        Example:
            .. code-block:: python

                from openCHA.datapipes import DatapipeType
                from openCHA.planners import PlannerType
                from openCHA.response_generators import ResponseGeneratorType
                from openCHA.tasks import TaskType
                from openCHA.llms import LLMType
                from openCHA.orchestrator import Orchestrator

                orchestrator = Orchestrator.initialize(
                    planner_llm=LLMType.OPENAI,
                    planner_name=PlannerType.ZERO_SHOT_REACT_PLANNER,
                    datapipe_name=DatapipeType.MEMORY,
                    promptist_name="",
                    response_generator_llm=LLMType.OPENAI,
                    response_generator_name=ResponseGeneratorType.BASE_GENERATOR,
                    available_tasks=[TaskType.SERPAPI, TaskType.EXTRACT_TEXT],
                    verbose=self.verbose,
                    **kwargs
                )

        """
        if available_tasks is None:
            available_tasks = []
        if previous_actions is None:
            previous_actions = []

        planner_logger = (
            tasks_logger
        ) = (
            orchestrator_logger
        ) = (
            final_answer_generator_logger
        ) = promptist_logger = error_logger = None
        if verbose:
            planner_logger = CustomDebugFormatter.create_logger(
                "Planner", "cyan"
            )
            tasks_logger = CustomDebugFormatter.create_logger(
                "Task", "purple"
            )
            orchestrator_logger = CustomDebugFormatter.create_logger(
                "Orchestrator", "green"
            )
            final_answer_generator_logger = (
                CustomDebugFormatter.create_logger(
                    "Response Generator", "blue"
                )
            )
            promptist_logger = CustomDebugFormatter.create_logger(
                "Promptist", "blue"
            )
            error_logger = CustomDebugFormatter.create_logger(
                "Error", "red"
            )

        datapipe = initialize_datapipe(
            datapipe=datapipe_name, **kwargs
        )
        if verbose:
            orchestrator_logger.debug(
                f"Datapipe {datapipe_name} is successfully initialized.\n"
            )

        tasks = {}
        for task in available_tasks:
            kwargs["datapipe"] = datapipe
            tasks[task] = initialize_task(task=task, **kwargs)
            if verbose:
                orchestrator_logger.debug(
                    f"Task '{task}' is successfully initialized."
                )

        planner = initialize_planner(
            tasks=list(tasks.values()),
            llm=planner_llm,
            planner=planner_name,
            **kwargs,
        )
        if verbose:
            orchestrator_logger.debug(
                f"Planner {planner_name} is successfully initialized."
            )

        response_generator = initialize_response_generator(
            response_generator=response_generator_name,
            llm=response_generator_llm,
            **kwargs,
        )
        if verbose:
            orchestrator_logger.debug(
                f"Response Generator {response_generator_name} is successfully initialized."
            )

        return self(
            planner=planner,
            datapipe=datapipe,
            promptist=None,
            response_generator=response_generator,
            available_tasks=tasks,
            verbose=verbose,
            previous_actions=previous_actions,
            current_failed_actions=[],
            current_failed_actions_inputs=[],
            succeed_actions=[],
            current_action=None,
            current_actions_inputs="",
            planner_logger=planner_logger,
            tasks_logger=tasks_logger,
            succeed_inputs = [], 
            orchestrator_logger=orchestrator_logger,
            final_answer_generator_logger=final_answer_generator_logger,
            promptist_logger=promptist_logger,
            error_logger=error_logger,
        )

    def process_meta(self) -> bool:
        """
            This method processes the meta information and returns a boolean value. Currently, it always returns False.

        Return:
            bool: False

        """
        return False

    def _update_runtime(self, action: Action = None):
        if action.output_type:
            self.runtime[action.task_response] = False
        for task_input in action.task_inputs:
            if task_input in self.runtime:
                self.runtime[task_input] = True

    def execute_task(
        self, task_name: str, task_inputs: List[str]
    ) -> Any:
        """
            Execute the specified task based on the planner's selected **Action**. This method executes a specific task based on the provided action.
            It takes an action as input and retrieves the corresponding task from the available tasks dictionary.
            It then executes the task with the given task input. If the task has an output_type, it stores the result in the datapipe and returns
            a message indicating the storage key. Otherwise, it returns the result directly.

        Args:
            task_name (str): The name of the Task.
            task_inputs List(str): The list of the inputs for the task.
        Return:
            str: Result of the task execution.
            bool: If the task result should be directly returned to the user and stop planning.
        """
        self.print_log(
            "task",
            f"---------------\nExecuting task:\nTask Name: {task_name}\nTask Inputs: {task_inputs}\n",
        )
        error_message = ""

        try:
            task = self.available_tasks[task_name]
            result = task.execute(task_inputs)
            self.print_log(
                "task",
                f"Task is executed successfully\nResult: {result}\n---------------\n",
            )
            action = Action(
                task_name=task_name,
                task_inputs=task_inputs,
                task_response=result,
                output_type=task.output_type,
                datapipe=self.datapipe,
            )

            self._update_runtime(action)

            # self.previous_actions.append(action) move to parse evaluation response
            # self.succeed_actions.append(action)
            self.current_actions.append(action)
            return result  # , task.return_direct
        except Exception as e:  # return the exception message and store as the current action
            self.print_log(
                "error",
                f"Error running task: \n{e}\n---------------\n",
            )
            logging.exception(e)
            error_message = e
            action = Action(
                task_name=task_name,
                task_inputs=task_inputs,
                task_response=error_message,
                output_type=False,
                datapipe=self.datapipe,
            )
            self.current_actions.append(action)
            return error_message
            # raise ValueError(
            #     f"Error executing task {task_name}: {error_message}\n\nTry again with different inputs."
            # )
            
    def parse_evaluation_response_and_update_current_action(
        self,
        response: str
    ) -> tuple[bool, bool, bool, str]:   # (strategy_change, step_success, strategy_complete, content)
        """
        Parse an LLM evaluation reply produced with the four-section format:

            [STRATEGY_CHANGE] yes|no
            [STEP_SUCCESS] yes|no
            [CONTENT]
            <free-form text or ```python``` block>

        Returns:
            strategy_change   (bool)
            step_success      (bool)
            content           (str)  - raw text of the [CONTENT] section

        Side effect:
            Stores the [CONTENT] block in self.current_action (create the
            attribute if it does not yet exist).
        """
        print("\n============================start of response========================================\n")
        print(response)
        print("\n============================end of response========================================\n")
        # ---- 1. Normalise “[TAG]: value”  →  “[TAG] value” ------------------
        cleaned = re.sub(
            r"\[(STRATEGY_CHANGE|STEP_SUCCESS|CONTENT)]\s*[-:]\s*",
            lambda m: f"[{m.group(1)}] ",
            response,
            flags=re.IGNORECASE,
        )

        # 2️⃣  Grab each block: everything up to the next tag or end of string
        block_re = re.compile(
            r"\[(STRATEGY_CHANGE|STEP_SUCCESS|CONTENT)]"
            r"([\s\S]*?)(?=\n\s*\[(?:STRATEGY_CHANGE|STEP_SUCCESS|STRATEGY_COMPLETE|CONTENT)]|$)",
            re.IGNORECASE,
        )
        sections = {m.group(1).upper(): m.group(2).strip() for m in block_re.finditer(cleaned)}


        expected = {"STRATEGY_CHANGE", "STEP_SUCCESS", "CONTENT"}
        flag = False
        for key in expected:
            if key not in sections:
                if key == "CONTENT":
                    flag = True
                else:
                    return False, False, False
        # missing = expected - sections.keys()
        # if missing:
        #     return False, False, False
            # raise ValueError(f"Missing tag(s) in response: {', '.join(sorted(missing))}")

        def to_bool(txt: str) -> bool:
            txt = txt.lower().strip().split()[0]
            if txt == "yes":
                return True
            if txt == "no":
                return False
            # return False
            raise ValueError(f"Expected 'yes' or 'no', got: {txt!r}")

        strategy_change   = to_bool(sections["STRATEGY_CHANGE"])
        step_success      = to_bool(sections["STEP_SUCCESS"])
        if flag:
            return strategy_change, step_success, ""
        # strategy_complete = to_bool(sections["STRATEGY_COMPLETE"])

        # ---- 3. Pull only the first ```python``` block from CONTENT ----------
        content_block = sections["CONTENT"]
        print("======content============\n")
        print(content_block)
        match = re.search(r"```python([\s\S]*?)``?", content_block, re.IGNORECASE)
        # content = f"```python{match.group(1)}```" if match else ""
        content = match.group(1)

        # ---- 4. Persist + return --------------------------------------------
        # self.current_actions_inputs = content
        return strategy_change, step_success, content


    def planner_generate_prompt(self, query) -> str:
        """
            Generate a prompt from the query to make it more understandable for both planner and response generator.
            Not implemented yet.

        Args:
                query (str): Input query.
        Return:
                str: Generated prompt.

        """
        return query

    def _prepare_planner_response_for_response_generator(self):
        print("runtime", self.runtime)
        final_response = ""
        print(len(self.succeed_actions))
        if len(self.succeed_actions) == 0:
            return ""
        for action in self.succeed_actions:
            final_response += action.dict(
                (
                    action.output_type
                    and not self.runtime[action.task_response]
                )
            )
        return final_response

    def response_generator_generate_prompt(
        self,
        final_response: str = "",
        history: str = "",
        meta: List[str] = None,
        use_history: bool = False,
    ) -> str:
        if meta is None:
            meta = []

        prompt = "MetaData: {meta}\n\nHistory: \n{history}\n\n"
        if use_history:
            prompt = prompt.replace("{history}", history)

        prompt = (
            prompt.replace("{meta}", ", ".join(meta))
            + f"\n{final_response}"
        )
        return prompt

    # def plan(
    #     self, query, history, meta, use_history, **kwargs
    # ) -> str:
    #     """
    #         Plan actions based on the query, history, and previous actions using the selected planner type.
    #         This method generates a plan of actions based on the provided query, history, previous actions, and use_history flag.
    #         It calls the plan method of the planner and returns a list of actions or plan finishes.

    #     Args:
    #         query (str): Input query.
    #         history (str): History information.
    #         meta (Any): meta information.
    #         use_history (bool): Flag indicating whether to use history.
    #     Return:
    #         str: A python code block will be returnd to be executed by Task Executor.

    #     """
    #     return self.planner.plan(
    #         query,
    #         history,
    #         meta,
    #         self.previous_actions,
    #         use_history,
    #         **kwargs,
    #     )

    def generate_final_answer(self, query, thinker, **kwargs) -> str:
        """
            Generate the final answer using the response generator.
            This method generates the final answer based on the provided query and thinker.
            It calls the generate method of the response generator and returns the generated answer.

        Args:
            query (str): Input query.
            thinker (str): Thinking component.
        Return:
            str: Final generated answer.

        """

        retries = 0
        while retries < self.max_final_answer_execute_retries:
            try:
                prefix = (
                    kwargs["response_generator_prefix_prompt"]
                    if "response_generator_prefix_prompt" in kwargs
                    else ""
                )
                return self.response_generator.generate(
                    query=query,
                    thinker=thinker,
                    prefix=prefix,
                    **kwargs,
                )
            except Exception as e:
                print(e)
                retries += 1
        return "We currently have problem processing your question. Please try again after a while."

    def run(
        self,
        query: str,
        meta: List[str] = None,
        history: str = "",
        use_history: bool = False,
        **kwargs: Any,
    ) -> str:
        """
            This method runs the orchestrator by taking a query, meta information, history, and other optional keyword arguments as input.
            It initializes variables for tracking the execution, generates a prompt based on the query, and sets up a loop for executing actions.
            Within the loop, it plans actions, executes tasks, and updates the previous actions list.
            If a PlanFinish action is encountered, the loop breaks, and the final response is set.
            If any errors occur during execution, the loop retries a limited number of times before setting a final error response.
            Finally, it generates the final response using the prompt and thinker, and returns the final response along with the previous actions.

        Args:
            query (str): Input query.
            meta (List[str]): Meta information.
            history (str): History information.
            use_history (bool): Flag indicating whether to use history.
            **kwargs (Any): Additional keyword arguments.
        Return:
            str: The final response to shown to the user.


        """
        if meta is None:
            meta = []
        i = 0
        meta_infos = ""
        for meta_data in meta:
            key = self.datapipe.store(meta_data)
            meta_infos += (
                f"The file with the name ${meta_data.split('/')[-1]}$ is stored with the key $datapipe:{key}$."
                "Pass this key to the tools when you want to send them over to the tool\n"
            )
        prompt = self.planner_generate_prompt(query)
        if "google_translate" in self.available_tasks:
            prompt = self.available_tasks["google_translate"].execute(
                [prompt, "en"]
            )
            source_language = prompt[1]
            prompt = prompt[0]
        # history = self.available_tasks["google_translate"].execute(history+"$#en").text
        final_response = ""
        finished = False
        self.print_log("planner", "Planning Started...\n")
        strategy = self.planner.plan_strategy(  # should separate plan to 2 parts, first get the strategy, second generate code
            query=prompt,
            history=history,
            meta=meta_infos,
            use_history=use_history,
            **kwargs,
        )
        with open("./log/logger.txt", mode="a", encoding="utf-8") as f:
            f.write("\n==========================================first strategy start================================================\n")
            f.write(strategy)
            f.write("\n==========================================first strategy end================================================\n")
        times = 0
        while True:  # keep running until finished planning
            if times>10:
                self.succeed_actions.extend(self.current_actions)
                self.succeed_inputs.append(self.current_actions_inputs)
                break
            times+=1
            with open("./log/logger.txt", mode="a", encoding="utf-8") as f:
                f.write(f"==================attempt {times} ==============================")
            response = self.planner.plan_evaluation(
                query=prompt, 
                strategy=strategy, 
                current_action = self.current_actions, 
                current_action_input=self.current_actions_inputs, 
                current_failed_actions=self.current_failed_actions, 
                current_failed_actions_inputs=self.current_failed_actions_inputs, 
                previous_inputs=self.succeed_inputs,
                previous_actions=self.succeed_actions
            )
            strategy_change, step_success, content = self.parse_evaluation_response_and_update_current_action(response)
            if content is False:
                continue
            if times == 1:
                strategy_change = False
                step_success = False
            if step_success:
                assert strategy_change is False
                self.succeed_actions.extend(self.current_actions)
                self.succeed_inputs.append(self.current_actions_inputs)
                break
            if strategy_change:
                strategy = content
            else:  # failed
                # content = self.planner.parse(content)
                self.current_failed_actions.append(self.current_actions)
                self.current_failed_actions_inputs.append(self.current_actions_inputs)
                self.current_actions_inputs = content
                self.current_actions = []
                try:
                    exec(content, locals(), self.vars)
                except (Exception, SystemExit) as error:
                    self.current_actions.append("action initialze failed, error message: " + str(error) + '\n')
        
        
        print("reach to final response")
        final_response = (  # move to the end
            self._prepare_planner_response_for_response_generator()
        )
        print(final_response)
        self.print_log(
            "planner",
            f"Planner final response: {final_response}\nPlanning Ended...\n\n",
        )
        self.previous_actions.extend(self.succeed_actions)

        final_response = self.response_generator_generate_prompt(
            final_response=final_response,
            history=history,
            meta=meta_infos,
            use_history=use_history,
        )

        self.print_log(
            "response_generator",
            f"Final Answer Generation Started...\nInput Prompt: \n\n{final_response}",
        )
        final_response = self.generate_final_answer(
            query=query, thinker=final_response, **kwargs
        )
        self.print_log(
            "response_generator",
            f"Response: {final_response}\n\nFinal Answer Generation Ended.\n",
        )

        if "google_translate" in self.available_tasks:
            final_response = self.available_tasks[
                "google_translate"
            ].execute([final_response, source_language])[0]

        return final_response
