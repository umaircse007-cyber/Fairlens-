import pandas as pd

def run_counterfactual_test(filepath, sensitive_column, outcome_column):
    df = pd.read_csv(filepath)
    
    # We will do a simple mock decision rule based on majority features, or simple linear correlation
    # For a true flip test without a model, we can map closest neighbors and see if different sensitive attribute
    # yielded a different outcome. Or we simply train a fast simple DecisionTreeClassifier to act as the "rules".
    from sklearn.tree import DecisionTreeClassifier
    import category_encoders as ce
    
    # Prepare data
    X = df.drop(columns=[outcome_column])
    y = df[outcome_column]
    
    # Encode categorical
    encoder = ce.OrdinalEncoder()
    X_enc = encoder.fit_transform(X)
    
    model = DecisionTreeClassifier(max_depth=5, random_state=42)
    model.fit(X_enc, y)
    
    # Original predictions
    preds_original = model.predict(X_enc)
    
    flip_count = 0
    flipped_samples = []
    
    unique_vals = df[sensitive_column].unique()
    if len(unique_vals) < 2:
        return 0, [], "Low"
        
    X_flipped_enc = X_enc.copy()
    
    # Flip the sensitive attribute to another random category
    for idx, row in X.iterrows():
        orig_val = row[sensitive_column]
        new_val = next((v for v in unique_vals if v != orig_val), orig_val)
        X.at[idx, sensitive_column] = new_val
    
    X_flipped_enc = encoder.transform(X)
    preds_flipped = model.predict(X_flipped_enc)
    
    flip_mask = preds_original != preds_flipped
    flip_count = flip_mask.sum()
    flip_rate = (flip_count / len(df)) * 100
    
    # Gather 5 samples
    flipped_indices = df[flip_mask].index.tolist()[:5]
    for idx in flipped_indices:
        flipped_samples.append({
            "original_sensitive": str(df.at[idx, sensitive_column]),
            "flipped_sensitive": str(X.at[idx, sensitive_column]),
            "original_outcome": str(preds_original[idx]),
            "flipped_outcome": str(preds_flipped[idx])
        })
        
    if flip_rate < 10:
        severity = "Low"
    elif flip_rate <= 25:
        severity = "Medium"
    else:
        severity = "High"
        
    return flip_rate, flipped_samples, severity
