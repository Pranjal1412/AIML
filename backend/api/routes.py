import uuid
import math
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

from backend.config import settings
from backend.ingestion.ingest import process_and_ingest_file
from backend.retrieval.vector_store import get_vector_store
from backend.context.engineer import build_context, rewrite_query_for_round
from backend.generation.candidate_generator import generate_candidates_for_context
from backend.nli.nli_service import get_nli_service
from backend.entropy.semantic_entropy import compute_semantic_entropy
from backend.policy.domain_check import (
    is_out_of_domain,
    is_meta_question,
    requires_institution_specific_fact,
    is_general_policy_topic
)
from backend.policy.state_builder import build_state_vector
from backend.policy.fixed_rule import select_action_fixed_rule
from backend.policy.ppo_policy import get_policy_network
from backend.storage.logger import log_query_session, get_session_by_id, get_all_sessions
from backend.evaluation.runner import run_benchmark_evaluation

router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    policy_mode: Optional[str] = None


class RetrieveRequest(BaseModel):
    query: str
    top_k: Optional[int] = 8


def compute_single_source_status(entropy: float, max_similarity: float, action_str: str, mode_str: str) -> str:
    """Single source of truth status computation per Section 7 PDF spec."""
    if action_str == "ABSTAIN" or mode_str == "abstain":
        return "ABSTAINED (Insufficient Evidence)"
    if action_str == "RETRIEVE_MORE":
        return "RETRIEVING MORE CONTEXT"
    if mode_str == "general_knowledge":
        return "GENERAL KNOWLEDGE (Uncited — Not from your documents)"
    if action_str == "ANSWER":
        if entropy <= settings.entropy.entropy_low_threshold and max_similarity >= settings.retrieval.min_evidence_similarity:
            return "ANSWERED (Grounded)"
        return "ANSWERED (Low Confidence — review router thresholds)"
    return "ABSTAINED (Insufficient Evidence)"


def run_full_pipeline(query_text: str, force_policy: Optional[str] = None) -> Dict[str, Any]:
    """
    Execute full end-to-end inference pipeline with 3-mode routing and exact single-source-of-truth status.
    """
    session_id = f"sess_{uuid.uuid4().hex[:12]}"
    vector_store = get_vector_store()
    
    # Guardrail 1: Check if any documents exist in knowledge base
    doc_count = vector_store.get_document_count()
    if doc_count == 0:
        return {
            "session_id": session_id,
            "query": query_text,
            "status": "ABSTAINED (Insufficient Evidence)",
            "action_taken": "ABSTAIN",
            "routing_mode": "abstain",
            "final_answer": "No institutional policy documents have been uploaded yet. Please submit or upload a policy PDF document first using the '+ Ingest Document' button before asking questions.",
            "sources": [],
            "entropy": 1.0,
            "num_clusters": 0,
            "top_cluster_mass": 0.0,
            "max_similarity": 0.0,
            "retrieval_rounds_count": 0,
            "retrieval_rounds": [],
            "decision_factors": [
                "Knowledge base is empty (0 indexed chunks)",
                "Document-First guardrail triggered: User must submit a policy PDF first before Q&A"
            ],
            "clusters": [],
            "math_calculations": {
                "formula_entropy": "H(X) = -sum(p_i * ln(p_i))",
                "normalized_entropy": 1.0,
                "n_candidates": 0,
                "nli_matrix": [],
                "state_vector": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                "action_probabilities": {"ANSWER": 0.0, "RETRIEVE_MORE": 0.0, "ABSTAIN": 1.0},
                "candidates": []
            }
        }

    # Guardrail 2: Section 8 Meta-Question Detection (authorship / provenance)
    if is_meta_question(query_text):
        retrieved = vector_store.query(query_text, top_k=5)
        _, top_sim = is_out_of_domain(retrieved)
        
        # Check if authorship metadata exists in retrieved chunks
        authors = [c.get("metadata", {}).get("doc_authors") for c in retrieved if c.get("metadata", {}).get("doc_authors")]
        committee = [c.get("metadata", {}).get("doc_committee") for c in retrieved if c.get("metadata", {}).get("doc_committee")]

        if not authors and not committee:
            # Section 8 PDF Spec honest abstention response for meta-questions
            return {
                "session_id": session_id,
                "query": query_text,
                "status": "ABSTAINED (Insufficient Evidence)",
                "action_taken": "ABSTAIN",
                "routing_mode": "abstain",
                "final_answer": "This information isn't available in the ingested documents' metadata. Try re-ingesting with the cover/approval page included, or ask a question about policy content instead.",
                "sources": [],
                "entropy": 1.0,
                "num_clusters": 0,
                "top_cluster_mass": 0.0,
                "max_similarity": round(top_sim, 4),
                "retrieval_rounds_count": 1,
                "retrieval_rounds": [],
                "decision_factors": [
                    f"Meta-question detected ('{query_text}')",
                    f"Retrieval similarity ({top_sim:.4f}) < MIN_EVIDENCE_SIMILARITY ({settings.retrieval.min_evidence_similarity})",
                    "Document authorship/committee cover metadata not found in ingested document — honest abstention triggered"
                ],
                "clusters": [],
                "math_calculations": {
                    "formula_entropy": "H(X) = -sum(p_i * ln(p_i))",
                    "normalized_entropy": 1.0,
                    "n_candidates": 0,
                    "nli_matrix": [],
                    "state_vector": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    "action_probabilities": {"ANSWER": 0.0, "RETRIEVE_MORE": 0.0, "ABSTAIN": 1.0},
                    "candidates": []
                }
            }

    nli_service = get_nli_service()
    policy_net = get_policy_network()

    policy_mode = force_policy or settings.policy.mode
    max_rounds = settings.entropy.max_retrieval_rounds

    retrieval_history = []
    current_round = 1
    current_k = settings.retrieval.top_k_round_1
    action_taken_str = "ANSWER"
    routing_mode = "grounded"
    final_answer = ""
    sources_metadata = []
    decision_factors = []

    last_context_pkg = None
    last_entropy_result = None
    last_state_vec = None
    last_nli_matrix = None
    last_candidates = []
    action_probs = [0.0, 0.0, 0.0]

    while current_round <= max_rounds:
        # Step 1: Vector + Hybrid Retrieval
        expanded_query = rewrite_query_for_round(query_text, round_no=current_round)
        retrieved_chunks = vector_store.query(expanded_query, top_k=current_k)

        # Step 2: Domain & Similarity Check
        is_ood, max_sim = is_out_of_domain(retrieved_chunks)

        # Section 9 PDF Spec & Section 5 Retrieval Regression Fix: 3-Mode Routing Evaluation
        if max_sim < settings.retrieval.min_evidence_similarity and current_round == 1:
            if not requires_institution_specific_fact(query_text) and not is_general_policy_topic(query_text):
                # Distinct out-of-scope message per Section 5 PDF spec
                routing_mode = "abstain"
                action_taken_str = "ABSTAIN"
                final_answer = "This assistant answers questions about academic policy and institutional regulations. That question is outside its scope."
                decision_factors = [
                    f"Out-of-scope question detected ('{query_text}')",
                    f"Retrieval similarity ({max_sim:.4f}) below MIN_EVIDENCE_SIMILARITY ({settings.retrieval.min_evidence_similarity})"
                ]
                last_entropy_result = compute_semantic_entropy([], [])
                last_nli_matrix = []
                last_state_vec = [0.0]*9
                break
            elif is_general_policy_topic(query_text) and not requires_institution_specific_fact(query_text):
                # Mode 2: General Knowledge Fallback
                routing_mode = "general_knowledge"
            else:
                # Mode 3: Honest Abstention for policy questions lacking specific institutional evidence
                routing_mode = "abstain"
                action_taken_str = "ABSTAIN"
                final_answer = "This information isn't available in the ingested documents. Try re-ingesting the relevant document, or rephrase the question."
                decision_factors = [
                    f"Retrieval similarity ({max_sim:.4f}) below MIN_EVIDENCE_SIMILARITY ({settings.retrieval.min_evidence_similarity})",
                    "Query requires specific institution facts not present in uploaded corpus — abstaining to prevent hallucination"
                ]
                last_entropy_result = compute_semantic_entropy([], [])
                last_nli_matrix = []
                last_state_vec = [0.0]*9
                break

        # Step 3: Context Engineering
        context_pkg = build_context(retrieved_chunks, query_text, round_no=current_round)
        last_context_pkg = context_pkg

        # Step 4: Candidate Generation (N=5 per Section 10 PDF spec)
        candidates = generate_candidates_for_context(context_pkg)
        last_candidates = candidates

        # Step 5: Pairwise NLI Scoring
        nli_matrix = nli_service.compute_pairwise_nli(candidates)
        last_nli_matrix = nli_matrix.tolist() if hasattr(nli_matrix, 'tolist') else nli_matrix

        # Step 6: Semantic Clustering & Continuous Entropy Calculation
        entropy_res = compute_semantic_entropy(candidates, nli_matrix)
        last_entropy_result = entropy_res

        # Step 7: Build 9-dim RL State Vector
        state_vec = build_state_vector(context_pkg, entropy_res, max_sim)
        last_state_vec = state_vec.tolist() if hasattr(state_vec, 'tolist') else state_vec

        # Step 8: Policy Decision (PPO or Fixed Rule)
        if policy_mode == "ppo":
            action, action_str, action_probs = policy_net.predict_action(state_vec)
            decision_factors = [
                f"PPO Router selected {action_str} (probs: {[round(p,4) for p in action_probs]})",
                f"Normalized entropy H = {entropy_res.normalized_entropy:.4f}",
                f"Max retrieval similarity = {max_sim:.4f}"
            ]
        else:
            action, action_str, decision_factors = select_action_fixed_rule(
                entropy=entropy_res.normalized_entropy,
                max_similarity=max_sim,
                retrieval_round=current_round,
                max_rounds=max_rounds
            )
            action_probs = [1.0, 0.0, 0.0] if action == 0 else ([0.0, 1.0, 0.0] if action == 1 else [0.0, 0.0, 1.0])

        retrieval_history.append({
            "round": current_round,
            "k": current_k,
            "entropy": entropy_res.normalized_entropy,
            "num_clusters": entropy_res.num_clusters,
            "chunks_kept": len(context_pkg.kept_chunks),
            "max_similarity": max_sim,
            "action_taken": action_str
        })

        # Section 9.3 Critical Rule: General Knowledge mode still evaluated via NLI/entropy
        if routing_mode == "general_knowledge":
            if entropy_res.normalized_entropy <= settings.entropy.general_knowledge_entropy_threshold:
                action_str = "ANSWER"
                top_cluster = entropy_res.clusters[0] if entropy_res.clusters else None
                final_answer = top_cluster.representative_text if top_cluster else candidates[0]["text"]
                sources_metadata = [] # Suppress citations for general knowledge
                decision_factors.append("General Knowledge mode active (labeled uncited answer)")
                break
            else:
                action_str = "ABSTAIN"
                routing_mode = "abstain"
                final_answer = "Based on the institutional policy documents available, there is insufficient evidence to provide a grounded answer."
                decision_factors.append(f"General Knowledge entropy H ({entropy_res.normalized_entropy:.4f}) > threshold ({settings.entropy.general_knowledge_entropy_threshold}) — downgraded to ABSTAIN")
                break

        if action_str == "ANSWER":
            top_cluster = entropy_res.clusters[0] if (entropy_res and entropy_res.clusters) else None
            candidate_text = top_cluster.representative_text if top_cluster else (candidates[0]["text"] if candidates else "")
            unevidenced_phrases = ["there is no information regarding", "repository does not contain details", "no policy regulations or details", "unable to answer as the policy corpus does not mention", "provides no evidence regarding", "insufficient evidence"]
            if any(p in candidate_text.lower() for p in unevidenced_phrases):
                action_str = "ABSTAIN"
                routing_mode = "abstain"
                final_answer = "This information isn't available in the ingested documents. Try re-ingesting the relevant document, or rephrase the question."
                sources_metadata = []
                decision_factors.append("Unevidenced candidate completion detected — converted to ABSTAIN")
            elif entropy_res.normalized_entropy <= settings.entropy.entropy_high_threshold and max_sim >= settings.retrieval.min_evidence_similarity:
                routing_mode = "grounded"
                final_answer = candidate_text
                sources_metadata = context_pkg.sources_metadata
            else:
                action_str = "ABSTAIN"
                routing_mode = "abstain"
                final_answer = "Based on the institutional policy documents available, there is insufficient evidence to provide a grounded answer."
                sources_metadata = []
                decision_factors.append("High entropy or low evidence similarity forced override to ABSTAIN (hallucination prevention)")
            break

        elif action_str == "RETRIEVE_MORE" and current_round < max_rounds:
            current_round += 1
            current_k += settings.retrieval.top_k_increment
            continue

        else: # ABSTAIN
            routing_mode = "abstain"
            action_taken_str = "ABSTAIN"
            final_answer = "Based on the institutional policy documents available, there is insufficient evidence to provide a grounded answer."
            sources_metadata = []
            break

    # Single source of truth status computation
    status_str = compute_single_source_status(
        entropy=last_entropy_result.normalized_entropy if last_entropy_result else 1.0,
        max_similarity=max_sim if 'max_sim' in locals() else 0.0,
        action_str=action_taken_str,
        mode_str=routing_mode
    )

    # Build complete mathematical breakdown dictionary
    n_candidates = max(1, len(last_candidates))
    max_possible_h = math.log(n_candidates) if n_candidates > 1 else 1.0
    raw_h = (last_entropy_result.normalized_entropy * max_possible_h) if last_entropy_result else 0.0

    math_calculations = {
        "formula_entropy": "H(X) = -sum(p_i * ln(p_i))",
        "formula_normalized_entropy": "Normalized H = H(X) / ln(N)",
        "raw_entropy": round(raw_h, 4),
        "max_possible_entropy": round(max_possible_h, 4),
        "normalized_entropy": last_entropy_result.normalized_entropy if last_entropy_result else 0.0,
        "n_candidates": n_candidates,
        "nli_matrix": last_nli_matrix,
        "state_vector_names": [
            "s1: normalized_entropy",
            "s2: num_clusters_ratio",
            "s3: top_cluster_mass",
            "s4: max_retrieval_similarity",
            "s5: mean_retrieval_similarity",
            "s6: num_chunks_kept_ratio",
            "s7: retrieval_round_ratio",
            "s8: evidence_coverage",
            "s9: is_out_of_domain_borderline"
        ],
        "state_vector": [round(val, 4) for val in (last_state_vec or [])],
        "action_probabilities": {
            "ANSWER": round(action_probs[0], 4),
            "RETRIEVE_MORE": round(action_probs[1], 4),
            "ABSTAIN": round(action_probs[2], 4)
        },
        "candidates": [
            {"id": c["candidate_id"], "text": c["text"]} for c in last_candidates
        ]
    }

    trace_data = {
        "session_id": session_id,
        "query": query_text,
        "status": status_str,
        "action_taken": action_taken_str,
        "routing_mode": routing_mode,
        "final_answer": final_answer,
        "sources": sources_metadata,
        "entropy": last_entropy_result.normalized_entropy if last_entropy_result else 0.0,
        "num_clusters": last_entropy_result.num_clusters if last_entropy_result else 1,
        "top_cluster_mass": last_entropy_result.top_cluster_mass if last_entropy_result else 1.0,
        "max_similarity": max_sim if 'max_sim' in locals() else 0.0,
        "retrieval_rounds_count": len(retrieval_history),
        "retrieval_rounds": retrieval_history,
        "decision_factors": decision_factors,
        "clusters": [
            {
                "cluster_id": c.cluster_id,
                "candidate_ids": c.candidate_ids,
                "probability_mass": c.probability_mass,
                "representative_text": c.representative_text
            } for c in (last_entropy_result.clusters if last_entropy_result else [])
        ],
        "math_calculations": math_calculations
    }

    log_query_session(trace_data)
    return trace_data


@router.post("/api/query")
def api_query(req: QueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query text cannot be empty.")
    return run_full_pipeline(req.query, req.policy_mode)


@router.post("/api/ingest")
async def api_ingest(
    file: UploadFile = File(...),
    institution: Optional[str] = Form("Apex Academic University"),
    doc_type: Optional[str] = Form("general_handbook")
):
    temp_dir = Path("storage/temp_uploads")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / file.filename

    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)

    try:
        chunks, doc_meta = process_and_ingest_file(temp_path)
        if institution:
            doc_meta["institution"] = institution
        if doc_type and doc_type != "general_handbook":
            doc_meta["doc_type"] = doc_type

        # Sync custom metadata to all chunks
        for c in chunks:
            if "metadata" in c:
                c["metadata"]["institution"] = doc_meta["institution"]
                c["metadata"]["doc_type"] = doc_meta["doc_type"]

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No readable text extracted from document. Please ensure the uploaded file contains searchable text."
            )

        v_store = get_vector_store()
        v_store.upsert_chunks(chunks)

        return {
            "status": "success",
            "message": f"Successfully ingested {file.filename}",
            "doc_metadata": doc_meta,
            "chunks_count": len(chunks)
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ingestion process error: {str(e)}")


@router.post("/api/retrieve")
def api_retrieve(req: RetrieveRequest):
    v_store = get_vector_store()
    retrieved = v_store.query(req.query, top_k=req.top_k or 8)
    context_pkg = build_context(retrieved, req.query, round_no=1)

    return {
        "query": req.query,
        "retrieved_count": len(retrieved),
        "kept_count": len(context_pkg.kept_chunks),
        "retrieved_chunks": retrieved,
        "context_text": context_pkg.context_text,
        "sources": context_pkg.sources_metadata
    }


@router.post("/api/evaluate")
def api_evaluate(policy_mode: Optional[str] = "fixed_rule"):
    return run_benchmark_evaluation(policy_mode)


@router.get("/api/sessions/{session_id}")
def api_get_session(session_id: str):
    sess = get_session_by_id(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found.")
    return sess


@router.get("/api/sessions")
def api_list_sessions(limit: Optional[int] = 30):
    return get_all_sessions(limit)


@router.get("/api/documents/count")
def api_document_count():
    v_store = get_vector_store()
    return {"count": v_store.get_document_count()}

