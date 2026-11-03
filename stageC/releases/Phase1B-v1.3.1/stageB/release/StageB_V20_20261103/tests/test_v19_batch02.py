import csv
import hashlib
import unittest
from pathlib import Path

from scripts.manifest_integrity import load_manifest, verify_manifest
from scripts.validate_v19_batch02 import validate, validate_records


class V19Batch02Tests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]
        parent = self.root.parent / "StageB_V18_20261103"

        def rows(base, rel):
            with (base / rel).open(encoding="utf-8-sig", newline="") as handle:
                return list(csv.DictReader(handle))

        self.e = rows(self.root, "data/interaction_evidence.csv")
        self.a = rows(self.root, "provenance/source_audit.csv")
        self.w = rows(self.root, "data/warning_ledger.csv")
        self.wa = rows(self.root, "validation/V19_warning_audit.csv")
        self.r = rows(self.root, "validation/V19_batch_002_review.csv")
        self.be = rows(parent, "data/interaction_evidence.csv")
        self.bw = rows(parent, "data/warning_ledger.csv")

    def errors(self, e=None, a=None, w=None, wa=None, r=None, be=None, bw=None):
        return validate_records(self.root, e or self.e, a or self.a, w or self.w, wa or self.wa, r or self.r, be or self.be, bw or self.bw)

    def test_actual_batch_and_release_pass(self):
        self.assertEqual(validate(self.root), [])

    def test_eight_review_rows_are_required(self):
        self.assertTrue(any("exactly cover the eight" in x for x in self.errors(r=self.r[:-1])))

    def test_changed_or_blank_outcome_is_detected(self):
        e = [dict(x) for x in self.e]
        row = next(x for x in e if x["Evidence_ID"] == "SB-0092")
        row["Quantitative_Outcome"] = ""
        self.assertTrue(any("blank quantitative outcome" in x or "required source-supported value" in x for x in self.errors(e=e)))

    def test_source_tier_downgrade_is_detected(self):
        a = [dict(x) for x in self.a]
        next(x for x in a if x["Evidence_ID"] == "SB-0101")["Verification_Level"] = "3"
        self.assertTrue(any("verification tier/disposition" in x for x in self.errors(a=a)))

    def test_wrong_existing_metadata_cache_is_detected(self):
        a = [dict(x) for x in self.a]
        next(x for x in a if x["Evidence_ID"] == "SB-0018")["Source_Cache"] = "source_archive/000ac944a870cad5527a3bd67770332ca58a3b80f3e9d038faee0853281fc54f_pmid_22114872.json"
        self.assertTrue(any("does not contain the asserted PMID/DOI" in x for x in self.errors(a=a)))

    def test_review_locator_cannot_drift_from_record(self):
        r = [dict(x) for x in self.r]
        next(x for x in r if x["Evidence_ID"] == "SB-0090")["Source_Locator"] = "Table 7"
        self.assertTrue(any("batch review does not point" in x for x in self.errors(r=r)))

    def test_open_scientific_warnings_cannot_be_closed(self):
        w = [dict(x) for x in self.w]
        wa = [dict(x) for x in self.wa]
        next(x for x in w if x["Warning_ID"] == "V19-W02")["Audit_Status"] = "RESOLVED"
        next(x for x in wa if x["Warning_ID"] == "V19-W02")["V19_Status"] = "RESOLVED"
        self.assertTrue(any("unsupported closure" in x for x in self.errors(w=w, wa=wa)))

    def test_duplicate_warning_id_is_detected(self):
        w = [dict(x) for x in self.w] + [dict(self.w[-1])]
        self.assertTrue(any("duplicate warning IDs" in x for x in self.errors(w=w)))

    def test_inherited_warning_cannot_disappear(self):
        w = [dict(x) for x in self.w if x["Warning_ID"] != "V3-W02"]
        wa = [dict(x) for x in self.wa if x["Warning_ID"] != "V3-W02"]
        self.assertTrue(any("warning audit coverage" in x or "history is incomplete" in x for x in self.errors(w=w, wa=wa)))

    def test_warning_ledger_and_audit_are_in_exact_manifest(self):
        result = verify_manifest(self.root, mode="exact")
        self.assertEqual(result["status"], "PASS")
        manifest = load_manifest(self.root)
        for rel in ("data/warning_ledger.csv", "validation/V19_warning_audit.csv"):
            digest = hashlib.sha256((self.root / rel).read_bytes()).hexdigest()
            self.assertEqual(manifest[rel], digest)


if __name__ == "__main__":
    unittest.main()
