import re
from typing import List, Dict, Any, Tuple
from backend.config import settings

def is_out_of_domain(
    retrieved_chunks: List[Dict[str, Any]],
    domain_threshold: float = settings.retrieval.domain_threshold
) -> Tuple[bool, float]:
    """
    Check if query is outside the academic policy domain based on retrieval similarity.
    Returns (is_ood, max_similarity).
    """
    if not retrieved_chunks:
        return True, 0.0

    max_sim = max([c.get("similarity", 0.0) for c in retrieved_chunks])
    is_ood = max_sim < domain_threshold
    return is_ood, max_sim


def is_meta_question(query: str) -> bool:
    """Detect document provenance / authorship / committee metadata questions (Section 8 PDF spec)."""
    q_lower = query.lower()
    meta_patterns = [
        r'who\s+(wrote|authored|drafted|published|approved|signed|created|prepared)\b',
        r'who\s+are\s+the\s+(writers|authors|panel|committee|board|members)',
        r'who\s+were\s+the\s+(panel|committee|board|authors|members|writers)',
        r'what\s+version\s+is\s+this',
        r'who\s+is\s+the\s+(author|writer|publisher|creator)',
        r'authorship\s+metadata'
    ]
    return any(re.search(pat, q_lower) for pat in meta_patterns)


def requires_institution_specific_fact(query: str) -> bool:
    """Check if query requires specific institution facts (dates, numbers, deadlines, named people)."""
    q_lower = query.lower()
    fact_keywords = ["deadline", "fee", "stipend", "gpa", "hours", "percent", "%", "fine", "dollar", "$", "date", "phone", "email"]
    if any(k in q_lower for k in fact_keywords):
        return True
    if re.search(r'\b(how many|how much|when is|what is the deadline|what is the fee|what is the stipend)\b', q_lower):
        return True
    return False


def is_general_policy_topic(query: str) -> bool:
    """Check if query is a general academic-policy concept (Section 9 PDF spec)."""
    q_lower = query.lower()

    # Exclude trivia, people, location, and founding questions
    trivia_patterns = [
        r'\bwho\s+is\s+(the\s+)?(founder|owner|president|ceo|inventor|author|creator|head)\b',
        r'\bwhere\s+is\b', r'\bwhen\s+was\s+(founded|built|established)\b',
        r'\bcapital\s+of\b', r'\bpopulation\s+of\b'
    ]
    if any(re.search(pat, q_lower) for pat in trivia_patterns):
        return False

    general_topics = [
        "appeal", "plagiarism", "probation", "attendance", "grading", "conduct", "syllabus",
        "credit", "semester", "academic policy", "exam", "grade", "gpa", "major", "minor",
        "thesis", "dissertation", "prerequisite", "transcript", "tuition", "scholarship",
        "financial aid", "internship", "graduation", "enrollment", "expulsion", "suspension",
        "dormitory", "residence hall", "office hour", "retire", "tenure", "academic integrity",
        "lab", "safety", "goggles", "waiver", "cloud", "storage", "quad", "event", "permit",
        "re-checking", "re-evaluation", "incomplete", "hostel", "microwave", "appliance",
        "hospitalization", "medical", "leave", "absence", "dress code", "uniform", "ragging",
        "fee", "installment", "refund", "cancellation", "immersion", "placement", "contest",
        "bonafide", "certificate", "id card", "identity", "code of conduct"
    ]
    return any(t in q_lower for t in general_topics)


def is_permission_query(query: str) -> bool:
    """Detect permission, compliance, or prohibition queries ('could I do this', 'can I', 'is it allowed')."""
    q_lower = query.lower()
    perm_patterns = [
        r'\b(can|could|may)\s+(i|we|a\s+student|faculty|students)\b',
        r'\bis\s+it\s+(allowed|permitted|prohibited|forbidden|illegal|against\s+policy|a\s+violation|acceptable)\b',
        r'\bam\s+i\s+(allowed|permitted)\b',
        r'\bare\s+(students|faculty)\s+(allowed|permitted)\b',
        r'\bwhat\s+happens\s+if\s+i\b',
        r'\bis\s+there\s+a\s+penalty\s+for\b',
        r'\bis\s+it\s+against\s+policy\b',
        r'\bcan\s+i\s+bring\b',
        r'\bis\s+it\s+permitted\s+to\b',
        r'\bcould\s+i\s+request\b'
    ]
    return any(re.search(pat, q_lower) for pat in perm_patterns)
