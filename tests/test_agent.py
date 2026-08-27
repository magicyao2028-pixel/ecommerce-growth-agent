import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from ecommerce_growth_agent import BusinessThresholds, GrowthAgent, analyze_request, load_thresholds


def row(**overrides):
    value = {
        "date": "2026-07-01",
        "sku": "SKU-001",
        "product_name": "Sample Product",
        "category": "Food",
        "impressions": 1000,
        "clicks": 40,
        "orders": 4,
        "units": 5,
        "revenue": 500,
        "ad_spend": 100,
        "cost": 250,
        "stock": 30,
    }
    value.update(overrides)
    return value


class GrowthAgentTests(unittest.TestCase):
    def test_service_contract_returns_offline_report_without_writes(self):
        payload = {"rows": [row()], "generated_at": "2026-08-25T09:00:00+08:00", "include_explanation": True}
        result = analyze_request(payload)
        self.assertEqual(result["schema_version"], "1.0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["report"]["generated_at"], "2026-08-25T09:00:00+08:00")
        self.assertIn("explanation", result["report"])
        self.assertFalse(result["governance"]["persistence_executed"])
        self.assertFalse(result["governance"]["external_action_executed"])
        self.assertTrue(result["request_receipt"]["retry_safe"])
        self.assertEqual(result["request_receipt"], analyze_request({**payload, "generated_at": "2026-08-26T09:00:00+08:00"})["request_receipt"])

    def test_service_receipt_changes_when_business_input_changes(self):
        first = analyze_request({"rows": [row()]})["request_receipt"]["request_fingerprint"]
        changed = analyze_request({"rows": [row(revenue=501)]})["request_receipt"]["request_fingerprint"]
        self.assertNotEqual(first, changed)

    def test_service_contract_rejects_empty_or_malformed_requests(self):
        with self.assertRaisesRegex(ValueError, "non-empty list"):
            analyze_request({"rows": []})
        with self.assertRaisesRegex(ValueError, "include_explanation"):
            analyze_request({"rows": [row()], "include_explanation": "yes"})

    def test_calculates_portfolio_metrics(self):
        report = GrowthAgent().run([row(), row(sku="SKU-002", revenue=300, ad_spend=50, cost=100)])
        self.assertEqual(report["summary"]["gmv"], 800.0)
        self.assertEqual(report["summary"]["orders"], 8)
        self.assertEqual(report["summary"]["ad_roi"], 5.33)
        self.assertEqual(len(report["trace"]), 5)

    def test_detects_low_conversion_and_negative_profit(self):
        report = GrowthAgent().run(
            [row(clicks=100, orders=1, revenue=100, ad_spend=80, cost=50)]
        )
        codes = {finding["code"] for finding in report["findings"]}
        self.assertIn("LOW_CONVERSION", codes)
        self.assertIn("LOW_AD_ROI", codes)
        self.assertIn("NEGATIVE_CONTRIBUTION", codes)

    def test_rejects_invalid_funnel_data(self):
        with self.assertRaisesRegex(ValueError, "clicks cannot exceed impressions"):
            GrowthAgent().run([row(impressions=10, clicks=20)])

    def test_requires_input(self):
        with self.assertRaisesRegex(ValueError, "At least one sales row"):
            GrowthAgent().run([])

    def test_accepts_reproducible_timestamp_and_rejects_naive_timestamp(self):
        report = GrowthAgent().run([row()], generated_at="2026-08-21T09:00:00+08:00")
        self.assertEqual(report["generated_at"], "2026-08-21T09:00:00+08:00")
        with self.assertRaisesRegex(ValueError, "timezone offset"):
            GrowthAgent().run([row()], generated_at="2026-08-21T09:00:00")

    def test_custom_threshold_changes_diagnosis_and_is_reported(self):
        data = [row(impressions=1000, clicks=15, orders=3, revenue=500, ad_spend=100, stock=100)]
        default_codes = {finding["code"] for finding in GrowthAgent().run(data)["findings"]}
        thresholds = BusinessThresholds(low_ctr=0.01, overstock_cover_days=200)
        report = GrowthAgent(thresholds).run(data)
        custom_codes = {finding["code"] for finding in report["findings"]}

        self.assertIn("LOW_CTR", default_codes)
        self.assertNotIn("LOW_CTR", custom_codes)
        self.assertEqual(report["guardrails"]["low_ctr"], 0.01)

    def test_loads_thresholds_and_rejects_invalid_ranges(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "thresholds.json"
            path.write_text('{"low_ad_roi": 2.25}', encoding="utf-8")
            self.assertEqual(load_thresholds(path).low_ad_roi, 2.25)

        with self.assertRaisesRegex(ValueError, "stockout_cover_days must be lower"):
            BusinessThresholds(stockout_cover_days=90, overstock_cover_days=60)

    def test_rejects_non_finite_thresholds(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "finite numbers"):
                    BusinessThresholds(low_ad_roi=value)
        with self.assertRaisesRegex(ValueError, "finite numbers"):
            BusinessThresholds.from_mapping({"low_ctr": "NaN"})
        with self.assertRaisesRegex(ValueError, "finite numbers"):
            BusinessThresholds.from_mapping({"low_ctr": True})

    def test_rejects_non_finite_or_boolean_sales_numbers(self):
        for field in ("revenue", "ad_spend", "cost"):
            for value in ("NaN", "Infinity", "-Infinity", True):
                with self.subTest(field=field, value=value):
                    with self.assertRaisesRegex(ValueError, field):
                        GrowthAgent().run([row(**{field: value})])

    def test_rejects_boolean_and_fractional_count_fields(self):
        for field in ("impressions", "clicks", "orders", "units", "stock"):
            for value in (True, 1.5, float("nan"), float("inf")):
                with self.subTest(field=field, value=value):
                    with self.assertRaisesRegex(ValueError, "integer"):
                        GrowthAgent().run([row(**{field: value})])


if __name__ == "__main__":
    unittest.main()
