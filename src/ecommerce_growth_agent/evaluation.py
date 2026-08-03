from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .agent import GrowthAgent
from .config import BusinessThresholds


SUPPORTED_FINDING_CODES = {
    "LOW_CTR",
    "LOW_CONVERSION",
    "LOW_AD_ROI",
    "NEGATIVE_CONTRIBUTION",
    "STOCKOUT_RISK",
    "OVERSTOCK_RISK",
}


def load_evaluation_cases(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError("Evaluation fixture must be a non-empty JSON array")
    for case in payload:
        if not isinstance(case, dict):
            raise ValueError("Each evaluation case must be an object")
        missing = {"case_id", "description", "rows", "expected_findings"}.difference(case)
        if missing:
            raise ValueError(f"Evaluation case is missing: {', '.join(sorted(missing))}")
        if not isinstance(case["rows"], list) or not case["rows"]:
            raise ValueError(f"{case['case_id']} must contain at least one row")
        if not isinstance(case["expected_findings"], list):
            raise ValueError(f"{case['case_id']} expected_findings must be a list")
    return payload


def evaluate_cases(
    cases: list[dict[str, Any]],
    thresholds: BusinessThresholds | None = None,
) -> dict[str, Any]:
    agent = GrowthAgent(thresholds)
    case_results: list[dict[str, Any]] = []
    expected_total = 0
    matched_expected_total = 0
    false_positive_total = 0
    covered_codes: set[str] = set()

    for case in cases:
        report = agent.run(case["rows"])
        actual = {(item["sku"], item["code"]) for item in report["findings"]}
        expected = {
            (str(item["sku"]), str(item["code"]))
            for item in case["expected_findings"]
        }
        matched = actual & expected
        missing = expected - actual
        unexpected = actual - expected
        expected_total += len(expected)
        matched_expected_total += len(matched)
        false_positive_total += len(unexpected)
        covered_codes.update(code for _, code in matched)
        case_results.append(
            {
                "case_id": case["case_id"],
                "description": case["description"],
                "passed": not missing and not unexpected,
                "expected": _serialize_findings(expected),
                "actual": _serialize_findings(actual),
                "missing": _serialize_findings(missing),
                "unexpected": _serialize_findings(unexpected),
            }
        )

    passed_cases = sum(1 for item in case_results if item["passed"])
    return {
        "fixture_type": "synthetic rule-isolation cases",
        "guardrails": agent.thresholds.to_dict(),
        "summary": {
            "case_count": len(case_results),
            "passed_cases": passed_cases,
            "exact_case_match_rate": round(passed_cases / len(case_results), 4),
            "expected_finding_recall": round(matched_expected_total / expected_total, 4) if expected_total else 1.0,
            "false_positive_count": false_positive_total,
            "rule_coverage": {
                "covered": len(covered_codes),
                "supported": len(SUPPORTED_FINDING_CODES),
                "rate": round(len(covered_codes) / len(SUPPORTED_FINDING_CODES), 4),
                "covered_codes": sorted(covered_codes),
                "uncovered_codes": sorted(SUPPORTED_FINDING_CODES - covered_codes),
            },
        },
        "cases": case_results,
        "interpretation": [
            "These fixtures are engineered to isolate known rules; they do not estimate real-world precision or business impact.",
            "A reviewed private dataset and operator labels are still required before production claims.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    coverage = summary["rule_coverage"]
    lines = [
        "# Evaluation Baseline",
        "",
        "> Synthetic rule-isolation fixture. This is deterministic regression evidence, not a real-user study.",
        "",
        "## Summary",
        "",
        "| Metric | Result |",
        "| --- | --- |",
        f"| Cases passed | {summary['passed_cases']}/{summary['case_count']} |",
        f"| Exact case match | {summary['exact_case_match_rate']:.0%} |",
        f"| Expected finding recall | {summary['expected_finding_recall']:.0%} |",
        f"| Unexpected findings | {summary['false_positive_count']} |",
        f"| Implemented rule coverage | {coverage['covered']}/{coverage['supported']} ({coverage['rate']:.0%}) |",
        "",
        "## Cases",
        "",
        "| Case | Purpose | Result |",
        "| --- | --- | --- |",
    ]
    for case in report["cases"]:
        lines.append(f"| `{case['case_id']}` | {case['description']} | {'PASS' if case['passed'] else 'FAIL'} |")
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "- The cases were designed to isolate the six implemented rules.",
            "- Passing these cases shows reproducibility and regression coverage only.",
            "- It does not prove real-world diagnostic precision, GMV growth, profit improvement, or user adoption.",
            "",
        ]
    )
    return "\n".join(lines)


def write_evaluation_report(
    fixture_path: Path,
    json_output: Path,
    markdown_output: Path,
) -> dict[str, Any]:
    report = evaluate_cases(load_evaluation_cases(fixture_path))
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_output.write_text(render_markdown(report), encoding="utf-8")
    return report


def _serialize_findings(values: set[tuple[str, str]]) -> list[dict[str, str]]:
    return [{"sku": sku, "code": code} for sku, code in sorted(values)]
