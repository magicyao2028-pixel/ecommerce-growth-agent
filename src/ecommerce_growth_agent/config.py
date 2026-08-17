from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class BusinessThresholds:
    """Review guardrails that can be adapted to one business context."""

    low_ctr: float = 0.02
    low_conversion_rate: float = 0.03
    low_ad_roi: float = 1.5
    stockout_cover_days: float = 7.0
    overstock_cover_days: float = 60.0

    def __post_init__(self) -> None:
        values = {
            field_name: getattr(self, field_name)
            for field_name in self.__dataclass_fields__
        }
        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            for value in values.values()
        ):
            raise ValueError("Threshold values must be finite numbers")
        for field_name in ("low_ctr", "low_conversion_rate"):
            value = getattr(self, field_name)
            if not 0 <= value <= 1:
                raise ValueError(f"{field_name} must be between 0 and 1")
        for field_name in ("low_ad_roi", "stockout_cover_days", "overstock_cover_days"):
            value = getattr(self, field_name)
            if value < 0:
                raise ValueError(f"{field_name} must not be negative")
        if self.stockout_cover_days >= self.overstock_cover_days:
            raise ValueError("stockout_cover_days must be lower than overstock_cover_days")

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "BusinessThresholds":
        allowed = set(cls.__dataclass_fields__)
        unknown = sorted(set(value).difference(allowed))
        if unknown:
            raise ValueError(f"Unknown threshold fields: {', '.join(unknown)}")
        if any(isinstance(item, bool) for item in value.values()):
            raise ValueError("Threshold values must be finite numbers")
        try:
            parsed = {key: float(item) for key, item in value.items()}
        except (TypeError, ValueError) as exc:
            raise ValueError("Threshold values must be numbers") from exc
        return cls(**parsed)

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


def load_thresholds(path: Path) -> BusinessThresholds:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid threshold JSON: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError("Threshold configuration must be a JSON object")
    return BusinessThresholds.from_mapping(payload)
