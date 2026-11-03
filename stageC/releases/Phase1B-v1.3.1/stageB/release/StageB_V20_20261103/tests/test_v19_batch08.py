"""Mutation tests for abstract-only V19-008 paclitaxel records and warning history."""
import csv
import unittest
from pathlib import Path

from scripts.validate_v19_batch08 import TARGETS, validate, validate_records


class V19Batch08Tests(unittest.TestCase):
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
        self.r = read(self.root, "validation/V19_batch_008_review.csv")
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

    def test_all_nine_abstract_dispositions_match_review_rows(self):
        outcomes = {r["Evidence_ID"]: r["Quantitative_Outcome"] for r in self.e if r["Evidence_ID"] in TARGETS}
        reviewed = {r["Evidence_ID"]: r["Verified_Outcome"] for r in self.r}
        self.assertEqual(set(outcomes), TARGETS)
        self.assertEqual(outcomes, reviewed)
        self.assertTrue(all("not inferred" in value for value in outcomes.values()))

    def test_no_inhibition_is_not_expressed_as_zero_or_absolute_safety(self):
        e = [dict(r) for r in self.e]
        row = next(r for r in e if r["Evidence_ID"] == "SB-0116")
        row["Limitations"] = "No interaction; safe."
        self.assertTrue(any("null finding is overstated" in error for error in self.errors(e=e)))

    def test_abstract_tier_cannot_be_upgraded_without_full_text(self):
        a = [dict(r) for r in self.a]
        next(r for r in a if r["Evidence_ID"] == "SB-0113")["Verification_Level"] = "1"
        self.assertTrue(any("must remain Tier 3" in error for error in self.errors(a=a)))

    def test_unsupported_ic50_value_is_rejected(self):
        e = [dict(r) for r in self.e]
        row = next(r for r in e if r["Evidence_ID"] == "SB-0113")
        row["Quantitative_Outcome"] += " IC50 = 2 µM."
        self.assertTrue(any("unsupported quantitative potency" in error for error in self.errors(e=e)))

    def test_closure_requires_corrected_underlying_classifications(self):
        e = [dict(r) for r in self.e]
        next(r for r in e if r["Evidence_ID"] == "SB-0118")["Evidence_Level"] = "formulation"
        self.assertTrue(any("individual compound was not reclassified" in error for error in self.errors(e=e)))

    def test_manual_review_discrepancies_remain_open(self):
        w = [dict(r) for r in self.w]
        next(r for r in w if r["Warning_ID"] == "V19-W13")["Audit_Status"] = "RESOLVED"
        self.assertTrue(any("must remain open for manual review" in error for error in self.errors(w=w)))

    def test_inherited_warning_ids_cannot_disappear(self):
        w = [dict(r) for r in self.w if r["Warning_ID"] != "V3-W02"]
        wa = [dict(r) for r in self.wa if r["Warning_ID"] != "V3-W02"]
        self.assertTrue(any("all 70 inherited" in error or "match uniquely" in error for error in self.errors(w=w, wa=wa)))

    def test_review_must_cover_exact_evidence_id_set(self):
        review = [dict(r) for r in self.r if r["Evidence_ID"] != "SB-0121"]
        self.assertTrue(any("cover exactly" in error for error in self.errors(r=review)))

    def test_metadata_locator_repair_is_auditable(self):
        wa = [dict(r) for r in self.wa]
        next(r for r in wa if r["Warning_ID"] == "V19-W10")["V19_Recheck_Status"] = "RESOLVED_IN_V19-007"
        self.assertTrue(any("Batch 008 repair history" in error for error in self.errors(wa=wa)))


if __name__ == "__main__":
    unittest.main()
