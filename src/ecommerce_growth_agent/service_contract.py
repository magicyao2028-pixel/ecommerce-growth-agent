from __future__ import annotations

from typing import Any

from .agent import GrowthAgent
from .config import BusinessThresholds
from .explanation import explain_report
from .request_receipt import build_request_receipt


SERVICE_SCHEMA_VERSION = "1.0"


def analyze_request(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate a service request and return an offline, non-writing response."""
    if not isinstance(payload, dict):
        raise ValueError("service request must be an object")
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("service request rows must be a non-empty list")
    generated_at = payload.get("generated_at")
    if generated_at is not None and not isinstance(generated_at, str):
        raise ValueError("generated_at must be a string or null")
    raw_thresholds = payload.get("thresholds")
    thresholds = None
    if raw_thresholds is not None:
        if not isinstance(raw_thresholds, dict):
            raise ValueError("thresholds must be an object")
        thresholds = BusinessThresholds.from_mapping(raw_thresholds)
    report = GrowthAgent(thresholds).run(rows, generated_at=generated_at)
    if payload.get("include_explanation") is True:
        report["explanation"] = explain_report(report)
    elif payload.get("include_explanation") not in (None, False):
        raise ValueError("include_explanation must be boolean")
    return {
        "schema_version": SERVICE_SCHEMA_VERSION,
        "status": "ok",
        "request_receipt": build_request_receipt(
            rows,
            thresholds or BusinessThresholds(),
            payload.get("include_explanation") is True,
        ),
        "report": report,
        "governance": {
            "authentication_required": True,
            "persistence_executed": False,
            "external_action_executed": False,
            "human_approval_required": True,
        },
    }
