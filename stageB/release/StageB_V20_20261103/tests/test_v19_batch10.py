"""Regression and mutation tests for V19-010 primary-source extractions."""
import csv
import unittest
from pathlib import Path

from scripts.validate_v19_batch10 import TARGETS, validate, validate_records


class V19Batch10Tests(unittest.TestCase):
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
        self.r = read(self.root, "validation/V19_batch_010_review.csv")
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

    def test_all_three_full_text_outcomes_match_review_ledger(self):
        evidence = {r["Evidence_ID"]: r["Quantitative_Outcome"] for r in self.e if r["Evidence_ID"] in TARGETS}
        review = {r["Evidence_ID"]: r["Verified_Outcome"] for r in self.r}
        self.assertEqual(evidence, review)
        self.assertEqual(set(evidence), set(TARGETS))

    def test_table_values_and_isolate_units_are_preserved(self):
        expected = {
            "SB-0135": ["3.9/31.25 µg/mL", "1.8/7.81 µg/mL", "3.9/15.62 µg/mL", "ΣFICI=0.374"],
            "SB-0136": ["15.62/125 µg/mL", "31.25/250 µg/mL", "62.5/250 µg/mL", "ΣFICI=0.187"],
            "SB-0137": ["62.5/500 µg/mL", "15.62/125 µg/mL", "125/500 µg/mL", "ΣFICI=0.750"],
        }
        for eid, markers in expected.items():
            outcome = next(r["Quantitative_Outcome"] for r in self.e if r["Evidence_ID"] == eid)
            for marker in markers:
                self.assertIn(marker, outcome)

    def test_thymol_boundary_ambiguity_remains_open_and_source_labeled(self):
        evidence = next(r["Quantitative_Outcome"] for r in self.e if r["Evidence_ID"] == "SB-0137")
        warning = next(r for r in self.w if r["Warning_ID"] == "V19-W16")
        self.assertIn("labeled “Partial synergy.”", evidence)
        self.assertEqual(warning["Audit_Status"], "NEEDS_MANUAL_REVIEW")
        self.assertIn("0.750", warning["Description"])

    def test_fabricated_table_value_is_rejected(self):
        e = [dict(r) for r in self.e]
        row = next(r for r in e if r["Evidence_ID"] == "SB-0136")
        row["Quantitative_Outcome"] = row["Quantitative_Outcome"].replace("ΣFICI=0.187", "ΣFICI=0.999")
        self.assertTrue(any("ΣFICI=0.187" in error for error in self.errors(e=e)))

    def test_in_vitro_isolates_cannot_be_reported_as_human_participants(self):
        e = [dict(r) for r in self.e]
        next(r for r in e if r["Evidence_ID"] == "SB-0135")["Population"] = "Human patients in a clinical interaction study"
        self.assertTrue(any("not distinguished from human-participant" in error for error in self.errors(e=e)))

    def test_w16_cannot_be_closed_while_threshold_is_unresolved(self):
        w = [dict(r) for r in self.w]
        next(r for r in w if r["Warning_ID"] == "V19-W16")["Audit_Status"] = "RESOLVED"
        self.assertTrue(any("V19-W16 must remain open" in error for error in self.errors(w=w)))

    def test_warning_audit_must_preserve_w16_traceability(self):
        w = [dict(r) for r in self.w]
        next(r for r in w if r["Warning_ID"] == "V19-W16")["Audit_Verification_Reference"] = ""
        self.assertTrue(any("V19-W16 lacks" in error for error in self.errors(w=w)))

    def test_inherited_warning_ids_cannot_disappear(self):
        w = [dict(r) for r in self.w if r["Warning_ID"] != "V3-W02"]
        wa = [dict(r) for r in self.wa if r["Warning_ID"] != "V3-W02"]
        self.assertTrue(any("all 70 inherited" in error or "match uniquely" in error for error in self.errors(w=w, wa=wa)))

    def test_full_text_tier_cannot_be_downgraded(self):
        a = [dict(r) for r in self.a]
        next(r for r in a if r["Evidence_ID"] == "SB-0137")["Verification_Level"] = "3"
        self.assertTrue(any("must remain Tier 1" in error for error in self.errors(a=a)))


if __name__ == "__main__":
    unittest.main()
