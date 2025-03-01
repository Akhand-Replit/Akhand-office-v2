import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def create_report_pdf(reports):
    """Generate a PDF report from employee daily reports.
    
    Args:
        reports: List of report data tuples (employee_name, date, text, id, employee_id)
        
    Returns:
        bytes: PDF content as bytes
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Title
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,
        spaceAfter=12
    )
    elements.append(Paragraph(f"Work Reports: {reports[0][0]}", title_style))
    elements.append(Spacer(1, 12))
    
    # Date range
    date_style = ParagraphStyle(
        'DateRange',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,
        textColor=colors.gray
    )
    min_date = min(report[1] for report in reports).strftime('%d %b %Y')
    max_date = max(report[1] for report in reports).strftime('%d %b %Y')
    elements.append(Paragraph(f"Period: {min_date} to {max_date}", date_style))
    elements.append(Spacer(1, 20))
    
    # Group reports by month
    reports_by_month = {}
    for report in reports:
        month_year = report[1].strftime('%B %Y')
        if month_year not in reports_by_month:
            reports_by_month[month_year] = []
        reports_by_month[month_year].append(report)
    
    # Add each month's reports
    for month, month_reports in reports_by_month.items():
        # Month header
        month_style = ParagraphStyle(
            'Month',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10
        )
        elements.append(Paragraph(month, month_style))
        
        # Reports for the month
        for report in month_reports:
            # Date
            date_style = ParagraphStyle(
                'Date',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.blue
            )
            elements.append(Paragraph(report[1].strftime('%A, %d %b %Y'), date_style))
            
            # Report text
            text_style = ParagraphStyle(
                'ReportText',
                parent=styles['Normal'],
                fontSize=10,
                leftIndent=10
            )
            elements.append(Paragraph(report[2], text_style))
            elements.append(Spacer(1, 12))
        
        elements.append(Spacer(1, 10))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
