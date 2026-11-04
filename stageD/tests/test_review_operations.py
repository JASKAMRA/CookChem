from __future__ import annotations

import hashlib
import hmac
import json
import sys
import tempfile
import unittest
from pathlib import Path

STAGE_D = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STAGE_D / "src"))
from stage_d.review_operations import (  # noqa: E402
    ReviewOperationsError, assign_reviewer, read_verified_review_operations, reviewer_worklist,
    review_progress, submit_review_status,
)
from stage_d.reviewer_identity import AuthenticatedReviewer  # noqa: E402


def register():
    return {"register_version": "1.1.0", "reviews": [
        {"review_id": "SYN-E-1", "review_type": "evidence", "review_status": "PENDING_HUMAN_REVIEW",
         "identity_and_evidence": {"evidence_id": "E-SYN-1", "source_locator": "Table 1"},
         "reviewer_requirement": "qualified evidence reviewer", "unresolved_questions": ["Synthetic identity check"]},
        {"review_id": "SYN-M-1", "review_type": "mechanism", "review_status": "PENDING_HUMAN_REVIEW",
         "identity_and_evidence": {"evidence_id": "E-SYN-2", "source_locator": "Figure 2"},
         "reviewer_requirement": "qualified mechanism reviewer", "unresolved_questions": ["Synthetic target check"]},
    ]}


class SyntheticQualifiedProvider:
    key = b"review-ops-synthetic-only"

    def __init__(self, *, deny_assignment=False, no_qualification=False):
        self.deny_assignment = deny_assignment
        self.no_qualification = no_qualification

    def authenticate(self, credentials):
        if credentials == "coordinator":
            return AuthenticatedReviewer("coord-1", "Synthetic Coordinator", frozenset({"reviewer", "expert"}),
                                         "synthetic-issuer", "2099-01-01T00:00:00Z", "synthetic-key")
        if credentials == "evidence-reviewer":
            return AuthenticatedReviewer("reviewer-1", "Synthetic Evidence Reviewer", frozenset({"reviewer", "expert"}),
                                         "synthetic-issuer", "2099-01-01T00:00:00Z", "synthetic-key")
        if credentials == "nonexpert":
            return AuthenticatedReviewer("reviewer-1", "Synthetic Evidence Reviewer", frozenset({"reviewer"}),
                                         "synthetic-issuer", "2099-01-01T00:00:00Z", "synthetic-key")
        raise ValueError("bad synthetic credential")

    def resolve_reviewer(self, issuer, subject_id):
        if issuer == "synthetic-issuer" and subject_id == "reviewer-1":
            return self.authenticate("evidence-reviewer")
        if issuer == "synthetic-issuer" and subject_id == "coord-1":
            return self.authenticate("coordinator")
        return None

    def authorize_assignment(self, actor, operation, *, target_issuer, target_subject_id):
        return not self.deny_assignment and actor.subject_id == "coord-1" and operation == "assign"

    def qualification_attestation(self, issuer, subject_id, review_type):
        if self.no_qualification or subject_id not in {"reviewer-1", "coord-1"}:
            return None
        return {"status": "VERIFIED", "review_type": review_type, "qualification_reference": f"synthetic:{subject_id}:{review_type}"}

    def verify_qualification_attestation(self, issuer, subject_id, review_type, attestation):
        return (isinstance(attestation, dict) and attestation.get("status") == "VERIFIED"
                and attestation.get("review_type") == review_type
                and attestation.get("qualification_reference") == f"synthetic:{subject_id}:{review_type}")

    def sign_audit_event(self, reviewer, payload):
        return hmac.new(self.key, payload, hashlib.sha256).hexdigest()

    def verify_audit_event(self, event):
        payload = {key: value for key, value in event.items() if key not in {"identity_signature", "event_sha256"}}
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        expected = hmac.new(self.key, canonical, hashlib.sha256).hexdigest()
        return hmac.compare_digest(str(event.get("identity_signature", "")), expected)


class ReviewOperationsTests(unittest.TestCase):
    def setUp(self):
        self.register = register()
        self.provider = SyntheticQualifiedProvider()
        self.temp = tempfile.TemporaryDirectory(prefix=".review-ops-", dir=STAGE_D / "tests")
        self.log = Path(self.temp.name) / "review-ops.jsonl"

    def tearDown(self):
        self.temp.cleanup()

    def assign(self, review_id="SYN-E-1", *, provider=None):
        return assign_reviewer(self.log, self.register, review_id=review_id,
                               target_issuer="synthetic-issuer", target_subject_id="reviewer-1",
                               review_date="2026-11-05", rationale="Synthetic assignment only.",
                               identity_provider=provider or self.provider, credentials="coordinator")

    def test_assignment_requires_authorized_coordinator_and_verified_qualification(self):
        with self.assertRaisesRegex(ReviewOperationsError, "coordinator/expert"):
            assign_reviewer(self.log, self.register, review_id="SYN-E-1", target_issuer="synthetic-issuer",
                            target_subject_id="reviewer-1", review_date="2026-11-05", rationale="Synthetic",
                            identity_provider=self.provider, credentials="nonexpert")
        with self.assertRaisesRegex(ReviewOperationsError, "denied"):
            self.assign(provider=SyntheticQualifiedProvider(deny_assignment=True))
        with self.assertRaisesRegex(ReviewOperationsError, "lacks verified qualifications"):
            self.assign(provider=SyntheticQualifiedProvider(no_qualification=True))
        self.assertFalse(self.log.exists())

    def test_unqualified_reviewer_cannot_submit_status_or_decision(self):
        self.assign()
        with self.assertRaisesRegex(ReviewOperationsError, "lacks verified qualifications"):
            submit_review_status(self.log, self.register, review_id="SYN-E-1", new_status="in_review",
                                 review_date="2026-11-05", rationale="Synthetic attempt.",
                                 evidence_references=["synthetic://source#table1"],
                                 identity_provider=SyntheticQualifiedProvider(no_qualification=True),
                                 credentials="evidence-reviewer")
        self.assertEqual(len(self.log.read_text(encoding="utf-8").splitlines()), 1)

    def test_status_transition_final_decision_and_audit_trail(self):
        self.assign()
        with self.assertRaisesRegex(ReviewOperationsError, "Cannot assign record currently in assigned"):
            self.assign()
        entered = submit_review_status(self.log, self.register, review_id="SYN-E-1", new_status="in_review",
                                       review_date="2026-11-05", rationale="Synthetic review entry.",
                                       evidence_references=["synthetic://source#table1"],
                                       identity_provider=self.provider, credentials="evidence-reviewer")
        with self.assertRaisesRegex(ReviewOperationsError, "evidence references and sign-off"):
            submit_review_status(self.log, self.register, review_id="SYN-E-1", new_status="approved",
                                 review_date="2026-11-05", rationale="Synthetic decision.",
                                 evidence_references=["synthetic://source#table1"], signoff_reference={"fake": True},
                                 identity_provider=self.provider,
                                 credentials="evidence-reviewer")
        final = submit_review_status(self.log, self.register, review_id="SYN-E-1", new_status="approved",
                                     review_date="2026-11-05", rationale="Synthetic final rationale.",
                                     evidence_references=["synthetic://source#table1"], signoff_reference="synthetic-signoff-1",
                                     identity_provider=self.provider, credentials="evidence-reviewer")
        raw = self.log.read_text().splitlines()
        self.assertEqual(len(raw), 3)
        self.assertEqual([json.loads(line)["sequence"] for line in raw], [1, 2, 3])
        self.assertEqual(entered["new_status"], "in_review")
        self.assertEqual(final["new_status"], "approved")
        progress = review_progress(self.register, [json.loads(line) for line in raw])
        self.assertEqual(progress["status_counts"]["approved"], 1)
        self.assertEqual(progress["status_counts"]["pending"], 1)
        with self.assertRaisesRegex(ReviewOperationsError, "Invalid status transition"):
            submit_review_status(self.log, self.register, review_id="SYN-E-1", new_status="rejected",
                                 review_date="2026-11-05", rationale="Synthetic", evidence_references=["synthetic"],
                                 signoff_reference="synthetic-signoff-2", identity_provider=self.provider,
                                 credentials="evidence-reviewer")

    def test_nonexpert_cannot_finalize_and_tampered_audit_event_is_rejected(self):
        self.assign()
        submit_review_status(self.log, self.register, review_id="SYN-E-1", new_status="in_review",
                             review_date="2026-11-05", rationale="Synthetic review entry.",
                             evidence_references=["synthetic://source#table1"],
                             identity_provider=self.provider, credentials="evidence-reviewer")
        with self.assertRaisesRegex(ReviewOperationsError, "Final decisions require an authorized expert"):
            submit_review_status(self.log, self.register, review_id="SYN-E-1", new_status="approved",
                                 review_date="2026-11-05", rationale="Synthetic decision.",
                                 evidence_references=["synthetic://source#table1"], signoff_reference="synthetic-signoff",
                                 identity_provider=self.provider, credentials="nonexpert")
        lines = self.log.read_text().splitlines()
        tampered = json.loads(lines[0])
        tampered["rationale"] = "altered after signing"
        lines[0] = json.dumps(tampered)
        self.log.write_text("\n".join(lines) + "\n")
        with self.assertRaisesRegex(ReviewOperationsError, "hash chain"):
            submit_review_status(self.log, self.register, review_id="SYN-E-1", new_status="approved",
                                 review_date="2026-11-05", rationale="Synthetic decision.",
                                 evidence_references=["synthetic://source#table1"], signoff_reference="synthetic-signoff",
                                 identity_provider=self.provider, credentials="evidence-reviewer")

    def test_needs_revision_can_be_reassigned_and_finally_rejected(self):
        self.assign("SYN-M-1")
        submit_review_status(self.log, self.register, review_id="SYN-M-1", new_status="in_review",
                             review_date="2026-11-05", rationale="Synthetic mechanism review started.",
                             evidence_references=["synthetic://mechanism#figure2"],
                             identity_provider=self.provider, credentials="evidence-reviewer")
        submit_review_status(self.log, self.register, review_id="SYN-M-1", new_status="needs_revision",
                             review_date="2026-11-05", rationale="Synthetic request for more evidence.",
                             evidence_references=["synthetic://mechanism#figure2"],
                             identity_provider=self.provider, credentials="evidence-reviewer")
        self.assign("SYN-M-1")
        submit_review_status(self.log, self.register, review_id="SYN-M-1", new_status="in_review",
                             review_date="2026-11-05", rationale="Synthetic follow-up review.",
                             evidence_references=["synthetic://mechanism#figure2"],
                             identity_provider=self.provider, credentials="evidence-reviewer")
        submit_review_status(self.log, self.register, review_id="SYN-M-1", new_status="rejected",
                             review_date="2026-11-05", rationale="Synthetic rejection scenario.",
                             evidence_references=["synthetic://mechanism#figure2"], signoff_reference="synthetic-signoff-2",
                             identity_provider=self.provider, credentials="evidence-reviewer")
        events = [json.loads(line) for line in self.log.read_text().splitlines()]
        self.assertEqual([event["new_status"] for event in events],
                         ["assigned", "in_review", "needs_revision", "assigned", "in_review", "rejected"])

    def test_reviewer_worklist_is_assignment_specific_and_current_register_stays_pending(self):
        event = self.assign("SYN-M-1")
        worklist = reviewer_worklist(self.register, [event], issuer="synthetic-issuer", subject_id="reviewer-1")
        self.assertEqual([row["review_id"] for row in worklist["records"]], ["SYN-M-1"])
        self.assertTrue(all(row["review_status"] == "PENDING_HUMAN_REVIEW" for row in self.register["reviews"]))

    def test_signed_but_malformed_return_event_is_rejected(self):
        self.assign()
        submit_review_status(self.log, self.register, review_id="SYN-E-1", new_status="in_review",
                             review_date="2026-11-05", rationale="Synthetic review entry.",
                             evidence_references=["synthetic://source#table1"],
                             identity_provider=self.provider, credentials="evidence-reviewer")
        submit_review_status(self.log, self.register, review_id="SYN-E-1", new_status="approved",
                             review_date="2026-11-05", rationale="Synthetic final rationale.",
                             evidence_references=["synthetic://source#table1"], signoff_reference="synthetic-signoff",
                             identity_provider=self.provider, credentials="evidence-reviewer")
        lines = self.log.read_text(encoding="utf-8").splitlines()
        event = json.loads(lines[-1])
        event.pop("event_sha256")
        event.pop("identity_signature")
        event["review_date"] = "not-a-date"
        event["identity_signature"] = self.provider.sign_audit_event(
            self.provider.authenticate("evidence-reviewer"),
            json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8"),
        )
        from stage_d.review_operations import _hash_event
        event["event_sha256"] = _hash_event(event)
        lines[-1] = json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        self.log.write_text("\n".join(lines) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ReviewOperationsError, "Review date is invalid"):
            read_verified_review_operations(self.log, self.register, self.provider)


if __name__ == "__main__":
    unittest.main()
