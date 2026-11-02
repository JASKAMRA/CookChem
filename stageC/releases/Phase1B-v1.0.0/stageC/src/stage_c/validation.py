"""Scientific integrity and structural validation for Phase 1 inputs and outputs."""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from .compound_mapping import VERIFIED_STATUSES
from .exceptions import ValidationError
from .food_composition import FIELDS, validate_food_record
from .unit_conversion import concentration_to_mg_per_kg, volume_concentration_to_mg_per_l


def validate_food_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    errors = []
    seen = set()
    for index, record in enumerate(records):
        issues = validate_food_record(record)
        key = record.get("food_record_id", "")
        if key in seen: issues.append("duplicate food_record_id")
        seen.add(key)
        if set(record) - set(FIELDS): issues.append("unexpected fields: " + ", ".join(sorted(set(record) - set(FIELDS))))
        if record.get("reported_concentration") not in (None, "") and record.get("normalized_concentration") not in (None, ""):
            try:
                source_unit = str(record.get("reported_unit", ""))
                volume_basis = any(token in source_unit.casefold() for token in ("/l", "/ml", "/100 ml", "/100ml"))
                converter = volume_concentration_to_mg_per_l if volume_basis else concentration_to_mg_per_kg
                expected = str(converter(record["reported_concentration"], source_unit))
                if expected != str(record["normalized_concentration"]): issues.append("reported and normalized concentrations are inconsistent")
                expected_unit = "mg/L" if volume_basis else "mg/kg"
                if record.get("normalized_unit") != expected_unit: issues.append(f"normalized unit must be {expected_unit}")
            except Exception as exc: issues.append(str(exc))
        if issues: errors.append({"index": index, "food_record_id": key, "errors": issues})
    return errors


def validate_mapping_records(mappings: list[dict[str, Any]], compound_ids: set[str], food_ids: set[str]) -> list[dict[str, str]]:
    errors = []
    for row in mappings:
        if row.get("compound_id") and row["compound_id"] not in compound_ids: errors.append({"mapping_id": row.get("mapping_id", ""), "error": "compound ID does not resolve in Stage B"})
        if row.get("food_record_id") not in food_ids: errors.append({"mapping_id": row.get("mapping_id", ""), "error": "food record ID does not resolve"})
        if row.get("mapping_status") in VERIFIED_STATUSES and not row.get("rationale"): errors.append({"mapping_id": row.get("mapping_id", ""), "error": "verified mapping lacks rationale"})
        if row.get("mapping_status") == "Verified synonym match" and not row.get("mapping_source"): errors.append({"mapping_id": row.get("mapping_id", ""), "error": "verified synonym mapping lacks a source"})
    return errors


def validate_exposure_output(row: dict[str, Any]) -> list[str]:
    errors = []
    if row.get("calculation_status") == "Complete":
        for field in ("compound_id", "food_record_id", "source_concentration", "source_unit", "normalized_concentration", "initial_compound_amount", "estimated_consumed_amount", "calculation_method", "input_source_ids", "provenance"):
            if row.get(field) in (None, "", []): errors.append(f"complete exposure is missing {field}")
        if row.get("estimated_consumed_amount") in (0, "0", "0.0", "0.00"):
            # Zero consumption is valid when the user explicitly supplies a zero consumed fraction.
            if row.get("source_concentration") not in ("0", "0.0", "0.00") and str(row.get("consumed_fraction", "")) not in ("0", "0.0", "0.00"):
                errors.append("calculated zero conflicts with nonzero source concentration and consumed fraction")
    if row.get("calculation_status", "").startswith("Incomplete") and row.get("estimated_consumed_amount") not in (None, ""):
        errors.append("incomplete estimate must not expose a numeric consumed amount")
    if row.get("consumed_fraction") not in (None, ""):
        try:
            fraction = Decimal(str(row["consumed_fraction"]))
            if not fraction.is_finite() or not 0 <= fraction <= 1: errors.append("consumed fraction is outside [0,1]")
        except Exception: errors.append("consumed fraction is not numeric")
    if "retention" in str(row.get("calculation_method", "")).casefold() or "cooking" in str(row.get("calculation_method", "")).casefold():
        errors.append("Phase 1 output must not apply cooking-retention calculations")
    return errors


def validate_all(food_records: list[dict[str, Any]], mappings: list[dict[str, Any]], exposures: list[dict[str, Any]], compound_ids: set[str]) -> dict[str, Any]:
    food_errors = validate_food_records(food_records)
    food_ids = {str(r.get("food_record_id", "")) for r in food_records}
    mapping_errors = validate_mapping_records(mappings, compound_ids, food_ids)
    exposure_errors = [{"estimate_id": r.get("estimate_id", ""), "errors": validate_exposure_output(r)} for r in exposures if validate_exposure_output(r)]
    violations = []
    for r in food_records:
        if not r.get("reported_concentration") and r.get("normalized_concentration") not in (None, ""):
            violations.append({"food_record_id": r.get("food_record_id", ""), "error": "missing reported concentration was replaced by a normalized value"})
    return {"status": "PASS" if not (food_errors or mapping_errors or exposure_errors or violations) else "FAIL", "food_errors": food_errors, "mapping_errors": mapping_errors, "exposure_errors": exposure_errors, "scientific_integrity_violations": violations}
