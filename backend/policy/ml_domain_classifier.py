import numpy as np
from typing import Tuple, Dict, Any, List
from backend.config import settings
from backend.embeddings.embedding_service import get_embedding_service
from backend.retrieval.vector_store import get_vector_store

class MLDomainClassifier:
    """
    Pure Machine Learning & Semantic Vector Embedding Classifier.
    Uses 768-dimensional dense vector embeddings and Cosine Similarity to classify queries
    into Academic Policy Domain vs Off-Domain Trivia without hardcoded keyword lists.
    """
    def __init__(self):
        self.embedding_service = get_embedding_service()
        self.vector_store = get_vector_store()
        self.temperature = 0.1

        # High-level academic policy latent anchor concepts (Embedded into 768d space)
        self.academic_anchors = [
            "university regulations, student manual guidelines, academic policies, campus rules",
            "tuition fees, administrative charges, refund policies, installment schedules, account department",
            "disciplinary actions, code of conduct, penalties, punishments, suspensions, expulsions, violations",
            "examination rules, continuous evaluation, grading schemes, term end exams, re-checking",
            "attendance requirements, leave of absence, medical waivers, absenteeism guidelines",
            "residence hall regulations, hostel rules, quiet hours, room allotments, guest policies",
            "laboratory safety protocols, emergency procedures, personal protective equipment, eyewash stations",
            "student services, bonafide certificates, transfer migration certificates, id card replacement",
            "library borrowing rules, overdue fines, electronic resources, reserve materials",
            "internships, campus placement process, pre-placement offers, career services",
            "student organization chartering, club budget allocation, campus event permits"
        ]

        # High-level off-domain trivia latent anchor concepts (Embedded into 768d space)
        self.trivia_anchors = [
            "general geography, world capitals, countries, mountains, rivers, world maps",
            "celebrity gossip, movie directors, hollywood cinema, pop music, actors, entertainment, films",
            "sports championships, world cup winners, olympic medals, football matches, athlete statistics",
            "historical events, ancient history, military battles, political elections, world leaders",
            "aerospace engineering, boeing aircraft specifications, wingspans, aviation, flight technology, planes",
            "cooking recipes, restaurant reviews, food cuisine, baking ingredients, culinary arts",
            "physics, astronomy, speed of light, planetary orbits, quantum mechanics, solar system",
            "biology trivia, animal species, wildlife, dinosaurs, zoology, nature facts"
        ]

        self._initialize_centroids()

    def _initialize_centroids(self):
        """Compute 768-dimensional latent vector centroids for academic vs trivia spaces."""
        academic_vecs = np.array(self.embedding_service.encode(self.academic_anchors))
        trivia_vecs = np.array(self.embedding_service.encode(self.trivia_anchors))

        # Calculate unit-normalized centroid vectors
        academic_mean = np.mean(academic_vecs, axis=0)
        self.academic_centroid = academic_mean / (np.linalg.norm(academic_mean) + 1e-9)

        trivia_mean = np.mean(trivia_vecs, axis=0)
        self.trivia_centroid = trivia_mean / (np.linalg.norm(trivia_mean) + 1e-9)

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two normalized vectors."""
        return float(np.dot(vec1, vec2) / ((np.linalg.norm(vec1) * np.linalg.norm(vec2)) + 1e-9))

    def classify_query(self, query: str) -> Tuple[bool, float, Dict[str, float]]:
        """
        Classify query using pure ML vector embeddings.
        Returns: (is_academic_policy, academic_probability, metadata_scores)
        """
        query_vec = np.array(self.embedding_service.encode_single(query))
        query_norm = query_vec / (np.linalg.norm(query_vec) + 1e-9)

        # 1. Compute Cosine Similarity to ML Latent Centroids
        sim_academic = self._cosine_similarity(query_norm, self.academic_centroid)
        sim_trivia = self._cosine_similarity(query_norm, self.trivia_centroid)

        # 2. Check Vector Store Similarity against Ingested PDF Chunks
        retrieved = self.vector_store.query(query, top_k=3)
        max_corpus_sim = max([c.get("similarity", 0.0) for c in retrieved]) if retrieved else 0.0

        # 3. Compute Softmax Academic Domain Probability
        exp_acad = np.exp(sim_academic / self.temperature)
        exp_triv = np.exp(sim_trivia / self.temperature)
        academic_prob = float(exp_acad / (exp_acad + exp_triv + 1e-9))

        # A query is in-domain academic policy if academic vector centroid similarity > trivia centroid similarity
        # OR if vector store evidence similarity >= min_evidence_similarity (0.55)
        if sim_trivia > sim_academic and max_corpus_sim < settings.retrieval.min_evidence_similarity:
            is_academic = False
        else:
            is_academic = (academic_prob >= 0.50) or (max_corpus_sim >= settings.retrieval.min_evidence_similarity)

        scores = {
            "academic_similarity": round(float(sim_academic), 4),
            "trivia_similarity": round(float(sim_trivia), 4),
            "corpus_max_similarity": round(float(max_corpus_sim), 4),
            "academic_probability": round(academic_prob, 4)
        }

        return is_academic, academic_prob, scores


_classifier_instance = None

def get_ml_domain_classifier() -> MLDomainClassifier:
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = MLDomainClassifier()
    return _classifier_instance
