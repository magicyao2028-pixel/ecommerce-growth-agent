import unittest

from ecommerce_growth_agent import GrowthAgent, explain_report
from ecommerce_growth_agent.explanation import build_explanation_context


def row(**overrides):
    value = {
        "date": "2026-07-01",
        "sku": "SKU-001",
        "product_name": "Synthetic Product",
        "category": "Food",
        "impressions": 1000,
        "clicks": 100,
        "orders": 1,
        "units": 1,
        "revenue": 100,
        "ad_spend": 80,
        "cost": 50,
        "stock": 5,
    }
    value.update(overrides)
    return value


class StaticAdapter:
    name = "mock-grounded-adapter"

    def __init__(self, draft):
        self.draft = draft
        self.context = None

    def explain(self, context):
        self.context = context
        return self.draft


class BrokenAdapter:
    name = "broken-adapter"

    def explain(self, context):
        raise TimeoutError("synthetic timeout")


class ExplanationTests(unittest.TestCase):
    def setUp(self):
        self.report = GrowthAgent().run([row()])

    def test_deterministic_explanation_carries_source_and_approval(self):
        result = explain_report(self.report)
        self.assertFalse(result["governance"]["fallback_triggered"])
        self.assertTrue(result["items"])
        self.assertTrue(all(item["source_evidence"] for item in result["items"]))
        self.assertTrue(all("Human approval" in item["approval"] for item in result["items"]))
        self.assertFalse(result["governance"]["external_action_executed"])

    def test_valid_adapter_receives_structured_report_without_source_rows(self):
        evidence = self.report["findings"][0]["evidence"]
        adapter = StaticAdapter({
            "headline": "Grounded operating review",
            "items": [{"text": evidence, "finding_refs": ["FIND-001"], "recommendation_ref": "REC-001"}],
        })
        result = explain_report(self.report, adapter)
        self.assertEqual(result["governance"]["used_adapter"], adapter.name)
        self.assertNotIn("rows", adapter.context)
        self.assertNotIn("sku_metrics", adapter.context)
        self.assertFalse(result["governance"]["source_rows_shared_with_adapter"])

    def test_unknown_citation_triggers_deterministic_fallback(self):
        adapter = StaticAdapter({
            "headline": "Review",
            "items": [{"text": "Review this issue.", "finding_refs": ["FIND-999"], "recommendation_ref": "REC-001"}],
        })
        result = explain_report(self.report, adapter)
        self.assertTrue(result["governance"]["fallback_triggered"])
        self.assertIn("unknown finding", result["governance"]["fallback_reason"])

    def test_unsupported_number_triggers_fallback(self):
        adapter = StaticAdapter({
            "headline": "Review",
            "items": [{"text": "Revenue will improve by 99%.", "finding_refs": ["FIND-001"], "recommendation_ref": "REC-001"}],
        })
        result = explain_report(self.report, adapter)
        self.assertTrue(result["governance"]["fallback_triggered"])
        self.assertIn("unsupported numbers", result["governance"]["fallback_reason"])

    def test_unsupported_headline_number_and_qualitative_claim_trigger_fallback(self):
        numbered = StaticAdapter({"headline": "Guaranteed 99% growth", "items": []})
        self.assertTrue(explain_report(self.report, numbered)["governance"]["fallback_triggered"])

        unsupported = StaticAdapter({
            "headline": "Review",
            "items": [{"text": "Market dominance is certain.", "finding_refs": ["FIND-001"], "recommendation_ref": "REC-001"}],
        })
        result = explain_report(self.report, unsupported)
        self.assertTrue(result["governance"]["fallback_triggered"])
        self.assertIn("no lexical support", result["governance"]["fallback_reason"])

    def test_unapproved_action_language_triggers_fallback(self):
        adapter = StaticAdapter({
            "headline": "Review",
            "items": [{"text": "Automatically pause the campaign.", "finding_refs": ["FIND-001"], "recommendation_ref": "REC-001"}],
        })
        result = explain_report(self.report, adapter)
        self.assertTrue(result["governance"]["fallback_triggered"])
        self.assertIn("unapproved external action", result["governance"]["fallback_reason"])

    def test_adapter_failure_triggers_fallback(self):
        result = explain_report(self.report, BrokenAdapter())
        self.assertTrue(result["governance"]["fallback_triggered"])
        self.assertEqual(result["governance"]["used_adapter"], "deterministic-evidence-v1")
        self.assertIn("synthetic timeout", result["governance"]["fallback_reason"])

    def test_no_findings_produces_empty_but_governed_explanation(self):
        report = GrowthAgent().run([row(clicks=40, orders=4, units=5, revenue=500, ad_spend=100, cost=250, stock=100)])
        self.assertEqual(report["findings"], [])
        result = explain_report(report)
        self.assertEqual(result["items"], [])
        self.assertFalse(result["governance"]["fallback_triggered"])

    def test_context_rejects_misaligned_findings_and_recommendations(self):
        changed = dict(self.report)
        changed["recommendations"] = []
        with self.assertRaisesRegex(ValueError, "one deterministic recommendation"):
            build_explanation_context(changed)


if __name__ == "__main__":
    unittest.main()
