from __future__ import annotations

import hashlib
import json
from typing import Any

from .config import BusinessThresholds


def build_request_receipt(
    rows: list[dict[str, Any]],
    thresholds: BusinessThresholds,
    include_explanation: bool,
) -> dict[str, Any]:
    """Build a deterministic, non-persistent receipt for a validated analysis request.

    The receipt makes a retry traceable without claiming distributed idempotency:
    generated timestamps are deliberately excluded, while rows, effective guardrails
    and explanation mode remain part of the fingerprint.
    """
    canonical = {
        "rows": rows,
        "thresholds": thresholds.to_dict(),
        "include_explanation": include_explanation,
    }
    encoded = json.dumps(
        canonical,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    digest = hashlib.sha256(encoded).hexdigest()
    return {
        "request_fingerprint": f"sha256:{digest}",
        "idempotency_scope": "validated_rows_effective_guardrails_and_explanation_mode",
        "retry_safe": True,
        "generated_at_included": False,
        "persistence_executed": False,
        "deduplication_executed": False,
    }
