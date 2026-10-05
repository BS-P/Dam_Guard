from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_report_pdf(project_data: dict, run_data: dict, output_path: str) -> str:
    """
    Generates a professional PDF report with project overview, inundation summary, 
    exposure and loss summary.
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    story.append(Paragraph(f"BREACHSCOPE Report: {project_data.get('name', 'Project')}", styles['Title']))
    story.append(Spacer(1, 12))
    
    # Project Overview
    story.append(Paragraph("Project Overview", styles['Heading1']))
    story.append(Paragraph(project_data.get('description', 'No description provided.'), styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Run Summary
    story.append(Paragraph("Inundation Summary", styles['Heading1']))
    story.append(Paragraph(f"Run ID: {run_data.get('run_id', 'N/A')}", styles['Normal']))
    story.append(Paragraph(f"Max Depth: {run_data.get('max_depth', 'N/A')} m", styles['Normal']))
    story.append(Paragraph(f"Flooded Area: {run_data.get('flooded_area', 'N/A')} sq km", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Disclaimer
    story.append(Paragraph("Disclaimer", styles['Heading1']))
    story.append(Paragraph("This report is generated for planning purposes. All results are estimations.", styles['Normal']))
    
    doc.build(story)
    return output_path
