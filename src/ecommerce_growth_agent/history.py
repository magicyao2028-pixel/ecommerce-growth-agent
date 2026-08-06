from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class RetentionPolicy:
    max_records: int = 20
    retain_days: int = 90

    def __post_init__(self) -> None:
        if self.max_records < 1:
            raise ValueError("max_records must be at least 1")
        if self.retain_days < 1:
            raise ValueError("retain_days must be at least 1")


def fingerprint_rows(rows: Iterable[dict[str, Any]]) -> str:
    normalized = json.dumps(list(rows), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class AnalysisHistoryStore:
    """Persists safe analysis summaries while excluding source-row details."""

    def __init__(self, path: Path, policy: RetentionPolicy | None = None) -> None:
        self.path = path
        self.policy = policy or RetentionPolicy()

    def append(
        self,
        report: dict[str, Any],
        source_label: str,
        data_fingerprint: str,
        recorded_at: datetime | None = None,
    ) -> dict[str, Any]:
        now = recorded_at or datetime.now(timezone.utc)
        if now.tzinfo is None:
            raise ValueError("recorded_at must include timezone information")
        payload = self._load()
        cutoff = now - timedelta(days=self.policy.retain_days)
        retained = [
            item for item in payload["records"]
            if _parse_timestamp(item["recorded_at"]) >= cutoff
        ]
        removed_by_age = len(payload["records"]) - len(retained)

        finding_codes = sorted({str(item.get("code", "")) for item in report.get("findings", []) if item.get("code")})
        record = {
            "run_id": f"RUN-{now.strftime('%Y%m%dT%H%M%SZ')}-{data_fingerprint.split(':')[-1][:8]}",
            "recorded_at": now.astimezone(timezone.utc).isoformat(),
            "report_generated_at": report.get("generated_at"),
            "source_label": Path(source_label).name,
            "data_fingerprint": data_fingerprint,
            "summary": deepcopy(report.get("summary", {})),
            "finding_count": len(report.get("findings", [])),
            "finding_codes": finding_codes,
            "recommendation_count": len(report.get("recommendations", [])),
        }
        retained.append(record)
        removed_by_limit = max(0, len(retained) - self.policy.max_records)
        if removed_by_limit:
            retained = retained[-self.policy.max_records :]

        saved = {
            "schema_version": "1.0",
            "retention_policy": asdict(self.policy),
            "data_boundary": {
                "stored": ["portfolio summary", "finding codes", "counts", "source filename", "data fingerprint"],
                "excluded": ["source rows", "customer identifiers", "order-level details", "free-text notes"],
            },
            "records": retained,
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(saved, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return {
            "record": deepcopy(record),
            "retention": asdict(self.policy),
            "removed_by_age": removed_by_age,
            "removed_by_limit": removed_by_limit,
            "stored_records": len(retained),
        }

    def read(self) -> dict[str, Any]:
        return deepcopy(self._load())

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"records": []}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid analysis history JSON: {exc.msg}") from exc
        if not isinstance(payload, dict) or not isinstance(payload.get("records"), list):
            raise ValueError("Analysis history must contain a records list")
        for record in payload["records"]:
            if not isinstance(record, dict) or "recorded_at" not in record or "run_id" not in record:
                raise ValueError("Analysis history contains an invalid record")
            _parse_timestamp(record["recorded_at"])
        return payload


def _parse_timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("History timestamps must use ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ValueError("History timestamps must include timezone information")
    return parsed
