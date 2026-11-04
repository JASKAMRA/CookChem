"""Fail-closed validation for a future Stage A deployable model package.

This module verifies package provenance only. It deliberately does not load
pickle/joblib files or perform inference. OOF predictions are evaluation
artifacts and can never satisfy the model-artifact requirement.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any


class ModelPackageError(ValueError):
    """Raised when a model package is incomplete or fails integrity checks."""


_REQUIRED_ARTIFACTS = {"model", "preprocessing", "feature_schema", "run_manifest", "runner", "dependency_lock"}
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ModelPackageError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def validate_model_package(
    package_dir: str | Path,
    *,
    expected_training_snapshot_sha256: str,
) -> dict[str, Any]:
    """Verify package hashes and contract; never treats OOF output as inference.

    A successful result means only that package files match their manifest and
    training snapshot. Scientific approval and runtime deployment authorization
    remain external, and this function does not enable inference.
    """
    root = Path(package_dir).resolve(strict=True)
    manifest_path = root / "model_package_manifest.json"
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise ModelPackageError("model_package_manifest.json is missing or not a regular file")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ModelPackageError(f"Invalid model package manifest: {exc}") from None
    if not isinstance(manifest, dict) or manifest.get("package_schema_version") != "1.0.0":
        raise ModelPackageError("Unsupported model package schema version")

    expected = expected_training_snapshot_sha256.lower()
    if not _SHA256.fullmatch(expected):
        raise ModelPackageError("Expected training snapshot hash must be SHA-256")
    training = manifest.get("training_data")
    if not isinstance(training, Mapping) or training.get("sha256") != expected:
        raise ModelPackageError("Package training-data hash does not match the verified snapshot")

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict) or set(artifacts) != _REQUIRED_ARTIFACTS:
        raise ModelPackageError("Package must contain exactly model, preprocessing, and feature_schema artifacts")
    verified: dict[str, str] = {}
    for role, entry in artifacts.items():
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256"}:
            raise ModelPackageError(f"Artifact {role!r} requires only path and sha256")
        relative = entry["path"]
        if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
            raise ModelPackageError(f"Artifact {role!r} path must be a safe relative path")
        lowered = Path(relative).name.casefold()
        if role == "model" and any(token in lowered for token in ("oof", "out_of_fold", "predictions")):
            raise ModelPackageError("OOF/prediction outputs cannot be used as a model artifact")
        artifact_path = root / relative
        try:
            resolved_artifact = artifact_path.resolve(strict=True)
            resolved_artifact.relative_to(root)
        except (OSError, ValueError):
            raise ModelPackageError(f"Artifact {role!r} is missing or escapes the package directory") from None
        if artifact_path.is_symlink() or not resolved_artifact.is_file():
            raise ModelPackageError(f"Artifact {role!r} is missing or not a regular file")
        digest = hashlib.sha256(resolved_artifact.read_bytes()).hexdigest()
        declared = entry["sha256"]
        if not isinstance(declared, str) or not _SHA256.fullmatch(declared) or digest != declared:
            raise ModelPackageError(f"Artifact {role!r} SHA-256 mismatch")
        verified[role] = digest

    try:
        feature_schema = json.loads(
            (root / artifacts["feature_schema"]["path"]).read_text(encoding="utf-8"),
            object_pairs_hook=_unique_object,
        )
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ModelPackageError(f"Invalid feature schema JSON: {exc}") from None
    if not isinstance(feature_schema, dict) or not isinstance(feature_schema.get("feature_names"), list) or not feature_schema["feature_names"]:
        raise ModelPackageError("Feature schema must declare a nonempty ordered feature_names list")
    names = feature_schema["feature_names"]
    if any(not isinstance(name, str) or not name for name in names) or len(set(names)) != len(names):
        raise ModelPackageError("Feature schema names must be nonempty, unique strings in order")
    run_manifest_entry = artifacts["run_manifest"]
    if manifest.get("run_manifest_sha256") != verified["run_manifest"]:
        raise ModelPackageError("Stage A run-manifest hash does not match its package artifact")
    try:
        run_manifest = json.loads(
            (root / run_manifest_entry["path"]).read_text(encoding="utf-8"),
            object_pairs_hook=_unique_object,
        )
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ModelPackageError(f"Invalid Stage A run manifest: {exc}") from None
    if not isinstance(run_manifest, Mapping):
        raise ModelPackageError("Stage A run manifest must be a JSON object")
    run_input = run_manifest.get("input")
    code = run_manifest.get("code")
    dependency_lock = run_manifest.get("dependency_lock")
    feature_contract = run_manifest.get("feature_contract")
    if any(not isinstance(section, Mapping) for section in (run_input, code, dependency_lock, feature_contract)):
        raise ModelPackageError("Stage A run manifest lacks input, code, dependency-lock, or feature contracts")
    recorded_training_hash = run_input.get("sha256")
    if recorded_training_hash != expected:
        raise ModelPackageError("Stage A run manifest does not identify the verified training snapshot")
    if code.get("runner_sha256") != verified["runner"]:
        raise ModelPackageError("Packaged runner does not match the Stage A run manifest")
    if dependency_lock.get("sha256") != verified["dependency_lock"]:
        raise ModelPackageError("Packaged dependency lock does not match the Stage A run manifest")
    feature_digest = hashlib.sha256("\n".join(names).encode("utf-8")).hexdigest()
    if feature_contract.get("columns_sha256") != feature_digest:
        raise ModelPackageError("Feature schema order does not match the Stage A run manifest")

    return {
        "package_integrity": "VERIFIED",
        "training_snapshot_sha256": expected,
        "artifact_sha256": verified,
        "feature_names": names,
        "inference_enabled": False,
        "deployment_status": "BLOCKED_PENDING_SCIENTIFIC_APPROVAL_AND_RUNTIME_AUTHORIZATION",
    }
