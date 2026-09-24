import json
from pathlib import Path
from typing import List, Dict, Any
from backend.config import settings, BASE_DIR
from backend.evaluation.metrics import compute_evaluation_metrics

EVAL_DATASET_PATH = BASE_DIR / settings.storage.eval_dataset_path


def load_eval_dataset() -> List[Dict[str, Any]]:
    """Load evaluation items from jsonl file."""
    items = []
    if EVAL_DATASET_PATH.exists():
        with open(EVAL_DATASET_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    items.append(json.loads(line.strip()))
    return items


def run_benchmark_evaluation(policy_mode: str = "fixed_rule") -> Dict[str, Any]:
    """
    Run the evaluation benchmark dataset across chosen policy baseline.
    Returns metric comparison dictionary.
    """
    items = load_eval_dataset()
    if not items:
        return {"error": "Evaluation dataset not found."}

    from backend.api.routes import run_full_pipeline

    results = []
    for item in items:
        query = item["question"]
        trace = run_full_pipeline(query, force_policy=policy_mode)

        status = trace.get("status", "ANSWERED")
        final_answer = trace.get("final_answer", "").lower()
        exp_answer = item.get("expected_answer", "").lower()

        # Simple semantic overlap correctness check
        exp_words = set(exp_answer.split())
        ans_words = set(final_answer.split())
        overlap = len(exp_words & ans_words) / float(max(1, len(exp_words)))

        is_correct = overlap >= 0.35 if status == "ANSWERED" else False
        is_grounded = len(trace.get("sources", [])) > 0 if status == "ANSWERED" else False

        results.append({
            "question": query,
            "status": status,
            "domain": item.get("domain", "in_domain"),
            "sufficient_evidence": item.get("sufficient_evidence", True),
            "is_correct": is_correct,
            "is_grounded": is_grounded,
            "entropy": trace.get("entropy", 0.0),
            "retrieval_rounds": trace.get("retrieval_rounds_count", 1)
        })

    metrics = compute_evaluation_metrics(results)
    metrics["policy_mode"] = policy_mode
    return metrics
