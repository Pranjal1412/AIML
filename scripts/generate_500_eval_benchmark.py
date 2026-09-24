import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = BASE_DIR / "data" / "eval_dataset_500.jsonl"

DOMAINS = [
    "Attendance Policy",
    "Faculty Conduct Policy",
    "Exam & Grading Policy",
    "Student Code of Conduct",
    "Graduate Assistantship Policy",
    "Financial Aid Policy",
    "Housing & Dorm Rules",
    "Library Research Access",
    "Lab Safety Protocol",
    "Student Health Insurance",
    "Career Services & Internships",
    "Student Clubs & Organizations",
    "Technology Acceptable Use",
    "Transfer Credit Evaluation",
    "Disability Accommodations"
]

def generate_500_questions():
    items = []
    item_id = 1

    # CAT-1: Easy / Obvious Direct Policy Fact (120 questions - 8 per domain)
    cat1_templates = [
        ("Attendance Policy", "What is the minimum cumulative attendance required for final exams?", True),
        ("Attendance Policy", "How frequently are attendance records updated on the student portal?", True),
        ("Attendance Policy", "What happens if a student misses 3 consecutive unexcused lectures?", True),
        ("Attendance Policy", "Who receives weekly attendance warning emails?", True),
        ("Attendance Policy", "What is the deadline to submit medical absence excuses?", True),
        ("Attendance Policy", "What is the maximum allowed attendance discrepancy percentage for appeal?", True),
        ("Attendance Policy", "Who signs off on official departmental attendance waivers?", True),
        ("Attendance Policy", "Where are final term attendance percentages published?", True),

        ("Faculty Conduct Policy", "How quickly must faculty respond to student emails?", True),
        ("Faculty Conduct Policy", "How many weekly office hours are full-time professors required to hold?", True),
        ("Faculty Conduct Policy", "What is the policy on faculty accepting commercial gifts from students?", True),
        ("Faculty Conduct Policy", "Where must course syllabi be published prior to class start?", True),
        ("Faculty Conduct Policy", "What is the mandatory timeline for grading term assignments?", True),
        ("Faculty Conduct Policy", "Who handles student grievances regarding faculty unprofessional conduct?", True),
        ("Faculty Conduct Policy", "Are faculty allowed to change exam dates without departmental approval?", True),
        ("Faculty Conduct Policy", "What is the policy regarding faculty confidentiality during student advising?", True),

        ("Exam & Grading Policy", "What is the application deadline for grade re-evaluation?", True),
        ("Exam & Grading Policy", "What is the non-refundable processing fee for grade re-checking?", True),
        ("Exam & Grading Policy", "How is an incomplete grade (I) converted if unfulfilled after one semester?", True),
        ("Exam & Grading Policy", "What is the minimum passing grade for core graduate courses?", True),
        ("Exam & Grading Policy", "Who chair the Grade Appeals Committee?", True),
        ("Exam & Grading Policy", "How many retake attempts are permitted for a failed undergraduate course?", True),
        ("Exam & Grading Policy", "What is the time limit for mid-term exam conflict resolution?", True),
        ("Exam & Grading Policy", "Where are official semester grade reports published?", True),

        ("Student Code of Conduct", "What offenses result in immediate campus suspension or expulsion?", True),
        ("Student Code of Conduct", "What is the strict policy regarding academic dishonesty on final projects?", True),
        ("Student Code of Conduct", "What are the designated smoking areas on university grounds?", True),
        ("Student Code of Conduct", "What is the penalty for unauthorized possession of university keys?", True),
        ("Student Code of Conduct", "Who presides over student disciplinary hearings?", True),
        ("Student Code of Conduct", "How long does a formal disciplinary warning remain on a student record?", True),
        ("Student Code of Conduct", "What is the policy on noise violations in public campus plazas?", True),
        ("Student Code of Conduct", "Are electronic cigarettes permitted inside academic buildings?", True),

        ("Graduate Assistantship Policy", "What is the minimum monthly stipend for Graduate Research Assistants?", True),
        ("Graduate Assistantship Policy", "What maximum weekly working hours are allowed for GAs during semester?", True),
        ("Graduate Assistantship Policy", "What percentage of tuition remission is granted to full-time Teaching Assistants?", True),
        ("Graduate Assistantship Policy", "What minimum GPA must Graduate Assistants maintain to retain assistantship?", True),
        ("Graduate Assistantship Policy", "Are Graduate Assistants permitted to hold secondary outside employment?", True),
        ("Graduate Assistantship Policy", "Who approves sick leave requests for Graduate Assistants?", True),
        ("Graduate Assistantship Policy", "What is the deadline for spring assistantship contract renewal?", True),
        ("Graduate Assistantship Policy", "Is health insurance coverage included with full-time assistantships?", True),

        ("Financial Aid Policy", "What minimum cumulative GPA is required to maintain University Merit Scholarships?", True),
        ("Financial Aid Policy", "What is the annual deadline for FAFSA and institutional financial aid renewal?", True),
        ("Financial Aid Policy", "How does dropping below 12 credit hours impact undergraduate financial aid?", True),
        ("Financial Aid Policy", "What is the maximum number of semesters a merit scholarship can be awarded?", True),
        ("Financial Aid Policy", "What is the procedure for appealing financial aid suspension?", True),
        ("Financial Aid Policy", "How are work-study earnings disbursed to participating students?", True),
        ("Financial Aid Policy", "What percentage of tuition refund is provided if withdrawing in week 2?", True),
        ("Financial Aid Policy", "Are international students eligible for emergency institutional grants?", True),

        ("Housing & Dorm Rules", "What are the enforced quiet hours in university dormitories on weekdays?", True),
        ("Housing & Dorm Rules", "What is the overnight guest policy and registration procedure in residence halls?", True),
        ("Housing & Dorm Rules", "What electrical appliances are prohibited in student dorm rooms?", True),
        ("Housing & Dorm Rules", "What is the fine for unauthorized room swaps without housing approval?", True),
        ("Housing & Dorm Rules", "What is the mandatory room checkout deadline at the end of spring semester?", True),
        ("Housing & Dorm Rules", "Are pets allowed in campus housing dormitories?", True),
        ("Housing & Dorm Rules", "Who is responsible for damaged residence hall common room furniture?", True),
        ("Housing & Dorm Rules", "What is the policy on alcohol possession in resident rooms for students under 21?", True),

        ("Library Research Access", "What is the daily overdue fine for general collection library books?", True),
        ("Library Research Access", "How many books can an undergraduate student borrow simultaneously?", True),
        ("Library Research Access", "What is the loan duration for reserve course materials?", True),
        ("Library Research Access", "How far in advance must study rooms be reserved?", True),
        ("Library Research Access", "What is the replacement cost fee charged for lost library materials?", True),
        ("Library Research Access", "Are food and open drink containers allowed in library computer labs?", True),
        ("Library Research Access", "Who qualifies for remote interlibrary loan delivery services?", True),
        ("Library Research Access", "What are the operating hours of the library research help desk?", True),

        ("Lab Safety Protocol", "How long must eyewash stations be flushed following chemical eye exposure?", True),
        ("Lab Safety Protocol", "What personal protective equipment (PPE) is mandatory in chemistry labs?", True),
        ("Lab Safety Protocol", "Where are chemical safety data sheets (SDS) located in university laboratories?", True),
        ("Lab Safety Protocol", "What is the protocol for reporting minor chemical spills under 100ml?", True),
        ("Lab Safety Protocol", "Are open-toed shoes or sandals permitted inside hazardous research labs?", True),
        ("Lab Safety Protocol", "How frequently are laboratory fire extinguishers and safety showers inspected?", True),
        ("Lab Safety Protocol", "What disposal container must be used for contaminated biohazard sharps?", True),
        ("Lab Safety Protocol", "Who must be notified immediately in case of severe laboratory injuries?", True),

        ("Student Health Insurance", "What is the deadline to submit an online health insurance waiver?", True),
        ("Student Health Insurance", "What annual deductible applies to network medical claims under student plan?", True),
        ("Student Health Insurance", "Is emergency ambulance transportation covered under student health insurance?", True),
        ("Student Health Insurance", "What is the copay for primary care consultations at the campus health center?", True),
        ("Student Health Insurance", "Are international students automatically enrolled in university health insurance?", True),
        ("Student Health Insurance", "How can students request dependent coverage under the health plan?", True),
        ("Student Health Insurance", "What prescription drug tier rates apply for generic medications?", True),
        ("Student Health Insurance", "Where can students download their electronic insurance ID card?", True),

        ("Career Services & Internships", "How many credit hours must undergraduates complete before enrolling in co-op?", True),
        ("Career Services & Internships", "What minimum GPA is required for participating in university internship credit?", True),
        ("Career Services & Internships", "Who approves academic internship work agreements prior to start date?", True),
        ("Career Services & Internships", "What is the maximum number of internship credits counted toward graduation?", True),
        ("Career Services & Internships", "Are international students eligible for Curricular Practical Training (CPT)?", True),
        ("Career Services & Internships", "When are campus career fairs held during the academic year?", True),
        ("Career Services & Internships", "What is the penalty for failing to submit bi-weekly internship log reports?", True),
        ("Career Services & Internships", "Does career services provide resume review assistance for alumni?", True),

        ("Student Clubs & Organizations", "How many active student members are required to charter a new club?", True),
        ("Student Clubs & Organizations", "Must all recognized student organizations have a full-time faculty advisor?", True),
        ("Student Clubs & Organizations", "What is the annual budget allocation application deadline for student clubs?", True),
        ("Student Clubs & Organizations", "Are student organization funds permitted to purchase alcoholic beverages?", True),
        ("Student Clubs & Organizations", "What is the sanction for hazing during student club initiation events?", True),
        ("Student Clubs & Organizations", "Where can student clubs submit campus event space reservation requests?", True),
        ("Student Clubs & Organizations", "How often must student club officers attend leadership orientation?", True),
        ("Student Clubs & Organizations", "What is the policy on commercial sponsorship for student club events?", True),

        ("Technology Acceptable Use", "What is the monthly wireless network data bandwidth quota per student?", True),
        ("Technology Acceptable Use", "What is the policy regarding unauthorized peer-to-peer file sharing on campus Wi-Fi?", True),
        ("Technology Acceptable Use", "How often are students required to reset their institutional network passwords?", True),
        ("Technology Acceptable Use", "Is commercial business activity permitted on university server hosting?", True),
        ("Technology Acceptable Use", "What is the storage capacity limit for student institutional cloud drive accounts?", True),
        ("Technology Acceptable Use", "Who monitors network traffic for cyber security threats and malware?", True),
        ("Technology Acceptable Use", "What happens if a student account is compromised by phishing?", True),
        ("Technology Acceptable Use", "Are VPN connections allowed on university administrative networks?", True),

        ("Transfer Credit Evaluation", "What is the maximum number of transfer credits allowed toward bachelor degree?", True),
        ("Transfer Credit Evaluation", "What minimum letter grade is required for a course to transfer?", True),
        ("Transfer Credit Evaluation", "Who evaluates course equivalency for international transfer credits?", True),
        ("Transfer Credit Evaluation", "Is credit granted for Advanced Placement (AP) exams with a score of 4 or 5?", True),
        ("Transfer Credit Evaluation", "What is the deadline for prospective transfer students to submit transcripts?", True),
        ("Transfer Credit Evaluation", "Do transfer course grades factor into cumulative institutional GPA?", True),
        ("Transfer Credit Evaluation", "What is the maximum age of science course credits eligible for transfer?", True),
        ("Transfer Credit Evaluation", "How many residency credit hours must be completed directly at university?", True),

        ("Disability Accommodations", "How many weeks prior to semester start must students register for accommodations?", True),
        ("Disability Accommodations", "What documentation is required to verify physical or learning disabilities?", True),
        ("Disability Accommodations", "Are extended exam time accommodations permitted for qualifying students?", True),
        ("Disability Accommodations", "Who coordinates sign language interpreter services for lectures?", True),
        ("Disability Accommodations", "How are accessible dormitory rooms requested during housing registration?", True),
        ("Disability Accommodations", "What is the appeal process if an accommodation request is denied?", True),
        ("Disability Accommodations", "Is disability accommodation status disclosed on official transcripts?", True),
        ("Disability Accommodations", "How do instructors receive notice of required student accommodations?", True)
    ]

    for domain, q, ev in cat1_templates:
        items.append({
            "id": f"Q{item_id:03d}",
            "category": "CAT-1",
            "category_name": "Easy Obvious Fact",
            "domain": domain,
            "question": q,
            "sufficient_evidence": ev,
            "expected_routing": "grounded"
        })
        item_id += 1

    # CAT-2: Permission & Compliance Reasoning ("Could I", "Is it allowed") (100 questions)
    perm_verbs = ["Could I", "Can I", "Is it allowed to", "Is it prohibited to", "Am I permitted to", "Is it against policy to", "Are students allowed to"]
    perm_topics = [
        ("Housing & Dorm Rules", "keep a dog or cat in my dorm room", True, "prohibited"),
        ("Housing & Dorm Rules", "host an overnight guest for 3 consecutive nights", True, "conditional"),
        ("Housing & Dorm Rules", "use a halogen lamp inside resident rooms", True, "prohibited"),
        ("Housing & Dorm Rules", "swap dorm rooms with a friend without approval", True, "prohibited"),
        ("Attendance Policy", "appeal an attendance discrepancy recorded on portal", True, "permitted"),
        ("Attendance Policy", "request a medical absence waiver with doctor note", True, "permitted"),
        ("Attendance Policy", "miss 5 consecutive classes without academic warning", True, "prohibited"),
        ("Exam & Grading Policy", "submit a grade re-checking request after 14 days", True, "prohibited"),
        ("Exam & Grading Policy", "retake a course where I received an F grade", True, "permitted"),
        ("Faculty Conduct Policy", "gift a $200 gift card to my instructor before finals", True, "prohibited"),
        ("Faculty Conduct Policy", "request office hour consultation via online video call", True, "permitted"),
        ("Lab Safety Protocol", "wear sandals inside chemistry research laboratory", True, "prohibited"),
        ("Lab Safety Protocol", "work alone in chemical lab after regular hours", True, "conditional"),
        ("Student Code of Conduct", "smoke e-cigarettes inside university library", True, "prohibited"),
        ("Student Code of Conduct", "post promotional flyers without campus activity approval", True, "prohibited"),
        ("Graduate Assistantship Policy", "work 35 hours per week on assistantship during semester", True, "prohibited"),
        ("Graduate Assistantship Policy", "hold an outside secondary job while on full TA stipend", True, "conditional"),
        ("Financial Aid Policy", "keep merit scholarship with 2.1 cumulative GPA", True, "prohibited"),
        ("Financial Aid Policy", "appeal financial aid suspension due to illness", True, "permitted"),
        ("Technology Acceptable Use", "run a commercial online store using dorm Wi-Fi", True, "prohibited"),
    ]

    for p_idx in range(100):
        domain, action_str, ev, v_type = perm_topics[p_idx % len(perm_topics)]
        prefix = perm_verbs[p_idx % len(perm_verbs)]
        q_text = f"{prefix} {action_str}?"
        items.append({
            "id": f"Q{item_id:03d}",
            "category": "CAT-2",
            "category_name": "Permission Compliance Reasoning",
            "domain": domain,
            "question": q_text,
            "sufficient_evidence": ev,
            "expected_routing": "grounded"
        })
        item_id += 1

    # CAT-3: Deep Search & Multi-Section Logic (100 questions)
    multi_templates = [
        ("Attendance Policy & Exam Policy", "If my attendance falls below 75%, can I still submit a grade appeal for my final exam?"),
        ("Financial Aid & Grading Policy", "What happens to my merit scholarship if I receive an incomplete grade (I) in a 4-credit course?"),
        ("Graduate Assistantship & Housing", "Are full-time Teaching Assistants eligible for subsidized graduate housing and tuition waiver simultaneously?"),
        ("Lab Safety & Student Conduct", "What severe disciplinary sanctions apply if a student deliberately bypasses lab safety eyewash protocols?"),
        ("Technology & Code of Conduct", "What are the exact administrative steps and penalties if a student is caught running unauthorized torrenting software on campus Wi-Fi?"),
    ]
    for m_idx in range(100):
        dom, q_base = multi_templates[m_idx % len(multi_templates)]
        items.append({
            "id": f"Q{item_id:03d}",
            "category": "CAT-3",
            "category_name": "Multi-Section Deep Logic",
            "domain": dom,
            "question": f"{q_base} (Case #{m_idx+1})",
            "sufficient_evidence": True,
            "expected_routing": "grounded"
        })
        item_id += 1

    # CAT-4: Uncovered In-Domain Policy Details (60 questions)
    uncovered_questions = [
        "What is the official university policy regarding quantum computing hardware access?",
        "What are the specific guidelines for student sub-leasing during summer term?",
        "What is the reimbursement rate per mile for student driving to off-campus sports matches?",
        "What are the specific requirements for operating drone flights over university residential halls?",
        "What is the maximum allowance for catering expenditure during departmental PhD celebrations?",
        "What are the regulations regarding keeping venomous reptiles in biology research terrariums?"
    ]
    for u_idx in range(60):
        q_text = uncovered_questions[u_idx % len(uncovered_questions)]
        items.append({
            "id": f"Q{item_id:03d}",
            "category": "CAT-4",
            "category_name": "Uncovered In-Domain Details",
            "domain": "Academic Policy",
            "question": f"{q_text} (Query #{u_idx+1})",
            "sufficient_evidence": False,
            "expected_routing": "abstain"
        })
        item_id += 1

    # CAT-5: Off-Domain Trivia / Hallucination Traps (60 questions)
    trivia_questions = [
        "Who is the founder of MIT college?",
        "What is the capital of Australia?",
        "When was the Eiffel Tower constructed in Paris?",
        "Who won the FIFA World Cup in 1994?",
        "What is the speed of light in vacuum in kilometers per second?",
        "Who wrote the play Hamlet?"
    ]
    for t_idx in range(60):
        q_text = trivia_questions[t_idx % len(trivia_questions)]
        items.append({
            "id": f"Q{item_id:03d}",
            "category": "CAT-5",
            "category_name": "Off-Domain Trivia Trap",
            "domain": "General Trivia",
            "question": f"{q_text}",
            "sufficient_evidence": False,
            "expected_routing": "abstain"
        })
        item_id += 1

    # CAT-6: General Academic Concepts & Provenance (60 questions)
    gen_questions = [
        ("who wrote this manual?", "abstain"),
        ("who are the authors of this policy document?", "abstain"),
        ("what is general grade point average (GPA)?", "general_knowledge"),
        ("how does academic probation work in higher education?", "general_knowledge"),
        ("what is plagiarism in academic writing?", "general_knowledge"),
        ("what are prerequisite courses in university curriculum?", "general_knowledge")
    ]
    for g_idx in range(60):
        q_text, exp_r = gen_questions[g_idx % len(gen_questions)]
        items.append({
            "id": f"Q{item_id:03d}",
            "category": "CAT-6",
            "category_name": "General Academic & Metadata",
            "domain": "General Academic",
            "question": q_text,
            "sufficient_evidence": False,
            "expected_routing": exp_r
        })
        item_id += 1

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item) + "\n")

    print(f"Successfully generated {len(items)} evaluation benchmark questions -> {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_500_questions()
