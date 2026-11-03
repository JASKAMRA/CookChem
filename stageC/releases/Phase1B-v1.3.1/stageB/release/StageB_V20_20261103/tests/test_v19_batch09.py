"""Mutation tests for Tier 3 evidence and unresolved Ki attribution in V19-009."""
import csv
import unittest
from pathlib import Path

from scripts.validate_v19_batch09 import INHIBITORS, TARGETS, validate, validate_records


class V19Batch09Tests(unittest.TestCase):
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
        self.r = read(self.root, "validation/V19_batch_009_review.csv")
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

    def test_exact_three_records_are_covered(self):
        self.assertEqual({r["Evidence_ID"] for r in self.r}, set(TARGETS))

    def test_group_ki_range_is_not_attributed_to_each_inhibitor(self):
        for eid in INHIBITORS:
            row = next(r for r in self.e if r["Evidence_ID"] == eid)
            self.assertIn("30–50 μmol", row["Quantitative_Outcome"])
            self.assertIn("not assigned to " + TARGETS[eid].lower() + " alone", row["Quantitative_Outcome"])

    def test_individual_ki_or_normalized_unit_is_rejected(self):
        e = [dict(r) for r in self.e]
        row = next(r for r in e if r["Evidence_ID"] == "SB-0149")
        row["Quantitative_Outcome"] = row["Quantitative_Outcome"].replace("not assigned to diosmetin alone", "Ki=35 μM for diosmetin")
        self.assertTrue(any("not assigned" in error or "compound-specific" in error or "normalization" in error for error in self.errors(e=e)))

    def test_tangeretin_stimulation_is_not_reclassified_as_inhibition(self):
        e = [dict(r) for r in self.e]
        row = next(r for r in e if r["Evidence_ID"] == "SB-0173")
        row["Quantitative_Outcome"] = "Tier 3 primary-abstract disposition: Tangeretin inhibited midazolam metabolism."
        self.assertTrue(any("tangeretin stimulation" in error for error in self.errors(e=e)))

    def test_full_text_does_not_become_tier1_from_abstract_review(self):
        a = [dict(r) for r in self.a]
        next(r for r in a if r["Evidence_ID"] == "SB-0150")["Verification_Level"] = "1"
        self.assertTrue(any("must not be promoted beyond Tier 3" in error for error in self.errors(a=a)))

    def test_shared_range_cannot_be_assigned_to_tangeretin(self):
        e = [dict(r) for r in self.e]
        next(r for r in e if r["Evidence_ID"] == "SB-0173")["Quantitative_Outcome"] += " Apparent Ki 30–50 μmol."
        self.assertTrue(any("incorrectly assigned to tangeretin" in error for error in self.errors(e=e)))

    def test_unit_and_attribution_warning_cannot_be_closed(self):
        w = [dict(r) for r in self.w]
        next(r for r in w if r["Warning_ID"] == "V19-W15")["Audit_Status"] = "RESOLVED"
        self.assertTrue(any("V19-W15 must remain open" in error for error in self.errors(w=w)))

    def test_warning_closure_requires_verification_reference(self):
        w = [dict(r) for r in self.w]
        next(r for r in w if r["Warning_ID"] == "V19-W15")["Audit_Verification_Reference"] = ""
        self.assertTrue(any("V19-W15 requires traceable" in error for error in self.errors(w=w)))

    def test_inherited_warnings_are_preserved(self):
        w = [dict(r) for r in self.w if r["Warning_ID"] != "V3-W02"]
        wa = [dict(r) for r in self.wa if r["Warning_ID"] != "V3-W02"]
        self.assertTrue(any("all 70 inherited" in error or "match uniquely" in error for error in self.errors(w=w, wa=wa)))


if __name__ == "__main__":
    unittest.main()
