import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from ecommerce_growth_agent.evaluation import evaluate_cases, load_evaluation_cases, write_evaluation_report


FIXTURE = Path(__file__).parents[1] / "data" / "evaluation_cases.json"


class EvaluationTests(unittest.TestCase):
    def test_full_fixture_matches_all_rules(self):
        report = evaluate_cases(load_evaluation_cases(FIXTURE))

        self.assertEqual(report["summary"]["passed_cases"], 7)
        self.assertEqual(report["summary"]["exact_case_match_rate"], 1.0)
        self.assertEqual(report["summary"]["false_positive_count"], 0)
        self.assertEqual(report["summary"]["rule_coverage"]["covered"], 6)
        self.assertEqual(report["summary"]["rule_coverage"]["uncovered_codes"], [])

    def test_reports_missing_and_unexpected_findings(self):
        cases = load_evaluation_cases(FIXTURE)
        cases[0]["expected_findings"] = [{"sku": "HEALTHY-001", "code": "LOW_CTR"}]

        report = evaluate_cases(cases)

        self.assertFalse(report["cases"][0]["passed"])
        self.assertEqual(report["cases"][0]["missing"][0]["code"], "LOW_CTR")

    def test_writes_reproducible_json_and_markdown_reports(self):
        with TemporaryDirectory() as directory:
            json_path = Path(directory) / "report.json"
            markdown_path = Path(directory) / "report.md"
            report = write_evaluation_report(FIXTURE, json_path, markdown_path)

            self.assertEqual(json.loads(json_path.read_text(encoding="utf-8")), report)
            self.assertIn("Implemented rule coverage", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
