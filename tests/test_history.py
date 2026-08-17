import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from ecommerce_growth_agent import AnalysisHistoryStore, GrowthAgent, RetentionPolicy, fingerprint_rows


def sales_row(revenue: int = 500) -> dict[str, object]:
    return {
        "date": "2026-07-01",
        "sku": "SKU-001",
        "product_name": "Synthetic Product",
        "category": "Food",
        "impressions": 1000,
        "clicks": 40,
        "orders": 4,
        "units": 5,
        "revenue": revenue,
        "ad_spend": 100,
        "cost": 250,
        "stock": 30,
    }


class AnalysisHistoryTests(unittest.TestCase):
    def test_stores_safe_summary_without_source_rows(self):
        rows = [sales_row()]
        report = GrowthAgent().run(rows)
        with TemporaryDirectory() as directory:
            path = Path(directory) / "history.json"
            result = AnalysisHistoryStore(path).append(
                report,
                "private-orders.csv",
                fingerprint_rows(rows),
                datetime(2026, 8, 6, tzinfo=timezone.utc),
            )
            payload = AnalysisHistoryStore(path).read()

        record = payload["records"][0]
        self.assertEqual(record["source_label"], "private-orders.csv")
        self.assertEqual(record["summary"]["gmv"], 500.0)
        self.assertNotIn("rows", record)
        self.assertNotIn("product_name", str(record))
        self.assertEqual(result["stored_records"], 1)

    def test_enforces_max_record_limit(self):
        with TemporaryDirectory() as directory:
            store = AnalysisHistoryStore(Path(directory) / "history.json", RetentionPolicy(max_records=2, retain_days=90))
            now = datetime(2026, 8, 6, tzinfo=timezone.utc)
            for offset in range(3):
                rows = [sales_row(500 + offset)]
                store.append(GrowthAgent().run(rows), "sales.csv", fingerprint_rows(rows), now + timedelta(minutes=offset))
            payload = store.read()

        self.assertEqual(len(payload["records"]), 2)
        self.assertEqual(payload["records"][-1]["summary"]["gmv"], 502.0)

    def test_removes_expired_records(self):
        with TemporaryDirectory() as directory:
            store = AnalysisHistoryStore(Path(directory) / "history.json", RetentionPolicy(max_records=20, retain_days=30))
            old = datetime(2026, 6, 1, tzinfo=timezone.utc)
            current = datetime(2026, 8, 6, tzinfo=timezone.utc)
            rows = [sales_row()]
            store.append(GrowthAgent().run(rows), "sales.csv", fingerprint_rows(rows), old)
            result = store.append(GrowthAgent().run(rows), "sales.csv", fingerprint_rows(rows), current)

        self.assertEqual(result["removed_by_age"], 1)
        self.assertEqual(result["stored_records"], 1)

    def test_fingerprint_is_stable_and_changes_with_data(self):
        first = fingerprint_rows([sales_row(500)])
        self.assertEqual(first, fingerprint_rows([sales_row(500)]))
        self.assertNotEqual(first, fingerprint_rows([sales_row(501)]))

    def test_identical_retry_is_idempotent(self):
        rows = [sales_row()]
        report = GrowthAgent().run(rows)
        fingerprint = fingerprint_rows(rows)
        now = datetime(2026, 8, 17, tzinfo=timezone.utc)
        with TemporaryDirectory() as directory:
            store = AnalysisHistoryStore(Path(directory) / "history.json")
            first = store.append(report, "sales.csv", fingerprint, now)
            second = store.append(report, "sales.csv", fingerprint, now + timedelta(seconds=5))
            payload = store.read()

        self.assertEqual(first["status"], "stored")
        self.assertEqual(second["status"], "duplicate_skipped")
        self.assertEqual(second["record"]["run_id"], first["record"]["run_id"])
        self.assertEqual(len(payload["records"]), 1)

    def test_rejects_invalid_retention_policy(self):
        with self.assertRaisesRegex(ValueError, "max_records"):
            RetentionPolicy(max_records=0)
        with self.assertRaisesRegex(ValueError, "retain_days"):
            RetentionPolicy(retain_days=0)


if __name__ == "__main__":
    unittest.main()
