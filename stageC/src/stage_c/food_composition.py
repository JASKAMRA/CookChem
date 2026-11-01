"""Validation and ingestion for source-backed food-composition measurements."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from .exceptions import ValidationError
from .provenance import sha256_file, utc_timestamp
from .unit_conversion import concentration_to_mg_per_kg

FIELDS = [
    "food_record_id", "food_name", "common_name", "scientific_name", "food_database", "food_database_record_id",
    "food_part", "cultivar_or_variety", "geographical_origin", "raw_or_processed_state", "compound_id", "compound_name",
    "food_use_classification", "pubchem_cid", "inchikey", "synonym_verification_status", "synonym_source", "mapping_review_status", "mapping_review_compound_id", "mapping_review_rationale", "mapping_review_source", "reported_concentration", "reported_unit", "normalized_concentration", "normalized_unit",
    "moisture_basis", "analytical_method", "extraction_method", "sample_size", "detection_limit", "quantification_limit",
    "source_title", "doi", "pmid", "database_reference", "source_url", "publication_year", "source_classification",
    "source_verification_status", "extraction_notes", "uncertainty_notes",
]
VERIFIED_CLASSES = {"Primary analytical measurement", "Peer-reviewed secondary source", "Authoritative food-composition database", "Verified laboratory measurement", "User-supplied measurement"}


def read_food_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None:
            raise ValidationError(f"Food-composition file has no header: {path}")
        missing = sorted(set(FIELDS) - set(reader.fieldnames))
        if missing:
            raise ValidationError(f"Food-composition schema is missing columns: {', '.join(missing)}")
        return [{field: (row.get(field) or "").strip() for field in FIELDS} for row in reader]


def validate_food_record(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not str(record.get("food_record_id", "")).strip(): errors.append("food_record_id is required")
    if not str(record.get("food_name", "")).strip(): errors.append("food_name is required")
    if not str(record.get("compound_name", "")).strip(): errors.append("compound_name is required")
    if record.get("reported_concentration", "") not in (None, ""):
        try:
            normalized = concentration_to_mg_per_kg(record["reported_concentration"], str(record.get("reported_unit", "")))
            if record.get("normalized_concentration", "") not in (None, ""):
                if str(normalized) != str(record["normalized_concentration"]): errors.append("normalized concentration does not match the reported value and unit")
                if record.get("normalized_unit") != "mg/kg": errors.append("normalized_unit must be mg/kg")
        except Exception as exc:
            errors.append(str(exc))
    elif record.get("normalized_concentration", "") not in (None, ""):
        errors.append("normalized concentration cannot exist when reported concentration is missing")
    if record.get("raw_or_processed_state", "").strip().lower() not in {"raw", "processed", "cooked", "fermented", "dried", "frozen", "other", ""}:
        errors.append("raw_or_processed_state must use a documented categorical value")
    if record.get("food_use_classification", "").strip().lower() not in {"ordinary food", "food ingredient", "supplement", "medicinal botanical", "extract", "uncertain", "not applicable", ""}:
        errors.append("food_use_classification must use a documented categorical value")
    if record.get("source_classification") not in VERIFIED_CLASSES | {"Unverified record", "Missing data"}:
        errors.append("source_classification must be an allowed evidence class")
    if record.get("source_classification") in VERIFIED_CLASSES and not (record.get("source_title") or record.get("source_url") or record.get("database_reference")):
        errors.append("verified records require a source title, URL, or database reference")
    if record.get("source_classification") in VERIFIED_CLASSES and record.get("source_verification_status", "").lower() not in {"verified", "full-text verified", "database verified", "user verified"}:
        errors.append("verified evidence class requires an explicit verified status")
    if record.get("source_verification_status", "").lower() in {"verified", "full-text verified", "database verified", "user verified"} and not record.get("reported_concentration"):
        errors.append("a verified quantitative record requires an explicit nonmissing reported concentration")
    doi = str(record.get("doi", "")).strip()
    if doi and not doi.lower().startswith("10."): errors.append("DOI must begin with 10.")
    pmid = str(record.get("pmid", "")).strip()
    if pmid and not pmid.isdigit(): errors.append("PMID must contain digits only")
    return errors


def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    output = {field: str(record.get(field, "") or "").strip() for field in FIELDS}
    reported = output["reported_concentration"]
    if not reported:
        output["normalized_concentration"] = ""
        output["normalized_unit"] = "mg/kg"
        return output
    output["normalized_concentration"] = str(concentration_to_mg_per_kg(reported, output["reported_unit"]))
    output["normalized_unit"] = "mg/kg"
    return output


def ingest_food_data(source: Path, destination: Path, manifest_path: Path) -> dict[str, Any]:
    records = read_food_csv(source)
    errors = []
    seen = set()
    normalized = []
    for index, record in enumerate(records, 2):
        issues = validate_food_record(record)
        if record["food_record_id"] in seen: issues.append("duplicate food_record_id")
        seen.add(record["food_record_id"])
        if issues: errors.append({"row": index, "food_record_id": record["food_record_id"], "errors": issues})
        else: normalized.append(normalize_record(record))
    if errors:
        raise ValidationError(f"Rejected {len(errors)} invalid food-composition row(s): {errors[:5]}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader(); writer.writerows(normalized)
    counts = {label: sum(r["source_classification"] == label for r in normalized) for label in sorted(VERIFIED_CLASSES | {"Unverified record", "Missing data"})}
    result = {"source_file": str(source.resolve()), "source_sha256": sha256_file(source), "output_file": str(destination.resolve()), "output_sha256": sha256_file(destination), "record_count": len(normalized), "source_classification_counts": counts, "ingested_at_utc": utc_timestamp(), "status": "PASS"}
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(__import__("json").dumps(result, indent=2), encoding="utf-8")
    return result


def load_food_data(path: Path) -> list[dict[str, str]]:
    return read_food_csv(path)
