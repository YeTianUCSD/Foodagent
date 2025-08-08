import os
from pathlib import Path
from typing import Dict, Optional

def collect_folders_and_csv_sample(
    root_dir: str,
    choose: str = "first",  # "first" | "random" | "latest"
) -> Dict[Path, Optional[Path]]:
    """
    遍历 root_dir 内的所有子目录，返回 {目录: 一个示例 csv 路径或 None} 的映射。

    参数
    ----
    root_dir : str
        要遍历的根目录。
    choose : str
        选取 csv 文件的策略：
        - "first"  : 字典序第一个
        - "random" : 随机挑选
        - "latest" : 按修改时间最新
    """
    from random import choice
    root = Path(root_dir).expanduser().resolve()
    result: Dict[Path, Optional[Path]] = {}

    for folder, _, _ in os.walk(root):
        folder_path = Path(folder)
        csv_files = sorted(folder_path.glob("*.csv"))  # 可按需要递归 *.csv
        if not csv_files:
            result[folder_path] = None
            continue

        if choose == "first":
            sample = csv_files[0]
        elif choose == "random":
            sample = choice(csv_files)
        elif choose == "latest":
            sample = max(csv_files, key=lambda p: p.stat().st_mtime)
        else:
            raise ValueError("choose must be 'first', 'random', or 'latest'")

        result[folder_path] = sample

    return result


if __name__ == "__main__":
    root = os.path.abspath(".")  # 修改为你的根目录
    mapping = collect_folders_and_csv_sample(root, choose="first")

    # 示范输出：文件夹 => 示例 csv
    for folder, csv_sample in mapping.items():
        if csv_sample is None:
            print(f"[{folder}]  (no CSV files found)")
        else:
            print(f"[{folder}]  ->  {csv_sample.name}")
