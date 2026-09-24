"""
Regression Test Set v2 (Section 7 PDF Specification)
Tests the 5 explicit acceptance criteria rows from the Retrieval Regression Fix procedure.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.api.routes import run_full_pipeline
from backend.config import settings

def run_regression_v2():
    print("=" * 80)
    print("RUNNING REGRESSION TEST SET V2 (SECTION 7 PDF SPECIFICATION)")
    print("=" * 80)

    results = []

    # -------------------------------------------------------------------------
    # ROW 1: "what is the attendance policy?"
    # Must NOT happen: Cited Evidence (0)
    # Must happen: >= 1 cited source, action = ANSWER or RETRIEVE_MORE, sim > 0
    # -------------------------------------------------------------------------
    print("\n[ROW 1] 'what is the attendance policy?' (Primary Acceptance Bar)")
    q1 = "what is the attendance policy?"
    res1 = run_full_pipeline(q1)
    sources1_count = len(res1["sources"])
    r1_pass = (
        sources1_count >= 1 and
        res1["action_taken"] in ["ANSWER", "RETRIEVE_MORE"] and
        res1["max_similarity"] >= settings.retrieval.min_evidence_similarity
    )
    results.append({
        "row": 1,
        "question": q1,
        "must_not": "Cited Evidence (0)",
        "must_happen": ">=1 cited source, action=ANSWER/RETRIEVE_MORE",
        "actual_mode": res1["routing_mode"],
        "actual_sources": sources1_count,
        "max_sim": res1["max_similarity"],
        "passed": r1_pass
    })
    print(f"  Mode: {res1['routing_mode']} | Sources: {sources1_count} | Max Sim: {res1['max_similarity']:.4f}")
    print(f"  Result: {'PASS' if r1_pass else 'FAIL'}")

    # -------------------------------------------------------------------------
    # ROW 2: "who wrote this manual?"
    # Must NOT happen: Fabricated stitched answer
    # Must happen: Abstain, metadata warning
    # -------------------------------------------------------------------------
    print("\n[ROW 2] 'who wrote this manual?' (Meta-Question Provenance)")
    q2 = "who wrote this manual?"
    res2 = run_full_pipeline(q2)
    r2_pass = (
        res2["routing_mode"] == "abstain" and
        "metadata" in res2["final_answer"].lower()
    )
    results.append({
        "row": 2,
        "question": q2,
        "must_not": "Fabricated stitched answer",
        "must_happen": "Abstain with metadata warning",
        "actual_mode": res2["routing_mode"],
        "actual_sources": len(res2["sources"]),
        "max_sim": res2["max_similarity"],
        "passed": r2_pass
    })
    print(f"  Mode: {res2['routing_mode']} | Status: {res2['status']}")
    print(f"  Answer: {res2['final_answer']}")
    print(f"  Result: {'PASS' if r2_pass else 'FAIL'}")

    # -------------------------------------------------------------------------
    # ROW 3: "who is founder of mit college?"
    # Must NOT happen: Generic 'insufficient evidence' phrasing
    # Must happen: Abstain, distinct out_of_scope message per Section 5
    # -------------------------------------------------------------------------
    print("\n[ROW 3] 'who is founder of mit college?' (Out-of-Scope Trivia)")
    q3 = "who is founder of mit college?"
    res3 = run_full_pipeline(q3)
    r3_pass = (
        res3["routing_mode"] == "abstain" and
        "outside its scope" in res3["final_answer"].lower()
    )
    results.append({
        "row": 3,
        "question": q3,
        "must_not": "Generic 'insufficient evidence' phrasing",
        "must_happen": "Abstain, distinct out_of_scope message",
        "actual_mode": res3["routing_mode"],
        "actual_sources": len(res3["sources"]),
        "max_sim": res3["max_similarity"],
        "passed": r3_pass
    })
    print(f"  Mode: {res3['routing_mode']} | Status: {res3['status']}")
    print(f"  Answer: {res3['final_answer']}")
    print(f"  Result: {'PASS' if r3_pass else 'FAIL'}")

    # -------------------------------------------------------------------------
    # ROW 4: Covered question (e.g. attendance requirement)
    # Must NOT happen: Cited Evidence (0)
    # Must happen: >= 1 cited source with real section name
    # -------------------------------------------------------------------------
    print("\n[ROW 4] Covered policy question")
    q4 = "What is the minimum attendance required to appear for final exams?"
    res4 = run_full_pipeline(q4)
    sources4_count = len(res4["sources"])
    r4_pass = (
        sources4_count >= 1 and
        res4["routing_mode"] == "grounded" and
        any("section" in s or "doc_title" in s for s in res4["sources"])
    )
    results.append({
        "row": 4,
        "question": q4,
        "must_not": "Cited Evidence (0)",
        "must_happen": ">=1 cited source with real section name",
        "actual_mode": res4["routing_mode"],
        "actual_sources": sources4_count,
        "max_sim": res4["max_similarity"],
        "passed": r4_pass
    })
    print(f"  Mode: {res4['routing_mode']} | Sources: {sources4_count} | Section: {res4['sources'][0]['section'] if res4['sources'] else 'N/A'}")
    print(f"  Result: {'PASS' if r4_pass else 'FAIL'}")

    # -------------------------------------------------------------------------
    # ROW 5: Genuinely uncovered in-domain policy question
    # Must NOT happen: Fabricated answer
    # Must happen: Abstain or general-knowledge mode
    # -------------------------------------------------------------------------
    print("\n[ROW 5] Genuinely uncovered in-domain policy question")
    q5 = "What is the policy for quantum teleportation lab permits?"
    res5 = run_full_pipeline(q5)
    r5_pass = (
        res5["routing_mode"] in ["abstain", "general_knowledge"] and
        len(res5["sources"]) == 0
    )
    results.append({
        "row": 5,
        "question": q5,
        "must_not": "Fabricated answer",
        "must_happen": "Abstain or general-knowledge mode",
        "actual_mode": res5["routing_mode"],
        "actual_sources": len(res5["sources"]),
        "max_sim": res5["max_similarity"],
        "passed": r5_pass
    })
    print(f"  Mode: {res5['routing_mode']} | Status: {res5['status']}")
    print(f"  Result: {'PASS' if r5_pass else 'FAIL'}")

    # -------------------------------------------------------------------------
    # SUMMARY TABLE
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("REGRESSION TEST SET V2 SUMMARY TABLE")
    print("=" * 80)
    print(f"{'#':<3} | {'Question':<42} | {'Mode':<18} | {'Sources':<8} | {'Result':<6}")
    print("-" * 80)
    passed_all = True
    for r in results:
        status_str = "PASS" if r["passed"] else "FAIL"
        if not r["passed"]: passed_all = False
        print(f"{r['row']:<3} | {r['question'][:42]:<42} | {r['actual_mode']:<18} | {r['actual_sources']:<8} | {status_str:<6}")
    print("=" * 80)

    if passed_all:
        print("ALL 5/5 REGRESSION V2 TEST ROWS PASSED CLEANLY!")
        sys.exit(0)
    else:
        print("WARNING: Some Regression V2 tests failed.")
        sys.exit(1)

if __name__ == "__main__":
    run_regression_v2()
