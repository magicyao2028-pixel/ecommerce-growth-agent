from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Protocol


UNSAFE_ACTION_PATTERN = re.compile(
    r"\b(automatically|auto[- ]?execute|without approval|execute (?:the )?action|publish now|"
    r"place (?:a )?(?:purchase )?order|change (?:the )?price|pause (?:the )?campaign|reorder now)\b",
    re.IGNORECASE,
)
NUMBER_PATTERN = re.compile(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?%?")
WORD_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9-]{2,}")
STOPWORDS = {"and", "are", "for", "from", "has", "have", "into", "not", "the", "this", "with"}


class ExplanationAdapter(Protocol):
    name: str

    def explain(self, context: dict[str, Any]) -> dict[str, Any]: ...


@dataclass(frozen=True)
class DeterministicExplanationAdapter:
    name: str = "deterministic-evidence-v1"

    def explain(self, context: dict[str, Any]) -> dict[str, Any]:
        items = []
        for finding in context["findings"][:3]:
            items.append({
                "text": finding["evidence"],
                "finding_refs": [finding["finding_ref"]],
                "recommendation_ref": finding["recommendation_ref"],
            })
        return {"headline": "Priority operating findings for human review", "items": items}


def build_explanation_context(report: dict[str, Any]) -> dict[str, Any]:
    findings = report.get("findings")
    recommendations = report.get("recommendations")
    if not isinstance(findings, list) or not isinstance(recommendations, list):
        raise ValueError("report must contain finding and recommendation lists")
    if len(findings) != len(recommendations):
        raise ValueError("every finding must have one deterministic recommendation")
    evidence_items = []
    for index, (finding, recommendation) in enumerate(zip(findings, recommendations), start=1):
        finding_ref = f"FIND-{index:03d}"
        recommendation_ref = f"REC-{index:03d}"
        evidence_items.append({
            "finding_ref": finding_ref,
            "recommendation_ref": recommendation_ref,
            "sku": finding["sku"],
            "severity": finding["severity"],
            "code": finding["code"],
            "evidence": finding["evidence"],
            "action": recommendation["action"],
            "owner": recommendation["owner"],
            "approval": recommendation["approval"],
        })
    return {
        "schema_version": "1.0",
        "source": "structured_growth_report",
        "summary": report.get("summary", {}),
        "findings": evidence_items,
        "instructions": {
            "cite_declared_finding_refs": True,
            "use_only_numbers_from_cited_evidence": True,
            "external_actions_require_human_approval": True,
        },
    }


def explain_report(
    report: dict[str, Any],
    adapter: ExplanationAdapter | None = None,
) -> dict[str, Any]:
    context = build_explanation_context(report)
    requested = adapter or DeterministicExplanationAdapter()
    fallback = DeterministicExplanationAdapter()
    try:
        draft = requested.explain(context)
        items = _validate_and_ground(draft, context)
        return _package(draft["headline"], items, requested.name, requested.name, False, None)
    except Exception as exc:
        fallback_draft = fallback.explain(context)
        items = _validate_and_ground(fallback_draft, context)
        return _package(
            fallback_draft["headline"],
            items,
            getattr(requested, "name", type(requested).__name__),
            fallback.name,
            True,
            f"{type(exc).__name__}: {exc}",
        )


def _validate_and_ground(draft: dict[str, Any], context: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(draft, dict) or not isinstance(draft.get("headline"), str) or not draft["headline"].strip():
        raise ValueError("explanation headline must not be blank")
    if UNSAFE_ACTION_PATTERN.search(draft["headline"]):
        raise ValueError("explanation requests an unapproved external action")
    if NUMBER_PATTERN.search(draft["headline"]):
        raise ValueError("explanation headline introduces an unsupported number")
    raw_items = draft.get("items")
    if not isinstance(raw_items, list) or len(raw_items) > 10:
        raise ValueError("explanation must contain between zero and ten items")
    finding_catalog = {item["finding_ref"]: item for item in context["findings"]}
    recommendation_catalog = {item["recommendation_ref"]: item for item in context["findings"]}
    grounded = []
    for raw in raw_items:
        if not isinstance(raw, dict) or not isinstance(raw.get("text"), str) or not raw["text"].strip():
            raise ValueError("every explanation item needs text")
        refs = raw.get("finding_refs")
        recommendation_ref = raw.get("recommendation_ref")
        if not isinstance(refs, list) or not refs or not all(isinstance(ref, str) for ref in refs):
            raise ValueError("every explanation item needs finding_refs")
        if any(ref not in finding_catalog for ref in refs):
            raise ValueError("explanation cites an unknown finding")
        if recommendation_ref not in recommendation_catalog:
            raise ValueError("explanation cites an unknown recommendation")
        cited = [finding_catalog[ref] for ref in refs]
        if recommendation_catalog[recommendation_ref]["finding_ref"] not in refs:
            raise ValueError("recommendation_ref must belong to a cited finding")
        if UNSAFE_ACTION_PATTERN.search(raw["text"]):
            raise ValueError("explanation requests an unapproved external action")
        allowed_numbers = set(NUMBER_PATTERN.findall(" ".join(item["evidence"] for item in cited)))
        introduced_numbers = set(NUMBER_PATTERN.findall(raw["text"])) - allowed_numbers
        if introduced_numbers:
            raise ValueError(f"explanation introduces unsupported numbers: {sorted(introduced_numbers)}")
        source = recommendation_catalog[recommendation_ref]
        allowed_words = _meaningful_words(" ".join(
            [item["evidence"] + " " + item["action"] + " " + item["code"] for item in cited]
        ))
        if _meaningful_words(raw["text"]) and not (_meaningful_words(raw["text"]) & allowed_words):
            raise ValueError("explanation text has no lexical support in cited evidence")
        grounded.append({
            "text": raw["text"].strip(),
            "finding_refs": refs,
            "recommendation_ref": recommendation_ref,
            "source_evidence": [item["evidence"] for item in cited],
            "recommended_action": source["action"],
            "owner": source["owner"],
            "approval": source["approval"],
        })
    return grounded


def _meaningful_words(value: str) -> set[str]:
    return {word.lower() for word in WORD_PATTERN.findall(value) if word.lower() not in STOPWORDS}


def _package(
    headline: str,
    items: list[dict[str, Any]],
    requested_adapter: str,
    used_adapter: str,
    fallback_triggered: bool,
    fallback_reason: str | None,
) -> dict[str, Any]:
    return {
        "headline": headline.strip(),
        "items": items,
        "governance": {
            "requested_adapter": requested_adapter,
            "used_adapter": used_adapter,
            "fallback_triggered": fallback_triggered,
            "fallback_reason": fallback_reason,
            "source_rows_shared_with_adapter": False,
            "metrics_recalculated_by_adapter": False,
            "external_action_executed": False,
            "human_approval_required": True,
        },
    }
