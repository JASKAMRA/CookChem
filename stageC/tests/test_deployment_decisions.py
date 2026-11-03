from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

STAGE_C = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STAGE_C / "src"))

from stage_c.deployment_decisions import (  # noqa: E402
    build_readiness_dashboard,
    create_initial_tracker,
    render_readiness_markdown,
    validate_decision_tracker,
)


class OwnerDecisionTrackerTests(unittest.TestCase):
    def setUp(self):
        self.tracker = create_initial_tracker()

    def test_initial_tracker_has_15_pending_decisions_and_does_not_clear_gate(self):
        result = validate_decision_tracker(self.tracker)
        dashboard = build_readiness_dashboard(self.tracker)
        self.assertEqual(result["validation_status"], "PASS")
        self.assertEqual(result["decision_count"], 15)
        self.assertEqual(result["approval_counts"], {"APPROVED": 0, "PENDING": 15, "REJECTED": 0})
        self.assertEqual(dashboard["overall_status"], "BLOCKED")
        self.assertFalse(dashboard["inference_authorized"])

    def test_schema_covers_all_required_decision_fields_and_exact_question_ids(self):
        schema_path = STAGE_C / "schemas/stage_a_owner_decision_tracker.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        item_schema = schema["properties"]["decisions"]["items"]["$ref"]
        self.assertEqual(item_schema, "#/$defs/decision")
        decision_schema = schema["$defs"]["decision"]
        self.assertEqual(set(decision_schema["required"]), {
            "decision_id", "topic", "owner_response", "supporting_artifact", "source_locator",
            "decision_date", "scientific_reviewer", "approval_status", "unresolved_rationale",
        })
        self.assertEqual(set(decision_schema["properties"]["decision_id"]["enum"]), {f"RF-{i:02}" for i in range(1, 16)})

    def test_checked_in_tracker_is_complete_and_all_questions_remain_open(self):
        tracker_path = STAGE_C / "data/phase2/owner_decision_tracker.json"
        tracker = json.loads(tracker_path.read_text(encoding="utf-8"))
        result = validate_decision_tracker(tracker)
        self.assertEqual(result["validation_status"], "PASS", result["issues"])
        self.assertEqual(result["approval_counts"]["PENDING"], 15)
        self.assertEqual(result["approval_counts"]["APPROVED"], 0)

    def test_missing_row_fails_completeness(self):
        tracker = copy.deepcopy(self.tracker)
        tracker["decisions"].pop()
        result = validate_decision_tracker(tracker)
        self.assertEqual(result["validation_status"], "FAIL")
        self.assertTrue(any("RF-15" in issue for issue in result["issues"]))

    def test_duplicate_and_unknown_ids_fail(self):
        tracker = copy.deepcopy(self.tracker)
        tracker["decisions"][1]["decision_id"] = "RF-01"
        result = validate_decision_tracker(tracker)
        self.assertEqual(result["validation_status"], "FAIL")
        self.assertTrue(any("Duplicate decision_id" in issue for issue in result["issues"]))
        tracker = copy.deepcopy(self.tracker)
        tracker["decisions"][0]["decision_id"] = "RF-99"
        result = validate_decision_tracker(tracker)
        self.assertTrue(any("Unknown decision_id" in issue for issue in result["issues"]))

    def test_approval_without_evidence_and_independent_fields_is_rejected(self):
        tracker = copy.deepcopy(self.tracker)
        row = tracker["decisions"][0]
        row["approval_status"] = "APPROVED"
        result = validate_decision_tracker(tracker)
        self.assertEqual(result["validation_status"], "FAIL")
        self.assertTrue(any("cannot be approved" in issue for issue in result["issues"]))

    def test_invalid_decision_date_and_missing_open_rationale_fail(self):
        tracker = copy.deepcopy(self.tracker)
        row = tracker["decisions"][0]
        row["approval_status"] = "APPROVED"
        row.update({"owner_response": "answer", "supporting_artifact": "artifact.pdf", "source_locator": "Table 1", "decision_date": "2026-99-99", "scientific_reviewer": "Reviewer"})
        result = validate_decision_tracker(tracker)
        self.assertTrue(any("ISO date" in issue for issue in result["issues"]))
        tracker = copy.deepcopy(self.tracker)
        tracker["decisions"][0]["unresolved_rationale"] = None
        result = validate_decision_tracker(tracker)
        self.assertTrue(any("requires unresolved_rationale" in issue for issue in result["issues"]))

    def test_malformed_status_type_is_rejected_without_crashing(self):
        tracker = copy.deepcopy(self.tracker)
        tracker["decisions"][0]["approval_status"] = ["APPROVED"]
        tracker["overall_status"] = []
        result = validate_decision_tracker(tracker)
        self.assertEqual(result["validation_status"], "FAIL")
        self.assertTrue(any("approval_status" in issue for issue in result["issues"]))
        self.assertTrue(any("overall_status" in issue for issue in result["issues"]))

    def test_rejected_decision_requires_a_named_reviewer_and_date(self):
        tracker = copy.deepcopy(self.tracker)
        tracker["decisions"][0]["approval_status"] = "REJECTED"
        result = validate_decision_tracker(tracker)
        self.assertTrue(any("cannot be rejected without" in issue for issue in result["issues"]))

    def test_package_failure_is_visible_and_cannot_authorize_inference(self):
        dashboard = build_readiness_dashboard(self.tracker, {"validation_status": "FAIL"})
        self.assertEqual(dashboard["overall_status"], "FAIL")
        self.assertFalse(dashboard["inference_authorized"])

    def test_invalid_tracker_fails_dashboard_even_without_package(self):
        invalid = copy.deepcopy(self.tracker)
        invalid["decisions"].pop()
        dashboard = build_readiness_dashboard(invalid)
        self.assertEqual(dashboard["overall_status"], "FAIL")
        self.assertFalse(dashboard["inference_authorized"])

    def test_package_integrity_pass_still_waits_for_actual_approval(self):
        dashboard = build_readiness_dashboard(self.tracker, {"validation_status": "PASS"})
        self.assertEqual(dashboard["overall_status"], "PENDING")
        self.assertFalse(dashboard["inference_authorized"])

    def test_markdown_dashboard_has_blocking_status_and_no_inference(self):
        markdown = render_readiness_markdown(build_readiness_dashboard(self.tracker))
        self.assertIn("**Overall: BLOCKED**", markdown)
        self.assertIn("Inference authorized: NO", markdown)


if __name__ == "__main__":
    unittest.main()
