import csv
import json
import unittest
from pathlib import Path

from scripts.validate_stageb_finalized import read_rows, validate, validate_records


class FinalizedReleaseTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]
        self.parent = self.root.parent / "StageB_V18_20261103"
        self.compounds = read_rows(self.root, "data/compound_registry.csv")
        self.evidence = read_rows(self.root, "data/interaction_evidence.csv")
        self.drugs = read_rows(self.root, "data/drug_probe_registry.csv")
        self.bibliography = read_rows(self.root, "data/publication_bibliography.csv")
        self.studies = read_rows(self.root, "data/study_registry.csv")
        self.source_audit = read_rows(self.root, "provenance/source_audit.csv")
        self.claims = read_rows(self.root, "provenance/claim_support_and_verification.csv")
        self.warnings = read_rows(self.root, "data/warning_ledger.csv")
        self.warning_audit = read_rows(self.root, "validation/V19_warning_audit.csv")
        self.baseline_warnings = read_rows(self.parent, "data/warning_ledger.csv")
        self.reviews = []
        for path in sorted((self.root / "validation").glob("V19_batch_*_review.csv")):
            self.reviews.extend(read_rows(self.root, path.relative_to(self.root).as_posix()))
        self.metadata = json.loads((self.root / "release_metadata.json").read_text(encoding="utf-8-sig"))

    def errors(self, **overrides):
        values = {
            "root": self.root,
            "compounds": self.compounds,
            "evidence": self.evidence,
            "drugs": self.drugs,
            "bibliography": self.bibliography,
            "studies": self.studies,
            "source_audit": self.source_audit,
            "claims": self.claims,
            "warnings": self.warnings,
            "warning_audit": self.warning_audit,
            "baseline_warnings": self.baseline_warnings,
            "batch_reviews": self.reviews,
            "metadata": self.metadata,
        }
        values.update(overrides)
        return validate_records(**values)

    def test_finalized_package_passes(self):
        self.assertEqual(validate(self.root), [])

    def test_canonical_counts_and_warning_dispositions(self):
        self.assertEqual(len(self.compounds), 143)
        self.assertEqual(len(self.evidence), 317)
        self.assertEqual(len(self.warnings), 88)
        observed = {}
        for row in self.warnings:
            status = row["Final_Disposition"]
            observed[status] = observed.get(status, 0) + 1
        self.assertEqual(observed, {"RESOLVED": 5, "PARTIALLY_RESOLVED": 15, "VALID": 26, "NEEDS_MANUAL_REVIEW": 40, "NOT_APPLICABLE": 2})

    def test_invalid_final_disposition_is_rejected(self):
        warnings = [dict(row) for row in self.warnings]
        warnings[0]["Final_Disposition"] = "CLOSED"
        self.assertTrue(any("final disposition" in error or "unsupported historical" in error for error in self.errors(warnings=warnings)))

    def test_status_mismatch_is_rejected(self):
        warnings = [dict(row) for row in self.warnings]
        next(row for row in warnings if row["Warning_ID"] == "V19-W01")["Final_Disposition"] = "RESOLVED"
        self.assertTrue(any("does not preserve the V19 status meaning" in error for error in self.errors(warnings=warnings)))

    def test_open_scientific_warning_cannot_be_closed(self):
        warnings = [dict(row) for row in self.warnings]
        row = next(row for row in warnings if row["Warning_ID"] == "V19-W18")
        row["Audit_Status"] = "RESOLVED"
        row["Final_Disposition"] = "RESOLVED"
        warning_audit = [dict(item) for item in self.warning_audit]
        next(item for item in warning_audit if item["Warning_ID"] == "V19-W18")["V19_Status"] = "RESOLVED"
        self.assertTrue(any("scientific uncertainty must remain open" in error for error in self.errors(warnings=warnings, warning_audit=warning_audit)))

    def test_duplicate_warning_id_is_rejected(self):
        warnings = [dict(row) for row in self.warnings] + [dict(self.warnings[-1])]
        self.assertTrue(any("duplicate Warning_ID" in error for error in self.errors(warnings=warnings)))

    def test_inherited_warning_disappearance_is_rejected(self):
        warnings = [dict(row) for row in self.warnings if row["Warning_ID"] != "V3-W02"]
        warning_audit = [dict(row) for row in self.warning_audit if row["Warning_ID"] != "V3-W02"]
        self.assertTrue(any("inherited V18 warning IDs" in error for error in self.errors(warnings=warnings, warning_audit=warning_audit)))

    def test_source_audit_coverage_loss_is_rejected(self):
        audits = [dict(row) for row in self.source_audit if row["Evidence_ID"] != "SB-0001"]
        self.assertTrue(any("source audit row count" in error or "exactly cover" in error for error in self.errors(source_audit=audits)))

    def test_release_status_cannot_revert_to_in_progress(self):
        metadata = dict(self.metadata)
        metadata["release_status"] = "SCIENTIFIC_REMEDIATION_IN_PROGRESS"
        self.assertTrue(any("required final status" in error for error in self.errors(metadata=metadata)))


if __name__ == "__main__":
    unittest.main()
