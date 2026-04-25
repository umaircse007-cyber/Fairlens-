import json
import os

from fastapi import APIRouter, Body, HTTPException

from services.metrics_service import calculate_fairness_metrics


router = APIRouter()


@router.post("/")
async def run_audit(
    file_id: str = Body(...),
    filepath: str = Body(...),
    sensitive_columns: list[str] = Body(default=[]),
    outcome_column: str = Body(...),
    favorable_value: str = Body(...),
):
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Dataset not found")

    if not sensitive_columns:
        raise HTTPException(status_code=400, detail="Select at least one sensitive or proxy column")

    metrics = calculate_fairness_metrics(
        filepath,
        sensitive_columns,
        outcome_column,
        favorable_value,
    )

    with open(f"data/uploads/{file_id}_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    return {
        "mode": "full_audit",
        "metrics": metrics,
    }
