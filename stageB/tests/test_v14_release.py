import csv
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / "stageB" / "release" / "StageB_V14_20261102"
V13 = ROOT / "stageB" / "release" / "StageB_V13_20261102"
sys.path.insert(0, str(ROOT / "stageB" / "scripts"))
import validate_v14


def table(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


class V14ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compounds = table(RELEASE / "data" / "compound_registry.csv")
        cls.evidence = table(RELEASE / "data" / "interaction_evidence.csv")
        cls.studies = table(RELEASE / "data" / "study_registry.csv")
        cls.bibliography = table(RELEASE / "data" / "publication_bibliography.csv")
        cls.warnings = table(RELEASE / "data" / "warning_ledger.csv")

    def test_release_metadata_counts_and_honest_status(self):
        metadata = json.loads((RELEASE / "release_metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["expected_compounds"], len({r["Compound_ID"] for r in self.compounds}))
        self.assertEqual(metadata["expected_evidence"], len({r["Evidence_ID"] for r in self.evidence}))
        self.assertEqual("PARTIAL_NOT_READY_FOR_160", metadata["readiness"])

    def test_v13_compound_and_evidence_records_are_preserved(self):
        for rel, key in (("data/compound_registry.csv", "Compound_ID"), ("data/interaction_evidence.csv", "Evidence_ID")):
            old = {r[key]: r for r in table(V13 / rel)}
            current = {r[key]: r for r in table(RELEASE / rel)}
            self.assertTrue(all(current.get(k) == v for k, v in old.items()), rel)

    def test_new_compounds_have_distinct_pubchem_identities(self):
        new = [r for r in self.compounds if r.get("Origin") == "v14_controlled_expansion"]
        self.assertGreaterEqual(len(new), 3)
        expected = {"MOL-V14-CID-5469424", "MOL-V14-CID-5315472", "MOL-V14-CID-145659"}
        self.assertTrue(expected.issubset({r["Compound_ID"] for r in new}))
        identity = {r["Compound_ID"]: r for r in table(RELEASE / "identity" / "identity_structure_audit.csv")}
        for row in new:
            self.assertEqual("True", identity[row["Compound_ID"]]["Exact_Key_Match"])
            self.assertEqual(row["InChIKey"], identity[row["Compound_ID"]]["Registry_InChIKey"])

    def test_evidence_has_valid_relationships_and_negative_result_is_not_zero(self):
        new = [r for r in self.evidence if r.get("Evidence_ID", "").startswith("SB-V14-")]
        self.assertGreaterEqual(len(new), 6)
        study_ids = {r["Study_ID"] for r in self.studies}
        pmids = {r["PMID"] for r in self.bibliography}
        for row in new:
            self.assertIn(row["Compound_ID"], {r["Compound_ID"] for r in self.compounds})
            self.assertIn(row["Study_ID"], study_ids)
            self.assertIn(row["PMID"], pmids)
            expected_type = "Animal" if row["Evidence_ID"] == "SB-V14-009" else "In vitro"
            self.assertEqual(expected_type, row["Evidence_Type"])
            self.assertIn("no clinical", row["Clinical_Extrapolation"].lower())
        negative = next(r for r in new if r["Evidence_ID"] == "SB-V14-004")
        self.assertIn("> 50 μM", negative["Quantitative_Outcome"])
        self.assertNotEqual("0", negative["Quantitative_Outcome"])

    def test_all_new_rows_pass_structural_and_provenance_checks(self):
        self.assertEqual([], validate_v14.issues(self.compounds, self.evidence, self.studies, self.bibliography, self.warnings))

    def test_mutations_are_rejected(self):
        c, e = [dict(r) for r in self.compounds], [dict(r) for r in self.evidence]
        s, b, w = [dict(r) for r in self.studies], [dict(r) for r in self.bibliography], [dict(r) for r in self.warnings]
        original = validate_v14.issues
        c.append(dict(c[0]))
        self.assertTrue(any("compound IDs" in x for x in original(c, e, s, b, w)))
        c.pop()
        c[0]["InChIKey"] = c[1]["InChIKey"]
        self.assertTrue(any("InChIKeys" in x for x in original(c, e, s, b, w)))
        c[0]["InChIKey"] = "test-key-restored"
        e.append(dict(e[0]))
        self.assertTrue(any("evidence IDs" in x for x in original(c, e, s, b, w)))
        e.pop()
        probes = [dict(r) for r in e]
        new_row = next(r for r in probes if r["Evidence_ID"].startswith("SB-V14-"))
        new_row["Compound_ID"] = "INVALID-ID"
        self.assertTrue(any("orphan evidence" in x for x in original(c, probes, s, b, w)))
        new_row["Compound_ID"] = "MOL-V14-CID-5469424"
        new_row["PMID"] = "not-a-pmid"
        self.assertTrue(any("invalid PMID" in x for x in original(c, probes, s, b, w)))
        new_row["PMID"] = "18480186"
        new_row["DOI"] = "invalid-doi"
        self.assertTrue(any("invalid DOI" in x for x in original(c, probes, s, b, w)))
        new_row["DOI"] = "10.1124/dmd.108.020552"
        new_row["Evidence_Type"] = "Human pharmacokinetic"
        self.assertTrue(any("mislabeled as human" in x for x in original(c, probes, s, b, w)))
        new_row["Evidence_Type"] = "In vitro"
        new_row["Quantitative_Outcome"] = "0"
        self.assertTrue(any("converted to zero" in x for x in original(c, probes, s, b, w)))


if __name__ == "__main__":
    unittest.main()
