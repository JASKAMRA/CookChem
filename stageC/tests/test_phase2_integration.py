import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "stageC/phase2/generated"
RELEASE = ROOT / "stageC/releases/Phase2-v0.1.0"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


class Phase2IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.all_food = read_csv(DATA / "phase1b_integrated_all.csv")
        cls.ordinary = read_csv(DATA / "ordinary_food_concentrations.csv")
        cls.contextual = read_csv(DATA / "contextual_food_concentrations.csv")
        cls.ratios = read_csv(DATA / "experimental_apparent_concentration_ratios.csv")
        cls.applicability = read_csv(DATA / "retention_applicability_review.csv")
        cls.cooked = read_csv(DATA / "cooked_concentration_estimates.csv")
        cls.summary = json.loads((DATA / "phase2_integration_summary.json").read_text())

    def test_all_phase1b_rows_integrate_once_and_split_by_food_class(self):
        ids = [r["food_record_id"] for r in self.all_food]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(self.all_food), 584)
        self.assertEqual(len(self.ordinary), 335)
        self.assertEqual(len(self.contextual), 249)
        self.assertTrue(all(r["ordinary_dietary_eligible"] == "true" for r in self.ordinary))
        self.assertTrue(all(r["food_use_classification"] != "ordinary food" for r in self.contextual))

    def test_all_apparent_ratios_recompute_from_group_means(self):
        self.assertEqual(len(self.ratios), 117)
        for row in self.ratios:
            expected = float(row["cooked_group_mean"]) / float(row["raw_group_mean"])
            self.assertAlmostEqual(expected, float(row["apparent_concentration_ratio"]), places=7)
            self.assertIn("NOT_TOTAL_MASS_RETENTION", row["semantics"])

    def test_incompatible_retention_is_never_applied(self):
        self.assertEqual(len(self.applicability), 584)
        self.assertTrue(all(r["decision"].startswith("NOT_") for r in self.applicability))
        self.assertEqual(len(self.cooked), 0)

    def test_curcumin_cid_discrepancy_is_kept_with_manual_structure_link(self):
        accepted = read_csv(DATA / "accepted_identity_crosswalk.csv")
        curcumin = [r for r in accepted if r.get("stagea_compound_name") == "Curcumin"]
        self.assertEqual(len(curcumin), 1)
        self.assertEqual(curcumin[0]["accepted_identity_status"], "MATCH_AFTER_MANUAL_REVIEW_CID_WARNING")
        self.assertEqual(curcumin[0]["stagea_pubchem_cid"], "55215")

    def test_release_manifest_and_report_exist(self):
        self.assertTrue((RELEASE / "RELEASE_MANIFEST.json").is_file())
        self.assertTrue((RELEASE / "PHASE2_COMPLETION_REPORT.md").is_file())
        self.assertEqual(self.summary["phase2_exit_decision"], "COMPLETE_WITH_DOCUMENTED_LIMITATIONS")
        self.assertEqual(self.summary["observed_cooking_pairs_reviewed"], 117)
        self.assertEqual(self.summary["retention_candidates_reviewed"], 63)
        self.assertEqual(self.summary["compatibility_combinations_reviewed"], 22)
        self.assertEqual(self.summary["applicability_records_reviewed"], 584)
        self.assertEqual(self.summary["identity_crosswalk_records_reviewed"], 197)
        self.assertEqual(self.summary["cooked_concentration_estimates"], 0)


if __name__ == "__main__":
    unittest.main()
