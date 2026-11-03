import csv
import unittest
from pathlib import Path

from scripts.validate_v19_batch12 import validate, validate_records


class V19Batch12Tests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]
        parent = self.root.parent / "StageB_V18_20261103"

        def rows(base, rel):
            with (base / rel).open(encoding="utf-8-sig", newline="") as handle:
                return list(csv.DictReader(handle))

        self.e = rows(self.root, "data/interaction_evidence.csv")
        self.a = rows(self.root, "provenance/source_audit.csv")
        self.c = rows(self.root, "provenance/claim_support_and_verification.csv")
        self.p = rows(self.root, "data/publication_bibliography.csv")
        self.w = rows(self.root, "data/warning_ledger.csv")
        self.wa = rows(self.root, "validation/V19_warning_audit.csv")
        self.r = rows(self.root, "validation/V19_batch_012_review.csv")
        self.bw = rows(parent, "data/warning_ledger.csv")

    def errors(self, e=None, a=None, w=None, wa=None, p=None):
        return validate_records(self.root, e or self.e, a or self.a, self.c, p or self.p, w or self.w, wa or self.wa, self.r, self.bw)

    def test_actual_batch_and_release_pass(self):
        self.assertEqual(validate(self.root), [])

    def test_exactly_one_tier_three_record_was_reviewed(self):
        self.assertEqual(len(self.r), 1)
        self.assertEqual(self.r[0]["Evidence_ID"], "SB-0013")
        self.assertEqual(self.r[0]["Verification_Tier"], "3")

    def test_abstract_values_and_unspecified_auc_interval_are_preserved(self):
        e = next(r for r in self.e if r["Evidence_ID"] == "SB-0013")
        self.assertIn("406.9 vs 767 ng/mL", e["Quantitative_Outcome"])
        self.assertIn("3403.7 vs 5724.7 ng·h/mL", e["Quantitative_Outcome"])
        self.assertIn("does not state the AUC interval", e["Quantitative_Outcome"])
        self.assertIn("no AUC0–t or AUC0–∞ label is inferred", e["Quantitative_Outcome"])

    def test_dose_and_sequential_design_are_source_supported(self):
        e = next(r for r in self.e if r["Evidence_ID"] == "SB-0013")
        self.assertIn("Piperine 20 mg", e["Dose"])
        self.assertIn("fexofenadine 120 mg", e["Dose"])
        self.assertIn("10 days", e["Dose"])
        self.assertIn("two-period sequential", e["Study_Design"])

    def test_local_metadata_cache_is_valid_and_all_pointers_match(self):
        e = next(r for r in self.e if r["Evidence_ID"] == "SB-0013")
        a = next(r for r in self.a if r["Evidence_ID"] == "SB-0013")
        p = next(r for r in self.p if r["PMID"] == "27981349")
        self.assertEqual(e["Source_Cache"], a["Source_Cache"])
        self.assertEqual(p["Source"], e["Source_Cache"])
        self.assertTrue((self.root / e["Source_Cache"]).is_file())

    def test_w10_repair_is_kept_resolved_and_traced(self):
        w10 = next(r for r in self.w if r["Warning_ID"] == "V19-W10")
        self.assertEqual(w10["Audit_Status"], "RESOLVED")
        self.assertIn("SB-0013", w10["Affected"])
        self.assertIn("27981349", w10["Affected"])
        self.assertIn("V19-012", next(r for r in self.wa if r["Warning_ID"] == "V19-W10")["V19_Recheck_Status"])

    def test_w18_is_open_for_full_text_adjudication(self):
        w18 = next(r for r in self.w if r["Warning_ID"] == "V19-W18")
        self.assertEqual(w18["Audit_Status"], "NEEDS_MANUAL_REVIEW")
        self.assertIn("AUC interval", w18["Description"])

    def test_unsupported_warning_closure_mutation_is_rejected(self):
        w = [dict(r) for r in self.w]
        wa = [dict(r) for r in self.wa]
        next(r for r in w if r["Warning_ID"] == "V19-W18")["Audit_Status"] = "RESOLVED"
        next(r for r in wa if r["Warning_ID"] == "V19-W18")["V19_Status"] = "RESOLVED"
        self.assertTrue(any("V19-W18 AUC interval warning must remain open" in x for x in self.errors(w=w, wa=wa)))

    def test_fabricated_auc_interval_mutation_is_rejected(self):
        e = [dict(r) for r in self.e]
        row = next(r for r in e if r["Evidence_ID"] == "SB-0013")
        row["Quantitative_Outcome"] = row["Quantitative_Outcome"].replace("no AUC0–t or AUC0–∞ label is inferred", "AUC0–∞")
        self.assertTrue(any("must not infer an AUC interval" in x for x in self.errors(e=e)))

    def test_inflated_verification_tier_mutation_is_rejected(self):
        a = [dict(r) for r in self.a]
        next(r for r in a if r["Evidence_ID"] == "SB-0013")["Verification_Level"] = "1"
        self.assertTrue(any("must remain Tier 3" in x for x in self.errors(a=a)))

    def test_broken_cache_pointer_mutation_is_rejected(self):
        e = [dict(r) for r in self.e]
        next(r for r in e if r["Evidence_ID"] == "SB-0013")["Source_Cache"] = "sources/selected_32.json"
        self.assertTrue(any("metadata cache pointer is broken" in x for x in self.errors(e=e)))

    def test_doi_mutation_is_rejected(self):
        e = [dict(r) for r in self.e]
        next(r for r in e if r["Evidence_ID"] == "SB-0013")["DOI"] = "10.1000/fabricated"
        self.assertTrue(any("attribution mismatch" in x for x in self.errors(e=e)))

    def test_all_inherited_warning_ids_remain(self):
        inherited = {r["Warning_ID"] for r in self.bw}
        current = {r["Warning_ID"] for r in self.w}
        self.assertEqual(len(inherited), 70)
        self.assertTrue(inherited <= current)

    def test_blank_outcomes_are_not_filled_by_assumption(self):
        self.assertEqual(sum(not r.get("Quantitative_Outcome", "").strip() for r in self.e), 44)


if __name__ == "__main__":
    unittest.main()
