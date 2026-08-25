from __future__ import annotations

import json
import os
import uuid
from datetime import UTC, datetime
from typing import Any

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agent import app


class AgentQuotaExceeded(RuntimeError):
    pass


def _consume_cloud_quota(limit: int = 30) -> None:
    if os.getenv("REVENUE_SENTINEL_LEDGER", "memory").lower() != "firestore":
        return

    from google.cloud import firestore

    client = firestore.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT") or None)
    hour = datetime.now(UTC).strftime("%Y%m%d%H")
    reference = client.collection("revenue_sentinel_limits").document(f"agent-{hour}")
    transaction = client.transaction()

    @firestore.transactional
    def increment(active_transaction: Any) -> None:
        snapshot = reference.get(transaction=active_transaction)
        count = int(snapshot.get("count")) if snapshot.exists else 0
        if count >= limit:
            raise AgentQuotaExceeded("Live Gemini demo hourly limit reached")
        active_transaction.set(
            reference,
            {"count": count + 1, "hour_utc": hour, "limit": limit},
            merge=False,
        )

    increment(transaction)


async def audit_with_agent(opportunity: dict[str, Any]) -> dict[str, Any]:
    """Run one bounded ADK/Gemini audit and return its final explanation and tool trace."""
    _consume_cloud_quota()
    user_id = "cloud-demo"
    session_id = uuid.uuid4().hex
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=app.name,
        user_id=user_id,
        session_id=session_id,
    )
    runner = Runner(app=app, session_service=session_service)
    message = types.Content(
        role="user",
        parts=[
            types.Part(
                text=(
                    "Audit this opportunity. Call audit_opportunity before explaining the decision. "
                    "Return the decision, expected value, risk, evidence gaps, action gate, and next action.\n\n"
                    + json.dumps(opportunity, sort_keys=True)
                )
            )
        ],
    )

    response_text = ""
    tool_calls: list[str] = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message,
    ):
        tool_calls.extend(call.name for call in event.get_function_calls() if call.name)
        if event.is_final_response() and event.content:
            response_text = "".join(part.text or "" for part in event.content.parts if part.text)

    if not response_text:
        raise RuntimeError("Gemini returned no final response")

    return {
        "model": "gemini-3.5-flash",
        "agent": app.root_agent.name,
        "tool_calls": tool_calls,
        "response": response_text,
    }
