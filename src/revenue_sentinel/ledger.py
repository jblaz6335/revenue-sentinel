from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


class Ledger(Protocol):
    def append(self, record: dict[str, Any]) -> dict[str, Any]: ...

    def list_records(self) -> list[dict[str, Any]]: ...


@dataclass(slots=True)
class MemoryLedger:
    records: list[dict[str, Any]]

    def __init__(self) -> None:
        self.records = []

    def append(self, record: dict[str, Any]) -> dict[str, Any]:
        chained = _chain_record(record, self.records[-1]["record_hash"] if self.records else "GENESIS")
        self.records.append(chained)
        return dict(chained)

    def list_records(self) -> list[dict[str, Any]]:
        return [dict(item) for item in self.records]


@dataclass(slots=True)
class JsonlLedger:
    path: Path

    def append(self, record: dict[str, Any]) -> dict[str, Any]:
        records = self.list_records()
        chained = _chain_record(record, records[-1]["record_hash"] if records else "GENESIS")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(chained, sort_keys=True) + "\n")
        return chained

    def list_records(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return [
            json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()
        ]


def _chain_record(record: dict[str, Any], previous_hash: str) -> dict[str, Any]:
    body = {"previous_hash": previous_hash, "record": record}
    record_hash = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {**body, "record_hash": record_hash}


def verify_chain(records: list[dict[str, Any]]) -> bool:
    previous = "GENESIS"
    for item in records:
        if item.get("previous_hash") != previous:
            return False
        body = {"previous_hash": previous, "record": item.get("record")}
        expected = hashlib.sha256(
            json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        if item.get("record_hash") != expected:
            return False
        previous = expected
    return True
