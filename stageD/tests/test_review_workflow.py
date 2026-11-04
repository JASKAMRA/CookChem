from __future__ import annotations

import copy
import csv
import hashlib
import hmac
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from stage_d.evidence_queue import SOURCE_RELEASE, SOURCE_SHA256, build_queue_from_rows  # noqa: E402
from stage_d.evidence_review_workflow import (  # noqa: E402
    ReviewWorkflowError,
    append_review_action,
    build_assignment_export,
    build_assignment_workload_summary,
    build_coverage_dashboard,
    export_assignment_csv,
    export_assignment_json,
    filter_review_queue,
    verify_review_action_log,
)
from stage_d.reviewer_identity import AuthenticatedReviewer  # noqa: E402


class SyntheticReviewerProvider:
    """Explicit test-only identity source; never configured by the product."""

    key = b"synthetic-review-provider-test-key"

    def authenticate(self, credentials):
        if credentials != "synthetic-test-credential":
            raise ValueError("invalid synthetic credential")
        return AuthenticatedReviewer(
            subject_id="synthetic-reviewer-001",
            display_name="Synthetic Test Reviewer",
            roles=frozenset({"reviewer", "expert"}),
            issuer="synthetic-test-provider",
            expires_at="2099-01-01T00:00:00Z",
            key_id="synthetic-test-key-1",
        )

    def sign_audit_event(self, reviewer, payload):
        return hmac.new(self.key, payload, hashlib.sha256).hexdigest()

    def verify_audit_event(self, event):
        payload = {key: value for key, value in event.items() if key not in {"identity_signature", "event_sha256"}}
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
        expected = hmac.new(self.key, canonical, hashlib.sha256).hexdigest()
        return hmac.compare_digest(str(event.get("identity_signature", "")), expected)

    def resolve_reviewer(self, issuer, subject_id):
        if (issuer, subject_id) == ("synthetic-test-provider", "synthetic-reviewer-001"):
            return self.authenticate("synthetic-test-credential")
        return None

    def authorize_assignment(self, actor, operation, *, target_issuer, target_subject_id):
        return operation == "assign_self" and actor.issuer == target_issuer and actor.subject_id == target_subject_id


def synthetic_review_queue():
    rows = []
    for index in range(1, 318):
        rows.append({
            "Evidence_ID": f"SB-SYN-{index:04d}",
            "Compound": f"Synthetic compound {index}",
            "Compound_ID": f"MOL-SYN-{index:04d}",
            "Drug": "Synthetic probe",
            "Evidence_Type": "In vitro",
            "Mechanism": "Synthetic assay text",
            "Study_ID": f"STUDY-SYN-{index:04d}",
            "Study_Design": "Synthetic cell assay",
            "Source_Title": f"Synthetic study {index}",
            "Outcome": "no effect detected" if index == 5 else "observed effect",
            "Direction": "synthetic direction",
            "Source_URL": "https://example.invalid/synthetic",
            "Source_Locator": "" if index == 4 else "Table 1",
            "PMID": "00000000",
            "DOI": f"10.0000/synthetic.{index}",
            "Identity_Status": "pending" if index == 3 else "verified_exact",
            "Conflict_Group": "SYNTHETIC-CONFLICT" if index == 2 else "",
        })
    return build_queue_from_rows(rows, source_sha256=SOURCE_SHA256, source_release=SOURCE_RELEASE)


class EvidenceReviewWorkflowTests(unittest.TestCase):
    provider = SyntheticReviewerProvider()

    @classmethod
    def setUpClass(cls):
        cls.queue = synthetic_review_queue()

    def _action(self, record, state="SOURCE_VERIFIED", *, role="reviewer", action_id="ACTION-TEST-1", **extra):
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
            "review_assessment": {
                "supporting_findings": [{"finding": "Synthetic outcome text", "source_locator": source.get("Source_Locator") or "Synthetic locator"}],
                "contradicting_findings": [],
                "uncertainty_and_limitations": ["Synthetic test fixture only."],
                "exposure_comparability_status": "NOT_ASSESSED",
            },
            **extra,
        }

    def _append(self, path, action):
        return append_review_action(
            path, self.queue, action, identity_provider=self.provider,
            credentials="synthetic-test-credential",
        )

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
        export_a = build_assignment_export(
            self.queue, filters=filters, assigned_to="Synthetic Test Reviewer",
            identity_provider=self.provider, credentials="synthetic-test-credential",
        )
        export_b = build_assignment_export(
            self.queue, filters=filters, assigned_to="Synthetic Test Reviewer",
            identity_provider=self.provider, credentials="synthetic-test-credential",
        )
        self.assertEqual(export_a, export_b)
        self.assertEqual(export_a["record_count"], len(export_a["records"]))
        self.assertTrue(export_a["records"])
        self.assertFalse(export_a["purpose_and_limits"]["assignment_is_human_review"])
        self.assertFalse(export_a["purpose_and_limits"]["decisions_created"])
        with self.assertRaisesRegex(ReviewWorkflowError, "no trusted identity provider"):
            build_assignment_export(self.queue, filters=filters, assigned_to="Synthetic Test Reviewer")
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
                self._append(log, self._action(record, "READY_FOR_EXPERT_REVIEW"))
            with self.assertRaisesRegex(ReviewWorkflowError, "prior READY_FOR_EXPERT_REVIEW"):
                self._append(log, self._action(record, "EXPERT_ACCEPTED", role="expert"))
            first = self._append(log, self._action(record))
            second = self._append(log, self._action(record, "READY_FOR_EXPERT_REVIEW", action_id="ACTION-TEST-2"))
            third = self._append(log, self._action(record, "EXPERT_ACCEPTED", role="expert", action_id="ACTION-TEST-3"))
            actions = verify_review_action_log(log, self.queue, identity_provider=self.provider)
            self.assertEqual([event["sequence"] for event in actions], [1, 2, 3])
            self.assertEqual(actions[-1]["event_sha256"], third["event_sha256"])
            self.assertEqual(self.queue, original)
            self.assertTrue(all(row["human_review"]["state"] == "NOT_REVIEWED" for row in self.queue["records"]))
            self.assertIn(record, filter_review_queue(self.queue, events=actions, human_review_status="EXPERT_ACCEPTED", identity_provider=self.provider))
            self.assertIn(record, filter_review_queue(self.queue, events=actions, source_verification_status="SOURCE_VERIFIED", identity_provider=self.provider))
            coverage = build_coverage_dashboard(self.queue, actions, identity_provider=self.provider)
            self.assertEqual(coverage["expert_accepted_count"], 1)
            self.assertEqual(coverage["automatic_approval_count"], 0)
            self.assertEqual(coverage["automatic_negative_inference_count"], 0)

    def test_assigned_record_completes_authenticated_review_to_coverage_and_export(self):
        record = self.queue["records"][0]
        assigned = build_assignment_export(
            self.queue,
            filters={"compound": record["source_record"]["Compound_ID"]},
            assigned_to="Synthetic Test Reviewer",
            identity_provider=self.provider,
            credentials="synthetic-test-credential",
        )
        self.assertEqual(assigned["record_count"], 1)
        self.assertEqual(assigned["records"][0]["review_status"], "NOT_REVIEWED")
        with tempfile.TemporaryDirectory(prefix=".review-lifecycle-", dir=ROOT / "tests") as tmp:
            log = Path(tmp) / "actions.jsonl"
            self._append(log, self._action(record))
            events = verify_review_action_log(log, self.queue, identity_provider=self.provider)
            coverage = build_coverage_dashboard(self.queue, events, identity_provider=self.provider)
            refreshed = build_assignment_export(
                self.queue,
                events=events,
                filters={"compound": record["source_record"]["Compound_ID"]},
                assigned_to="Synthetic Test Reviewer",
                identity_provider=self.provider,
                credentials="synthetic-test-credential",
                event_identity_provider=self.provider,
            )
            self.assertEqual(coverage["audit_action_count"], 1)
            self.assertEqual(coverage["audit_head_sha256"], events[-1]["event_sha256"])
            self.assertEqual(coverage["reviewed_record_count"], 1)
            self.assertEqual(refreshed["records"][0]["review_status"], "SOURCE_VERIFIED")
            workload = build_assignment_workload_summary(
                self.queue, [assigned], events, identity_provider=self.provider,
            )
            self.assertEqual(workload["assigned_record_count"], 1)
            self.assertEqual(workload["in_progress_count"], 1)
            csv_path = Path(tmp) / "review-export.csv"
            export_assignment_csv(csv_path, refreshed)
            self.assertIn("SOURCE_VERIFIED", csv_path.read_text(encoding="utf-8"))

    def test_workload_rejects_duplicate_active_assignments_and_counts_completion(self):
        record = self.queue["records"][0]
        assignment = build_assignment_export(
            self.queue,
            filters={"compound": record["source_record"]["Compound_ID"]},
            assigned_to="Synthetic Test Reviewer",
            identity_provider=self.provider,
            credentials="synthetic-test-credential",
        )
        with self.assertRaisesRegex(ReviewWorkflowError, "duplicate active reviewer assignments"):
            build_assignment_workload_summary(self.queue, [assignment, assignment])
        with tempfile.TemporaryDirectory(prefix=".review-workload-", dir=ROOT / "tests") as tmp:
            log = Path(tmp) / "actions.jsonl"
            self._append(log, self._action(record))
            self._append(log, self._action(record, "READY_FOR_EXPERT_REVIEW", action_id="ACTION-WORKLOAD-2"))
            self._append(log, self._action(record, "EXPERT_ACCEPTED", role="expert", action_id="ACTION-WORKLOAD-3"))
            events = verify_review_action_log(log, self.queue, identity_provider=self.provider)
            workload = build_assignment_workload_summary(
                self.queue, [assignment], events, identity_provider=self.provider,
            )
            self.assertEqual(workload["completed_count"], 1)
            self.assertEqual(workload["in_progress_count"], 0)

    def test_expert_action_requires_expert_role_and_source_locator(self):
        record = self.queue["records"][0]
        with tempfile.TemporaryDirectory(prefix=".review-workflow-", dir=ROOT / "tests") as tmp:
            log = Path(tmp) / "review.jsonl"
            self._append(log, self._action(record))
            self._append(log, self._action(record, "READY_FOR_EXPERT_REVIEW", action_id="ACTION-2"))
            with self.assertRaisesRegex(ReviewWorkflowError, "reviewer_role=expert"):
                self._append(log, self._action(record, "EXPERT_ACCEPTED", role="reviewer", action_id="ACTION-3"))
            incomplete = self._action(record, "EXPERT_REJECTED", role="expert", action_id="ACTION-4")
            incomplete["source_locator"] = " "
            with self.assertRaisesRegex(ReviewWorkflowError, "missing required fields"):
                self._append(log, incomplete)

    def test_review_date_must_use_calendar_date_representation(self):
        record = self.queue["records"][0]
        action = self._action(record)
        action["review_date"] = "2026-W45-3"  # Python accepts this ISO week date; schema `format: date` does not.
        with tempfile.TemporaryDirectory(prefix=".review-workflow-", dir=ROOT / "tests") as tmp:
            with self.assertRaisesRegex(ReviewWorkflowError, "YYYY-MM-DD"):
                self._append(Path(tmp) / "review.jsonl", action)
        self.assertTrue(all(row["human_review"]["state"] == "NOT_REVIEWED" for row in self.queue["records"]))

    def test_explicit_negative_requires_human_verified_state_and_is_not_inferred(self):
        record = next(row for row in self.queue["records"] if row["machine_assessment"]["finding_polarity"] == "negative")
        with tempfile.TemporaryDirectory(prefix=".review-workflow-", dir=ROOT / "tests") as tmp:
            log = Path(tmp) / "review.jsonl"
            invalid = self._action(record, "IDENTITY_PENDING", negative_evidence_assessment="EXPLICIT_NEGATIVE_REVIEWED")
            with self.assertRaisesRegex(ReviewWorkflowError, "source-verified review state"):
                self._append(log, invalid)
            valid = self._action(record, "SOURCE_VERIFIED", negative_evidence_assessment="EXPLICIT_NEGATIVE_REVIEWED")
            self._append(log, valid)
            dashboard = build_coverage_dashboard(
                self.queue,
                verify_review_action_log(log, self.queue, identity_provider=self.provider),
                identity_provider=self.provider,
            )
            self.assertEqual(dashboard["automatic_negative_inference_count"], 0)
            self.assertEqual(dashboard["negative_assessments_require_human_action"], True)

    def test_positive_source_cannot_be_reviewed_as_explicit_negative(self):
        record = self.queue["records"][0]
        with tempfile.TemporaryDirectory(prefix=".review-workflow-", dir=ROOT / "tests") as tmp:
            log = Path(tmp) / "review.jsonl"
            action = self._action(record, "SOURCE_VERIFIED", negative_evidence_assessment="EXPLICIT_NEGATIVE_REVIEWED")
            with self.assertRaisesRegex(ReviewWorkflowError, "requires a source-negative finding"):
                self._append(log, action)
            self.assertFalse(log.exists())

    def test_hash_chain_detects_tampering_and_truncation(self):
        record = self.queue["records"][0]
        with tempfile.TemporaryDirectory(prefix=".review-workflow-", dir=ROOT / "tests") as tmp:
            log = Path(tmp) / "review.jsonl"
            self._append(log, self._action(record))
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
        self.skipTest("Checked-in export reconciliation depends on the frozen Stage B source; tested in the source-integration workflow")

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

    def test_review_schema_source_hashes_match_current_stage_d_records(self):
        schemas_dir = ROOT / "schemas"
        queue_schema = json.loads((schemas_dir / "evidence_review_queue.schema.json").read_text(encoding="utf-8"))
        assignment_schema = json.loads((schemas_dir / "evidence_review_assignment.schema.json").read_text(encoding="utf-8"))
        coverage_schema = json.loads((schemas_dir / "evidence_review_coverage.schema.json").read_text(encoding="utf-8"))
        data_dir = ROOT / "data" / "phase5"
        assignment = json.loads((data_dir / "evidence_review_assignment_unassigned.json").read_text(encoding="utf-8"))
        dashboard = json.loads((data_dir / "evidence_review_coverage_dashboard.json").read_text(encoding="utf-8"))
        source_sha256 = self.queue["source"]["sha256"]

        self.assertEqual(queue_schema["$defs"]["source"]["properties"]["sha256"]["const"], source_sha256)
        self.assertEqual(queue_schema["$defs"]["sourceReference"]["properties"]["source_sha256"]["const"], source_sha256)
        self.assertEqual(assignment_schema["properties"]["source_sha256"]["const"], source_sha256)
        self.assertEqual(coverage_schema["properties"]["source_sha256"]["const"], source_sha256)
        self.assertEqual(assignment["source_sha256"], source_sha256)
        self.assertEqual(dashboard["source_sha256"], source_sha256)
        self.assertEqual(assignment["record_count"], 317)
        self.assertIsNone(assignment["assigned_to"])


if __name__ == "__main__":
    unittest.main()
