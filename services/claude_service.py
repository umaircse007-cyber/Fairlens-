import os
import json
from anthropic import Anthropic

def validate_findings_with_claude(columns: list, samples: dict, gemini_findings: list):
    client = Anthropic(api_key=os.environ.get("CLAUDE_API_KEY", ""))
    
    prompt = f"""
    You are a secondary AI validation bot for algorithmic fairness.
    Another AI (Gemini) scanned the following column samples:
    {json.dumps(samples, indent=2)}
    
    Gemini's findings:
    {json.dumps(gemini_findings, indent=2)}
    
    Your task:
    1. Validate Gemini's detections.
    2. Identify anything Gemini missed (columns that are sensitive or proxies).
    3. Assign a confidence score (High, Medium, Low) to each finding.
    
    Return a unified JSON array containing your assessment (do not include markdown wrapping):
    [
      {{
         "column": "column_name",
         "type": "sensitive|proxy",
         "reason": "Plain English reason",
         "source": "Gemini|Claude|Both",
         "confidence": "High|Medium|Low"
      }}
    ]
    Return ONLY a valid JSON list.
    """
    
    try:
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.content[0].text.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
        return json.loads(text)
    except Exception as e:
        print("Claude validation error:", e)
        return []

def analyze_counterfactual(flip_rate: float, severity: str):
    client = Anthropic(api_key=os.environ.get("CLAUDE_API_KEY", ""))
    prompt = f"""
    You are an AI auditor. A counterfactual flip test (changing sensitive attribute and checking outcome change) 
    resulted in a flip rate of {flip_rate:.2f}% and is rated as {severity} severity.
    Does this constitute direct or indirect discrimination? Interpret this in 2-3 plain English sentences for a non-technical manager.
    """
    try:
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()
    except Exception as e:
        print("Claude CF error:", e)
        return "Unable to generate interpretation."

def interpret_eu_clauses(triggered_clauses: list, audit_context: str):
    client = Anthropic(api_key=os.environ.get("CLAUDE_API_KEY", ""))
    prompt = f"""
    You are an AI legal assistant specializing in the EU AI Act.
    The dataset has triggered these clauses: {json.dumps([c['clause'] for c in triggered_clauses])}.
    Audit context: {audit_context}
    
    For each triggered clause, write a 2-sentence plain English legal explanation specific to this dataset.
    Return JSON format without markdown wrappers:
    {{
        "Clause Number": "explanation"
    }}
    Return ONLY valid JSON.
    """
    try:
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.content[0].text.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
        return json.loads(text)
    except Exception as e:
        print("Claude EU error:", e)
        return {}

def generate_report_sections(audit_results: dict):
    client = Anthropic(api_key=os.environ.get("CLAUDE_API_KEY", ""))
    prompt = f"""
    You are an AI auditor. Based on the following audit data, write a structured report with these exact sections:
    1. Executive Summary (2-3 sentences)
    2. Bias Findings (what was found, which groups affected)
    3. Legal Risk Assessment (which EU AI Act clauses triggered and why)
    4. Recommended Actions (what to do next)
    
    Audit Data: {json.dumps(audit_results)}
    
    Output JSON format without markdown wrapping:
    {{
        "Executive Summary": "...",
        "Bias Findings": "...",
        "Legal Risk Assessment": "...",
        "Recommended Actions": "..."
    }}
    Return ONLY valid JSON.
    """
    try:
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.content[0].text.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
        return json.loads(text)
    except Exception as e:
        print("Claude Report error:", e)
        return {}
