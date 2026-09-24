from backend.config import settings

def compute_reward(
    action: int,
    is_correct_grounded: bool,
    is_hallucinated_unsupported: bool,
    retrieval_rounds_used: int,
    sufficient_evidence_exists: bool,
    is_out_of_domain: bool
) -> float:
    """
    Reward function for RL policy optimization:
    - Action 0: ANSWER
    - Action 1: RETRIEVE_MORE
    - Action 2: ABSTAIN
    """
    w = settings.reward_weights
    reward = 0.0

    if action == 0:  # ANSWER
        if is_correct_grounded and not is_hallucinated_unsupported:
            reward += w.w_correct
        else:
            reward += w.w_halluc

    elif action == 1:  # RETRIEVE_MORE
        # Small cost for each retrieval round to discourage endless loops
        reward += w.w_cost * retrieval_rounds_used

    elif action == 2:  # ABSTAIN
        if not sufficient_evidence_exists or is_out_of_domain:
            reward += w.w_good_abstain
        else:
            # Penalty for refusing to answer when sufficient evidence was present
            reward += w.w_bad_abstain

    return round(float(reward), 4)
