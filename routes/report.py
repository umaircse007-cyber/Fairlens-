from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import FileResponse
from services.groq_service import generate_report_sections
from services.report_service import create_pdf_report
import json
import os

router = APIRouter()

@router.post("/")
async def generate_report(file_id: str = Body(...)):
    def load_if_exists(filepath):
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                return json.load(f)
        return {}

    metrics = load_if_exists(f"data/uploads/{file_id}_metrics.json")
    cf_data = load_if_exists(f"data/uploads/{file_id}_cf.json")
    findings = load_if_exists(f"data/uploads/{file_id}_findings.json")
    eu_clauses = load_if_exists(f"data/uploads/{file_id}_eu.json")
        
    audit_results = {
        "metrics": metrics,
        "counterfactual_flip_rate": cf_data.get("flip_rate", 0),
        "dual_bot_findings": findings,
        "eu_clauses_triggered": eu_clauses
    }
    
    sections = generate_report_sections(audit_results)
    pdf_path = create_pdf_report(sections, file_id)
    
    return {"pdf_path": f"/api/report/download/{file_id}"}

@router.get("/download/{file_id}")
async def download_report(file_id: str):
    filepath = f"data/reports/{file_id}_report.pdf"
    if not os.path.exists(filepath):
        raise HTTPException(404, "Report not found")
    return FileResponse(filepath, media_type="application/pdf", filename="FairLens_Audit_Report.pdf")
