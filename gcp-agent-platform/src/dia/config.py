"""Central config. Everything reads from env so the same code runs locally,
on Cloud Run, and inside Agent Runtime without branching."""
from __future__ import annotations

import os
from dataclasses import dataclass, field


def _env(key: str, default: str | None = None, required: bool = False) -> str:
    val = os.getenv(key, default)
    if required and not val:
        raise RuntimeError(f"Missing required env var: {key}")
    return val or ""


@dataclass(frozen=True)
class Settings:
    # --- project / location -------------------------------------------------
    project_id: str = field(default_factory=lambda: _env("GOOGLE_CLOUD_PROJECT", required=True))
    location: str = field(default_factory=lambda: _env("GOOGLE_CLOUD_LOCATION", "us-central1"))

    # --- models -------------------------------------------------------------
    # Pin these. Do not let a default drift under you between environments.
    # Verify what your project actually has:
    #   gcloud ai models list --region=$GOOGLE_CLOUD_LOCATION
    orchestrator_model: str = field(default_factory=lambda: _env("ORCHESTRATOR_MODEL", "gemini-3.5-flash"))
    reasoning_model: str = field(default_factory=lambda: _env("REASONING_MODEL", "gemini-2.5-pro"))
    embedding_model: str = field(default_factory=lambda: _env("EMBEDDING_MODEL", "text-embedding-005"))

    # --- storage ------------------------------------------------------------
    raw_bucket: str = field(default_factory=lambda: _env("RAW_BUCKET"))
    staging_bucket: str = field(default_factory=lambda: _env("STAGING_BUCKET"))

    # --- retrieval ----------------------------------------------------------
    rag_corpus: str = field(default_factory=lambda: _env("RAG_CORPUS"))  # full resource name
    retrieval_top_k: int = field(default_factory=lambda: int(_env("RETRIEVAL_TOP_K", "10")))
    vector_distance_threshold: float = field(
        default_factory=lambda: float(_env("VECTOR_DISTANCE_THRESHOLD", "0.5"))
    )

    # --- analytics ----------------------------------------------------------
    bq_dataset: str = field(default_factory=lambda: _env("BQ_DATASET", "dia_analytics"))
    bq_max_bytes_billed: int = field(
        default_factory=lambda: int(_env("BQ_MAX_BYTES_BILLED", str(2 * 1024**3)))
    )

    # --- governance ---------------------------------------------------------
    hitl_threshold: float = field(default_factory=lambda: float(_env("HITL_THRESHOLD", "0.75")))
    hitl_topic: str = field(default_factory=lambda: _env("HITL_TOPIC", "dia-approvals"))

    @property
    def genai_kwargs(self) -> dict:
        """Kwargs for google.genai.Client() when talking to Agent Platform
        rather than the public Gemini API."""
        return {"vertexai": True, "project": self.project_id, "location": self.location}


settings = Settings()
