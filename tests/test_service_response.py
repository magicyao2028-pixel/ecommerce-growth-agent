import unittest

from ecommerce_growth_agent.service_response import validate_service_response


class ServiceResponseTests(unittest.TestCase):
    def setUp(self):
        self.payload = {
            "schema_version": "1.0",
            "status": "ok",
            "report": {},
            "request_receipt": {
                "request_fingerprint": "sha256:" + "a" * 64,
                "persistence_executed": False,
                "deduplication_executed": False,
                "external_action_executed": False,
            },
            "governance": {
                "persistence_executed": False,
                "external_action_executed": False,
                "human_approval_required": True,
            },
        }

    def test_validates_non_writing_envelope(self):
        result = validate_service_response(self.payload)
        self.assertTrue(result["valid"])
        self.assertTrue(result["human_approval_required"])

    def test_rejects_bad_fingerprint(self):
        self.payload["request_receipt"]["request_fingerprint"] = "not-a-fingerprint"
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            validate_service_response(self.payload)

    def test_rejects_external_action_declaration(self):
        self.payload["governance"]["external_action_executed"] = True
        with self.assertRaisesRegex(ValueError, "governance"):
            validate_service_response(self.payload)


if __name__ == "__main__":
    unittest.main()
