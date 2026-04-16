from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os

def create_pdf_report(report_data: dict, file_id: str):
    filename = f"data/reports/{file_id}_report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    Story = []
    
    title_style = styles['Heading1']
    heading_style = styles['Heading2']
    normal_style = styles['BodyText']
    
    Story.append(Paragraph("FairLens Audit Report", title_style))
    Story.append(Spacer(1, 12))
    
    sections = [
        ("Executive Summary", report_data.get("Executive Summary", "N/A")),
        ("Bias Findings", report_data.get("Bias Findings", "N/A")),
        ("Legal Risk Assessment", report_data.get("Legal Risk Assessment", "N/A")),
        ("Recommended Actions", report_data.get("Recommended Actions", "N/A"))
    ]
    
    for section_title, content in sections:
        Story.append(Paragraph(section_title, heading_style))
        Story.append(Spacer(1, 6))
        Story.append(Paragraph(str(content), normal_style))
        Story.append(Spacer(1, 12))
        
    doc.build(Story)
    return filename
