from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from routes import upload, audit, fix, counterfactual, eu_mapper, report, history
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="FairLens API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("data/uploads", exist_ok=True)
os.makedirs("data/reports", exist_ok=True)

app.mount("/static", StaticFiles(directory="frontend"), name="static")
templates = Jinja2Templates(directory="frontend")

app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(audit.router, prefix="/api/audit", tags=["Audit"])
app.include_router(fix.router, prefix="/api/fix", tags=["Fix"])
app.include_router(counterfactual.router, prefix="/api/counterfactual", tags=["Counterfactual"])
app.include_router(eu_mapper.router, prefix="/api/eu-map", tags=["EU AI Act"])
app.include_router(report.router, prefix="/api/report", tags=["Report"])
app.include_router(history.router, prefix="/api/history", tags=["History"])

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.get("/results")
def results(request: Request):
    return templates.TemplateResponse("results.html", {"request": request})

@app.get("/view-history")
def get_history(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})
