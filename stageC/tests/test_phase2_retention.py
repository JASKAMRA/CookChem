import sys
import unittest
import csv
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from stage_c.phase2_retention import (
    Phase2CompatibilityError,
    PercentInterval,
    adjust_concentration_interval,
    retention_from_loss,
)


class Phase2RetentionTests(unittest.TestCase):
    def test_loss_interval_complements_and_reverses_bounds(self):
        self.assertEqual(retention_from_loss("16", "34"), PercentInterval(Decimal("66"), Decimal("84")))

    def test_adjusts_concentration_interval_after_all_compatibility_gates(self):
        retention = retention_from_loss(16, 34)
        result = adjust_concentration_interval(
            "100", retention,
            exact_compound_match=True,
            food_matrix_match=True,
            cooking_condition_match=True,
            measurement_basis_compatible=True,
        )
        self.assertEqual(result.low, Decimal("66"))
        self.assertEqual(result.high, Decimal("84"))

    def test_incompatible_evidence_is_blocked(self):
        with self.assertRaisesRegex(Phase2CompatibilityError, "food matrix"):
            adjust_concentration_interval(
                100, retention_from_loss(10, 20),
                exact_compound_match=True,
                food_matrix_match=False,
                cooking_condition_match=True,
                measurement_basis_compatible=True,
            )

    def test_invalid_percentages_are_rejected(self):
        for bounds in [(-1, 5), (5, 101), (20, 10)]:
            with self.subTest(bounds=bounds), self.assertRaises(Phase2CompatibilityError):
                retention_from_loss(*bounds)

    def test_negative_concentration_is_rejected(self):
        with self.assertRaises(Phase2CompatibilityError):
            adjust_concentration_interval(
                -1, retention_from_loss(10, 20),
                exact_compound_match=True,
                food_matrix_match=True,
                cooking_condition_match=True,
                measurement_basis_compatible=True,
            )

    def test_primary_curcumin_pairs_are_ingested_with_concentration_ratio_semantics(self):
        path = Path(__file__).resolve().parents[1] / "phase2/data/observed_cooking_pairs.csv"
        with path.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 117)
        boil_1 = next(row for row in rows if row["source_stagea_record_id"] == "R227")
        self.assertEqual(boil_1["stageb_compound_id"], "MOL-16B10569D6F0625E")
        self.assertEqual(boil_1["raw_mean_mg_per_g"], "113.92")
        self.assertEqual(boil_1["cooked_mean_mg_per_g"], "125.33")
        self.assertEqual(boil_1["concentration_ratio_percent"], "110.02")
        self.assertEqual(boil_1["ratio_semantics"], "concentration_ratio_not_mass_retention")
        self.assertIn("PMC10453412", boil_1["source_url"])
        bisdemethoxy = next(row for row in rows if row["source_stagea_record_id"] == "R225")
        self.assertEqual(bisdemethoxy["stageb_compound_id"], "")
        pumpkin = next(row for row in rows if row["source_doi"] == "10.3390/molecules31162740")
        self.assertEqual(pumpkin["measurement_unit"], "mg/100 g dry weight")
        self.assertEqual(pumpkin["stageb_compound_id"], "")
        self.assertEqual(sum(row["source_doi"] == "10.3390/molecules31162740" for row in rows), 84)
        stagea = Path(__file__).resolve().parents[2] / "stageA/input/cookchem_molecular_retention_preprocessed.csv"
        with stagea.open(encoding="utf-8-sig", newline="") as source:
            stagea_rows = {item["Record_ID"]: item for item in csv.DictReader(source)}
        for row in rows:
            with self.subTest(pair=row["pair_id"]):
                self.assertAlmostEqual(float(row["concentration_ratio_percent"]), float(stagea_rows[row["source_stagea_record_id"]]["Retention_Final"]), delta=0.011)

    def test_curcumin_cid_discrepancy_is_resolved_by_stable_id_and_structure(self):
        path = Path(__file__).resolve().parents[1] / "phase2/data/stagea_stageb_identity_crosswalk.csv"
        with path.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        curcumin = next(row for row in rows if row["stagea_group_id"] == "MOL-16B10569D6F0625E")
        self.assertEqual(curcumin["crosswalk_status"], "STABLE_ID_STRUCTURE_MATCH_CID_DISCREPANCY")
        self.assertEqual(curcumin["stageb_compound_id_candidate"], "MOL-16B10569D6F0625E")
        self.assertEqual(curcumin["stagea_pubchem_cid"], "55215")
        self.assertEqual(curcumin["stagea_pubchem_cid_resolved"], "")

    def test_all_non_strict_identity_candidates_have_documented_dispositions(self):
        path = Path(__file__).resolve().parents[1] / "phase2/data/identity_candidate_review.csv"
        with path.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 45)
        self.assertTrue(all(row["review_decision"].startswith("PENDING_") for row in rows))
        self.assertEqual(sum(row["review_decision"] == "PENDING_INTRA_GROUP_CID_CONFLICT" for row in rows), 9)

    def test_model_candidate_checksum_and_runtime_gates_are_visible(self):
        summary_path = Path(__file__).resolve().parents[1] / "phase2/data/phase2_intake_summary.json"
        import json
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        self.assertTrue(summary["stageb_selected_model_candidate_found"])
        self.assertTrue(summary["stageb_selected_model_sha256_matches_manifest"])
        self.assertFalse(summary["stageb_selected_model_input_sha256_matches_current_stagea"])
        self.assertEqual(summary["stageb_model_inference_readiness"], "BLOCKED_CHECKSUM_OR_RUNTIME_GATE")


if __name__ == "__main__":
    unittest.main()
