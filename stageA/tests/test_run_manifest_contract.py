"""Exercise Stage A run-manifest integrity without running or overwriting outputs."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
STAGE_A = ROOT / "stageA"
SCRIPT = STAGE_A / "scripts" / "run_stage_a.py"
LOCK = STAGE_A / "stageA-requirements-py312.lock"

import importlib.util

SPEC = importlib.util.spec_from_file_location("stage_a_manifest_runner", SCRIPT)
RUNNER = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(RUNNER)


class StageARunManifestContractTests(unittest.TestCase):
    def test_manifest_records_reproducible_contract_without_repository_writes(self):
        frame_data = {
            "Record_ID": [f"SYN-{i:02d}" for i in range(10)],
            "Canonical_Molecular_ID": [f"GROUP-{i // 2}" for i in range(10)],
            "Retention_Final": [float(i + 1) for i in range(10)],
        }
        for index, column in enumerate(RUNNER.BASE_FEATURES):
            if column in RUNNER.CATEGORICAL:
                frame_data[column] = [f"category-{i % 2}" for i in range(10)]
            else:
                frame_data[column] = [float(index + i + 1) for i in range(10)]
        frame = pd.DataFrame(frame_data)

        with tempfile.TemporaryDirectory(prefix="cookrisk-stagea-manifest-") as temp:
            out = Path(temp)
            (out / "stageA_benchmark_results.csv").write_text("synthetic-output\n", encoding="utf-8")
            original_out = RUNNER.OUT
            RUNNER.OUT = out
            self.addCleanup(setattr, RUNNER, "OUT", original_out)

            RUNNER.write_run_manifest(
                frame,
                "a" * 64,
                {
                    "n_estimators": 450, "max_depth": 3, "learning_rate": 0.03,
                    "min_child_weight": 3, "subsample": 0.8,
                    "colsample_bytree": 0.8, "reg_lambda": 5.0,
                },
            )

            manifest_path = out / "stageA_run_manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["input"]["sha256"], "a" * 64)
            self.assertEqual(manifest["input"]["rows"], 10)
            self.assertEqual(manifest["input"]["path"], "stageA/input/cookchem_molecular_retention_preprocessed.csv")
            self.assertEqual(manifest["code"]["runner_sha256"], hashlib.sha256(SCRIPT.read_bytes()).hexdigest())
            self.assertEqual(manifest["dependency_lock"]["sha256"], hashlib.sha256(LOCK.read_bytes()).hexdigest())
            self.assertEqual(manifest["cross_validation"]["n_splits"], 5)
            self.assertEqual(len(manifest["cross_validation"]["folds"]), 5)
            self.assertTrue(all(fold["group_overlap_count"] == 0 for fold in manifest["cross_validation"]["folds"]))
            self.assertIn("xgboost_build", manifest["runtime"]["native_build"])
            self.assertTrue(manifest["runtime"]["native_build"]["threadpools"])
            self.assertEqual(
                manifest["outputs"]["stageA_benchmark_results.csv"],
                hashlib.sha256((out / "stageA_benchmark_results.csv").read_bytes()).hexdigest(),
            )
            self.assertNotIn(str(out), manifest_path.read_text(encoding="utf-8"))
            self.assertNotIn("timestamp", manifest)


if __name__ == "__main__":
    unittest.main()
