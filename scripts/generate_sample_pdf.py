import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PDF = BASE_DIR / "sample_academic_policy.pdf"

def generate_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=letter,
        rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#0D9488'),
        spaceAfter=12
    )

    section_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )

    story = []

    # Title & Metadata Header
    story.append(Paragraph("APEX ACADEMIC UNIVERSITY", subtitle_style))
    story.append(Paragraph("Official Policy: Graduate Assistantship & Tuition Remission Regulations", title_style))
    story.append(Paragraph("DOCUMENT TITLE: Graduate Assistantship and Research Regulations<br/>DOCUMENT TYPE: faculty_policy<br/>EFFECTIVE DATE: Fall Semester 2025<br/>VERSION: 4.2", body_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=12))

    # Section 1
    story.append(Paragraph("SECTION 1: GRADUATE ASSISTANTSHIP ELIGIBILITY & WORKLOAD", section_style))
    story.append(Paragraph("1.1 Graduate Teaching Assistants (GTAs) and Graduate Research Assistants (GRAs) must maintain full-time enrollment of at least 9 credit hours per semester during the academic year.", body_style))
    story.append(Paragraph("1.2 The maximum allowable appointment workload for a Graduate Assistant is 20 hours per week during regular Fall and Spring semesters. Overtime beyond 20 hours requires prior written authorization from the Graduate Dean.", body_style))
    story.append(Paragraph("1.3 Graduate Assistants must maintain a minimum Cumulative GPA of 3.25. If the CGPA drops below 3.25, the assistantship is placed on conditional probation for one semester.", body_style))

    story.append(Spacer(1, 10))

    # Section 2
    story.append(Paragraph("SECTION 2: STIPEND RATES AND TUITION REMISSION", section_style))
    story.append(Paragraph("2.1 Full-time 20-hour Graduate Assistantships include a minimum monthly stipend of $2,200 plus 100% full tuition remission for up to 12 graduate credit hours per semester.", body_style))
    story.append(Paragraph("2.2 University mandatory student fees (health fee, technology fee, activity fee) are not covered by tuition remission and remain the personal financial responsibility of the student.", body_style))
    story.append(Paragraph("2.3 Tuition remission benefits are applied to the student financial account within 10 business days following the formal execution of the Assistantship Contract.", body_style))

    story.append(Spacer(1, 10))

    # Section 3
    story.append(Paragraph("SECTION 3: LEAVE POLICIES AND TERMINATION CONDITIONS", section_style))
    story.append(Paragraph("3.1 Graduate Assistants are entitled to 5 paid leave business days per semester for personal illness or family emergencies, subject to approval by the Faculty Advisor.", body_style))
    story.append(Paragraph("3.2 Assistantship contracts may be terminated immediately for cause in cases of gross neglect of duty, violation of university code of conduct, or academic misconduct.", body_style))

    doc.build(story)
    print(f"Generated sample PDF at: {OUTPUT_PDF}")

if __name__ == "__main__":
    generate_pdf()
