"""Checksum and deterministic provenance helpers (standard library only)."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def deterministic_id(prefix: str, value: Any) -> str:
    digest = hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()[:20].upper()
    return f"{prefix}-{digest}"


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def calculation_provenance(estimate: dict[str, Any], stage_b_release: str, source_checksum: str) -> dict[str, Any]:
    """Return the reproducibility-critical fields without changing the estimate."""
    return {
        "estimate_id": estimate.get("estimate_id", ""),
        "stage_b_release": stage_b_release,
        "stage_b_manifest_sha256": source_checksum,
        "compound_id": estimate.get("compound_id", ""),
        "food_record_id": estimate.get("food_record_id", ""),
        "input_source_ids": estimate.get("input_source_ids", []),
        "source_concentration": estimate.get("source_concentration", ""),
        "source_unit": estimate.get("source_unit", ""),
        "normalized_concentration": estimate.get("normalized_concentration", ""),
        "normalized_unit": estimate.get("normalized_unit", ""),
        "ingredient_quantity": estimate.get("ingredient_quantity", ""),
        "ingredient_unit": estimate.get("ingredient_unit", ""),
        "consumed_fraction": estimate.get("consumed_fraction", ""),
        "formula": estimate.get("calculation_method", ""),
        "software_version": estimate.get("software_version", ""),
    }
