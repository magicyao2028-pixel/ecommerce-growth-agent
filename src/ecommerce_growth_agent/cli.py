from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .agent import GrowthAgent
from .config import load_thresholds


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze e-commerce operating data offline.")
    parser.add_argument("csv_file", type=Path, help="CSV file using the documented schema")
    parser.add_argument("--output", type=Path, help="Optional path for the JSON report")
    parser.add_argument("--config", type=Path, help="Optional JSON file containing business review thresholds")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with args.csv_file.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    thresholds = load_thresholds(args.config) if args.config else None
    report = GrowthAgent(thresholds).run(rows)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
