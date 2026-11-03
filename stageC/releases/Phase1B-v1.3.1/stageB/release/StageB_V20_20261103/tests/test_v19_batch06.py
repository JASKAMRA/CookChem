import csv
import unittest
from pathlib import Path

from scripts.validate_v19_batch06 import validate, validate_records


class V19Batch06Tests(unittest.TestCase):
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
        self.r = read(self.root, "validation/V19_batch_006_review.csv")
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

    def test_all_four_records_have_source_specific_outcomes(self):
        self.assertEqual({r["Evidence_ID"] for r in self.r}, {"SB-0110", "SB-0111", "SB-0163", "SB-0164"})
        self.assertEqual(len({r["Source_Locator"] for r in self.r}), 4)

    def test_reported_ci_and_cell_line_uncertainty_cannot_be_dropped(self):
        e = [dict(x) for x in self.e]
        row = next(x for x in e if x["Evidence_ID"] == "SB-0110")
        row["Quantitative_Outcome"] = "Fisetin and cabazitaxel synergized in vitro."
        self.assertTrue(any("0.45676" in x or "source-supported outcome" in x for x in self.errors(e=e)))

    def test_xenograft_timing_discrepancy_must_remain_visible(self):
        e = [dict(x) for x in self.e]
        row = next(x for x in e if x["Evidence_ID"] == "SB-0111")
        row["Study_Design"] = "Controlled animal study; treatment began two weeks after implantation."
        row["Quantitative_Outcome"] = row["Quantitative_Outcome"].replace("Results state 3 days", "")
        self.assertTrue(any("3 days" in x for x in self.errors(e=e)))

    def test_animal_record_cannot_be_classified_as_human(self):
        e = [dict(x) for x in self.e]
        next(x for x in e if x["Evidence_ID"] == "SB-0164")["Evidence_Type"] = "Human clinical"
        self.assertTrue(any("evidence type/level" in x for x in self.errors(e=e)))

    def test_source_audit_tier_cannot_be_fabricated(self):
        a = [dict(x) for x in self.a]
        next(x for x in a if x["Evidence_ID"] == "SB-0110")["Verification_Level"] = "4"
        self.assertTrue(any("not Tier 1" in x for x in self.errors(a=a)))

    def test_missing_local_metadata_path_is_rejected(self):
        a = [dict(x) for x in self.a]
        next(x for x in a if x["Evidence_ID"] == "SB-0163")["Source_Cache"] = "sources/missing.json"
        self.assertTrue(any("metadata-cache locator mismatch" in x for x in self.errors(a=a)))

    def test_unresolved_source_warnings_cannot_be_closed(self):
        w = [dict(x) for x in self.w]
        next(x for x in w if x["Warning_ID"] == "V19-W11")["Audit_Status"] = "RESOLVED"
        self.assertTrue(any("V19-W11" in x and "remain open" in x for x in self.errors(w=w)))

    def test_source_warning_history_cannot_be_deleted(self):
        w = [dict(x) for x in self.w if x["Warning_ID"] != "V19-W13"]
        wa = [dict(x) for x in self.wa if x["Warning_ID"] != "V19-W13"]
        self.assertTrue(any("V19-W13" in x or "match uniquely" in x for x in self.errors(w=w, wa=wa)))

    def test_cache_warning_must_cover_newly_repaired_pmids(self):
        w = [dict(x) for x in self.w]
        row = next(x for x in w if x["Warning_ID"] == "V19-W10")
        row["Affected"] = row["Affected"].replace("27765854", "00000000")
        self.assertTrue(any("V19-W10" in x and "27765854" in x for x in self.errors(w=w)))

    def test_treatment_schedule_typo_in_outcome_fails_review_equality(self):
        r = [dict(x) for x in self.r]
        next(x for x in r if x["Evidence_ID"] == "SB-0164")["Verified_Outcome"] += " Incorrect inferred food-equivalent dose."
        self.assertTrue(any("disagrees with batch review" in x for x in self.errors(r=r)))

    def test_historical_warning_rows_remain_present(self):
        w = [dict(x) for x in self.w if x["Warning_ID"] != "V3-W02"]
        wa = [dict(x) for x in self.wa if x["Warning_ID"] != "V3-W02"]
        self.assertTrue(any("all 70 inherited" in x or "match uniquely" in x for x in self.errors(w=w, wa=wa)))


if __name__ == "__main__":
    unittest.main()
