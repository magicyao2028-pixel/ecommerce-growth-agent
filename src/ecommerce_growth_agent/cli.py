from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .agent import GrowthAgent
from .config import load_thresholds
from .history import AnalysisHistoryStore, RetentionPolicy, fingerprint_rows
from .explanation import DeterministicExplanationAdapter, explain_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze e-commerce operating data offline.")
    parser.add_argument("csv_file", type=Path, help="CSV file using the documented schema")
    parser.add_argument("--output", type=Path, help="Optional path for the JSON report")
    parser.add_argument("--config", type=Path, help="Optional JSON file containing business review thresholds")
    parser.add_argument("--history", type=Path, help="Optional local JSON history file for safe summary records")
    parser.add_argument("--history-max-records", type=int, default=20, help="Maximum local summary records")
    parser.add_argument("--history-retain-days", type=int, default=90, help="Maximum record age in days")
    parser.add_argument("--explain", action="store_true", help="Add an evidence-constrained offline explanation")
    parser.add_argument("--generated-at", help="Optional timezone-aware ISO timestamp for reproducible fixtures")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with args.csv_file.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    thresholds = load_thresholds(args.config) if args.config else None
    report = GrowthAgent(thresholds).run(rows, generated_at=args.generated_at)
    if args.explain:
        report["explanation"] = explain_report(report, DeterministicExplanationAdapter())
    if args.history:
        history_result = AnalysisHistoryStore(
            args.history,
            RetentionPolicy(args.history_max_records, args.history_retain_days),
        ).append(report, args.csv_file.name, fingerprint_rows(rows))
        report["history_record"] = history_result
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
