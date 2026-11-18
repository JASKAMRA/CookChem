"""Read-only access to documented CookRisk research evidence.

No training, inference, scientific metric recomputation, normalization, or imputation
is performed here. The one interactive ACR dataset is byte-pinned and loaded only
when an evidence/ACR page needs it.
"""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
PROTOTYPE = REPO_ROOT / "research" / "CookRisk_Computational_Research_Prototype"

RECONSTRUCTION_REL = Path(
    "stageA/verified_concentration_ratio_reconstruction/final_verified_master_dataset.csv"
)
RECONSTRUCTION_SHA256 = "16dbbd9c38a21675a2644b415289004e5a8eb7091e97a96dae645ed2bf52be99"
RECONSTRUCTION_ROWS = 1016

BATCH021_HISTORICAL_AUDIT_SHA256 = (
    "111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8"
)
BATCH021_CURRENT_SHA256 = (
    "d866d0ffab8c335e0469f2815c3cdf518b3d019be1bdf2e37ba2ced2e7d5d3c1"
)

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
        "status": "REPORTED; current data/manifest parent linkage BLOCKED/UNVERIFIED",
        "hash": "Manifest parent SHA-256 d3960dc6ec808ca1783cbb2c57d35fb4676da04feeff675280c1f07eb072005a; current linkage unresolved",
        "source": "stageA/final_prototype_2026_11_10/manifest.json; model_comparison.csv",
        "interactive": "Metrics only; no record-level comparison is made against another family.",
    },
    {
        "family": "Batch021 ACR master",
        "snapshot": "1,016 rows; 48 canonical IDs; 32 DOI families reported",
        "target": "ACR",
        "status": "REPORTED; file hash documented; do not conflate with reconstruction",
        "hash": BATCH021_CURRENT_SHA256,
        "source": "stageA/dataset_expansion_1000/batch_021/updated_master_dataset.csv",
        "interactive": "Metadata and result status only; its records are not loaded by this demonstrator.",
    },
    {
        "family": "Verified concentration-ratio reconstruction",
        "snapshot": "1,016 rows; 48 identities; 32 DOI families; 66 matrices; 41 methods reported",
        "target": "verified_concentration_ratio_percent = 100 × cooked/raw",
        "status": "REPORTED; demonstrator pins the current file bytes; not owner-designated canonical; not freshly scientifically validated here",
        "hash": RECONSTRUCTION_SHA256,
        "source": str(RECONSTRUCTION_REL),
        "interactive": "Selected for record-level exploration because its source locators, identity, target fields and reconstruction report are present. Distinct from Batch021.",
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


def load_acr_dataset() -> tuple[list[dict[str, str]], str]:
    """Load the pinned reconstruction without transforming its source rows."""
    path = REPO_ROOT / RECONSTRUCTION_REL
    if not path.is_file():
        raise FileNotFoundError(
            f"Selected evidence file is missing: {RECONSTRUCTION_REL.as_posix()}"
        )
    actual_hash = sha256_file(path)
    if actual_hash != RECONSTRUCTION_SHA256:
        raise ValueError(
            "The selected ACR file does not match this demonstrator's recorded "
            f"byte snapshot. Expected {RECONSTRUCTION_SHA256}; found {actual_hash}. "
            "Record-level exploration is disabled until the snapshot is reviewed."
        )
    rows = read_csv_rows(path)
    if len(rows) != RECONSTRUCTION_ROWS:
        raise ValueError(
            f"Pinned ACR file row count changed: expected {RECONSTRUCTION_ROWS}, "
            f"found {len(rows)}. Record-level exploration is disabled."
        )
    required = {
        "observation_id", "doi", "compound", "food_matrix", "cooking_method",
        "raw_concentration", "cooked_concentration", "target_value_percent",
        "measurement_basis", "concentration_unit", "source_locator",
    }
    if not rows or not required.issubset(rows[0]):
        missing = sorted(required - set(rows[0] if rows else {}))
        raise ValueError(f"Selected ACR file is missing required columns: {missing}")
    return rows, actual_hash


def load_selected_metrics() -> list[dict[str, str]]:
    return read_csv_rows(PROTOTYPE / "tables" / "EXISTING_METRICS_SELECTED.csv")


def load_dataset_catalog() -> list[dict[str, str]]:
    return read_csv_rows(PROTOTYPE / "tables" / "DATASET_SNAPSHOT_CATALOG.csv")


def load_validation_folds() -> list[dict[str, str]]:
    path = REPO_ROOT / "stageA" / "molecular_vs_source_validation_audit" / "fold_metrics.csv"
    rows = read_csv_rows(path)
    return rows


def numeric(row: dict[str, Any], key: str) -> float | None:
    value = row.get(key)
    if value is None or str(value).strip() == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
