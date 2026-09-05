from __future__ import annotations

from collections import Counter
from datetime import date
from typing import Any

from .service_response import validate_service_response


_STATUSES = {"accepted", "pending", "rejected"}


def audit_response_review_feedback(
    response: dict[str, Any], feedback_batch: list[dict[str, Any]]
) -> dict[str, Any]:
    """Audit reviewer feedback against one response envelope without applying it."""
    envelope = validate_service_response(response)
    if not isinstance(feedback_batch, list) or not feedback_batch:
        raise ValueError("response review feedback must be a non-empty list")
    fingerprint = envelope["request_fingerprint"]
    seen: set[str] = set()
    statuses: Counter[str] = Counter()
    accepted: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    dates: list[date] = []
    for record in feedback_batch:
        if not isinstance(record, dict):
            raise ValueError("each response review record must be an object")
        required = {"feedback_id", "request_fingerprint", "recorded_on", "status", "summary", "applied"}
        if required.difference(record):
            raise ValueError("response review record is incomplete")
        feedback_id = str(record["feedback_id"]).strip()
        if not feedback_id or feedback_id in seen:
            raise ValueError("response review feedback IDs must be unique")
        seen.add(feedback_id)
        if str(record["request_fingerprint"]) != fingerprint:
            raise ValueError("response review fingerprint does not match envelope")
        try:
            recorded_on = date.fromisoformat(str(record["recorded_on"]))
        except ValueError as exc:
            raise ValueError("response review recorded_on must be ISO format") from exc
        if dates and recorded_on < dates[-1]:
            raise ValueError("response review dates must be chronological")
        dates.append(recorded_on)
        status = str(record["status"]).strip()
        if status not in _STATUSES or not str(record["summary"]).strip():
            raise ValueError("response review status or summary is invalid")
        if record["applied"] is not False:
            raise ValueError("response review cannot apply changes")
        item = {"feedback_id": feedback_id, "status": status, "passed": True}
        statuses[status] += 1
        (accepted if status == "accepted" else excluded).append(item)
    return {
        "schema_version": "1.0",
        "request_fingerprint": fingerprint,
        "record_count": len(feedback_batch),
        "status_counts": dict(sorted(statuses.items())),
        "accepted_count": len(accepted),
        "excluded_count": len(excluded),
        "accepted": accepted,
        "excluded": excluded,
        "persistence_executed": False,
        "external_action_executed": False,
        "boundary": "Reviewer feedback is audited against one response envelope; it does not modify reports, stores or external systems.",
    }


__all__ = ["audit_response_review_feedback"]
