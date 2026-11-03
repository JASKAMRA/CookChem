"""Validate and reconcile Cycle 5 source observations with Phase1B raw records.

This script performs descriptive source-to-source arithmetic only. It does not
read model predictions, train or score a model, or claim external validation.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Dict, Iterable, List


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PHASE1B_ROOT = ROOT / "stageC" / "releases" / "Phase1B-v1.3.2"
PHASE1B_MANIFEST_SHA256 = "df3a95ae0957b68a89e38098c0824877196aa74ef7dd92573e6ab1f37e39b9b5"
PHASE1B_CSV = PHASE1B_ROOT / "stageC" / "data" / "food_composition" / "food_composition.csv"
OBSERVATIONS_CSV = HERE / "benchmark_observations.csv"
CANDIDATES_CSV = HERE / "candidate_matrix.csv"
COMPARISONS_CSV = HERE / "descriptive_comparison.csv"
MANIFEST_JSON = HERE / "manifest.json"
SCREEN_REPORT = ROOT / "stageC" / "reports" / "phase5" / "CYCLE5_BROAD_BENCHMARK_SCREEN.md"


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_phase1b_release() -> Dict[str, str]:
    manifest_path = PHASE1B_ROOT / "CHECKSUMS.json"
    digest_path = PHASE1B_ROOT / "CHECKSUMS.sha256"
    if not manifest_path.is_file() or not digest_path.is_file():
        raise ValueError("Pinned Phase1B-v1.3.2 checksum files are missing")
    actual_manifest_hash = sha256_file(manifest_path)
    expected_manifest_hash = digest_path.read_text(encoding="utf-8").split()[0].lower()
    if actual_manifest_hash != expected_manifest_hash or actual_manifest_hash != PHASE1B_MANIFEST_SHA256:
        raise ValueError("Pinned Phase1B-v1.3.2 release manifest hash does not match")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("release_id") != "Phase1B-v1.3.2":
        raise ValueError("Unexpected Phase1B package identity")
    relative_path = "stageC/data/food_composition/food_composition.csv"
    artifact = next((row for row in manifest.get("artifacts", []) if row.get("path") == relative_path), None)
    if artifact is None:
        raise ValueError("Pinned release manifest does not inventory the food-composition file")
    actual_file_hash = sha256_file(PHASE1B_CSV)
    if actual_file_hash != artifact.get("sha256") or PHASE1B_CSV.stat().st_size != artifact.get("bytes"):
        raise ValueError("Pinned Phase1B food-composition file failed checksum/size verification")
    return {
        "release_id": str(manifest["release_id"]),
        "manifest_sha256": actual_manifest_hash,
        "food_composition_sha256": actual_file_hash,
    }


def expected_mg_per_100g(value: float, unit: str) -> float:
    unit_key = unit.strip().lower().replace(" ", "")
    if unit_key.startswith("ug/") or unit_key.startswith("µg/") or unit_key.startswith("μg/"):
        return value / 1000.0
    if unit_key.startswith("mg/kg"):
        return value / 10.0
    if unit_key.startswith("mg/100g"):
        return value
    raise ValueError(f"Unsupported reported unit for explicit conversion: {unit!r}")


def validate_observations(rows: Iterable[Dict[str, str]]) -> None:
    seen = set()
    rows = list(rows)
    if not rows:
        raise ValueError("Benchmark observation file is empty")
    required = (
        "observation_id", "dataset_id", "food_name", "scientific_name", "analyte",
        "compound_record_id", "food_state", "concentration", "reported_unit",
        "normalized_mg_per_100g", "source_title", "source_url", "table_locator",
        "analytical_method", "replication",
    )
    for row in rows:
        missing = [field for field in required if not row.get(field, "").strip()]
        if missing:
            raise ValueError(f"{row.get('observation_id', '<unknown>')} missing {missing}")
        observation_id = row["observation_id"]
        if observation_id in seen:
            raise ValueError(f"Duplicate observation_id: {observation_id}")
        seen.add(observation_id)
        reported = float(row["concentration"])
        normalized = float(row["normalized_mg_per_100g"])
        expected = expected_mg_per_100g(reported, row["reported_unit"])
        if not math.isclose(normalized, expected, rel_tol=0, abs_tol=1e-9):
            raise ValueError(
                f"Unit conversion mismatch for {observation_id}: "
                f"stored {normalized}, expected {expected}"
            )
        if row["food_state"].lower() == "raw" and not row["phase1b_comparator_record_id"].strip():
            raise ValueError(f"Raw observation has no Phase1B comparator: {observation_id}")


def phase1b_mg_per_100g(row: Dict[str, str]) -> float:
    unit = row.get("reported_unit", "").strip().lower().replace(" ", "")
    value = float(row["reported_concentration"])
    if unit.startswith("mg/100g"):
        return value
    if unit.startswith("mg/kg"):
        return value / 10.0
    raise ValueError(f"Unsupported Phase1B comparator unit: {row.get('reported_unit')!r}")


def build_comparisons(
    observations: List[Dict[str, str]], phase1b_rows: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    validate_observations(observations)
    catalog_by_id = {row["food_record_id"]: row for row in phase1b_rows}
    raw_by_dataset: Dict[str, Dict[str, str]] = {}
    for row in observations:
        if row["food_state"].strip().lower() == "raw":
            dataset_id = row["dataset_id"]
            if dataset_id in raw_by_dataset:
                raise ValueError(f"Multiple raw observations for dataset {dataset_id}")
            raw_by_dataset[dataset_id] = row

    comparisons = []
    for dataset_id in sorted(raw_by_dataset):
        reference = raw_by_dataset[dataset_id]
        record_id = reference["phase1b_comparator_record_id"]
        if record_id not in catalog_by_id:
            raise ValueError(f"Comparator record does not exist: {record_id}")
        catalog = catalog_by_id[record_id]
        if catalog["compound_name"].strip().casefold() != reference["analyte"].strip().casefold():
            raise ValueError(f"Analyte mismatch between {record_id} and {reference['observation_id']}")
        catalog_compound_id = catalog.get("mapping_review_compound_id", "").strip()
        if catalog_compound_id and catalog_compound_id != reference["compound_record_id"]:
            raise ValueError(f"Mapped compound ID mismatch for {record_id}")

        catalog_value = phase1b_mg_per_100g(catalog)
        reference_value = float(reference["normalized_mg_per_100g"])
        if reference_value == 0:
            raise ValueError(f"Zero reference value cannot support a ratio: {reference['observation_id']}")
        delta = reference_value - catalog_value
        comparison = {
            "comparison_id": f"{dataset_id}-RAW-CATALOG-DESCRIPTIVE",
            "dataset_id": dataset_id,
            "food_name": reference["food_name"],
            "scientific_name": reference["scientific_name"],
            "analyte": reference["analyte"],
            "phase1b_record_id": record_id,
            "phase1b_reported_value": catalog["reported_concentration"],
            "phase1b_reported_unit": catalog["reported_unit"],
            "phase1b_mg_per_100g": f"{catalog_value:.9g}",
            "benchmark_observation_id": reference["observation_id"],
            "benchmark_reported_value": reference["concentration"],
            "benchmark_reported_unit": reference["reported_unit"],
            "benchmark_mg_per_100g": f"{reference_value:.9g}",
            "benchmark_minus_phase1b_mg_per_100g": f"{delta:.9g}",
            "phase1b_to_benchmark_ratio": f"{catalog_value / reference_value:.9g}",
            "benchmark_percent_difference_vs_phase1b": f"{(delta / catalog_value * 100.0):.6g}",
            "status": "CONTEXT_LIMITED_SOURCE_TO_SOURCE_ONLY",
            "scope": "Raw concentration arithmetic only; not a model prediction comparison or external validation.",
            "reason": reference["comparison_note"],
            "benchmark_source_url": reference["source_url"],
            "benchmark_locator": reference["table_locator"],
        }
        comparisons.append(comparison)
    return comparisons


def write_csv(path: Path, rows: List[Dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write an empty output: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    phase1b_integrity = verify_phase1b_release()
    observations = read_csv(OBSERVATIONS_CSV)
    phase1b_rows = read_csv(PHASE1B_CSV)
    comparisons = build_comparisons(observations, phase1b_rows)
    write_csv(COMPARISONS_CSV, comparisons)

    manifest = {
        "artifact": "Cycle 5 broad benchmark search: additive source dataset and descriptive raw-pair reconciliation",
        "manifest_version": 1,
        "comparison_scope": "Descriptive raw food-composition values only; no Stage C model estimates or external-validation metrics are read or emitted.",
        "normalization_rules": {
            "micrograms_per_100g_to_mg_per_100g": "divide by 1000",
            "mg_per_kg_to_mg_per_100g": "divide by 10",
            "mg_per_100g": "unchanged",
            "no moisture, cooking-yield, or tea-brew-ratio imputation": True,
        },
        "inputs": {
            "phase1b_food_composition_csv": {
                "path_from_repository_root": "stageC/releases/Phase1B-v1.3.2/stageC/data/food_composition/food_composition.csv",
                "sha256": phase1b_integrity["food_composition_sha256"],
                "release_id": phase1b_integrity["release_id"],
            },
            "phase1b_release_manifest": {
                "path_from_repository_root": "stageC/releases/Phase1B-v1.3.2/CHECKSUMS.json",
                "sha256": phase1b_integrity["manifest_sha256"],
            },
            "benchmark_observations_csv": {
                "path": OBSERVATIONS_CSV.name,
                "sha256": sha256_file(OBSERVATIONS_CSV),
                "rows": len(observations),
            },
            "candidate_matrix_csv": {
                "path": CANDIDATES_CSV.name,
                "sha256": sha256_file(CANDIDATES_CSV),
                "rows": len(read_csv(CANDIDATES_CSV)),
            },
            "comparison_script": {
                "path": Path(__file__).name,
                "sha256": sha256_file(Path(__file__).resolve()),
            },
            "screen_report": {
                "path_from_repository_root": "stageC/reports/phase5/CYCLE5_BROAD_BENCHMARK_SCREEN.md",
                "sha256": sha256_file(SCREEN_REPORT),
            },
        },
        "outputs": {
            "descriptive_comparison_csv": {
                "path": COMPARISONS_CSV.name,
                "sha256": sha256_file(COMPARISONS_CSV),
                "rows": len(comparisons),
            }
        },
        "checks": [
            "observation identifiers unique",
            "citation, table locator, source URL and analytical method present",
            "stored unit conversions recomputed and checked",
            "comparator IDs and mapped compound IDs checked against current Phase1B file",
            "only raw-to-raw descriptive comparisons emitted",
            "cooked observations retained without synthetic or model comparison",
        ],
    }
    MANIFEST_JSON.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Validated {len(observations)} source observations; emitted {len(comparisons)} context-limited raw comparisons.")
    print(f"No model estimates or external-validation metrics were evaluated.")


if __name__ == "__main__":
    main()
