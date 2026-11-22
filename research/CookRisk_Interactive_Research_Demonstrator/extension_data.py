"""Read-only, release-pinned inputs for the two additional research pages."""
from __future__ import annotations

import hashlib
import json
import math
import statistics
from pathlib import Path

from research_data import REPO_ROOT, LIVE_EXPLORATION_DATASET_ID, load_acr_dataset, read_csv_rows

RECON_DIR = REPO_ROOT / "stageA" / "verified_concentration_ratio_reconstruction"
OOF_SHA256 = "d0416a08713f0b071794541c5260b921c05287298786c41dc40c6574ea8d05ce"
FOLD_SHA256 = {
    "molecular_grouped": "1703d9fec57394554888e5fb7a0033ea4ae2d2a3f86e4a4fa5917868ee558135",
    "source_held_out": "bd8668d7d77d4a1f9e7226a69f137f2995ed76d9f6c82df90fbc46f526e3a74b",
}
DESIGNS = ("molecular_grouped", "source_held_out")
STAGEB_DIR = REPO_ROOT / "stageB" / "release" / "StageB_FINALIZED"
STAGEB_MANIFEST_SHA256 = "b85f8293297cb5e447d2293e31cfcdafbef50497260d870d54f14da441c7359e"
STAGEB_TABLES = {
    "compounds": ("compound_registry.csv", 143),
    "evidence": ("interaction_evidence.csv", 317),
    "drugs": ("drug_probe_registry.csv", 133),
    "bibliography": ("publication_bibliography.csv", 163),
    "studies": ("study_registry.csv", 161),
    "warnings": ("warning_ledger.csv", 88),
}


def _verified_bytes(path: Path, expected: str, *, allow_crlf_checkout: bool = False) -> bytes:
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        # Git stores LF release bytes; some Windows checkouts translate them to CRLF.
        # Accept only that exact, reversible difference, never changed content.
        if not allow_crlf_checkout or b"\r\n" not in raw or raw.count(b"\n") != raw.count(b"\r\n") or hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest() != expected:
            raise ValueError(f"Saved file integrity check failed: {path}")
    return raw


def _verified_csv(path: Path, expected: str, *, allow_crlf_checkout: bool = False) -> list[dict[str, str]]:
    _verified_bytes(path, expected, allow_crlf_checkout=allow_crlf_checkout)
    return read_csv_rows(path)


def _quantile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    low = math.floor(position)
    high = math.ceil(position)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def error_metrics(rows: list[dict]) -> dict[str, float | int]:
    if not rows:
        raise ValueError("No OOF observations are available")
    actual = [float(row["actual"]) for row in rows]
    predicted = [float(row["predicted"]) for row in rows]
    if not all(math.isfinite(value) for value in actual + predicted):
        raise ValueError("Nonfinite OOF target or prediction")
    residuals = [a - p for a, p in zip(actual, predicted)]
    absolute = [abs(value) for value in residuals]
    center = statistics.mean(actual)
    total = sum((value - center) ** 2 for value in actual)
    if total == 0:
        raise ValueError("OOF R² is undefined for a constant target")
    return {
        "n": len(rows),
        "r2": 1 - sum(value * value for value in residuals) / total,
        "mae": statistics.mean(absolute),
        "rmse": math.sqrt(statistics.mean(value * value for value in residuals)),
        "median_absolute_error": statistics.median(absolute),
        "p90_absolute_error": _quantile(absolute, 0.9),
    }


def load_reconstruction_errors() -> tuple[dict[str, list[dict]], dict[str, dict], str]:
    """Join exact OOF IDs to the approved Reconstruction; reject changed inputs."""
    observations, dataset_hash, entry = load_acr_dataset(LIVE_EXPLORATION_DATASET_ID)
    by_id = {row["observation_id"]: row for row in observations}
    if len(by_id) != 1016:
        raise ValueError("Reconstruction observation IDs are not unique")
    raw = _verified_csv(RECON_DIR / "oof_predictions.csv", OOF_SHA256)
    if set(raw[0]) != {"evaluation", "row_index", "fold", "observation_id", "doi", "canonical_molecular_id", "actual", "predicted"}:
        raise ValueError("Unexpected Reconstruction OOF schema")
    if len(raw) != 2032:
        raise ValueError("Reconstruction OOF row count is not 2 × 1,016")
    grouped: dict[str, list[dict]] = {key: [] for key in DESIGNS}
    for row in raw:
        design = row["evaluation"]
        if design not in grouped:
            raise ValueError(f"Unsupported OOF validation design: {design}")
        source = by_id.get(row["observation_id"])
        if source is None or row["doi"] != source["doi"] or row["canonical_molecular_id"] != source["canonical_molecular_id"]:
            raise ValueError(f"OOF source identity mismatch: {row['observation_id']}")
        actual, predicted = float(row["actual"]), float(row["predicted"])
        if not math.isfinite(actual) or not math.isfinite(predicted) or not math.isclose(actual, float(source["target_value_percent"]), abs_tol=1e-7):
            raise ValueError(f"OOF target mismatch: {row['observation_id']}")
        fold = int(row["fold"])
        if fold not in range(1, 6):
            raise ValueError("OOF fold must be 1–5")
        grouped[design].append({**source, "fold": fold, "actual": actual, "predicted": predicted,
                                "residual": actual - predicted, "absolute_error": abs(actual - predicted)})
    for design, rows in grouped.items():
        if len(rows) != 1016 or {row["observation_id"] for row in rows} != set(by_id):
            raise ValueError(f"OOF coverage or ID uniqueness failed: {design}")
        field = "canonical_molecular_id" if design == "molecular_grouped" else "doi"
        for fold in range(1, 6):
            test = {row[field] for row in rows if row["fold"] == fold}
            train = {row[field] for row in rows if row["fold"] != fold}
            if not test or test & train:
                raise ValueError(f"Group leakage or empty OOF fold: {design}/{fold}")
        suffix = "molecular_grouped" if design == "molecular_grouped" else "source_held_out"
        saved = _verified_csv(RECON_DIR / f"{suffix}_fold_metrics.csv", FOLD_SHA256[design])
        for fold in range(1, 6):
            subset = [row for row in rows if row["fold"] == fold]
            result = error_metrics(subset)
            recorded = next((row for row in saved if row["fold"] == str(fold)), None)
            if recorded is None or int(recorded["n_test"]) != len(subset) or any(
                not math.isclose(float(recorded[name]), result[name], rel_tol=1e-8, abs_tol=1e-7)
                for name in ("r2", "mae", "rmse")
            ):
                raise ValueError(f"Saved fold metrics disagree with OOF predictions: {design}/{fold}")
    return grouped, {design: error_metrics(rows) for design, rows in grouped.items()}, dataset_hash


def load_stageb_finalized() -> dict[str, object]:
    """Load only the final release's six displayed tables with manifest checks."""
    manifest_path = STAGEB_DIR / "manifests" / "SHA256SUMS.json"
    manifest_bytes = _verified_bytes(manifest_path, STAGEB_MANIFEST_SHA256, allow_crlf_checkout=True)
    manifest = json.loads(manifest_bytes.decode("utf-8"))
    tables: dict[str, list[dict[str, str]]] = {}
    for name, (filename, expected_count) in STAGEB_TABLES.items():
        relative = f"data/{filename}"
        expected_hash = manifest.get(relative)
        if not isinstance(expected_hash, str):
            raise ValueError(f"StageB_FINALIZED manifest lacks {relative}")
        rows = _verified_csv(STAGEB_DIR / relative, expected_hash, allow_crlf_checkout=True)
        if len(rows) != expected_count:
            raise ValueError(f"StageB_FINALIZED {name} count changed: {len(rows)}")
        tables[name] = rows

    def keys(name: str, field: str, *, allow_blank: bool = False) -> set[str]:
        values = [row[field].strip() for row in tables[name]]
        present = [value for value in values if value]
        if (not allow_blank and len(present) != len(values)) or len(present) != len(set(present)):
            raise ValueError(f"StageB_FINALIZED {name} has missing or duplicate {field}")
        return set(present)

    compounds = keys("compounds", "Compound_ID")
    evidence = keys("evidence", "Evidence_ID")
    drugs = keys("drugs", "Drug_Probe")
    studies = keys("studies", "Study_ID")
    pmids = keys("bibliography", "PMID", allow_blank=True)
    keys("warnings", "Warning_ID")
    for row in tables["evidence"]:
        if row["Compound_ID"] not in compounds or row["Drug"] not in drugs or row["Study_ID"] not in studies:
            raise ValueError(f"Stage B evidence reference does not resolve: {row['Evidence_ID']}")
        if row["PMID"] and row["PMID"] not in pmids:
            raise ValueError(f"Stage B bibliography reference does not resolve: {row['Evidence_ID']}")
    if len(evidence) != 317:
        raise ValueError("Stage B evidence ID coverage changed")
    tables["study_by_id"] = {row["Study_ID"]: row for row in tables["studies"]}
    tables["bibliography_by_pmid"] = {row["PMID"]: row for row in tables["bibliography"] if row["PMID"]}
    tables["compound_by_id"] = {row["Compound_ID"]: row for row in tables["compounds"]}
    tables["integrity_note"] = "The finalized manifest and displayed CSVs match Git's LF release bytes directly or after reversible CRLF-to-LF checkout normalization. No content changes are accepted."
    return tables
