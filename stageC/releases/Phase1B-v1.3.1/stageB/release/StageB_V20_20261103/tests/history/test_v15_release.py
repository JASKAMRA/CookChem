import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_v15


class V15Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = validate_v15.load("data/compound_registry.csv")
        cls.e = validate_v15.load("data/interaction_evidence.csv")
        cls.s = validate_v15.load("data/study_registry.csv")
        cls.b = validate_v15.load("data/publication_bibliography.csv")
        cls.p = validate_v15.load("data/drug_probe_registry.csv")
        cls.w = validate_v15.load("data/warning_ledger.csv")
        cls.i = validate_v15.load("identity/identity_structure_audit.csv")

    def errs(self, c=None, e=None, s=None, b=None, p=None, w=None, i=None):
        return validate_v15.issues(c or self.c, e or self.e, s or self.s, b or self.b, p or self.p, w or self.w, i or self.i)

    def test_counts_status_and_batch6(self):
        m = json.loads((ROOT / "release_metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(136, m["expected_compounds"])
        self.assertEqual(310, m["expected_evidence"])
        self.assertEqual("PARTIAL_NOT_READY_FOR_160", m["readiness"])
        self.assertEqual([], self.errs())

    def test_all_v14_compound_evidence_and_warning_records_preserved(self):
        for rel, key in (("data/compound_registry.csv", "Compound_ID"), ("data/interaction_evidence.csv", "Evidence_ID"), ("data/warning_ledger.csv", "Warning_ID")):
            old = {r[key]: r for r in validate_v15.load(rel, validate_v15.V14)}
            new = {r[key]: r for r in validate_v15.load(rel)}
            self.assertTrue(all(new.get(k) == row for k, row in old.items()), rel)

    def test_negative_caco2_finding_and_conflict_are_explicit(self):
        beta_null = next(r for r in self.e if r["Evidence_ID"] == "SB-V15-004")
        self.assertEqual("null_finding", beta_null["Outcome"])
        self.assertIn("No effect detected", beta_null["Quantitative_Outcome"])
        octyl = next(r for r in self.e if r["Evidence_ID"] == "SB-V15-007")
        self.assertEqual("V15-OCTYL-GALLATE-TRANSPORTER-CONFLICT", octyl["Conflict_Group"])
        self.assertIn("no dose-response", octyl["Source_Locator"])

    def test_batch7_null_findings_are_typed_and_quantified_only_as_reported(self):
        rows = [r for r in self.e if r["Evidence_ID"] in {"SB-V15-008", "SB-V15-009", "SB-V15-010", "SB-V15-011"}]
        self.assertEqual(4, len(rows))
        self.assertTrue(all(r["Outcome"] == "null_finding" for r in rows))
        self.assertTrue(all(r["Evidence_Type"] == "In vitro" for r in rows))
        self.assertTrue(all("no effect detected" in r["Quantitative_Outcome"].lower() for r in rows))
        self.assertTrue(all(r["Quantitative_Outcome"].strip() != "0" for r in rows))
        self.assertEqual({"Additive 100 μM", "Additive 200 μM"}, {" ".join(r["Dose"].split(";")[0].split()[:3]) for r in rows})
        self.assertTrue(all("no clinical extrapolation" in r["Clinical_Extrapolation"].lower() for r in rows))

    def test_mutations_detected(self):
        c = [dict(r) for r in self.c]; e = [dict(r) for r in self.e]; s = [dict(r) for r in self.s]
        b = [dict(r) for r in self.b]; p = [dict(r) for r in self.p]; w = [dict(r) for r in self.w]; i = [dict(r) for r in self.i]
        c.append(dict(c[-1])); self.assertTrue(any("compound IDs" in x for x in self.errs(c=c)))
        c.pop()
        e.append(dict(e[-1])); self.assertTrue(any("Evidence_ID" in x for x in self.errs(e=e)))
        e.pop()
        e0 = next(r for r in e if r["Evidence_ID"] == "SB-V15-001"); e0["Compound_ID"] = "BAD"; self.assertTrue(any("orphan evidence" in x for x in self.errs(e=e)))
        e0["Compound_ID"] = "MOL-V15-CID-5280489"; e0["DOI"] = "bad"; self.assertTrue(any("invalid DOI" in x for x in self.errs(e=e)))
        e0["DOI"] = "10.1021/acs.molpharmaceut.5c00705"; e0["Evidence_Type"] = "Human pharmacokinetic"; self.assertTrue(any("misclassified" in x for x in self.errs(e=e)))
        e0["Evidence_Type"] = "In vitro"; e0["Drug"] = "missing"; self.assertTrue(any("unregistered probe" in x for x in self.errs(e=e)))
        e0["Drug"] = "BCRP-mediated Lucifer yellow efflux"; e0["PMID"] = ""; self.assertTrue(any("invalid PMID" in x for x in self.errs(e=e)))
        e0["PMID"] = "40773056"; e0["Quantitative_Outcome"] = "0"; e0["Outcome"] = "null_finding"; self.assertTrue(any("null converted" in x for x in self.errs(e=e)))
        i0 = next(r for r in i if r["Compound_ID"] == "MOL-V15-CID-14425"); i0["Exact_Key_Match"] = "False"; self.assertTrue(any("identity audit mismatch" in x for x in self.errs(i=i)))
        w.append(dict(w[0])); self.assertTrue(any("Warning_ID duplicated" in x for x in self.errs(w=w)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
