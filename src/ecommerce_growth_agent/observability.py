from __future__ import annotations

import math
from typing import Any, Iterable


OBSERVABILITY_VERSION = "0.9"
_STATUSES = {"success", "error"}


def _finite_nonnegative(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a finite non-negative number")
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise ValueError(f"{field} must be a finite non-negative number")
    return number


def summarize_request_observability(events: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Summarize caller-supplied request telemetry without storing or emitting it.

    The function is intentionally a pure reducer: it accepts already-redacted
    fields, computes review metrics, and makes no monitoring or alerting calls.
    """
    if isinstance(events, (str, bytes, dict)):
        raise ValueError("observability events must be a non-empty list")
    normalized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for event in events:
        if not isinstance(event, dict):
            raise ValueError("each observability event must be an object")
        request_id = event.get("request_id")
        if not isinstance(request_id, str) or not request_id.strip():
            raise ValueError("request_id must be a non-empty string")
        if request_id in seen_ids:
            raise ValueError("request_id values must be unique")
        seen_ids.add(request_id)
        status = event.get("status")
        if status not in _STATUSES:
            raise ValueError("status must be success or error")
        latency_ms = _finite_nonnegative(event.get("latency_ms"), "latency_ms")
        error_code = event.get("error_code")
        if status == "error":
            if not isinstance(error_code, str) or not error_code.strip():
                raise ValueError("error events require a non-empty error_code")
        elif error_code not in (None, ""):
            raise ValueError("success events cannot carry an error_code")
        normalized.append({"request_id": request_id, "status": status, "latency_ms": latency_ms})

    if not normalized:
        raise ValueError("observability events must be a non-empty list")

    latencies = sorted(item["latency_ms"] for item in normalized)
    count = len(normalized)
    success_count = sum(item["status"] == "success" for item in normalized)
    error_count = count - success_count
    # Nearest-rank p95 keeps the result deterministic for small reviewer fixtures.
    p95_index = max(0, math.ceil(0.95 * count) - 1)
    return {
        "observability_version": OBSERVABILITY_VERSION,
        "request_count": count,
        "success_count": success_count,
        "error_count": error_count,
        "error_rate": round(error_count / count, 4),
        "latency_ms": {
            "min": round(latencies[0], 3),
            "max": round(latencies[-1], 3),
            "avg": round(sum(latencies) / count, 3),
            "p95": round(latencies[p95_index], 3),
        },
        "source": "caller_supplied_redacted_events",
        "review_only": True,
        "persistence_executed": False,
        "external_action_executed": False,
        "monitoring_service_called": False,
        "boundary": "Telemetry is summarized for local review only; no alert, dashboard, or production SLO claim is made.",
    }


__all__ = ["OBSERVABILITY_VERSION", "summarize_request_observability"]
