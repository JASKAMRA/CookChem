import csv
import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGE = ROOT / "stageC"
REPORTS = STAGE / "reports" / "phase1b"
GAPS = {
    "MOL-V10-5281605",
    "MOL-V10-64982",
    "MOL-V10-5281697",
    "MOL-V10-5281703",
    "MOL-V10-5320315",
    "MOL-V10-2825024",
    "MOL-V10-3084961",
    "MOL-V17-CID-92794",
}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


class Phase1BBatch104GapReauditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = REPORTS / "batches" / "batch_104_eligible_gap_reaudit"
        cls.screening = read_csv(cls.batch / "screening_matrix.csv")
        cls.assessments = read_csv(cls.batch / "source_assessment.csv")
        cls.gaps = read_csv(REPORTS / "coverage_gap_register.csv")
        cls.coverage = read_csv(REPORTS / "COMPOUND_COVERAGE_REGISTER_2026-11-03.csv")
        cls.search = read_csv(REPORTS / "SEARCH_LOG.csv")
        cls.sources = read_csv(STAGE / "data/food_composition/source_registry.csv")
        cls.food = read_csv(STAGE / "data/food_composition/food_composition.csv")
        cls.mappings = read_csv(STAGE / "data/compound_food_mapping/compound_food_mapping.csv")
        cls.checkpoint = json.loads((REPORTS / "CHECKPOINTS.json").read_text(encoding="utf-8"))
        cls.batch105_baseline = json.loads((REPORTS / "batches/batch_105_targeted_source_followup/baseline.json").read_text(encoding="utf-8"))

    def test_exact_gaps_were_researched_without_accepting_unverified_measurements(self):
        batch_rows = [r for r in self.search if r["screening_decision"] == "NO_NEW_QUALIFYING_MEASUREMENT" and r["candidate_publications"] == "See batches/batch_104_eligible_gap_reaudit/source_assessment.csv"]
        batch_ids = {r["Compound_ID"] for r in batch_rows}
        self.assertEqual(batch_ids, GAPS)
        self.assertEqual(len(batch_rows), 10)
        self.assertEqual(len({(r["Compound_ID"], r["search_query"]) for r in batch_rows}), 10)
        followups = [r for r in batch_rows if "2026" in r["search_query"] and "widely targeted metabolomics" in r["search_query"]]
        self.assertEqual({r["Compound_ID"] for r in followups}, {"MOL-V10-64982", "MOL-V10-3084961"})
        self.assertTrue(all("sample-level calibrated concentration" in r["results_identified"] and "on request" in r["results_identified"] for r in followups))
        self.assertEqual({r["Compound_ID"] for r in self.screening}, GAPS)
        self.assertTrue(all(r["New_Quantitative_Candidates"] == "0" for r in self.screening))
        self.assertTrue(all(r["Accepted_Record_Change"] == "none" for r in self.screening))
        self.assertTrue(all(r["Decision"] == "NO_NEW_QUALIFYING_MEASUREMENT" for r in self.screening))
        self.assertEqual(len({r["search_query"] for r in batch_rows}), 10)

    def test_all_gaps_remain_open_with_targeted_source_traceability(self):
        gap_rows = {r["Compound_ID"]: r for r in self.gaps if r["Compound_ID"] in GAPS}
        coverage_rows = {r["Compound_ID"]: r for r in self.coverage if r["Compound_ID"] in GAPS}
        self.assertEqual(set(gap_rows), GAPS)
        self.assertEqual(set(coverage_rows), GAPS)
        known_urls = {r["source_url"] for r in self.sources}
        for cid, row in gap_rows.items():
            if cid == "MOL-V10-64982":
                self.assertEqual(coverage_rows[cid]["Accepted_Quantitative_Coverage_Status"], "Covered")
            else:
                self.assertEqual(coverage_rows[cid]["Accepted_Quantitative_Coverage_Status"], "Not covered")
            # Later batches may advance the live disposition. Batch 104's original
            # screening decisions and gap state are preserved in its own artifacts.
            self.assertTrue(row["Last_Screen_Batch"].startswith("batch_"))
            self.assertTrue(row["Last_Decision"])
            refs = set(coverage_rows[cid]["Relevant_Source_References"].split("; "))
            self.assertTrue(refs)
        self.assertEqual(set(self.batch105_baseline["baseline_gap_ids"]), GAPS)
        self.assertTrue(all(x["coverage_status"] == "No accepted quantitative mapping" for x in self.batch105_baseline["baseline_gap_statuses"].values()))
        new_refs = {
            cid: set(row["Relevant_Source_References"].split("; "))
            for cid, row in coverage_rows.items()
        }
        self.assertTrue({
            "https://doi.org/10.1016/j.chmed.2018.09.005",
            "https://pubmed.ncbi.nlm.nih.gov/33048099/",
            "https://doi.org/10.1016/j.lwt.2026.119022",
            "https://doi.org/10.48130/BPR-2023-0031",
        } <= new_refs["MOL-V10-64982"] & known_urls)
        self.assertIn("https://doi.org/10.1016/j.lwt.2026.119022", new_refs["MOL-V10-3084961"] & known_urls)
        prunin_refs = set(coverage_rows["MOL-V17-CID-92794"]["Relevant_Source_References"].split("; "))
        self.assertTrue({
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC11301317/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC6696472/",
            "https://doi.org/10.1021/jf00035a021",
        } <= prunin_refs & known_urls)
        methoxy_refs = set(coverage_rows["MOL-V10-2825024"]["Relevant_Source_References"].split("; "))
        self.assertIn("https://pubchem.ncbi.nlm.nih.gov/compound/2825024", methoxy_refs & known_urls)

    def test_checkpoint_preserves_active_data_and_records_batch_totals(self):
        baseline = self.batch105_baseline
        self.assertEqual(baseline["baseline_counts"]["food_records"], 541)
        self.assertEqual(baseline["baseline_counts"]["mapping_rows"], 541)
        self.assertEqual(baseline["baseline_counts"]["identity_complete_gaps"], 8)
        self.assertEqual(baseline["baseline_counts"]["accepted_identity_complete_quantitative_compounds"], 99)
        self.assertEqual(baseline["baseline_counts"]["search_log_events"], 448)
        self.assertEqual(baseline["baseline_counts"]["source_registry_rows"], 57)
        self.assertEqual(baseline["baseline_counts"]["unique_source_urls"], 56)
        self.assertEqual(baseline["checkpoint_hashes_match_actual"]["food_composition.csv"], True)
        self.assertEqual(baseline["checkpoint_hashes_match_actual"]["compound_food_mapping.csv"], True)
        self.assertEqual(self.checkpoint["research_screened_fraction"], "143/143")
        batch = self.checkpoint["batch_104"]
        self.assertEqual(batch["new_search_events"], 10)
        self.assertEqual(batch["new_source_registry_entries"], 11)
        self.assertEqual(batch["source_assessments"], 12)
        self.assertEqual(len(self.sources), self.checkpoint["source_registry_rows"])
        self.assertEqual(len({r["source_url"] for r in self.sources}), self.checkpoint["unique_source_urls"])
        self.assertEqual(len(self.assessments), 12)
        self.assertEqual(batch["accepted_records"], 0)
        self.assertEqual(batch["accepted_mappings"], 0)
        self.assertEqual(batch["identity_complete_gaps_remaining"], 8)
        for rel, key in [
            ("data/food_composition/food_composition.csv", "food_composition.csv"),
            ("data/compound_food_mapping/compound_food_mapping.csv", "compound_food_mapping.csv"),
        ]:
            digest = hashlib.sha256((STAGE / rel).read_bytes()).hexdigest()
            self.assertEqual(digest, self.checkpoint["sha256"][key])


if __name__ == "__main__":
    unittest.main()
