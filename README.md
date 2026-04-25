# FairLens

FairLens is an end-to-end AI fairness audit tool for decision datasets. It uploads CSV or Excel data, detects sensitive and proxy columns, runs fairness metrics, performs a counterfactual flip test, maps potential EU AI Act risks, applies a reweighing-based fix, and generates a plain-English PDF audit report.

## Features

- CSV and Excel upload
- Gemini-powered sensitive and proxy column scan with local fallback
- Groq-powered secondary validation and report language with local fallback
- Demographic parity checks
- Disparate impact ratio with the 80% rule
- Feature influence scoring
- Counterfactual flip testing
- Reweighing-based dataset correction
- Before and after fairness comparison
- Fixed CSV download
- PDF audit report download
- Audit history page

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\pip.exe install -r requirements.txt
copy .env.example .env
```

Add your API keys to `.env`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

The app still runs without keys by using deterministic fallback logic for demos.

## Run

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

## Project Structure

```text
frontend/      Static HTML, CSS, and browser workflow
routes/        FastAPI endpoints
services/      Fairness, AI scan, fix, report, and data services
data/uploads/  Local uploaded datasets, ignored by Git
data/reports/  Local generated PDF reports, ignored by Git
```

## Privacy Notes

Local uploads, generated reports, SQLite database files, logs, and `.env` secrets are ignored by Git.
