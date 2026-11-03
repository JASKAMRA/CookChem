import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_v16_warnings as v16w
import manifest_integrity


class WarningAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.w = v16w.rows(ROOT / "data/warning_ledger.csv")
        cls.c = v16w.rows(ROOT / "data/compound_registry.csv")
        cls.e = v16w.rows(ROOT / "data/interaction_evidence.csv")
        cls.s = v16w.rows(ROOT / "data/study_registry.csv")
        cls.b = v16w.rows(ROOT / "data/publication_bibliography.csv")

    def errors(self, warnings):
        return v16w.validate(warnings, self.c, self.e, self.s, self.b)

    def test_ledger_valid_and_preserves_all_v15_warning_ids(self):
        baseline = v16w.rows(ROOT.parent / "StageB_V15_20261102/data/warning_ledger.csv")
        ids = {r["Warning_ID"] for r in self.w}
        self.assertTrue({r["Warning_ID"] for r in baseline}.issubset(ids))
        self.assertEqual([], self.errors(self.w))

    def test_duplicate_and_missing_warnings_rejected(self):
        mutated = [dict(r) for r in self.w] + [dict(self.w[0])]
        self.assertTrue(any("duplicated" in e for e in self.errors(mutated)))
        ids = {r["Warning_ID"] for r in self.w}
        mutated = [r for r in self.w if r["Warning_ID"] != "V15-W01"]
        self.assertNotEqual(ids, {r["Warning_ID"] for r in mutated})

    def test_invalid_closure_and_open_scientific_warnings(self):
        mutated = [dict(r) for r in self.w]
        row = next(r for r in mutated if r["Warning_ID"] == "V15-W01")
        row["Audit_Status"] = "RESOLVED"
        row["Audit_Verification_Reference"] = ""
        self.assertTrue(any("resolved warning" in e for e in self.errors(mutated)))
        statuses = {r["Warning_ID"]: r["Audit_Status"] for r in self.w}
        self.assertEqual("STILL_VALID", statuses["V15-W01"])
        self.assertEqual("STILL_VALID", statuses["V15-W02"])
        self.assertEqual("STILL_VALID", statuses["V15-W03"])

    def test_legacy_severity_is_not_invented_and_manifest_covers_audit(self):
        self.assertTrue(all(r["Inherited_Severity"] == "NOT_RECORDED" for r in self.w))
        result = manifest_integrity.verify_manifest(ROOT, mode="exact")
        self.assertEqual("PASS", result["status"], result)
        self.assertIn("validation/V16_warning_audit.csv", manifest_integrity.load_manifest(ROOT))


if __name__ == "__main__":
    unittest.main(verbosity=2)
