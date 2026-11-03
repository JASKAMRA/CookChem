import csv
import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGE = ROOT / "stageC"
REPORTS = STAGE / "reports" / "phase1b"
PENDING_TARGETS = {
    "MOL-V14-CID-33258",   # Allura Red AC
    "MOL-V15-CID-19700",   # Brilliant Blue FCF
    "MOL-V15-CID-19118",   # Azorubine
    "MOL-V15-CID-30231",   # Neohesperidin dihydrochalcone
    "MOL-V15-CID-164825",  # Tartrazine
}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


class Phase1BContinuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.food = read_csv(STAGE / "data/food_composition/food_composition.csv")
        cls.mappings = read_csv(STAGE / "data/compound_food_mapping/compound_food_mapping.csv")
        cls.identity = read_csv(STAGE / "data/stage_b_snapshot_20261103/identity_structure_audit.csv")
        cls.universe = read_csv(REPORTS / "COMPOUND_COVERAGE_REGISTER_2026-11-03.csv")
        cls.search = read_csv(REPORTS / "SEARCH_LOG.csv")
        cls.pending = read_csv(REPORTS / "PENDING_IDENTITY_CANDIDATES.csv")
        cls.checkpoint = json.loads((REPORTS / "CHECKPOINTS.json").read_text(encoding="utf-8"))
        cls.validation = json.loads((STAGE / "reports/validation/phase1_validation.json").read_text(encoding="utf-8"))
        cls.batch102 = STAGE / "reports/phase1b/batches/batch_102_scientific_coverage"
        cls.batch103 = STAGE / "reports/phase1b/batches/batch_103_final_screen"

    def test_accepted_batch102_values_have_complete_identity_and_source_basis(self):
        accepted = read_csv(self.batch102 / "accepted_rows.csv")
        by_id = {r["food_record_id"]: r for r in self.food}
        self.assertEqual(len(accepted), 2)
        self.assertEqual(len(self.food), 546)
        self.assertEqual(len(self.mappings), 546)
        self.assertEqual({r["food_record_id"] for r in accepted} - set(by_id), set())
        expected = {
            "APIGETRIN-FOODS2021-LAMBSLETTUCE-STANDARD": ("0.012", "µg/g", "fresh weight (FW)"),
            "MYRICITRIN-PLANTS2024-SPINACH": (
                "398.2", "mg/kg", "as-analyzed homogenized food-sample mass; moisture state and correction not reported"
            ),
        }
        for record_id, values in expected.items():
            self.assertEqual(
                (by_id[record_id]["reported_concentration"], by_id[record_id]["reported_unit"], by_id[record_id]["moisture_basis"]),
                values,
            )
            self.assertEqual(by_id[record_id]["source_verification_status"], "full-text verified")
        complete_ids = {r["Compound_ID"] for r in self.identity if r["Status"] == "Complete"}
        accepted_ids = {r["compound_id"] for r in accepted}
        self.assertTrue(accepted_ids <= complete_ids)
        map_by_record = {r["food_record_id"]: r for r in self.mappings}
        self.assertTrue(all(map_by_record[r["food_record_id"]]["quantitative_data_available"] == "true" for r in accepted))

    def test_all_stage_b_ids_screened_and_coverage_is_identity_gated(self):
        ids = {r["Compound_ID"] for r in self.identity}
        searched = {r["Compound_ID"] for r in self.search}
        self.assertEqual(len(ids), 143)
        self.assertEqual(searched, ids)
        self.assertEqual(len({r["Compound_ID"] for r in self.universe}), 143)
        self.assertEqual(len([r for r in self.universe if r["Identity_Complete_Quantitative_Eligible"] == "true"]), 100)
        self.assertEqual(sum(r["Status"] == "Complete" for r in self.identity), 107)
        self.assertEqual(sum(r["Status"] != "Complete" for r in self.identity), 36)
        self.assertEqual(self.checkpoint["research_screened_fraction"], "143/143")
        self.assertEqual(self.checkpoint["identity_complete_quantitative_compounds"], 100)
        self.assertFalse(self.checkpoint["target"]["achieved"])
        self.assertEqual(self.checkpoint["target"]["additional_compounds_needed"], 30)

    def test_batch103_candidates_remain_unaccepted_and_missing_is_not_zero(self):
        batch_rows = read_csv(self.batch103 / "pending_identity_candidates.csv")
        self.assertEqual(len(batch_rows), 13)
        numeric = [r for r in batch_rows if r["Original_Value"]]
        self.assertEqual(len(numeric), 12)
        self.assertEqual({r["Compound_ID"] for r in batch_rows}, PENDING_TARGETS)
        active_ids = {r["compound_id"] for r in self.food}
        self.assertFalse(PENDING_TARGETS & active_ids)
        nhdc = [r for r in batch_rows if r["Compound_ID"] == "MOL-V15-CID-30231"]
        self.assertEqual(len(nhdc), 1)
        self.assertEqual(nhdc[0]["Original_Value"], "")
        self.assertEqual(nhdc[0]["Normalized_Value"], "")
        self.assertIn("do not replace with LOQ", nhdc[0]["Limitations"])

    def test_pending_candidate_history_and_source_rows_are_preserved(self):
        self.assertEqual(len(self.pending), 42)
        self.assertEqual(sum(bool(r["Original_Value"]) for r in self.pending), 39)
        candidate_ids = [r["Candidate_Record_ID"] for r in self.pending]
        self.assertEqual(len(candidate_ids), len(set(candidate_ids)))
        self.assertEqual({r["Batch"] for r in self.pending}, {"102", "103"})
        proposals = read_csv(REPORTS / "IDENTITY_ADJUDICATION_PROPOSALS_2026-11-03.csv")
        self.assertEqual(len(proposals), 36)
        self.assertTrue(all(r["Current_Identity_Status"] != "Complete" for r in proposals))
        self.assertTrue(all(r["Recommended_Decision"] == "requires specialist review; no change proposed" for r in proposals))

    def test_independent_full_mapping_rebuild_and_checkpoint_hashes(self):
        rebuilt = read_csv(self.batch103 / "mapping_rebuild.csv")
        self.assertEqual(self.mappings[:len(rebuilt)], rebuilt)
        batch105_rebuild = read_csv(REPORTS / "batches/batch_105_targeted_source_followup/mapping_rebuild.csv")
        self.assertEqual(self.mappings, batch105_rebuild)
        self.assertEqual(len(batch105_rebuild), 546)
        cp_hashes = self.checkpoint["sha256"]
        for rel, key in [
            ("data/food_composition/food_composition.csv", "food_composition.csv"),
            ("data/compound_food_mapping/compound_food_mapping.csv", "compound_food_mapping.csv"),
        ]:
            digest = hashlib.sha256((STAGE / rel).read_bytes()).hexdigest()
            self.assertEqual(digest, cp_hashes[key])
        self.assertEqual(self.validation["status"], "PASS")
        self.assertEqual(self.validation["stage_b_snapshot_changes"], [])
        self.assertEqual(self.validation["food_errors"], [])
        self.assertEqual(self.validation["mapping_errors"], [])


if __name__ == "__main__":
    unittest.main()
