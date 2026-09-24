import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.api.routes import run_full_pipeline

TEST_QUESTIONS = [
    ("Attendance Policy", "What is the minimum cumulative attendance required to appear for final exams?"),
    ("Faculty Conduct Policy", "How quickly must faculty members respond to student emails and academic inquiries?"),
    ("Exam & Grading Policy", "What is the deadline and processing fee for grade re-checking or re-evaluation applications?"),
    ("Student Code of Conduct", "What situations result in immediate disciplinary suspension or expulsion on campus?"),
    ("Graduate Assistantship Policy", "What is the minimum monthly stipend and tuition remission provided to Graduate Assistants?"),
    ("Financial Aid Policy", "What cumulative GPA is required to maintain University Merit Scholarships?"),
    ("Housing & Dorm Rules", "What are the enforced quiet hours in university residence halls on weekdays?"),
    ("Library Research Access", "What is the overdue fine per day for general collection library books?"),
    ("Lab Safety Protocol", "How long must affected areas be flushed at emergency eyewash stations in case of chemical contact?"),
    ("Student Health Insurance", "What is the deadline to submit an online Health Insurance Waiver for the Fall semester?"),
    ("Career Services & Internships", "How many earned credit hours are required before an undergraduate can enroll in academic co-op credit?"),
    ("Student Clubs & Organizations", "How many active student members are required to charter a new student organization?"),
    ("Technology Acceptable Use", "What is the monthly wireless network data quota per student account?"),
    ("Transfer Credit Evaluation", "What is the maximum number of transfer semester credit hours allowed for undergraduate students?"),
    ("Disability Accommodations", "How many weeks prior to the start of the semester must students register for disability accommodations?")
]

def test_all_15_policies():
    print("=" * 80)
    print("TESTING UNIQUE QUESTIONS ACROSS ALL 15 INSTITUTIONAL POLICY DOMAINS")
    print("=" * 80)

    success_count = 0
    for idx, (domain, q) in enumerate(TEST_QUESTIONS, start=1):
        print(f"\n[{idx}/15] DOMAIN: {domain}")
        print(f"QUERY: \"{q}\"")

        res = run_full_pipeline(q)
        status = res.get("status")
        answer = res.get("final_answer")
        sources = res.get("sources", [])

        print(f"  -> STATUS: {status}")
        print(f"  -> ANSWER: {answer[:140]}...")
        if sources:
            print(f"  -> CITED SOURCE: [{sources[0].get('doc_title')}] {sources[0].get('section')}")
            success_count += 1
        else:
            print("  -> CITED SOURCE: None")

    print("\n" + "=" * 80)
    print(f"SUMMARY: {success_count}/{len(TEST_QUESTIONS)} Questions Successfully Answered with Cited Policy Sources!")
    print("=" * 80)

if __name__ == "__main__":
    test_all_15_policies()
