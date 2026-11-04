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

from stage_d.audit_checkpoint import (  # noqa: E402
    AuditCheckpointError,
    audit_history_diagnostics,
    create_external_checkpoint,
    verify_external_checkpoint,
)
from stage_d.evidence_review_workflow import append_review_action  # noqa: E402
from stage_d.evidence_queue import SOURCE_SHA256, SOURCE_RELEASE, build_queue_from_rows  # noqa: E402
from stage_d.reviewer_identity import AuthenticatedReviewer  # noqa: E402


def synthetic_review_queue():
    rows = []
    for index in range(1, 318):
        rows.append({
            "Evidence_ID": f"SB-SYN-{index:04d}", "Compound": f"Synthetic compound {index}",
            "Compound_ID": f"MOL-SYN-{index:04d}", "Drug": "Synthetic probe", "Evidence_Type": "In vitro",
            "Mechanism": "Synthetic assay", "Study_ID": f"STUDY-SYN-{index:04d}",
            "Study_Design": "Synthetic design", "Source_Title": f"Synthetic study {index}",
            "Outcome": "observed effect", "Direction": "synthetic", "Source_URL": "https://example.invalid/source",
            "Source_Locator": "Table 1", "PMID": "00000000", "DOI": f"10.0000/synthetic.{index}",
            "Identity_Status": "verified_exact", "Conflict_Group": "SYNTHETIC-CONFLICT" if index == 2 else "",
        })
    return build_queue_from_rows(rows, source_sha256=SOURCE_SHA256, source_release=SOURCE_RELEASE)


class SyntheticReviewerProvider:
    key = b"review-audit-synthetic-key"

    def authenticate(self, credentials):
        if credentials != "synthetic-test-credential":
            raise ValueError("invalid credentials")
        return AuthenticatedReviewer("synthetic-reviewer-001", "Synthetic Test Reviewer",
                                     frozenset({"reviewer", "expert"}), "synthetic-test-provider",
                                     "2099-01-01T00:00:00Z", "synthetic-review-key-1")

    def sign_audit_event(self, reviewer, payload):
        return hmac.new(self.key, payload, hashlib.sha256).hexdigest()

    def verify_audit_event(self, event):
        payload = {key: value for key, value in event.items() if key not in {"identity_signature", "event_sha256"}}
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
        expected = hmac.new(self.key, canonical, hashlib.sha256).hexdigest()
        return hmac.compare_digest(str(event.get("identity_signature", "")), expected)


class SyntheticCheckpointProvider:
    key = b"independent-synthetic-checkpoint-key"

    def __init__(self):
        self.store = {}

    def publish_checkpoint(self, payload):
        reference = "synthetic-checkpoint:" + hashlib.sha256(payload).hexdigest()
        self.store[reference] = hmac.new(self.key, payload, hashlib.sha256).hexdigest()
        return reference

    def verify_checkpoint(self, payload, external_reference):
        expected = self.store.get(external_reference)
        actual = hmac.new(self.key, payload, hashlib.sha256).hexdigest()
        return expected is not None and hmac.compare_digest(expected, actual)


class AuditCheckpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.queue = synthetic_review_queue()
        cls.record = cls.queue["records"][0]

    def test_external_checkpoint_anchors_and_verifies_exact_audit_head(self):
        reviewer = SyntheticReviewerProvider()
        checkpoint_provider = SyntheticCheckpointProvider()
        payload = self._action()
        with tempfile.TemporaryDirectory(prefix=".audit-checkpoint-", dir=STAGE_D / "tests") as tmp:
            log = Path(tmp) / "actions.jsonl"
            append_review_action(log, self.queue, payload, identity_provider=reviewer, credentials="synthetic-test-credential")
            unanchored = audit_history_diagnostics(str(log), self.queue, identity_provider=reviewer)
            self.assertEqual(unanchored["local_integrity_status"], "VALID_LOCAL_CHAIN")
            self.assertEqual(unanchored["external_integrity_status"], "NOT_CONFIGURED")
            checkpoint = create_external_checkpoint(
                str(log), self.queue, identity_provider=reviewer, checkpoint_provider=checkpoint_provider,
            )
            result = verify_external_checkpoint(
                str(log), self.queue, checkpoint,
                identity_provider=reviewer, checkpoint_provider=checkpoint_provider,
            )
            self.assertEqual(result["status"], "EXTERNALLY_ANCHORED")
            self.assertEqual(result["event_count"], 1)

    def test_trailing_event_removal_is_detected_by_external_checkpoint(self):
        reviewer = SyntheticReviewerProvider()
        checkpoint_provider = SyntheticCheckpointProvider()
        action = self._action()
        with tempfile.TemporaryDirectory(prefix=".audit-checkpoint-", dir=STAGE_D / "tests") as tmp:
            log = Path(tmp) / "actions.jsonl"
            append_review_action(log, self.queue, action, identity_provider=reviewer, credentials="synthetic-test-credential")
            checkpoint = create_external_checkpoint(
                str(log), self.queue, identity_provider=reviewer, checkpoint_provider=checkpoint_provider,
            )
            log.write_bytes(b"")
            result = verify_external_checkpoint(
                str(log), self.queue, checkpoint,
                identity_provider=reviewer, checkpoint_provider=checkpoint_provider,
            )
            self.assertEqual(result["status"], "CHECKPOINT_MISMATCH")

    def _action(self):
        return {
            "review_id": self.record["review_id"],
            "evidence_id": self.record["source_reference"]["evidence_id"],
            "resulting_status": "SOURCE_VERIFIED",
            "reviewer_name": "Synthetic Test Reviewer",
            "reviewer_role": "reviewer",
            "review_date": "2026-11-04",
            "source_locator": "Table 1",
            "rationale": "Synthetic action for checkpoint tests.",
            "review_assessment": {
                "supporting_findings": [], "contradicting_findings": [],
                "uncertainty_and_limitations": ["Synthetic fixture."],
                "exposure_comparability_status": "NOT_ASSESSED",
            },
        }

    def test_external_checkpoint_is_not_faked_when_adapter_is_missing(self):
        with tempfile.TemporaryDirectory(prefix=".audit-checkpoint-", dir=STAGE_D / "tests") as tmp:
            with self.assertRaisesRegex(AuditCheckpointError, "no independent checkpoint provider"):
                create_external_checkpoint(
                    str(Path(tmp) / "actions.jsonl"), self.queue,
                    identity_provider=None, checkpoint_provider=None,
                )


if __name__ == "__main__":
    unittest.main()
