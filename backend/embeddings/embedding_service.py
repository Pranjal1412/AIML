import hashlib
import numpy as np
from typing import List
from backend.config import settings

_model_instance = None


class EmbeddingService:
    def __init__(self, model_name: str = "all-mpnet-base-v2"):
        self.model_name = model_name
        self.model = None
        self._init_model()

    def _init_model(self):
        global _model_instance
        if _model_instance is not None:
            self.model = _model_instance
            return

        try:
            from sentence_transformers import SentenceTransformer
            print(f"[EmbeddingService] Loading SentenceTransformer: {self.model_name}...")
            self.model = SentenceTransformer(self.model_name)
            _model_instance = self.model
            print("[EmbeddingService] Model loaded successfully.")
        except Exception as e:
            print(f"[EmbeddingService] Could not load SentenceTransformer ({e}). Using deterministic fallback encoder.")
            self.model = None

    def encode_single(self, text: str) -> List[float]:
        return self.encode([text])[0]

    def encode(self, texts: List[str]) -> List[List[float]]:
        if self.model is not None:
            embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
            return embeddings.tolist()
        else:
            # Deterministic fallback embedding generator (768-dim pseudo vector)
            return [self._fallback_encode(t) for t in texts]

    def _fallback_encode(self, text: str, dim: int = 768) -> List[float]:
        """Generate deterministic normalized unit vector from text hash + word counts."""
        words = text.lower().split()
        vec = np.zeros(dim, dtype=np.float32)
        for idx, word in enumerate(words):
            h = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)
            pos = h % dim
            val = (h % 100) / 50.0 - 1.0
            vec[pos] += val

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        else:
            vec[0] = 1.0
        return vec.tolist()


_embedding_service = None

def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService("all-mpnet-base-v2")
    return _embedding_service
