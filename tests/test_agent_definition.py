from __future__ import annotations

import json

from app.agent import app, audit_opportunity, create_action_brief, root_agent


def payload() -> str:
    return json.dumps(
        {
            "opportunity_id": "agent-1",
            "title": "Agent test",
            "source_url": "https://example.com/agent",
            "channel": "Hackathon",
            "potential_value_usd": 10_000,
            "deadline_iso": "2099-01-01T00:00:00Z",
            "eligible": None,
            "buyer_verified": True,
            "payment_protected": None,
            "budget_clear": True,
            "scope_clear": True,
            "public_evidence": ["https://example.com/agent", "https://example.com/rules"],
            "external_actions": ["submit"],
        }
    )


def test_adk_agent_identity_and_model() -> None:
    assert app.name == "revenue_sentinel"
    assert root_agent.name == "revenue_sentinel"
    assert root_agent.model.model == "gemini-3.5-flash"
    assert len(root_agent.tools) == 2


def test_agent_audit_tool_preserves_unknown_eligibility_gate() -> None:
    result = audit_opportunity(payload())
    assert result["decision"] == "review"
    assert result["probability"] == 0.01
    assert result["action_gate"] == "owner review"


def test_agent_brief_contains_digest_and_gate() -> None:
    brief = create_action_brief(payload())
    assert "Decision: review" in brief
    assert "Action gate: owner review" in brief
    assert "Evidence digest:" in brief
