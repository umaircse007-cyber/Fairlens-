import os
from typing import Any

import pandas as pd


UPLOAD_DIR = "data/uploads"
REPORT_DIR = "data/reports"


def ensure_data_dirs() -> None:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)


def load_dataset(filepath: str) -> pd.DataFrame:
    ext = os.path.splitext(filepath)[1].lower()

    if ext in [".xlsx", ".xls"]:
        return pd.read_excel(filepath)

    return pd.read_csv(filepath)


def json_safe(value: Any) -> Any:
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        return value.item()

    return value


def build_column_profile(df: pd.DataFrame, sample_size: int = 8) -> dict:
    profile = {}

    for col in df.columns:
        series = df[col].dropna()
        profile[col] = {
            "dtype": str(df[col].dtype),
            "sample_values": [json_safe(v) for v in series.head(sample_size).tolist()],
            "unique_count": int(series.nunique()),
            "missing_count": int(df[col].isna().sum()),
        }

    return profile


def infer_outcome_column(df: pd.DataFrame) -> str:
    preferred_names = [
        "hired",
        "hire",
        "selected",
        "approved",
        "accepted",
        "admitted",
        "shortlisted",
        "outcome",
        "decision",
        "result",
        "label",
        "target",
    ]

    lower_to_actual = {str(c).strip().lower(): c for c in df.columns}
    for name in preferred_names:
        if name in lower_to_actual:
            return lower_to_actual[name]

    for col in reversed(df.columns.tolist()):
        values = set(str(v).strip().lower() for v in df[col].dropna().unique()[:20])
        if values and values.issubset({"yes", "no", "true", "false", "1", "0", "hired", "rejected", "approved", "denied"}):
            return col

    return df.columns[-1] if len(df.columns) else ""


def infer_favorable_value(df: pd.DataFrame, outcome_column: str) -> str:
    if not outcome_column or outcome_column not in df.columns:
        return "Yes"

    values = [v for v in df[outcome_column].dropna().unique().tolist()]
    lowered = {str(v).strip().lower(): v for v in values}

    for candidate in ["yes", "true", "1", "hired", "approved", "accepted", "selected", "pass"]:
        if candidate in lowered:
            return str(lowered[candidate])

    if pd.api.types.is_numeric_dtype(df[outcome_column]) and values:
        return str(max(values))

    return str(values[0]) if values else "Yes"
