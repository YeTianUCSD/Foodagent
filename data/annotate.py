#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
annotate_schema.py
生成逐行带注释的 schema_annotated.sql
用法:  python annotate_schema.py schema.sql
"""
import re, sys, pathlib, textwrap

def humanize(name: str) -> str:
    """snake_case / camelCase -> Title Case  (for quick column hints)."""
    # 去掉反引号与首尾空格
    name = name.strip("` ").replace("`","")
    # 拆 snake_case 或 camel
    parts = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).split('_')
    return ' '.join(w.capitalize() for w in parts if w)

def annotate_line(line: str) -> str:
    stripped = line.strip()

    # -------- 表级块注释 --------
    m = re.match(r'CREATE TABLE `([^`]+)`', stripped, flags=re.I)
    if m:
        table = m.group(1)
        block = [
            "",
            f"/* =====================================================",
            f" *  TABLE: {table}",
            f" *  Auto-generated annotations; edit freely if需要更细描述",
            f" ===================================================== */"
        ]
        return "\n".join(block) + "\n" + line

    # -------- 列定义 --------
    # 以反引号开头且在 CREATE 块里
    if stripped.startswith("`"):
        colname = stripped.split()[0]
        comment = humanize(colname)
        # 已经有手写注释就不覆盖
        return line.rstrip("\n") + f"   -- {comment}\n"

    # -------- 外键 / 主键 / 索引 --------
    if "FOREIGN KEY" in stripped.upper():
        return line.rstrip("\n") + "   -- 外键约束\n"
    if stripped.upper().startswith("PRIMARY KEY"):
        return line.rstrip("\n") + "   -- 主键\n"
    if stripped.upper().startswith("KEY ") or stripped.upper().startswith("INDEX"):
        return line.rstrip("\n") + "   -- 二级索引\n"
    if stripped.upper().startswith("DROP TABLE"):
        tbl = re.findall(r'`([^`]+)`', stripped)
        return line.rstrip("\n") + (f"   -- 若存在则先删除表 {tbl[0]}\n" if tbl else "\n")

    return line  # 其他行原样返还

def main():
    if len(sys.argv) < 2:
        print("Usage: python annotate_schema.py schema.sql")
        sys.exit(1)

    in_path = pathlib.Path(sys.argv[1])
    out_path = in_path.with_name(in_path.stem + "_annotated.sql")

    with in_path.open(encoding="utf-8") as f_in, out_path.open("w", encoding="utf-8") as f_out:
        for ln in f_in:
            f_out.write(annotate_line(ln))

    print(f"✅ Done. Annotated file saved to {out_path}")

if __name__ == "__main__":
    main()
