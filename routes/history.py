from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session
from database import get_db, AuditHistory

router = APIRouter()

@router.post("/")
async def save_audit(
    filename: str = Body(...),
    compliance_status: str = Body(...),
    clause_count: int = Body(...),
    db: Session = Depends(get_db)
):
    audit = AuditHistory(
        filename=filename,
        compliance_status=compliance_status,
        clause_count=clause_count
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return {"status": "saved", "id": audit.id}

@router.get("/list")
async def get_audits(db: Session = Depends(get_db)):
    audits = db.query(AuditHistory).order_by(AuditHistory.timestamp.desc()).all()
    return audits
