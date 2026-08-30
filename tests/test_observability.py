import unittest

from ecommerce_growth_agent.observability import summarize_request_observability


class ObservabilityTests(unittest.TestCase):
    def test_summary_is_deterministic_and_review_only(self):
        result = summarize_request_observability([
            {"request_id": "a", "status": "success", "latency_ms": 100},
            {"request_id": "b", "status": "error", "latency_ms": 300, "error_code": "TIMEOUT"},
            {"request_id": "c", "status": "success", "latency_ms": 200},
        ])
        self.assertEqual(result["request_count"], 3)
        self.assertEqual(result["error_count"], 1)
        self.assertEqual(result["error_rate"], 0.3333)
        self.assertEqual(result["latency_ms"], {"min": 100.0, "max": 300.0, "avg": 200.0, "p95": 300.0})
        self.assertTrue(result["review_only"])
        self.assertFalse(result["persistence_executed"])
        self.assertFalse(result["external_action_executed"])

    def test_rejects_duplicate_ids_and_bad_error_shape(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            summarize_request_observability([
                {"request_id": "a", "status": "success", "latency_ms": 1},
                {"request_id": "a", "status": "success", "latency_ms": 2},
            ])
        with self.assertRaisesRegex(ValueError, "error_code"):
            summarize_request_observability([{"request_id": "a", "status": "error", "latency_ms": 1}])

    def test_rejects_non_finite_latency_and_success_error_code(self):
        with self.assertRaisesRegex(ValueError, "finite"):
            summarize_request_observability([{"request_id": "a", "status": "success", "latency_ms": float("nan")}])
        with self.assertRaisesRegex(ValueError, "cannot carry"):
            summarize_request_observability([{"request_id": "a", "status": "success", "latency_ms": 1, "error_code": "X"}])


if __name__ == "__main__":
    unittest.main()
