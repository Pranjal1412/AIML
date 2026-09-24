import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from pydantic import BaseModel, Field

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.yaml"


class SystemConfig(BaseModel):
    name: str = "The Semantic Entropy Engine"
    version: str = "1.0.0"
    domain: str = "Academic Institutions"
    demo_mode: bool = True
    seed: int = 42


class ChunkingConfig(BaseModel):
    chunk_size: int = 500
    chunk_overlap: int = 75
    min_chunk_len: int = 30


class RetrievalConfig(BaseModel):
    collection_name: str = "institution_policies"
    top_k_round_1: int = 8
    top_k_increment: int = 6
    similarity_threshold: float = 0.55
    domain_threshold: float = 0.55
    min_evidence_similarity: float = 0.55


class ContextEngineeringConfig(BaseModel):
    max_evidence_tokens: int = 1800
    dedup_similarity_threshold: float = 0.90
    enable_reranking: bool = True
    source_tag_prefix: str = "[SOURCE: "
    source_tag_suffix: str = "]"


class GenerationConfig(BaseModel):
    model_provider: str = "huggingface"
    model_name: str = "google/flan-t5-base"
    num_candidates: int = 5
    temperature: float = 0.9
    top_p: float = 0.95
    max_tokens: int = 250


class NLIConfig(BaseModel):
    model_name: str = "cross-encoder/nli-deberta-v3-small"
    entailment_threshold: float = 0.50


class EntropyConfig(BaseModel):
    clustering_method: str = "union_find_bidirectional"
    fixed_rule_entropy_threshold: float = 0.70
    fixed_rule_similarity_threshold: float = 0.55
    entropy_low_threshold: float = 0.70
    entropy_high_threshold: float = 0.75
    general_knowledge_entropy_threshold: float = 0.35
    max_retrieval_rounds: int = 2


class PolicyConfig(BaseModel):
    mode: str = "ppo"
    checkpoint_dir: str = "models/policy_checkpoints"


class RewardWeightsConfig(BaseModel):
    w_correct: float = 1.0
    w_halluc: float = -1.5
    w_cost: float = -0.1
    w_good_abstain: float = 0.5
    w_bad_abstain: float = -0.7


class StorageConfig(BaseModel):
    db_path: str = "storage/app.db"
    eval_dataset_path: str = "storage/eval_dataset.jsonl"
    logs_dir: str = "logs"


class AppSettings(BaseModel):
    system: SystemConfig = Field(default_factory=SystemConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    context_engineering: ContextEngineeringConfig = Field(default_factory=ContextEngineeringConfig)
    generation: GenerationConfig = Field(default_factory=GenerationConfig)
    nli: NLIConfig = Field(default_factory=NLIConfig)
    entropy: EntropyConfig = Field(default_factory=EntropyConfig)
    policy: PolicyConfig = Field(default_factory=PolicyConfig)
    reward_weights: RewardWeightsConfig = Field(default_factory=RewardWeightsConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)


def load_settings() -> AppSettings:
    """Load configuration from config.yaml and environment variables."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            raw_config = yaml.safe_load(f) or {}
    else:
        raw_config = {}

    if "DEMO_MODE" in os.environ:
        demo_flag = os.environ["DEMO_MODE"].lower() in ("true", "1", "yes")
        raw_config.setdefault("system", {})["demo_mode"] = demo_flag

    if "LLM_PROVIDER" in os.environ:
        raw_config.setdefault("generation", {})["model_provider"] = os.environ["LLM_PROVIDER"]

    return AppSettings(**raw_config)


settings = load_settings()
