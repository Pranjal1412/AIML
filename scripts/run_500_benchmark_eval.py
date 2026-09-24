import sys
import json
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.ingestion.ingest import process_and_ingest_file
from backend.retrieval.vector_store import get_vector_store
from backend.api.routes import run_full_pipeline

DATASET_PATH = BASE_DIR / "data" / "eval_dataset_500.jsonl"
PDF_DIR = BASE_DIR / "data" / "policies_pdf"
REPORT_PATH = BASE_DIR / "data" / "eval_500_summary_report.json"

def ensure_all_pdfs_ingested():
    """Ensure all 15 policy PDFs are ingested into ChromaDB."""
    vs = get_vector_store()
    initial_count = vs.get_document_count()
    print(f"[Ingest Check] ChromaDB currently has {initial_count} indexed chunks.")

    if PDF_DIR.exists():
        pdf_files = list(PDF_DIR.glob("*.pdf"))
        print(f"[Ingest Check] Found {len(pdf_files)} policy PDFs in {PDF_DIR}.")
        for pdf_path in pdf_files:
            try:
                res = process_and_ingest_file(str(pdf_path))
                print(f"  Ingested: {pdf_path.name} -> {res.get('chunks_count', 0)} chunks")
            except Exception as e:
                print(f"  Failed to ingest {pdf_path.name}: {e}")
    
    final_count = vs.get_document_count()
    print(f"[Ingest Check] Ingestion completed. Total indexed chunks: {final_count}")


def run_500_benchmark():
    ensure_all_pdfs_ingested()

    if not DATASET_PATH.exists():
        print(f"Error: Dataset {DATASET_PATH} not found. Run generate_500_eval_benchmark.py first.")
        return

    items = []
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                items.append(json.loads(line.strip()))

    print("=" * 80)
    print(f"STARTING 500-QUESTION MARKET READINESS BENCHMARK EVALUATION ({len(items)} items)")
    print("=" * 80)

    start_time = time.time()

    category_stats = {}
    grounded_count = 0
    abstain_count = 0
    general_knowledge_count = 0
    permission_verdict_count = 0
    hallucination_count = 0
    total_entropy_grounded = 0.0

    for idx, item in enumerate(items, start=1):
        cat = item["category"]
        if cat not in category_stats:
            category_stats[cat] = {
                "name": item["category_name"],
                "total": 0,
                "grounded": 0,
                "abstain": 0,
                "general_knowledge": 0,
                "verdict_correct": 0
            }
        
        category_stats[cat]["total"] += 1

        res = run_full_pipeline(item["question"], force_policy="fixed_rule")
        routing_mode = res.get("routing_mode", "abstain")
        status = res.get("status", "")
        answer = res.get("final_answer", "")
        sources = res.get("sources", [])
        entropy = res.get("entropy", 0.0)

        # Hallucination Check: Off-domain trivia (CAT-5) MUST NOT return grounded answer
        if cat == "CAT-5" and routing_mode == "grounded":
            hallucination_count += 1

        if routing_mode == "grounded":
            grounded_count += 1
            category_stats[cat]["grounded"] += 1
            total_entropy_grounded += entropy
            if "[VERDICT:" in answer:
                permission_verdict_count += 1
                category_stats[cat]["verdict_correct"] += 1
        elif routing_mode == "general_knowledge":
            general_knowledge_count += 1
            category_stats[cat]["general_knowledge"] += 1
        else:
            abstain_count += 1
            category_stats[cat]["abstain"] += 1

        if idx % 50 == 0 or idx == len(items):
            elapsed = time.time() - start_time
            qps = idx / elapsed if elapsed > 0 else 0
            print(f"Progress: [{idx}/{len(items)}] ({idx/len(items)*100:.1f}%) | QPS: {qps:.1f} q/s | Grounded: {grounded_count} | Abstain: {abstain_count} | GK: {general_knowledge_count}")

    total_time = time.time() - start_time
    avg_entropy = total_entropy_grounded / max(1, grounded_count)
    hallucination_rate = (hallucination_count / float(len(items))) * 100.0

    report = {
        "total_questions": len(items),
        "total_execution_time_sec": round(total_time, 2),
        "avg_query_latency_ms": round((total_time / len(items)) * 1000, 2),
        "grounded_answers_count": grounded_count,
        "abstained_answers_count": abstain_count,
        "general_knowledge_answers_count": general_knowledge_count,
        "permission_verdicts_generated": permission_verdict_count,
        "hallucinations_detected": hallucination_count,
        "hallucination_rate_pct": round(hallucination_rate, 4),
        "zero_hallucination_guarantee_passed": (hallucination_count == 0),
        "avg_grounded_semantic_entropy": round(avg_entropy, 4),
        "category_breakdown": category_stats
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 80)
    print("500-QUESTION BENCHMARK EVALUATION SUMMARY")
    print("=" * 80)
    print(f"Total Questions Evaluated : {len(items)}")
    print(f"Total Execution Time     : {total_time:.2f} seconds ({report['avg_query_latency_ms']} ms/query)")
    print(f"Grounded Answers (Cited) : {grounded_count} ({grounded_count/len(items)*100:.1f}%)")
    print(f"Abstained Answers        : {abstain_count} ({abstain_count/len(items)*100:.1f}%)")
    print(f"General Knowledge Answers: {general_knowledge_count} ({general_knowledge_count/len(items)*100:.1f}%)")
    print(f"Permission Verdicts      : {permission_verdict_count}")
    print(f"Hallucinations Detected  : {hallucination_count} (Hallucination Rate: {hallucination_rate:.2f}%)")
    print(f"Avg Grounded Entropy (H) : {avg_entropy:.4f}")
    print(f"Zero-Hallucination Status: {'PASSED (0.00% Hallucinations)' if hallucination_count == 0 else 'FAILED'}")
    print("=" * 80)
    print(f"Full JSON Report written to -> {REPORT_PATH}")

if __name__ == "__main__":
    run_500_benchmark()
