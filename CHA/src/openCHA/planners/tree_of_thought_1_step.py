"""
Heavily borrowed from langchain: https://github.com/langchain-ai/langchain/
"""
import re
from typing import Any
from typing import List

from openCHA.planners import Action
from openCHA.planners import BasePlanner
from openCHA.planners import PlanFinish


class TreeOfThoughtStepPlanner(BasePlanner):
    """
    **Description:**

        This class implements Tree of Thought planner, which inherits from the BasePlanner base class.
        Tree of Thought employs parallel chain of thoughts startegies and decides which one is more
        suitable to proceed to get to the final answer.
        `Paper <https://arxiv.org/abs/2305.10601>`_

        This code defines a base class called "BasePlanner" that inherits from the "BaseModel" class of the pydantic library.
        The BasePlanner class serves as a base for implementing specific planners.


    """

    summarize_prompt: bool = True
    max_tokens_allowed: int = 10000

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    @property
    def _planner_type(self):
        return "zero-shot-react-planner"

    @property
    def _planner_model(self):
        return self.llm_model

    @property
    def _response_generator_model(self):
        return self.llm_model

    @property
    def _stop(self) -> List[str]:
        return ["Wait"]

    @property
    def _shorten_prompt(self):
        return (
            "Summarize the following text. Make sure to keep the main ideas "
            "and objectives in the summary. Keep the links "
            "exactly as they are: "
            "{chunk}"
        )

    @property
    def _planner_prompt(self):
        return [
            """As a knowledgeable and empathetic health assistant, your primary objective is to provide the user with precise and valuable \
information regarding their health and well-being. Utilize the available tools effectively to answer health-related queries. \
Here are the tools at your disposal:
{tool_names}

The following is the format of the information provided:
MetaData: this contains the name of data files of different types like image, audio, video, and text. You can pass these files to tools when needed.
History: the history of previous chats happened. Review the history for any previous responses relevant to the current query
PreviousActions: the list of already performed actions. You should start planning knowing that these actions are performed.
Question: the input question you must answer.

Considering previously actions and their results, use the tools and provided information, first suggest three \
creative strategies with detailed explanation consisting of sequences of tools to properly answer the user query. \
Make sure the strategies are comprehensive enough and use proper tools. The tools constraints should be always satisfied. \

After specifying the strategies, mention the pros and cons of each strategy. \
In the end decide the best strategy and write the detailed tool executions step by step.
start your final decision with
'Decision:'. Only **one** decision should appear behind 'Decision:' tag

Begin!

MetaData:
{meta}
=========================
{previous_actions}
=========================
{history}
=========================
USER: {input} \n CHA:
""",
            """
{strategy}
=========================
Completed actions (with results):
{previous_actions}

Result of the most recent step attempt:
{current_attempt_result}

Last attempts that FAILED before the current one (if any):
{previous_step_failed_actions}
=========================
Tools:
{tool_names}
=========================

You are a skilled Python programmer tasked with executing a specific strategy by calling tools.

Your output **must follow the STRICT FORMAT below**. If you fail to follow it, your output will be rejected.

Your response **must contain ONLY the three tagged sections below, in EXACTLY this order**:

[STRATEGY_CHANGE]  
- `yes` if the overall strategy should be redesigned, otherwise `no`.

[STEP_SUCCESS]  
- `yes` if **all goals have been achieved** and **no further tool calls are required**, otherwise `no`.

[CONTENT]  
- If `[STRATEGY_CHANGE] = yes`, provide the **new full strategy** (plain text, no code).  
- If `[STEP_SUCCESS] = yes`, leave this section **empty**.  
- If `[STEP_SUCCESS] = no`, provide the **next Python code block** that may contain **one or multiple tool calls** needed to advance the strategy.

Coding rules for the ```python``` block:
- Each line must follow the pattern  
  `result = self.execute_task('<tool_name>', ['arg1', 'arg2', ...])`
- All arguments go inside the list.
- You may include **several lines** (i.e., call multiple tools) in a single code block when needed.
- No comments, explanations, markdown headers, or extra text outside the code block.

Failing to strictly follow this format will cause your output to be discarded.

Example of a valid answer when the task is still in progress:

[STRATEGY_CHANGE] no
[STEP_SUCCESS] no
[CONTENT]
```python
{TASK_EXAMPLES}
````

Example of a valid answer when the task has been completed:

[STRATEGY_CHANGE] no
[STEP_SUCCESS] yes
[CONTENT]


Question: {input}

CHA:
""",
        ]

    def task_descriptions(self):
        return "".join(
            [
                (
                    "\n-----------------------------------\n"
                    f"**{task.name}**: {task.description}"
                    "\nThis tool have the following outputs:\n"
                    + "\n".join(task.outputs)
                    + (
                        "\n- The result of this tool will be stored in the datapipe."
                        if task.output_type
                        else ""
                    )
                    + "\n-----------------------------------\n"
                )
                for task in self.available_tasks
            ]
        )

    def divide_text_into_chunks(
        self,
        input_text: str = "",
        max_tokens: int = 10000,
    ) -> List[str]:
        """
        Generate a response based on the input prefix, query, and thinker (task planner).

        Args:
            input_text (str): the input text (e.g., prompt).
            max_tokens (int): Maximum number of tokens allowed.
        Return:
            chunks(List): List of string variables
        """
        # 1 token ~= 4 chars in English
        chunks = [
            input_text[i : i + max_tokens * 4]
            for i in range(0, len(input_text), max_tokens * 4)
        ]
        return chunks

    def generate_scratch_pad(
        self, previous_actions: List[str] = None, **kwargs: Any
    ):
        if previous_actions is None:
            previous_actions = []

        agent_scratchpad = ""
        if len(previous_actions) > 0:
            agent_scratchpad = "\n".join(
                [f"\n{action}" for action in previous_actions]
            )
        # agent_scratchpad
        if (
            self.summarize_prompt
            and len(agent_scratchpad) / 4 > self.max_tokens_allowed
        ):
            # Shorten agent_scratchpad
            chunks = self.divide_text_into_chunks(
                input_text=agent_scratchpad,
                max_tokens=self.max_tokens_allowed,
            )
            agent_scratchpad = ""
            kwargs["max_tokens"] = min(
                2000, int(self.max_tokens_allowed / len(chunks))
            )
            for chunk in chunks:
                prompt = self._shorten_prompt.replace(
                    "{chunk}", chunk
                )
                chunk_summary = (
                    self._response_generator_model.generate(
                        query=prompt, **kwargs
                    )
                )
                agent_scratchpad += chunk_summary + " "

    def plan(
        self,
        query: str,
        history: str = "",
        meta: str = "",
        previous_actions: List[str] = None,
        use_history: bool = False,
        **kwargs: Any,
    ) -> str:
        """
            Generate a plan using Tree of Thought

        Args:
            query (str): Input query.
            history (str): History information.
            meta (str): meta information.
            previous_actions (List[Action]): List of previous actions.
            use_history (bool): Flag indicating whether to use history.
            **kwargs (Any): Additional keyword arguments.
        Return:
            Action: return action.

        """
        if previous_actions is None:
            previous_actions = []

        previous_actions_prompt = ""
        if len(previous_actions) > 0 and self.use_previous_action:
            previous_actions_prompt = f"Previoius Actions:\n{self.generate_scratch_pad(previous_actions, **kwargs)}"

        prompt = (
            self._planner_prompt[0]
            .replace("{input}", query)
            .replace("{meta}", ", ".join(meta))
            .replace(
                "{history}", history if use_history else "No History"
            )
            .replace("{previous_actions}", previous_actions_prompt)
            .replace("{tool_names}", self.task_descriptions())
        )
        # if len(previous_actions) > 0:
        # prompt += "\nThought:"
        # print(prompt)
        # kwargs["max_tokens"] = 2000  # 增加token数量以支持更复杂的代码生成
        response = self._planner_model.generate(
            query=prompt, **kwargs
        )
        # print("respp\n\n", response)
        prompt = (
            self._planner_prompt[1]
            .replace(
                "{strategy}",
                "Decision:\n" + response.split("Decision:")[-1],
            )
            .replace("{tool_names}", self.get_available_tasks())
            .replace("{previous_actions}", previous_actions_prompt)
            .replace("{input}", query)
        )
        # print("prompt2\n\n", prompt)
        kwargs["stop"] = self._stop
        # kwargs["max_tokens"] = 3000  # 为代码生成设置更高的token限制
        response = self._planner_model.generate(
            query=prompt, **kwargs
        )

        index = min([response.find(text) for text in self._stop])
        response = response[0:index]
        actions = self.parse(response)
        print("actions", actions)
        return actions
    
    
    def plan_strategy(  # get only strategy
        self,
        query: str,
        history: str = "",
        meta: str = "",
        previous_actions: List[str] = None,
        use_history: bool = False,
        **kwargs: Any,
    ) -> str:
        """
        get the strategy 
        """
        if previous_actions is None:
            previous_actions = []

        previous_actions_prompt = ""
        if len(previous_actions) > 0 and self.use_previous_action:
            previous_actions_prompt = f"Previoius Actions:\n{self.generate_scratch_pad(previous_actions, **kwargs)}"

        prompt = (
            self._planner_prompt[0]
            .replace("{input}", query)
            .replace("{meta}", ", ".join(meta))
            .replace(
                "{history}", history if use_history else "No History"
            )
            .replace("{previous_actions}", previous_actions_prompt)
            .replace("{tool_names}", self.task_descriptions())
        )
        with open("./log/logger.txt", mode="w", encoding="utf-8") as f:
            f.write("\n==========================================first prompt start================================================\n")
            f.write(prompt)
            f.write("\n==========================================first prompt end================================================\n")
        kwargs["stop"] = self._stop
        kwargs['repetition_penalty'] = 1.2
        response = self._planner_model.generate(
            query=prompt, **kwargs
        )
        index = min([response.find(text) for text in self._stop])
        response = response[0:index]
        
        return "Decision:\n" + response.split("Decision:")[-1]
    
    
    def plan_evaluation(
        self,
        query, 
        strategy, 
        current_action, 
        current_action_input, 
        current_failed_actions, 
        current_failed_actions_inputs, 
        previous_inputs, 
        previous_actions: List[str] = None,
        **kwargs: Any
    ): 
        prompt = (
            self._planner_prompt[1]
            .replace("{input}", query)
            .replace(
                "{strategy}",
                "Decision:\n" + self._safe_join(strategy),
            ).replace(
                "{previous_actions}", self._safe_join(previous_actions) + '\n' + "previous inputs: \n" + self._safe_join(previous_inputs)
            ).replace(
                "{current_attempt_result}", self._safe_join(current_action) + '\n' + "current input: \n" + self._safe_join(current_action_input)
            ).replace(
                "{previous_step_failed_actions}", self._safe_join(current_failed_actions) + '\n' + "failed inputs: \n" + self._safe_join(current_failed_actions_inputs)
            ).replace(
                "{tool_names}", self.task_descriptions()
            ).replace(
                "{TASK_EXAMPLES}", "".join(
                    task.using_example + "\n"
                    for task in self.available_tasks if hasattr(task, 'using_example')
                )
            )
        )
        # print("prompt2\n\n", prompt)
        with open("./log/logger.txt", mode="a", encoding="utf-8") as f:
            f.write("\n====================prompt start===========================\n")
            f.write(prompt)
            f.write("\n====================prompt end===========================\n")
            
        kwargs["stop"] = self._stop
        response = self._planner_model.generate(
            query=prompt, **kwargs
        )

        index = min([response.find(text) for text in self._stop])
        response = response[0:index]
        with open("./log/logger.txt", mode="a", encoding="utf-8") as f:
            f.write("\n====================response start===========================\n")
            f.write(response)
            f.write("\n====================response end===========================\n")
        return response
        # actions = self.parse(response)  # parse if good
        # print("actions", actions)
        # return actions
        

    def parse(
        self,
        query: str,
        **kwargs: Any,
    ) -> str:
        """
            Parse the output query into a list of actions or a final answer. It parses the output based on \
            the following format:

                Action: action\n
                Action Inputs: inputs

        Args:\n
            query (str): The planner output query to extract actions.
            **kwargs (Any): Additional keyword arguments.
        Return:
            List[Union[Action, PlanFinish]]: List of parsed actions or a finishing signal.
        Raise:
            ValueError: If parsing encounters an invalid format or unexpected content.

        """
        # print("query: ", query)
        # pattern = r"`+python\n(.*?)`+"
        pattern = r"```python\s*(.*?)``?"
        # with open("/home/gdfwj/AIagant`/precode.txt", "w") as f:
        #     f.write(query)
        code = re.search(pattern, query, re.DOTALL).group(1)
        # with open("/home/gdfwj/AIagant/code.txt", "w") as f:
        #     f.write(code)
        # exit()
        return code
    # def parse(self, query: str, **kwargs: Any) -> str:
    #     """
    #     Return the single-line code right after ```python.
    #     Accepts any of these forms:
    #         ```python
    #         result = ...
    #         ```
    #         ```python result = ... ```
    #         ```python   result = ...
    #     """
    #     # 1️⃣ 找到 ```python 后面的内容直到行尾
    #     m = re.search(r"```python[ \t]*\n?([^\n\r]*)", query, re.IGNORECASE)
    #     if not m:
    #         raise ValueError("No python code block found in planner output")

    #     code_line = m.group(1).strip()

    #     # 2️⃣ 如果 code_line 为空，可能是 ```python\n换行，在下一行
    #     if not code_line:
    #         m2 = re.search(r"```python[^\n\r]*[\n\r]+([^\n\r]+)", query, re.IGNORECASE)
    #         if not m2:
    #             raise ValueError("No python code line found after ```python")
    #         code_line = m2.group(1).strip()

    #     return code_line


    def _safe_join(self, data: Any) -> str:
        """Safely joins elements into a string, handling None, lists, and other types."""
        if data is None:
            return "None"
        if isinstance(data, list):
            return '\n'.join(map(str, data))
        return str(data)
