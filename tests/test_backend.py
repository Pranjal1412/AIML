import pytest
import numpy as np
from pathlib import Path

from backend.ingestion.ingest import process_and_ingest_file
from backend.retrieval.vector_store import get_vector_store
from backend.context.engineer import build_context
from backend.generation.candidate_generator import generate_candidates_for_context
from backend.nli.nli_service import get_nli_service
from backend.entropy.semantic_entropy import compute_semantic_entropy
from backend.policy.state_builder import build_state_vector
from backend.policy.fixed_rule import select_action_fixed_rule
from backend.policy.domain_check import is_out_of_domain
from backend.api.routes import run_full_pipeline


def test_ingestion_and_chunking():
    sample_path = Path("data/sample_policies/attendance_policy.txt")
    chunks, meta = process_and_ingest_file(sample_path)

    assert len(chunks) > 0
    assert meta["doc_type"] == "attendance_policy"
    assert "doc_title" in meta
    assert "chunk_id" in chunks[0]


def test_vector_store():
    v_store = get_vector_store()
    sample_path = Path("data/sample_policies/attendance_policy.txt")
    chunks, _ = process_and_ingest_file(sample_path)
    v_store.upsert_chunks(chunks)

    results = v_store.query("attendance requirement percentage", top_k=5)
    assert len(results) > 0
    assert "similarity" in results[0]


def test_context_engineering():
    v_store = get_vector_store()
    results = v_store.query("attendance requirement percentage", top_k=5)
    ctx_pkg = build_context(results, "What is the minimum attendance required?", round_no=1)

    assert len(ctx_pkg.kept_chunks) > 0
    assert "[S1]" in ctx_pkg.context_text


def test_entropy_and_clustering():
    candidates = [
        {"candidate_id": 0, "text": "Minimum attendance required is 75%."},
        {"candidate_id": 1, "text": "Students must maintain at least 75% attendance."},
        {"candidate_id": 2, "text": "A 75% attendance is strictly mandatory."},
        {"candidate_id": 3, "text": "Students need 75% attendance across all courses."}
    ]

    nli_service = get_nli_service()
    nli_matrix = nli_service.compute_pairwise_nli(candidates)
    entropy_res = compute_semantic_entropy(candidates, nli_matrix)

    assert 0.0 <= entropy_res.normalized_entropy <= 1.0
    assert entropy_res.num_clusters >= 1
    assert entropy_res.top_cluster_mass > 0.0


def test_policy_and_domain_check():
    # Out of domain query test
    results_ood = []
    is_ood, sim = is_out_of_domain(results_ood)
    assert is_ood is True

    # Fixed rule test
    action, action_str, factors = select_action_fixed_rule(entropy=0.10, max_similarity=0.85, retrieval_round=1)
    assert action == 0
    assert action_str == "ANSWER"


def test_end_to_end_pipeline():
    v_store = get_vector_store()
    sample_path = Path("data/sample_policies/attendance_policy.txt")
    chunks, _ = process_and_ingest_file(sample_path)
    v_store.upsert_chunks(chunks)

    # In-domain answerable query
    res = run_full_pipeline("What is the minimum attendance required?")
    assert res["status"].startswith("ANSWERED") or res["status"] == "RETRIEVED_MORE"
    assert "final_answer" in res
    assert "entropy" in res

    # Out-of-domain query
    res_ood = run_full_pipeline("What is the wingspan of a Boeing 747?")
    assert res_ood["status"].startswith("ABSTAINED")
