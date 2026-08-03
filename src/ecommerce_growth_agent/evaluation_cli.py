from __future__ import annotations

import argparse
from pathlib import Path

from .evaluation import write_evaluation_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the synthetic rule-coverage evaluation suite.")
    parser.add_argument("--fixture", type=Path, default=Path("data/evaluation_cases.json"))
    parser.add_argument("--json-output", type=Path, default=Path("reports/evaluation_report.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("reports/evaluation_report.md"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = write_evaluation_report(args.fixture, args.json_output, args.markdown_output)
    summary = report["summary"]
    print(
        f"Evaluation complete: {summary['passed_cases']}/{summary['case_count']} cases passed; "
        f"rule coverage {summary['rule_coverage']['covered']}/{summary['rule_coverage']['supported']}."
    )


if __name__ == "__main__":
    main()
