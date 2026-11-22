"""Read-only access to documented CookRisk research evidence.

No training, inference, scientific metric recomputation, normalization, or imputation
is performed here. The one interactive ACR dataset is byte-pinned and loaded only
when an evidence/ACR page needs it.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
PROTOTYPE = REPO_ROOT / "research" / "CookRisk_Computational_Research_Prototype"
REPORTS = Path(__file__).resolve().parent / "reports"
FINAL_CONSOLIDATION = REPORTS / "final_model_r2_consolidation_2026-11-20"
REGISTRY_PATH = Path(__file__).resolve().parent / "dataset_registry" / "datasets.json"
LIVE_EXPLORATION_DATASET_ID = "stagea-acr-reconstruction-1016-f939"
BATCH021_DATASET_ID = "stagea-batch021-historical-1016-111064"

with REGISTRY_PATH.open("r", encoding="utf-8-sig") as _registry_stream:
    _registry_seed = json.load(_registry_stream)
_reconstruction_seed = _registry_seed["datasets"][LIVE_EXPLORATION_DATASET_ID]
_batch021_seed = _registry_seed["datasets"][BATCH021_DATASET_ID]
RECONSTRUCTION_REL = Path(_reconstruction_seed["repository_relative_path"])
RECONSTRUCTION_SHA256 = _reconstruction_seed["expected_sha256"]
RECONSTRUCTION_ROWS = _reconstruction_seed["row_count"]
BATCH021_HISTORICAL_AUDIT_SHA256 = _batch021_seed["saved_evaluation_provenance"]["summary_input_sha256"]
BATCH021_CURRENT_SHA256 = _batch021_seed["expected_sha256"]
del _registry_stream, _registry_seed, _reconstruction_seed, _batch021_seed

DATASET_FAMILIES: list[dict[str, str]] = [
    {
        "family": "Historical Stage A benchmark",
        "snapshot": "1,124 rows; 197 molecular groups; 183 DOIs reported",
        "target": "Retention_Final (not established as ACR)",
        "status": "REPORTED; prior repeatability applies only to the documented benchmark pipeline; historical equivalence unresolved",
        "hash": "750124efc8b89dff1f67764064b1049b5db51fb1b2f222d4f91cd94c56945f89 (documented input)",
        "source": "stageA/input/cookchem_molecular_retention_preprocessed.csv; stageA/stageA_reproducibility.md",
        "interactive": "Metrics only; not loaded as the ACR evidence table.",
    },
    {
        "family": "439-row final-prototype family",
        "snapshot": "439 eligible rows; 46 identities; 10 DOI families reported",
        "target": "ACR",
        "status": "REPORTED; saved parent/output data linkage verified; current prototype scripts have checksum drift",
        "hash": "Parent SHA-256 d3960dc6ec808ca1783cbb2c57d35fb4676da04feeff675280c1f07eb072005a; output SHA-256 1fea513ac44777411357df6ac7d084eecd97cd08f956d3ac23e38695552554d1",
        "source": "stageA/final_prototype_2026_11_10/manifest.json; model_comparison.csv",
        "interactive": "Saved historical metrics only; 439-row subset and not loaded into live record-level exploration.",
    },
    {
        "family": "Batch021 ACR master",
        "snapshot": "1,016 rows; 48 canonical IDs; 32 DOI families reported",
        "target": "ACR",
        "status": "OWNER-APPROVED SEPARATE HISTORICAL REFERENCE; saved results are not recalculated",
        "hash": BATCH021_CURRENT_SHA256,
        "source": "stageA/dataset_expansion_1000/batch_021/updated_master_dataset.csv",
        "interactive": "Historical dataset metadata and saved Batch021 evaluations only; never a fallback for live exploration.",
    },
    {
        "family": "Verified concentration-ratio reconstruction",
        "snapshot": "1,016 rows; 48 identities; 32 DOI families; 66 matrices; 50 recorded method labels (41 normalized)",
        "target": "target_value_percent — apparent concentration ratio; 100 × C_cooked / C_raw",
        "status": "OWNER-APPROVED FOR DEMONSTRATOR LIVE EXPLORATION ONLY; not canonical; not independently validated",
        "hash": RECONSTRUCTION_SHA256,
        "source": str(RECONSTRUCTION_REL),
        "interactive": "Live Evidence Explorer, ACR distributions, and Cooking & Compound Patterns; saved OOF record inspection in ML Error Analysis. Separate from Batch021 historical metrics.",
    },
    {
        "family": "Strict source-verified subset",
        "snapshot": "338 rows; 45 identities; 6 DOI families reported",
        "target": "ACR",
        "status": "REPORTED; strict subset, not interchangeable with broader datasets",
        "hash": "No standalone dataset hash recorded in the selected catalog",
        "source": "stageA/989_observation_recovery_audit/989_recovery_audit_report.md",
        "interactive": "Metrics and documented summary only; not loaded as the record-level ACR table.",
    },
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def load_dataset_registry(registry_path: Path = REGISTRY_PATH) -> dict[str, Any]:
    """Read and structurally validate the local dataset registry."""
    try:
        with registry_path.open("r", encoding="utf-8-sig") as stream:
            registry = json.load(stream)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Dataset registry is missing: {registry_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Dataset registry is malformed: {exc}") from exc

    if not isinstance(registry, dict) or registry.get("schema_version") != 1:
        raise ValueError("Dataset registry has a missing or unsupported schema_version.")
    datasets = registry.get("datasets")
    if not isinstance(datasets, dict) or not datasets:
        raise ValueError("Dataset registry has no dataset entries.")
    for dataset_id, entry in datasets.items():
        if not isinstance(entry, dict) or entry.get("dataset_id") != dataset_id:
            raise ValueError(f"Dataset registry entry identity is invalid: {dataset_id!r}.")
    return registry


def get_dataset_entry(
    dataset_id: str, registry_path: Path = REGISTRY_PATH
) -> dict[str, Any]:
    registry = load_dataset_registry(registry_path)
    entry = registry["datasets"].get(dataset_id)
    if entry is None:
        raise KeyError(f"Unknown dataset ID: {dataset_id}")
    return entry


def load_registered_dataset(
    dataset_id: str,
    repo_root: Path = REPO_ROOT,
    registry_path: Path = REGISTRY_PATH,
) -> tuple[list[dict[str, str]], str, dict[str, Any]]:
    """Load only a registry-approved live dataset, with no path or data fallback."""
    entry = get_dataset_entry(dataset_id, registry_path)
    if entry.get("designation_status") != "OWNER_APPROVED_DEMONSTRATOR_EXPLORATION_ONLY":
        raise ValueError(f"Dataset ID is not approved for live exploration: {dataset_id}")
    if "live_record_level_exploration" not in entry.get("allowed_application_uses", []):
        raise ValueError(f"Dataset ID is not permitted for live exploration: {dataset_id}")

    relative = entry.get("repository_relative_path")
    if not isinstance(relative, str) or not relative.strip():
        raise ValueError(f"Dataset registry path is missing for {dataset_id}.")
    candidate = Path(relative)
    if candidate.is_absolute():
        raise ValueError(f"Dataset registry path must be repository-relative: {relative}")
    root = repo_root.resolve()
    path = (root / candidate).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Dataset registry path escapes the repository: {relative}") from exc
    if not path.is_file():
        raise FileNotFoundError(f"Selected dataset file is missing: {relative}")

    expected_hash = entry.get("expected_sha256")
    if (
        not isinstance(expected_hash, str)
        or len(expected_hash) != 64
        or any(ch not in "0123456789abcdef" for ch in expected_hash.lower())
    ):
        raise ValueError(f"Dataset registry has an invalid SHA-256 for {dataset_id}.")
    actual_hash = sha256_file(path)
    if actual_hash.lower() != expected_hash.lower():
        raise ValueError(
            f"Dataset hash mismatch for {dataset_id}: expected {expected_hash}; "
            f"found {actual_hash}. Live exploration is disabled; no fallback is permitted."
        )

    columns = entry.get("schema_columns")
    expected_column_count = entry.get("column_count")
    if (
        not isinstance(columns, list)
        or not columns
        or not all(isinstance(column, str) for column in columns)
        or expected_column_count != len(columns)
    ):
        raise ValueError(f"Dataset registry schema is missing or inconsistent for {dataset_id}.")
    rows = read_csv_rows(path)
    actual_columns = list(rows[0].keys()) if rows else []
    if actual_columns != columns:
        raise ValueError(
            f"Dataset schema mismatch for {dataset_id}: expected {len(columns)} recorded "
            f"columns in registry order, found {len(actual_columns)}. Live exploration is disabled."
        )
    if len(rows) != entry.get("row_count"):
        raise ValueError(
            f"Dataset row-count mismatch for {dataset_id}: expected {entry.get('row_count')}, "
            f"found {len(rows)}. Live exploration is disabled."
        )

    id_field = entry.get("id_field")
    if not isinstance(id_field, str) or id_field not in columns:
        raise ValueError(f"Dataset registry ID field is missing or invalid for {dataset_id}.")
    ids = [row.get(id_field, "").strip() for row in rows]
    if (
        any(not value for value in ids)
        or len(set(ids)) != entry.get("unique_id_count")
        or len(ids) != entry.get("unique_id_count")
    ):
        raise ValueError(f"Dataset ID integrity check failed for {dataset_id}.")

    target = entry.get("target_definition")
    required_target_keys = {
        "field", "name_field", "name", "equation_field", "equation",
        "semantics_field", "semantics", "unit", "scientific_meaning",
    }
    if not isinstance(target, dict) or not required_target_keys.issubset(target):
        raise ValueError(f"Dataset target definition is missing for {dataset_id}.")
    for key in ("field", "name_field", "equation_field", "semantics_field"):
        if not isinstance(target.get(key), str) or target[key] not in columns:
            raise ValueError(f"Dataset target definition field {key!r} is invalid for {dataset_id}.")
    for field in ("name", "equation", "semantics", "scientific_meaning"):
        if not isinstance(target.get(field), str) or not target[field].strip():
            raise ValueError(f"Dataset target definition {field!r} is missing for {dataset_id}.")
    for row in rows:
        if (
            row.get(target["name_field"], "").strip() != target["name"]
            or row.get(target["equation_field"], "").strip() != target["equation"]
            or row.get(target["semantics_field"], "").strip() != target["semantics"]
        ):
            raise ValueError(
                f"Dataset row target definition is missing or inconsistent for {dataset_id}."
            )
    return rows, actual_hash, entry


def load_acr_dataset(
    dataset_id: str = LIVE_EXPLORATION_DATASET_ID,
) -> tuple[list[dict[str, str]], str, dict[str, Any]]:
    """Load the explicitly approved Reconstruction for live record exploration."""
    return load_registered_dataset(dataset_id)


def load_batch021_evaluation_provenance() -> dict[str, Any]:
    """Compare the saved Batch021 audit input digest with the preserved current file."""
    entry = get_dataset_entry(BATCH021_DATASET_ID)
    path = REPO_ROOT / entry["repository_relative_path"]
    actual_hash = sha256_file(path) if path.is_file() else None
    summary_path = REPO_ROOT / entry["saved_evaluation_provenance"]["summary_path"]
    summary = None
    if summary_path.is_file():
        with summary_path.open("r", encoding="utf-8-sig") as stream:
            summary = json.load(stream)
    input_hash = summary.get("input_sha256") if isinstance(summary, dict) else None
    expected_hash = entry["expected_sha256"]
    return {
        "entry": entry,
        "actual_sha256": actual_hash,
        "saved_input_sha256": input_hash,
        "identity_matches": bool(
            actual_hash == expected_hash and input_hash == expected_hash
        ),
        "summary": summary,
    }


def annotate_saved_metric_provenance(
    metrics: list[dict[str, str]], provenance: dict[str, Any]
) -> list[dict[str, str]]:
    """Correct stale Batch021 display metadata without changing any saved metric."""
    display_rows = []
    entry = provenance["entry"]
    saved_input = provenance.get("saved_input_sha256") or "unavailable"
    current_hash = provenance.get("actual_sha256") or "unavailable"
    for row in metrics:
        display_row = dict(row)
        if row.get("result_family") == "Batch021 fixed audit":
            if provenance.get("identity_matches"):
                display_row["status"] = (
                    "REPORTED; saved audit input hash matches current Batch021 bytes; "
                    "metrics not freshly reproduced"
                )
                display_row["limitation"] = (
                    f"Saved validation summary input SHA-256 {saved_input} matches the "
                    f"current Batch021 CSV SHA-256 {current_hash}. Saved metrics and "
                    "predictions were not recalculated or independently reproduced here. "
                    "DOI remains a source-family proxy."
                )
            else:
                display_row["status"] = "REPORTED; current-snapshot attribution BLOCKED/UNVERIFIED"
                display_row["limitation"] = (
                    f"Saved validation input SHA-256: {saved_input}; current Batch021 CSV "
                    f"SHA-256: {current_hash}; registry expected SHA-256: "
                    f"{entry['expected_sha256']}. Hash identity is not established. "
                    "Saved metrics remain historical and were not recalculated."
                )
        display_rows.append(display_row)
    return display_rows


def load_selected_metrics() -> list[dict[str, str]]:
    return read_csv_rows(PROTOTYPE / "tables" / "EXISTING_METRICS_SELECTED.csv")


def load_dataset_catalog() -> list[dict[str, str]]:
    return read_csv_rows(PROTOTYPE / "tables" / "DATASET_SNAPSHOT_CATALOG.csv")


def _load_consolidation_register(name: str, required_columns: set[str]) -> list[dict[str, str]]:
    """Read a named, approved Phase 4 evidence register without modifying it."""
    path = FINAL_CONSOLIDATION / name
    try:
        rows = read_csv_rows(path)
    except OSError as exc:
        raise OSError(f"Saved evidence register is unavailable: {name}") from exc
    if not rows:
        raise ValueError(f"Saved evidence register is empty: {name}")
    missing = required_columns.difference(rows[0])
    if missing:
        raise ValueError(
            f"Saved evidence register has an unsupported schema: {name}; "
            f"missing columns: {', '.join(sorted(missing))}"
        )
    return rows


def load_consolidated_model_evidence() -> list[dict[str, str]]:
    """Return saved model metrics and evidence labels from the final consolidation."""
    return _load_consolidation_register(
        "CONSOLIDATED_MODEL_R2_REGISTER.csv",
        {
            "result_id", "dataset_family", "dataset_identity", "row_count", "target",
            "model", "configuration", "configuration_status", "evaluation_protocol",
            "grouping_unit", "fold_count", "pooled_oof_r2", "pooled_metric_status",
            "mean_fold_r2", "mean_fold_metric_status", "supporting_evidence",
            "checksum_status", "input_provenance_status", "interpretation",
        },
    )


def load_consolidated_fold_evidence() -> list[dict[str, str]]:
    """Return saved fold-level records; no fold statistics are recomputed."""
    return _load_consolidation_register(
        "FOLD_RECORD_EVIDENCE_REGISTER.csv",
        {
            "dataset_family", "dataset_identity", "target", "model", "configuration",
            "evaluation_protocol", "grouping_unit", "fold", "fold_r2", "fold_mae",
            "fold_rmse", "n_test", "supporting_file", "checksum_status", "notes",
        },
    )


def load_historical_metric_conflicts() -> list[dict[str, str]]:
    """Return unresolved conflict records from the final consolidation."""
    return _load_consolidation_register(
        "HISTORICAL_METRIC_CONFLICT_REGISTER.csv",
        {
            "conflict_id", "scope", "dataset_family", "model", "evaluation_protocol",
            "metric_or_artifact", "value_a", "value_b", "artifact_integrity", "status",
            "verified_facts", "unresolved_cause_or_interpretation", "evidence_reference",
        },
    )


def load_provenance_gap_register() -> list[dict[str, str]]:
    """Return documented unverified and provenance-gap records."""
    return _load_consolidation_register(
        "UNVERIFIED_AND_PROVENANCE_GAP_REGISTER.csv",
        {
            "gap_id", "status", "area", "finding", "evidence_available",
            "not_established", "safe_handling", "evidence_reference",
        },
    )


SCIENTIFIC_LIMITATIONS: list[dict[str, str]] = [
    {
        "issue": "Historical Retention_Final semantics and units",
        "evidence": "Final Phase 4 consolidation; Phase 2 provenance report.",
        "effect_on_interpretation": "Equation, scale, units, and measurement basis are unresolved; this is not established as ACR.",
        "status": "OPEN SCIENTIFIC LIMITATION",
        "handling": "Keep the 1,124-row historical benchmark separate and label its target as Retention_Final.",
    },
    {
        "issue": "Historical input-byte provenance",
        "evidence": "Final Phase 4 provenance-gap register; original source CSV intentionally not accessed.",
        "effect_on_interpretation": "Historical and currently documented input digests differ; the exact historical input bytes are not independently verified.",
        "status": "PROVENANCE INCOMPLETE",
        "handling": "Display saved pooled results as reported with incomplete provenance; do not recalculate or infer overwrite.",
    },
    {
        "issue": "Tuned XGBoost saved-result conflict",
        "evidence": "Initial benchmark and separately checksummed replay records in the final consolidation.",
        "effect_on_interpretation": "Two pooled/mean-fold pairs exist; the replay input digest is absent and no winning version is established.",
        "status": "CONFLICTING SAVED EVIDENCE",
        "handling": "Show both versions and their evidence provenance; do not merge or select a winner.",
    },
    {
        "issue": "ACR is not total-mass retention",
        "evidence": "Dataset registry; Phase 3 ACR validation report.",
        "effect_on_interpretation": "100 × C_cooked / C_raw is an apparent concentration ratio and cannot establish change in total analyte mass by itself.",
        "status": "SCIENTIFIC BOUNDARY",
        "handling": "Label the target as ACR; require compatible paired food masses or validated yield for total-mass retention.",
    },
    {
        "issue": "Raw/cooked measurement compatibility",
        "evidence": "Phase 3 ACR validation report.",
        "effect_on_interpretation": "Source-level confirmation that paired values share analyte, units, basis, extraction, and assay is not established for every source.",
        "status": "OPEN SCIENTIFIC LIMITATION",
        "handling": "Preserve source fields as recorded and avoid broad cross-source or causal interpretation.",
    },
    {
        "issue": "Heterogeneous units and measurement bases",
        "evidence": "Phase 3 ACR validation report documents 20 unit labels, 15 basis labels, including unspecified bases.",
        "effect_on_interpretation": "Values have not been harmonized; pooled comparisons may reflect incompatible measurement bases.",
        "status": "OPEN SCIENTIFIC LIMITATION",
        "handling": "Display stored values and labels without unit conversion or normalization.",
    },
    {
        "issue": "Missing assay and replicate metadata",
        "evidence": "Phase 3 ACR validation report documents missing analytical definitions and replicate-design fields.",
        "effect_on_interpretation": "Precision, assay compatibility, and experimental independence are not fully characterized.",
        "status": "OPEN SCIENTIFIC LIMITATION",
        "handling": "Expose the recorded source context; do not treat repeated rows as independent replicates.",
    },
    {
        "issue": "Stored versus strict target precision",
        "evidence": "Phase 3 ACR validation report: 118 strict numeric differences match at displayed precision; source precision was not verified.",
        "effect_on_interpretation": "Exact stored target strings and a strict recalculation can differ below displayed precision.",
        "status": "DOCUMENTED PRECISION LIMITATION",
        "handling": "Preserve stored targets; make no source correction without primary-source precision evidence.",
    },
    {
        "issue": "Cooked-concentration zeros",
        "evidence": "Phase 3 ACR validation report records two zero cooked-concentration values.",
        "effect_on_interpretation": "True zero versus detection-limit or reporting convention is unknown.",
        "status": "UNRESOLVED SOURCE INTERPRETATION",
        "handling": "Keep values as stored; do not infer absence or replace values.",
    },
    {
        "issue": "Outlier review",
        "evidence": "Phase 3/4 reports identify high Tukey review flags; no observation was removed.",
        "effect_on_interpretation": "Extreme values can affect descriptive summaries and saved model metrics; a flag is not proof of error.",
        "status": "REVIEW INDICATOR",
        "handling": "Retain all observations and do not apply automatic deletion.",
    },
    {
        "issue": "Sparse groups and repeated source families",
        "evidence": "Phase 3/4 reports document 32 DOI families, repeated rows, and sparse descriptive groups.",
        "effect_on_interpretation": "Rows are not necessarily independent observations; group summaries do not establish statistical sufficiency.",
        "status": "OPEN SCIENTIFIC LIMITATION",
        "handling": "Show support counts and minimum-group rules; label group summaries descriptive and noncausal.",
    },
    {
        "issue": "Batch021 molecular/source-held-out interpretation",
        "evidence": "Final Phase 4 consolidation and saved Batch021 evaluation provenance.",
        "effect_on_interpretation": "DOI/source-held-out is a source-family proxy, not independent-laboratory or external validation.",
        "status": "HISTORICAL EVIDENCE ONLY",
        "handling": "Keep the split label exact and describe its limits; do not imply external generalization.",
    },
    {
        "issue": "Reconstruction model-output provenance",
        "evidence": "Final Phase 4 consolidation reports no output sidecar/build-time digest.",
        "effect_on_interpretation": "Saved pooled values are reported with incomplete provenance; mean-fold values are supported by saved folds.",
        "status": "PROVENANCE INCOMPLETE",
        "handling": "Show separate pooled and mean-fold status labels; do not claim independent validation or a fresh replay.",
    },
    {
        "issue": "Post1000 aggregate checksum and metric conflicts",
        "evidence": "Final Phase 4 conflict register: three aggregate checksum mismatches and 12 of 21 comparison rows differ; nine agree numerically.",
        "effect_on_interpretation": "The aggregate view is checksum-invalid, component/aggregate values conflict, and the alternate-writer cause is unproven.",
        "status": "CONFLICTING SAVED EVIDENCE",
        "handling": "Preserve both versions in the conflict register; do not rank models or repair historical artifacts.",
    },
    {
        "issue": "Strict verified subset pooled R²",
        "evidence": "Final Phase 4 consolidation; five saved fold records exist but pooled OOF evidence was not located.",
        "effect_on_interpretation": "Pooled R² is not assessable from available saved evidence.",
        "status": "NOT ASSESSABLE",
        "handling": "Show only the saved mean-fold result and label pooled R² NOT ASSESSABLE.",
    },
    {
        "issue": "Friend-reported R² claims",
        "evidence": "Final Phase 4 consolidation found no supporting records for pooled 0.3301 / mean-fold 0.2990.",
        "effect_on_interpretation": "Dataset, target, model, and split are not established.",
        "status": "UNVERIFIED",
        "handling": "Keep out of model results and any achievement claim; show only as an unresolved claim if needed.",
    },
    {
        "issue": "No external/prospective validation or deployment evidence",
        "evidence": "Phase 4 statistical review; no external laboratory, temporal, prospective, or deployed-model evaluation is documented.",
        "effect_on_interpretation": "Saved historical splits do not establish performance on future or independent laboratories.",
        "status": "NOT ESTABLISHED",
        "handling": "Describe this as a research prototype only; make no clinical, patient-specific, causal, or consumer-ready claims.",
    },
]


def load_validation_folds() -> list[dict[str, str]]:
    path = REPO_ROOT / "stageA" / "molecular_vs_source_validation_audit" / "fold_metrics.csv"
    rows = read_csv_rows(path)
    return rows


def numeric(row: dict[str, Any], key: str) -> float | None:
    value = row.get(key)
    if value is None or str(value).strip() == "":
        return None
    try:
        parsed = float(value)
        return parsed if math.isfinite(parsed) else None
    except (TypeError, ValueError):
        return None
