import pandas as pd

from services.dataset_service import load_dataset


MIN_GROUP_FLOOR = 5


def _coerce_favorable(series: pd.Series, favorable_value):
    if pd.api.types.is_numeric_dtype(series):
        try:
            if "." in str(favorable_value):
                return float(favorable_value)
            return int(favorable_value)
        except Exception:
            return favorable_value
    return str(favorable_value)


def _positive_mask(series: pd.Series, favorable_value) -> pd.Series:
    favorable = _coerce_favorable(series, favorable_value)
    if pd.api.types.is_numeric_dtype(series):
        return series == favorable
    return series.astype(str).str.strip().str.lower() == str(favorable).strip().lower()


def _encode_for_correlation(df: pd.DataFrame, outcome_column: str, favorable_value) -> pd.DataFrame:
    encoded = pd.DataFrame(index=df.index)
    encoded["__outcome__"] = _positive_mask(df[outcome_column], favorable_value).astype(int)

    for col in df.columns:
        if col == outcome_column:
            continue
        series = df[col]
        if pd.api.types.is_numeric_dtype(series):
            encoded[col] = pd.to_numeric(series, errors="coerce")
        else:
            codes, _ = pd.factorize(series.astype(str), sort=True)
            encoded[col] = codes

    return encoded


def _is_continuous_column(series: pd.Series) -> bool:
    if not pd.api.types.is_numeric_dtype(series):
        return False

    non_null = series.dropna()
    if non_null.empty:
        return False

    unique_count = non_null.nunique()
    return unique_count >= max(10, int(len(non_null) * 0.2))


def _min_group_size(total_rows: int) -> int:
    return max(MIN_GROUP_FLOOR, int(total_rows * 0.02))


def calculate_fairness_metrics(filepath, sensitive_columns, outcome_column, favorable_value):
    df = load_dataset(filepath)

    if df.empty or outcome_column not in df.columns:
        return {
            "demographic_parity": {},
            "disparate_impact_ratio": {},
            "feature_influence": {},
            "plain_language": [],
            "overall_status": "Insufficient Data",
        }

    sensitive_columns = [c for c in sensitive_columns if c in df.columns and c != outcome_column]
    df = df.dropna(subset=sensitive_columns + [outcome_column])

    if df.empty or not sensitive_columns:
        return {
            "demographic_parity": {},
            "disparate_impact_ratio": {},
            "feature_influence": {},
            "plain_language": ["No selected sensitive columns were available for audit."],
            "overall_status": "Insufficient Data",
        }

    positive = _positive_mask(df[outcome_column], favorable_value)
    demographic_parity = {}
    disparate_impact_ratio = {}
    plain_language = []
    failing_columns = []

    for col in sensitive_columns:
        group_rows = []
        rates = {}
        valid_rates = {}
        skipped_groups = []

        if _is_continuous_column(df[col]):
            plain_language.append(
                f"{col} looks like a continuous numeric field, so FairLens skipped disparate impact ratio for it and relies on association metrics instead."
            )
            demographic_parity[col] = group_rows
            continue

        min_group_size = _min_group_size(len(df))

        for group_value, group_df in df.groupby(col, dropna=False):
            mask = group_df.index
            favorable_count = int(positive.loc[mask].sum())
            total = int(len(group_df))
            rate = favorable_count / total if total else 0
            rates[str(group_value)] = rate
            if total >= min_group_size:
                valid_rates[str(group_value)] = rate
            else:
                skipped_groups.append(str(group_value))
            group_rows.append({
                "group": str(group_value),
                "total": total,
                "favorable": favorable_count,
                "rate": round(rate, 4),
                "percent": round(rate * 100, 1),
            })

        demographic_parity[col] = group_rows

        if len(valid_rates) >= 2:
            max_group = max(valid_rates, key=valid_rates.get)
            min_group = min(valid_rates, key=valid_rates.get)
            max_rate = valid_rates[max_group]
            min_rate = valid_rates[min_group]
            ratio = min_rate / max_rate if max_rate else 0
            gap = max_rate - min_rate

            disparate_impact_ratio[col] = {
                "ratio": round(ratio, 4),
                "percent": round(ratio * 100, 1),
                "passes_80_rule": ratio >= 0.8,
                "lowest_group": str(min_group),
                "highest_group": str(max_group),
                "lowest_rate": round(min_rate, 4),
                "highest_rate": round(max_rate, 4),
                "gap": round(gap, 4),
                "gap_points": round(gap * 100, 1),
                "min_group_size": min_group_size,
                "skipped_groups": skipped_groups,
            }

            if ratio < 0.8:
                failing_columns.append(col)

            plain_language.append(
                f"For {col}, {min_group} had a {min_rate * 100:.1f}% favorable outcome rate versus {max_group} at {max_rate * 100:.1f}%, a {gap * 100:.1f} point gap."
            )
        elif skipped_groups:
            plain_language.append(
                f"FairLens skipped disparate impact ratio for underpowered groups in {col}. Groups with fewer than {min_group_size} rows were excluded from the 80% rule calculation."
            )

    feature_influence = {}
    encoded = _encode_for_correlation(df, outcome_column, favorable_value)
    if len(encoded.columns) > 1:
        corr = encoded.corr(numeric_only=True)["__outcome__"].drop("__outcome__", errors="ignore")
        corr = corr.dropna().abs().sort_values(ascending=False)
        feature_influence = {
            str(k): round(float(v), 4)
            for k, v in corr.head(10).to_dict().items()
        }

    overall_status = "Fails 80% Rule" if failing_columns else "Passes 80% Rule"

    return {
        "demographic_parity": demographic_parity,
        "disparate_impact_ratio": disparate_impact_ratio,
        "feature_influence": feature_influence,
        "plain_language": plain_language,
        "overall_status": overall_status,
    }
