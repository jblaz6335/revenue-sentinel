from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .service import OpportunityService


def load_fixture(path: str | Path) -> list[dict[str, Any]]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("fixture must contain a JSON array")
    return raw


def run_demo(path: str | Path) -> dict[str, Any]:
    results = OpportunityService().audit_many(load_fixture(path), persist=False)
    return {
        "summary": {
            "total": len(results),
            "ready": sum(item["decision"] == "ready" for item in results),
            "review": sum(item["decision"] == "review" for item in results),
            "table": sum(item["decision"] == "table" for item in results),
            "reject": sum(item["decision"] == "reject" for item in results),
            "expected_value_usd": round(sum(float(item["expected_value_usd"]) for item in results), 2),
        },
        "queue": results,
    }
