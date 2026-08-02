from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import date
from typing import Iterable

from .config import BusinessThresholds
from .domain import SalesRow


def safe_ratio(numerator: float, denominator: float) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


@dataclass(frozen=True)
class Finding:
    sku: str
    product_name: str
    severity: str
    code: str
    evidence: str
    recommended_action: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def compute_portfolio_metrics(rows: Iterable[SalesRow]) -> dict[str, float | int]:
    items = list(rows)
    impressions = sum(row.impressions for row in items)
    clicks = sum(row.clicks for row in items)
    orders = sum(row.orders for row in items)
    units = sum(row.units for row in items)
    revenue = round(sum(row.revenue for row in items), 2)
    ad_spend = round(sum(row.ad_spend for row in items), 2)
    cost = round(sum(row.cost for row in items), 2)
    contribution_profit = round(revenue - ad_spend - cost, 2)

    return {
        "row_count": len(items),
        "sku_count": len({row.sku for row in items}),
        "gmv": revenue,
        "orders": orders,
        "units": units,
        "ctr": safe_ratio(clicks, impressions),
        "conversion_rate": safe_ratio(orders, clicks),
        "ad_roi": round(revenue / ad_spend, 2) if ad_spend else 0.0,
        "contribution_profit": contribution_profit,
        "contribution_margin": safe_ratio(contribution_profit, revenue),
    }


def aggregate_by_sku(rows: Iterable[SalesRow]) -> list[dict[str, float | int | str]]:
    groups: dict[str, list[SalesRow]] = defaultdict(list)
    for row in rows:
        groups[row.sku].append(row)

    result: list[dict[str, float | int | str]] = []
    for sku, items in groups.items():
        impressions = sum(row.impressions for row in items)
        clicks = sum(row.clicks for row in items)
        orders = sum(row.orders for row in items)
        units = sum(row.units for row in items)
        revenue = round(sum(row.revenue for row in items), 2)
        ad_spend = round(sum(row.ad_spend for row in items), 2)
        cost = round(sum(row.cost for row in items), 2)
        active_days = max(1, len({row.date for row in items}))
        daily_units = units / active_days
        stock = items[-1].stock
        stock_cover_days = round(stock / daily_units, 1) if daily_units else 999.0
        contribution_profit = round(revenue - ad_spend - cost, 2)

        result.append(
            {
                "sku": sku,
                "product_name": items[0].product_name,
                "category": items[0].category,
                "impressions": impressions,
                "clicks": clicks,
                "orders": orders,
                "units": units,
                "revenue": revenue,
                "ad_spend": ad_spend,
                "ctr": safe_ratio(clicks, impressions),
                "conversion_rate": safe_ratio(orders, clicks),
                "ad_roi": round(revenue / ad_spend, 2) if ad_spend else 0.0,
                "contribution_profit": contribution_profit,
                "stock": stock,
                "stock_cover_days": stock_cover_days,
            }
        )
    return sorted(result, key=lambda item: float(item["revenue"]), reverse=True)


def diagnose_skus(
    sku_metrics: Iterable[dict[str, float | int | str]],
    thresholds: BusinessThresholds | None = None,
) -> list[Finding]:
    guardrails = thresholds or BusinessThresholds()
    findings: list[Finding] = []
    for item in sku_metrics:
        sku = str(item["sku"])
        name = str(item["product_name"])
        ctr = float(item["ctr"])
        conversion = float(item["conversion_rate"])
        roi = float(item["ad_roi"])
        profit = float(item["contribution_profit"])
        cover = float(item["stock_cover_days"])

        if ctr < guardrails.low_ctr:
            findings.append(
                Finding(
                    sku,
                    name,
                    "medium",
                    "LOW_CTR",
                    f"CTR is {ctr:.1%}, below the {guardrails.low_ctr:.1%} review threshold.",
                    "Review creative, title and audience targeting before increasing traffic spend.",
                )
            )
        if conversion < guardrails.low_conversion_rate:
            findings.append(
                Finding(
                    sku,
                    name,
                    "high",
                    "LOW_CONVERSION",
                    f"Click-to-order conversion is {conversion:.1%}, below the {guardrails.low_conversion_rate:.1%} threshold.",
                    "Audit product page, price, reviews, offer and checkout friction.",
                )
            )
        if roi and roi < guardrails.low_ad_roi:
            findings.append(
                Finding(
                    sku,
                    name,
                    "high",
                    "LOW_AD_ROI",
                    f"Advertising ROI is {roi:.2f}, below the {guardrails.low_ad_roi:.2f} guardrail.",
                    "Reduce or pause low-performing spend after human review; test a new audience or creative.",
                )
            )
        if profit < 0:
            findings.append(
                Finding(
                    sku,
                    name,
                    "critical",
                    "NEGATIVE_CONTRIBUTION",
                    f"Contribution profit is {profit:.2f} after product and advertising cost.",
                    "Check pricing, discount, sourcing cost and paid traffic before accepting more volume.",
                )
            )
        if cover < guardrails.stockout_cover_days:
            findings.append(
                Finding(
                    sku,
                    name,
                    "high",
                    "STOCKOUT_RISK",
                    f"Estimated stock cover is {cover:.1f} days.",
                    "Confirm demand forecast and replenishment lead time; prepare a controlled reorder.",
                )
            )
        elif cover > guardrails.overstock_cover_days and cover < 999:
            findings.append(
                Finding(
                    sku,
                    name,
                    "medium",
                    "OVERSTOCK_RISK",
                    f"Estimated stock cover is {cover:.1f} days.",
                    "Slow procurement and test a bundle, content or promotion plan without destroying margin.",
                )
            )

    priority = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    return sorted(findings, key=lambda finding: (priority[finding.severity], finding.sku, finding.code))


def build_recommendations(findings: Iterable[Finding]) -> list[dict[str, str | int]]:
    recommendations: list[dict[str, str | int]] = []
    for rank, finding in enumerate(findings, start=1):
        recommendations.append(
            {
                "priority": rank,
                "owner": _owner_for(finding.code),
                "sku": finding.sku,
                "action": finding.recommended_action,
                "reason": finding.evidence,
                "approval": "Human approval required before any external action.",
            }
        )
    return recommendations


def data_freshness(rows: Iterable[SalesRow]) -> str:
    dates: list[date] = []
    for row in rows:
        try:
            dates.append(date.fromisoformat(row.date))
        except ValueError:
            return "Unknown: one or more dates are not ISO-8601 values."
    if not dates:
        return "Unknown: no rows provided."
    return f"Dataset range: {min(dates).isoformat()} to {max(dates).isoformat()}."


def _owner_for(code: str) -> str:
    if code in {"LOW_CTR", "LOW_AD_ROI"}:
        return "Growth / Advertising"
    if code == "LOW_CONVERSION":
        return "Product Operations"
    if code in {"STOCKOUT_RISK", "OVERSTOCK_RISK"}:
        return "Supply Chain"
    return "Business Owner"
