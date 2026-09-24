import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

BASE_DIR = Path(__file__).resolve().parent.parent
TXT_DIR = BASE_DIR / "data" / "sample_policies"
PDF_DIR = BASE_DIR / "data" / "policies_pdf"

TXT_DIR.mkdir(parents=True, exist_ok=True)
PDF_DIR.mkdir(parents=True, exist_ok=True)

POLICIES_DATA = [
    {
        "filename": "attendance_policy",
        "doc_type": "attendance_policy",
        "doc_title": "Student Attendance Policy and Absence Regulations",
        "sections": [
            ("SECTION 1: MANDATORY ATTENDANCE REQUIREMENTS", [
                "1.1 Students enrolled in undergraduate and postgraduate programs are expected to attend all scheduled lectures, tutorials, laboratory sessions, and seminars.",
                "1.2 A minimum cumulative attendance of 75% across all registered courses in a semester is strictly mandatory to maintain academic eligibility.",
                "1.3 Students falling between 65% and 74% attendance due to documented medical conditions or institutional representation must submit a formal condonation request to the Academic Dean within 5 working days of the absence."
            ]),
            ("SECTION 2: ABSENCE LIMITS AND COURSE WITHDRAWAL", [
                "2.1 If a student exceeds 6 consecutive unexcused absences in a single course, the Course Instructor is required to submit an Academic Advisory Warning to the Registrar.",
                "2.2 If a student's total attendance in a course drops below 60%, the student is automatically withdrawn from the course with a grade of 'W/F' (Withdrawn/Failed) and is ineligible to sit for the End-Semester Examination for that course.",
                "2.3 Maximum allowable medical leave in a single semester is 14 calendar days, subject to verified medical certification from an empaneled university physician."
            ]),
            ("SECTION 3: APPEALS AND CONDONATION PROCEDURE", [
                "3.1 Condonation for attendance shortage up to 10% may be granted by the Academic Dean upon payment of a condonation fee of $50 per course and submission of valid medical documentation.",
                "3.2 No condonation is permitted under any circumstances if attendance drops below 65%.",
                "3.3 Attendance records are updated weekly on the University Student Portal. Appeals regarding attendance discrepancies must be filed within 7 days of the portal update."
            ])
        ]
    },
    {
        "filename": "faculty_conduct_policy",
        "doc_type": "faculty_policy",
        "doc_title": "Faculty Code of Conduct and Professional Responsibilities",
        "sections": [
            ("SECTION 1: OFFICE HOURS AND STUDENT CONSULTATION", [
                "1.1 Full-time faculty members must hold a minimum of 4 scheduled office hours per week dedicated to student advisement and course consultation.",
                "1.2 Office hours must be posted on the course syllabus and uploaded to the Learning Management System (LMS) within the first week of the semester.",
                "1.3 Faculty members must respond to student emails and academic inquiries within 48 business hours."
            ]),
            ("SECTION 2: SYLLABUS DISTRIBUTION AND EVALUATION CRITERIA", [
                "2.1 Faculty members are required to distribute a comprehensive course syllabus during the first class session of the semester.",
                "2.2 The syllabus must clearly define grading criteria, examination schedules, assignment deadlines, and attendance rules.",
                "2.3 Any modification to the grading weights or exam dates during the semester requires written approval from the Department Head and unanimous consent of enrolled students."
            ]),
            ("SECTION 3: ACADEMIC INTEGRITY AND GRADING TIMELINES", [
                "3.1 Faculty members must evaluate and return mid-term examination results and feedback within 10 business days of exam completion.",
                "3.2 All cases of suspected academic misconduct, plagiarism, or exam cheating must be formally reported to the University Disciplinary Committee within 3 business days with supporting evidence.",
                "3.3 Faculty are strictly prohibited from accepting personal gifts valued over $25 from current students to prevent conflict of interest."
            ])
        ]
    },
    {
        "filename": "examination_grading_policy",
        "doc_type": "exam_regulation",
        "doc_title": "Examination Regulations, Grading Scale, and Academic Eligibility",
        "sections": [
            ("SECTION 1: GRADING SYSTEM AND CGPA REQUIREMENTS", [
                "1.1 Apex Academic University utilizes a 4.0 grading scale: Grade A (90-100%): 4.0 Grade Points (Excellent); Grade B (80-89%): 3.0 Grade Points (Good); Grade C (70-79%): 2.0 Grade Points (Satisfactory); Grade D (60-69%): 1.0 Grade Point (Passing); Grade F (<60%): 0.0 Grade Points (Failure).",
                "1.2 Undergraduate students must maintain a minimum Cumulative Grade Point Average (CGPA) of 2.0 to remain in Good Academic Standing.",
                "1.3 Postgraduate students must maintain a minimum CGPA of 3.0 for degree qualification."
            ]),
            ("SECTION 2: ACADEMIC PROBATION AND DISMISSAL", [
                "2.1 An undergraduate student whose CGPA drops below 2.0 at the end of any semester will be placed on Academic Probation for the subsequent semester.",
                "2.2 Students on Academic Probation are restricted to a maximum course load of 12 credit hours per semester.",
                "2.3 Failure to raise the CGPA to 2.0 after two consecutive semesters on Academic Probation results in Academic Dismissal from the university."
            ]),
            ("SECTION 3: RE-EXAMINATION AND MAKE-UP EXAMS", [
                "3.1 Make-up final examinations are granted solely for documented emergency hospitalizations or bereavement of an immediate family member.",
                "3.2 A student who fails a course with a Grade 'D' or 'F' may attempt a Re-Examination in the summer session, subject to a maximum grade cap of 'C' (2.0 GP).",
                "3.3 Applications for grade re-evaluation or re-checking must be submitted within 14 calendar days of grade publication, accompanied by a $30 processing fee per paper."
            ])
        ]
    },
    {
        "filename": "student_code_of_conduct",
        "doc_type": "code_of_conduct",
        "doc_title": "Student Code of Conduct and Disciplinary Rules",
        "sections": [
            ("SECTION 1: ACADEMIC MISCONDUCT AND PLAGIARISM", [
                "1.1 Academic dishonesty includes plagiarism, unauthorized collaboration, fabrication of data, and cheating during examinations.",
                "1.2 Plagiarism is defined as submitting work containing more than 15% uncredited similarity to external published or electronic sources.",
                "1.3 Penalties for plagiarism: First Offense: Zero marks on the assignment and a formal written warning placed in the student file. Second Offense: Automatic grade 'F' in the course. Third Offense: Formal referral to the Disciplinary Committee for university suspension or expulsion."
            ]),
            ("SECTION 2: CAMPUS BEHAVIOR AND DISCIPLINARY SUSPENSION", [
                "2.1 All university members have the right to a safe, respectful learning environment free from harassment, discrimination, or intimidation.",
                "2.2 The following situations result in immediate disciplinary suspension or expulsion: physical assault or threats of violence on campus, illegal substance distribution, unauthorized forced entry into university server rooms or administrative offices, and deliberate destruction or vandalism of university property exceeding $500.",
                "2.3 Destruction or vandalism of university property requires full financial restitution in addition to suspension sanctions."
            ])
        ]
    },
    {
        "filename": "graduate_assistantship_policy",
        "doc_type": "faculty_policy",
        "doc_title": "Graduate Assistantship & Research Regulations",
        "sections": [
            ("SECTION 1: ASSISTANTSHIP WORKLOAD & CGPA REQUIREMENT", [
                "1.1 Graduate Teaching Assistants (GTAs) and Research Assistants (GRAs) must enroll in at least 9 credit hours per semester.",
                "1.2 The maximum allowable workload for a Graduate Assistant appointment is 20 hours per week during regular Fall/Spring semesters.",
                "1.3 Graduate Assistants must maintain a minimum Cumulative GPA of 3.25. If CGPA drops below 3.25, the assistantship is placed on conditional probation for one semester."
            ]),
            ("SECTION 2: STIPEND & TUITION REMISSION BENEFITS", [
                "2.1 Full-time 20-hour Graduate Assistantships include a minimum monthly stipend of $2,200 plus 100% full tuition remission for up to 12 graduate credit hours.",
                "2.2 Mandatory university student fees (health fee, technology fee, activity fee) are not covered by tuition remission and remain the student's personal responsibility.",
                "2.3 Tuition remission benefits are credited within 10 business days following the execution of the Assistantship Contract."
            ])
        ]
    },
    {
        "filename": "financial_aid_scholarships",
        "doc_type": "general_handbook",
        "doc_title": "Financial Aid, Merit Scholarships, and Payment Regulations",
        "sections": [
            ("SECTION 1: MERIT SCHOLARSHIP ELIGIBILITY & RENEWAL", [
                "1.1 University Merit Scholarships require recipients to maintain a cumulative GPA of 3.50 or higher assessed at the end of each academic year.",
                "1.2 Scholarship recipients must complete a minimum of 30 credit hours per academic year. Dropping below 30 credit hours results in immediate scholarship forfeiture.",
                "1.3 FAFSA (Free Application for Federal Student Aid) priority submission deadline is March 1st for the upcoming academic year."
            ]),
            ("SECTION 2: TUITION PAYMENT INSTALLMENTS & LATE FEES", [
                "2.1 Tuition fees are payable in 3 equal monthly installments per semester.",
                "2.2 Failure to pay a tuition installment by the 5th calendar day of the month incurs an automatic late payment fee of $75.",
                "2.3 Unpaid balances exceeding 30 calendar days trigger an administrative financial hold on transcripts and registration."
            ])
        ]
    },
    {
        "filename": "housing_dormitory_rules",
        "doc_type": "code_of_conduct",
        "doc_title": "University Housing and Dormitory Residence Regulations",
        "sections": [
            ("SECTION 1: DORMITORY QUIET HOURS AND CURFEW", [
                "1.1 Mandatory quiet hours in all university residence halls are enforced from 10:00 PM to 7:00 AM Sunday through Thursday, and 12:00 AM to 8:00 AM Friday and Saturday.",
                "1.2 Non-resident visitors must sign in at the front desk and depart the residence hall by 11:00 PM daily. Overnight guests are restricted to a maximum of 3 consecutive nights with prior RA approval.",
                "1.3 Unauthorized room alterations, painting walls, or mounting heavy fixtures incur a $150 room restoration fee."
            ]),
            ("SECTION 2: PET AND HAZARD PROHIBITIONS", [
                "2.1 Pets are strictly prohibited in university housing, with the exception of certified service animals or small fish in aquariums under 5 gallons.",
                "2.2 Possession of open-flame devices, candles, incense, space heaters, or hot plates is prohibited in student dorm rooms."
            ])
        ]
    },
    {
        "filename": "library_research_access",
        "doc_type": "general_handbook",
        "doc_title": "University Library Regulations and Interlibrary Loans",
        "sections": [
            ("SECTION 1: BORROWING LIMITS AND OVERDUE FINES", [
                "1.1 Undergraduate students may check out up to 15 general collection books for a 21-day loan period.",
                "1.2 Graduate students and faculty members may check out up to 35 books for a 90-day loan period.",
                "1.3 Overdue fines for general collection items are assessed at $0.50 per item per calendar day up to a maximum cap of $25 per book."
            ]),
            ("SECTION 2: INTERLIBRARY LOANS AND RESERVE MATERIALS", [
                "2.1 Students in good standing may request up to 10 Interlibrary Loan (ILL) items per month free of charge.",
                "2.2 Course reserve items (textbooks placed on reserve by faculty) are restricted to 2-hour in-library use only. Overdue reserve items accrue fines at $2.00 per hour."
            ])
        ]
    },
    {
        "filename": "laboratory_safety_protocol",
        "doc_type": "general_handbook",
        "doc_title": "Laboratory Safety Protocols and Hazardous Waste Management",
        "sections": [
            ("SECTION 1: MANDATORY PERSONAL PROTECTIVE EQUIPMENT (PPE)", [
                "1.1 All students, researchers, and instructors entering wet laboratories must wear ANSI-approved safety goggles, chemical-resistant lab coats, and closed-toe shoes.",
                "1.2 Shorts, sandals, loose jewelry, and unconfined long hair are strictly prohibited in chemical and biological containment laboratories.",
                "1.3 Emergency eyewash stations and safety showers must be inspected monthly. In case of chemical contact, flush affected areas for a minimum of 15 continuous minutes."
            ]),
            ("SECTION 2: HAZARDOUS CHEMICAL DISPOSAL", [
                "2.1 Chemical waste must never be poured down laboratory sinks or drains. Waste must be segregated into clearly labeled hazardous waste containers.",
                "2.2 Chemical waste collection requests must be submitted to the Environmental Health & Safety (EHS) office when containers reach 80% capacity."
            ])
        ]
    },
    {
        "filename": "student_health_insurance",
        "doc_type": "general_handbook",
        "doc_title": "Student Health Center & Mandatory Insurance Waiver Rules",
        "sections": [
            ("SECTION 1: HEALTH INSURANCE REQUIREMENT & WAIVER DEADLINE", [
                "1.1 All full-time undergraduate and graduate students must maintain active health insurance coverage.",
                "1.2 Students with comparable private coverage must submit an online Health Insurance Waiver request by September 15th for Fall or January 31st for Spring.",
                "1.3 Failure to submit a verified waiver by the deadline results in automatic enrollment in the University Student Health Insurance Plan with a non-refundable $1,450 semester premium."
            ]),
            ("SECTION 2: IMMUNIZATION MANDATE AND CLINIC COPAYS", [
                "2.1 All matriculating students must submit verified immunization records for Measles, Mumps, Rubella (MMR) and Hepatitis B prior to class registration.",
                "2.2 Student Health Clinic primary care consultations require a nominal $15 copay per visit for enrolled students."
            ])
        ]
    },
    {
        "filename": "internship_career_services",
        "doc_type": "general_handbook",
        "doc_title": "Career Services, Academic Internships, and CPT Approval",
        "sections": [
            ("SECTION 1: CO-OP AND ACADEMIC INTERNSHIP CREDIT ELIGIBILITY", [
                "1.1 Undergraduate students must complete a minimum of 60 earned credit hours (Junior standing) before enrolling in academic internship credit.",
                "1.2 Internship credit requires a minimum cumulative GPA of 2.75 and approval from the Department Internship Coordinator prior to starting work hours.",
                "1.3 International students applying for Curricular Practical Training (CPT) must submit CPT authorization applications at least 30 calendar days before the internship start date."
            ]),
            ("SECTION 2: CAREER FAIR DRESS CODE AND NO-SHOW POLICY", [
                "2.1 Business Formal attire (suit, dress shirt, tie, formal dress) is strictly required for admission to University Career Fairs.",
                "2.2 Students who register for employer interviews and fail to attend without 24-hour prior cancellation incur a 30-day suspension from the career portal."
            ])
        ]
    },
    {
        "filename": "student_organizations_clubs",
        "doc_type": "general_handbook",
        "doc_title": "Student Organizations Chartering and Event Permits",
        "sections": [
            ("SECTION 1: CLUB CHARTERING REQUIREMENTS", [
                "1.1 New student organizations must maintain a minimum roster of 10 active student members and a full-time university faculty or staff advisor.",
                "1.2 All student club executive officers (President, Treasurer) must maintain a cumulative GPA of 2.50 or higher.",
                "1.3 Annual budget allocation requests for student organization funding must be submitted to the Student Government Association (SGA) by April 30th."
            ]),
            ("SECTION 2: ON-CAMPUS EVENT PERMITS AND SAFETY", [
                "2.1 On-campus events expecting over 50 attendees require an approved Campus Event Safety Permit submitted 14 business days in advance.",
                "2.2 Amplified sound outdoors is restricted to 12:00 PM - 1:00 PM and 5:00 PM - 10:00 PM weekdays."
            ])
        ]
    },
    {
        "filename": "technology_acceptable_use",
        "doc_type": "general_handbook",
        "doc_title": "Information Technology Acceptable Use & Wi-Fi Policy",
        "sections": [
            ("SECTION 1: NETWORK BANDWIDTH QUOTAS AND PROHIBITIONS", [
                "1.1 Campus wireless network usage is subject to a monthly data quota of 50 GB per student user account.",
                "1.2 Peer-to-peer (P2P) file sharing, torrenting, and distribution of copyrighted materials on university networks are strictly illegal and prohibited.",
                "1.3 Unauthorized network scanning, packet sniffing, or attempting to bypass campus firewalls results in immediate network account suspension."
            ]),
            ("SECTION 2: ACCOUNT DEACTIVATION", [
                "2.1 University email and network accounts are automatically deactivated 90 days following student graduation or formal withdrawal."
            ])
        ]
    },
    {
        "filename": "transfer_credit_evaluation",
        "doc_type": "exam_regulation",
        "doc_title": "Transfer Credit Evaluation and Advanced Placement Rules",
        "sections": [
            ("SECTION 1: TRANSFER CREDIT LIMITS AND GRADE THRESHOLD", [
                "1.1 Undergraduate students may transfer a maximum of 60 semester credit hours from accredited two-year community colleges or four-year universities.",
                "1.2 Only courses completed with a grade of 'C' (2.0 Grade Points) or higher are eligible for transfer credit acceptance.",
                "1.3 Official transcripts from previous institutions must be submitted along with a $40 transcript evaluation processing fee."
            ]),
            ("SECTION 2: ADVANCED PLACEMENT (AP) AND CLEP CREDIT", [
                "2.1 Advanced Placement (AP) examination scores of 4 or 5 qualify for equivalent introductory course credit as determined by department heads."
            ])
        ]
    },
    {
        "filename": "disability_accommodations",
        "doc_type": "general_handbook",
        "doc_title": "Student Disability Accommodation and Accessibility Services",
        "sections": [
            ("SECTION 1: ACCOMMODATION REQUEST DEADLINES AND DOCUMENTATION", [
                "1.1 Students requesting academic accommodations for documented disabilities must register with the Student Disability Services (SDS) office at least 3 weeks prior to the start of the semester.",
                "1.2 Standard examination accommodations include 1.5x extended exam time, reduced-distraction testing environments, and auxiliary note-taker assignment.",
                "1.3 Accommodation letters are issued directly to faculty; retroactively applying accommodations to completed exams or assignments is not permitted."
            ])
        ]
    }
]


def create_txt_and_pdf_policies():
    print(f"Generating {len(POLICIES_DATA)} comprehensive policy documents...")
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=colors.HexColor('#0F172A'), spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=colors.HexColor('#0D9488'), spaceAfter=10
    )
    section_style = ParagraphStyle(
        'SectionHeading', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11, leading=15, textColor=colors.HexColor('#1E293B'), spaceBefore=10, spaceAfter=4
    )
    body_style = ParagraphStyle(
        'BodyText', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=13, textColor=colors.HexColor('#334155'), spaceAfter=6
    )

    for p in POLICIES_DATA:
        fname = p["filename"]
        title = p["doc_title"]
        doc_type = p["doc_type"]
        sections = p["sections"]

        # 1. Generate TXT File
        txt_path = TXT_DIR / f"{fname}.txt"
        txt_content = []
        txt_content.append("=== ACADEMIC INSTITUTION POLICY DOCUMENT ===")
        txt_content.append(f"DOCUMENT TITLE: {title}")
        txt_content.append(f"DOCUMENT TYPE: {doc_type}")
        txt_content.append("EFFECTIVE DATE: Fall Semester 2025")
        txt_content.append("VERSION: 3.0")
        txt_content.append("INSTITUTION: Apex Academic University\n")

        for sec_name, clauses in sections:
            txt_content.append(sec_name)
            for c in clauses:
                txt_content.append(c)
            txt_content.append("")

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(txt_content))

        # 2. Generate PDF File
        pdf_path = PDF_DIR / f"{fname}.pdf"
        doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
        story = []
        story.append(Paragraph("APEX ACADEMIC UNIVERSITY", subtitle_style))
        story.append(Paragraph(title, title_style))
        story.append(Paragraph(f"DOCUMENT TITLE: {title}<br/>DOCUMENT TYPE: {doc_type}<br/>EFFECTIVE DATE: Fall Semester 2025 | VERSION: 3.0", body_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=10))

        for sec_name, clauses in sections:
            story.append(Paragraph(sec_name, section_style))
            for c in clauses:
                story.append(Paragraph(c, body_style))
            story.append(Spacer(1, 6))

        doc.build(story)
        print(f"  [OK] Generated: {fname}.txt and {fname}.pdf")

    print("\n[Done] All 15 policy documents generated successfully!")

if __name__ == "__main__":
    create_txt_and_pdf_policies()
