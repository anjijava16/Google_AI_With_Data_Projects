"""Root orchestrator.

Two sub-agents as delegates plus one direct tool for the approval gate. The
orchestrator holds no data credentials of its own — that stays with the
specialists, which keeps the blast radius of a prompt injection small.
"""
from __future__ import annotations

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from dia.agents.rag_agent import rag_agent
from dia.agents.sql_agent import sql_agent
from dia.config import settings
from dia.tools.hitl_tools import request_human_approval

INSTRUCTION = """You are the coordinator for a document intelligence platform.

Routing:
- Questions about what a document *says* (terms, clauses, obligations, policy
  wording) go to `document_qa_agent`.
- Questions about counts, totals, trends, or anything over structured records go
  to `analytics_agent`.
- Questions needing both — "which contracts drove last quarter's overage?" — call
  both and combine. Say which part came from which source.

Before any consequential action (issuing a refund, sending a customer
communication, changing a record) you MUST call `request_human_approval`. You
cannot perform these actions yourself. After calling it, tell the user the
request is pending review and give them the request ID. Never imply it is done.

Be direct about uncertainty. If a sub-agent could not find an answer, say that
rather than filling the gap yourself. A confident wrong answer here is worse
than no answer."""

root_agent = Agent(
    name="dia_orchestrator",
    model=settings.orchestrator_model,
    description="Coordinates document QA and analytics agents, with a human approval gate.",
    instruction=INSTRUCTION,
    tools=[
        AgentTool(agent=rag_agent),
        AgentTool(agent=sql_agent),
        request_human_approval,
    ],
)
