from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

import io


def generate_class_report(session, student_data, metrics):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph(f"<b>Class Report: {session.title}</b>", styles["Title"]))
    elements.append(Paragraph(f"Subject: {session.subject}", styles["Normal"]))
    elements.append(Paragraph(f"Date: {session.date} | Time: {session.start_time} - {session.end_time}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Metrics
    elements.append(Paragraph(f"Total Students: {metrics['total_students']}", styles["Normal"]))
    elements.append(Paragraph(f"Attended: {metrics['attended']}", styles["Normal"]))
    elements.append(Paragraph(f"Absent: {metrics['absent']}", styles["Normal"]))
    elements.append(Paragraph(f"Average Engagement: {metrics['avg_engagement']}%", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Student Table
    data = [["Name", "Department", "Year", "Status", "Engagement %"]]
    for item in student_data:
        status = "Attended" if item["report"] else "Absent"
        engagement = item["report"].avg_engagement if item["report"] else "-"
        data.append([
            item["student"].user.username,
            item["student"].department,
            item["student"].year,
            status,
            engagement,
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def generate_student_report(session, student, report):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph(f"<b>Student Report</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    # Student Info
    elements.append(Paragraph(f"Student: {student.user.username}", styles["Normal"]))
    elements.append(Paragraph(f"Department: {student.department}", styles["Normal"]))
    elements.append(Paragraph(f"Year: {student.year}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Session Info
    elements.append(Paragraph(f"Class: {session.title}", styles["Normal"]))
    elements.append(Paragraph(f"Subject: {session.subject}", styles["Normal"]))
    elements.append(Paragraph(f"Date: {session.date} | Time: {session.start_time} - {session.end_time}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Engagement Info
    if report:
        elements.append(Paragraph(f"Average Engagement: {report.avg_engagement}%", styles["Normal"]))
        elements.append(Paragraph(f"Created At: {report.created_at}", styles["Normal"]))
    else:
        elements.append(Paragraph("No engagement data available.", styles["Normal"]))

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

