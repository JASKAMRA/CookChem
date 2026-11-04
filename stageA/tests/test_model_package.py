from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from model_package import ModelPackageError, validate_model_package  # noqa: E402


TRAINING_HASH = "a" * 64


class ModelPackageTests(unittest.TestCase):
    def build_package(self, directory: Path, *, model_name="model.bin", model_bytes=b"synthetic model") -> None:
        feature_names = ["temperature", "food"]
        payloads = {
            model_name: model_bytes,
            "preprocessing.bin": b"synthetic preprocessing",
            "feature_schema.json": json.dumps({"feature_names": feature_names}).encode(),
            "stage_a_runner.py": b"synthetic runner",
            "stage_a.lock": b"synthetic dependency lock",
            "stageA_run_manifest.json": json.dumps({
                "input": {"sha256": TRAINING_HASH},
                "code": {"runner_sha256": hashlib.sha256(b"synthetic runner").hexdigest()},
                "dependency_lock": {"sha256": hashlib.sha256(b"synthetic dependency lock").hexdigest()},
                "feature_contract": {"columns_sha256": hashlib.sha256("\n".join(feature_names).encode()).hexdigest()},
            }).encode(),
        }
        artifacts = {}
        for role, name in (
            ("model", model_name), ("preprocessing", "preprocessing.bin"),
            ("feature_schema", "feature_schema.json"), ("run_manifest", "stageA_run_manifest.json"),
            ("runner", "stage_a_runner.py"), ("dependency_lock", "stage_a.lock"),
        ):
            (directory / name).write_bytes(payloads[name])
            artifacts[role] = {"path": name, "sha256": hashlib.sha256(payloads[name]).hexdigest()}
        (directory / "model_package_manifest.json").write_text(json.dumps({
            "package_schema_version": "1.0.0",
            "training_data": {"sha256": TRAINING_HASH},
            "run_manifest_sha256": artifacts["run_manifest"]["sha256"],
            "artifacts": artifacts,
        }), encoding="utf-8")

    def test_verified_package_is_integrity_only_and_never_enables_inference(self):
        with tempfile.TemporaryDirectory(prefix="stage-a-model-package-") as temp:
            root = Path(temp)
            self.build_package(root)
            result = validate_model_package(root, expected_training_snapshot_sha256=TRAINING_HASH)
        self.assertEqual(result["package_integrity"], "VERIFIED")
        self.assertFalse(result["inference_enabled"])
        self.assertEqual(result["deployment_status"], "BLOCKED_PENDING_SCIENTIFIC_APPROVAL_AND_RUNTIME_AUTHORIZATION")
        self.assertEqual(result["feature_names"], ["temperature", "food"])

    def test_wrong_training_snapshot_and_tampered_artifacts_fail_closed(self):
        with tempfile.TemporaryDirectory(prefix="stage-a-model-package-") as temp:
            root = Path(temp)
            self.build_package(root)
            with self.assertRaisesRegex(ModelPackageError, "training-data hash"):
                validate_model_package(root, expected_training_snapshot_sha256="c" * 64)
            (root / "model.bin").write_bytes(b"changed")
            with self.assertRaisesRegex(ModelPackageError, "SHA-256 mismatch"):
                validate_model_package(root, expected_training_snapshot_sha256=TRAINING_HASH)

    def test_oof_prediction_file_cannot_satisfy_model_artifact(self):
        with tempfile.TemporaryDirectory(prefix="stage-a-model-package-") as temp:
            root = Path(temp)
            self.build_package(root, model_name="stageA_oof_predictions.csv")
            with self.assertRaisesRegex(ModelPackageError, "OOF/prediction"):
                validate_model_package(root, expected_training_snapshot_sha256=TRAINING_HASH)

    def test_artifact_path_escape_and_duplicate_feature_names_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix="stage-a-model-package-") as temp:
            root = Path(temp)
            self.build_package(root)
            manifest_path = root / "model_package_manifest.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["artifacts"]["model"]["path"] = "../outside.bin"
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ModelPackageError, "safe relative path"):
                validate_model_package(root, expected_training_snapshot_sha256=TRAINING_HASH)

            self.build_package(root)
            (root / "feature_schema.json").write_text('{"feature_names":["x","x"]}')
            manifest = json.loads(manifest_path.read_text())
            manifest["artifacts"]["feature_schema"]["sha256"] = hashlib.sha256((root / "feature_schema.json").read_bytes()).hexdigest()
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ModelPackageError, "unique strings"):
                validate_model_package(root, expected_training_snapshot_sha256=TRAINING_HASH)


if __name__ == "__main__":
    unittest.main()
