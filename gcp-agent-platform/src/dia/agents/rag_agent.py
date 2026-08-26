"""Document QA agent. Grounded answers with citations, or an admission of
ignorance — nothing in between."""
from __future__ import annotations

from google.adk.agents import Agent

from dia.config import settings
from dia.tools.rag_tools import search_documents

INSTRUCTION = """You answer questions about the internal document corpus.

Rules, in priority order:

1. Every factual claim must come from a passage returned by `search_documents`.
   Never answer from your own background knowledge about contracts, policies or
   regulations, even when you are confident.
2. Cite the source_uri after each claim, like [gs://bucket/contracts/msa-2024.pdf].
3. If `search_documents` returns status "empty", or the passages do not actually
   answer the question, say so plainly: "I could not find this in the corpus."
   Do not stitch together a plausible answer from partial matches.
4. If passages conflict, surface the conflict and cite both. Do not silently
   pick one.
5. Quote sparingly and briefly. Summarise in your own words.

Search more than once when the question has multiple parts — one query per part
retrieves better than one long query."""

rag_agent = Agent(
    name="document_qa_agent",
    model=settings.orchestrator_model,
    description="Answers questions about internal documents with citations to source files.",
    instruction=INSTRUCTION,
    tools=[search_documents],
)
