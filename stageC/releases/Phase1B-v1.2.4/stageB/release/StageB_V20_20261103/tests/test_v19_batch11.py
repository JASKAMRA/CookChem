import csv
import unittest
from pathlib import Path

from scripts.validate_v19_batch11 import validate, validate_records


class V19Batch11Tests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]
        parent = self.root.parent / "StageB_V18_20261103"

        def rows(base, rel):
            with (base / rel).open(encoding="utf-8-sig", newline="") as handle:
                return list(csv.DictReader(handle))

        self.e = rows(self.root, "data/interaction_evidence.csv")
        self.a = rows(self.root, "provenance/source_audit.csv")
        self.c = rows(self.root, "provenance/claim_support_and_verification.csv")
        self.w = rows(self.root, "data/warning_ledger.csv")
        self.wa = rows(self.root, "validation/V19_warning_audit.csv")
        self.r = rows(self.root, "validation/V19_batch_011_review.csv")
        self.p = rows(self.root, "data/publication_bibliography.csv")
        self.bw = rows(parent, "data/warning_ledger.csv")

    def errors(self, e=None, a=None, w=None, wa=None):
        return validate_records(self.root, e or self.e, a or self.a, self.c, w or self.w, wa or self.wa, self.r, self.p, self.bw)

    def test_actual_batch_and_release_pass(self):
        self.assertEqual(validate(self.root), [])

    def test_three_record_batch_is_exact(self):
        self.assertEqual({r["Evidence_ID"] for r in self.r}, {"SB-0003", "SB-0004", "SB-0005"})

    def test_tier_one_source_and_cache_are_verified(self):
        for row in self.r:
            self.assertEqual(row["Verification_Tier"], "1")
            self.assertIn("PMC4898966", row["Primary_Source_URL"])
            self.assertIn("Table 1", row["Source_Locator"])

    def test_midazolam_table_values_and_conflict_are_retained(self):
        e = next(r for r in self.e if r["Evidence_ID"] == "SB-0003")
        self.assertIn("140% (117–168%)", e["Quantitative_Outcome"])
        self.assertIn("137% (112–167%)", e["Quantitative_Outcome"])
        self.assertIn("Tmax 0.66", e["Quantitative_Outcome"])
        self.assertIn("t1/2 3.03", e["Quantitative_Outcome"])
        self.assertIn("abstract prose swaps", e["Quantitative_Outcome"])

    def test_dextromethorphan_table_ratio_is_not_called_auc(self):
        e = next(r for r in self.e if r["Evidence_ID"] == "SB-0004")
        self.assertIn("979% (650–1,474%)", e["Quantitative_Outcome"])
        self.assertIn("not a measured dextromethorphan AUC", e["Quantitative_Outcome"])

    def test_losartan_internal_target_conflict_is_open(self):
        e = next(r for r in self.e if r["Evidence_ID"] == "SB-0005")
        self.assertIn("CYP2C19", e["Quantitative_Outcome"])
        self.assertIn("CYP2C9", e["Quantitative_Outcome"])
        warning = next(r for r in self.w if r["Warning_ID"] == "V19-W17")
        self.assertEqual(warning["Audit_Status"], "NEEDS_MANUAL_REVIEW")

    def test_warning_closure_mutation_is_rejected(self):
        w = [dict(r) for r in self.w]
        wa = [dict(r) for r in self.wa]
        next(r for r in w if r["Warning_ID"] == "V19-W17")["Audit_Status"] = "RESOLVED"
        next(r for r in wa if r["Warning_ID"] == "V19-W17")["V19_Status"] = "RESOLVED"
        self.assertTrue(any("V19-W17 source discrepancy must remain open" in e for e in self.errors(w=w, wa=wa)))

    def test_source_tier_downgrade_mutation_is_rejected(self):
        a = [dict(r) for r in self.a]
        next(r for r in a if r["Evidence_ID"] == "SB-0003")["Verification_Level"] = "3"
        self.assertTrue(any("source tier/date/disposition" in e for e in self.errors(a=a)))

    def test_broken_cache_pointer_mutation_is_rejected(self):
        e = [dict(r) for r in self.e]
        next(r for r in e if r["Evidence_ID"] == "SB-0004")["Source_Cache"] = "sources/selected_21.json"
        self.assertTrue(any("evidence source URL or repaired local cache pointer" in x for x in self.errors(e=e)))

    def test_wrong_full_text_outcome_mutation_is_rejected(self):
        e = [dict(r) for r in self.e]
        next(r for r in e if r["Evidence_ID"] == "SB-0005")["Quantitative_Outcome"] = "Losartan AUC increased."
        self.assertTrue(any("source-supported outcome marker absent" in x or "source URL or outcome does not match" in x for x in self.errors(e=e)))

    def test_source_audit_duplicate_is_rejected(self):
        a = [dict(r) for r in self.a] + [dict(self.a[0])]
        self.assertTrue(any("source-audit coverage must uniquely match" in e for e in self.errors(a=a)))

    def test_repaired_w10_scope_includes_all_three_rows(self):
        w10 = next(r for r in self.w if r["Warning_ID"] == "V19-W10")
        self.assertEqual(w10["Audit_Status"], "RESOLVED")
        self.assertTrue(all(eid in w10["Affected"] for eid in ("SB-0003", "SB-0004", "SB-0005")))

    def test_all_inherited_warning_ids_remain(self):
        inherited = {r["Warning_ID"] for r in self.bw}
        current = {r["Warning_ID"] for r in self.w}
        self.assertEqual(len(inherited), 70)
        self.assertTrue(inherited <= current)

    def test_missing_values_remain_missing(self):
        self.assertEqual(sum(not r.get("Quantitative_Outcome", "").strip() for r in self.e), 44)

    def test_probe_doses_and_crossover_regimen_are_recorded(self):
        for row in self.e:
            if row["Evidence_ID"] not in {"SB-0003", "SB-0004", "SB-0005"}:
                continue
            self.assertIn("300 mg", row["Dose"])
            self.assertIn("4-week washout", row["Dose"])
            self.assertIn("17 completed", row["Population"])


if __name__ == "__main__":
    unittest.main()
