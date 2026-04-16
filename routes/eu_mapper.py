from fastapi import APIRouter, Body
import json
from services.eu_mapper_service import map_eu_clauses

router = APIRouter()

@router.post("/")
async def eu_map(
    file_id: str = Body(...)
):
    with open(f"data/uploads/{file_id}_metrics.json", "r") as f:
        metrics = json.load(f)
        
    with open(f"data/uploads/{file_id}_cf.json", "r") as f:
        cf_data = json.load(f)
        
    with open(f"data/uploads/{file_id}_findings.json", "r") as f:
        findings = json.load(f)
        
    triggered_clauses = map_eu_clauses(metrics, cf_data["flip_rate"], findings)
    
    with open(f"data/uploads/{file_id}_eu.json", "w") as f:
        json.dump(triggered_clauses, f)
        
    return {"triggered_clauses": triggered_clauses}
