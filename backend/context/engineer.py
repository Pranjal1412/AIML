import re
from typing import List, Dict, Any
from dataclasses import dataclass
from backend.config import settings

@dataclass
class ContextPackage:
    query: str
    original_query: str
    round_no: int
    kept_chunks: List[Dict[str, Any]]
    dropped_chunks_count: int
    context_text: str
    prompt_string: str
    token_count_estimate: int
    sources_metadata: List[Dict[str, Any]]


def rewrite_query_for_round(query: str, round_no: int) -> str:
    """Expand or modify query strategy for retrieval rounds."""
    expansions = []
    q_lower = query.lower()

    if any(p in q_lower for p in ["can i", "could i", "allowed", "permitted", "prohibited", "against policy", "may i", "violation", "illegal"]):
        expansions.append("prohibited allowed permitted policy restriction penalty rule requirement approval consent")

    if any(p in q_lower for p in ["who to talk to", "who to contact", "who do i talk to", "where to go", "contact for", "reach out", "talk to", "contact person", "whom to contact"]):
        expansions.append("contact department office mentor ssw student service wing account escalation matrix officer director student affairs")

    if "fee" in q_lower or "tuition" in q_lower or "installment" in q_lower or "payment" in q_lower:
        expansions.append("account department fees payment erp ssw student service wing financial installment refund extension")

    if any(p in q_lower for p in ["punishment", "penalty", "property", "damage", "violation", "sanction", "fine"]):
        expansions.append("property damage willful negligent damage university property penalty punishment code of conduct violation 15 days suspension expulsion deliberate actions")

    if "attendance" in q_lower:
        expansions.append("absence limits medical leave condonation mandatory percentage")
    if "exam" in q_lower or "grade" in q_lower:
        expansions.append("grading scale cgpa probation retake fail pass requirement")
    if "conduct" in q_lower or "plagiarism" in q_lower:
        expansions.append("academic integrity plagiarism disciplinary offense penalties")
    if "faculty" in q_lower or "teacher" in q_lower:
        expansions.append("office hours syllabus consultation responsibilities")

    expanded_query = query + " " + " ".join(expansions)
    return expanded_query.strip()


def deduplicate_chunks(chunks: List[Dict[str, Any]], similarity_threshold: float = 0.90) -> List[Dict[str, Any]]:
    """Remove near-duplicate chunks based on text similarity."""
    unique_chunks = []
    seen_texts = []

    for chunk in chunks:
        text = chunk["text"].strip().lower()
        is_dup = False
        for s_text in seen_texts:
            # Quick Jaccard word set similarity for dedup
            w1 = set(text.split())
            w2 = set(s_text.split())
            if not w1 or not w2:
                continue
            jaccard = len(w1 & w2) / float(len(w1 | w2))
            if jaccard >= similarity_threshold:
                is_dup = True
                break

        if not is_dup:
            unique_chunks.append(chunk)
            seen_texts.append(text)

    return unique_chunks


def build_context(
    retrieved_chunks: List[Dict[str, Any]],
    query: str,
    round_no: int = 1
) -> ContextPackage:
    """
    Context Engineering pipeline:
    Filters, deduplicates, orders, wraps with source boundary tags, and enforces token budget.
    """
    original_query = query
    effective_query = rewrite_query_for_round(query, round_no)

    # Step 1: Relevance filtering (floor cut)
    sim_floor = settings.retrieval.similarity_threshold
    relevant_chunks = [c for c in retrieved_chunks if c.get("similarity", 0.0) >= sim_floor]

    # Step 2: Deduplication
    deduped_chunks = deduplicate_chunks(relevant_chunks, settings.context_engineering.dedup_similarity_threshold)

    # Step 3: Ordering (sort by similarity descending)
    sorted_chunks = sorted(deduped_chunks, key=lambda c: c.get("similarity", 0.0), reverse=True)

    # Step 4: Token budget enforcement and source boundary wrapping
    max_tokens = settings.context_engineering.max_evidence_tokens
    token_accum = 0
    kept_chunks = []
    wrapped_evidence_blocks = []
    sources_meta = []

    for idx, chunk in enumerate(sorted_chunks, start=1):
        meta = chunk.get("metadata", {})
        doc_title = meta.get("doc_title", meta.get("source_file", "Policy Document"))
        section = meta.get("section") or "General"
        page = meta.get("page", 1)

        source_tag = f"[S{idx}]"
        source_header = f"{source_tag} ({doc_title}, Section: {section}, p.{page})"
        chunk_text = chunk["text"].strip()
        wrapped_block = f"{source_header}\n{chunk_text}"

        est_tokens = int(len(wrapped_block.split()) * 1.3)
        if token_accum + est_tokens <= max_tokens or not kept_chunks:
            kept_chunks.append(chunk)
            wrapped_evidence_blocks.append(wrapped_block)
            token_accum += est_tokens
            sources_meta.append({
                "tag": source_tag,
                "chunk_id": chunk.get("chunk_id"),
                "doc_title": doc_title,
                "doc_type": meta.get("doc_type", "general_handbook"),
                "section": section,
                "page": page,
                "similarity": chunk.get("similarity", 0.0)
            })

    context_text = "\n\n".join(wrapped_evidence_blocks) if wrapped_evidence_blocks else "NO RELEVANT EVIDENCE FOUND."
    dropped_count = len(retrieved_chunks) - len(kept_chunks)

    prompt_string = (
        f"SYSTEM:\n"
        f"You are an academic-policy assistant. Answer ONLY using the EVIDENCE below. If the evidence does not contain the answer, say so plainly — "
        f"do not guess and do not repeat evidence verbatim as if it were an answer. Write one direct, well-formed answer in your own words, "
        f"then cite the evidence you used with [S1], [S2] style tags.\n\n"
        f"EVIDENCE:\n"
        f"{context_text}\n\n"
        f"QUESTION:\n"
        f"{query}\n\n"
        f"If none of the evidence above answers the question, respond exactly:\n"
        f"\"I don't have enough information in the ingested documents to answer this.\"\n\n"
        f"ANSWER:"
    )

    return ContextPackage(
        query=effective_query,
        original_query=original_query,
        round_no=round_no,
        kept_chunks=kept_chunks,
        dropped_chunks_count=dropped_count,
        context_text=context_text,
        prompt_string=prompt_string,
        token_count_estimate=token_accum,
        sources_metadata=sources_meta
    )
