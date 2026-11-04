"""Run the full benchmark twice in isolated trees and compare serialization."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGE_A = ROOT / "stageA"
RUNNER = STAGE_A / "scripts" / "run_stage_a.py"
INPUT = STAGE_A / "input" / "cookchem_molecular_retention_preprocessed.csv"
EXPECTED_INPUT_SHA256 = "750124efc8b89dff1f67764064b1049b5db51fb1b2f222d4f91cd94c56945f89"
SERIALIZED_OUTPUTS = (
    "stageA_benchmark_results.csv",
    "stageA_fold_results.csv",
    "stageA_oof_predictions.csv",
    "stageA_robustness.csv",
    "stageA_tuning_results.csv",
    "stageA_validation_audit.csv",
    "stageA_run_manifest.json",
)


class StageARepeatedRunTests(unittest.TestCase):
    def test_full_benchmark_repeats_byte_identically_without_touching_history(self) -> None:
        digest = hashlib.sha256(INPUT.read_bytes()).hexdigest()
        self.assertEqual(digest, EXPECTED_INPUT_SHA256)

        with tempfile.TemporaryDirectory(prefix="cookrisk-stagea-repeat-") as temporary:
            base = Path(temporary)
            outputs = []
            for run_name in ("run1", "run2"):
                project = base / run_name / "stageA"
                (project / "input").mkdir(parents=True)
                (project / "scripts").mkdir()
                (project / "outputs").mkdir()
                shutil.copy2(INPUT, project / "input" / INPUT.name)
                shutil.copy2(RUNNER, project / "scripts" / RUNNER.name)
                shutil.copy2(STAGE_A / "stageA-requirements-py312.lock", project / "stageA-requirements-py312.lock")
                completed = subprocess.run(
                    [sys.executable, str(project / "scripts" / RUNNER.name)],
                    cwd=project.parents[1],
                    capture_output=True,
                    text=True,
                    timeout=900,
                    check=False,
                )
                self.assertEqual(completed.returncode, 0, completed.stdout + "\n" + completed.stderr)
                self.assertIn("Stage A complete", completed.stdout)
                outputs.append(project / "outputs")

            for name in SERIALIZED_OUTPUTS:
                self.assertEqual((outputs[0] / name).read_bytes(), (outputs[1] / name).read_bytes(), name)

            qa1 = json.loads((outputs[0] / "stageA_qa.json").read_text())
            qa2 = json.loads((outputs[1] / "stageA_qa.json").read_text())
            self.assertEqual(qa1["input"], "stageA/input/cookchem_molecular_retention_preprocessed.csv")
            self.assertEqual(qa2["input"], "stageA/input/cookchem_molecular_retention_preprocessed.csv")
            self.assertEqual(qa1, qa2)
            self.assertEqual(qa1["input_sha256"], EXPECTED_INPUT_SHA256)

            manifest1 = json.loads((outputs[0] / "stageA_run_manifest.json").read_text())
            manifest2 = json.loads((outputs[1] / "stageA_run_manifest.json").read_text())
            self.assertEqual(manifest1, manifest2)
            self.assertEqual(manifest1["input"]["sha256"], EXPECTED_INPUT_SHA256)
            self.assertIsNotNone(manifest1["dependency_lock"]["sha256"])
            self.assertEqual(len(manifest1["input"]["columns"]), 47)
            self.assertEqual(len(manifest1["feature_contract"]["source_columns_in_order"]), 22)
            self.assertEqual(len(manifest1["feature_contract"]["derived_columns_in_order"]), 5)
            self.assertEqual(len(manifest1["cross_validation"]["folds"]), 5)
            self.assertTrue(all(fold["group_overlap_count"] == 0 for fold in manifest1["cross_validation"]["folds"]))
            for filename, digest in manifest1["outputs"].items():
                self.assertEqual(hashlib.sha256((outputs[0] / filename).read_bytes()).hexdigest(), digest)
