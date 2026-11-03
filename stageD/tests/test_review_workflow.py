from __future__ import annotations

import copy
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from stage_d.evidence_queue import build_review_queue  # noqa: E402
from stage_d.evidence_review_workflow import (  # noqa: E402
    ReviewWorkflowError,
    append_review_action,
    build_assignment_export,
    build_coverage_dashboard,
    export_assignment_csv,
    export_assignment_json,
    filter_review_queue,
    verify_review_action_log,
)


class EvidenceReviewWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.queue = build_review_queue()

    def _action(self, record, state="SOURCE_VERIFIED", *, role="researcher", action_id="ACTION-TEST-1", **extra):
        source = record["source_record"]
        return {
            "action_id": action_id,
            "review_id": record["review_id"],
            "evidence_id": record["source_reference"]["evidence_id"],
            "resulting_status": state,
            "reviewer_name": "Synthetic Test Reviewer",
            "reviewer_role": role,
            "review_date": "2026-11-04",
            "source_locator": source.get("Source_Locator") or source.get("DOI") or source.get("PMID") or "synthetic test locator",
            "rationale": "Synthetic unit-test action only; not a real review decision.",
            **extra,
        }

    def test_filters_cover_all_requested_dimensions(self):
        record = next(row for row in self.queue["records"] if all(
            row["source_record"].get(key)
            for key in ("Compound_ID", "Drug", "Study_ID", "Evidence_Type", "Identity_Status")
        ))
        source = record["source_record"]
        self.assertIn(record, filter_review_queue(self.queue, compound=source["Compound_ID"]))
        self.assertIn(record, filter_review_queue(self.queue, drug=source["Drug"]))
        self.assertIn(record, filter_review_queue(self.queue, study=source["Study_ID"]))
        self.assertIn(record, filter_review_queue(self.queue, evidence_category=source["Evidence_Type"]))
        self.assertIn(record, filter_review_queue(self.queue, outcome_polarity=record["machine_assessment"]["finding_polarity"]))
        self.assertIn(record, filter_review_queue(self.queue, identity_status=source["Identity_Status"]))
        self.assertIn(record, filter_review_queue(self.queue, source_verification_status="NOT_PERFORMED"))
        self.assertIn(record, filter_review_queue(self.queue, human_review_status="NOT_REVIEWED"))
        conflict = next(row for row in self.queue["records"] if row["source_record"].get("Conflict_Group"))
        self.assertIn(conflict, filter_review_queue(self.queue, conflict_status="CONFLICT"))
        no_conflict = next(row for row in self.queue["records"] if not row["source_record"].get("Conflict_Group"))
        self.assertIn(no_conflict, filter_review_queue(self.queue, conflict_status="NO_CONFLICT"))

    def test_assignment_export_is_deterministic_and_contains_no_review_decisions(self):
        record = self.queue["records"][0]
        filters = {"compound": record["source_record"]["Compound_ID"]}
        export_a = build_assignment_export(self.queue, filters=filters, assigned_to="reviewer@example.test")
        export_b = build_assignment_export(self.queue, filters=filters, assigned_to="reviewer@example.test")
        self.assertEqual(export_a, export_b)
        self.assertEqual(export_a["record_count"], len(export_a["records"]))
        self.assertTrue(export_a["records"])
        self.assertFalse(export_a["purpose_and_limits"]["assignment_is_human_review"])
        self.assertFalse(export_a["purpose_and_limits"]["decisions_created"])
        with tempfile.TemporaryDirectory(prefix=".review-workflow-", dir=ROOT / "tests") as tmp:
            root = Path(tmp)
            json_path, csv_path = root / "nested" / "assignment.json", root / "assignment.csv"
            export_assignment_json(json_path, export_a)
            export_assignment_csv(csv_path, export_a)
            self.assertEqual(json.loads(json_path.read_text(encoding="utf-8")), export_a)
            with csv_path.open(encoding="utf-8", newline="") as stream:
                self.assertEqual(len(list(csv.DictReader(stream))), export_a["record_count"])

    def test_workflow_requires_explicit_human_actions_and_keeps_queue_snapshot_unreviewed(self):
        record = self.queue["records"][0]
        original = copy.deepcopy(self.queue)
        with tempfile.TemporaryDirectory(prefix=".review-workflow-", dir=ROOT / "tests") as tmp:
            log = Path(tmp) / "review.jsonl"
            with self.assertRaisesRegex(ReviewWorkflowError, "prior SOURCE_VERIFIED"):
                append_review_action(log, self.queue, self._action(record, "READY_FOR_EXPERT_REVIEW"))
            with self.assertRaisesRegex(ReviewWorkflowError, "prior READY_FOR_EXPERT_REVIEW"):
                append_review_action(log, self.queue, self._action(record, "EXPERT_ACCEPTED", role="expert"))
            first = append_review_action(log, self.queue, self._action(record))
            second = append_review_action(log, self.queue, self._action(record, "READY_FOR_EXPERT_REVIEW", action_id="ACTION-TEST-2"))
            third = append_review_action(log, self.queue, self._action(record, "EXPERT_ACCEPTED", role="expert", action_id="ACTION-TEST-3"))
            actions = verify_review_action_log(log, self.queue)
            self.assertEqual([event["sequence"] for event in actions], [1, 2, 3])
            self.assertEqual(actions[-1]["event_sha256"], third["event_sha256"])
            self.assertEqual(self.queue, original)
            self.assertTrue(all(row["human_review"]["state"] == "NOT_REVIEWED" for row in self.queue["records"]))
            self.assertIn(record, filter_review_queue(self.queue, events=actions, human_review_status="EXPERT_ACCEPTED"))
            self.assertIn(record, filter_review_queue(self.queue, events=actions, source_verification_status="SOURCE_VERIFIED"))
            coverage = build_coverage_dashboard(self.queue, actions)
            self.assertEqual(coverage["expert_accepted_count"], 1)
            self.assertEqual(coverage["automatic_approval_count"], 0)
            self.assertEqual(coverage["automatic_negative_inference_count"], 0)

    def test_expert_action_requires_expert_role_and_source_locator(self):
        record = self.queue["records"][0]
        with tempfile.TemporaryDirectory(prefix=".review-workflow-", dir=ROOT / "tests") as tmp:
            log = Path(tmp) / "review.jsonl"
            append_review_action(log, self.queue, self._action(record))
            append_review_action(log, self.queue, self._action(record, "READY_FOR_EXPERT_REVIEW", action_id="ACTION-2"))
            with self.assertRaisesRegex(ReviewWorkflowError, "reviewer_role=expert"):
                append_review_action(log, self.queue, self._action(record, "EXPERT_ACCEPTED", role="researcher", action_id="ACTION-3"))
            incomplete = self._action(record, "EXPERT_REJECTED", role="expert", action_id="ACTION-4")
            incomplete["source_locator"] = " "
            with self.assertRaisesRegex(ReviewWorkflowError, "missing required fields"):
                append_review_action(log, self.queue, incomplete)

    def test_explicit_negative_requires_human_verified_state_and_is_not_inferred(self):
        record = self.queue["records"][0]
        with tempfile.TemporaryDirectory(prefix=".review-workflow-", dir=ROOT / "tests") as tmp:
            log = Path(tmp) / "review.jsonl"
            invalid = self._action(record, "IDENTITY_PENDING", negative_evidence_assessment="EXPLICIT_NEGATIVE_REVIEWED")
            with self.assertRaisesRegex(ReviewWorkflowError, "source-verified review state"):
                append_review_action(log, self.queue, invalid)
            valid = self._action(record, "SOURCE_VERIFIED", negative_evidence_assessment="EXPLICIT_NEGATIVE_REVIEWED")
            append_review_action(log, self.queue, valid)
            dashboard = build_coverage_dashboard(self.queue, verify_review_action_log(log, self.queue))
            self.assertEqual(dashboard["automatic_negative_inference_count"], 0)
            self.assertEqual(dashboard["negative_assessments_require_human_action"], True)

    def test_hash_chain_detects_tampering_and_truncation(self):
        record = self.queue["records"][0]
        with tempfile.TemporaryDirectory(prefix=".review-workflow-", dir=ROOT / "tests") as tmp:
            log = Path(tmp) / "review.jsonl"
            append_review_action(log, self.queue, self._action(record))
            original_bytes = log.read_bytes()
            event = json.loads(original_bytes.decode("utf-8"))
            event["rationale"] = "tampered"
            log.write_text(json.dumps(event) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ReviewWorkflowError, "hash is invalid"):
                verify_review_action_log(log, self.queue)
            log.write_bytes(original_bytes[:-1])
            with self.assertRaisesRegex(ReviewWorkflowError, "truncated"):
                verify_review_action_log(log, self.queue)

    def test_audit_log_access_is_confined_to_stage_d(self):
        forbidden_path = ROOT.parent / "stageB" / "evidence_review_actions.jsonl"
        with self.assertRaisesRegex(ReviewWorkflowError, "inside the Stage D workspace"):
            verify_review_action_log(forbidden_path, self.queue)

    def test_no_log_means_all_317_stay_unreviewed_and_no_auto_negative(self):
        dashboard = build_coverage_dashboard(self.queue)
        self.assertEqual(dashboard["record_count"], 317)
        self.assertEqual(dashboard["not_reviewed_record_count"], 317)
        self.assertEqual(dashboard["reviewed_record_count"], 0)
        self.assertEqual(dashboard["automatic_approval_count"], 0)
        self.assertEqual(dashboard["automatic_negative_inference_count"], 0)

    def test_checked_in_unassigned_export_and_coverage_match_current_queue(self):
        data_dir = ROOT / "data" / "phase5"
        assignment = json.loads((data_dir / "evidence_review_assignment_unassigned.json").read_text(encoding="utf-8"))
        dashboard = json.loads((data_dir / "evidence_review_coverage_dashboard.json").read_text(encoding="utf-8"))
        rebuilt_assignment = build_assignment_export(self.queue)
        rebuilt_dashboard = build_coverage_dashboard(self.queue)
        self.assertEqual(assignment, rebuilt_assignment)
        self.assertEqual(dashboard, rebuilt_dashboard)
        self.assertEqual(assignment["record_count"], 317)
        self.assertIsNone(assignment["assigned_to"])
        self.assertEqual(dashboard["not_reviewed_record_count"], 317)

    def test_action_schema_is_parseable_and_optional_draft_2020_12_validation(self):
        action_schema = json.loads((ROOT / "schemas" / "evidence_review_action.schema.json").read_text(encoding="utf-8"))
        assignment_schema = json.loads((ROOT / "schemas" / "evidence_review_assignment.schema.json").read_text(encoding="utf-8"))
        coverage_schema = json.loads((ROOT / "schemas" / "evidence_review_coverage.schema.json").read_text(encoding="utf-8"))
        for schema in (action_schema, assignment_schema, coverage_schema):
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertIn("EXPERT_ACCEPTED", action_schema["properties"]["resulting_status"]["enum"])
        self.assertIn("automatic_approval_count", coverage_schema["required"])
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema is not installed")
        for schema in (action_schema, assignment_schema, coverage_schema):
            jsonschema.Draft202012Validator.check_schema(schema)


if __name__ == "__main__":
    unittest.main()
