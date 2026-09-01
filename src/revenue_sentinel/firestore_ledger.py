from __future__ import annotations

import os
from typing import Any


class FirestoreLedger:
    """Append-only Cloud Firestore ledger used by the deployed Cloud Run service."""

    def __init__(self, collection: str | None = None) -> None:
        self._collection_name = collection or os.getenv("FIRESTORE_COLLECTION", "revenue_sentinel_audits")
        self._collection: Any | None = None

    def _get_collection(self) -> Any:
        if self._collection is None:
            from google.cloud import firestore

            client = firestore.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT") or None)
            self._collection = client.collection(self._collection_name)
        return self._collection

    def append(self, record: dict[str, Any]) -> dict[str, Any]:
        digest = str(record["evidence_digest"])
        document = self._get_collection().document(digest)
        document.set(record, merge=False)
        return {"record": record, "record_hash": digest, "previous_hash": "FIRESTORE_DOCUMENT_ID"}

    def list_records(self) -> list[dict[str, Any]]:
        return [snapshot.to_dict() for snapshot in self._get_collection().limit(100).stream()]
