from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class Decision(StrEnum):
    READY = "ready"
    REVIEW = "review"
    TABLE = "table"
    REJECT = "reject"


class EvidenceState(StrEnum):
    VERIFIED = "verified"
    PARTIAL = "partial"
    UNVERIFIED = "unverified"


@dataclass(frozen=True, slots=True)
class Opportunity:
    opportunity_id: str
    title: str
    source_url: str
    channel: str
    potential_value_usd: float
    deadline_iso: str | None = None
    eligible: bool | None = None
    buyer_verified: bool | None = None
    payment_protected: bool | None = None
    budget_clear: bool = False
    scope_clear: bool = False
    public_evidence: tuple[str, ...] = ()
    external_actions: tuple[str, ...] = ()
    notes: str = ""

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Opportunity:
        data = dict(raw)
        data["public_evidence"] = tuple(data.get("public_evidence") or ())
        data["external_actions"] = tuple(data.get("external_actions") or ())
        return cls(**data)


@dataclass(frozen=True, slots=True)
class GateFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True, slots=True)
class AuditResult:
    opportunity_id: str
    decision: Decision
    evidence_state: EvidenceState
    risk_score: int
    probability: float
    expected_value_usd: float
    action_gate: str
    next_action: str
    findings: tuple[GateFinding, ...]
    evaluated_at: str
    evidence_digest: str
    score_components: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["decision"] = self.decision.value
        result["evidence_state"] = self.evidence_state.value
        return result


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()
