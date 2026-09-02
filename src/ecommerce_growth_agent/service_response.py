from __future__ import annotations

import re
from typing import Any


_FINGERPRINT = re.compile(r"^sha256:[0-9a-f]{64}$")


def validate_service_response(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate the response envelope consumed by a reviewer or UI adapter."""
    if not isinstance(payload, dict) or payload.get("schema_version") != "1.0" or payload.get("status") != "ok":
        raise ValueError("service response envelope is invalid")
    report = payload.get("report")
    receipt = payload.get("request_receipt")
    governance = payload.get("governance")
    if not isinstance(report, dict) or not isinstance(receipt, dict) or not isinstance(governance, dict):
        raise ValueError("service response is missing report, receipt or governance")
    fingerprint = str(receipt.get("request_fingerprint", ""))
    if not _FINGERPRINT.fullmatch(fingerprint):
        raise ValueError("service response fingerprint is invalid")
    if receipt.get("persistence_executed") is not False or receipt.get("deduplication_executed") is not False:
        raise ValueError("service response receipt must remain non-writing")
    if governance.get("persistence_executed") is not False or governance.get("external_action_executed") is not False or governance.get("human_approval_required") is not True:
        raise ValueError("service response governance is invalid")
    return {
        "schema_version": "1.0",
        "valid": True,
        "request_fingerprint": fingerprint,
        "human_approval_required": True,
        "persistence_executed": False,
        "external_action_executed": False,
        "boundary": "Envelope validation proves shape and no-write declarations; it does not authenticate callers or authorize production actions.",
    }
