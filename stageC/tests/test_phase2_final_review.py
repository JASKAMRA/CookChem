from __future__ import annotations

import csv
import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve()
if HERE.parents[1].name.startswith("Phase2-v0.3."):
    RELEASE = HERE.parents[1]
else:
    RELEASE = HERE.parents[1] / "releases" / "Phase2-v0.3.0"


def read_csv(relative: str) -> list[dict[str, str]]:
    with (RELEASE / relative).open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


class Phase2FinalReviewTests(unittest.TestCase):
    def test_frozen_pair_scope_and_independent_recalculation(self):
        pairs = read_csv("data/source_observed_cooking_pairs.csv")
        audit = read_csv("data/source_pair_audit_2026-11-03.csv")
        self.assertEqual(len(pairs), 117)
        self.assertEqual(len(audit), 117)
        self.assertEqual(len({row["pair_id"] for row in pairs}), 117)
        self.assertTrue(all(not row["audit_error_codes"] for row in audit))
        self.assertEqual(Counter(row["source_verification_status"] for row in audit), {
            "VERIFIED_AGAINST_PRIMARY_TABLE": 84,
            "VERIFIED_WITH_BASIS_LIMITATION": 33,
        })
        turmeric = [row for row in pairs if row["food_matrix"] == "Curcuma longa rhizome"]
        self.assertEqual(len(turmeric), 33)
        self.assertTrue(all(row["measurement_unit"] == "mg/g plant material" for row in turmeric))
        for row in audit:
            expected = float(row["cooked_mean_value"]) / float(row["raw_mean_value"])
            self.assertAlmostEqual(float(row["independently_recalculated_ratio"]), expected, places=7)

    def test_all_candidate_reviews_are_classified_and_nonnumeric(self):
        rows = read_csv("data/source_condition_level_retention_candidates_2026-11-03.csv")
        self.assertEqual(len(rows), 63)
        self.assertEqual(Counter(row["final_classification"] for row in rows), {
            "PENDING_SOURCE_BASIS": 30,
            "PENDING_MATRIX_COMPATIBILITY": 33,
        })
        self.assertTrue(all(row["reviewed"] == "true" and row["evidence_reference"] for row in rows))
        self.assertTrue(all(row["numerical_use_allowed"] == "false" and row["yield_mass_balance_status"] == "NOT_REPORTED" for row in rows))
        self.assertTrue(all(not row["calculated_phase1b_cooked_concentration"] for row in rows))

    def test_all_compatibility_rows_have_final_scientific_dispositions(self):
        rows = read_csv("data/retention_compatibility_matrix_2026-11-03.csv")
        self.assertEqual(len(rows), 22)
        self.assertEqual(Counter(row["final_status"] for row in rows), {
            "PENDING_SOURCE_BASIS": 10,
            "PENDING_MATRIX_COMPATIBILITY": 11,
            "QUALITATIVE_ONLY": 1,
        })
        self.assertTrue(all(row["final_reason"] and row["evidence_references"] for row in rows))
        self.assertTrue(all(row["numerical_application_allowed"] == "false" for row in rows))

    def test_all_applicability_rows_are_reviewed(self):
        rows = read_csv("data/retention_applicability_review.csv")
        self.assertEqual(len(rows), 584)
        self.assertTrue(all(row["retention_scope_reviewed"] == "true" for row in rows))
        self.assertEqual(Counter(row["final_status"] for row in rows), {
            "NO_LINKED_RETENTION_EVIDENCE": 569,
            "PENDING_SOURCE_BASIS_AND_MATRIX_COMPATIBILITY": 10,
            "PENDING_MATRIX_COMPATIBILITY": 1,
            "QUALITATIVE_ONLY": 4,
        })
        self.assertTrue(all(row["final_reason"] and row["review_evidence_refs"] for row in rows))

    def test_all_identity_crosswalk_rows_reviewed_without_forced_join(self):
        rows = read_csv("data/identity_crosswalk_final_review.csv")
        self.assertEqual(len(rows), 197)
        self.assertEqual(Counter(row["final_review_status"] for row in rows), {
            "ACCEPTED_STRICT_MATCH": 19,
            "ACCEPTED_MANUAL_MATCH_WITH_CID_WARNING": 1,
            "PENDING_STRUCTURE_EQUIVALENCE_REVIEW": 27,
            "PENDING_NAME_AND_STRUCTURE_REVIEW": 9,
            "NEEDS_MANUAL_SOURCE_ADJUDICATION": 9,
            "NO_STAGEB_CID_MATCH": 127,
            "NO_CID": 5,
        })
        self.assertEqual(sum(row["join_allowed"] == "true" for row in rows), 20)
        self.assertTrue(all(row["final_review_reason"] and row["identity_evidence_reference"] for row in rows))

    def test_zero_cooked_estimates_and_release_integrity(self):
        cooked = read_csv("data/cooked_concentration_estimates.csv")
        self.assertEqual(cooked, [])
        release = json.loads((RELEASE / "RELEASE.json").read_text(encoding="utf-8"))
        self.assertEqual(release["status"], "COMPLETE_WITH_DOCUMENTED_LIMITATIONS")
        self.assertFalse(release["stage_a_model_inference_performed"])
        self.assertEqual(release["cooked_concentration_estimates"], 0)
        manifest = json.loads((RELEASE / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
        manifest_bytes = (RELEASE / "RELEASE_MANIFEST.json").read_bytes()
        expected = (RELEASE / "RELEASE_MANIFEST.sha256").read_text(encoding="utf-8").split()[0]
        self.assertEqual(hashlib.sha256(manifest_bytes).hexdigest(), expected)
        for relative, digest in manifest["file_hashes"].items():
            self.assertEqual(hashlib.sha256((RELEASE / relative).read_bytes()).hexdigest(), digest, relative)
        self.assertEqual(len(release["excluded_unavailable_artifacts"]), 2)
        for item in release["excluded_unavailable_artifacts"]:
            self.assertFalse((RELEASE / item["path"]).exists())
            self.assertTrue(item["reason"])


if __name__ == "__main__":
    unittest.main()
