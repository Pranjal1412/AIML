from typing import List, Dict, Any

def compute_evaluation_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute aggregate benchmark metrics over evaluation run results.
    """
    total = len(results)
    if total == 0:
        return {}

    correct_count = 0
    grounded_count = 0
    halluc_count = 0
    abstain_count = 0
    true_abstain_count = 0
    false_abstain_count = 0
    total_rounds = 0

    for r in results:
        status = r.get("status", "ANSWERED")
        is_correct = r.get("is_correct", False)
        is_grounded = r.get("is_grounded", False)
        sufficient_evidence = r.get("sufficient_evidence", True)
        is_ood = r.get("domain") == "out_of_domain"
        rounds = r.get("retrieval_rounds", 1)

        total_rounds += rounds

        if status == "ABSTAINED":
            abstain_count += 1
            if not sufficient_evidence or is_ood:
                true_abstain_count += 1
            else:
                false_abstain_count += 1
        else:
            if is_correct:
                correct_count += 1
            if is_grounded:
                grounded_count += 1
            if not is_correct or not is_grounded:
                halluc_count += 1

    ans_denom = max(1, total - abstain_count)

    return {
        "total_queries": total,
        "correctness_rate": round(correct_count / float(ans_denom), 4),
        "groundedness_rate": round(grounded_count / float(ans_denom), 4),
        "hallucination_rate": round(halluc_count / float(ans_denom), 4),
        "abstention_rate": round(abstain_count / float(total), 4),
        "true_abstention_accuracy": round(true_abstain_count / float(max(1, abstain_count)), 4),
        "avg_retrieval_rounds": round(total_rounds / float(total), 2)
    }
