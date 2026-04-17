import os
import json
def safe_load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            print("Load error:", e)
            return default
    return default

def generate_report_data(file_id):
    try:
        base_path = "data/uploads"

        metrics = safe_load_json(f"{base_path}/{file_id}_metrics.json", {})
        cf_data = safe_load_json(f"{base_path}/{file_id}_cf.json", {})
        findings = safe_load_json(f"{base_path}/{file_id}_findings.json", [])
        eu_data = safe_load_json(f"{base_path}/{file_id}_eu.json", {})

        report = {
            "summary": {},
            "bias_findings": {},
            "counterfactual": {},
            "legal": {},
            "recommendations": []
        }

        #Summary
        dp = metrics.get("demographic_parity", {})
        di = metrics.get("disparate_impact_ratio", {})

        report["summary"] = {
            "demographic_parity": dp,
            "disparate_impact_ratio": di
        }

        #Bias findings
        report["bias_findings"] = {
            "sensitive_columns": findings
        }

        #Counterfactual
        report["counterfactual"] = cf_data if cf_data else {
            "flip_rate": 0,
            "severity": "Low",
            "samples": []
        }

        #Legal mapping
        report["legal"] = eu_data if eu_data else {
            "risk_level": "Low",
            "triggered_clauses": []
        }

        #Recommendations (simple + safe)
        recommendations = []

        if di:
            for col, value in di.items():
                if value < 0.8:
                    recommendations.append(
                        f"Potential bias detected in '{col}'. Consider rebalancing dataset."
                    )

        if cf_data.get("severity") == "High":
            recommendations.append(
                "High counterfactual sensitivity detected. Review model training data."
            )

        if not recommendations:
            recommendations.append("No major fairness risks detected.")

        report["recommendations"] = recommendations

        return report

    except Exception as e:
        print("Report generation error:", e)
        return {
            "summary": {},
            "bias_findings": {},
            "counterfactual": {},
            "legal": {},
            "recommendations": ["Unable to generate report."]
        }

    
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
def create_pdf_report(file_id, report_data):
    try:
        os.makedirs("data/reports", exist_ok=True)
        pdf_path = f"data/reports/{file_id}_report.pdf"

        doc = SimpleDocTemplate(pdf_path)
        styles = getSampleStyleSheet()

        elements = []

        # Title
        elements.append(Paragraph("FairLens Bias Audit Report", styles["Title"]))
        elements.append(Spacer(1, 12))

        # Sections
        for section, content in report_data.items():
            elements.append(Paragraph(f"<b>{section}</b>", styles["Heading2"]))
            elements.append(Spacer(1, 8))

            elements.append(Paragraph(str(content), styles["Normal"]))
            elements.append(Spacer(1, 12))

        doc.build(elements)

        return pdf_path

    except Exception as e:
        print("PDF error:", e)
        return None    