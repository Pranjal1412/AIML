import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from backend.config import settings, BASE_DIR
from backend.embeddings.embedding_service import get_embedding_service

CHROMA_DIR = BASE_DIR / "storage" / "chromadb"
CHROMA_DIR.mkdir(parents=True, exist_ok=True)


class VectorStore:
    def __init__(self, collection_name: str = "institution_policies"):
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self.in_memory_db = [] # Fallback in-memory store if chromadb fails
        self._init_chroma()

    def _init_chroma(self):
        try:
            import chromadb
            from chromadb.config import Settings
            print(f"[VectorStore] Initializing ChromaDB at {CHROMA_DIR}...")
            self.client = chromadb.PersistentClient(
                path=str(CHROMA_DIR),
                settings=Settings(anonymized_telemetry=False)
            )
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"[VectorStore] ChromaDB collection '{self.collection_name}' ready.")
        except Exception as e:
            print(f"[VectorStore] ChromaDB initialization warning ({e}). Using in-memory vector store.")
            self.client = None
            self.collection = None

    def upsert_chunks(self, chunks: List[Dict[str, Any]]):
        if not chunks:
            return

        texts = [c["text"] for c in chunks]
        ids = [c["chunk_id"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        embedder = get_embedding_service()
        embeddings = embedder.encode(texts)

        if self.collection is not None:
            self.collection.upsert(
                ids=ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas
            )
            print(f"[VectorStore] Upserted {len(chunks)} chunks into ChromaDB.")
        else:
            # Fallback in-memory upsert
            for i, chunk in enumerate(chunks):
                self.in_memory_db.append({
                    "id": ids[i],
                    "text": texts[i],
                    "embedding": np.array(embeddings[i], dtype=np.float32),
                    "metadata": metadatas[i]
                })

    def _bm25_keyword_rank(self, query_text: str, all_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simple BM25 / keyword frequency scoring over retrieved chunks."""
        q_words = [w.lower() for w in query_text.split() if len(w) > 2]
        if not q_words:
            return all_chunks

        scored = []
        for c in all_chunks:
            text_lower = c["text"].lower()
            bm25_score = 0.0
            for qw in q_words:
                tf = text_lower.count(qw)
                if tf > 0:
                    bm25_score += (tf * (1.5 + 1.0)) / (tf + 1.5 * (0.25 + 0.75 * (len(text_lower.split()) / 200.0)))
            scored.append((bm25_score, c))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored]

    def query(
        self,
        query_text: str,
        top_k: int = 8,
        where_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Hybrid (Dense + BM25) Search with Reciprocal Rank Fusion (RRF) per Section 5 PDF spec.
        Combines vector similarity and keyword relevance to eliminate false 20-30% low matches on missing concepts.
        """
        embedder = get_embedding_service()
        q_vec = embedder.encode_single(query_text)

        dense_results = []

        if self.collection is not None:
            try:
                # Fetch candidate pool (top 20 for hybrid ranking)
                pool_k = max(20, top_k * 2)
                chroma_res = self.collection.query(
                    query_embeddings=[q_vec],
                    n_results=pool_k,
                    where=where_filter if where_filter else None
                )
                if chroma_res and chroma_res["documents"]:
                    docs = chroma_res["documents"][0]
                    ids = chroma_res["ids"][0]
                    metas = chroma_res["metadatas"][0]
                    dists = chroma_res["distances"][0] if "distances" in chroma_res else [0.0]*len(docs)

                    for i in range(len(docs)):
                        sim = max(0.0, min(1.0, 1.0 - dists[i])) if dists[i] <= 1.0 else max(0.0, 1.0 / (1.0 + dists[i]))
                        dense_results.append({
                            "chunk_id": ids[i],
                            "text": docs[i],
                            "metadata": metas[i],
                            "similarity": round(float(sim), 4)
                        })
            except Exception as e:
                print(f"[VectorStore] ChromaDB query error: {e}")

        if not dense_results and self.in_memory_db:
            q_arr = np.array(q_vec, dtype=np.float32)
            scored = []
            for item in self.in_memory_db:
                e_arr = item["embedding"]
                denom = (np.linalg.norm(q_arr) * np.linalg.norm(e_arr))
                sim = float(np.dot(q_arr, e_arr) / denom) if denom > 0 else 0.0
                scored.append((sim, item))

            scored.sort(key=lambda x: x[0], reverse=True)
            for sim, item in scored[:20]:
                dense_results.append({
                    "chunk_id": item["id"],
                    "text": item["text"],
                    "metadata": item["metadata"],
                    "similarity": round(sim, 4)
                })

        if not dense_results:
            return []

        # Step 2: BM25 / Keyword ranking
        bm25_results = self._bm25_keyword_rank(query_text, dense_results)

        # Step 3: Reciprocal Rank Fusion (RRF k=60)
        rrf_scores: Dict[str, float] = {}
        chunk_map: Dict[str, Dict[str, Any]] = {}

        for rank, c in enumerate(dense_results):
            cid = c["chunk_id"]
            chunk_map[cid] = c
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (60.0 + rank + 1))

        for rank, c in enumerate(bm25_results):
            cid = c["chunk_id"]
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (60.0 + rank + 1))

        # Sort chunks by RRF score descending
        fused_cids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)
        final_results = [chunk_map[cid] for cid in fused_cids[:top_k]]

        return final_results

    def get_document_count(self) -> int:
        if self.collection is not None:
            try:
                return self.collection.count()
            except Exception:
                return 0
        return len(self.in_memory_db)


_vector_store = None

def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore(settings.retrieval.collection_name)
    return _vector_store
