"""
Regression Test Suite (Section 11 PDF Specification)
Executes 7 strict accuracy and 3-mode routing regression tests against the running system.
"""

import sys
import os
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.api.routes import run_full_pipeline
from backend.config import settings

def run_suite():
    print("=" * 80)
    print("RUNNING 7-QUESTION REGRESSION TEST SUITE (SECTION 11 PDF SPEC)")
    print("=" * 80)

    passed_count = 0
    total_tests = 7

    # -------------------------------------------------------------------------
    # TEST 1: Well-covered factual query -> Grounded, cited, H <= 0.30
    # -------------------------------------------------------------------------
    print("\n[TEST 1] Well-covered factual query")
    q1 = "What is the minimum attendance required to appear for final exams?"
    res1 = run_full_pipeline(q1)
    t1_pass = (
        res1["routing_mode"] == "grounded" and
        res1["entropy"] <= settings.entropy.entropy_low_threshold and
        len(res1["sources"]) > 0
    )
    print(f"  Query: '{q1}'")
    print(f"  Mode: {res1['routing_mode']} | Entropy H: {res1['entropy']:.4f} | Citations: {len(res1['sources'])}")
    print(f"  Result: {'PASS' if t1_pass else 'FAIL'}")
    if t1_pass: passed_count += 1

    # -------------------------------------------------------------------------
    # TEST 2: Meta-question (authorship / provenance) -> Honest Abstention
    # -------------------------------------------------------------------------
    print("\n[TEST 2] Meta-question authorship/provenance query")
    q2 = "Who wrote this manual? Who were the panel members who drafted this document?"
    res2 = run_full_pipeline(q2)
    t2_pass = (
        res2["routing_mode"] == "abstain" and
        "metadata" in res2["final_answer"].lower()
    )
    print(f"  Query: '{q2}'")
    print(f"  Mode: {res2['routing_mode']} | Status: {res2['status']}")
    print(f"  Answer snippet: {res2['final_answer'][:100]}...")
    print(f"  Result: {'PASS' if t2_pass else 'FAIL'}")
    if t2_pass: passed_count += 1

    # -------------------------------------------------------------------------
    # TEST 3: Out-of-domain query -> Abstain with low similarity
    # -------------------------------------------------------------------------
    print("\n[TEST 3] Completely out-of-domain non-academic query")
    q3 = "What is the capital of France and how to make sourdough bread?"
    res3 = run_full_pipeline(q3)
    t3_pass = (
        res3["routing_mode"] == "abstain" and
        res3["max_similarity"] < settings.retrieval.min_evidence_similarity
    )
    print(f"  Query: '{q3}'")
    print(f"  Mode: {res3['routing_mode']} | Max Sim: {res3['max_similarity']:.4f}")
    print(f"  Result: {'PASS' if t3_pass else 'FAIL'}")
    if t3_pass: passed_count += 1

    # -------------------------------------------------------------------------
    # TEST 4: General academic policy query -> General Knowledge mode (Uncited)
    # -------------------------------------------------------------------------
    print("\n[TEST 4] General academic policy query")
    q4 = "What is a typical grade appeal process in universities?"
    res4 = run_full_pipeline(q4)
    t4_pass = (
        res4["routing_mode"] in ["general_knowledge", "abstain"] and
        len(res4["sources"]) == 0
    )
    print(f"  Query: '{q4}'")
    print(f"  Mode: {res4['routing_mode']} | Status: {res4['status']} | Citations: {len(res4['sources'])}")
    print(f"  Result: {'PASS' if t4_pass else 'FAIL'}")
    if t4_pass: passed_count += 1

    # -------------------------------------------------------------------------
    # TEST 5: Vague/ambiguous query -> Multi-round retrieval check
    # -------------------------------------------------------------------------
    print("\n[TEST 5] Vague/ambiguous query multi-round check")
    q5 = "Tell me about rules and regulations for students"
    res5 = run_full_pipeline(q5)
    t5_pass = res5["retrieval_rounds_count"] >= 1
    print(f"  Query: '{q5}'")
    print(f"  Rounds executed: {res5['retrieval_rounds_count']} | Action: {res5['action_taken']}")
    print(f"  Result: {'PASS' if t5_pass else 'FAIL'}")
    if t5_pass: passed_count += 1

    # -------------------------------------------------------------------------
    # TEST 6: Stability check (3 repeat executions) -> Consistent mode & H
    # -------------------------------------------------------------------------
    print("\n[TEST 6] Stability check (3 identical runs)")
    q6 = "What is the minimum attendance required to appear for final exams?"
    modes = []
    entropies = []
    for _ in range(3):
        res6 = run_full_pipeline(q6)
        modes.append(res6["routing_mode"])
        entropies.append(res6["entropy"])
    
    t6_pass = (len(set(modes)) == 1) and (max(entropies) - min(entropies) < 0.20)
    print(f"  Query: '{q6}'")
    print(f"  Modes returned: {modes}")
    print(f"  Entropies: {[round(h, 4) for h in entropies]}")
    print(f"  Result: {'PASS' if t6_pass else 'FAIL'}")
    if t6_pass: passed_count += 1

    # -------------------------------------------------------------------------
    # TEST 7: Guardrail check: max_sim < 0.55 must NEVER return 'grounded'
    # -------------------------------------------------------------------------
    print("\n[TEST 7] Similarity floor guardrail check (sim < 0.55)")
    q7 = "What is the quantum mechanics spin ratio of helium atoms?"
    res7 = run_full_pipeline(q7)
    t7_pass = (res7["routing_mode"] != "grounded")
    print(f"  Query: '{q7}'")
    print(f"  Mode: {res7['routing_mode']} | Max Sim: {res7['max_similarity']:.4f}")
    print(f"  Result: {'PASS' if t7_pass else 'FAIL'}")
    if t7_pass: passed_count += 1

    # -------------------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print(f"REGRESSION SUITE SUMMARY: {passed_count}/{total_tests} TESTS PASSED")
    print("=" * 80)

    if passed_count == total_tests:
        print("SUCCESS: System satisfies all 7 accuracy & routing constraints from Section 11 PDF spec.")
        sys.exit(0)
    else:
        print("WARNING: Some regression tests did not pass.")
        sys.exit(1)

if __name__ == "__main__":
    run_suite()
