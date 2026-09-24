import math
import numpy as np
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from backend.config import settings

@dataclass
class Cluster:
    cluster_id: int
    candidate_ids: List[int]
    probability_mass: float
    representative_text: str


@dataclass
class EntropyResult:
    clusters: List[Cluster]
    num_clusters: int
    top_cluster_mass: float
    entropy: float
    normalized_entropy: float
    nli_matrix: List[List[float]]


class UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))

    def find(self, i: int) -> int:
        if self.parent[i] == i:
            return i
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i: int, j: int):
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            self.parent[root_i] = root_j


def cluster_candidates(
    candidates: List[Dict[str, Any]],
    nli_matrix: np.ndarray,
    entailment_threshold: float = settings.nli.entailment_threshold
) -> List[Cluster]:
    """
    Form semantic clusters using Union-Find on bidirectional entailment graph.
    Rule: Candidates A and B are equivalent iff Entailment(A->B) > threshold AND Entailment(B->A) > threshold.
    """
    n = len(candidates)
    if n == 0:
        return []

    uf = UnionFind(n)
    for i in range(n):
        for j in range(i + 1, n):
            # Bidirectional entailment check
            if nli_matrix[i][j] >= entailment_threshold and nli_matrix[j][i] >= entailment_threshold:
                uf.union(i, j)

    groups: Dict[int, List[int]] = {}
    for i in range(n):
        root = uf.find(i)
        groups.setdefault(root, []).append(i)

    clusters = []
    for c_id, (root, member_ids) in enumerate(groups.items()):
        prob_mass = len(member_ids) / float(n)
        # Select representative candidate (first member or lowest perplexity)
        rep_text = candidates[member_ids[0]]["text"]
        clusters.append(Cluster(
            cluster_id=c_id,
            candidate_ids=member_ids,
            probability_mass=round(prob_mass, 4),
            representative_text=rep_text
        ))

    # Sort clusters by probability mass descending
    clusters.sort(key=lambda c: c.probability_mass, reverse=True)
    return clusters


def compute_semantic_entropy(
    candidates: List[Dict[str, Any]],
    nli_matrix: np.ndarray,
    entailment_threshold: float = settings.nli.entailment_threshold
) -> EntropyResult:
    """
    Calculate semantic entropy over candidate clusters:
    H = - sum(p_i * log(p_i))
    Normalized H = H / log(n)
    """
    n = len(candidates)
    if n <= 1:
        return EntropyResult(
            clusters=[Cluster(0, [0], 1.0, candidates[0]["text"] if candidates else "")],
            num_clusters=1,
            top_cluster_mass=1.0,
            entropy=0.0,
            normalized_entropy=0.0,
            nli_matrix=nli_matrix.tolist() if isinstance(nli_matrix, np.ndarray) else nli_matrix
        )

    clusters = cluster_candidates(candidates, nli_matrix, entailment_threshold)

    raw_h = 0.0
    for c in clusters:
        p = c.probability_mass
        if p > 0:
            raw_h -= p * math.log(p)

    max_possible_h = math.log(n)
    normalized_h = raw_h / max_possible_h if max_possible_h > 0 else 0.0

    # Ensure continuous bounds [0.0, 1.0]
    normalized_h = max(0.0, min(1.0, normalized_h))

    top_mass = clusters[0].probability_mass if clusters else 0.0

    return EntropyResult(
        clusters=clusters,
        num_clusters=len(clusters),
        top_cluster_mass=round(top_mass, 4),
        entropy=round(raw_h, 4),
        normalized_entropy=round(normalized_h, 4),
        nli_matrix=nli_matrix.tolist() if isinstance(nli_matrix, np.ndarray) else nli_matrix
    )
