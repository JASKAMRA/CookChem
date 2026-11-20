from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import research_data
from research_data import (
    SCIENTIFIC_LIMITATIONS,
    load_consolidated_fold_evidence,
    load_consolidated_model_evidence,
    load_historical_metric_conflicts,
    load_provenance_gap_register,
    numeric,
)


class ConsolidatedEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = load_consolidated_model_evidence()
        cls.by_id = {row["result_id"]: row for row in cls.results}

    def test_all_required_evidence_registers_load_with_expected_records(self) -> None:
        self.assertEqual(len(self.results), 33)
        self.assertEqual(len(load_consolidated_fold_evidence()), 349)
        self.assertEqual(len(load_historical_metric_conflicts()), 17)
        self.assertEqual(len(load_provenance_gap_register()), 11)

    def test_stage_a_tuned_versions_remain_separate_and_conflicted(self) -> None:
        initial = self.by_id["STAGEA-XGBoost_tuned"]
        replay = self.by_id["STAGEA-XGBOOST-TUNED-REPLAY"]
        self.assertEqual(initial["pooled_oof_r2"], "0.2832468313018399")
        self.assertEqual(initial["mean_fold_r2"], "0.40037582421724")
        self.assertEqual(replay["pooled_oof_r2"], "0.27579634550899224")
        self.assertEqual(replay["mean_fold_r2"], "0.394286907871563")
        self.assertEqual(initial["pooled_metric_status"], "CONFLICTING SAVED EVIDENCE")
        self.assertEqual(replay["mean_fold_metric_status"], "CONFLICTING SAVED EVIDENCE")

    def test_dataset_families_keep_their_own_pooled_and_mean_fold_statuses(self) -> None:
        stage_a = self.by_id["STAGEA-ExtraTrees_reference"]
        batch = self.by_id["BATCH021-ET25-molecular_grouped"]
        reconstruction = self.by_id["RECON-XGB450-molecular_grouped"]
        strict = self.by_id["STRICT338-XGB-MOLECULAR"]
        self.assertTrue(stage_a["pooled_metric_status"].startswith("REPORTED"))
        self.assertTrue(stage_a["pooled_metric_status"].endswith("PROVENANCE INCOMPLETE"))
        self.assertEqual(stage_a["mean_fold_metric_status"], "VERIFIED FROM SAVED RECORDS")
        self.assertEqual(batch["pooled_metric_status"], "VERIFIED FROM SAVED RECORDS")
        self.assertTrue(reconstruction["pooled_metric_status"].startswith("REPORTED"))
        self.assertTrue(reconstruction["pooled_metric_status"].endswith("PROVENANCE INCOMPLETE"))
        self.assertEqual(reconstruction["mean_fold_metric_status"], "VERIFIED FROM SAVED RECORDS")
        self.assertEqual(strict["pooled_metric_status"], "NOT ASSESSABLE")
        self.assertEqual(strict["pooled_oof_r2"], "")
        self.assertEqual(strict["mean_fold_metric_status"], "VERIFIED FROM SAVED RECORDS")
        self.assertNotEqual(stage_a["dataset_family"], batch["dataset_family"])
        self.assertNotEqual(batch["dataset_family"], reconstruction["dataset_family"])

    def test_friend_claim_stays_outside_verified_evidence(self) -> None:
        friend = self.by_id["FRIEND-CLAIM"]
        self.assertEqual(friend["pooled_oof_r2"], "0.3301")
        self.assertEqual(friend["mean_fold_r2"], "0.2990")
        self.assertIn("SUPPORTING RECORDS NOT FOUND", friend["pooled_metric_status"])
        self.assertEqual(friend["input_provenance_status"], "UNVERIFIED")

    def test_conflict_register_preserves_all_post1000_disagreements(self) -> None:
        rows = [r for r in load_historical_metric_conflicts() if r["conflict_id"].startswith("P21-")]
        hash_rows = [r for r in rows if "-HASH-" in r["conflict_id"]]
        differing_comparison_rows = [r for r in rows if "-ROW-" in r["conflict_id"]]
        self.assertEqual(len(hash_rows), 3)
        self.assertEqual(len(differing_comparison_rows), 12)
        self.assertTrue(all(r["status"] == "CONFLICTING SAVED EVIDENCE" for r in rows))

    def test_numeric_rejects_invalid_and_nonfinite_values_but_preserves_zero(self) -> None:
        self.assertIsNone(numeric({"x": "NaN"}, "x"))
        self.assertIsNone(numeric({"x": "Inf"}, "x"))
        self.assertIsNone(numeric({"x": "not numeric"}, "x"))
        self.assertEqual(numeric({"x": "0"}, "x"), 0.0)

    def test_missing_evidence_register_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as temporary:
            with patch.object(research_data, "FINAL_CONSOLIDATION", Path(temporary)):
                with self.assertRaisesRegex(OSError, "Saved evidence register is unavailable"):
                    load_consolidated_model_evidence()

    def test_scientific_limitations_register_has_complete_fields_and_core_topics(self) -> None:
        required = {"issue", "evidence", "effect_on_interpretation", "status", "handling"}
        self.assertGreaterEqual(len(SCIENTIFIC_LIMITATIONS), 15)
        self.assertTrue(all(required.issubset(row) for row in SCIENTIFIC_LIMITATIONS))
        issues = {row["issue"] for row in SCIENTIFIC_LIMITATIONS}
        self.assertTrue(any("Retention_Final" in item for item in issues))
        self.assertTrue(any("total-mass retention" in item for item in issues))
        self.assertTrue(any("Post1000" in item for item in issues))
        self.assertTrue(any("Strict verified subset pooled R²" == item for item in issues))
        self.assertTrue(any("Friend-reported R² claims" == item for item in issues))


if __name__ == "__main__":
    unittest.main()
