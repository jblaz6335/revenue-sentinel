from __future__ import annotations

from datetime import UTC, datetime

import pytest

from revenue_sentinel.engine import AuditEngine, audit_payload
from revenue_sentinel.models import Decision, EvidenceState, Opportunity

NOW = datetime(2026, 8, 22, 12, tzinfo=UTC)


def make_opportunity(**overrides: object) -> Opportunity:
    payload = {
        "opportunity_id": "x1",
        "title": "Verified route",
        "source_url": "https://example.com/open",
        "channel": "Contract",
        "potential_value_usd": 1000,
        "deadline_iso": "2026-09-01T00:00:00Z",
        "eligible": True,
        "buyer_verified": True,
        "payment_protected": True,
        "budget_clear": True,
        "scope_clear": True,
        "public_evidence": ("https://example.com/open", "https://example.com/rules"),
        "external_actions": (),
    }
    payload.update(overrides)
    return Opportunity(**payload)


def test_verified_safe_route_is_ready() -> None:
    result = AuditEngine(now=NOW).audit(make_opportunity())
    assert result.decision is Decision.READY
    assert result.evidence_state is EvidenceState.VERIFIED
    assert result.risk_score == 0
    assert result.probability == 0.15
    assert result.expected_value_usd == 150


@pytest.mark.parametrize(
    ("overrides", "code"),
    [
        ({"source_url": "http://example.com"}, "source.invalid"),
        ({"deadline_iso": "2026-01-01T00:00:00Z"}, "deadline.closed"),
        ({"eligible": False}, "eligibility.failed"),
    ],
)
def test_hard_gates_reject(overrides: dict[str, object], code: str) -> None:
    result = AuditEngine(now=NOW).audit(make_opportunity(**overrides))
    assert result.decision is Decision.REJECT
    assert result.probability == 0
    assert any(item.code == code for item in result.findings)


def test_dust_value_is_tabled() -> None:
    result = AuditEngine(now=NOW).audit(make_opportunity(potential_value_usd=0.00016))
    assert result.decision is Decision.TABLE
    assert result.next_action.startswith("Deprioritize")


def test_missing_evidence_routes_to_review() -> None:
    result = AuditEngine(now=NOW).audit(make_opportunity(public_evidence=()))
    assert result.decision is Decision.REVIEW
    assert result.evidence_state is EvidenceState.UNVERIFIED
    assert result.action_gate == "owner review"


def test_unknown_eligibility_is_visible() -> None:
    result = AuditEngine(now=NOW).audit(make_opportunity(eligible=None))
    assert any(item.code == "eligibility.unknown" for item in result.findings)
    assert result.decision is Decision.REVIEW


def test_invalid_deadline_is_not_silently_accepted() -> None:
    result = AuditEngine(now=NOW).audit(make_opportunity(deadline_iso="yesterday-ish"))
    assert any(item.code == "deadline.invalid" for item in result.findings)
    assert result.decision is Decision.REVIEW


def test_digest_is_deterministic() -> None:
    engine = AuditEngine(now=NOW)
    first = engine.audit(make_opportunity())
    second = engine.audit(make_opportunity())
    assert first.evidence_digest == second.evidence_digest


def test_digest_changes_with_material_input() -> None:
    engine = AuditEngine(now=NOW)
    first = engine.audit(make_opportunity())
    second = engine.audit(make_opportunity(potential_value_usd=1001))
    assert first.evidence_digest != second.evidence_digest


def test_sort_places_ready_before_review_table_and_reject() -> None:
    queue = AuditEngine(now=NOW).audit_many(
        [
            make_opportunity(opportunity_id="reject", eligible=False),
            make_opportunity(opportunity_id="table", potential_value_usd=0.2),
            make_opportunity(opportunity_id="review", eligible=None),
            make_opportunity(opportunity_id="ready"),
        ]
    )
    assert [item.decision for item in queue] == [
        Decision.READY,
        Decision.REVIEW,
        Decision.TABLE,
        Decision.REJECT,
    ]


def test_external_actions_create_owner_approval_gate() -> None:
    result = AuditEngine(now=NOW).audit(make_opportunity(external_actions=("submit",)))
    assert result.decision is Decision.READY
    assert result.action_gate == "owner approval"


def test_negative_value_is_clamped_for_expected_value() -> None:
    result = AuditEngine(now=NOW).audit(make_opportunity(potential_value_usd=-5))
    assert result.expected_value_usd == 0


@pytest.mark.parametrize(
    ("channel", "cap"),
    [("Hackathon", 0.01), ("Employment", 0.05), ("Digital Product", 0.08), ("Contract", 0.15)],
)
def test_channel_probability_caps(channel: str, cap: float) -> None:
    result = AuditEngine(now=NOW).audit(make_opportunity(channel=channel, potential_value_usd=50_000))
    assert result.probability <= cap


def test_dict_adapter_returns_json_friendly_enums() -> None:
    payload = (
        make_opportunity().__dict__
        if hasattr(make_opportunity(), "__dict__")
        else {
            "opportunity_id": "x1",
            "title": "Verified route",
            "source_url": "https://example.com/open",
            "channel": "Contract",
            "potential_value_usd": 1000,
            "deadline_iso": "2026-09-01T00:00:00Z",
            "eligible": True,
            "buyer_verified": True,
            "payment_protected": True,
            "budget_clear": True,
            "scope_clear": True,
            "public_evidence": ["a", "b"],
            "external_actions": [],
        }
    )
    result = audit_payload(payload, now=NOW)
    assert result["decision"] == "ready"
    assert result["evidence_state"] == "verified"
