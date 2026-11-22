"""Release and OOF contract tests for the two additive pages."""
from __future__ import annotations

import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from extension_data import (
    DESIGNS,
    STAGEB_DIR,
    STAGEB_TABLES,
    _verified_csv,
    error_metrics,
    load_reconstruction_errors,
    load_stageb_finalized,
)
from research_data import load_consolidated_fold_evidence, load_consolidated_model_evidence


class ErrorAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.groups, cls.metrics, cls.dataset_hash = load_reconstruction_errors()

    def test_exact_reconstruction_coverage_and_saved_metrics(self) -> None:
        self.assertEqual(set(self.groups), set(DESIGNS))
        self.assertEqual({key: len(rows) for key, rows in self.groups.items()},
                         {"molecular_grouped": 1016, "source_held_out": 1016})
        self.assertEqual({row["observation_id"] for row in self.groups[DESIGNS[0]]},
                         {row["observation_id"] for row in self.groups[DESIGNS[1]]})
        expected = {
            "molecular_grouped": (0.05983078290531, 91.32814954002, 406.11724646066, 22.61304904526, 111.41231389605),
            "source_held_out": (-0.07370962306226, 115.43291196737, 434.00211099624, 36.36770429452, 139.92624557280),
        }
        names = ("r2", "mae", "rmse", "median_absolute_error", "p90_absolute_error")
        for design, values in expected.items():
            for name, value in zip(names, values):
                self.assertTrue(math.isclose(self.metrics[design][name], value, abs_tol=1e-7), (design, name))

    def test_residuals_and_group_holdout(self) -> None:
        for design, rows in self.groups.items():
            field = "canonical_molecular_id" if design == "molecular_grouped" else "doi"
            self.assertEqual({row["fold"] for row in rows}, set(range(1, 6)))
            for row in rows:
                self.assertAlmostEqual(row["residual"], row["actual"] - row["predicted"])
                self.assertAlmostEqual(row["absolute_error"], abs(row["residual"]))
            for fold in range(1, 6):
                test = {row[field] for row in rows if row["fold"] == fold}
                train = {row[field] for row in rows if row["fold"] != fold}
                self.assertFalse(test & train)

    def test_results_register_matches_error_analysis(self) -> None:
        results = {row["evaluation_protocol"]: row for row in load_consolidated_model_evidence()
                   if row["dataset_family"] == "Verified Reconstruction ACR"}
        folds = [row for row in load_consolidated_fold_evidence()
                 if row["dataset_family"] == "Verified Reconstruction ACR"]
        self.assertEqual(set(results), set(DESIGNS))
        for design in DESIGNS:
            self.assertEqual(int(results[design]["row_count"]), len(self.groups[design]))
            self.assertEqual(results[design]["dataset_identity"].split(";")[0], self.dataset_hash)
            self.assertTrue(math.isclose(float(results[design]["pooled_oof_r2"]),
                                         self.metrics[design]["r2"], abs_tol=1e-12))
            saved_folds = {int(row["fold"]): row for row in folds if row["evaluation_protocol"] == design}
            self.assertEqual(set(saved_folds), set(range(1, 6)))
            calculated_fold_r2 = []
            for fold, saved in saved_folds.items():
                calculated = error_metrics([row for row in self.groups[design] if row["fold"] == fold])
                self.assertEqual(int(saved["n_test"]), calculated["n"])
                for metric, column in (("r2", "fold_r2"), ("mae", "fold_mae"), ("rmse", "fold_rmse")):
                    self.assertTrue(math.isclose(float(saved[column]), calculated[metric], abs_tol=1e-8))
                calculated_fold_r2.append(calculated["r2"])
            self.assertTrue(math.isclose(float(results[design]["mean_fold_r2"]),
                                         sum(calculated_fold_r2) / 5, abs_tol=1e-12))

    def test_changed_csv_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "predictions.csv"
            path.write_text("changed\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "integrity check failed"):
                _verified_csv(path, "0" * 64)


class StageBFinalizedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tables = load_stageb_finalized()

    def test_counts_and_references(self) -> None:
        expected = {"compounds": 143, "evidence": 317, "drugs": 133,
                    "bibliography": 163, "studies": 161, "warnings": 88}
        self.assertEqual({key: len(self.tables[key]) for key in expected}, expected)
        for row in self.tables["evidence"]:
            self.assertIn(row["Compound_ID"], self.tables["compound_by_id"])
            self.assertIn(row["Study_ID"], self.tables["study_by_id"])
            if row["PMID"]:
                self.assertIn(row["PMID"], self.tables["bibliography_by_pmid"])

    def test_crlf_checkout_is_disclosed_and_other_changes_rejected(self) -> None:
        self.assertIn("CRLF", self.tables["integrity_note"])
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "changed.csv"
            path.write_bytes(b"a,b\r\n1,CHANGED\r\n")
            with self.assertRaisesRegex(ValueError, "integrity check failed"):
                _verified_csv(path, "0" * 64, allow_crlf_checkout=True)

    def test_lf_checkout_loads_same_finalized_release(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            checkout = Path(temporary)
            (checkout / "manifests").mkdir()
            (checkout / "data").mkdir()
            relative_paths = ["manifests/SHA256SUMS.json"] + [f"data/{filename}" for filename, _ in STAGEB_TABLES.values()]
            for relative in relative_paths:
                raw = (STAGEB_DIR / relative).read_bytes()
                (checkout / relative).write_bytes(raw.replace(b"\r\n", b"\n"))
            with patch("extension_data.STAGEB_DIR", checkout):
                restored = load_stageb_finalized()
            for name in STAGEB_TABLES:
                self.assertEqual(restored[name], self.tables[name])


if __name__ == "__main__":
    unittest.main()
