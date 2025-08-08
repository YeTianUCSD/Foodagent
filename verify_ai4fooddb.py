#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_ai4food.py
对 AI4food_db 导入结果做体检与一致性校验
"""
import os
import pymysql
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

DB = dict(
    host=os.getenv("MYSQL_HOST", "localhost"),
    port=int(os.getenv("MYSQL_PORT", 3306)),
    user=os.getenv("MYSQL_USER", "gdfwj"),
    password=os.getenv("MYSQL_PWD", "010923Wzh!"),
    database="AI4food_db",
    charset="utf8mb4",
    autocommit=True,
)

# 常见时间/日期列名
TIME_COLS  = {"ts","record_ts","session_ts","start_time","end_time","start_sleep","end_sleep","night_end"}
DATE_COLS  = {"day","date"}

def q(conn, sql, params=None):
    try:
        # 如果你安装了 SQLAlchemy，建议用引擎（去掉警告）
        from sqlalchemy import create_engine
        user = DB["user"]; pwd = DB["password"]; host = DB["host"]; port = DB["port"]; db = DB["database"]
        engine = create_engine(f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}?charset=utf8mb4")
        with engine.begin() as econn:
            return pd.read_sql(sql, econn, params=params)
    except Exception:
        # 回退到 PyMySQL 连接（会有一个 warning，但不影响结果）
        return pd.read_sql(sql, conn, params=params)

def list_tables(conn):
    sql = """SELECT TABLE_NAME
             FROM INFORMATION_SCHEMA.TABLES
             WHERE TABLE_SCHEMA=%s
             ORDER BY TABLE_NAME"""
    df = q(conn, sql, (DB["database"],))
    return df["TABLE_NAME"].tolist()

def get_columns(conn, table):
    sql = """SELECT COLUMN_NAME, DATA_TYPE
             FROM INFORMATION_SCHEMA.COLUMNS
             WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s
             ORDER BY ORDINAL_POSITION"""
    return q(conn, sql, (DB["database"], table))

def summary_counts(conn):
    rows = []
    for t in list_tables(conn):
        # 这里改成位置索引
        cnt = int(q(conn, f"SELECT COUNT(*) AS c FROM `{t}`").iloc[0, 0])
        cols = get_columns(conn, t)
        id_col = "id" if "id" in set(cols["COLUMN_NAME"]) else None
        time_cols = [c for c in cols["COLUMN_NAME"] if c in TIME_COLS | DATE_COLS]
        rows.append({"table": t, "rows": cnt, "has_id": bool(id_col), "time_cols": ",".join(time_cols)})
    return pd.DataFrame(rows).sort_values("table")

def time_ranges(conn, table):
    cols = get_columns(conn, table)
    time_cols = [c for c in cols["COLUMN_NAME"] if c in TIME_COLS]
    date_cols = [c for c in cols["COLUMN_NAME"] if c in DATE_COLS]
    parts = []
    for c in time_cols:
        parts.append(f"MIN(`{c}`) AS min_{c}, MAX(`{c}`) AS max_{c}")
    for c in date_cols:
        parts.append(f"MIN(`{c}`) AS min_{c}, MAX(`{c}`) AS max_{c}")
    if not parts:
        return pd.DataFrame()
    sql = f"SELECT {', '.join(parts)} FROM `{table}`"
    return q(conn, sql)

def check_orphans(conn, table, ref="participants", key="id"):
    sql = f"""
    SELECT COUNT(*) AS orphans
    FROM `{table}` t LEFT JOIN `{ref}` p ON t.`{key}` = p.`{key}`
    WHERE p.`{key}` IS NULL
    """
    # 改成位置索引
    return int(q(conn, sql).iloc[0, 0])

def check_pk_collisions_hint():
    # 我们用了 INSERT IGNORE，若导入行数明显低于 CSV 行数，可能是主键冲突导致被忽略
    print("Hint: 如需检查被 IGNORE 的主键冲突，请对照 CSV 行数与表内 COUNT(*)。")

def ecg_consistency(conn):
    # 检查 ecg_recordings.sample_count 是否等于 ecg_waveforms 逐点行数
    sql = """
    SELECT r.id, r.record_ts,
           r.sample_count,
           COUNT(w.sample_idx) AS wave_points,
           (r.sample_count = COUNT(w.sample_idx)) AS ok
    FROM ecg_recordings r
    LEFT JOIN ecg_waveforms w
      ON r.id = w.id AND r.record_ts = w.record_ts
    GROUP BY r.id, r.record_ts, r.sample_count
    ORDER BY r.record_ts DESC
    LIMIT 50
    """
    return q(conn, sql)

def eda_consistency(conn):
    # 检查 eda_sessions.sample_count 与 eda_levels 行数一致性
    sql = """
    SELECT s.session_id, s.id, s.session_ts,
           s.sample_count,
           COUNT(l.sample_idx) AS level_points,
           (s.sample_count = COUNT(l.sample_idx)) AS ok
    FROM eda_sessions s
    LEFT JOIN eda_levels l
      ON s.session_id = l.session_id
    GROUP BY s.session_id, s.id, s.session_ts, s.sample_count
    ORDER BY s.session_ts DESC
    LIMIT 50
    """
    return q(conn, sql)

def quick_samples(conn, table, n=5):
    return q(conn, f"SELECT * FROM `{table}` LIMIT {int(n)}")

def main():
    conn = pymysql.connect(**DB)
    with conn:
        print("=== 表行数与时间列 ===")
        df = summary_counts(conn)
        print(df.to_string(index=False))

        print("\n=== 关键表的时间范围 ===")
        key_tables = [
            "glucose_levels","heart_rate","ecg_recordings","eda_sessions",
            "pa_active_minutes","pa_daily_summary","pa_estimated_VO2","pa_reports",
            "oxygen_sat_minute","oxygen_sat_daily","respiratory_rate","heart_rate_variability",
            "skin_temp_wrist_minute","skin_temp_sleep_nightly","additional_sleep",
        ]
        for t in key_tables:
            if t in list_tables(conn):
                tr = time_ranges(conn, t)
                if not tr.empty:
                    print(f"\n-- {t} --")
                    print(tr.to_string(index=False))

        print("\n=== 外键孤儿检查（应全部为 0） ===")
        child_tables = [
            "anthropometrics","health","lifestyle","biomarkers","glucose_levels",
            "vital_signs","heart_rate",
            "pa_active_minutes","pa_daily_summary","pa_estimated_VO2","pa_reports",
            "oxygen_sat_minute","oxygen_sat_daily","respiratory_rate","heart_rate_variability",
            "skin_temp_wrist_minute","skin_temp_sleep_nightly","additional_sleep",
            "OviedoSleepQuestionnaire","emotional_dass21","stress_daily_scores",
            "eda_sessions"
        ]
        for t in child_tables:
            if t in list_tables(conn):
                n = check_orphans(conn, t, "participants", "id")
                print(f"{t:32s} orphans={n}")

        print("\n=== ECG 一致性（sample_count vs wave_points） ===")
        if "ecg_recordings" in list_tables(conn):
            print(ecg_consistency(conn).to_string(index=False))

        print("\n=== EDA 一致性（sample_count vs level_points） ===")
        if "eda_sessions" in list_tables(conn):
            print(eda_consistency(conn).to_string(index=False))

        print("\n=== 示例抽样（每表前 5 行） ===")
        for t in ["participants","biomarkers","vital_signs","pa_daily_summary","sleep_quality","sus_scores"]:
            if t in list_tables(conn):
                print(f"\n-- {t} --")
                print(quick_samples(conn, t, 5).to_string(index=False))

        print("\n✓ 校验完成。")
        check_pk_collisions_hint()

if __name__ == "__main__":
    main()
