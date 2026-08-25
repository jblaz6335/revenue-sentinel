from __future__ import annotations

import json

from revenue_sentinel.ledger import JsonlLedger, MemoryLedger, verify_chain


def test_memory_ledger_builds_valid_chain() -> None:
    ledger = MemoryLedger()
    first = ledger.append({"id": 1})
    second = ledger.append({"id": 2})
    assert first["previous_hash"] == "GENESIS"
    assert second["previous_hash"] == first["record_hash"]
    assert verify_chain(ledger.list_records())


def test_chain_detects_record_tampering() -> None:
    ledger = MemoryLedger()
    ledger.append({"id": 1})
    records = ledger.list_records()
    records[0]["record"]["id"] = 99
    assert not verify_chain(records)


def test_chain_detects_hash_tampering() -> None:
    ledger = MemoryLedger()
    ledger.append({"id": 1})
    records = ledger.list_records()
    records[0]["record_hash"] = "bad"
    assert not verify_chain(records)


def test_jsonl_ledger_round_trip(tmp_path) -> None:
    ledger = JsonlLedger(tmp_path / "audit.jsonl")
    ledger.append({"id": "a"})
    ledger.append({"id": "b"})
    assert verify_chain(ledger.list_records())
    assert len((tmp_path / "audit.jsonl").read_text().splitlines()) == 2


def test_jsonl_is_machine_readable(tmp_path) -> None:
    ledger = JsonlLedger(tmp_path / "audit.jsonl")
    ledger.append({"nested": {"safe": True}})
    parsed = json.loads((tmp_path / "audit.jsonl").read_text())
    assert parsed["record"]["nested"]["safe"] is True
