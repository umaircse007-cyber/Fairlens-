import os
import json
import google.generativeai as genai

def get_gemini_findings(columns: list, samples: dict):
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
    You are an AI bias detector. 
    Analyze these dataset columns and 5 sample values for each:
    {json.dumps(samples, indent=2)}
    
    Identify any columns that might be:
    1. A sensitive attribute (race, gender, age, religion, etc.)
    2. A proxy column (a column that strongly correlates with a sensitive attribute, e.g. zip code matching with race)
    
    Format the response as JSON (do not include markdown wrapping like ```json):
    [
      {{
         "column": "column_name",
         "type": "sensitive|proxy",
         "reason": "Plain English reason for this flag."
      }}
    ]
    Return ONLY a valid JSON list.
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
        return json.loads(text)
    except Exception as e:
        print("Gemini error:", e)
        return []
