"""Retrieval tools exposed to the agent.

Two paths on purpose:
  managed_retrieval_tool() -> hand Gemini a grounding tool, Google runs retrieval
  custom_retrieve()        -> you run retrieval, you rerank, you build context

The managed tool is faster to ship. The custom path is what you reach for when
retrieval quality plateaus and you need to see and fix every stage.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from google.genai import types as genai_types

from dia.config import settings

log = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    text: str
    source_uri: str
    score: float


def managed_retrieval_tool(corpus_name: str | None = None) -> genai_types.Tool:
    """A grounding tool Gemini calls itself. Closest analogue: attaching a
    Bedrock Knowledge Base to a Bedrock Agent."""
    corpus = corpus_name or settings.rag_corpus
    if not corpus:
        raise RuntimeError("RAG_CORPUS is not set — run dia.ingestion.build_corpus first")

    return genai_types.Tool(
        retrieval=genai_types.Retrieval(
            vertex_rag_store=genai_types.VertexRagStore(
                rag_resources=[genai_types.VertexRagStoreRagResource(rag_corpus=corpus)],
                rag_retrieval_config=genai_types.RagRetrievalConfig(
                    top_k=settings.retrieval_top_k,
                    filter=genai_types.RagRetrievalConfigFilter(
                        vector_distance_threshold=settings.vector_distance_threshold
                    ),
                ),
            )
        )
    )


def custom_retrieve(query: str, top_k: int | None = None) -> list[RetrievedChunk]:
    """Explicit retrieval you can inspect, log, rerank and evaluate."""
    import agentplatform

    corpus = settings.rag_corpus
    if not corpus:
        raise RuntimeError("RAG_CORPUS is not set")

    client = agentplatform.Client(project=settings.project_id, location=settings.location)
    response = client.rag.retrieve_contexts(
        vertex_rag_store=genai_types.VertexRagStore(
            rag_resources=[genai_types.VertexRagStoreRagResource(rag_corpus=corpus)],
            rag_retrieval_config=genai_types.RagRetrievalConfig(
                top_k=top_k or settings.retrieval_top_k,
                filter=genai_types.RagRetrievalConfigFilter(
                    vector_distance_threshold=settings.vector_distance_threshold
                ),
            ),
        ),
        query=genai_types.RagQuery(text=query),
    )

    out: list[RetrievedChunk] = []
    for ctx in getattr(response.contexts, "contexts", []) or []:
        out.append(
            RetrievedChunk(
                text=getattr(ctx, "text", "") or "",
                source_uri=getattr(ctx, "source_uri", "") or "",
                score=float(getattr(ctx, "score", 0.0) or 0.0),
            )
        )
    return out


def search_documents(query: str) -> dict:
    """ADK tool: search the document corpus.

    Returns passages with their source URIs so the model can cite them. Always
    cite the source_uri of any passage you use.

    Args:
        query: A natural-language question about the document corpus.
    """
    try:
        chunks = custom_retrieve(query)
    except Exception as exc:  # surface failure to the model, do not crash the turn
        log.exception("retrieval failed")
        return {"status": "error", "error": str(exc), "passages": []}

    if not chunks:
        return {
            "status": "empty",
            "passages": [],
            "note": "No passages passed the similarity threshold. Say you do not know.",
        }

    return {
        "status": "ok",
        "passages": [
            {"text": c.text, "source_uri": c.source_uri, "score": round(c.score, 4)}
            for c in chunks
        ],
    }
