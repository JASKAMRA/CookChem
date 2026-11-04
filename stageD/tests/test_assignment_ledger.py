from __future__ import annotations

import concurrent.futures
import hashlib
import hmac
import json
import sys
import tempfile
import unittest
from pathlib import Path

STAGE_D = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STAGE_D / "src"))

from stage_d.assignment_ledger import (  # noqa: E402
    AssignmentLedgerError,
    assign_to_self,
    assignment_ledger_diagnostics,
    build_verified_durable_assignment_workload,
    reassign,
    stable_assignment_id,
    verify_assignment_ledger,
)
from stage_d.audit_checkpoint import (  # noqa: E402
    AuditCheckpointError, create_assignment_checkpoint, verify_assignment_checkpoint,
)
from stage_d.evidence_queue import SOURCE_SHA256, SOURCE_RELEASE, build_queue_from_rows  # noqa: E402
from stage_d.evidence_review_workflow import append_review_action  # noqa: E402
from stage_d.reviewer_identity import AuthenticatedReviewer  # noqa: E402


def synthetic_queue():
    template = {
        "Compound": "Synthetic compound", "Compound_ID": "MOL-SYN-001", "Drug": "Synthetic probe",
        "Evidence_Type": "In vitro", "Mechanism": "Synthetic assay", "Study_ID": "SYN-STUDY-1",
        "Study_Design": "Synthetic design", "Source_Title": "Synthetic title", "Outcome": "observed effect",
        "Direction": "synthetic", "Source_URL": "https://example.invalid/source", "Source_Locator": "Table 1",
        "PMID": "00000000", "DOI": "10.0000/synthetic", "Identity_Status": "verified_exact", "Conflict_Group": "",
    }
    rows = [{"Evidence_ID": f"SB-SYN-{i:04d}", **template} for i in range(1, 318)]
    rows[0]["Conflict_Group"] = "SYNTHETIC-CONFLICT"
    return build_queue_from_rows(rows, source_sha256=SOURCE_SHA256, source_release=SOURCE_RELEASE)


class SyntheticProvider:
    key = b"assignment-ledger-synthetic-key"

    def authenticate(self, credentials):
        if credentials != "valid-synthetic-credential":
            raise ValueError("invalid credentials")
        return AuthenticatedReviewer("synthetic-subject-17", "Synthetic Reviewer", frozenset({"reviewer", "expert"}),
                                     "synthetic-identity-provider", "2099-01-01T00:00:00Z", "synthetic-test-key-1")

    def sign_audit_event(self, reviewer, payload):
        return hmac.new(self.key, payload, hashlib.sha256).hexdigest()

    def verify_audit_event(self, event):
        payload = {key: value for key, value in event.items() if key not in {"identity_signature", "event_sha256"}}
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
        expected = hmac.new(self.key, canonical, hashlib.sha256).hexdigest()
        return hmac.compare_digest(str(event.get("identity_signature", "")), expected)

    def resolve_reviewer(self, issuer, subject_id):
        if (issuer, subject_id) == ("synthetic-identity-provider", "synthetic-subject-17"):
            return self.authenticate("valid-synthetic-credential")
        return None

    def authorize_assignment(self, actor, operation, *, target_issuer, target_subject_id):
        return operation == "assign_self" and actor.issuer == target_issuer and actor.subject_id == target_subject_id


class SyntheticCheckpointProvider:
    key = b"assignment-checkpoint-synthetic-key"

    def __init__(self):
        self.store = {}

    def publish_checkpoint(self, payload):
        reference = "synthetic:" + hashlib.sha256(payload).hexdigest()
        self.store[reference] = hmac.new(self.key, payload, hashlib.sha256).hexdigest()
        return reference

    def verify_checkpoint(self, payload, reference):
        expected = self.store.get(reference)
        return expected is not None and hmac.compare_digest(expected, hmac.new(self.key, payload, hashlib.sha256).hexdigest())


class RosterProvider(SyntheticProvider):
    def authorize_assignment(self, actor, operation, *, target_issuer, target_subject_id):
        return operation in {"assign_self", "reassign"}

    def resolve_reviewer(self, issuer, subject_id):
        if issuer == "synthetic-identity-provider" and subject_id == "synthetic-subject-18":
            return AuthenticatedReviewer(
                subject_id=subject_id,
                display_name="Synthetic Reviewer Two",
                roles=frozenset({"reviewer"}),
                issuer=issuer,
                expires_at="2099-01-01T00:00:00Z",
                key_id="synthetic-test-key-2",
            )
        return super().resolve_reviewer(issuer, subject_id)


class AssignmentLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.queue = synthetic_queue()

    def _assign(self, path, record, provider=None):
        provider = provider or SyntheticProvider()
        return assign_to_self(
            path, self.queue, review_id=record["review_id"],
            identity_provider=provider, credentials="valid-synthetic-credential",
            reason="Synthetic assignment fixture only.",
        )

    def test_create_verify_duplicate_prevention_and_reassignment_history(self):
        provider = RosterProvider()
        record = self.queue["records"][0]
        with tempfile.TemporaryDirectory(prefix=".assignment-ledger-", dir=STAGE_D / "tests") as tmp:
            path = Path(tmp) / "assignments.jsonl"
            created = self._assign(path, record, provider)
            self.assertEqual(created["event_type"], "ASSIGNED")
            self.assertEqual(created["assignment_id"], stable_assignment_id(self.queue["source"]["sha256"], record["review_id"]))
            with self.assertRaisesRegex(AssignmentLedgerError, "already has an active assignment"):
                self._assign(path, record, provider)
            moved = reassign(
                path, self.queue, review_id=record["review_id"],
                target_issuer="synthetic-identity-provider", target_subject_id="synthetic-subject-18",
                identity_provider=provider, credentials="valid-synthetic-credential",
                reason="Synthetic reassignment scenario.",
            )
            events = verify_assignment_ledger(path, self.queue, identity_provider=provider)
            self.assertEqual([event["event_type"] for event in events], ["ASSIGNED", "REASSIGNED"])
            self.assertEqual(moved["previous_reviewer"], created["reviewer"])
            self.assertEqual(moved["reviewer"]["subject_id"], "synthetic-subject-18")
            diag = assignment_ledger_diagnostics(path, self.queue, identity_provider=provider)
            self.assertEqual(diag["status"], "VALID_LOCAL_CHAIN")
            self.assertEqual(diag["active_assignment_count"], 1)
            self.assertEqual(diag["external_anchor_status"], "NOT_CONFIGURED")

    def test_reassignment_fails_closed_without_authorized_roster_target(self):
        provider = SyntheticProvider()
        record = self.queue["records"][0]
        with tempfile.TemporaryDirectory(prefix=".assignment-ledger-", dir=STAGE_D / "tests") as tmp:
            path = Path(tmp) / "assignments.jsonl"
            self._assign(path, record, provider)
            with self.assertRaisesRegex(AssignmentLedgerError, "denied reassignment"):
                reassign(
                    path, self.queue, review_id=record["review_id"],
                    target_issuer="synthetic-identity-provider", target_subject_id="synthetic-subject-18",
                    identity_provider=provider, credentials="valid-synthetic-credential", reason="No policy.",
                )

    def test_reassignment_rejects_roster_resolution_for_a_different_identity(self):
        class MismatchedRosterProvider(RosterProvider):
            def resolve_reviewer(self, issuer, subject_id):
                return super().resolve_reviewer("synthetic-identity-provider", "synthetic-subject-17")

        provider = MismatchedRosterProvider()
        record = self.queue["records"][0]
        with tempfile.TemporaryDirectory(prefix=".assignment-ledger-", dir=STAGE_D / "tests") as tmp:
            path = Path(tmp) / "assignments.jsonl"
            self._assign(path, record, provider)
            with self.assertRaisesRegex(AssignmentLedgerError, "not an active roster-authorized reviewer"):
                reassign(
                    path, self.queue, review_id=record["review_id"],
                    target_issuer="synthetic-identity-provider", target_subject_id="synthetic-subject-18",
                    identity_provider=provider, credentials="valid-synthetic-credential", reason="Wrong roster identity.",
                )

    def test_concurrent_writes_are_serialized_and_events_remain_contiguous(self):
        provider = SyntheticProvider()
        records = self.queue["records"][:12]
        with tempfile.TemporaryDirectory(prefix=".assignment-ledger-", dir=STAGE_D / "tests") as tmp:
            path = Path(tmp) / "assignments.jsonl"
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
                results = list(pool.map(lambda row: self._assign(path, row, provider), records))
            events = verify_assignment_ledger(path, self.queue, identity_provider=provider)
            self.assertEqual(len(results), 12)
            self.assertEqual([event["sequence"] for event in events], list(range(1, 13)))

    def test_modified_or_reordered_event_is_detected(self):
        provider = SyntheticProvider()
        records = self.queue["records"][:2]
        with tempfile.TemporaryDirectory(prefix=".assignment-ledger-", dir=STAGE_D / "tests") as tmp:
            path = Path(tmp) / "assignments.jsonl"
            for record in records:
                self._assign(path, record, provider)
            lines = path.read_text(encoding="utf-8").splitlines()
            first, second = json.loads(lines[0]), json.loads(lines[1])
            first["reason"] = "modified"
            path.write_text(json.dumps(first) + "\n" + json.dumps(second) + "\n", encoding="utf-8")
            with self.assertRaises(AssignmentLedgerError):
                verify_assignment_ledger(path, self.queue, identity_provider=provider)
            diagnosis = assignment_ledger_diagnostics(path, self.queue, identity_provider=provider)
            self.assertEqual(diagnosis["status"], "RECOVERY_REQUIRED")

    def test_external_checkpoint_detects_assignment_tail_removal(self):
        provider = SyntheticProvider()
        checkpoint_provider = SyntheticCheckpointProvider()
        record = self.queue["records"][0]
        with tempfile.TemporaryDirectory(prefix=".assignment-ledger-", dir=STAGE_D / "tests") as tmp:
            path = Path(tmp) / "assignments.jsonl"
            self._assign(path, record, provider)
            checkpoint = create_assignment_checkpoint(
                str(path), self.queue, identity_provider=provider, checkpoint_provider=checkpoint_provider,
            )
            path.write_bytes(b"")
            result = verify_assignment_checkpoint(
                str(path), self.queue, checkpoint,
                identity_provider=provider, checkpoint_provider=checkpoint_provider,
            )
            self.assertEqual(result["status"], "CHECKPOINT_MISMATCH")

    def test_assignment_publish_response_requires_successful_reference_verification(self):
        class LyingCheckpointProvider(SyntheticCheckpointProvider):
            def verify_checkpoint(self, payload, reference):
                return False

        provider = SyntheticProvider()
        record = self.queue["records"][0]
        with tempfile.TemporaryDirectory(prefix=".assignment-ledger-", dir=STAGE_D / "tests") as tmp:
            path = Path(tmp) / "assignments.jsonl"
            self._assign(path, record, provider)
            with self.assertRaisesRegex(AuditCheckpointError, "did not verify the published assignment head"):
                create_assignment_checkpoint(
                    str(path), self.queue, identity_provider=provider,
                    checkpoint_provider=LyingCheckpointProvider(),
                )

    def test_verified_assignment_and_review_ledgers_join_into_workload(self):
        provider = SyntheticProvider()
        record = self.queue["records"][0]
        action = {
            "review_id": record["review_id"],
            "evidence_id": record["source_reference"]["evidence_id"],
            "resulting_status": "CONFLICT_REVIEW",
            "reviewer_name": "Synthetic Reviewer",
            "reviewer_role": "reviewer",
            "review_date": "2026-11-04",
            "source_locator": "Table 1",
            "rationale": "Synthetic audit fixture.",
            "review_assessment": {
                "supporting_findings": [], "contradicting_findings": [],
                "uncertainty_and_limitations": ["Synthetic fixture."],
                "exposure_comparability_status": "NOT_ASSESSED",
            },
        }
        with tempfile.TemporaryDirectory(prefix=".assignment-ledger-", dir=STAGE_D / "tests") as tmp:
            assignment_path = Path(tmp) / "assignments.jsonl"
            review_path = Path(tmp) / "reviews.jsonl"
            self._assign(assignment_path, record, provider)
            append_review_action(
                review_path, self.queue, action,
                identity_provider=provider, credentials="valid-synthetic-credential",
            )
            summary = build_verified_durable_assignment_workload(
                assignment_path, review_path, self.queue, identity_provider=provider,
            )
            self.assertEqual(summary["assigned_record_count"], 1)
            self.assertEqual(summary["in_progress_count"], 1)
            self.assertEqual(summary["reviewer_workloads"]["Synthetic Reviewer"]["in_progress"], 1)


if __name__ == "__main__":
    unittest.main()
