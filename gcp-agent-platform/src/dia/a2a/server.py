"""Expose the orchestrator as an A2A agent.

MCP and A2A solve different problems and you want both:
  MCP = my agent calls a *tool*        (client -> capability)
  A2A = my agent delegates to an *agent* that has its own model, memory,
        and judgement, and may come back with clarifying questions

The Agent Card at /.well-known/agent-card.json is the discovery contract. Other
teams read it to find out what this agent does and how to reach it — think of it
as the OpenAPI spec of the agent world.

Run:  python -m dia.a2a.server
"""
from __future__ import annotations

import logging
import os

import uvicorn

logging.basicConfig(level=logging.INFO)


def build_app():
    from google.adk.a2a.utils.agent_to_a2a import to_a2a

    from dia.agents.root_agent import root_agent

    host = os.getenv("A2A_PUBLIC_HOST", f"http://localhost:{os.getenv('PORT', '8082')}")
    return to_a2a(root_agent, host=host)


app = build_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8082")))
