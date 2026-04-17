from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

#  Load environment variables
load_dotenv()

#  Create required directories (prevents crash)
os.makedirs("data/uploads", exist_ok=True)
os.makedirs("data/reports", exist_ok=True)

#  Initialize app
app = FastAPI(title="FairLens API")

#  CORS (useful for frontend requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # safe for hackathon
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  Import routes AFTER app creation (avoids circular issues)
from routes import (
    upload,
    audit,
    counterfactual,
    eu_mapper,
    fix,
    report,
    history,
)

#  Register routes
from routes import upload, audit, fix, report, history

app.include_router(upload.router, prefix="/upload")
app.include_router(audit.router, prefix="/audit")
app.include_router(fix.router, prefix="/fix")
app.include_router(report.router, prefix="/report")
app.include_router(history.router, prefix="/history")

#  Serve frontend safely
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="frontend")
else:
    print("⚠ Frontend folder not found")

#  Health check (VERY useful for demo)
@app.get("/health")
def health_check():
    return {"status": "ok"}

#  Root fallback (optional safety)
@app.get("/api")
def api_root():
    return {"message": "FairLens API running"}

from fastapi.responses import FileResponse
@app.get("/")
def serve_home():
    return FileResponse("frontend/upload.html")