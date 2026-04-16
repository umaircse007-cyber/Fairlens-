from fastapi import APIRouter, Body, HTTPException
import json
import os
from services.metrics_service import run_metrics

router = APIRouter()

@router.post("/")
async def run_audit(
    file_id: str = Body(...),
    filename: str = Body(...),
    filepath: str = Body(...),
    sensitive_columns: list = Body(...),
    outcome_column: str = Body(...),
    privileged_groups: dict = Body(...)
):
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    metrics = run_metrics(filepath, sensitive_columns, outcome_column, privileged_groups)
    
    # Save run for report
    with open(f"data/uploads/{file_id}_metrics.json", "w") as f:
        json.dump(metrics, f)
        
    return {
        "status": "success",
        "metrics": metrics
    }
