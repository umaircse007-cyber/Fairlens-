import os
import json
from groq import Groq


def safe_json_parse(text, fallback):
    try:
        return json.loads(text)
    except Exception as e:
        print("JSON parse error:", e)
        return fallback


def clean_response(text):
    if not text:
        return ""

    text = text.strip()

    if text.startswith("```json"):
        text = text[7:-3].strip()
    elif text.startswith("```"):
        text = text[3:-3].strip()

    return text


def get_client():
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY not set")

    return Groq(api_key=api_key)


# ✅ 1. VALIDATE FINDINGS
def validate_findings_with_claude(columns, samples, gemini_findings):
    try:
        client = get_client()

        prompt = f"""
You are an AI fairness validator.

DATA:
{json.dumps(samples, indent=2)}

GEMINI FINDINGS:
{json.dumps(gemini_findings, indent=2)}

TASK:
- Validate findings
- Add missing ones
- Assign confidence

Return ONLY JSON:
[
  {{
    "column": "name",
    "type": "sensitive|proxy",
    "reason": "explanation",
    "source": "Gemini|Groq|Both",
    "confidence": "High|Medium|Low"
  }}
]
"""

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        text = response.choices[0].message.content
        text = clean_response(text)

        parsed = safe_json_parse(text, gemini_findings)

        return parsed if parsed else gemini_findings

    except Exception as e:
        print("Groq validation error:", e)
        return gemini_findings


# ✅ 2. COUNTERFACTUAL INTERPRETATION
def analyze_counterfactual(flip_rate: float, severity: str):
    try:
        client = get_client()

        prompt = f"""
Flip rate: {flip_rate:.2f}%
Severity: {severity}

Explain in 2-3 simple sentences if this indicates bias.
"""

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        if not response or not response.choices:
            return "Unable to generate interpretation."
        content = response.choices[0].message.content

        if not content:
            return "Unable to generate interpretation."

        return content.strip()

    except Exception as e:
        print("Groq CF error:", e)
        return "Unable to generate interpretation."


# ✅ 3. EU CLAUSE EXPLANATION
def interpret_eu_clauses(triggered_clauses: list, audit_context: str):
    try:
        client = get_client()

        clauses = [c["clause"] for c in triggered_clauses]

        prompt = f"""
Clauses: {clauses}
Context: {audit_context}

Explain each clause in simple terms.

Return JSON:
{{
  "Clause": "Explanation"
}}
"""

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        text = clean_response(response.choices[0].message.content)

        return safe_json_parse(text, {})

    except Exception as e:
        print("Groq EU error:", e)
        return {}


# ✅ 4. REPORT GENERATION
def generate_report_sections(audit_results: dict):
    try:
        client = get_client()

        prompt = f"""
Generate a structured audit report.

DATA:
{json.dumps(audit_results)}

Return JSON:
{{
  "Executive Summary": "...",
  "Bias Findings": "...",
  "Legal Risk Assessment": "...",
  "Recommended Actions": "..."
}}
"""

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        text = clean_response(response.choices[0].message.content)

        return safe_json_parse(text, {})

    except Exception as e:
        print("Groq report error:", e)
        return {}