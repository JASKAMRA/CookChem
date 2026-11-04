"""Integrity and behavior checks for the Stage A benchmark.

Run from the repository root with the locked Stage A Python environment:
python -m unittest discover -s stageA/tests -v
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold


ROOT = Path(__file__).resolve().parents[2]
STAGE_A = ROOT / "stageA"
SCRIPT_PATH = STAGE_A / "scripts" / "run_stage_a.py"
SPEC = importlib.util.spec_from_file_location("stage_a_runner", SCRIPT_PATH)
RUNNER = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(RUNNER)


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


class StageAIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = pd.read_csv(STAGE_A / "input" / "cookchem_molecular_retention_preprocessed.csv")
        cls.qa = json.loads((STAGE_A / "outputs" / "stageA_qa.json").read_text())
        cls.oof = load_csv(STAGE_A / "outputs" / "stageA_oof_predictions.csv")
        cls.folds = load_csv(STAGE_A / "outputs" / "stageA_fold_results.csv")
        cls.audit = load_csv(STAGE_A / "outputs" / "stageA_validation_audit.csv")
        cls.benchmarks = {
            row["Model"]: row
            for row in load_csv(STAGE_A / "outputs" / "stageA_benchmark_results.csv")
        }

    def test_exact_stage_a_input_snapshot_and_structure(self) -> None:
        path = STAGE_A / "input" / "cookchem_molecular_retention_preprocessed.csv"
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(digest, "750124efc8b89dff1f67764064b1049b5db51fb1b2f222d4f91cd94c56945f89")
        self.assertEqual(RUNNER.verify_input_snapshot(path), digest)
        self.assertEqual(len(self.data), 1124)
        self.assertEqual(self.data["Record_ID"].nunique(), 1124)
        self.assertEqual(self.data["Canonical_Molecular_ID"].nunique(), 197)
        self.assertTrue(np.isfinite(pd.to_numeric(self.data["Retention_Final"], errors="coerce")).all())
        self.assertTrue((self.data["Retention_Final"] > -1).all())

    def test_snapshot_guard_rejects_modified_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            changed = Path(directory) / "changed.csv"
            changed.write_bytes((STAGE_A / "input" / "cookchem_molecular_retention_preprocessed.csv").read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                RUNNER.verify_input_snapshot(changed)

    def test_validation_rejects_missing_duplicate_invalid_and_changed_input(self) -> None:
        RUNNER.validate_input(self.data)
        missing = self.data.drop(columns=[RUNNER.BASE_FEATURES[0]])
        with self.assertRaisesRegex(ValueError, "missing required columns"):
            RUNNER.validate_input(missing)

        duplicate = self.data.copy()
        duplicate.loc[1, "Record_ID"] = duplicate.loc[0, "Record_ID"]
        with self.assertRaisesRegex(ValueError, "unique"):
            RUNNER.validate_input(duplicate)

        missing_group = self.data.copy()
        missing_group.loc[0, RUNNER.GROUP] = None
        with self.assertRaisesRegex(ValueError, "Canonical_Molecular_ID values"):
            RUNNER.validate_input(missing_group)

        invalid_target = self.data.copy()
        invalid_target.loc[0, RUNNER.TARGET] = -1
        with self.assertRaisesRegex(ValueError, "greater than -1"):
            RUNNER.validate_input(invalid_target)

        nonnumeric_target = self.data.copy()
        nonnumeric_target[RUNNER.TARGET] = nonnumeric_target[RUNNER.TARGET].astype(object)
        nonnumeric_target.loc[0, RUNNER.TARGET] = "not-a-number"
        with self.assertRaisesRegex(ValueError, "greater than -1"):
            RUNNER.validate_input(nonnumeric_target)

        wrong_size = self.data.iloc[:-1].copy()
        with self.assertRaisesRegex(ValueError, "dimensions"):
            RUNNER.validate_input(wrong_size)

    def test_missing_predictor_values_are_imputed_but_targets_are_required(self) -> None:
        frame = self.data.copy()
        frame.loc[0, "Temperature_C"] = np.nan
        frame.loc[1, "Food_Name_Standardized"] = None
        RUNNER.validate_input(frame)
        features = RUNNER.make_features(frame)
        encoded = RUNNER.preprocessor(features.columns.tolist()).fit_transform(features)
        self.assertTrue(np.isfinite(encoded).all())

        frame.loc[0, RUNNER.TARGET] = np.nan
        with self.assertRaisesRegex(ValueError, "greater than -1"):
            RUNNER.validate_input(frame)

    def test_groupkfold_reconstruction_matches_saved_folds_and_audit(self) -> None:
        x = RUNNER.make_features(self.data)
        y = self.data[RUNNER.TARGET].to_numpy(float)
        groups = self.data[RUNNER.GROUP].astype(str).to_numpy()
        splits = list(GroupKFold(n_splits=5).split(x, y, groups))
        record_ids = self.data["Record_ID"].astype(str).to_numpy()

        self.assertEqual(len(self.audit), 25)
        self.assertTrue(all(int(row["group_intersection_count"]) == 0 for row in self.audit))
        models = sorted({row["Model"] for row in self.oof})
        self.assertEqual(len(models), 5)
        for model in models:
            rows = [row for row in self.oof if row["Model"] == model]
            self.assertEqual(len(rows), len(self.data))
            fold_by_id = {row["Record_ID"]: int(float(row["fold"])) for row in rows}
            self.assertEqual(set(fold_by_id), set(record_ids))
            for fold_number, (train_idx, valid_idx) in enumerate(splits, 1):
                train_groups = set(groups[train_idx])
                valid_groups = set(groups[valid_idx])
                self.assertFalse(train_groups & valid_groups)
                actual_validation_ids = {record_ids[i] for i in valid_idx}
                saved_validation_ids = {rid for rid, f in fold_by_id.items() if f == fold_number}
                self.assertEqual(saved_validation_ids, actual_validation_ids)
                audit_row = next(
                    row for row in self.audit
                    if row["Model"] == model and int(row["Fold"]) == fold_number
                )
                self.assertEqual(int(audit_row["train_rows"]), len(train_idx))
                self.assertEqual(int(audit_row["validation_rows"]), len(valid_idx))
                self.assertEqual(int(audit_row["train_groups"]), len(train_groups))
                self.assertEqual(int(audit_row["validation_groups"]), len(valid_groups))

    def test_saved_oof_actuals_match_exact_training_snapshot(self) -> None:
        target_by_id = dict(zip(self.data["Record_ID"].astype(str), self.data[RUNNER.TARGET].astype(float)))
        group_by_id = dict(zip(self.data["Record_ID"].astype(str), self.data[RUNNER.GROUP].astype(str)))
        self.assertEqual(len(self.oof), 5 * len(self.data))
        seen: set[tuple[str, str]] = set()
        for row in self.oof:
            pair = (row["Model"], row["Record_ID"])
            self.assertNotIn(pair, seen)
            seen.add(pair)
            self.assertAlmostEqual(float(row["actual"]), target_by_id[row["Record_ID"]], places=12)
            self.assertEqual(row["Canonical_Molecular_ID"], group_by_id[row["Record_ID"]])
            self.assertTrue(math.isfinite(float(row["predicted"])))

    def test_metrics_independently_recalculate_from_saved_oof(self) -> None:
        for model in self.benchmarks:
            pairs = [row for row in self.oof if row["Model"] == model]
            actual = [float(row["actual"]) for row in pairs]
            predicted = [float(row["predicted"]) for row in pairs]
            mean = sum(actual) / len(actual)
            mae = sum(abs(a - p) for a, p in zip(actual, predicted)) / len(actual)
            mse = sum((a - p) ** 2 for a, p in zip(actual, predicted)) / len(actual)
            rmse = math.sqrt(mse)
            r2 = 1 - sum((a - p) ** 2 for a, p in zip(actual, predicted)) / sum((a - mean) ** 2 for a in actual)
            for name, value in (("MAE", mae), ("RMSE", rmse), ("R2", r2)):
                self.assertAlmostEqual(value, float(self.benchmarks[model][name]), places=9, msg=f"{model} {name}")

    def test_log1p_transform_and_inverse_are_present_in_training_path(self) -> None:
        source = SCRIPT_PATH.read_text()
        self.assertIn("pipe.fit(x.iloc[train_idx], np.log1p(y[train_idx]))", source)
        self.assertIn("np.expm1(np.clip(pipe.predict(x.iloc[valid_idx]), -20, 20))", source)
        target = self.data[RUNNER.TARGET].to_numpy(float)[:25]
        np.testing.assert_allclose(np.expm1(np.log1p(target)), target, rtol=1e-12, atol=1e-12)

    def test_engineered_features_match_the_documented_formulas(self) -> None:
        row = self.data.iloc[[0]]
        features = RUNNER.make_features(row)
        self.assertAlmostEqual(
            features["FE_Temperature_x_Time"].iloc[0],
            row["Temperature_C"].iloc[0] * row["Cooking_Time_min"].iloc[0],
        )
        self.assertAlmostEqual(features["FE_Log_Cooking_Time"].iloc[0], np.log1p(row["Cooking_Time_min"].iloc[0]))
        self.assertAlmostEqual(features["FE_Log_Initial_Concentration"].iloc[0], np.log1p(row["Initial_Concentration"].iloc[0]))
        self.assertAlmostEqual(features["FE_LogP_x_Temperature"].iloc[0], row["RDKit_LogP"].iloc[0] * row["Temperature_C"].iloc[0])
        self.assertAlmostEqual(features["FE_TPSA_x_Cooking_Time"].iloc[0], row["RDKit_TPSA"].iloc[0] * row["Cooking_Time_min"].iloc[0])

    def test_feature_order_and_estimator_configuration_are_locked(self) -> None:
        self.assertEqual(len(RUNNER.BASE_FEATURES), 22)
        self.assertEqual(list(RUNNER.make_features(self.data.iloc[:1]).columns[:22]), RUNNER.BASE_FEATURES)
        extra = RUNNER.model_factory("ExtraTrees_reference", {}).get_params()
        self.assertEqual((extra["n_estimators"], extra["min_samples_leaf"], extra["random_state"], extra["n_jobs"]), (300, 2, 42, 1))
        forest = RUNNER.model_factory("RandomForest", {}).get_params()
        self.assertEqual((forest["n_estimators"], forest["min_samples_leaf"], forest["random_state"], forest["n_jobs"]), (300, 2, 42, 1))
        svr = RUNNER.model_factory("RBF_SVR", {}).get_params()
        self.assertEqual((svr["C"], svr["epsilon"], svr["gamma"]), (10.0, 0.1, "scale"))
        xgb = RUNNER.model_factory("XGBoost_tuned", {"n_estimators": 450, "max_depth": 3, "learning_rate": 0.03, "min_child_weight": 3, "subsample": 0.8, "colsample_bytree": 0.8, "reg_lambda": 5.0}).get_params()
        self.assertEqual((xgb["n_estimators"], xgb["max_depth"], xgb["learning_rate"], xgb["min_child_weight"], xgb["subsample"], xgb["colsample_bytree"], xgb["reg_lambda"], xgb["random_state"], xgb["n_jobs"], xgb["tree_method"]), (450, 3, 0.03, 3, 0.8, 0.8, 5.0, 42, 1, "hist"))

    def test_serialized_oof_contract(self) -> None:
        expected = ["Model", "Record_ID", "Canonical_Molecular_ID", "actual", "predicted", "fold", "tuning"]
        with (STAGE_A / "outputs" / "stageA_oof_predictions.csv").open(newline="") as stream:
            reader = csv.DictReader(stream)
            self.assertEqual(reader.fieldnames, expected)
        self.assertEqual(len(self.oof), 5620)
        self.assertEqual({int(float(row["fold"])) for row in self.oof}, {1, 2, 3, 4, 5})


if __name__ == "__main__":
    unittest.main()
