import pandas as pd

def calculate_fairness_metrics(filepath, sensitive_columns, outcome_column, favorable_value):
    try:
        df = pd.read_csv(filepath)

        #  Basic validation
        if outcome_column not in df.columns:
            return {}

        for col in sensitive_columns:
            if col not in df.columns:
                return {}

        if len(df) == 0:
            return {}

        # Drop missing values (important)
        df = df.dropna(subset=sensitive_columns + [outcome_column])

        if len(df) == 0:
            return {}

        results = {}

        #1. Demographic Parity
        dp_results = {}

        for col in sensitive_columns:
            groups = df[col].unique()
            col_result = {}

            for g in groups:
                group_df = df[df[col] == g]

                if len(group_df) == 0:
                    continue

                rate = (group_df[outcome_column] == favorable_value).mean()
                col_result[str(g)] = round(float(rate), 3)

            dp_results[col] = col_result

        results["demographic_parity"] = dp_results

        #2. Disparate Impact Ratio
        di_results = {}

        for col in sensitive_columns:
            groups = df[col].unique()

            if len(groups) < 2:
                continue

            rates = {}

            for g in groups:
                group_df = df[df[col] == g]

                if len(group_df) == 0:
                    continue

                rate = (group_df[outcome_column] == favorable_value).mean()
                rates[g] = rate

            if len(rates) < 2:
                continue

            max_rate = max(rates.values())
            min_rate = min(rates.values())

            # Avoid division by zero
            if max_rate == 0:
                di = 0
            else:
                di = min_rate / max_rate

            di_results[col] = round(float(di), 3)

        results["disparate_impact_ratio"] = di_results

        #3. Feature Influence (safe correlation)
        numeric_df = df.select_dtypes(include=["number"])

        if outcome_column in numeric_df.columns and len(numeric_df.columns) > 1:
            corr = numeric_df.corr()

            if outcome_column in corr:
                influence = corr[outcome_column].drop(outcome_column)

                influence_dict = {
                    str(k): round(float(abs(v)), 3)
                    for k, v in influence.to_dict().items()
                }

                results["feature_influence"] = influence_dict
            else:
                results["feature_influence"] = {}
        else:
            results["feature_influence"] = {}

        return results

    except Exception as e:
        print("Metrics error:", e)
        return {}