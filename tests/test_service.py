from __future__ import annotations

from datetime import UTC, datetime

from revenue_sentinel.demo import load_fixture, run_demo
from revenue_sentinel.engine import AuditEngine
from revenue_sentinel.ledger import MemoryLedger, verify_chain
from revenue_sentinel.service import OpportunityService

NOW = datetime(2026, 8, 22, 12, tzinfo=UTC)


def test_fixture_demo_has_all_decision_classes() -> None:
    result = run_demo("fixtures/opportunities.json")
    assert result["summary"]["total"] == 5
    assert result["summary"]["review"] >= 1
    assert result["summary"]["table"] == 1
    assert result["summary"]["reject"] >= 2


def test_fixture_loader_rejects_non_array(tmp_path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("{}")
    try:
        load_fixture(path)
    except ValueError as exc:
        assert "JSON array" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_service_persists_audits() -> None:
    ledger = MemoryLedger()
    service = OpportunityService(engine=AuditEngine(now=NOW), ledger=ledger)
    payload = load_fixture("fixtures/opportunities.json")[0]
    result = service.audit_one(payload)
    assert ledger.records[0]["record"]["evidence_digest"] == result["evidence_digest"]
    assert verify_chain(ledger.list_records())


def test_service_can_skip_persistence() -> None:
    ledger = MemoryLedger()
    service = OpportunityService(engine=AuditEngine(now=NOW), ledger=ledger)
    service.audit_many(load_fixture("fixtures/opportunities.json"), persist=False)
    assert ledger.list_records() == []


def test_service_returns_sorted_batch() -> None:
    service = OpportunityService(engine=AuditEngine(now=NOW), ledger=MemoryLedger())
    result = service.audit_many(load_fixture("fixtures/opportunities.json"), persist=False)
    ranks = {"ready": 0, "review": 1, "table": 2, "reject": 3}
    assert [ranks[item["decision"]] for item in result] == sorted(ranks[item["decision"]] for item in result)
