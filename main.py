import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from services.dataset_service import ensure_data_dirs


load_dotenv()
ensure_data_dirs()

app = FastAPI(title="FairLens API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routes import audit, counterfactual, eu_mapper, fix, history, report, upload

app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(audit.router, prefix="/audit", tags=["Audit"])
app.include_router(counterfactual.router, prefix="/counterfactual", tags=["Counterfactual"])
app.include_router(eu_mapper.router, prefix="/eu-mapper", tags=["EU Mapper"])
app.include_router(fix.router, prefix="/fix", tags=["Fix"])
app.include_router(report.router, prefix="/report", tags=["Report"])
app.include_router(history.router, prefix="/history", tags=["History"])
app.include_router(history.router, prefix="/api/history", tags=["History"])

if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="frontend")


@app.get("/")
def upload_page():
    return FileResponse("frontend/upload.html")


@app.get("/upload.html")
def upload_html():
    return FileResponse("frontend/upload.html")


@app.get("/results")
@app.get("/results.html")
def results_page():
    return FileResponse("frontend/results.html")


@app.get("/view-history")
@app.get("/history.html")
def history_page():
    return FileResponse("frontend/history.html")


@app.get("/download/fixed/{file_id}")
def download_fixed(file_id: str):
    path = f"data/uploads/{file_id}_fixed.csv"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Fixed dataset not found")
    return FileResponse(path, media_type="text/csv", filename=f"fairlens_fixed_{file_id}.csv")


@app.get("/download/report/{file_id}")
def download_report(file_id: str):
    path = f"data/reports/{file_id}_report.pdf"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(path, media_type="application/pdf", filename=f"fairlens_report_{file_id}.pdf")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/api")
def api_root():
    return {"message": "FairLens API running"}
