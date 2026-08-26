"""FastAPI front door.

Deployment choice you have to make once and live with:

  Cloud Run       — you own the container, the HTTP surface, the session store.
                    Deploy anything. This file is that path.
  Agent Runtime   — Google owns the runtime, sessions and Memory Bank come
                    managed. Less control, much less to operate.

Cloud Run is closer to what you already do with ECS/Fargate + FastAPI. Agent
Runtime is closer to Bedrock AgentCore. Start on Cloud Run while iterating,
move to Agent Runtime when session and memory management stops being fun.
"""
from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from dia.config import settings
from dia.obs.tracing import init_tracing, span

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = FastAPI(title="Document Intelligence Agent", version="1.0.0")

_runner: Any = None
_session_service: Any = None
APP_NAME = "dia"


@app.on_event("startup")
async def _startup() -> None:
    global _runner, _session_service
    init_tracing("dia-api")

    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService, VertexAiSessionService

    from dia.agents.root_agent import root_agent

    # In-memory sessions vanish on every Cloud Run scale-to-zero. Fine for dev,
    # wrong for production — use the managed session service there.
    if os.getenv("USE_MANAGED_SESSIONS", "false").lower() == "true":
        _session_service = VertexAiSessionService(
            project=settings.project_id, location=settings.location
        )
    else:
        _session_service = InMemorySessionService()

    _runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=_session_service)
    log.info("agent ready (managed_sessions=%s)", os.getenv("USE_MANAGED_SESSIONS", "false"))


class ChatRequest(BaseModel):
    user_id: str = Field(..., max_length=128)
    session_id: str | None = None
    message: str


@app.get("/healthz")
async def healthz() -> dict:
    # Liveness only. Do not call Gemini here — Cloud Run probes this often and
    # you will pay for every probe.
    return {"status": "ok", "model": settings.orchestrator_model}


@app.post("/chat")
async def chat(req: ChatRequest) -> dict:
    if _runner is None:
        raise HTTPException(503, "agent not initialised")

    from google.genai import types as genai_types

    session = await _session_service.create_session(
        app_name=APP_NAME, user_id=req.user_id, session_id=req.session_id
    )
    content = genai_types.Content(role="user", parts=[genai_types.Part(text=req.message)])

    final_text, tool_calls = "", []
    with span("chat.turn", user_id=req.user_id, session_id=session.id):
        async for event in _runner.run_async(
            user_id=req.user_id, session_id=session.id, new_message=content
        ):
            for part in getattr(event.content, "parts", []) or []:
                if getattr(part, "function_call", None):
                    tool_calls.append(part.function_call.name)
            if event.is_final_response() and event.content and event.content.parts:
                final_text = "".join(p.text or "" for p in event.content.parts)

    return {"session_id": session.id, "response": final_text, "tool_calls": tool_calls}


@app.post("/chat/stream")
async def chat_stream(req: ChatRequest) -> StreamingResponse:
    """SSE streaming. Two things people get wrong on Cloud Run:
    disable response buffering, and set a request timeout longer than your
    worst-case agent turn (`--timeout=900`), or long turns get cut mid-stream."""
    if _runner is None:
        raise HTTPException(503, "agent not initialised")

    from google.genai import types as genai_types

    session = await _session_service.create_session(
        app_name=APP_NAME, user_id=req.user_id, session_id=req.session_id
    )
    content = genai_types.Content(role="user", parts=[genai_types.Part(text=req.message)])

    async def generate():
        import json

        yield f"data: {json.dumps({'type': 'session', 'session_id': session.id})}\n\n"
        try:
            async for event in _runner.run_async(
                user_id=req.user_id, session_id=session.id, new_message=content
            ):
                for part in getattr(event.content, "parts", []) or []:
                    if getattr(part, "function_call", None):
                        yield f"data: {json.dumps({'type': 'tool', 'name': part.function_call.name})}\n\n"
                    elif getattr(part, "text", None):
                        yield f"data: {json.dumps({'type': 'text', 'text': part.text})}\n\n"
        except Exception as exc:
            log.exception("stream failed")
            yield f"data: {json.dumps({'type': 'error', 'error': str(exc)})}\n\n"
        yield "data: {\"type\": \"done\"}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
