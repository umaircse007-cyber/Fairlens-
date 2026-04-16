from fastapi import APIRouter, Body, HTTPException
import json
import os
import pandas as pd
from services.metrics_service import run_metrics
from services.fix_service import apply_reweighing_and_resample

router = APIRouter()

@router.post("/")
async def apply_fix(
    file_id: str = Body(...),
    filepath: str = Body(...),
    sensitive_columns: list = Body(...),
    outcome_column: str = Body(...),
    privileged_groups: dict = Body(...),
    favorable_outcome: str = Body(...)
):
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    # Cast to int or float if it was numeric in original CSV but passed as string
    df = pd.read_csv(filepath)
    if not pd.api.types.is_string_dtype(df[outcome_column]) and favorable_outcome.isdigit():
        favorable_outcome = int(favorable_outcome)
        
    # Apply fix for the first sensitive column primarily, or iteratively.
    df_fixed = df.copy()
    for sc in sensitive_columns:
        df_fixed = apply_reweighing_and_resample(df_fixed, sc, outcome_column, favorable_outcome)
        
    fixed_filepath = f"data/uploads/{file_id}_fixed.csv"
    df_fixed.to_csv(fixed_filepath, index=False)
    
    # Recalculate metrics
    original_metrics = run_metrics(filepath, sensitive_columns, outcome_column, privileged_groups)
    fixed_metrics = run_metrics(fixed_filepath, sensitive_columns, outcome_column, privileged_groups)
    
    return {
        "original_metrics": original_metrics,
        "fixed_metrics": fixed_metrics,
        "fixed_filepath": fixed_filepath
    }
