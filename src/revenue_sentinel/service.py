from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .engine import AuditEngine
from .ledger import JsonlLedger, Ledger, MemoryLedger
from .models import Opportunity


class OpportunityService:
    def __init__(self, *, engine: AuditEngine | None = None, ledger: Ledger | None = None) -> None:
        self.engine = engine or AuditEngine()
        self.ledger = ledger or _default_ledger()

    def audit_one(self, payload: dict[str, Any], *, persist: bool = True) -> dict[str, Any]:
        result = self.engine.audit(Opportunity.from_dict(payload)).to_dict()
        if persist:
            self.ledger.append(result)
        return result

    def audit_many(self, payloads: list[dict[str, Any]], *, persist: bool = True) -> list[dict[str, Any]]:
        results = self.engine.audit_many(Opportunity.from_dict(item) for item in payloads)
        rendered = [item.to_dict() for item in results]
        if persist:
            for item in rendered:
                self.ledger.append(item)
        return rendered


def _default_ledger() -> Ledger:
    mode = os.getenv("REVENUE_SENTINEL_LEDGER", "memory").lower()
    if mode == "firestore":
        from .firestore_ledger import FirestoreLedger

        return FirestoreLedger()
    if mode == "jsonl":
        return JsonlLedger(Path(os.getenv("REVENUE_SENTINEL_LEDGER_PATH", "runtime/audits.jsonl")))
    return MemoryLedger()
