import numpy as np
from typing import List, Dict, Any, Tuple
from backend.config import settings

_nli_model_instance = None


class NLIService:
    def __init__(self, model_name: str = settings.nli.model_name):
        self.model_name = model_name
        self.model = None
        self._init_nli_model()

    def _init_nli_model(self):
        global _nli_model_instance
        if _nli_model_instance is not None:
            self.model = _nli_model_instance
            return

        try:
            from sentence_transformers import CrossEncoder
            print(f"[NLIService] Loading CrossEncoder NLI model: {self.model_name}...")
            self.model = CrossEncoder(self.model_name)
            _nli_model_instance = self.model
            print("[NLIService] CrossEncoder NLI model loaded successfully.")
        except Exception as e:
            print(f"[NLIService] Could not load CrossEncoder ({e}). Using semantic similarity NLI fallback.")
            self.model = None

    def compute_pairwise_nli(self, candidates: List[Dict[str, Any]]) -> np.ndarray:
        """
        Compute NxN matrix of bidirectional entailment probability scores between all candidate pairs.
        Returns NxN numpy array where matrix[i][j] = entailment score of Candidate i -> Candidate j.
        """
        n = len(candidates)
        matrix = np.ones((n, n), dtype=np.float32)

        if n <= 1:
            return matrix

        pairs = []
        pair_indices = []
        for i in range(n):
            for j in range(n):
                if i != j:
                    pairs.append((candidates[i]["text"], candidates[j]["text"]))
                    pair_indices.append((i, j))

        if self.model is not None:
            try:
                # CrossEncoder output logits or probabilities for [contradiction, entailment, neutral]
                scores = self.model.predict(pairs, apply_softmax=True)
                for idx, (i, j) in enumerate(pair_indices):
                    # Index 1 is typically entailment in DeBERTa NLI
                    entail_prob = float(scores[idx][1]) if len(scores[idx]) > 1 else float(scores[idx][0])
                    matrix[i][j] = round(entail_prob, 4)
                return matrix
            except Exception as e:
                print(f"[NLIService] CrossEncoder inference failed: {e}")

        # Fallback NLI using word embedding / token overlap similarity
        for idx, (i, j) in enumerate(pair_indices):
            w1 = set(candidates[i]["text"].lower().split())
            w2 = set(candidates[j]["text"].lower().split())
            if not w1 or not w2:
                sim = 1.0
            else:
                jaccard = len(w1 & w2) / float(len(w1 | w2))
                sim = min(1.0, jaccard * 1.3)
            matrix[i][j] = round(sim, 4)

        return matrix


_nli_service_instance = None

def get_nli_service() -> NLIService:
    global _nli_service_instance
    if _nli_service_instance is None:
        _nli_service_instance = NLIService()
    return _nli_service_instance
