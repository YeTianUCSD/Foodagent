#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
load_ai4food.py
- 执行 schema.sql
- 递归匹配 data/ 下的 CSV
- 以最小改动导入到 AI4food_db
依赖: pandas, pymysql, tqdm, python-dotenv
"""

from __future__ import annotations
import os, re, glob, pathlib, logging
from typing import Dict, Callable
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import pymysql
from tqdm import tqdm

# -------------------- 环境 & 配置 --------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
load_dotenv()

ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT / "data"
SCHEMA_SQL = DATA / "schema.sql"

DB_CFG = dict(
    host=os.getenv("MYSQL_HOST", "localhost"),
    port=int(os.getenv("MYSQL_PORT", 3306)),
    user=os.getenv("MYSQL_USER", "gdfwj"),
    password=os.getenv("MYSQL_PWD", "010923Wzh!"),
    database="AI4food_db",
    charset="utf8mb4",
    autocommit=True,
)

CHUNKSIZE = 2000

# -------------------- 基础函数 --------------------
def run_schema(conn):
    """执行 schema.sql，临时关闭外键检查，避免 DROP 顺序问题"""
    logging.info("Executing schema.sql …")
    with conn.cursor() as cur:
        cur.execute("SET FOREIGN_KEY_CHECKS=0;")  # ← 关闭
        try:
            with open(SCHEMA_SQL, encoding="utf-8") as f:
                buff = ""
                for line in f:
                    buff += line
                    if line.strip().endswith(";"):
                        try:
                            cur.execute(buff)
                        except pymysql.err.InternalError as e:
                            # 表已存在/无法删除等，除非是致命错误都忽略
                            if e.args[0] not in (1050, 1091):
                                raise
                        buff = ""
        finally:
            cur.execute("SET FOREIGN_KEY_CHECKS=1;")  # ← 重新开启


def df_to_sql(df: pd.DataFrame, table: str, conn):
    """批量 INSERT IGNORE（安全处理 NaN/NaT/Inf）"""
    if df.empty:
        return
    # 先统一把 inf 变成 NaN
    df = df.replace([np.inf, -np.inf], np.nan)

    cols = ", ".join(f"`{c}`" for c in df.columns)
    ph = ", ".join(["%s"] * len(df.columns))
    sql = f"INSERT IGNORE INTO `{table}` ({cols}) VALUES ({ph})"

    def _clean(v):
        # 任何 NaN/NaT -> None；pandas Timestamp 保留即可
        if v is None:
            return None
        # pandas 的 NA / NaT / numpy.nan
        try:
            if pd.isna(v):
                return None
        except Exception:
            pass
        return v

    with conn.cursor() as cur:
        for i in range(0, len(df), CHUNKSIZE):
            chunk = df.iloc[i : i + CHUNKSIZE]
            # 逐行转 tuple，并把 NaN/NaT 清理为 None
            values = [tuple(_clean(x) for x in row) for row in chunk.itertuples(index=False, name=None)]
            cur.executemany(sql, values)


def get_table_columns(conn, table: str) -> list[str]:
    sql = """SELECT COLUMN_NAME
             FROM INFORMATION_SCHEMA.COLUMNS
             WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s
             ORDER BY ORDINAL_POSITION"""
    with conn.cursor() as cur:
        cur.execute(sql, (DB_CFG["database"], table))
        return [r[0] for r in cur.fetchall()]

# -------------------- 通用清洗/辅助 --------------------
_NUM_RE = re.compile(r"^\s*[<>]\s*")  # 前导 > 或 <

def clean_numeric(df: pd.DataFrame, numeric_cols: list[str] | None = None):
    """去掉 > / < 前缀并转为数值"""
    if numeric_cols is None:
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        for col in df.select_dtypes(include=["object"]).columns:
            sample = df[col].dropna().astype(str).head(20)
            if (sample.str.match(r"^\s*[<>]?\s*\d")).mean() > 0.8:
                numeric_cols.append(col)
    for col in set(numeric_cols):
        ser = df[col].astype(str)
        if ser.str.contains(_NUM_RE).any():
            ser = ser.str.replace(_NUM_RE, "", regex=True)
        df[col] = pd.to_numeric(ser, errors="coerce")
    return df

def to_datetime_naive(s: pd.Series) -> pd.Series:
    dt = pd.to_datetime(s, errors="coerce", utc=True)
    try:
        return dt.dt.tz_convert(None)
    except Exception:
        return dt.dt.tz_localize(None)

def id_from_filename(name: str) -> str | None:
    m = re.match(r"(A\d+[A-Z]?_\d+)", pathlib.Path(name).stem)
    return m.group(1) if m else None

# 仅当缺列时采用的“最小别名”
ALIASES = {
    "ts": ["timestamp"],
    "record_ts": ["timestamp"],
    "session_ts": ["timestamp"],

    "start_time": ["start", "start_local", "start_time_local"],
    "end_time": ["end", "end_local", "end_time_local"],
    "start_sleep": ["start_sleep_time"],
    "end_sleep": ["end_sleep_time"],

    "day": ["date", "timestamp"],
    "date": ["day", "timestamp"],

    "bpm": ["value", "heart_rate", "hr"],
    "glucose_mg_dl": ["glucose_value_in_mg_dl"],

    "resting_hr_bpm": ["resting_heart_rate", "resting_hr"],
    "systolic_bp_mmhg": ["systolic", "systolic_bp"],
    "diastolic_bp_mmhg": ["diastolic", "diastolic_bp"],

    "calories_kcal": ["calories"],
    "distance_m": ["distance"],
    "altitude_m": ["altitude"],

    "rmssd": ["rmssd_ms"],
    "nrem_hr": ["nrem_heart_rate"],
    "minutes_in_rem": ["minutes_in_rem_sleep"],

    "night_end": ["timestamp"],
}

TIME_LIKE = {
    "ts","record_ts","session_ts",
    "start_time","end_time","start_sleep","end_sleep",
    "night_end"
}

def build_insert_frame(df: pd.DataFrame, table: str, conn, per_id=False, pid=None) -> pd.DataFrame:
    """
    不改原 CSV 列名，只构建一份“用于写库”的 DataFrame：
    1) 同名(忽略大小写)优先；2) 目标列缺失时用 ALIASES 匹配；3) day/date 可由 timestamp 推导；
    4) 时间列统一转 DATETIME；5) 数值列做去符号清洗。
    """
    wanted = get_table_columns(conn, table)
    src_cols = {c.lower(): c for c in df.columns}
    out = pd.DataFrame(index=df.index)

    for tgt in wanted:
        # 同名
        if tgt.lower() in src_cols:
            out[tgt] = df[src_cols[tgt.lower()]]
            continue
        # 别名
        for alias in ALIASES.get(tgt, []):
            if alias.lower() in src_cols:
                out[tgt] = df[src_cols[alias.lower()]]
                break
        # id 注入（每人一文件）
        if tgt == "id" and per_id and "id" not in out.columns:
            out["id"] = pid
        # 缺列占位
        if tgt not in out.columns:
            out[tgt] = pd.Series([None]*len(df), index=df.index)

    # day 推导
    if "day" in wanted and out["day"].isna().all():
        cand = None
        for c in ["timestamp","ts"]:
            if c.lower() in src_cols:
                cand = df[src_cols[c.lower()]]
                break
        if cand is not None:
            out["day"] = pd.to_datetime(to_datetime_naive(cand).dt.date)

    # date 推导
    if "date" in wanted and out["date"].isna().all():
        cand = None
        for c in ["date","timestamp","ts","day"]:
            if c.lower() in src_cols:
                cand = df[src_cols[c.lower()]]
                break
            if c in out.columns and out[c].notna().any():
                cand = out[c]; break
        if cand is not None:
            out["date"] = pd.to_datetime(pd.to_datetime(cand).dt.date)

    # 时间列标准化
    for c in set(TIME_LIKE).intersection(wanted):
        if c in out.columns and out[c].notna().any():
            out[c] = to_datetime_naive(out[c])

    # 数值清洗
    clean_numeric(out)

    return out[wanted]

# -------------------- 通用 loader --------------------
def load_generic_single(fp: pathlib.Path, table: str, conn):
    df = pd.read_csv(fp)
    insert_df = build_insert_frame(df, table, conn, per_id=False)
    df_to_sql(insert_df, table, conn)

def load_generic_per_id(fp: pathlib.Path, table: str, conn):
    pid = id_from_filename(fp.name)
    df = pd.read_csv(fp)
    insert_df = build_insert_frame(df, table, conn, per_id=True, pid=pid)
    df_to_sql(insert_df, table, conn)

# -------------------- ECG / EDA 特例 --------------------

def find_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """在 df 里按不区分大小写找到第一个匹配的列名，并返回真实列名"""
    low = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in low:
            return low[cand.lower()]
    return None



def parse_numeric_array(cell) -> list[int]:
    if pd.isna(cell): return []
    text = str(cell).strip()
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1]
    parts = re.split(r"[,\s]+", text.strip())
    out = []
    for p in parts:
        if not p: continue
        try: out.append(int(float(p)))
        except: pass
    return out

def load_ecg_file(fp: pathlib.Path, conn):
    """写 ecg_recordings + ecg_waveforms，并计算 sample_count"""
    pid = id_from_filename(fp.name)
    df = pd.read_csv(fp)

    # 元信息：使用最小改动构建（会生成 id/record_ts 等）
    rec_df = build_insert_frame(df, "ecg_recordings", conn, per_id=True, pid=pid)

    # 波形列（忽略大小写）
    wave_col = find_col(df, ["waveform_samples", "waveform", "samples"])

    for i, row in rec_df.iterrows():
        # 计算样本数
        arr = parse_numeric_array(df.iloc[i][wave_col]) if wave_col else []
        rec_df.at[i, "sample_count"] = int(len(arr))

        # 插入一行 recordings
        df_to_sql(pd.DataFrame([rec_df.loc[i]]), "ecg_recordings", conn)

        # 插入 waveforms 长表
        if arr:
            wf = pd.DataFrame({
                "id": row["id"],
                "record_ts": row["record_ts"],
                "sample_idx": np.arange(len(arr), dtype=int),
                "voltage": arr,
            })
            df_to_sql(wf, "ecg_waveforms", conn)


def load_eda_sessions_file(fp: pathlib.Path, conn):
    """写 eda_sessions + eda_levels（逐点），并计算 sample_count"""
    pid = id_from_filename(fp.name)
    df = pd.read_csv(fp)

    # 元信息
    meta_df = build_insert_frame(df, "eda_sessions", conn, per_id=True, pid=pid)

    # 波形列（忽略大小写）
    wave_col = find_col(df, ["skin_conductance_levels", "levels", "eda_levels", "eda_series"])

    with conn.cursor() as cur:
        for i, meta in meta_df.iterrows():
            # 计算样本数
            arr = parse_numeric_array(df.iloc[i][wave_col]) if wave_col else []
            meta_df.at[i, "sample_count"] = int(len(arr))

            # 插入 session（只写有值的列 + 必要的 id/session_ts）
            cols = [c for c in meta.index if pd.notna(meta_df.at[i, c]) or c in ["id", "session_ts"]]
            sql = f"INSERT INTO `eda_sessions` ({', '.join('`'+c+'`' for c in cols)}) VALUES ({', '.join(['%s']*len(cols))})"
            cur.execute(sql, [meta_df.at[i, c] for c in cols])
            session_id = cur.lastrowid

            # 插入 levels
            if arr:
                batch = [(int(session_id), int(j), float(v)) for j, v in enumerate(arr)]
                cur.executemany(
                    "INSERT IGNORE INTO `eda_levels` (`session_id`,`sample_idx`,`level_microsiemens`) VALUES (%s,%s,%s)",
                    batch
                )


# -------------------- 路由表（通用为主） --------------------
LOAD_MAP: Dict[str, Dict[str, Callable]] = {
    # Core
    "participant_information.csv": {"table": "participants", "loader": load_generic_single},

    # DS1
    "DS1_AnthropometricMeasurements/anthropometrics.csv": {"table": "anthropometrics", "loader": load_generic_single},

    # DS2
    "DS2_LifestyleHealth/health.csv": {"table": "health", "loader": load_generic_single},
    "DS2_LifestyleHealth/lifestyle.csv": {"table": "lifestyle", "loader": load_generic_single},  # 若无会跳过

    # DS4
    "DS4_Biomarkers/biomarkers.csv": {"table": "biomarkers", "loader": load_generic_single},
    "DS4_Biomarkers/glucose_levels/*.csv": {"table": "glucose_levels", "loader": load_generic_per_id},

    # DS6
    "DS6_VitalSigns/vital_signs.csv": {"table": "vital_signs", "loader": load_generic_single},
    "DS6_VitalSigns/heart_rate/*.csv": {"table": "heart_rate", "loader": load_generic_per_id},
    "DS6_VitalSigns/electrocardiogram/*.csv": {"table": "ecg_recordings", "loader": load_ecg_file},  # 特例

    # DS7
    "DS7_PhysicalActivity/IPAQ.csv": {"table": "physical_activity_ipaq", "loader": load_generic_single},
    "DS7_PhysicalActivity/active_minutes/*.csv": {"table": "pa_active_minutes", "loader": load_generic_per_id},
    "DS7_PhysicalActivity/estimated_VO2/*.csv": {"table": "pa_estimated_VO2", "loader": load_generic_per_id},
    "DS7_PhysicalActivity/physical_activity_reports/*.csv": {"table": "pa_reports", "loader": load_generic_per_id},
    "DS7_PhysicalActivity/additional_physical_activity_data/*.csv": {"table": "pa_daily_summary", "loader": load_generic_per_id},

    # DS8
    "DS8_SleepActivity/OviedoSleepQuestionnaire.csv": {"table": "OviedoSleepQuestionnaire", "loader": load_generic_single},
    "DS8_SleepActivity/additional_sleep_data/*.csv": {"table": "additional_sleep", "loader": load_generic_per_id},
    "DS8_SleepActivity/skin_temperature/*computed_temperature.csv": {"table": "skin_temp_sleep_nightly", "loader": load_generic_per_id},
    "DS8_SleepActivity/skin_temperature/*wrist_temperature.csv": {"table": "skin_temp_wrist_minute", "loader": load_generic_per_id},
    "DS8_SleepActivity/sleep_quality/*.csv": {"table": "sleep_quality", "loader": load_generic_per_id},
    "DS8_SleepActivity/oxygen_saturation/*daily_oxygen_saturation.csv": {"table": "oxygen_sat_daily", "loader": load_generic_per_id},
    "DS8_SleepActivity/oxygen_saturation/*oxygen_saturation_by_minute.csv": {"table": "oxygen_sat_minute", "loader": load_generic_per_id},
    "DS8_SleepActivity/respiratory_rate/*.csv": {"table": "respiratory_rate", "loader": load_generic_per_id},
    "DS8_SleepActivity/heart_rate_variability/*.csv": {"table": "heart_rate_variability", "loader": load_generic_per_id},

    # DS9
    "DS9_EmotionalState/DASS-21.csv": {"table": "emotional_dass21", "loader": load_generic_single},
    "DS9_EmotionalState/stress_score/*.csv": {"table": "stress_daily_scores", "loader": load_generic_per_id},
    "DS9_EmotionalState/eda_sessions/*.csv": {"table": "eda_sessions", "loader": load_eda_sessions_file},  # 特例

    # DS10
    "DS10_AdditionalInformation/SUS.csv": {"table": "sus_scores", "loader": load_generic_single},
}

# -------------------- 主流程 --------------------
def main():
    if not DATA.exists():
        logging.error("data/ not found at %s", DATA)
        return
    conn = pymysql.connect(**DB_CFG)
    with conn:
        run_schema(conn)
        for pattern, cfg in LOAD_MAP.items():
            files = glob.glob(str(DATA / pattern))
            if not files:
                logging.warning("No match: %s", pattern)
                continue
            logging.info("Loading %s (%d files)…", pattern, len(files))
            for fp in tqdm(files, unit="file", ncols=80, leave=False):
                fp = pathlib.Path(fp)
                loader: Callable = cfg["loader"]
                table: str = cfg["table"]
                # 通用 loader 统一签名 (fp, table, conn)；特例忽略第2参
                try:
                    if loader in (load_ecg_file, load_eda_sessions_file):
                        loader(fp, conn)
                    else:
                        loader(fp, table, conn)
                except Exception as e:
                    logging.exception("Failed to load %s into %s: %s", fp.name, table, e)

    logging.info("✅ All done.")

if __name__ == "__main__":
    main()
