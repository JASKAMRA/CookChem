import csv
import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGE = ROOT / "stageC"
ACCEPTED_IDS = {
    "MOL-V17-CID-6072",      # phloridzin
    "MOL-V17-CID-5280459",   # quercitrin
    "MOL-V17-CID-91469",     # S-equol
    "MOL-V17-CID-17730",     # Sunset Yellow FCF
}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


class Phase1BBatch101Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.food = read_csv(STAGE / "data/food_composition/food_composition.csv")
        cls.mappings = read_csv(STAGE / "data/compound_food_mapping/compound_food_mapping.csv")
        cls.audit = read_csv(STAGE / "data/stage_b_snapshot_20261103/identity_structure_audit.csv")
        cls.batch = STAGE / "reports/phase1b/batches/batch_101_final_eligible_foodscreen"
        cls.accepted = read_csv(cls.batch / "accepted_rows.csv")
        cls.rejected = read_csv(cls.batch / "rejected_candidates.csv")
        cls.delta = json.loads((cls.batch / "coverage_delta.json").read_text(encoding="utf-8"))
        cls.universe = read_csv(STAGE / "reports/phase1b/COMPOUND_COVERAGE_REGISTER_2026-11-03.csv")

    def test_append_counts_and_global_record_ids(self):
        # The active file includes Batch 102, Batch 105, and later accepted records.
        self.assertEqual(len(self.food), 546)
        self.assertEqual(len(self.mappings), 546)
        food_ids = [r["food_record_id"] for r in self.food]
        mapping_ids = [r["mapping_id"] for r in self.mappings]
        self.assertEqual(len(food_ids), len(set(food_ids)))
        self.assertEqual(len(mapping_ids), len(set(mapping_ids)))
        self.assertEqual(len(self.accepted), 28)

    def test_preexisting_511_rows_remain_byte_identical(self):
        expected = {
            STAGE / "data/food_composition/food_composition.csv": "aa15fd49be4afd30d1f61fe06de9039d0a925c22a6c56e970ddc75033b04f127",
            STAGE / "data/compound_food_mapping/compound_food_mapping.csv": "9dcaadf0821aee15f1666ca26c88c592bb1e98a781eb533e246ddd94dab9ca97",
        }
        for path, baseline_hash in expected.items():
            lines = path.read_bytes().splitlines(keepends=True)
            self.assertGreaterEqual(len(lines), 512)
            prefix_hash = hashlib.sha256(b"".join(lines[:512])).hexdigest()
            self.assertEqual(prefix_hash, baseline_hash)

    def test_independent_mapping_rebuild_matches_active_rows_in_order(self):
        rebuilt = read_csv(self.batch / "mapping_rebuild.csv")
        self.assertEqual(len(rebuilt), 539)
        self.assertEqual(self.mappings[:len(rebuilt)], rebuilt)

    def test_new_records_have_verified_complete_identity_mappings(self):
        food_by_id = {r["food_record_id"]: r for r in self.food}
        audit_status = {r["Compound_ID"]: r["Status"] for r in self.audit}
        compounds = {r["Compound_ID"]: r for r in read_csv(STAGE / "data/stage_b_snapshot_20261103/compound_registry.csv")}
        batch_food_ids = {r["food_record_id"] for r in self.accepted}
        selected = [r for r in self.mappings if r["food_record_id"] in batch_food_ids]
        self.assertEqual(len(selected), 28)
        self.assertEqual({r["compound_id"] for r in selected}, ACCEPTED_IDS)
        self.assertTrue(all(r["quantitative_data_available"] == "true" for r in selected))
        self.assertTrue(all(r["mapping_status"] in {"Exact identity match", "Verified synonym match", "Structure-supported match"} for r in selected))
        self.assertTrue(all(audit_status[r["compound_id"]] == "Complete" for r in selected))
        self.assertTrue(all(r["food_record_id"] in food_by_id for r in selected))
        for record in self.accepted:
            compound = compounds[record["compound_id"]]
            self.assertEqual(record["pubchem_cid"], compound["PubChem_CID"])
            self.assertEqual(record["inchikey"], compound["InChIKey"])
            for field in ("source_title", "doi", "source_url", "analytical_method", "source_verification_status", "extraction_notes", "uncertainty_notes"):
                self.assertTrue(record[field], f"{record['food_record_id']} lacks {field}")

    def test_exact_source_values_and_bases_are_preserved(self):
        rows = {r["food_record_id"]: r for r in self.accepted}
        phloridzin = [r for r in self.accepted if r["compound_id"] == "MOL-V17-CID-6072"]
        self.assertEqual(len(phloridzin), 22)
        self.assertTrue(all(r["reported_unit"] == "µg/g" and r["moisture_basis"] == "fresh weight (FW)" for r in phloridzin))
        quercitrin = rows["QUERCITRIN-ANTIOX2022-GALAVAL-G11-FLESH"]
        self.assertEqual((quercitrin["reported_concentration"], quercitrin["reported_unit"], quercitrin["moisture_basis"]), ("148", "µg/g", "dry weight (DW)"))
        equol = rows["SEQUOL-JFF2013-STINKYTOFU-ALL138"]
        self.assertEqual((equol["reported_concentration"], equol["reported_unit"], equol["moisture_basis"]), ("1.2", "mg/100 g", "wet weight"))
        dyes = [r for r in self.accepted if r["compound_id"] == "MOL-V17-CID-17730"]
        self.assertEqual(len(dyes), 4)
        self.assertTrue(all(r["reported_unit"] == "mg/L" and r["normalized_unit"] == "mg/L" for r in dyes))

    def test_held_and_rejected_candidates_are_not_ingested(self):
        # These compounds were later accepted from different, basis-resolved sources
        # in Batch 102. The specific Batch 101 held/rejected source rows stay excluded.
        active_sources = {
            (r["compound_id"], r["food_name"], r["source_title"])
            for r in self.food
        }
        excluded = {
            (r["compound_id"], r["food_name"], r["source_title"])
            for r in self.rejected
            if r["compound_id"] in {"MOL-V17-CID-5280704", "MOL-V17-CID-5281673", "MOL-V17-CID-92794"}
        }
        self.assertFalse(active_sources & excluded)
        coffee = [r for r in self.rejected if r["food_name"].startswith("Green coffee,")]
        self.assertEqual(len(coffee), 22)
        self.assertTrue(all(r["screening_disposition"] == "REJECTED_NATIVE_FOOD_MEASUREMENT" for r in coffee))

    def test_coverage_counts_identity_pending_rows_separately(self):
        self.assertEqual(self.delta["current"]["identity_complete_quantitative_compounds"], 97)
        self.assertEqual(self.delta["current"]["identity_pending"], 36)
        self.assertEqual(self.delta["current"]["pending_identity_mapping_rows"], 46)
        self.assertEqual(self.delta["current"]["pending_identity_compounds_with_mappings"], 16)
        self.assertEqual(self.delta["current"]["orphans"], 0)
        self.assertFalse(self.delta["target"]["achieved"])

    def test_current_coverage_register_reconciles_all_143_stage_b_ids(self):
        complete = [r for r in self.universe if r["Identity_Audit_Status"] == "Complete"]
        eligible = [r for r in self.universe if r["Identity_Complete_Quantitative_Eligible"] == "true"]
        pending = [r for r in self.universe if r["Coverage_Status"].startswith("Identity review pending")]
        self.assertEqual(len(self.universe), 143)
        self.assertEqual(len({r["Compound_ID"] for r in self.universe}), 143)
        self.assertEqual(len(complete), 107)
        self.assertEqual(len(eligible), 100)
        self.assertEqual(len(pending), 36)
        self.assertEqual(sum(r["Coverage_Status"].startswith("Identity-complete; no accepted quantitative measurement") for r in self.universe), 7)
        self.assertEqual(len({r["Compound_ID"] for r in self.universe if int(r["Search_Log_Event_Count"]) > 0 and r["Identity_Audit_Status"] == "Complete"}), 107)


if __name__ == "__main__":
    unittest.main()
