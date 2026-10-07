import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.api.routes import router as api_router

app = FastAPI(
    title=settings.system.name,
    version=settings.system.version,
    description="Mitigating LLM Hallucinations via RL-Driven Context Optimization"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": settings.system.name,
        "version": settings.system.version,
        "domain": settings.system.domain,
        "demo_mode": settings.system.demo_mode
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "models_loaded": {
            "embeddings": True,
            "llm_client": settings.generation.model_provider,
            "nli_cross_encoder": settings.nli.model_name,
            "policy_mode": settings.policy.mode
        },
        "config": {
            "demo_mode": settings.system.demo_mode,
            "top_k": settings.retrieval.top_k_round_1,
            "candidates": settings.generation.num_candidates
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_excludes=["storage/*", "logs/*", "scratch/*", "frontend/*", "data/*"]
    )
