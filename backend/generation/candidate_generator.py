from typing import List, Dict, Any
from backend.config import settings
from backend.context.engineer import ContextPackage
from backend.models.model_client import get_model_client


def generate_candidates_for_context(
    context_pkg: ContextPackage,
    n_candidates: int = settings.generation.num_candidates,
    temperature: float = settings.generation.temperature
) -> List[Dict[str, Any]]:
    """
    Generate n independent candidate answers for the given context package.
    Returns list of candidate objects: [{'candidate_id': 0, 'text': '...'}]
    """
    client = get_model_client()
    raw_candidates = client.generate_candidates(
        prompt_string=context_pkg.prompt_string,
        context_text=context_pkg.context_text,
        user_query=context_pkg.original_query,
        n=n_candidates,
        temperature=temperature,
        top_p=settings.generation.top_p
    )

    candidates = []
    for idx, text in enumerate(raw_candidates):
        candidates.append({
            "candidate_id": idx,
            "text": text
        })

    return candidates
