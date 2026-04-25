import json
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from services.dataset_service import REPORT_DIR, UPLOAD_DIR, ensure_data_dirs
from services.groq_service import generate_report_sections


def safe_load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        print("Load JSON error:", exc)
        return default


def _stringify_report_value(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = []
        for item in value:
            parts.append(_stringify_report_value(item))
        return "; ".join(part for part in parts if part)
    if isinstance(value, dict):
        parts = []
        for key, item in value.items():
            parts.append(f"{key}: {_stringify_report_value(item)}")
        return "; ".join(part for part in parts if part)
    return str(value)


def _normalize_report_sections(sections: dict) -> dict:
    normalized = {}
    for title, body in (sections or {}).items():
        normalized[str(title)] = _stringify_report_value(body)
    return normalized


def generate_report_data(file_id):
    metrics = safe_load_json(f"{UPLOAD_DIR}/{file_id}_metrics.json", {})
    fixed_metrics = safe_load_json(f"{UPLOAD_DIR}/{file_id}_fixed_metrics.json", {})
    cf_data = safe_load_json(f"{UPLOAD_DIR}/{file_id}_cf.json", {})
    findings = safe_load_json(f"{UPLOAD_DIR}/{file_id}_findings.json", [])
    eu_data = safe_load_json(f"{UPLOAD_DIR}/{file_id}_eu.json", [])
    upload_meta = safe_load_json(f"{UPLOAD_DIR}/{file_id}_meta.json", {})

    audit_results = {
        "filename": upload_meta.get("filename", "Uploaded dataset"),
        "findings": findings,
        "metrics": metrics,
        "fixed_metrics": fixed_metrics,
        "counterfactual": cf_data,
        "eu_clauses": eu_data,
    }

    sections = _normalize_report_sections(generate_report_sections(audit_results))

    return {
        "filename": upload_meta.get("filename", "Uploaded dataset"),
        "sections": sections,
        "findings": findings,
        "metrics": metrics,
        "fixed_metrics": fixed_metrics,
        "counterfactual": cf_data,
        "eu_clauses": eu_data,
    }


def _paragraph(text, style):
    return Paragraph(str(text).replace("\n", "<br/>"), style)


def create_pdf_report(file_id, report_data):
    ensure_data_dirs()
    pdf_path = f"{REPORT_DIR}/{file_id}_report.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=42, leftMargin=42, topMargin=42, bottomMargin=42)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("FairLens Bias Audit Report", styles["Title"]))
    elements.append(Paragraph(report_data.get("filename", "Uploaded dataset"), styles["Normal"]))
    elements.append(Spacer(1, 18))

    for title, body in report_data.get("sections", {}).items():
        elements.append(Paragraph(title, styles["Heading2"]))
        elements.append(_paragraph(body, styles["BodyText"]))
        elements.append(Spacer(1, 12))

    findings = report_data.get("findings", [])
    if findings:
        elements.append(Paragraph("Flagged Columns", styles["Heading2"]))
        table_data = [["Column", "Type", "Confidence", "Reason"]]
        for item in findings:
            table_data.append([
                item.get("column", ""),
                item.get("type", ""),
                item.get("confidence", ""),
                item.get("reason", ""),
            ])
        table = Table(table_data, colWidths=[90, 70, 70, 270])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))

    clauses = report_data.get("eu_clauses", [])
    if clauses:
        elements.append(Paragraph("EU AI Act Risk Mapping", styles["Heading2"]))
        for clause in clauses:
            elements.append(_paragraph(f"{clause.get('clause')} - {clause.get('title')}: {clause.get('explanation')}", styles["BodyText"]))
            elements.append(Spacer(1, 6))

    doc.build(elements)
    return pdf_path
