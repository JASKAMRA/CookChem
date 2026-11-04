from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

STAGE_D = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STAGE_D / "scripts"))
from run_phase7_benchmark import run_benchmark  # noqa: E402
from stage_d.schema_validation import SchemaValidationResult  # noqa: E402


def case(case_id, evidence_level, outcome):
    return {
        "schema_version": "1.0.0", "assessment_id": case_id,
        "evidence_level": evidence_level, "evidence_strength": "single_source",
        "source_review_status": "full_text_reviewed", "source_identity_status": "verified",
        "mechanistic_plausibility": "not_assessed", "experimental_context": "in_vitro",
        "outcome": outcome, "exposure_comparability": "not_assessed",
        "dietary_exposure_status": "unavailable", "uncertainty_status": "material",
        "conflict_status": "none_known", "human_relevance_status": "preclinical_only",
        "source_reference": "synthetic://source#table1", "dietary_exposure_reference": "",
        "comparability_review_reference": "",
        "expert_review": {"status": "not_reviewed", "adjudication": "not_assessed", "reviewer_reference": "", "rationale": ""},
    }


def inputs():
    cases = []
    for i, (level, outcome, refcat) in enumerate([
        ("none", "not_reported", "INSUFFICIENT_EVIDENCE"),
        ("mechanistic_only", "positive", "MECHANISTIC_EVIDENCE_ONLY"),
    ], 1):
        case_id = f"SYN-P7-{i}"
        cases.append({"case_id": case_id, "input": case(case_id, level, outcome),
                      "reference_category": refcat, "independent_review_refs": ["synthetic-review-1", "synthetic-review-2"],
                      "adjudication_reference": "synthetic-adjudication-record"})
    case_set = {"schema_version": "1.0.0", "case_set_id": "SYNTHETIC-ONLY", "protocol_version": "1.0.0", "cases": cases}
    approval = {"status": "APPROVED", "approval_reference": "synthetic-only", "protocol_version": "1.0.0",
                "approver_identity": "synthetic-owner", "approver_role": "synthetic-owner",
                "approval_date": "2026-11-05", "signature_reference": "synthetic-approval-record",
                "case_set_sha256": "a" * 64, "implementation_release_id": "synthetic-build",
                "dependency_lock_sha256": "c" * 64,
                "thresholds": {"minimum_exact_agreement": 1.0, "minimum_coverage": 0.0,
                               "minimum_per_category_agreement": {"INSUFFICIENT_EVIDENCE": 1.0}},
                "abstention_categories": ["REQUIRES_EXPERT_REVIEW"]}
    return case_set, approval


def run(case_set, approval, *, case_digest="a" * 64, approval_digest="b" * 64, schema="synthetic"):
    return run_benchmark(case_set, approval, case_set_sha256=case_digest,
                         approval_sha256=approval_digest, schema_text=schema)


class Phase7BenchmarkRunnerTests(unittest.TestCase):
    def test_missing_owner_approval_is_rejected(self):
        case_set, approval = inputs()
        approval["status"] = "PENDING"
        with self.assertRaisesRegex(ValueError, "owner-approved protocol"):
            run(case_set, approval)

    def test_synthetic_fixture_metrics_are_deterministic_and_not_acceptance(self):
        case_set, approval = inputs()
        approved_validator = SchemaValidationResult("VALID", (), "synthetic-test-only")
        with patch("run_phase7_benchmark.validate_draft_2020_12", return_value=approved_validator):
            output = run(case_set, approval)
            rerun = run(case_set, approval)
        self.assertEqual(output["case_count"], 2)
        self.assertEqual(output["exact_agreement"], 1.0)
        self.assertEqual(output["coverage"], 1.0)
        self.assertTrue(output["thresholds_met"])
        self.assertEqual(output["scientific_acceptance"], "NOT_GRANTED")
        self.assertEqual(output["run_status"], "RESULTS_PENDING_INDEPENDENT_REVIEW")
        self.assertEqual(output["approval_sha256_exact_bytes"], "b" * 64)
        self.assertEqual(output, rerun)

    def test_case_digest_mismatch_and_duplicate_reviewers_are_rejected(self):
        case_set, approval = inputs()
        with self.assertRaisesRegex(ValueError, "SHA-256 does not match"):
            run(case_set, approval, case_digest="c" * 64)
        case_set, approval = inputs()
        case_set["cases"][0]["independent_review_refs"] = ["same", "same"]
        approved_validator = SchemaValidationResult("VALID", (), "synthetic-test-only")
        with patch("run_phase7_benchmark.validate_draft_2020_12", return_value=approved_validator):
            with self.assertRaisesRegex(ValueError, "complete independent adjudication"):
                run(case_set, approval)

    def test_incomplete_hash_or_case_set_type_is_rejected(self):
        case_set, approval = inputs()
        with self.assertRaisesRegex(ValueError, "valid exact-byte approval SHA-256"):
            run(case_set, approval, approval_digest="short")
        with self.assertRaisesRegex(ValueError, "Case set must be a JSON object"):
            run(None, approval)

    def test_malformed_unhashable_reference_category_is_rejected_cleanly(self):
        case_set, approval = inputs()
        case_set["cases"][0]["reference_category"] = ["not", "a", "category"]
        approved_validator = SchemaValidationResult("VALID", (), "synthetic-test-only")
        with patch("run_phase7_benchmark.validate_draft_2020_12", return_value=approved_validator):
            with self.assertRaisesRegex(ValueError, "complete independent adjudication"):
                run(case_set, approval)

    def test_duplicate_json_keys_are_rejected_by_strict_loader(self):
        from run_phase7_benchmark import _load_json_object

        with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
            _load_json_object(b'{"case_set_id":"first","case_set_id":"second"}', "Case set")


if __name__ == "__main__":
    unittest.main()
