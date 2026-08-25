from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from datetime import UTC, datetime
from urllib.parse import urlparse

from .models import (
    AuditResult,
    Decision,
    EvidenceState,
    GateFinding,
    Opportunity,
)


class AuditEngine:
    """Deterministic gate before an LLM recommends external action."""

    def __init__(self, *, now: datetime | None = None) -> None:
        self._now = (now or datetime.now(UTC)).astimezone(UTC)

    def audit(self, opportunity: Opportunity) -> AuditResult:
        findings: list[GateFinding] = []
        hard_reject = False

        parsed = urlparse(opportunity.source_url)
        if parsed.scheme != "https" or not parsed.netloc:
            findings.append(GateFinding("source.invalid", "high", "A canonical HTTPS source is required."))
            hard_reject = True

        deadline = self._parse_deadline(opportunity.deadline_iso, findings)
        if deadline and deadline < self._now:
            findings.append(GateFinding("deadline.closed", "high", "The opportunity deadline has passed."))
            hard_reject = True

        if opportunity.eligible is False:
            findings.append(GateFinding("eligibility.failed", "high", "The entrant is not eligible."))
            hard_reject = True
        elif opportunity.eligible is None:
            findings.append(
                GateFinding("eligibility.unknown", "medium", "Eligibility requires owner verification.")
            )

        evidence_state = self._evidence_state(opportunity)
        if evidence_state is EvidenceState.UNVERIFIED:
            findings.append(
                GateFinding("evidence.missing", "high", "No independent public evidence was captured.")
            )
        elif evidence_state is EvidenceState.PARTIAL:
            findings.append(
                GateFinding(
                    "evidence.partial", "medium", "The source is captured but key facts remain unverified."
                )
            )

        if opportunity.buyer_verified is False:
            findings.append(
                GateFinding("buyer.unverified", "medium", "Buyer or sponsor verification is absent.")
            )
        if opportunity.payment_protected is False:
            findings.append(GateFinding("payment.unprotected", "high", "Payment protection is absent."))
        if not opportunity.budget_clear:
            findings.append(GateFinding("budget.unclear", "medium", "The authoritative budget is unclear."))
        if not opportunity.scope_clear:
            findings.append(GateFinding("scope.unclear", "medium", "The deliverable boundary is unclear."))

        risk_score = self._risk_score(findings)
        probability = self._probability(opportunity, evidence_state, risk_score, hard_reject)
        expected_value = round(max(opportunity.potential_value_usd, 0.0) * probability, 6)
        decision = self._decision(opportunity, evidence_state, risk_score, hard_reject)
        action_gate, next_action = self._action(opportunity, decision, findings)
        evaluated_at = self._now.replace(microsecond=0).isoformat()

        payload = {
            "opportunity": self._canonical_opportunity(opportunity),
            "decision": decision.value,
            "evidence_state": evidence_state.value,
            "risk_score": risk_score,
            "probability": probability,
            "expected_value_usd": expected_value,
            "action_gate": action_gate,
            "next_action": next_action,
            "findings": [
                f.__dict__
                if hasattr(f, "__dict__")
                else {"code": f.code, "severity": f.severity, "message": f.message}
                for f in findings
            ],
            "evaluated_at": evaluated_at,
        }
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

        return AuditResult(
            opportunity_id=opportunity.opportunity_id,
            decision=decision,
            evidence_state=evidence_state,
            risk_score=risk_score,
            probability=probability,
            expected_value_usd=expected_value,
            action_gate=action_gate,
            next_action=next_action,
            findings=tuple(findings),
            evaluated_at=evaluated_at,
            evidence_digest=digest,
            score_components={
                "value": round(min(max(opportunity.potential_value_usd, 0.0) / 50000, 1), 3),
                "evidence": 1.0
                if evidence_state is EvidenceState.VERIFIED
                else 0.5
                if evidence_state is EvidenceState.PARTIAL
                else 0.0,
                "risk_inverse": round((100 - risk_score) / 100, 3),
            },
        )

    def audit_many(self, opportunities: Iterable[Opportunity]) -> list[AuditResult]:
        return sorted(
            (self.audit(item) for item in opportunities),
            key=lambda item: (
                {Decision.READY: 0, Decision.REVIEW: 1, Decision.TABLE: 2, Decision.REJECT: 3}[item.decision],
                -item.expected_value_usd,
                item.risk_score,
                item.opportunity_id,
            ),
        )

    def _parse_deadline(self, value: str | None, findings: list[GateFinding]) -> datetime | None:
        if not value:
            findings.append(GateFinding("deadline.unknown", "medium", "The deadline is not recorded."))
            return None
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=UTC)
            return parsed.astimezone(UTC)
        except ValueError:
            findings.append(GateFinding("deadline.invalid", "high", "The deadline is not valid ISO-8601."))
            return None

    @staticmethod
    def _evidence_state(opportunity: Opportunity) -> EvidenceState:
        count = len(tuple(item for item in opportunity.public_evidence if item.strip()))
        if count >= 2 and opportunity.budget_clear and opportunity.deadline_iso:
            return EvidenceState.VERIFIED
        if count >= 1:
            return EvidenceState.PARTIAL
        return EvidenceState.UNVERIFIED

    @staticmethod
    def _risk_score(findings: list[GateFinding]) -> int:
        weights = {"high": 24, "medium": 11, "low": 4}
        return min(sum(weights.get(item.severity, 0) for item in findings), 100)

    @staticmethod
    def _probability(
        opportunity: Opportunity,
        evidence_state: EvidenceState,
        risk_score: int,
        hard_reject: bool,
    ) -> float:
        if hard_reject or opportunity.potential_value_usd <= 0:
            return 0.0
        base = 0.08
        base += (
            0.04
            if evidence_state is EvidenceState.VERIFIED
            else 0.01
            if evidence_state is EvidenceState.PARTIAL
            else -0.04
        )
        base += 0.03 if opportunity.scope_clear else -0.02
        base += (
            0.02
            if opportunity.payment_protected is True
            else -0.02
            if opportunity.payment_protected is False
            else 0
        )
        base += (
            0.01
            if opportunity.buyer_verified is True
            else -0.01
            if opportunity.buyer_verified is False
            else 0
        )
        base -= risk_score / 1000
        return round(min(max(base, 0.01), AuditEngine._channel_cap(opportunity.channel)), 3)

    @staticmethod
    def _channel_cap(channel: str) -> float:
        normalized = channel.strip().lower()
        if normalized in {"hackathon", "contest", "competition", "bounty"}:
            return 0.01
        if normalized in {"employment", "job"}:
            return 0.05
        if normalized in {"digital product", "digital products", "product"}:
            return 0.08
        if normalized in {"contract", "freelance", "freelancer"}:
            return 0.15
        return 0.10

    @staticmethod
    def _decision(
        opportunity: Opportunity,
        evidence_state: EvidenceState,
        risk_score: int,
        hard_reject: bool,
    ) -> Decision:
        if hard_reject:
            return Decision.REJECT
        if opportunity.potential_value_usd < 1:
            return Decision.TABLE
        if opportunity.eligible is not True:
            return Decision.REVIEW
        if evidence_state is EvidenceState.VERIFIED and risk_score <= 22 and opportunity.scope_clear:
            return Decision.READY
        return Decision.REVIEW

    @staticmethod
    def _action(
        opportunity: Opportunity,
        decision: Decision,
        findings: list[GateFinding],
    ) -> tuple[str, str]:
        if decision is Decision.REJECT:
            return "none", "Archive with the rejection evidence; do not pursue."
        if decision is Decision.TABLE:
            return "none", "Deprioritize until compensation becomes economically meaningful."
        if findings:
            codes = ", ".join(item.code for item in findings[:3])
            return "owner review", f"Resolve evidence gates ({codes}) before any external action."
        if opportunity.external_actions:
            actions = ", ".join(opportunity.external_actions)
            return "owner approval", f"Review the prepared action packet before: {actions}."
        return "none", "Proceed with local preparation; no external mutation is required."

    @staticmethod
    def _canonical_opportunity(opportunity: Opportunity) -> dict[str, object]:
        return {
            "opportunity_id": opportunity.opportunity_id,
            "title": opportunity.title,
            "source_url": opportunity.source_url,
            "channel": opportunity.channel,
            "potential_value_usd": round(opportunity.potential_value_usd, 6),
            "deadline_iso": opportunity.deadline_iso,
            "eligible": opportunity.eligible,
            "buyer_verified": opportunity.buyer_verified,
            "payment_protected": opportunity.payment_protected,
            "budget_clear": opportunity.budget_clear,
            "scope_clear": opportunity.scope_clear,
            "public_evidence": sorted(opportunity.public_evidence),
            "external_actions": sorted(opportunity.external_actions),
            "notes": opportunity.notes,
        }


def audit_payload(payload: dict[str, object], *, now: datetime | None = None) -> dict[str, object]:
    return AuditEngine(now=now).audit(Opportunity.from_dict(payload)).to_dict()


def build_evidence_brief(payload: dict[str, object]) -> str:
    result = AuditEngine().audit(Opportunity.from_dict(payload))
    lines = [
        f"# Opportunity {result.opportunity_id}",
        f"Decision: {result.decision.value}",
        f"Evidence: {result.evidence_state.value}",
        f"Expected value: USD {result.expected_value_usd:,.2f}",
        f"Risk score: {result.risk_score}/100",
        f"Action gate: {result.action_gate}",
        f"Next action: {result.next_action}",
        "Findings:",
    ]
    lines.extend(f"- [{item.severity}] {item.code}: {item.message}" for item in result.findings)
    lines.append(f"Evidence digest: {result.evidence_digest}")
    return "\n".join(lines)
