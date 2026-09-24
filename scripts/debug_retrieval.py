"""
Diagnostic Retrieval Procedure (Section 3 PDF Specification)
Runs raw step 1 to step 6 checks to isolate retrieval failure points.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.retrieval.vector_store import get_vector_store
from backend.embeddings.embedding_service import get_embedding_service
from backend.config import settings

def debug_retrieve(question: str = "what is the attendance policy?", institution_id: str = None):
    v = get_vector_store()
    print("=" * 80)
    print(f"DIAGNOSTIC RETRIEVAL PIPELINE CHECK FOR: '{question}'")
    print("=" * 80)

    # STEP 1 - raw vector search, no filters, no threshold
    print("[STEP 1] raw vector search, no filters, no threshold")
    embedder = get_embedding_service()
    q_vec = embedder.encode_single(question)
    raw_res = v.collection.query(
        query_embeddings=[q_vec],
        n_results=10
    )
    docs = raw_res["documents"][0] if raw_res and raw_res["documents"] else []
    ids = raw_res["ids"][0] if raw_res and raw_res["ids"] else []
    metas = raw_res["metadatas"][0] if raw_res and raw_res["metadatas"] else []
    dists = raw_res["distances"][0] if raw_res and "distances" in raw_res else []

    raw_vector_hits = []
    for i in range(len(docs)):
        sim = max(0.0, min(1.0, 1.0 - dists[i])) if dists[i] <= 1.0 else max(0.0, 1.0 / (1.0 + dists[i]))
        raw_vector_hits.append({
            "id": ids[i],
            "text": docs[i],
            "metadata": metas[i],
            "score": round(sim, 4)
        })

    print(f" -> {len(raw_vector_hits)} hits, top score: {raw_vector_hits[0]['score'] if raw_vector_hits else 'N/A'}")
    for h in raw_vector_hits[:5]:
        print(f"  id={h['id']} inst={h['metadata'].get('institution_id', 'N/A')} score={h['score']:.3f} text={h['text'][:60]!r}")

    # STEP 2 - same search, filtered by institution_id
    print(f"\n[STEP 2] same search, filtered by institution_id = {institution_id}")
    if institution_id:
        try:
            filtered_res = v.collection.query(
                query_embeddings=[q_vec],
                n_results=10,
                where={"institution_id": institution_id}
            )
            filtered_docs = filtered_res["documents"][0] if filtered_res and filtered_res["documents"] else []
            print(f" -> {len(filtered_docs)} hits after institution_id filter")
        except Exception as e:
            print(f" -> Error filtering by institution_id: {e}")
    else:
        print(" -> (No institution_id filter applied, skipped)")

    # STEP 3 - BM25 search
    print("\n[STEP 3] BM25 keyword search")
    bm25_hits = v._bm25_keyword_rank(question, raw_vector_hits)
    print(f" -> {len(bm25_hits)} hits after BM25 ranking")

    # STEP 4 - fusion output
    print("\n[STEP 4] fusion output (Reciprocal Rank Fusion RRF)")
    fused = v.query(question, top_k=8)
    print(f" -> {len(fused)} hits after fusion")

    # STEP 5 - after rerank
    print("\n[STEP 5] after rerank")
    print(f" -> {len(fused)} hits after rerank (similarity range: {min([c['similarity'] for c in fused]) if fused else 0:.4f} to {max([c['similarity'] for c in fused]) if fused else 0:.4f})")

    # STEP 6 - after MIN_EVIDENCE_SIMILARITY filter
    print(f"\n[STEP 6] after MIN_EVIDENCE_SIMILARITY filter (threshold={settings.retrieval.min_evidence_similarity})")
    final = [c for c in fused if c["similarity"] >= settings.retrieval.min_evidence_similarity]
    print(f" -> {len(final)} hits survive threshold (threshold={settings.retrieval.min_evidence_similarity})")

    print("=" * 80)
    return len(final)

if __name__ == "__main__":
    debug_retrieve()
