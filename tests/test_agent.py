import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from ecommerce_growth_agent import BusinessThresholds, GrowthAgent, load_thresholds


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


if __name__ == "__main__":
    unittest.main()
