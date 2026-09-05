import unittest

from ecommerce_growth_agent.response_review import audit_response_review_feedback


class ResponseReviewTests(unittest.TestCase):
    def setUp(self):
        self.fingerprint = "sha256:" + "a" * 64
        self.response = {
            "schema_version": "1.0", "status": "ok", "report": {},
            "request_receipt": {"request_fingerprint": self.fingerprint, "persistence_executed": False, "deduplication_executed": False},
            "governance": {"persistence_executed": False, "external_action_executed": False, "human_approval_required": True},
        }
        self.feedback = [
            {"feedback_id": "A", "request_fingerprint": self.fingerprint, "recorded_on": "2026-08-20", "status": "accepted", "summary": "ok", "applied": False},
            {"feedback_id": "B", "request_fingerprint": self.fingerprint, "recorded_on": "2026-08-21", "status": "pending", "summary": "later", "applied": False},
        ]

    def test_counts_accepted_and_excluded(self):
        result = audit_response_review_feedback(self.response, self.feedback)
        self.assertEqual(result["accepted_count"], 1)
        self.assertEqual(result["excluded_count"], 1)
        self.assertFalse(result["persistence_executed"])

    def test_rejects_fingerprint_mismatch(self):
        self.feedback[0]["request_fingerprint"] = "sha256:" + "b" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            audit_response_review_feedback(self.response, self.feedback)

    def test_rejects_duplicate_ids(self):
        self.feedback[1]["feedback_id"] = "A"
        with self.assertRaisesRegex(ValueError, "unique"):
            audit_response_review_feedback(self.response, self.feedback)

    def test_rejects_out_of_order_dates(self):
        self.feedback[1]["recorded_on"] = "2026-08-19"
        with self.assertRaisesRegex(ValueError, "chronological"):
            audit_response_review_feedback(self.response, self.feedback)

    def test_rejects_applied_feedback(self):
        self.feedback[0]["applied"] = True
        with self.assertRaisesRegex(ValueError, "apply"):
            audit_response_review_feedback(self.response, self.feedback)

    def test_rejects_unknown_status(self):
        self.feedback[0]["status"] = "approved"
        with self.assertRaisesRegex(ValueError, "status"):
            audit_response_review_feedback(self.response, self.feedback)

    def test_rejects_empty_batch(self):
        with self.assertRaisesRegex(ValueError, "non-empty"):
            audit_response_review_feedback(self.response, [])

    def test_rejects_invalid_envelope(self):
        bad = dict(self.response)
        bad["governance"] = {**bad["governance"], "external_action_executed": True}
        with self.assertRaisesRegex(ValueError, "governance"):
            audit_response_review_feedback(bad, self.feedback)


if __name__ == "__main__":
    unittest.main()
