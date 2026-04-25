import os
from typing import Any

import pandas as pd


UPLOAD_DIR = "data/uploads"
REPORT_DIR = "data/reports"

PROTECTED_HINTS = {
    "gender",
    "sex",
    "age",
    "age_group",
    "race",
    "ethnicity",
    "religion",
    "disability",
    "nationality",
    "citizenship",
    "marital",
    "pregnancy",
}

IDENTIFIER_HINTS = {
    "id",
    "identifier",
    "uuid",
    "applicant_id",
    "candidate_id",
    "employee_id",
    "user_id",
    "record_id",
}

MERIT_BASED_HINTS = {
    "education",
    "degree",
    "experience",
    "salary",
    "compensation",
    "skill",
    "skills",
    "score",
    "merit",
    "qualification",
    "certification",
    "performance",
    "tenure",
    "interview",
    "assessment",
}

STRONG_PROXY_HINTS = {
    "zip",
    "postal",
    "postcode",
    "address",
    "city",
    "state",
    "name",
    "surname",
    "nationality",
    "citizenship",
}


def ensure_data_dirs() -> None:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)


def load_dataset(filepath: str) -> pd.DataFrame:
    ext = os.path.splitext(filepath)[1].lower()

    if ext in [".xlsx", ".xls"]:
        try:
            return pd.read_excel(filepath)
        except ImportError as exc:
            raise ImportError(
                "Excel upload requires openpyxl. Run: .\\.venv\\Scripts\\python.exe -m pip install openpyxl"
            ) from exc

    return pd.read_csv(filepath)


def json_safe(value: Any) -> Any:
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        return value.item()

    return value


def normalize_column_name(column: str) -> str:
    return str(column).strip().lower().replace(" ", "_")


def is_identifier_column(column: str) -> bool:
    key = normalize_column_name(column)
    return any(hint == key or hint in key for hint in IDENTIFIER_HINTS)


def is_merit_based_column(column: str) -> bool:
    key = normalize_column_name(column)
    return any(hint in key for hint in MERIT_BASED_HINTS)


def is_protected_column(column: str) -> bool:
    key = normalize_column_name(column)
    return any(hint == key or key.endswith(f"_{hint}") or hint in key for hint in PROTECTED_HINTS)


def is_strong_proxy_column(column: str) -> bool:
    key = normalize_column_name(column)
    return any(hint in key for hint in STRONG_PROXY_HINTS)


def is_continuous_numeric(series: pd.Series) -> bool:
    if not pd.api.types.is_numeric_dtype(series):
        return False

    non_null = series.dropna()
    if non_null.empty:
        return False

    unique_count = non_null.nunique()
    if unique_count >= 15:
        return True

    return unique_count >= max(8, int(len(non_null) * 0.1))


def sanitize_findings(findings: list[dict], columns: list[str], outcome_column: str) -> list[dict]:
    valid_columns = {str(col): col for col in columns}
    seen = set()
    cleaned = []

    for finding in findings or []:
        raw_column = str(finding.get("column", "")).strip()
        if raw_column not in valid_columns:
            continue
        column = valid_columns[raw_column]
        if column == outcome_column:
            continue
        if is_identifier_column(column):
            continue

        finding_type = str(finding.get("type", "proxy")).lower()
        if finding_type == "sensitive" and not is_protected_column(column):
            if is_merit_based_column(column):
                continue
            finding_type = "proxy" if is_strong_proxy_column(column) else ""
        elif finding_type == "proxy" and is_merit_based_column(column) and not is_strong_proxy_column(column):
            continue

        if not finding_type:
            continue

        key = (column, finding_type)
        if key in seen:
            continue
        seen.add(key)
        cleaned.append({
            "column": column,
            "type": finding_type,
            "reason": str(finding.get("reason", "Potential fairness-relevant column.")),
            "source": str(finding.get("source", "FairLens")),
            "confidence": str(finding.get("confidence", "Medium")),
            "recommended": finding_type == "sensitive",
        })

    return cleaned


def default_audit_columns(findings: list[dict], df: pd.DataFrame, outcome_column: str) -> list[str]:
    selected = []

    for finding in findings:
        column = finding.get("column")
        if not column or column == outcome_column or column not in df.columns:
            continue
        if not finding.get("recommended"):
            continue
        if is_identifier_column(column):
            continue
        if finding.get("type") == "sensitive":
            selected.append(column)

    filtered = []
    for column in selected:
        if column not in df.columns:
            continue
        if is_continuous_numeric(df[column]):
            # Keep continuous protected fields visible in scan, but do not auto-audit them with DI.
            continue
        filtered.append(column)

    return filtered


def filter_core_audit_columns(selected_columns: list[str], findings: list[dict], df: pd.DataFrame, outcome_column: str) -> list[str]:
    finding_by_column = {item.get("column"): item for item in findings or []}
    filtered = []

    for column in selected_columns or []:
        if column not in df.columns or column == outcome_column:
            continue
        if is_identifier_column(column):
            continue

        finding = finding_by_column.get(column, {})
        finding_type = str(finding.get("type", "")).lower()

        if finding_type != "sensitive":
            continue
        if is_continuous_numeric(df[column]):
            continue

        filtered.append(column)

    return filtered


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
