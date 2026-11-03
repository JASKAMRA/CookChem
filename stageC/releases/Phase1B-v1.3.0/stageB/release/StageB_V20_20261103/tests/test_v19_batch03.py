import csv
import unittest
from pathlib import Path

from scripts.validate_v19_batch03 import BATCH3, validate, validate_records


class V19Batch03Tests(unittest.TestCase):
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
        self.r = read(self.root, "validation/V19_batch_003_review.csv")
        self.be = read(parent, "data/interaction_evidence.csv")
        self.bw = read(parent, "data/warning_ledger.csv")

    def errors(self, e=None, a=None, c=None, w=None, wa=None, r=None, be=None, bw=None):
        return validate_records(
            self.root, e if e is not None else self.e, a if a is not None else self.a,
            c if c is not None else self.c, w if w is not None else self.w,
            wa if wa is not None else self.wa, r if r is not None else self.r,
            be if be is not None else self.be, bw if bw is not None else self.bw,
        )

    def test_actual_batch_and_release_pass(self):
        self.assertEqual(validate(self.root), [])

    def test_all_seven_review_rows_are_required(self):
        self.assertTrue(any("cover all seven" in x for x in self.errors(r=self.r[:-1])))

    def test_source_tier_downgrade_is_detected(self):
        a = [dict(x) for x in self.a]
        next(x for x in a if x["Evidence_ID"] == "SB-0165")["Verification_Level"] = "3"
        self.assertTrue(any("full-text source tier" in x for x in self.errors(a=a)))

    def test_source_locator_drift_is_detected(self):
        r = [dict(x) for x in self.r]
        next(x for x in r if x["Evidence_ID"] == "SB-0107")["Source_Locator"] = "Table 9"
        self.assertTrue(any("source locator/URL drift" in x for x in self.errors(r=r)))

    def test_table_prose_fici_mismatch_must_remain_visible(self):
        e = [dict(x) for x in self.e]
        row = next(x for x in e if x["Evidence_ID"] == "SB-0165")
        row["Quantitative_Outcome"] = row["Quantitative_Outcome"].replace("<0.313", "0.313")
        self.assertTrue(any("required source finding" in x for x in self.errors(e=e)))

    def test_unreported_fisetin_dose_cannot_be_inferred(self):
        e = [dict(x) for x in self.e]
        next(x for x in e if x["Evidence_ID"] == "SB-0107")["Dose"] = "20 μM"
        self.assertTrue(any("pair-specific dose must remain explicitly unreported" in x for x in self.errors(e=e)))

    def test_fisetin_is_not_a_formulation_in_this_study(self):
        e = [dict(x) for x in self.e]
        next(x for x in e if x["Evidence_ID"] == "SB-0108")["Evidence_Level"] = "formulation"
        self.assertTrue(any("must not be classified as formulation" in x for x in self.errors(e=e)))

    def test_no_synergy_cannot_be_promoted_to_no_interaction(self):
        e = [dict(x) for x in self.e]
        next(x for x in e if x["Evidence_ID"] == "SB-0109")["Outcome"] = "no_interaction_detected_under_tested_conditions"
        self.assertTrue(any("no-synergy must not be encoded as no interaction" in x for x in self.errors(e=e)))

    def test_source_no_interaction_label_retains_cutoff_uncertainty(self):
        e = [dict(x) for x in self.e]
        next(x for x in e if x["Evidence_ID"] == "SB-0167")["Outcome"] = "no_interaction_detected_under_tested_conditions"
        self.assertTrue(any("must remain qualified" in x for x in self.errors(e=e)))

    def test_new_scientific_warning_cannot_be_closed(self):
        w, wa = [dict(x) for x in self.w], [dict(x) for x in self.wa]
        next(x for x in w if x["Warning_ID"] == "V19-W05")["Audit_Status"] = "RESOLVED"
        next(x for x in wa if x["Warning_ID"] == "V19-W05")["V19_Status"] = "RESOLVED"
        self.assertTrue(any("unsupportedly closed or downgraded" in x for x in self.errors(w=w, wa=wa)))

    def test_duplicate_warning_id_is_detected(self):
        self.assertTrue(any("duplicate warning IDs" in x for x in self.errors(w=self.w + [dict(self.w[-1])])))

    def test_inherited_warning_cannot_disappear(self):
        w = [dict(x) for x in self.w if x["Warning_ID"] != "V3-W02"]
        wa = [dict(x) for x in self.wa if x["Warning_ID"] != "V3-W02"]
        self.assertTrue(any("warning audit must uniquely match" in x or "all 70 inherited" in x for x in self.errors(w=w, wa=wa)))

    def test_batch_ids_are_exactly_the_seven_inherited_blanks(self):
        self.assertEqual(len(BATCH3), 7)
        baseline_blank = {r["Evidence_ID"] for r in self.be if not r.get("Quantitative_Outcome", "").strip()}
        self.assertTrue(set(BATCH3) <= baseline_blank)


if __name__ == "__main__":
    unittest.main()
