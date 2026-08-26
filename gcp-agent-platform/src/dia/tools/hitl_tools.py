"""Human-in-the-loop gate.

The pattern that matters: the agent cannot perform the sensitive action itself.
It can only *request* approval. A separate system approves, and the agent polls
or resumes. If the agent holds the credential to act unilaterally, you do not
have a human in the loop — you have a human being informed.
"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone

from dia.config import settings

log = logging.getLogger(__name__)


def request_human_approval(action: str, justification: str, confidence: float) -> dict:
    """ADK tool: request human approval for a consequential action.

    Call this before any action that changes state, releases money, or sends
    something to a customer — and any time your own confidence is low. Do not
    tell the user the action is done; tell them it is pending review.

    Args:
        action: Plain description of what should happen, e.g. "issue refund of $412.00 on case 88213".
        justification: Why you believe this is correct, citing evidence.
        confidence: Your confidence between 0.0 and 1.0.
    """
    if not 0.0 <= confidence <= 1.0:
        return {"status": "error", "error": "confidence must be between 0 and 1"}

    request_id = str(uuid.uuid4())
    payload = {
        "request_id": request_id,
        "action": action,
        "justification": justification,
        "confidence": round(confidence, 3),
        "auto_approvable": confidence >= settings.hitl_threshold,
        "requested_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        from google.cloud import pubsub_v1

        publisher = pubsub_v1.PublisherClient()
        topic = publisher.topic_path(settings.project_id, settings.hitl_topic)
        publisher.publish(topic, json.dumps(payload).encode("utf-8")).result(timeout=30)
        delivered = True
    except Exception as exc:
        log.exception("failed to publish approval request")
        delivered = False
        payload["publish_error"] = str(exc)

    return {
        "status": "pending_approval" if delivered else "error",
        "request_id": request_id,
        "message": (
            "Approval request submitted. The action has NOT been performed. "
            "Tell the user it is awaiting human review and give them this request ID."
        ),
        **payload,
    }
