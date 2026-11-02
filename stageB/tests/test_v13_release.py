import csv
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "stageB" / "release" / "StageB_Final"
RELEASE = ROOT / "stageB" / "release" / "StageB_V13_20261102"
VALIDATOR = RELEASE / "scripts" / "manifest_integrity.py"
SPEC = importlib.util.spec_from_file_location("v13_manifest_integrity", VALIDATOR)
manifest_integrity = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(manifest_integrity)


def table(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


class V13ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compounds = table(RELEASE / "data" / "compound_registry.csv")
        cls.evidence = table(RELEASE / "data" / "interaction_evidence.csv")
        cls.identity = table(RELEASE / "identity" / "identity_structure_audit.csv")

    def test_unique_counts_and_version_metadata(self):
        metadata = json.loads((RELEASE / "release_metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(123, len({r["Compound_ID"] for r in self.compounds}))
        self.assertEqual(290, len({r["Evidence_ID"] for r in self.evidence}))
        self.assertEqual("PARTIAL_NOT_READY_FOR_160", metadata["readiness"])

    def test_all_baseline_compounds_and_evidence_are_preserved(self):
        baseline_compounds = {r["Compound_ID"]: r for r in table(BASELINE / "data" / "compound_registry.csv")}
        baseline_evidence = {r["Evidence_ID"]: r for r in table(BASELINE / "data" / "interaction_evidence.csv")}
        new_compounds = {r["Compound_ID"]: r for r in self.compounds}
        new_evidence = {r["Evidence_ID"]: r for r in self.evidence}
        self.assertEqual(119, len(baseline_compounds))
        self.assertEqual(286, len(baseline_evidence))
        self.assertTrue(all(new_compounds[k] == v for k, v in baseline_compounds.items()))
        self.assertTrue(all(new_evidence[k] == v for k, v in baseline_evidence.items()))

    def test_candidate_structures_are_unique_and_linked(self):
        compounds = {r["Compound_ID"]: r for r in self.compounds}
        identities = {r["Compound_ID"]: r for r in self.identity}
        new_ids = {"MOL-V13-CID-161306", "MOL-V13-CID-5281858", "MOL-V13-CID-5469634", "MOL-V13-CID-8468"}
        self.assertTrue(new_ids.issubset(compounds))
        self.assertTrue(new_ids.issubset(identities))
        for compound_id in new_ids:
            self.assertEqual(compounds[compound_id]["InChIKey"], identities[compound_id]["Registry_InChIKey"])
            self.assertEqual("True", identities[compound_id]["Exact_Key_Match"])
        self.assertEqual(123, len({r["InChIKey"] for r in self.compounds}))

    def test_evidence_references_resolve_and_negative_finding_is_retained(self):
        compound_ids = {r["Compound_ID"] for r in self.compounds}
        study_ids = {r["Study_ID"] for r in table(RELEASE / "data" / "study_registry.csv")}
        pub_ids = {r["PMID"] for r in table(RELEASE / "data" / "publication_bibliography.csv")}
        drugs = {r["Drug_Probe"] for r in table(RELEASE / "data" / "drug_probe_registry.csv")}
        new_evidence = [r for r in self.evidence if r["Evidence_ID"].startswith("SB-V13-")]
        self.assertEqual(4, len(new_evidence))
        for row in new_evidence:
            self.assertIn(row["Compound_ID"], compound_ids)
            self.assertIn(row["Study_ID"], study_ids)
            self.assertIn(row["PMID"], pub_ids)
            self.assertIn(row["Drug"], drugs)
        negative = next(r for r in new_evidence if r["Compound_ID"] == "MOL-V13-CID-161306")
        self.assertIn("No significant", negative["Quantitative_Outcome"])

    def test_sinapinic_identity_is_held_without_overwriting_inherited_row(self):
        baseline = {r["Compound_ID"]: r for r in table(BASELINE / "data" / "compound_registry.csv")}
        release = {r["Compound_ID"]: r for r in self.compounds}
        inherited_id = "MOL-V10-1549091"
        self.assertIn(inherited_id, baseline)
        self.assertEqual(baseline[inherited_id], release[inherited_id])
        warning_ids = {r["Warning_ID"] for r in table(RELEASE / "data" / "warning_ledger.csv")}
        self.assertIn("V13-W02", warning_ids)
        decisions = table(RELEASE / "provenance" / "selection_decisions.csv")
        held = [r for r in decisions if r["Candidate"] == "Sinapinic acid (inherited registry row)"]
        self.assertEqual(1, len(held))
        self.assertIn("Hold", held[0]["Decision"])

    def test_release_manifest_has_no_missing_extra_or_modified_files(self):
        result = manifest_integrity.verify_manifest(RELEASE, mode="canonical")
        self.assertEqual(
            "PASS",
            result["status"],
            f"mismatches={result['mismatches'][:5]}, missing={result['missing']}, unexpected={result['unexpected']}",
        )
        self.assertEqual(result["manifest_entries"], result["release_files"])
        self.assertFalse(result["missing"])
        self.assertFalse(result["unexpected"])


if __name__ == "__main__":
    unittest.main()
