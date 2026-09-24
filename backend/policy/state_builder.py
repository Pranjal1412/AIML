import numpy as np
from typing import List, Dict, Any
from backend.context.engineer import ContextPackage
from backend.entropy.semantic_entropy import EntropyResult
from backend.config import settings


def compute_evidence_coverage(query: str, kept_chunks: List[Dict[str, Any]]) -> float:
    """Calculate heuristic fraction of query keywords found in kept evidence chunks."""
    query_words = set([w.lower() for w in query.split() if len(w) > 3])
    if not query_words:
        return 1.0

    combined_text = " ".join([c["text"].lower() for c in kept_chunks])
    matched = sum(1 for w in query_words if w in combined_text)
    return round(matched / float(len(query_words)), 4)


def build_state_vector(
    context_pkg: ContextPackage,
    entropy_result: EntropyResult,
    max_retrieval_sim: float
) -> np.ndarray:
    """
    Build 9-dimensional state vector:
    [
        semantic_entropy,           # 0: [0, 1]
        num_clusters,               # 1: normalized count (num_clusters / num_candidates)
        top_cluster_mass,          # 2: [0, 1]
        max_retrieval_similarity,   # 3: [0, 1]
        mean_retrieval_similarity,  # 4: [0, 1]
        num_chunks_kept,            # 5: normalized count (kept / max 10)
        retrieval_round,            # 6: normalized round (round / max 3)
        evidence_coverage,          # 7: [0, 1]
        is_out_of_domain_borderline # 8: binary 0/1
    ]
    """
    kept = context_pkg.kept_chunks
    mean_sim = float(np.mean([c.get("similarity", 0.0) for c in kept])) if kept else 0.0
    coverage = compute_evidence_coverage(context_pkg.original_query, kept)

    domain_thresh = settings.retrieval.domain_threshold
    is_borderline = 1.0 if abs(max_retrieval_sim - domain_thresh) < 0.08 else 0.0

    num_candidates = max(1, len(context_pkg.kept_chunks))
    num_clusters_norm = entropy_result.num_clusters / float(num_candidates)

    state = np.array([
        entropy_result.normalized_entropy,
        num_clusters_norm,
        entropy_result.top_cluster_mass,
        max_retrieval_sim,
        mean_sim,
        min(1.0, len(kept) / 10.0),
        min(1.0, context_pkg.round_no / 3.0),
        coverage,
        is_borderline
    ], dtype=np.float32)

    return state
