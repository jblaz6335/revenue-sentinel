from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from app import runtime


class FakeSessionService:
    async def create_session(self, **_: object) -> object:
        return object()


class FakeEvent:
    content = SimpleNamespace(parts=[SimpleNamespace(text="Decision: ready")])

    def get_function_calls(self) -> list[object]:
        return [SimpleNamespace(name="audit_opportunity")]

    def is_final_response(self) -> bool:
        return True


class FakeRunner:
    def __init__(self, **_: object) -> None:
        pass

    async def run_async(self, **_: object):
        yield FakeEvent()


def test_audit_with_agent_returns_tool_trace(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(runtime, "InMemorySessionService", FakeSessionService)
    monkeypatch.setattr(runtime, "Runner", FakeRunner)
    monkeypatch.setattr(runtime, "_consume_cloud_quota", lambda: None)
    result = asyncio.run(runtime.audit_with_agent({"title": "Synthetic"}))
    assert result["tool_calls"] == ["audit_opportunity"]
    assert result["response"] == "Decision: ready"


def test_memory_mode_skips_cloud_quota(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REVENUE_SENTINEL_LEDGER", "memory")
    runtime._consume_cloud_quota()


def test_cloud_quota_increments_and_rejects_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    from google.cloud import firestore

    class Snapshot:
        def __init__(self, count: int | None) -> None:
            self.exists = count is not None
            self.count = count

        def get(self, _: str) -> int:
            assert self.count is not None
            return self.count

    class Reference:
        def __init__(self) -> None:
            self.snapshot = Snapshot(None)

        def get(self, **_: object) -> Snapshot:
            return self.snapshot

    reference = Reference()

    class Collection:
        def document(self, _: str) -> Reference:
            return reference

    class Transaction:
        def __init__(self) -> None:
            self.writes: list[dict[str, object]] = []

        def set(self, _: object, value: dict[str, object], **__: object) -> None:
            self.writes.append(value)

    transaction = Transaction()
    client = SimpleNamespace(collection=lambda _: Collection(), transaction=lambda: transaction)
    monkeypatch.setenv("REVENUE_SENTINEL_LEDGER", "firestore")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-project")
    monkeypatch.setattr(firestore, "Client", lambda **_: client)
    monkeypatch.setattr(firestore, "transactional", lambda function: function)

    runtime._consume_cloud_quota(limit=1)
    assert transaction.writes[0]["count"] == 1

    reference.snapshot = Snapshot(1)
    with pytest.raises(runtime.AgentQuotaExceeded):
        runtime._consume_cloud_quota(limit=1)
