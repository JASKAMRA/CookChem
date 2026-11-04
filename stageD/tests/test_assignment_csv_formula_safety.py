"""Spreadsheet-safety regression for reviewer assignment CSV exports."""
from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from stage_d.evidence_review_workflow import export_assignment_csv  # noqa: E402


class AssignmentCsvFormulaSafetyTests(unittest.TestCase):
    def test_untrusted_reviewer_and_source_text_are_not_exported_as_formulas(self):
        assignment = {
            "assignment_id": "ASG-SYNTHETIC-001",
            "source_release_id": "SYNTHETIC-TEST",
            "source_sha256": "a" * 64,
            "assigned_to": "=HYPERLINK(\"https://example.invalid\",\"review\")",
            "records": [{
                "review_id": "RV-00000000000000000001",
                "evidence_id": "SB-SYNTHETIC-001",
                "compound_id": "MOL-SYNTHETIC-001",
                "compound_source_label": "Synthetic compound",
                "drug_source_label": "Synthetic probe",
                "study_id": "STUDY-SYNTHETIC-001",
                "source_title": " \t=1+1",
                "evidence_category": "synthetic",
                "outcome_polarity_machine_triage": "unclear",
                "machine_triage_state": "IDENTITY_PENDING",
                "identity_source_label": "synthetic_unverified",
                "source_verification_status": "NOT_PERFORMED",
                "conflict_group": "",
                "source_url": "https://example.invalid/synthetic",
                "doi": "",
                "pmid": "",
                "source_locator": "@SUM(1,1)",
                "review_status": "NOT_REVIEWED",
            }],
        }

        with tempfile.TemporaryDirectory(prefix="stage-d-csv-safety-") as tmp:
            output = Path(tmp) / "assignment.csv"
            export_assignment_csv(output, assignment)
            with output.open(encoding="utf-8", newline="") as stream:
                row = next(csv.DictReader(stream))

        for column in ("assigned_to", "source_title", "source_locator"):
            with self.subTest(column=column):
                self.assertFalse(
                    row[column].lstrip(" \t\r\n\v\f\ufeff").startswith(("=", "+", "-", "@")),
                    f"untrusted {column} is spreadsheet-formula-active: {row[column]!r}",
                )
        self.assertEqual(row["review_status"], "NOT_REVIEWED")
        self.assertEqual(row["source_url"], "https://example.invalid/synthetic")


if __name__ == "__main__":
    unittest.main()
