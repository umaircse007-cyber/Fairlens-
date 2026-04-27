# FairLens

**AI fairness auditing for decision datasets — no data science degree required.**

Most bias auditing tools tell you a problem exists. FairLens tells you exactly where it is, how bad it is, whether it breaks EU law, and hands you a corrected dataset to fix it — all in under 60 seconds.

🔗 **Live demo: [fairlens-2ggj.onrender.com](https://fairlens-2ggj.onrender.com)**

---

## The problem it solves

An HR manager uploads a hiring dataset. A loan officer submits approval records. A hospital admin shares patient triage outcomes. None of them have a data scientist on their team. They just need to know: *is this system treating people fairly?*

FairLens answers that question end-to-end — from raw file to signed-off PDF report — without requiring the user to write a single line of code.

---

## How it works

Upload a CSV or Excel file and FairLens runs a full audit pipeline:

| Step | What happens |
|---|---|
| **Scan** | Gemini and Groq independently detect sensitive attributes and proxy columns |
| **Measure** | Demographic parity, disparate impact ratio, and feature influence scores are computed |
| **Test** | Counterfactual flip test checks if changing only gender (or age) changes the outcome |
| **Fix** | A reweighing algorithm corrects the dataset; before/after metrics are compared side by side |
| **Report** | A plain-English PDF is generated with EU AI Act article mappings, ready to hand to legal |

The two-model approach — Gemini and Groq scanning independently — means findings come with a confidence level. Columns both models agree on are flagged **High Confidence**. Columns only one model catches are marked **Disputed**, so a human can make the final call rather than trusting a single AI blindly.

---

## Features

- CSV and Excel upload
- Gemini-powered sensitive and proxy column detection with local fallback
- Groq-powered secondary validation and report generation with local fallback
- Demographic parity checks across all protected groups
- Disparate impact ratio with 80% rule (EEOC / EU AI Act Article 10 standard)
- Feature influence scoring
- Counterfactual flip testing for individual fairness
- Reweighing-based dataset correction
- Before and after fairness metric comparison
- Corrected dataset download
- PDF audit report download
- Audit history page

---

## Fairness metrics

FairLens follows the same standards used by regulators and compliance teams.

**Disparate Impact Ratio** — outcome rate for the minority group divided by the outcome rate for the majority group. A ratio below 0.80 fails the 80% rule under EEOC guidelines and EU AI Act Article 10(2)(f). FairLens computes this per group, not per bucketed age range, to avoid false positives from empty buckets.

**Statistical Parity Difference** — the raw percentage point gap in outcome rates between groups. Reported alongside the DI ratio for context.

**Counterfactual Flip Rate** — the percentage of individuals whose outcome changes when only their protected attribute (gender, age, etc.) is altered and everything else stays the same. A high flip rate indicates the model is using protected characteristics as a decision factor, even indirectly. Protected attributes are excluded from model training so that a non-zero flip rate reflects data-level bias, not a measurement artifact.

---

## EU AI Act mapping

| Article | Topic | Triggered when |
|---|---|---|
| Article 10(2)(f) | Data governance | Disparate impact ratio fails the 80% rule |
| Article 13 | Transparency | Proxy columns detected that may conceal protected-group effects |

---

## Running locally

**1. Clone the repository**

```bash
git clone https://github.com/umaircse007-cyber/Fairlens-.git
cd Fairlens-
```

**2. Create a virtual environment and install dependencies**

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\pip.exe install -r requirements.txt

# macOS / Linux
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

**3. Set up environment variables**

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and add your keys:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

The app works without API keys — deterministic fallback logic runs automatically, which is useful for demos and local testing.

**4. Start the server**

```bash
# Windows
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000

# macOS / Linux
.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## Deployment

The app is live at [fairlens-2ggj.onrender.com](https://fairlens-2ggj.onrender.com), deployed on Render via the included `render.yaml`.

To deploy your own instance:

1. Push the repository to GitHub
2. In Render, go to **New → Blueprint** and connect the repo
3. Render picks up the build and start commands from `render.yaml` automatically
4. Add your environment variables in the Render dashboard — never in the codebase

```
GEMINI_API_KEY=
GROQ_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
```

---

## Project structure

```
FairLens/
├── frontend/          # Static HTML, CSS, and browser-side workflow
├── routes/            # FastAPI route handlers
├── services/          # Fairness metrics, AI scan, fix, report, and data services
├── data/
│   ├── uploads/       # Uploaded datasets (git-ignored)
│   └── reports/       # Generated PDF reports (git-ignored)
├── main.py            # App entry point
├── render.yaml        # Render deployment config
├── requirements.txt
└── .env.example
```

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, Uvicorn |
| AI scanning | Google Gemini 2.5 Flash, Groq |
| Fairness engine | pandas, scikit-learn, scipy |
| Report generation | ReportLab |
| Frontend | HTML, CSS, JavaScript |
| Deployment | Render |

---

## Privacy

Uploaded files, generated reports, the audit history database, logs, and `.env` secrets are all excluded from Git. When API keys are present, only column headers and a small sample of anonymised values are sent to Gemini and Groq for scanning — full rows are never transmitted.

---

## Contributing

Issues and pull requests are welcome. For significant changes, open an issue first to discuss the approach.

---

## License

MIT
