from fastapi import APIRouter, Body, HTTPException
import os
from services.counterfactual_service import run_counterfactual_test
from services.groq_service import analyze_counterfactual
import json

router = APIRouter()

@router.post("/")
async def run_counterfactual(
    file_id: str = Body(...),
    filepath: str = Body(...),
    sensitive_column: str = Body(...),
    outcome_column: str = Body(...)
):
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    flip_rate, samples, severity = run_counterfactual_test(filepath, sensitive_column, outcome_column)
    interpretation = analyze_counterfactual(flip_rate, severity)
    
    result = {
        "flip_rate": flip_rate,
        "severity": severity,
        "samples": samples,
        "interpretation": interpretation
    }
    
    with open(f"data/uploads/{file_id}_cf.json", "w") as f:
        json.dump(result, f)
        
    return result
