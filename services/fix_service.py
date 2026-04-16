import pandas as pd
import numpy as np

def apply_reweighing_and_resample(df, sensitive_column, outcome_column, favorable_outcome):
    weights = []
    p_fav = (df[outcome_column] == favorable_outcome).mean()
    p_unfav = 1 - p_fav
    
    for idx, row in df.iterrows():
        s_val = row[sensitive_column]
        o_val = row[outcome_column]
        
        p_s = (df[sensitive_column] == s_val).mean()
        p_s_and_o = ((df[sensitive_column] == s_val) & (df[outcome_column] == o_val)).mean()
        
        expected_prob = p_s * (p_fav if o_val == favorable_outcome else p_unfav)
        actual_prob = p_s_and_o
        
        if actual_prob > 0:
            weight = expected_prob / actual_prob
        else:
            weight = 1.0
        weights.append(weight)
        
    df_temp = df.copy()
    df_temp['sample_weight'] = weights
    
    df_fixed = df_temp.sample(n=len(df_temp), replace=True, weights='sample_weight', random_state=42)
    df_fixed = df_fixed.drop(columns=['sample_weight'])
    return df_fixed
