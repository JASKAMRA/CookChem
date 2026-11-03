import csv
import unittest
from pathlib import Path

from scripts.validate_v19_batch05 import validate, validate_records


class V19Batch05Tests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]
        parent = self.root.parent / "StageB_V18_20261103"

        def read(base, rel):
            with (base / rel).open(encoding="utf-8-sig", newline="") as handle:
                return list(csv.DictReader(handle))

        self.e = read(self.root, "data/interaction_evidence.csv")
        self.a = read(self.root, "provenance/source_audit.csv")
        self.c = read(self.root, "provenance/claim_support_and_verification.csv")
        self.w = read(self.root, "data/warning_ledger.csv")
        self.wa = read(self.root, "validation/V19_warning_audit.csv")
        self.r = read(self.root, "validation/V19_batch_005_review.csv")
        self.b = read(self.root, "data/publication_bibliography.csv")
        self.be = read(parent, "data/interaction_evidence.csv")
        self.bw = read(parent, "data/warning_ledger.csv")

    def errors(self, e=None, a=None, c=None, w=None, wa=None, r=None, b=None):
        return validate_records(
            self.root, e if e is not None else self.e, a if a is not None else self.a,
            c if c is not None else self.c, w if w is not None else self.w,
            wa if wa is not None else self.wa, r if r is not None else self.r,
            b if b is not None else self.b, self.be, self.bw,
        )

    def test_actual_batch_passes(self):
        self.assertEqual(validate(self.root), [])

    def test_all_six_record_reviews_are_required(self):
        self.assertTrue(any("all six target records" in x for x in self.errors(r=self.r[:-1])))

    def test_null_findings_must_keep_tested_condition_scope(self):
        e = [dict(x) for x in self.e]
        next(x for x in e if x["Evidence_ID"] == "SB-0157")["Quantitative_Outcome"] = "No pharmacological interaction exists."
        self.assertTrue(any("primary-source result or limitation missing" in x for x in self.errors(e=e)))

    def test_vpa_omnibus_and_pairwise_results_must_both_remain(self):
        e = [dict(x) for x in self.e]
        next(x for x in e if x["Evidence_ID"] == "SB-0161")["Quantitative_Outcome"] = "No effect in the study."
        self.assertTrue(any("primary-source result or limitation missing" in x for x in self.errors(e=e)))

    def test_carbamazepine_muscle_strength_signal_cannot_disappear(self):
        e = [dict(x) for x in self.e]
        next(x for x in e if x["Evidence_ID"] == "SB-0158")["Quantitative_Outcome"] = "11.66 ± 0.61; 7.83 ± 0.86; 2.06 ± 0.10; 2.41 ± 0.06; 5.45 ± 0.36"
        self.assertTrue(any("26.72 ± 1.1" in x for x in self.errors(e=e)))

    def test_human_classification_is_rejected(self):
        e = [dict(x) for x in self.e]
        next(x for x in e if x["Evidence_ID"] == "SB-0160")["Evidence_Type"] = "Human clinical"
        self.assertTrue(any("classification must be compound-tested animal evidence" in x for x in self.errors(e=e)))

    def test_source_cache_locator_is_verified_against_metadata(self):
        a = [dict(x) for x in self.a]
        next(x for x in a if x["Evidence_ID"] == "SB-0156")["Source_Cache"] = "release_v7/sources/missing.json"
        self.assertTrue(any("local MED metadata cache path is inconsistent" in x for x in self.errors(a=a)))

    def test_warning_scope_expansion_must_be_documented(self):
        w = [dict(x) for x in self.w]
        next(x for x in w if x["Warning_ID"] == "V19-W10")["Affected"] = "only PMIDs 24276478 and 26396928"
        self.assertTrue(any("Batch 005 cache-path repair" in x for x in self.errors(w=w)))

    def test_resolved_warning_audit_must_include_batch5_history(self):
        wa = [dict(x) for x in self.wa]
        next(x for x in wa if x["Warning_ID"] == "V19-W10")["V19_Recheck_Status"] = "RESOLVED_IN_V19-004"
        self.assertTrue(any("expanded Batch 005 review history" in x for x in self.errors(wa=wa)))

    def test_inherited_warning_cannot_disappear(self):
        w = [dict(x) for x in self.w if x["Warning_ID"] != "V3-W02"]
        wa = [dict(x) for x in self.wa if x["Warning_ID"] != "V3-W02"]
        self.assertTrue(any("all 70 inherited" in x or "match uniquely" in x for x in self.errors(w=w, wa=wa)))


if __name__ == "__main__":
    unittest.main()
