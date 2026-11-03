import csv
import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGE = ROOT / "stageC"
REPORTS = STAGE / "reports" / "phase1b"
BATCH = REPORTS / "batches" / "batch_106_prunin_source_followup"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


class Phase1BBatch106Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.food_path = STAGE / "data/food_composition/food_composition.csv"
        cls.mapping_path = STAGE / "data/compound_food_mapping/compound_food_mapping.csv"
        cls.food = read_csv(cls.food_path)
        cls.mappings = read_csv(cls.mapping_path)
        cls.gaps = read_csv(REPORTS / "coverage_gap_register.csv")
        cls.coverage = read_csv(REPORTS / "COMPOUND_COVERAGE_REGISTER_2026-11-03.csv")
        cls.candidates = read_csv(REPORTS / "CANDIDATES.csv")
        cls.sources = read_csv(STAGE / "data/food_composition/source_registry.csv")
        cls.search = read_csv(REPORTS / "SEARCH_LOG.csv")
        cls.checkpoint = json.loads((REPORTS / "CHECKPOINTS.json").read_text(encoding="utf-8"))
        cls.results = json.loads((BATCH / "validation_and_test_results.json").read_text(encoding="utf-8"))

    def test_nine_orange_peel_values_preserved_as_held_candidate_rows(self):
        detail = read_csv(BATCH / "candidate_measurements.csv")
        self.assertEqual(len(detail), 9)
        self.assertEqual(
            [r["Original_Value"] for r in detail],
            [
                "149.44 ± 1.35", "141.97 ± 2.65", "138.38 ± 2.75", "120.88 ± 1.30",
                "124.48 ± 1.71", "137.31 ± 0.14", "123.74 ± 2.72", "176.0 ± 0.8", "102.7 ± 0.6",
            ],
        )
        self.assertTrue(all(r["Compound_ID"] == "MOL-V17-CID-92794" for r in detail))
        self.assertTrue(all("HELD_" in r["Candidate_Status"] for r in detail))
        self.assertTrue(all(r["Normalized_Value"] == "" for r in detail))
        central = {r["candidate_id"]: r for r in self.candidates}
        self.assertTrue(all(r["Candidate_Record_ID"] in central for r in detail))
        self.assertEqual(len([r for r in central if r.startswith("CAND-B106-PRUNIN-")]), 9)

    def test_no_held_prunin_value_entered_active_food_or_mapping_data(self):
        self.assertEqual(len(self.food), 546)
        self.assertEqual(len(self.mappings), 546)
        self.assertFalse(any(r["compound_id"] == "MOL-V17-CID-92794" for r in self.food))
        self.assertFalse(any(r["compound_id"] == "MOL-V17-CID-92794" for r in self.mappings))
        coverage = {r["Compound_ID"]: r for r in self.coverage}["MOL-V17-CID-92794"]
        self.assertEqual(coverage["Accepted_Quantitative_Coverage_Status"], "Not covered")
        self.assertIn("Table S1", coverage["Pending_Issues"])

    def test_authentic_standard_apple_source_is_visible_without_fabricated_values(self):
        sources = {r["source_url"]: r for r in self.sources}
        apple = sources["https://pmc.ncbi.nlm.nih.gov/articles/PMC8230845/"]
        self.assertIn("authentic prunin", apple["availability_status"].lower())
        self.assertIn("Table S1", apple["availability_status"])
        self.assertFalse(any(r["source_url"] == apple["source_url"] for r in self.food))
        self.assertIn("Table S1", (BATCH / "BATCH_106_PRUNIN_SOURCE_FOLLOWUP_REPORT.md").read_text(encoding="utf-8"))

    def test_source_registry_search_log_and_gap_disposition_are_current(self):
        self.assertIn("https://doi.org/10.3390/foods13081212", {r["source_url"] for r in self.sources})
        self.assertIn("https://doi.org/10.1016/j.lwt.2024.115950", {r["source_url"] for r in self.sources})
        self.assertEqual(sum(r["Compound_ID"] == "MOL-V17-CID-92794" and "batch 106" in r["search_query"].lower() for r in self.search), 3)
        gap = {r["Compound_ID"]: r for r in self.gaps}["MOL-V17-CID-92794"]
        self.assertEqual(gap["Last_Screen_Batch"], "batch_106_prunin_source_followup")
        self.assertIn("Table S1", gap["Next_Action"])

    def test_batch_checkpoint_hashes_and_stage_b_protection(self):
        self.assertEqual(self.checkpoint["checkpoint_id"], "Phase1B-2026-11-03-batch-106-prunin-source-followup")
        self.assertEqual(self.checkpoint["identity_complete_quantitative_compounds"], 100)
        self.assertEqual(self.checkpoint["active_food_records"], 546)
        self.assertEqual(self.checkpoint["active_mapping_rows"], 546)
        self.assertEqual(self.checkpoint["stage_b_snapshot_changes"], 0)
        hashes = self.checkpoint["sha256"]
        self.assertEqual(hashlib.sha256(self.food_path.read_bytes()).hexdigest(), hashes["food_composition.csv"])
        self.assertEqual(hashlib.sha256(self.mapping_path.read_bytes()).hexdigest(), hashes["compound_food_mapping.csv"])
        self.assertEqual(self.results["phase1_validation"]["orphans"], 0)
        self.assertEqual(self.results["mapping_rebuild"]["exact_row_order_match"], True)


if __name__ == "__main__":
    unittest.main()
