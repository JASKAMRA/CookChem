from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

STAGE_C = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STAGE_C / "src"))
from stage_c.deployment_package import validate_deployment_package


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _dump(path: Path, value: object) -> bytes:
    data = (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return data


def make_synthetic_package(root: Path) -> Path:
    """Create metadata-only synthetic package files; the model bytes are never loaded."""
    package = root / "StageA-SYNTHETIC-TEST-v0.0.1"
    package.mkdir(parents=True)
    feature_names = ["initial_concentration", "sample_weight"]
    payloads: dict[str, bytes] = {
        "model/synthetic-model.bin": b"SYNTHETIC PLACEHOLDER BYTES; NOT A LOADABLE MODEL\n",
        "runtime/requirements.lock": b"python==3.14.0\njoblib==1.5.2\n",
        "runtime/training_environment.lock": b"SYNTHETIC ENVIRONMENT DESCRIPTION\n",
        "features/feature_schema.json": _dump(package / "features/feature_schema.json", {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object", "feature_names": feature_names,
        }),
        "features/preprocessing.json": _dump(package / "features/preprocessing.json", {
            "feature_order": feature_names,
            "missing_value_policy": {"initial_concentration": "reject", "sample_weight": "reject"},
        }),
        "schemas/prediction_output.schema.json": _dump(package / "schemas/prediction_output.schema.json", {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object", "required": ["prediction_id", "output_sha256"],
        }),
        "data/training_input.csv": b"Record_ID,initial_concentration,sample_weight\nSYN-1,1.25,2.0\n",
        "training/train.py": b"# SYNTHETIC PLACEHOLDER; NEVER EXECUTED\n",
    }
    payloads["model/metadata.json"] = _dump(package / "model/metadata.json", {
        "model_class": "SyntheticMetadataOnlyModel",
        "feature_names": feature_names,
        "notice": "TEST FIXTURE ONLY; no estimator present",
    })
    target_fields = {
        "contract_id": "TARGET-SYN-001",
        "target_name": "Retention_Final",
        "semantic_type": "concentration_retention",
        "output_unit": "fraction",
        "numerator": "cooked concentration on the declared measurement basis",
        "denominator": "raw concentration on the same declared measurement basis",
        "measurement_basis": "fresh_weight",
    }
    payloads["target/definition.json"] = _dump(package / "target/definition.json", target_fields)
    for rel, data in payloads.items():
        if not (package / rel).exists():
            (package / rel).parent.mkdir(parents=True, exist_ok=True)
            (package / rel).write_bytes(data)

    artifacts = []
    for rel in sorted(payloads):
        data = (package / rel).read_bytes()
        artifacts.append({"path": rel, "sha256": _hash(data), "size_bytes": len(data), "media_type": "application/octet-stream"})
    digest_by_path = {row["path"]: row["sha256"] for row in artifacts}
    features = [
        {"name": "initial_concentration", "type": "number", "unit": "mg/kg", "missing_policy": "reject", "preprocessing": ["standardize"]},
        {"name": "sample_weight", "type": "number", "unit": "g", "missing_policy": "reject", "preprocessing": ["standardize"]},
    ]
    manifest = {
        "contract_version": "1.0.0",
        "package_id": "SYNTHETIC-PACKAGE-001",
        "package_version": "0.0.1",
        "package_status": "DRAFT",
        "build_date": "2026-11-04",
        "owner": "synthetic test fixture",
        "runtime_interface": "supplied_prediction_record",
        "selected_model": {
            "name": "Synthetic placeholder",
            "class": "SyntheticMetadataOnlyModel",
            "selection_decision": "synthetic fixture only; not a real model selection",
            "best_model_by_rmse": None,
            "overall_benchmark_model": None,
            "artifact_path": "model/synthetic-model.bin",
            "artifact_sha256": digest_by_path["model/synthetic-model.bin"],
            "metadata_path": "model/metadata.json",
            "metadata_sha256": digest_by_path["model/metadata.json"],
        },
        "target_contract": {
            **target_fields,
            "artifact_path": "target/definition.json",
            "sha256": digest_by_path["target/definition.json"],
            "scientific_approval": {"status": "pending"},
        },
        "runtime": {
            "python_version": "3.14.0",
            "lock_path": "runtime/requirements.lock",
            "lock_sha256": digest_by_path["runtime/requirements.lock"],
            "serialization_library": "joblib",
            "serialization_library_version": "1.5.2",
        },
        "feature_contract": {
            "schema_path": "features/feature_schema.json",
            "schema_sha256": digest_by_path["features/feature_schema.json"],
            "preprocessing_path": "features/preprocessing.json",
            "preprocessing_sha256": digest_by_path["features/preprocessing.json"],
            "ordered_feature_names": feature_names,
            "features": features,
            "engineered_feature_names": [],
        },
        "output_contract": {
            "schema_path": "schemas/prediction_output.schema.json",
            "schema_sha256": digest_by_path["schemas/prediction_output.schema.json"],
            "canonicalization": "utf8_sorted_keys_compact_json_no_nan",
            "checksum_rule": "sha256_payload_without_output_sha256",
        },
        "training_provenance": {
            "dataset_version": "SYNTHETIC-DATA-ONLY",
            "training_input_path": "data/training_input.csv",
            "training_input_sha256": digest_by_path["data/training_input.csv"],
            "training_code_path": "training/train.py",
            "training_code_sha256": digest_by_path["training/train.py"],
            "training_environment_path": "runtime/training_environment.lock",
            "training_environment_sha256": digest_by_path["runtime/training_environment.lock"],
            "record_count": 1,
            "group_count": 1,
            "feature_count": len(feature_names),
        },
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "review": {"status": "pending"},
    }
    _write_manifest(package, manifest)
    return package


def _write_manifest(package: Path, manifest: dict) -> None:
    raw = (json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")
    (package / "package_manifest.json").write_bytes(raw)
    (package / "package_manifest.sha256").write_text(_hash(raw) + "  package_manifest.json\n", encoding="utf-8")


def _read_manifest(package: Path) -> dict:
    return json.loads((package / "package_manifest.json").read_text(encoding="utf-8"))


def _refresh_artifact(package: Path, manifest: dict, path: str, data: bytes) -> None:
    artifact_path = package / path
    artifact_path.write_bytes(data)
    row = next(row for row in manifest["artifacts"] if row["path"] == path)
    row["sha256"] = _hash(data)
    row["size_bytes"] = len(data)
    for obj, path_key, hash_key in (
        (manifest["selected_model"], "artifact_path", "artifact_sha256"),
        (manifest["selected_model"], "metadata_path", "metadata_sha256"),
        (manifest["target_contract"], "artifact_path", "sha256"),
        (manifest["runtime"], "lock_path", "lock_sha256"),
        (manifest["feature_contract"], "schema_path", "schema_sha256"),
        (manifest["feature_contract"], "preprocessing_path", "preprocessing_sha256"),
        (manifest["output_contract"], "schema_path", "schema_sha256"),
        (manifest["training_provenance"], "training_input_path", "training_input_sha256"),
        (manifest["training_provenance"], "training_code_path", "training_code_sha256"),
        (manifest["training_provenance"], "training_environment_path", "training_environment_sha256"),
    ):
        if obj.get(path_key) == path:
            obj[hash_key] = row["sha256"]
    _write_manifest(package, manifest)


class DeploymentPackageValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".cookrisk-deployment-synthetic-", dir=STAGE_C / "tests")
        self.package = make_synthetic_package(Path(self.temp.name))

    def tearDown(self):
        self.temp.cleanup()

    def test_valid_synthetic_package_passes_integrity_but_never_authorizes_inference(self):
        result = validate_deployment_package(self.package)
        self.assertEqual(result["validation_status"], "PASS", result["issues"])
        self.assertEqual(result["deployment_readiness"], "PENDING_REVIEW")
        self.assertFalse(result["inference_authorized"])
        self.assertTrue(any(check["name"] == "feature_contract" and check["status"] == "PASS" for check in result["checks"]))

    def test_altered_package_artifact_hash_is_rejected(self):
        (self.package / "model/synthetic-model.bin").write_bytes(b"ALTERED SYNTHETIC CONTENT")
        result = validate_deployment_package(self.package)
        self.assertEqual(result["validation_status"], "FAIL")
        self.assertTrue(any("hash or byte count mismatch" in issue for issue in result["issues"]))

    def test_missing_runtime_file_is_rejected(self):
        (self.package / "runtime/requirements.lock").unlink()
        result = validate_deployment_package(self.package)
        self.assertEqual(result["validation_status"], "FAIL")
        self.assertTrue(any("runtime/requirements.lock" in issue for issue in result["issues"]))

    def test_bad_target_unit_fails_even_when_all_file_hashes_are_consistent(self):
        manifest = _read_manifest(self.package)
        target_doc = json.loads((self.package / "target/definition.json").read_text(encoding="utf-8"))
        target_doc["output_unit"] = "mg/kg"
        manifest["target_contract"]["output_unit"] = "mg/kg"
        _refresh_artifact(self.package, manifest, "target/definition.json", _dump(self.package / "target/definition.json", target_doc))
        result = validate_deployment_package(self.package)
        self.assertEqual(result["validation_status"], "FAIL")
        self.assertTrue(any("ratio unit" in issue for issue in result["issues"]))

    def test_missing_target_denominator_is_rejected(self):
        manifest = _read_manifest(self.package)
        manifest["target_contract"].pop("denominator")
        target_doc = json.loads((self.package / "target/definition.json").read_text(encoding="utf-8"))
        target_doc.pop("denominator")
        _refresh_artifact(self.package, manifest, "target/definition.json", _dump(self.package / "target/definition.json", target_doc))
        result = validate_deployment_package(self.package)
        self.assertEqual(result["validation_status"], "FAIL")
        self.assertTrue(any("denominator" in issue for issue in result["issues"]))

    def test_feature_preprocessing_order_mismatch_is_rejected(self):
        manifest = _read_manifest(self.package)
        preprocessing_path = self.package / "features/preprocessing.json"
        preprocessing = json.loads(preprocessing_path.read_text(encoding="utf-8"))
        preprocessing["feature_order"] = list(reversed(preprocessing["feature_order"]))
        _refresh_artifact(self.package, manifest, "features/preprocessing.json", _dump(preprocessing_path, preprocessing))
        result = validate_deployment_package(self.package)
        self.assertEqual(result["validation_status"], "FAIL")
        self.assertTrue(any("preprocessing feature_order" in issue for issue in result["issues"]))

    def test_path_traversal_in_artifact_inventory_is_rejected(self):
        manifest = _read_manifest(self.package)
        manifest["artifacts"][0]["path"] = "../outside.txt"
        _write_manifest(self.package, manifest)
        result = validate_deployment_package(self.package)
        self.assertEqual(result["validation_status"], "FAIL")
        self.assertTrue(any("traversal" in issue for issue in result["issues"]))

    def test_output_schema_wrong_draft_is_rejected(self):
        manifest = _read_manifest(self.package)
        output_path = self.package / "schemas/prediction_output.schema.json"
        output_schema = json.loads(output_path.read_text(encoding="utf-8"))
        output_schema["$schema"] = "https://json-schema.org/draft/2019-09/schema"
        _refresh_artifact(self.package, manifest, "schemas/prediction_output.schema.json", _dump(output_path, output_schema))
        result = validate_deployment_package(self.package)
        self.assertEqual(result["validation_status"], "FAIL")
        self.assertTrue(any("Draft 2020-12" in issue for issue in result["issues"]))

    def test_acceptance_schema_is_declared_and_valid_json(self):
        schema = json.loads((STAGE_C / "schemas" / "stage_a_deployment_manifest.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            return
        Draft202012Validator.check_schema(schema)


if __name__ == "__main__":
    unittest.main()
