from __future__ import annotations

from types import SimpleNamespace

from google.cloud import firestore

from revenue_sentinel.firestore_ledger import FirestoreLedger


def test_firestore_ledger_append_and_list(monkeypatch) -> None:
    writes: list[tuple[str, dict[str, object]]] = []
    client_calls: list[dict[str, object]] = []

    class Document:
        def __init__(self, digest: str) -> None:
            self.digest = digest

        def set(self, record: dict[str, object], **_: object) -> None:
            writes.append((self.digest, record))

    snapshots = [SimpleNamespace(to_dict=lambda: {"evidence_digest": "abc"})]

    class Collection:
        def document(self, digest: str) -> Document:
            return Document(digest)

        def limit(self, _: int) -> Collection:
            return self

        def stream(self) -> list[object]:
            return snapshots

    client = SimpleNamespace(collection=lambda _: Collection())

    def create_client(**kwargs: object) -> object:
        client_calls.append(kwargs)
        return client

    monkeypatch.setattr(firestore, "Client", create_client)

    ledger = FirestoreLedger(collection="audits")
    assert client_calls == []

    result = ledger.append({"evidence_digest": "abc", "decision": "ready"})

    assert len(client_calls) == 1
    assert writes[0][0] == "abc"
    assert result["record_hash"] == "abc"
    assert ledger.list_records() == [{"evidence_digest": "abc"}]
    assert len(client_calls) == 1
