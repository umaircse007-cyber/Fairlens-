import pandas as pd
import numpy as np

def calculate_demographic_parity(df, sensitive_column, outcome_column):
    return df.groupby(sensitive_column)[outcome_column].mean().to_dict()

def calculate_disparate_impact_ratio(df, sensitive_column, outcome_column, privileged_group):
    rates = df.groupby(sensitive_column)[outcome_column].mean()
    if privileged_group not in rates or rates[privileged_group] == 0:
        return 1.0
    privileged_rate = rates[privileged_group]
    unprivileged_rate = rates[rates.index != privileged_group].mean()
    return unprivileged_rate / privileged_rate

def calculate_feature_influence(df, outcome_column):
    scores = {}
    numeric_df = df.select_dtypes(include=[np.number])
    if outcome_column in numeric_df.columns:
        correlations = numeric_df.corr()[outcome_column].drop(outcome_column)
        for col, val in correlations.items():
            if not pd.isna(val):
                scores[col] = float(abs(val))
    return dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))

def run_metrics(filepath, sensitive_columns, outcome_column, privileged_groups):
    df = pd.read_csv(filepath)
    results = {
        "demographic_parity": {},
        "disparate_impact_ratio": {},
        "feature_influence": calculate_feature_influence(df, outcome_column)
    }
    
    for sc in sensitive_columns:
        if sc in df.columns:
            results["demographic_parity"][sc] = calculate_demographic_parity(df, sc, outcome_column)
            priv_group = privileged_groups.get(sc)
            if priv_group is not None:
                results["disparate_impact_ratio"][sc] = calculate_disparate_impact_ratio(df, sc, outcome_column, priv_group)
            
    return results
