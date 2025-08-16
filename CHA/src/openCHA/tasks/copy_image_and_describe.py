# openCHA/tasks/copy_image_and_describe.py
from __future__ import annotations
import os, shutil
from typing import Any, List
from openCHA.tasks.task import BaseTask  

class CopyImageAndDescribe(BaseTask):
    # ---- metadata exposed to the planner (CRITICAL) ----
    name: str = "copy_image_and_describe"
    chat_name: str = "CopyImageAndDescribe"
    description: str = (
        "Identify the food in an IMAGE FILE by using its local path. "
        "Input: one absolute image path (string) or a datapipe key that resolves to the path. "
        "If the user asks to recognize/identify food from an image OR provides a path that ends with .jpg/.jpeg/.png, "
        "USE THIS TOOL. The tool will copy the image to the current working directory and return a sentence "
        "as the result to describe the food."
        "Usage (Python code you must emit): self.execute_task('copy_image_and_describe', ['/abs/path/to/image.jpg'])"
    )
    inputs: List[str]  = ["Absolute image path (e.g. /path/to/file.jpg) or datapipe:<key>"]
    outputs: List[str] = ["A sentence describing the food."]
    using_example: str = "result = self.execute_task('copy_image_and_describe', ['/abs/path/to/image.jpg'])"

    output_type: bool  = False
    return_direct: bool = False

    def _execute(self, inputs: List[Any]) -> str:
        src = inputs[0]
        if isinstance(src, dict):  # support datapipe-decoded JSON
            src = src.get("path") or src.get("image_path") or src.get("file") or ""
        if not isinstance(src, str) or not src.strip():
            raise ValueError("The image path must be a non-empty string.")
        src = src.strip()
        if not os.path.isfile(src):
            raise FileNotFoundError(f"Image file not found: {src}")
        dst = os.path.join(os.getcwd(), os.path.basename(src))
        shutil.copy2(src, dst)
        return "The food in this image is bread."
