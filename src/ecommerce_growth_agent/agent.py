from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable

from .domain import SalesRow
from .tools import (
    aggregate_by_sku,
    build_recommendations,
    compute_portfolio_metrics,
    data_freshness,
    diagnose_skus,
)


@dataclass
class AgentTrace:
    steps: list[dict[str, str]] = field(default_factory=list)

    def record(self, tool: str, purpose: str, status: str = "completed") -> None:
        self.steps.append({"tool": tool, "purpose": purpose, "status": status})


class GrowthAgent:
    """Orchestrates transparent analysis tools without a paid model dependency."""

    def run(self, values: Iterable[SalesRow | dict[str, Any]]) -> dict[str, Any]:
        trace = AgentTrace()
        rows = [value if isinstance(value, SalesRow) else SalesRow.from_mapping(value) for value in values]
        if not rows:
            raise ValueError("At least one sales row is required")
        trace.record("validate_input", "Validate schema, values and basic business invariants.")

        summary = compute_portfolio_metrics(rows)
        trace.record("compute_portfolio_metrics", "Calculate portfolio KPIs from source rows.")

        sku_metrics = aggregate_by_sku(rows)
        trace.record("aggregate_by_sku", "Aggregate traffic, sales, advertising and stock by SKU.")

        findings = diagnose_skus(sku_metrics)
        trace.record("diagnose_skus", "Apply explicit business guardrails and preserve evidence.")

        recommendations = build_recommendations(findings)
        trace.record("build_recommendations", "Prioritize actions and assign a responsible function.")

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "data_freshness": data_freshness(rows),
            "summary": summary,
            "sku_metrics": sku_metrics,
            "findings": [finding.to_dict() for finding in findings],
            "recommendations": recommendations,
            "trace": trace.steps,
            "limitations": [
                "Thresholds are product hypotheses and must be configured for each business.",
                "Stock cover uses observed units per active date and is not a full demand forecast.",
                "Recommendations are advisory and require human approval.",
            ],
        }
