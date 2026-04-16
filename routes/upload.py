from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
import uuid
import os
from services.gemini_service import get_gemini_findings
from services.claude_service import validate_findings_with_claude

router = APIRouter()

@router.post("/")
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "File must be a CSV")
    
    file_id = str(uuid.uuid4())
    filepath = f"data/uploads/{file_id}_{file.filename}"
    with open(filepath, "wb") as f:
        f.write(await file.read())
        
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        raise HTTPException(400, f"Invalid CSV format: {e}")

    columns = df.columns.tolist()
    samples = {}
    for col in columns:
        samples[col] = df[col].dropna().head(5).tolist()
        
    gemini_findings = get_gemini_findings(columns, samples)
    final_findings = validate_findings_with_claude(columns, samples, gemini_findings)
    
    # Save findings for later use
    with open(f"data/uploads/{file_id}_findings.json", "w") as f:
        import json
        json.dump(final_findings, f)
        
    return {
        "file_id": file_id,
        "filename": file.filename,
        "filepath": filepath,
        "findings": final_findings
    }
