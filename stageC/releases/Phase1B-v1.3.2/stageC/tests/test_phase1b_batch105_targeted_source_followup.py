import csv
import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGE = ROOT / "stageC"
REPORTS = STAGE / "reports" / "phase1b"
BATCH = REPORTS / "batches" / "batch_105_targeted_source_followup"
BAICALIN_VALUES = {
    "BAICALIN-HHT2025-MICROWAVE_ROASTING": ("1.11", "0.08", "1110.00"),
    "BAICALIN-HHT2025-ELECTRIC_ROASTING": ("2.79", "0.22", "2790.00"),
    "BAICALIN-HHT2025-CHARCOAL_ROASTING": ("3.11", "0.09", "3110.00"),
    "BAICALIN-HHT2025-STEAM_ROASTING": ("1.10", "0.16", "1100.00"),
    "BAICALIN-HHT2025-NATURAL_DRYING": ("1.05", "0.03", "1050.00"),
}
PRUNIN_VALUES = [
    "2.05 ± 0.00", "3.45 ± 0.04", "2.47 ± 0.01", "2.11 ± 0.00",
    "2.13 ± 0.04", "2.95 ± 0.01", "2.32 ± 0.04", "2.11 ± 0.11",
    "3.13", "3.14", "3.15", "3.12", "3.05",
]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


class Phase1BBatch105Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.food = read_csv(STAGE / "data/food_composition/food_composition.csv")
        cls.mappings = read_csv(STAGE / "data/compound_food_mapping/compound_food_mapping.csv")
        cls.coverage = read_csv(REPORTS / "COMPOUND_COVERAGE_REGISTER_2026-11-03.csv")
        cls.gaps = read_csv(REPORTS / "coverage_gap_register.csv")
        cls.pending = read_csv(REPORTS / "PENDING_IDENTITY_CANDIDATES.csv")
        cls.checkpoint = json.loads((REPORTS / "CHECKPOINTS.json").read_text(encoding="utf-8"))
        cls.baseline = json.loads((BATCH / "baseline.json").read_text(encoding="utf-8"))

    def test_five_baicalin_table_values_ingested_through_existing_pipeline(self):
        by_id = {r["food_record_id"]: r for r in self.food}
        mapping_by_food = {r["food_record_id"]: r for r in self.mappings}
        self.assertEqual(len(self.food), 546)
        self.assertEqual(len(self.mappings), 546)
        for rid, (mean, sd, normalized) in BAICALIN_VALUES.items():
            record = by_id[rid]
            mapping = mapping_by_food[rid]
            self.assertEqual(record["compound_id"], "MOL-V10-64982")
            self.assertEqual(record["compound_name"], "Baicalin")
            self.assertEqual(record["reported_concentration"], mean)
            self.assertEqual(record["reported_unit"], "mg/g")
            self.assertEqual(record["normalized_concentration"], normalized)
            self.assertEqual(record["normalized_unit"], "mg/kg")
            self.assertIn(f"±{sd}", record["uncertainty_notes"])
            self.assertEqual(record["food_use_classification"], "food ingredient")
            self.assertIn("as-analyzed", record["moisture_basis"])
            self.assertNotIn("fresh weight", record["moisture_basis"].lower())
            self.assertNotIn("dry weight", record["moisture_basis"].lower())
            self.assertEqual(record["source_verification_status"], "full-text verified")
            self.assertEqual(mapping["compound_id"], "MOL-V10-64982")
            self.assertIn(mapping["mapping_status"], {"Exact identity match", "Verified synonym match", "Structure-supported match"})
            self.assertEqual(mapping["quantitative_data_available"], "true")

    def test_coverage_increased_by_one_compound_and_seven_complete_gaps_remain(self):
        coverage = {r["Compound_ID"]: r for r in self.coverage}
        baicalin = coverage["MOL-V10-64982"]
        self.assertEqual(baicalin["Identity_Audit_Status"], "Complete")
        self.assertEqual(baicalin["Accepted_Quantitative_Coverage_Status"], "Covered")
        self.assertEqual(baicalin["Food_Record_Count"], "5")
        self.assertEqual(baicalin["Mapping_Row_Count"], "5")
        complete_covered = [r for r in self.coverage if r["Identity_Audit_Status"] == "Complete" and r["Accepted_Quantitative_Coverage_Status"] == "Covered"]
        self.assertEqual(len(complete_covered), 100)
        uncovered_complete = [r for r in self.coverage if r["Identity_Audit_Status"] == "Complete" and r["Accepted_Quantitative_Coverage_Status"] != "Covered"]
        self.assertEqual(len(uncovered_complete), 7)
        self.assertEqual(self.checkpoint["target"]["additional_compounds_needed"], 30)
        self.assertFalse(self.checkpoint["target"]["achieved"])

    def test_prunin_hydrolysis_yields_are_preserved_as_held_candidates(self):
        candidates = read_csv(BATCH / "candidate_measurements.csv")
        self.assertEqual(len(candidates), 13)
        self.assertEqual([r["Original_Value"] for r in candidates], PRUNIN_VALUES)
        self.assertTrue(all(r["Candidate_Status"] == "HELD_PROCESS_GENERATED_HYDROLYSIS_YIELD" for r in candidates))
        self.assertTrue(all("starting freeze-dried pomace" in r["Measurement_Basis"] and "not native food concentration" in r["Measurement_Basis"] for r in candidates))
        self.assertFalse(any(r["compound_id"] == "MOL-V17-CID-92794" for r in self.food))
        central = [r for r in read_csv(REPORTS / "CANDIDATES.csv") if r["candidate_id"].startswith("CAND-B105-PRUNIN-SW-")]
        self.assertEqual(len(central), 13)

    def test_all_42_pending_candidates_and_36_identity_proposals_reconcile(self):
        reviewed = read_csv(BATCH / "pending_candidate_review.csv")
        identity = read_csv(BATCH / "identity_review_36.csv")
        self.assertEqual(len(self.pending), 42)
        self.assertEqual(len(reviewed), 42)
        self.assertEqual(sum(bool(r["Original_Value"]) for r in self.pending), 39)
        self.assertTrue(all(r["StageB_Identity_Status"] != "Complete" for r in reviewed))
        self.assertTrue(all(r["B105_Review_Decision"] == "RETAIN_PENDING_IDENTITY; NOT PROMOTABLE IN STAGE C" for r in reviewed))
        self.assertEqual(len(identity), 36)
        self.assertTrue(all(r["Batch_105_Adjudication_Outcome"] == "SPECIALIST_REVIEW_REQUIRED" for r in identity))
        self.assertTrue(all(r["Proposed_StageB_Change"] == "None; StageB_FINALIZED remains read-only" for r in identity))

    def test_baseline_batch104_and_protected_stage_b_snapshot_are_preserved(self):
        self.assertEqual(self.baseline["baseline_counts"]["food_records"], 541)
        self.assertEqual(self.baseline["baseline_counts"]["mapping_rows"], 541)
        self.assertEqual(self.baseline["baseline_counts"]["identity_complete_gaps"], 8)
        self.assertTrue(all(self.baseline["checkpoint_hashes_match_actual"].values()))
        self.assertEqual(self.checkpoint["active_food_records"], 546)
        self.assertEqual(self.checkpoint["active_mapping_rows"], 546)
        self.assertEqual(self.checkpoint["stage_b_snapshot_changes"], 0)
        self.assertEqual(self.checkpoint["batch_105"]["new_accepted_unique_compounds"], 1)

    def test_batch_has_a_complete_traceable_author_data_request_draft(self):
        draft = (BATCH / "author_data_request_2026_huangqin_tea.txt").read_text(encoding="utf-8")
        self.assertIn("10.1016/j.lwt.2026.119022", draft)
        self.assertIn("baicalin and wogonoside", draft)
        self.assertIn("not sent", draft.lower())
        sources = read_csv(STAGE / "data/food_composition/source_registry.csv")
        self.assertIn("https://pmc.ncbi.nlm.nih.gov/articles/PMC12657378/", {r["source_url"] for r in sources})


if __name__ == "__main__":
    unittest.main()
