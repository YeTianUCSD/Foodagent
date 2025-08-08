#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_ai4food_report.py
生成 AI4food_db 全库统计报告到 AI4food_db_report.txt

依赖:
  pip install pymysql python-dotenv
可选:
  在项目根创建 .env 设置 MySQL 连接:
    MYSQL_HOST=localhost
    MYSQL_PORT=3306
    MYSQL_USER=root
    MYSQL_PWD=yourpassword
"""

from __future__ import annotations
import os, sys, math
import pymysql
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

DBCFG = dict(
    host=os.getenv("MYSQL_HOST", "localhost"),
    port=int(os.getenv("MYSQL_PORT", 3306)),
    user=os.getenv("MYSQL_USER", "gdfwj"),
    password=os.getenv("MYSQL_PWD", "010923Wzh!"),
    database="AI4food_db",
    charset="utf8mb4",
    autocommit=True,
)

REPORT_PATH = "AI4food_db_report.txt"
TOP_SAMPLE_LIMIT = 100_000    # 计算 TopN 时最多扫描的样本行数
EXAMPLE_ROWS = 5

# 小心：上面变量名写错了，修正：
def connect():
    return pymysql.connect(**DBCFG)

def fetchall_dict(cur, sql, params=None):
    cur.execute(sql, params or ())
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]

def list_tables(cur):
    sql = """
    SELECT TABLE_NAME
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA=%s
    ORDER BY TABLE_NAME
    """
    return [r["TABLE_NAME"] for r in fetchall_dict(cur, sql, (DBCFIG["database"],))]

# 再修：上面也用了 DBCFIG 打错，改全局一次：
def list_tables(cur):
    sql = """
    SELECT TABLE_NAME
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA=%s
    ORDER BY TABLE_NAME
    """
    return [r["TABLE_NAME"] for r in fetchall_dict(cur, sql, (DBCFG["database"],))]

def table_columns(cur, table):
    sql = """
    SELECT COLUMN_NAME, DATA_TYPE, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY,
           COLUMN_DEFAULT, EXTRA, CHARACTER_MAXIMUM_LENGTH AS char_len,
           NUMERIC_PRECISION AS num_prec, NUMERIC_SCALE AS num_scale
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s
    ORDER BY ORDINAL_POSITION
    """
    return fetchall_dict(cur, sql, (DBCFG["database"], table))

def table_indexes(cur, table):
    sql = """
    SELECT INDEX_NAME, NON_UNIQUE, SEQ_IN_INDEX, COLUMN_NAME
    FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s
    ORDER BY INDEX_NAME, SEQ_IN_INDEX
    """
    return fetchall_dict(cur, sql, (DBCFG["database"], table))

def table_rowcount(cur, table):
    cur.execute(f"SELECT COUNT(*) FROM `{table}`")
    return int(cur.fetchone()[0])

def is_numeric(dtype: str) -> bool:
    return dtype.lower() in {
        "int","integer","tinyint","smallint","mediumint","bigint",
        "decimal","numeric","float","double","double precision","real"
    }

def is_temporal(dtype: str) -> bool:
    return dtype.lower() in {"date","datetime","timestamp","time","year"}

def column_stats(cur, table, col, dtype):
    # 基本计数
    cur.execute(f"SELECT COUNT(*) AS total, COUNT(`{col}`) AS nonnull FROM `{table}`")
    total, nonnull = cur.fetchone()
    nulls = total - nonnull
    # distinct（可能慢，但表通常不大；可按需注释）
    cur.execute(f"SELECT COUNT(DISTINCT `{col}`) FROM `{table}`")
    distinct = int(cur.fetchone()[0])

    stats = {
        "total": int(total), "nonnull": int(nonnull), "nulls": int(nulls), "distinct": distinct
    }

    if nonnull == 0:
        return stats

    if is_numeric(dtype):
        # 数值汇总
        cur.execute(
            f"SELECT MIN(`{col}`), MAX(`{col}`), AVG(`{col}`), STDDEV_POP(`{col}`) FROM `{table}` WHERE `{col}` IS NOT NULL"
        )
        mn, mx, avg, std = cur.fetchone()
        stats.update({
            "min": mn, "max": mx, "avg": avg, "stddev_pop": std
        })
    elif is_temporal(dtype):
        cur.execute(
            f"SELECT MIN(`{col}`), MAX(`{col}`) FROM `{table}` WHERE `{col}` IS NOT NULL"
        )
        mn, mx = cur.fetchone()
        stats.update({"min": mn, "max": mx})
    else:
        # Top 5 高频（在样本内统计以防全表扫描过慢）
        sql = f"""
        SELECT `{col}` AS val, COUNT(*) AS c
        FROM (SELECT `{col}` FROM `{table}` WHERE `{col}` IS NOT NULL LIMIT {TOP_SAMPLE_LIMIT}) AS t
        GROUP BY val
        ORDER BY c DESC
        LIMIT 5
        """
        top = fetchall_dict(cur, sql)
        stats["top5"] = [(str(r["val"]), int(r["c"])) for r in top]

    return stats

def print_kv(out, key, val, indent=0):
    out.write(" " * indent + f"- {key}: {val}\n")

def fk_relations(cur):
    sql = """
    SELECT TABLE_NAME AS child_table,
           COLUMN_NAME AS child_column,
           REFERENCED_TABLE_NAME AS parent_table,
           REFERENCED_COLUMN_NAME AS parent_column,
           CONSTRAINT_NAME
    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA=%s
      AND REFERENCED_TABLE_NAME IS NOT NULL
    ORDER BY child_table, CONSTRAINT_NAME, ORDINAL_POSITION
    """
    return fetchall_dict(cur, sql, (DBCFG["database"],))

def orphan_count(cur, child_table, child_col, parent_table, parent_col):
    sql = f"""
    SELECT COUNT(*) FROM `{child_table}` c
    LEFT JOIN `{parent_table}` p
      ON c.`{child_col}` = p.`{parent_col}`
    WHERE p.`{parent_col}` IS NULL
    """
    cur.execute(sql)
    return int(cur.fetchone()[0])

def examples(cur, table, limit=5):
    cur.execute(f"SELECT * FROM `{table}` LIMIT {int(limit)}")
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    res = []
    for r in rows:
        res.append({c: v for c, v in zip(cols, r)})
    return res

def ecg_consistency(cur):
    sql = """
    SELECT COUNT(*) FROM (
      SELECT r.id, r.record_ts, r.sample_count, COUNT(w.sample_idx) AS n
      FROM ecg_recordings r
      LEFT JOIN ecg_waveforms w ON r.id=w.id AND r.record_ts=w.record_ts
      GROUP BY r.id, r.record_ts, r.sample_count
      HAVING (r.sample_count IS NULL AND COUNT(w.sample_idx) IS NOT NULL)
          OR (r.sample_count IS NOT NULL AND COUNT(w.sample_idx) IS NULL)
          OR (r.sample_count <> COUNT(w.sample_idx))
    ) AS t
    """
    try:
        cur.execute(sql)
        return int(cur.fetchone()[0])
    except Exception:
        return None

def eda_consistency(cur):
    sql = """
    SELECT COUNT(*) FROM (
      SELECT s.session_id, s.sample_count, COUNT(l.sample_idx) AS n
      FROM eda_sessions s
      LEFT JOIN eda_levels l ON s.session_id=l.session_id
      GROUP BY s.session_id, s.sample_count
      HAVING (s.sample_count IS NULL AND COUNT(l.sample_idx) IS NOT NULL)
          OR (s.sample_count IS NOT NULL AND COUNT(l.sample_idx) IS NULL)
          OR (s.sample_count <> COUNT(l.sample_idx))
    ) AS t
    """
    try:
        cur.execute(sql)
        return int(cur.fetchone()[0])
    except Exception:
        return None

def main():
    conn = connect()
    with conn, conn.cursor() as cur, open(REPORT_PATH, "w", encoding="utf-8") as out:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        out.write(f"# AI4food_db 数据库统计报告\nGenerated at {now}\n\n")

        # 库里所有表
        tables = list_tables(cur)
        out.write(f"## 表清单 ({len(tables)} 张)\n")
        out.write(", ".join(tables) + "\n\n")

        # 外键关系
        fks = fk_relations(cur)
        out.write("## 外键关系\n")
        if not fks:
            out.write("(无外键)\n\n")
        else:
            for r in fks:
                out.write(f"- {r['child_table']}.{r['child_column']} → {r['parent_table']}.{r['parent_column']}  (constraint={r['CONSTRAINT_NAME']})\n")
            out.write("\n")

        # 核心一致性（若相关表存在）
        if "ecg_recordings" in tables and "ecg_waveforms" in tables:
            mism = ecg_consistency(cur)
            out.write(f"### ECG 一致性：记录 vs 波形点数不一致条数 = {mism}\n\n")
        if "eda_sessions" in tables and "eda_levels" in tables:
            mism = eda_consistency(cur)
            out.write(f"### EDA 一致性：会话 vs 电导点数不一致条数 = {mism}\n\n")

        # 逐表统计
        for t in tables:
            out.write(f"\n\n## 表：{t}\n")
            try:
                nrows = table_rowcount(cur, t)
            except Exception as e:
                out.write(f"(无法统计行数：{e})\n")
                nrows = None
            print_kv(out, "行数", nrows if nrows is not None else "N/A", indent=0)

            # 列信息
            cols = table_columns(cur, t)
            out.write("\n### 列定义\n")
            for c in cols:
                line = (
                    f"{c['COLUMN_NAME']}  | {c['DATA_TYPE']} ({c['COLUMN_TYPE']}) "
                    f"| NULLABLE={c['IS_NULLABLE']} | KEY={c['COLUMN_KEY'] or '-'} "
                    f"| DEFAULT={c['COLUMN_DEFAULT'] if c['COLUMN_DEFAULT'] is not None else '-'} "
                )
                if c['char_len']:
                    line += f"| len={c['char_len']}"
                if c['num_prec'] is not None:
                    line += f"| prec/scale={c['num_prec']}/{c['num_scale']}"
                out.write("- " + line + "\n")

            # 索引
            idx = table_indexes(cur, t)
            out.write("\n### 索引\n")
            if not idx:
                out.write("(无索引)\n")
            else:
                by_name = {}
                for r in idx:
                    by_name.setdefault(r["INDEX_NAME"], []).append(r)
                for name, rows in by_name.items():
                    parts = ", ".join(f"{r['COLUMN_NAME']}#{r['SEQ_IN_INDEX']}" for r in rows)
                    uniq = "UNIQUE" if rows[0]["NON_UNIQUE"] == 0 else "NON-UNIQUE"
                    out.write(f"- {name} ({uniq}): {parts}\n")

            # 列级统计
            out.write("\n### 列级统计\n")
            for c in cols:
                cname, dtype = c["COLUMN_NAME"], c["DATA_TYPE"]
                try:
                    st = column_stats(cur, t, cname, dtype)
                    out.write(f"- {cname}:\n")
                    print_kv(out, "nonnull", st["nonnull"], indent=2)
                    print_kv(out, "nulls", st["nulls"], indent=2)
                    print_kv(out, "distinct", st["distinct"], indent=2)
                    if "min" in st: print_kv(out, "min", st["min"], indent=2)
                    if "max" in st: print_kv(out, "max", st["max"], indent=2)
                    if "avg" in st: print_kv(out, "avg", st["avg"], indent=2)
                    if "stddev_pop" in st: print_kv(out, "stddev_pop", st["stddev_pop"], indent=2)
                    if "top5" in st:
                        out.write("  - top5:\n")
                        for v, ccount in st["top5"]:
                            out.write(f"    * {v}  (n={ccount})\n")
                except Exception as e:
                    out.write(f"- {cname}: (统计失败: {e})\n")

            # 示例数据
            out.write("\n### 示例（前 5 行）\n")
            try:
                rows = examples(cur, t, EXAMPLE_ROWS)
                if not rows:
                    out.write("(空表)\n")
                else:
                    for r in rows:
                        kv = "; ".join(f"{k}={r[k]}" for k in r.keys())
                        out.write(f"- {kv}\n")
            except Exception as e:
                out.write(f"(示例查询失败: {e})\n")

            # 外键孤儿（若该表是子表）
            child_fks = [fk for fk in fks if fk["child_table"] == t]
            if child_fks:
                out.write("\n### 外键孤儿检查\n")
                for fk in child_fks:
                    try:
                        n = orphan_count(cur, fk["child_table"], fk["child_column"],
                                         fk["parent_table"], fk["parent_column"])
                        out.write(f"- {fk['child_column']} → {fk['parent_table']}.{fk['parent_column']}: orphans={n}\n")
                    except Exception as e:
                        out.write(f"- {fk['child_column']} → {fk['parent_table']}.{fk['parent_column']}: (失败: {e})\n")

        # 总结
        out.write("\n\n---\n报告生成完毕。\n")

if __name__ == "__main__":
    try:
        main()
        print(f"✅ 报告已生成：{REPORT_PATH}")
    except Exception as e:
        print("❌ 生成报告失败：", e)
        raise
