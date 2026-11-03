"""Validate a supplied Stage A deployment package without loading Stage A.

The validator checks package metadata, contained paths, hashes, and feature,
target, runtime, and output-contract consistency. It never imports a model,
executes a transformation, predicts, or grants scientific approval.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any


_SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
_RATIO_UNITS = {"%", "percent", "percentage", "fraction", "1", "unitless"}
_SEMANTICS = {"apparent_concentration_ratio", "concentration_retention", "total_mass_retention", "other"}
_MEASUREMENT_BASES = {"fresh_weight", "dry_weight", "cooked_weight", "volume", "total_mass", "source_native", "other"}


class DeploymentPackageError(ValueError):
    """Raised internally when package metadata is structurally unsafe or inconsistent."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DeploymentPackageError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_relative_path(root: Path, value: Any) -> Path:
    raw = str(value or "")
    if not raw or "\\" in raw or ":" in raw:
        raise DeploymentPackageError("Artifact paths must be nonempty POSIX relative paths")
    rel = PurePosixPath(raw)
    if rel.is_absolute() or any(part in {"", ".", ".."} for part in rel.parts):
        raise DeploymentPackageError("Artifact path is absolute or contains traversal segments")
    candidate = root.joinpath(*rel.parts)
    cursor = root
    for part in rel.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise DeploymentPackageError(f"Symbolic links are not allowed in package paths: {raw}")
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError):
        raise DeploymentPackageError(f"Artifact path is missing or escapes package root: {raw}") from None
    if not resolved.is_file():
        raise DeploymentPackageError(f"Artifact is not a regular file: {raw}")
    return resolved


def _read_json(root: Path, rel_path: Any) -> tuple[dict[str, Any], bytes]:
    path = _safe_relative_path(root, rel_path)
    raw = path.read_bytes()
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError, DeploymentPackageError):
        raise DeploymentPackageError(f"Expected valid UTF-8 JSON at {rel_path}") from None
    if not isinstance(value, dict):
        raise DeploymentPackageError(f"Expected a JSON object at {rel_path}")
    return value, raw


def _get_path_hash_pair(obj: Mapping[str, Any], path_key: str, hash_key: str, label: str) -> tuple[str, str]:
    path = str(obj.get(path_key) or "")
    digest = str(obj.get(hash_key) or "").lower()
    if not path:
        raise DeploymentPackageError(f"{label}.{path_key} is required")
    if not _SHA256.fullmatch(digest):
        raise DeploymentPackageError(f"{label}.{hash_key} must be a SHA-256 digest")
    return path, digest


def validate_deployment_package(package_dir: str | Path) -> dict[str, Any]:
    """Audit a supplied metadata-only package; never load or execute its model.

    Returns `validation_status=PASS` when package integrity/contract checks pass,
    but always returns `deployment_readiness=PENDING_REVIEW` and
    `inference_authorized=False`. Human scientific and operational review is not
    inferable from files or metadata alone.
    """
    checks: list[dict[str, str]] = []
    issues: list[str] = []

    def record(name: str, status: str, detail: str) -> None:
        checks.append({"name": name, "status": status, "detail": detail})
        if status == "FAIL":
            issues.append(detail)

    supplied_root = Path(package_dir)
    try:
        if supplied_root.is_symlink():
            raise DeploymentPackageError("Package root must not be a symbolic link")
        root = supplied_root.resolve(strict=True)
        if not root.is_dir():
            raise DeploymentPackageError("Package root must be a directory")
        record("package_root", "PASS", "Package root is an existing directory.")
    except (OSError, DeploymentPackageError) as exc:
        record("package_root", "FAIL", str(exc))
        return _result(checks, issues)

    manifest_path = root / "package_manifest.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        record("manifest_file", "FAIL", "package_manifest.json is missing or not a regular file.")
        return _result(checks, issues)
    raw_manifest = manifest_path.read_bytes()
    try:
        manifest = json.loads(raw_manifest.decode("utf-8"), object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError, DeploymentPackageError):
        record("manifest_json", "FAIL", "package_manifest.json is not valid UTF-8 JSON with unique object keys.")
        return _result(checks, issues)
    if not isinstance(manifest, dict):
        record("manifest_json", "FAIL", "package_manifest.json must contain a JSON object.")
        return _result(checks, issues)
    record("manifest_json", "PASS", "Manifest JSON parses with duplicate keys rejected.")

    sidecar = root / "package_manifest.sha256"
    try:
        if sidecar.is_symlink() or not sidecar.is_file():
            raise DeploymentPackageError("Detached package_manifest.sha256 is missing or not a regular file")
        expected_manifest_hash = sidecar.read_text(encoding="utf-8").strip().split()[0].lower()
        if not _SHA256.fullmatch(expected_manifest_hash) or expected_manifest_hash != _sha256_bytes(raw_manifest):
            raise DeploymentPackageError("Detached manifest checksum does not match package_manifest.json")
        record("manifest_checksum", "PASS", "Detached manifest checksum matches the exact manifest bytes.")
    except (OSError, UnicodeDecodeError, IndexError, DeploymentPackageError) as exc:
        record("manifest_checksum", "FAIL", str(exc))

    required_top = {
        "contract_version", "package_id", "package_version", "package_status", "build_date", "owner",
        "runtime_interface", "selected_model", "target_contract", "runtime", "feature_contract",
        "output_contract", "training_provenance", "artifact_count", "artifacts", "review",
    }
    missing_top = sorted(required_top - set(manifest))
    if missing_top:
        record("manifest_fields", "FAIL", "Missing required manifest fields: " + ", ".join(missing_top))
    else:
        record("manifest_fields", "PASS", "Required package and scientific contract fields are present.")
    if manifest.get("contract_version") != "1.0.0":
        record("contract_version", "FAIL", "Unsupported deployment manifest contract_version.")
    else:
        record("contract_version", "PASS", "Manifest contract version is 1.0.0.")
    try:
        if not str(manifest.get("package_id") or "").strip():
            raise DeploymentPackageError("package_id is required")
        if not re.fullmatch(r"\d+\.\d+\.\d+", str(manifest.get("package_version") or "")):
            raise DeploymentPackageError("package_version must use MAJOR.MINOR.PATCH")
        if manifest.get("package_status") not in {"DRAFT", "REVIEW_PENDING", "APPROVED"}:
            raise DeploymentPackageError("package_status is invalid")
        date.fromisoformat(str(manifest.get("build_date") or ""))
        if not str(manifest.get("owner") or "").strip() or manifest.get("runtime_interface") != "supplied_prediction_record":
            raise DeploymentPackageError("owner and supplied_prediction_record runtime_interface are required")
        record("package_metadata", "PASS", "Package identity, version, date, owner, and interface are present.")
    except (DeploymentPackageError, ValueError) as exc:
        record("package_metadata", "FAIL", str(exc))

    inventory: dict[str, tuple[str, int]] = {}
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        record("artifact_inventory", "FAIL", "artifacts must be a nonempty list.")
    else:
        seen: set[str] = set()
        artifact_failures: list[str] = []
        for index, item in enumerate(artifacts):
            if not isinstance(item, Mapping):
                artifact_failures.append(f"artifacts[{index}] must be an object")
                continue
            rel = str(item.get("path") or "")
            digest = str(item.get("sha256") or "").lower()
            if rel in seen:
                artifact_failures.append(f"duplicate artifact path: {rel}")
                continue
            seen.add(rel)
            if rel in {"package_manifest.json", "package_manifest.sha256"}:
                artifact_failures.append(f"manifest cannot list itself as an artifact: {rel}")
                continue
            if not _SHA256.fullmatch(digest):
                artifact_failures.append(f"invalid SHA-256 for artifact: {rel}")
                continue
            if type(item.get("size_bytes")) is not int or item["size_bytes"] < 0:
                artifact_failures.append(f"invalid size_bytes for artifact: {rel}")
                continue
            if not str(item.get("media_type") or "").strip():
                artifact_failures.append(f"missing media_type for artifact: {rel}")
                continue
            try:
                path = _safe_relative_path(root, rel)
                data = path.read_bytes()
            except (OSError, DeploymentPackageError) as exc:
                artifact_failures.append(str(exc))
                continue
            actual_hash = _sha256_bytes(data)
            if actual_hash != digest or len(data) != item["size_bytes"]:
                artifact_failures.append(f"artifact hash or byte count mismatch: {rel}")
                continue
            inventory[rel] = (actual_hash, len(data))
        if type(manifest.get("artifact_count")) is not int or manifest["artifact_count"] != len(artifacts):
            artifact_failures.append("artifact_count does not match artifacts list length")
        if artifact_failures:
            record("artifact_inventory", "FAIL", "; ".join(artifact_failures))
        else:
            record("artifact_inventory", "PASS", f"All {len(artifacts)} listed artifacts are contained, hash-valid, and size-valid.")

    def require_reference(obj: Any, path_key: str, hash_key: str, label: str) -> bool:
        try:
            if not isinstance(obj, Mapping):
                raise DeploymentPackageError(f"{label} must be an object")
            rel, digest = _get_path_hash_pair(obj, path_key, hash_key, label)
            if rel not in inventory:
                raise DeploymentPackageError(f"{label} path is absent from valid artifact inventory: {rel}")
            if inventory[rel][0] != digest:
                raise DeploymentPackageError(f"{label} digest does not match artifact inventory: {rel}")
            return True
        except DeploymentPackageError as exc:
            issues.append(str(exc))
            return False

    model = manifest.get("selected_model")
    target = manifest.get("target_contract")
    runtime = manifest.get("runtime")
    features = manifest.get("feature_contract")
    output = manifest.get("output_contract")
    training = manifest.get("training_provenance")
    if isinstance(model, Mapping) and all(str(model.get(key) or "").strip() for key in ("name", "class", "selection_decision")):
        record("model_selection", "PASS", "Selected model name, class, and explicit selection decision are present as metadata.")
    else:
        record("model_selection", "FAIL", "Selected model name, class, and selection_decision are required.")
    reference_specs = [
        (model, "artifact_path", "artifact_sha256", "selected_model.artifact"),
        (model, "metadata_path", "metadata_sha256", "selected_model.metadata"),
        (target, "artifact_path", "sha256", "target_contract"),
        (runtime, "lock_path", "lock_sha256", "runtime.lock"),
        (features, "schema_path", "schema_sha256", "feature_contract.schema"),
        (features, "preprocessing_path", "preprocessing_sha256", "feature_contract.preprocessing"),
        (output, "schema_path", "schema_sha256", "output_contract.schema"),
        (training, "training_input_path", "training_input_sha256", "training_provenance.input"),
        (training, "training_code_path", "training_code_sha256", "training_provenance.code"),
        (training, "training_environment_path", "training_environment_sha256", "training_provenance.environment"),
    ]
    ref_results = [require_reference(obj, path_key, hash_key, label) for obj, path_key, hash_key, label in reference_specs]
    if len(ref_results) == len(reference_specs) and all(ref_results):
        record("linked_artifacts", "PASS", "Model, target, runtime, feature, preprocessing, output, and training references match inventory hashes.")
    else:
        record("linked_artifacts", "FAIL", "One or more referenced package artifacts are missing or inconsistent.")

    if isinstance(features, Mapping) and isinstance(model, Mapping) and isinstance(training, Mapping):
        try:
            ordered_names = features.get("ordered_feature_names")
            feature_rows = features.get("features")
            engineered = features.get("engineered_feature_names")
            if not isinstance(ordered_names, list) or not ordered_names or len(set(ordered_names)) != len(ordered_names):
                raise DeploymentPackageError("ordered_feature_names must be a nonempty unique ordered list")
            if not isinstance(feature_rows, list) or [row.get("name") for row in feature_rows if isinstance(row, Mapping)] != ordered_names:
                raise DeploymentPackageError("feature definitions must exactly match ordered_feature_names")
            for row in feature_rows:
                if not isinstance(row, Mapping) or not all(str(row.get(key) or "").strip() for key in ("name", "type", "unit", "missing_policy")):
                    raise DeploymentPackageError("every feature requires name, type, unit, and missing_policy")
            if not isinstance(engineered, list) or len(set(engineered)) != len(engineered) or not set(engineered).issubset(set(ordered_names)):
                raise DeploymentPackageError("engineered_feature_names must be a unique subset of declared features")
            if training.get("feature_count") != len(ordered_names):
                raise DeploymentPackageError("training_provenance.feature_count disagrees with ordered feature list")
            metadata, _ = _read_json(root, model.get("metadata_path"))
            if metadata.get("feature_names") != ordered_names:
                raise DeploymentPackageError("serialized model metadata feature_names/order does not match feature contract")
            if metadata.get("model_class") != model.get("class"):
                raise DeploymentPackageError("model metadata class disagrees with selected_model.class")
            feature_schema, _ = _read_json(root, features.get("schema_path"))
            if feature_schema.get("feature_names") != ordered_names:
                raise DeploymentPackageError("feature schema feature_names/order does not match manifest")
            preprocessing, _ = _read_json(root, features.get("preprocessing_path"))
            if preprocessing.get("feature_order") != ordered_names:
                raise DeploymentPackageError("preprocessing feature_order does not match feature contract")
            if not isinstance(preprocessing.get("missing_value_policy"), Mapping):
                raise DeploymentPackageError("preprocessing contract must define a per-feature missing_value_policy")
            record("feature_contract", "PASS", "Manifest, model metadata, feature schema, preprocessing order, and count agree.")
        except (DeploymentPackageError, AttributeError, TypeError) as exc:
            record("feature_contract", "FAIL", str(exc))
    else:
        record("feature_contract", "FAIL", "Feature/model/training contract objects are missing or malformed.")

    if isinstance(target, Mapping):
        try:
            semantic = target.get("semantic_type")
            unit = str(target.get("output_unit") or "").strip().casefold()
            denominator = str(target.get("denominator") or "").strip()
            basis = target.get("measurement_basis")
            if semantic not in _SEMANTICS:
                raise DeploymentPackageError("target semantic_type is not supported")
            if not denominator:
                raise DeploymentPackageError("target denominator must be explicitly defined")
            if basis not in _MEASUREMENT_BASES:
                raise DeploymentPackageError("target measurement_basis is not recognized")
            if semantic in {"apparent_concentration_ratio", "concentration_retention", "total_mass_retention"} and unit not in _RATIO_UNITS:
                raise DeploymentPackageError("retention/ratio targets require an explicit ratio unit (percent or fraction), not a concentration unit")
            if semantic == "total_mass_retention" and basis != "total_mass":
                raise DeploymentPackageError("total_mass_retention requires measurement_basis=total_mass")
            target_doc, _ = _read_json(root, target.get("artifact_path"))
            if target.get("target_name") != "Retention_Final":
                raise DeploymentPackageError("target_name must identify Retention_Final")
            if not str(target.get("contract_id") or "").strip() or not str(target.get("numerator") or "").strip():
                raise DeploymentPackageError("target contract ID and numerator are required")
            for field in ("contract_id", "target_name", "semantic_type", "output_unit", "numerator", "denominator", "measurement_basis"):
                if target_doc.get(field) != target.get(field):
                    raise DeploymentPackageError(f"target artifact and manifest disagree on {field}")
            record("target_contract", "PASS", "Target semantics, output unit, numerator, denominator, basis, and artifact agree structurally.")
        except (DeploymentPackageError, AttributeError, TypeError) as exc:
            record("target_contract", "FAIL", str(exc))
    else:
        record("target_contract", "FAIL", "target_contract object is missing.")

    if isinstance(runtime, Mapping):
        try:
            pyver = str(runtime.get("python_version") or "")
            if not re.fullmatch(r"\d+\.\d+\.\d+", pyver):
                raise DeploymentPackageError("runtime.python_version must pin major.minor.patch")
            lib = str(runtime.get("serialization_library") or "").strip().casefold()
            version = str(runtime.get("serialization_library_version") or "").strip()
            lock_data = _safe_relative_path(root, runtime.get("lock_path")).read_text(encoding="utf-8").casefold()
            if not lib or not version or f"{lib}=={version.casefold()}" not in lock_data:
                raise DeploymentPackageError("runtime lock must pin the recorded serialization library and version")
            record("runtime", "PASS", "Python and serialization-library versions are pinned and consistent with lock file.")
        except (DeploymentPackageError, OSError, UnicodeDecodeError) as exc:
            record("runtime", "FAIL", str(exc))
    else:
        record("runtime", "FAIL", "runtime object is missing.")

    if isinstance(output, Mapping):
        try:
            if output.get("canonicalization") != "utf8_sorted_keys_compact_json_no_nan" or output.get("checksum_rule") != "sha256_payload_without_output_sha256":
                raise DeploymentPackageError("output canonicalization or checksum rule is unsupported")
            output_schema, _ = _read_json(root, output.get("schema_path"))
            if output_schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
                raise DeploymentPackageError("prediction output schema must declare Draft 2020-12")
            record("output_schema", "PASS", "Prediction output schema is present and declares Draft 2020-12.")
        except (DeploymentPackageError, AttributeError, TypeError) as exc:
            record("output_schema", "FAIL", str(exc))
    else:
        record("output_schema", "FAIL", "output_contract object is missing.")

    if not isinstance(manifest.get("review"), Mapping) or not isinstance(target, Mapping):
        record("human_review", "PENDING", "Human approval fields are missing; metadata validation cannot approve a model or target.")
    else:
        review = manifest["review"]
        target_review = target.get("scientific_approval")
        complete_manifest_review = all(str(review.get(key) or "").strip() for key in ("reviewer", "review_date", "review_reference")) and review.get("status") == "approved"
        complete_target_review = isinstance(target_review, Mapping) and target_review.get("status") == "approved" and all(
            str(target_review.get(key) or "").strip() for key in ("reviewer", "review_date", "review_reference")
        )
        if complete_manifest_review and complete_target_review:
            record("human_review", "PENDING", "Approval metadata is present but requires independent verification by the scientific owner.")
        else:
            record("human_review", "PENDING", "Scientific and independent reviewer approval remains pending.")

    return _result(checks, issues, package_id=str(manifest.get("package_id") or ""), package_version=str(manifest.get("package_version") or ""))


def _result(checks: list[dict[str, str]], issues: list[str], *, package_id: str = "", package_version: str = "") -> dict[str, Any]:
    failures = [row for row in checks if row["status"] == "FAIL"]
    return {
        "package_id": package_id,
        "package_version": package_version,
        "validation_status": "FAIL" if failures else "PASS",
        "deployment_readiness": "PENDING_REVIEW",
        "inference_authorized": False,
        "checks": checks,
        "issues": issues,
        "pending_prerequisites": [
            "independent verification of Stage A model selection and serialized artifact",
            "scientific owner adjudication of Retention_Final unit, numerator, denominator, and measurement basis",
            "verification of source lineage, scientific applicability, and independent approvals",
        ],
        "limitations": [
            "This validator checks supplied files and metadata only; it never imports, loads, or executes a model.",
            "A passing package integrity check is not Stage C compatibility or scientific approval.",
        ],
    }
