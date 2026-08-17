from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class SalesRow:
    date: str
    sku: str
    product_name: str
    category: str
    impressions: int
    clicks: int
    orders: int
    units: int
    revenue: float
    ad_spend: float
    cost: float
    stock: int

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "SalesRow":
        required = {
            "date",
            "sku",
            "product_name",
            "category",
            "impressions",
            "clicks",
            "orders",
            "units",
            "revenue",
            "ad_spend",
            "cost",
            "stock",
        }
        missing = sorted(required.difference(value))
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        row = cls(
            date=str(value["date"]).strip(),
            sku=str(value["sku"]).strip(),
            product_name=str(value["product_name"]).strip(),
            category=str(value["category"]).strip(),
            impressions=_as_non_negative_int(value["impressions"], "impressions"),
            clicks=_as_non_negative_int(value["clicks"], "clicks"),
            orders=_as_non_negative_int(value["orders"], "orders"),
            units=_as_non_negative_int(value["units"], "units"),
            revenue=_as_non_negative_float(value["revenue"], "revenue"),
            ad_spend=_as_non_negative_float(value["ad_spend"], "ad_spend"),
            cost=_as_non_negative_float(value["cost"], "cost"),
            stock=_as_non_negative_int(value["stock"], "stock"),
        )
        if not row.date or not row.sku or not row.product_name:
            raise ValueError("date, sku and product_name must not be blank")
        if row.clicks > row.impressions:
            raise ValueError(f"clicks cannot exceed impressions for {row.sku}")
        if row.orders > row.clicks:
            raise ValueError(f"orders cannot exceed clicks for {row.sku}")
        return row

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _as_non_negative_int(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be an integer")
    if isinstance(value, int):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = int(value.strip())
        except ValueError as exc:
            raise ValueError(f"{field} must be an integer") from exc
    else:
        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{field} must be an integer") from exc
        if not math.isfinite(numeric) or not numeric.is_integer():
            raise ValueError(f"{field} must be an integer")
        parsed = int(numeric)
    if parsed < 0:
        raise ValueError(f"{field} must not be negative")
    return parsed


def _as_non_negative_float(value: Any, field: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be a finite number")
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be a number") from exc
    if not math.isfinite(parsed):
        raise ValueError(f"{field} must be a finite number")
    if parsed < 0:
        raise ValueError(f"{field} must not be negative")
    return parsed
