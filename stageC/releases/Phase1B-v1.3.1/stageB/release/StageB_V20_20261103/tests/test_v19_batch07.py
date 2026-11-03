import csv
import unittest
from pathlib import Path

from scripts.validate_v19_batch07 import validate, validate_records


class V19Batch07Tests(unittest.TestCase):
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
        self.r = read(self.root, "validation/V19_batch_007_review.csv")
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

    def test_caffeine_estimates_and_nonsignificance_are_preserved(self):
        out = next(r["Quantitative_Outcome"] for r in self.e if r["Evidence_ID"] == "SB-0187")
        self.assertIn("85% (76–95%)", out)
        self.assertIn("no statistically significant", out)
        self.assertIn("not evidence of equivalence", out)

    def test_omeprazole_table_values_and_units_are_preserved(self):
        out = next(r["Quantitative_Outcome"] for r in self.e if r["Evidence_ID"] == "SB-0188")
        self.assertIn("1.73 ± 1.86 vs 1.47 ± 1.48 μg·h/mL", out)
        self.assertIn("99% (84–117%)", out)
        self.assertIn("24.13 ± 17.40 vs 21.70 ± 12.29 L/h", out)

    def test_nonsignificance_cannot_be_upgraded_to_no_interaction(self):
        e = [dict(x) for x in self.e]
        row = next(x for x in e if x["Evidence_ID"] == "SB-0187")
        row["Quantitative_Outcome"] = "No interaction with caffeine."
        self.assertTrue(any("85% (76–95%)" in x or "primary-source estimate" in x for x in self.errors(e=e)))

    def test_caffeine_equivalence_limitation_cannot_be_removed(self):
        e = [dict(x) for x in self.e]
        row = next(x for x in e if x["Evidence_ID"] == "SB-0187")
        row["Quantitative_Outcome"] = row["Quantitative_Outcome"].replace("not evidence of equivalence", "equivalent")
        self.assertTrue(any("not evidence of equivalence" in x for x in self.errors(e=e)))

    def test_human_source_cannot_be_reclassified_as_cell_or_animal(self):
        e = [dict(x) for x in self.e]
        next(x for x in e if x["Evidence_ID"] == "SB-0188")["Evidence_Type"] = "Animal"
        self.assertTrue(any("human pharmacokinetic" in x for x in self.errors(e=e)))

    def test_fabricated_source_tier_is_rejected(self):
        a = [dict(x) for x in self.a]
        next(x for x in a if x["Evidence_ID"] == "SB-0187")["Verification_Level"] = "4"
        self.assertTrue(any("not Tier 1" in x for x in self.errors(a=a)))

    def test_missing_pmid_cache_path_is_rejected(self):
        a = [dict(x) for x in self.a]
        next(x for x in a if x["Evidence_ID"] == "SB-0188")["Source_Cache"] = "sources/missing.json"
        self.assertTrue(any("metadata locator mismatch" in x for x in self.errors(a=a)))

    def test_cache_warning_must_preserve_batch_007_repair_history(self):
        wa = [dict(x) for x in self.wa]
        next(x for x in wa if x["Warning_ID"] == "V19-W10")["V19_Recheck_Status"] = "RESOLVED_IN_V19-006"
        self.assertTrue(any("Batch 007 repair history" in x for x in self.errors(wa=wa)))

    def test_historical_warning_ids_cannot_disappear(self):
        w = [dict(x) for x in self.w if x["Warning_ID"] != "V3-W02"]
        wa = [dict(x) for x in self.wa if x["Warning_ID"] != "V3-W02"]
        self.assertTrue(any("all 70 inherited" in x or "match uniquely" in x for x in self.errors(w=w, wa=wa)))

    def test_review_outcome_must_match_authoritative_evidence_record(self):
        r = [dict(x) for x in self.r]
        next(x for x in r if x["Evidence_ID"] == "SB-0187")["Verified_Outcome"] += " fabricated"
        self.assertTrue(any("differs from review ledger" in x for x in self.errors(r=r)))


if __name__ == "__main__":
    unittest.main()
