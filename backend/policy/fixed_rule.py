from typing import Tuple, List
from backend.config import settings

def select_action_fixed_rule(
    entropy: float,
    max_similarity: float,
    retrieval_round: int,
    max_rounds: int = settings.entropy.max_retrieval_rounds,
    entropy_threshold: float = settings.entropy.fixed_rule_entropy_threshold,
    similarity_threshold: float = settings.entropy.fixed_rule_similarity_threshold
) -> Tuple[int, str, List[str]]:
    """
    Fixed-Rule baseline policy (Section 12 of specification):
    - Action 0: "ANSWER"
    - Action 1: "RETRIEVE_MORE"
    - Action 2: "ABSTAIN"
    """
    decision_factors = []

    if entropy <= entropy_threshold and max_similarity >= similarity_threshold:
        action = 0
        action_str = "ANSWER"
        decision_factors.append(f"Low semantic entropy ({entropy:.2f} < {entropy_threshold})")
        decision_factors.append(f"Strong evidence similarity ({max_similarity:.2f} >= {similarity_threshold})")
        decision_factors.append("High candidate agreement across sampled generations")
    elif retrieval_round < max_rounds and (entropy >= entropy_threshold or max_similarity < similarity_threshold):
        action = 1
        action_str = "RETRIEVE_MORE"
        if entropy >= entropy_threshold:
            decision_factors.append(f"Elevated semantic entropy ({entropy:.2f} >= {entropy_threshold})")
        if max_similarity < similarity_threshold:
            decision_factors.append(f"Sub-optimal retrieval similarity ({max_similarity:.2f} < {similarity_threshold})")
        decision_factors.append(f"Retrieval budget remaining (Round {retrieval_round} of {max_rounds})")
    else:
        action = 2
        action_str = "ABSTAIN"
        decision_factors.append("Insufficient grounded evidence in knowledge base")
        if retrieval_round >= max_rounds:
            decision_factors.append(f"Max retrieval rounds reached ({max_rounds})")
        if max_similarity < settings.retrieval.domain_threshold:
            decision_factors.append("Query classified as out-of-domain or unsupported policy topic")

    return action, action_str, decision_factors
