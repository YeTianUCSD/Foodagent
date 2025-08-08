"""
openCHA.llms.llama
~~~~~~~~~~~~~~~~~~

本地 Llama-3 Instruct 模型接口，实现 BaseLLM 规范。

特点
-----
* **完全离线**：不依赖任何网络或 API Key。
* **支持单轮对话**：仅实现最基本的 `generate`，方便后续扩展为多轮。
* **与 openCHA.llms.openai 接口一致**：同样实现 _parse_response、_prepare_prompt、generate。
"""

from typing import Any, Dict, List, Optional
import os

from openCHA.llms import BaseLLM
from openCHA.utils import get_from_dict_or_env
from pydantic import model_validator

# 延迟导入，大文件模型加载可能较慢
import importlib


class LlamaLLM(BaseLLM):
    """
    **Description**

        An offline implementation for running local Llama-3 models
        (e.g. *Meta-Llama-3-8B-Instruct*) via llama-cpp-python.
    """

    # 这里维护常见官方上下文窗口大小，便于做超长输入检测
    models: Dict[str, int] = {
        # 官方给出的最大 context window
        "~/models/Llama3.2-1B-Instruct-hf": 8192,  # 本地转换的 1B 模型
        "~/models/Llama3.2-3B-Instruct-hf": 8192,
        "~/models/Llama3.1-8B-Instruct": 8192,
        "microsoft/DialoGPT-medium": 1024,
        "microsoft/DialoGPT-large": 1024,
        "gpt2": 1024,
        "meta-llama/Llama-4-Scout-17B-16E-Instruct": 2**20, 
        "meta-llama/Meta-Llama-3.1-8B-Instruct": 128000,
        "meta-llama/Meta-Llama-3-70B-Instruct": 8192,
    }

    # pydantic 字段
    model_path: str = ""          # 本地权重路径或 HuggingFace repo 名
    model: Any = None             # llama-cpp model
    tokenizer: Any = None         # HF tokenizer (for transformers mode)
    device: str = "cpu"
    max_new_tokens: int = 1024     # 默认生成 token 数
    use_llama_cpp: bool = True    # 是否使用 llama-cpp-python

    #
    # ──────────────────────────────────────────────────────────────────────────
    # 环境校验与模型加载
    # ──────────────────────────────────────────────────────────────────────────
    #
    @model_validator(mode="before")
    def validate_environment(cls, values: Dict) -> Dict:
        """
        检查 llama-cpp-python 是否可用，并在实例化时加载模型。
        """
        # 1. 解析模型路径：优先参数，其次环境变量
        model_path = get_from_dict_or_env(
            values,
            "model_path",
            "LLAMA_MODEL_PATH",
            default="meta-llama/Meta-Llama-3.1-8B-Instruct",  # 使用本地转换的 1B 模型
        )
        values["model_path"] = model_path

        # 2. 检查模型路径是否存在
        if model_path.startswith("~/"):
            model_path = os.path.expanduser(model_path)
        
        # 3. 暂时只使用 transformers 格式
        values["use_llama_cpp"] = False

        # 4. 导入依赖
        try:
            transformers = importlib.import_module("transformers")
            torch = importlib.import_module("torch")
            values["transformers"] = transformers
            values["torch"] = torch
        except ModuleNotFoundError:
            raise ValueError(
                "请先安装依赖：pip install torch transformers sentencepiece"
            )

        # 5. 自动选择设备
        values["device"] = "cuda" if values["torch"].cuda.is_available() else "cpu"

        # 6. 加载模型
        # 使用 transformers 加载
        tokenizer = values["transformers"].AutoTokenizer.from_pretrained(
            model_path, use_fast=True, trust_remote_code=True
        )
        model = values["transformers"].AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=values["torch"].float16 if values["device"] == "cuda" else values["torch"].float32,
            device_map="auto" if values["device"] == "cuda" else None,
            trust_remote_code=True,
        )
        model.eval()
        values["tokenizer"] = tokenizer
        values["model"] = model

        return values

    #
    # ──────────────────────────────────────────────────────────────────────────
    # 公共辅助函数
    # ──────────────────────────────────────────────────────────────────────────
    #
    def get_model_names(self) -> List[str]:
        """返回支持的模型列表。"""
        return list(self.models.keys())

    def is_max_token(self, prompt: str, model_name: Optional[str] = None) -> bool:
        """
        判断输入 prompt token 数是否超过模型上下文窗口。
        """
        model_name = model_name or self.model_path
        max_ctx = self.models.get(model_name, 8192)
        
        # 使用 transformers 的 tokenizer
        n_tokens = len(self.tokenizer.encode(prompt))
        
        return n_tokens > max_ctx

    #
    # ──────────────────────────────────────────────────────────────────────────
    # BaseLLM 规定需要实现的 3 个抽象方法
    # ──────────────────────────────────────────────────────────────────────────
    #
    def _prepare_prompt(self, prompt: str) -> str:
        return self.tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            tokenize=False,
            add_generation_prompt=True,
        )


    def _parse_response(self, response) -> str:
        """
        将生成的 token 序列解码为文本；同时去掉原始 prompt。
        """
        # transformers 返回的是 token ids
        full_text = self.tokenizer.decode(
            response[0], skip_special_tokens=True
        )
        # 去掉前缀 prompt
        prompt_text = self._prepare_prompt(self._current_prompt)
        return full_text[len(prompt_text) :].lstrip()

    def generate(self, query: str, **kwargs: Any) -> str:
        """
        调用本地 Llama-3 生成回复。

        可选参数
        -----------
        max_new_tokens : int    新生成 token 数
        temperature     : float 采样温度
        top_p           : float nucleus sampling
        """
        # 参数解析
        max_new_tokens = kwargs.get("max_new_tokens", self.max_new_tokens)
        temperature = kwargs.get("temperature", 0.7)
        top_p = kwargs.get("top_p", 0.9)
        stop = kwargs.get("stop")  # 停止词，列表或字符串

        # 准备 prompt
        prompt = self._prepare_prompt(query)
        self._current_prompt = prompt  # 供 _parse_response 使用
        if self.is_max_token(prompt):
            raise ValueError("输入过长，已超过模型最大上下文窗口。")

        # 使用 transformers
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            add_special_tokens=True,
        ).to(self.device)

        with importlib.import_module("torch").inference_mode():
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                eos_token_id=self.tokenizer.convert_tokens_to_ids("<|eot_id|>"),
                pad_token_id=self.tokenizer.eos_token_id,
            )

        
        gen_ids = output_ids[0][inputs["input_ids"].shape[-1]:]   # 把 prompt 长度切掉
        result = self.tokenizer.decode(gen_ids, skip_special_tokens=True).strip()
        # result = self._parse_response(output_ids)

        # # 简易 stop-word 截断
        # if stop:
        #     if isinstance(stop, str):
        #         stop = [stop]
        #     for s in stop:
        #         if s in result:
        #             result = result.split(s)[0]

        return result.strip()
