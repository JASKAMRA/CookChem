from __future__ import annotations

import sys
import tempfile
import unittest
import hashlib
import hmac
import json
from pathlib import Path

STAGE_D = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STAGE_D / "src"))

from stage_d.evidence_queue import SOURCE_SHA256, SOURCE_RELEASE, build_queue_from_rows  # noqa: E402
from stage_d.evidence_review_workflow import (  # noqa: E402
    ReviewWorkflowError,
    append_review_action,
    build_coverage_dashboard,
    build_assignment_export,
    verify_review_action_log,
)
from stage_d.reviewer_identity import AuthenticatedReviewer, reviewer_authorization_diagnostics  # noqa: E402


def synthetic_queue():
    row_template = {
        "Compound": "Synthetic compound",
        "Compound_ID": "SYN-COMPOUND-001",
        "Drug": "Synthetic probe",
        "Evidence_Type": "In vitro",
        "Mechanism": "Synthetic assay text",
        "Study_ID": "SYN-STUDY-001",
        "Study_Design": "Synthetic cell assay",
        "Source_Title": "Synthetic primary source",
        "Outcome": "observed effect",
        "Direction": "synthetic direction",
        "Source_URL": "https://example.invalid/synthetic",
        "Source_Locator": "Table 1",
        "PMID": "00000000",
        "DOI": "10.0000/synthetic",
        "Identity_Status": "verified_exact",
        "Conflict_Group": "",
    }
    rows = [{"Evidence_ID": f"SB-SYN-{index:04d}", **row_template} for index in range(1, 318)]
    rows[0]["Conflict_Group"] = "SYNTHETIC-EXPLICIT-CONFLICT"
    return build_queue_from_rows(rows, source_sha256=SOURCE_SHA256, source_release=SOURCE_RELEASE)


class SyntheticProvider:
    key = b"synthetic-review-provider-test-key"

    def __init__(self, roles=frozenset({"reviewer"}), *, display_name="Synthetic Reviewer"):
        self.roles = roles
        self.display_name = display_name

    def authenticate(self, credentials):
        if credentials != "valid-synthetic-credential":
            raise ValueError("invalid synthetic credential")
        return AuthenticatedReviewer(
            subject_id="synthetic-subject-17",
            display_name=self.display_name,
            roles=frozenset(self.roles),
            issuer="synthetic-identity-provider",
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
        if (issuer, subject_id) == ("synthetic-identity-provider", "synthetic-subject-17"):
            return self.authenticate("valid-synthetic-credential")
        return None

    def authorize_assignment(self, actor, operation, *, target_issuer, target_subject_id):
        return operation == "assign_self" and actor.issuer == target_issuer and actor.subject_id == target_subject_id

    def qualification_attestation(self, issuer, subject_id, review_type):
        return {"status": "VERIFIED", "review_type": review_type,
                "qualification_reference": f"synthetic:{issuer}:{subject_id}:{review_type}"}

    def verify_qualification_attestation(self, issuer, subject_id, review_type, attestation):
        return (attestation == self.qualification_attestation(issuer, subject_id, review_type))


class AuthenticationOnlyProvider:
    def authenticate(self, credentials):
        return AuthenticatedReviewer(
            subject_id="synthetic-subject-no-signer",
            display_name="Synthetic Reviewer",
            roles=frozenset({"reviewer"}),
            issuer="synthetic-authentication-only",
            expires_at="2099-01-01T00:00:00Z",
            key_id="synthetic-authentication-key",
        )


class ReviewAuthorizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.queue = synthetic_queue()
        cls.record = cls.queue["records"][0]

    def action(self, state="SOURCE_VERIFIED", *, role="reviewer", name="Synthetic Reviewer", action_id="SYN-ACTION-1"):
        return {
            "action_id": action_id,
            "review_id": self.record["review_id"],
            "evidence_id": self.record["source_reference"]["evidence_id"],
            "resulting_status": state,
            "reviewer_name": name,
            "reviewer_role": role,
            "review_date": "2026-11-04",
            "source_locator": "Table 1",
            "rationale": "Synthetic test action; no real evidence review is claimed.",
            "review_assessment": {
                "supporting_findings": [{"finding": "Synthetic finding", "source_locator": "Table 1"}],
                "contradicting_findings": [],
                "uncertainty_and_limitations": ["Synthetic test fixture only."],
                "exposure_comparability_status": "NOT_ASSESSED",
            },
        }

    def call_append(self, path, action, provider=None):
        return append_review_action(
            path, self.queue, action,
            identity_provider=provider,
            credentials="valid-synthetic-credential" if provider else None,
        )

    def test_submission_is_disabled_without_trusted_provider(self):
        with tempfile.TemporaryDirectory(prefix=".stage-d-auth-", dir=STAGE_D / "tests") as temp:
            log = Path(temp) / "actions.jsonl"
            with self.assertRaisesRegex(ReviewWorkflowError, "no trusted identity provider"):
                self.call_append(log, self.action())
            self.assertFalse(log.exists())

    def test_trusted_provider_configuration_still_requires_owner_release(self):
        class ConfiguredProvider(SyntheticProvider):
            def trusted_configuration(self):
                return {
                    "status": "READY",
                    "issuer": "synthetic-identity-provider",
                    "trusted_key_source": "synthetic-test-key-store",
                    "reviewer_roster_source": "synthetic-test-roster",
                    "key_rotation_policy": "synthetic-test-only",
                    "revocation_source": "synthetic-test-only",
                }

        result = reviewer_authorization_diagnostics(ConfiguredProvider())
        self.assertEqual(result["status"], "CONFIGURED_REQUIRES_DEPLOYMENT_REVIEW")
        self.assertFalse(result["production_authorization_available"])

    def test_expired_or_unbounded_credentials_are_rejected(self):
        class ExpiredProvider(SyntheticProvider):
            def authenticate(self, credentials):
                principal = super().authenticate(credentials)
                return AuthenticatedReviewer(
                    subject_id=principal.subject_id,
                    display_name=principal.display_name,
                    roles=principal.roles,
                    issuer=principal.issuer,
                    expires_at="2000-01-01T00:00:00Z",
                    key_id=principal.key_id,
                )

        with self.assertRaisesRegex(ReviewWorkflowError, "expired"):
            self.call_append("unused.jsonl", self.action(), ExpiredProvider())

    def test_named_assignment_requires_authenticated_reviewer(self):
        with self.assertRaisesRegex(ReviewWorkflowError, "no trusted identity provider"):
            build_assignment_export(self.queue, assigned_to="Synthetic Reviewer")
        with self.assertRaisesRegex(ReviewWorkflowError, "authenticated identity"):
            build_assignment_export(
                self.queue, assigned_to="Impersonated Reviewer",
                identity_provider=SyntheticProvider(), credentials="valid-synthetic-credential",
            )
        assignment = build_assignment_export(
            self.queue, assigned_to="Synthetic Reviewer",
            identity_provider=SyntheticProvider(), credentials="valid-synthetic-credential",
        )
        self.assertEqual(assignment["assigned_to"], "Synthetic Reviewer")
        self.assertFalse(assignment["purpose_and_limits"]["decisions_created"])

    def test_self_declared_name_mismatch_and_unauthorized_role_fail_closed(self):
        with tempfile.TemporaryDirectory(prefix=".stage-d-auth-", dir=STAGE_D / "tests") as temp:
            log = Path(temp) / "actions.jsonl"
            with self.assertRaisesRegex(ReviewWorkflowError, "does not match the authenticated identity"):
                self.call_append(log, self.action(name="Impersonated Reviewer"), SyntheticProvider())
            with self.assertRaisesRegex(ReviewWorkflowError, "not authorized"):
                self.call_append(log, self.action(state="EXPERT_ACCEPTED", role="expert"), SyntheticProvider())
            self.assertFalse(log.exists())

    def test_provider_without_audit_signing_cannot_submit_actions(self):
        with tempfile.TemporaryDirectory(prefix=".stage-d-auth-", dir=STAGE_D / "tests") as temp:
            log = Path(temp) / "actions.jsonl"
            action = self.action(state="CONFLICT_REVIEW", name="Synthetic Reviewer")
            with self.assertRaisesRegex(ReviewWorkflowError, "cannot sign audit events"):
                self.call_append(log, action, AuthenticationOnlyProvider())
            self.assertFalse(log.exists())

    def test_expert_disposition_requires_structured_source_linked_assessment(self):
        provider = SyntheticProvider(roles=frozenset({"reviewer", "expert"}))
        action = self.action(state="EXPERT_ACCEPTED", role="expert")
        action["review_assessment"] = None
        with tempfile.TemporaryDirectory(prefix=".stage-d-auth-", dir=STAGE_D / "tests") as temp:
            log = Path(temp) / "actions.jsonl"
            self.call_append(log, self.action(state="CONFLICT_REVIEW"), provider)
            self.call_append(log, self.action(state="SOURCE_VERIFIED", action_id="SYN-ACTION-2"), provider)
            self.call_append(log, self.action(state="READY_FOR_EXPERT_REVIEW", action_id="SYN-ACTION-3"), provider)
            action["action_id"] = "SYN-ACTION-4"
            with self.assertRaisesRegex(ReviewWorkflowError, "structured findings"):
                self.call_append(log, action, provider)

    def test_authenticated_actions_record_identity_and_enforce_transition_graph(self):
        provider = SyntheticProvider(roles=frozenset({"reviewer", "expert"}))
        with tempfile.TemporaryDirectory(prefix=".stage-d-auth-", dir=STAGE_D / "tests") as temp:
            log = Path(temp) / "actions.jsonl"
            with self.assertRaisesRegex(ReviewWorkflowError, "must explicitly address machine triage state CONFLICT_REVIEW"):
                self.call_append(log, self.action(), provider)
            first = self.call_append(log, self.action(state="CONFLICT_REVIEW"), provider)
            self.assertEqual(first["schema_version"], "1.2.0")
            self.assertEqual(first["reviewer_subject_id"], "synthetic-subject-17")
            self.assertEqual(first["identity_issuer"], "synthetic-identity-provider")
            with self.assertRaisesRegex(ReviewWorkflowError, "Invalid review-state transition"):
                self.call_append(log, self.action(state="CONFLICT_REVIEW", action_id="SYN-ACTION-2"), provider)
            with self.assertRaisesRegex(ReviewWorkflowError, "prior READY_FOR_EXPERT_REVIEW"):
                self.call_append(log, self.action(state="EXPERT_ACCEPTED", role="expert", action_id="SYN-ACTION-3"), provider)
            verified = self.call_append(log, self.action(state="SOURCE_VERIFIED", action_id="SYN-ACTION-4"), provider)
            self.assertEqual(verified["sequence"], 2)
            second = self.call_append(log, self.action(state="READY_FOR_EXPERT_REVIEW", action_id="SYN-ACTION-5"), provider)
            self.assertEqual(second["sequence"], 3)
            with self.assertRaisesRegex(ReviewWorkflowError, "trusted identity verifier is required"):
                verify_review_action_log(log, self.queue)
            events = verify_review_action_log(log, self.queue, identity_provider=provider)
            self.assertEqual(len(events), 3)
            self.assertEqual(events[-1]["resulting_status"], "READY_FOR_EXPERT_REVIEW")

    def test_legacy_self_declared_events_do_not_count_as_verified_review(self):
        record = self.record
        events = []
        previous = "0" * 64
        for sequence, status, role in (
            (1, "SOURCE_VERIFIED", "reviewer"),
            (2, "READY_FOR_EXPERT_REVIEW", "reviewer"),
            (3, "EXPERT_ACCEPTED", "expert"),
        ):
            event = {
                "schema_version": "1.0.0",
                "sequence": sequence,
                "action_id": f"LEGACY-SYNTHETIC-{sequence}",
                "review_id": record["review_id"],
                "evidence_id": record["source_reference"]["evidence_id"],
                "resulting_status": status,
                "reviewer_name": "Self-Declared Expert",
                "reviewer_role": role,
                "review_date": "2026-11-04",
                "source_locator": "Unverified synthetic locator",
                "rationale": "Unverified legacy synthetic entry.",
                "negative_evidence_assessment": "NOT_ASSESSED",
                "previous_event_sha256": previous,
            }
            event["event_sha256"] = hashlib.sha256(json.dumps(
                event, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False,
            ).encode("utf-8")).hexdigest()
            events.append(event)
            previous = event["event_sha256"]
        with tempfile.TemporaryDirectory(prefix=".stage-d-auth-", dir=STAGE_D / "tests") as temp:
            log = Path(temp) / "legacy.jsonl"
            log.write_text("".join(json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for item in events), encoding="utf-8")
            verified_events = verify_review_action_log(log, self.queue)
            coverage = build_coverage_dashboard(self.queue, verified_events)
            self.assertEqual(coverage["expert_accepted_count"], 0)
            self.assertEqual(coverage["source_verification_status_counts"]["NOT_PERFORMED"], len(self.queue["records"]))
            self.assertEqual(coverage["not_reviewed_record_count"], len(self.queue["records"]))
            with self.assertRaisesRegex(ReviewWorkflowError, "Legacy unauthenticated history"):
                self.call_append(log, self.action(), SyntheticProvider(roles=frozenset({"reviewer", "expert"})))

    def test_boolean_sequence_is_not_accepted_as_integer_audit_sequence(self):
        provider = SyntheticProvider()
        with tempfile.TemporaryDirectory(prefix=".stage-d-auth-", dir=STAGE_D / "tests") as temp:
            log = Path(temp) / "actions.jsonl"
            self.call_append(log, self.action(state="CONFLICT_REVIEW"), provider)
            event = json.loads(log.read_text(encoding="utf-8"))
            event["sequence"] = True
            log.write_text(json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ReviewWorkflowError, "Audit sequence is not contiguous"):
                verify_review_action_log(log, self.queue)

    def test_rehashed_identity_tampering_fails_provider_signature_check(self):
        provider = SyntheticProvider()
        with tempfile.TemporaryDirectory(prefix=".stage-d-auth-", dir=STAGE_D / "tests") as temp:
            log = Path(temp) / "actions.jsonl"
            self.call_append(log, self.action(state="CONFLICT_REVIEW"), provider)
            event = json.loads(log.read_text(encoding="utf-8"))
            event["reviewer_subject_id"] = "forged-subject"
            payload = {key: value for key, value in event.items() if key != "event_sha256"}
            event["event_sha256"] = hashlib.sha256(json.dumps(
                payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False,
            ).encode("utf-8")).hexdigest()
            log.write_text(json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ReviewWorkflowError, "identity signature is invalid"):
                verify_review_action_log(log, self.queue, identity_provider=provider)


if __name__ == "__main__":
    unittest.main()
