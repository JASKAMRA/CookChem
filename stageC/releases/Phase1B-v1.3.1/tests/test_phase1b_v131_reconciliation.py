from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve()
if HERE.parents[1].name == "Phase1B-v1.3.1":
    RELEASE = HERE.parents[1]
else:
    RELEASE = HERE.parents[1] / "releases" / "Phase1B-v1.3.1"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


class Phase1BV131ReconciliationTests(unittest.TestCase):
    def test_separates_raw_mapping_identity_and_quantitative_eligibility(self):
        foods = rows(RELEASE / "stageC/data/food_composition/food_composition.csv")
        mappings = rows(RELEASE / "stageC/data/compound_food_mapping/compound_food_mapping.csv")
        coverage = rows(RELEASE / "stageC/reports/phase1b/COMPOUND_COVERAGE_REGISTER_2026-11-03.csv")
        self.assertEqual((len(foods), len(mappings), len(coverage)), (584, 584, 143))
        self.assertEqual(sum(r["food_use_classification"] == "ordinary food" for r in foods), 335)
        self.assertEqual(sum(r["food_use_classification"] == "food ingredient" for r in foods), 221)
        self.assertEqual(sum(r["food_use_classification"] == "prepared beverage" for r in foods), 28)
        self.assertEqual(sum(r["Raw_Mapping_Present"] == "true" for r in coverage), 130)
        self.assertEqual(sum(r["Identity_Complete_Per_V20"] == "true" and r["Raw_Mapping_Present"] == "true" for r in coverage), 125)
        self.assertEqual(sum(r["Identity_Complete_Per_V20"] == "false" and r["Raw_Mapping_Present"] == "true" for r in coverage), 5)
        self.assertEqual(sum(r["Accepted_Mapping_Present"] == "true" for r in coverage), 121)
        self.assertEqual(sum(r["Scientific_Eligibility_Status"] == "ELIGIBLE_ACCEPTED_QUANTITATIVE" for r in coverage), 116)
        self.assertEqual(sum(r["Scientific_Eligibility_Status"] == "ELIGIBLE_ACCEPTED_QUANTITATIVE" and "ordinary food" in r["Raw_Mapped_Food_Classes"] for r in coverage), 80)

    def test_eleven_stale_identity_flags_reconciled_without_changing_measurements(self):
        resolved = {
            "MOL-V12-CID-107905", "MOL-V12-CID-122685", "MOL-V12-CID-16741", "MOL-V12-CID-3712",
            "MOL-V12-CID-465405", "MOL-V12-CID-5276890", "MOL-V12-CID-5280544", "MOL-V12-CID-5280647",
            "MOL-V12-CID-6419835", "MOL-V12-CID-65084", "MOL-V12-CID-72277",
        }
        coverage = {r["Compound_ID"]: r for r in rows(RELEASE / "stageC/reports/phase1b/COMPOUND_COVERAGE_REGISTER_2026-11-03.csv")}
        self.assertTrue(all(coverage[cid]["Scientific_Eligibility_Status"] == "ELIGIBLE_ACCEPTED_QUANTITATIVE" for cid in resolved))
        predecessor = RELEASE.parent / "Phase1B-v1.3.0"
        for rel in ("stageC/data/food_composition/food_composition.csv", "stageC/data/compound_food_mapping/compound_food_mapping.csv"):
            self.assertEqual((RELEASE / rel).read_bytes(), (predecessor / rel).read_bytes())

    def test_manifest_checkpoint_and_user_closeout_are_traceable(self):
        release = json.loads((RELEASE / "RELEASE.json").read_text(encoding="utf-8"))
        checkpoint = json.loads((RELEASE / "stageC/reports/phase1b/CHECKPOINTS.json").read_text(encoding="utf-8"))
        self.assertEqual(release["release_id"], "Phase1B-v1.3.1")
        self.assertEqual(release["data"]["scientifically_eligible_quantitative_compounds_all_classes"], 116)
        self.assertEqual(release["data"]["ordinary_food_scientifically_eligible_quantitative_compounds"], 80)
        self.assertEqual(checkpoint["scientifically_eligible_quantitative_compounds"], 116)
        self.assertTrue((RELEASE / "stageC/reports/phase1b/CHECKPOINTS_BATCH120_HISTORICAL.json").is_file())
        manifest = json.loads((RELEASE / "CHECKSUMS.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["release_id"], "Phase1B-v1.3.1")


if __name__ == "__main__":
    unittest.main()
