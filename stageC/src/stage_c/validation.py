"""Independent arithmetic checks and validation-evidence classification.

This module is deliberately separate from the recipe engine. It can calculate
small reference examples using its own conversion constants and records which
kind of validation was actually performed. Passing software tests is not
reported as published-data or external scientific validation.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from .exceptions import ValidationError


_MASS_TO_KG = {
    "kg": Decimal("1"), "g": Decimal("0.001"), "mg": Decimal("0.000001"),
    "ug": Decimal("0.000000001"), "µg": Decimal("0.000000001"), "μg": Decimal("0.000000001"),
}
_VOLUME_TO_L = {
    "l": Decimal("1"), "liter": Decimal("1"), "litre": Decimal("1"),
    "ml": Decimal("0.001"), "milliliter": Decimal("0.001"), "millilitre": Decimal("0.001"),
}
_MASS_CONC_TO_MG_PER_KG = {
    "mg/kg": Decimal("1"), "ug/kg": Decimal("0.001"), "µg/kg": Decimal("0.001"), "μg/kg": Decimal("0.001"),
    "mg/g": Decimal("1000"), "ug/g": Decimal("1"), "µg/g": Decimal("1"), "μg/g": Decimal("1"),
    "mg/100 g": Decimal("10"), "mg/100g": Decimal("10"), "ug/100 g": Decimal("0.01"), "ug/100g": Decimal("0.01"),
}
_VOLUME_CONC_TO_MG_PER_L = {
    "mg/l": Decimal("1"), "ug/l": Decimal("0.001"), "µg/l": Decimal("0.001"), "μg/l": Decimal("0.001"),
    "mg/ml": Decimal("1000"), "ug/ml": Decimal("1"), "mg/100 ml": Decimal("10"), "mg/100ml": Decimal("10"),
}
VALIDATION_LAYERS = {
    "software_correctness",
    "internal_regression",
    "independent_mathematical_verification",
    "published_data_comparison",
    "external_scientific_validation",
}


def _decimal(value: Any, label: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValidationError(f"{label} must be a finite decimal") from None
    if not result.is_finite() or result < 0:
        raise ValidationError(f"{label} must be finite and nonnegative")
    return result


def _unit(unit: str) -> str:
    return " ".join(str(unit).strip().lower().split()).replace("μg", "ug").replace("µg", "ug")


def independent_reference_exposure_mg(
    concentration: Any,
    concentration_unit: str,
    quantity: Any,
    quantity_unit: str,
    consumed_fraction: Any = "1",
) -> Decimal:
    """Compute a reference exposure using an independent, restricted unit table.

    No density or mass/volume conversion is performed. Mass concentration must
    pair with mass quantity; volume concentration must pair with volume quantity.
    The formula is C × quantity × consumed fraction, returned in mg.
    """
    c = _decimal(concentration, "concentration")
    q = _decimal(quantity, "quantity")
    f = _decimal(consumed_fraction, "consumed_fraction")
    if f > 1:
        raise ValidationError("consumed_fraction must be between zero and one")
    c_unit = _unit(concentration_unit)
    q_unit = _unit(quantity_unit)
    if c_unit in _MASS_CONC_TO_MG_PER_KG:
        if q_unit not in _MASS_TO_KG:
            raise ValidationError("mass concentration requires a mass quantity; density conversions are not performed")
        normalized_c = c * _MASS_CONC_TO_MG_PER_KG[c_unit]
        normalized_q = q * _MASS_TO_KG[q_unit]
    elif c_unit in _VOLUME_CONC_TO_MG_PER_L:
        if q_unit not in _VOLUME_TO_L:
            raise ValidationError("volume concentration requires a volume quantity; density conversions are not performed")
        normalized_c = c * _VOLUME_CONC_TO_MG_PER_L[c_unit]
        normalized_q = q * _VOLUME_TO_L[q_unit]
    else:
        raise ValidationError(f"unsupported reference concentration unit: {concentration_unit!r}")
    return normalized_c * normalized_q * f


def compare_to_reference(
    *,
    item_id: str,
    actual: Any,
    reference: Any,
    unit: str,
    reference_unit: str,
    measurement_basis: str,
    reference_basis: str,
    layer: str,
    tolerance: Any = "0",
    reference_id: str = "",
    source_reference: str = "",
    benchmark_dataset_id: str = "",
) -> dict[str, Any]:
    """Compare commensurate values while keeping validation layers distinct."""
    if layer not in VALIDATION_LAYERS:
        raise ValidationError(f"layer must be one of {sorted(VALIDATION_LAYERS)}")
    if layer == "external_scientific_validation":
        # External validity needs a study protocol, representative benchmark and
        # independent review. A two-number comparison cannot establish it.
        return {
            "item_id": item_id,
            "validation_layer": layer,
            "status": "NOT_ESTABLISHED",
            "reason": "An arithmetic comparison alone cannot establish external scientific validation.",
            "external_validation_claim": False,
            "benchmark_dataset_id": benchmark_dataset_id,
        }
    if not str(item_id).strip() or not str(unit).strip() or not str(reference_unit).strip():
        raise ValidationError("item_id and both units are required")
    if layer == "published_data_comparison" and (not reference_id.strip() or not source_reference.strip()):
        raise ValidationError("published-data comparisons require reference_id and source_reference")
    if _unit(unit) != _unit(reference_unit):
        return {
            "item_id": item_id,
            "validation_layer": layer,
            "status": "REJECTED_INCOMPARABLE",
            "reason": "Units differ; normalize independently before comparison.",
            "actual_unit": unit,
            "reference_unit": reference_unit,
            "external_validation_claim": False,
        }
    if not str(measurement_basis).strip() or not str(reference_basis).strip():
        return {
            "item_id": item_id,
            "validation_layer": layer,
            "status": "REJECTED_INCOMPARABLE",
            "reason": "Measurement basis is missing.",
            "external_validation_claim": False,
        }
    if measurement_basis.strip().casefold() != reference_basis.strip().casefold():
        return {
            "item_id": item_id,
            "validation_layer": layer,
            "status": "REJECTED_INCOMPARABLE",
            "reason": "Measurement bases differ; no basis conversion was supplied.",
            "actual_basis": measurement_basis,
            "reference_basis": reference_basis,
            "external_validation_claim": False,
        }
    actual_value = _decimal(actual, "actual")
    reference_value = _decimal(reference, "reference")
    tolerance_value = _decimal(tolerance, "tolerance")
    absolute_error = abs(actual_value - reference_value)
    relative_error = "" if reference_value == 0 else str(absolute_error / reference_value)
    return {
        "item_id": item_id,
        "validation_layer": layer,
        "status": "PASS" if absolute_error <= tolerance_value else "FAIL",
        "actual": str(actual_value),
        "reference": str(reference_value),
        "absolute_error": str(absolute_error),
        "relative_error": relative_error,
        "tolerance": str(tolerance_value),
        "unit": unit,
        "measurement_basis": measurement_basis,
        "reference_id": reference_id,
        "source_reference": source_reference,
        "external_validation_claim": False,
    }


def summarize_validation(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize evidence by validation layer; never infer external validation."""
    if not isinstance(records, list):
        raise ValidationError("records must be a list")
    layer_counts: dict[str, dict[str, int]] = {}
    published_errors: list[Decimal] = []
    for row in records:
        if not isinstance(row, dict):
            raise ValidationError("each validation record must be an object")
        layer = row.get("validation_layer")
        status = row.get("status")
        if layer not in VALIDATION_LAYERS:
            raise ValidationError(f"unknown validation layer: {layer!r}")
        if layer == "external_scientific_validation" and status != "NOT_ESTABLISHED":
            raise ValidationError("external scientific validation cannot be claimed by this arithmetic framework")
        if layer == "published_data_comparison" and status in {"PASS", "FAIL"}:
            if not str(row.get("reference_id", "")).strip() or not str(row.get("source_reference", "")).strip():
                raise ValidationError("published-data summary rows require reference_id and source_reference")
            if not str(row.get("unit", "")).strip() or not str(row.get("measurement_basis", "")).strip():
                raise ValidationError("published-data summary rows require a unit and measurement basis")
        counts = layer_counts.setdefault(layer, {})
        counts[status] = counts.get(status, 0) + 1
        if layer == "published_data_comparison" and status in {"PASS", "FAIL"}:
            published_errors.append(_decimal(row.get("absolute_error"), "absolute_error"))
    published_metrics: dict[str, Any] = {"n": len(published_errors), "mean_absolute_error": "", "rmse": ""}
    if published_errors:
        mae = sum(published_errors, Decimal(0)) / Decimal(len(published_errors))
        mse = sum((error * error for error in published_errors), Decimal(0)) / Decimal(len(published_errors))
        published_metrics.update(mean_absolute_error=str(mae), rmse=str(mse.sqrt()))
    return {
        "validation_layers": layer_counts,
        "published_comparison_metrics": published_metrics,
        "external_scientific_validation": "NOT_ESTABLISHED",
        "interpretation": "Software correctness, regression, independent arithmetic, and published-data comparisons are separate evidence categories.",
        "external_validation_claim": False,
    }


def verify_phase3_ingredient_arithmetic(estimate: dict[str, Any]) -> dict[str, Any]:
    """Independently recompute numeric fields in a Phase 3 ingredient result.

    This is a software/arithmetic check using inputs and provenance already
    present in the output. It does not independently validate source values or
    establish published-data agreement.
    """
    if not isinstance(estimate, dict):
        raise ValidationError("estimate must be a Phase 3 ingredient-result object")
    estimate_id = str(estimate.get("estimate_id", ""))
    base = {
        "item_id": estimate_id,
        "validation_layer": "independent_mathematical_verification",
        "external_validation_claim": False,
    }
    if estimate.get("calculation_status") != "Complete":
        return {**base, "status": "NOT_VERIFIABLE", "reason": "Phase 3 ingredient estimate is incomplete."}
    provenance = estimate.get("provenance")
    if not isinstance(provenance, dict):
        raise ValidationError("Phase 3 estimate requires provenance for independent arithmetic check")
    concentration = provenance.get("normalized_concentration")
    concentration_unit = provenance.get("normalized_unit")
    portion = provenance.get("normalized_portion_quantity")
    portion_unit = provenance.get("normalized_portion_unit")
    consumed = provenance.get("consumed_fraction")
    if any(value in (None, "") for value in (concentration, concentration_unit, portion, portion_unit, consumed)):
        return {**base, "status": "NOT_VERIFIABLE", "reason": "Required normalized inputs are absent from provenance."}
    if _unit(str(estimate.get("raw_concentration_unit", ""))) != _unit(str(concentration_unit)):
        return {**base, "status": "FAIL", "reason": "Top-level raw concentration unit differs from normalized provenance."}
    serving_multiplier = Decimal(1)
    if estimate.get("servings_consumed") not in (None, ""):
        serving_multiplier = _decimal(estimate.get("servings_consumed"), "servings_consumed")
        serving_multiplier += _decimal(estimate.get("leftovers_servings_consumed", "0"), "leftovers_servings_consumed")
    expected_raw = independent_reference_exposure_mg(concentration, concentration_unit, portion, portion_unit) * serving_multiplier
    expected_raw_consumed = expected_raw * _decimal(consumed, "provenance.consumed_fraction")
    comparisons: list[dict[str, str]] = []

    def check(field: str, expected: Decimal) -> None:
        actual = _decimal(estimate.get(field), field)
        comparisons.append({"field": field, "actual": str(actual), "expected": str(expected),
                           "absolute_error": str(abs(actual - expected))})

    check("raw_concentration", _decimal(concentration, "normalized_concentration"))
    check("raw_reference_amount_mg", expected_raw)
    check("raw_reference_consumed_amount_mg", expected_raw_consumed)
    if estimate.get("estimate_type") == "point":
        check("consumed_amount_low_mg", expected_raw_consumed)
        check("consumed_amount_high_mg", expected_raw_consumed)
    elif estimate.get("estimate_type") == "interval":
        retention = provenance.get("retention_evidence")
        if not isinstance(retention, dict) or not retention.get("evidence_id") or not retention.get("source_reference"):
            raise ValidationError("Phase 3 cooked interval must retain its Phase 2 source reference")
        gates = retention.get("compatibility_gates")
        gate_names = ("exact_compound_match", "food_matrix_match", "cooking_condition_match", "measurement_basis_compatible")
        if not isinstance(gates, dict) or any(gates.get(name) is not True for name in gate_names):
            return {**base, "status": "FAIL", "reason": "One or more Phase 2 retention compatibility gates are not true.", "comparisons": comparisons}
        retention_low = _decimal(retention.get("retention_low_percent"), "retention_low_percent")
        retention_high = _decimal(retention.get("retention_high_percent"), "retention_high_percent")
        if retention_high > 100 or retention_low > retention_high:
            return {**base, "status": "FAIL", "reason": "Phase 2 retention endpoints are outside ordered [0,100] bounds.", "comparisons": comparisons}
        if _unit(str(estimate.get("cooked_concentration_unit", ""))) != _unit(str(concentration_unit)):
            return {**base, "status": "FAIL", "reason": "Cooked and raw concentration bases differ.", "comparisons": comparisons}
        expected_cooked_low = _decimal(concentration, "normalized_concentration") * retention_low / Decimal(100)
        expected_cooked_high = _decimal(concentration, "normalized_concentration") * retention_high / Decimal(100)
        check("cooked_concentration_low", expected_cooked_low)
        check("cooked_concentration_high", expected_cooked_high)
        cooked_portion = retention.get("normalized_cooked_portion_quantity")
        cooked_unit = retention.get("normalized_cooked_portion_unit")
        cooked_low = estimate.get("cooked_concentration_low")
        cooked_high = estimate.get("cooked_concentration_high")
        cooked_concentration_unit = estimate.get("cooked_concentration_unit")
        if any(value in (None, "") for value in (cooked_portion, cooked_unit, cooked_low, cooked_high, cooked_concentration_unit)):
            return {**base, "status": "NOT_VERIFIABLE", "reason": "Cooked interval provenance or normalized inputs are absent.", "comparisons": comparisons}
        expected_low = independent_reference_exposure_mg(expected_cooked_low, cooked_concentration_unit, cooked_portion, cooked_unit) * serving_multiplier * _decimal(consumed, "provenance.consumed_fraction")
        expected_high = independent_reference_exposure_mg(expected_cooked_high, cooked_concentration_unit, cooked_portion, cooked_unit) * serving_multiplier * _decimal(consumed, "provenance.consumed_fraction")
        check("consumed_amount_low_mg", expected_low)
        check("consumed_amount_high_mg", expected_high)
    else:
        raise ValidationError(f"unsupported Phase 3 estimate_type: {estimate.get('estimate_type')!r}")
    passed = all(Decimal(row["absolute_error"]) == 0 for row in comparisons)
    return {**base, "status": "PASS" if passed else "FAIL", "comparisons": comparisons,
            "method": "independent Decimal arithmetic over Phase 3 normalized provenance inputs"}


def verify_phase3_aggregate_arithmetic(output: dict[str, Any]) -> dict[str, Any]:
    """Check Phase 3 recipe/meal compound totals against component estimates."""
    if not isinstance(output, dict):
        raise ValidationError("output must be a Phase 3 recipe or meal result")
    ingredients = output.get("ingredient_results")
    if ingredients is None and isinstance(output.get("component_results"), list):
        ingredients = [row for component in output["component_results"]
                       if isinstance(component, dict)
                       for row in component.get("ingredient_results", [])]
    totals = output.get("compound_totals")
    raw_totals = output.get("raw_reference_totals")
    if not isinstance(ingredients, list) or not isinstance(totals, list) or not isinstance(raw_totals, list):
        raise ValidationError("Phase 3 output lacks ingredient_results, compound_totals, or raw_reference_totals")
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in ingredients:
        grouped.setdefault(str(row.get("compound_id", "")), []).append(row)
    total_ids = [str(row.get("compound_id", "")) for row in totals]
    raw_ids = [str(row.get("compound_id", "")) for row in raw_totals]
    total_map = {str(row.get("compound_id", "")): row for row in totals}
    raw_map = {str(row.get("compound_id", "")): row for row in raw_totals}
    checks: list[dict[str, Any]] = []
    if len(total_ids) != len(set(total_ids)):
        checks.append({"item_id": "", "field": "compound_totals", "status": "FAIL", "reason": "duplicate compound total IDs"})
    if len(raw_ids) != len(set(raw_ids)):
        checks.append({"item_id": "", "field": "raw_reference_totals", "status": "FAIL", "reason": "duplicate raw-reference total IDs"})
    for compound_id in sorted(set(total_ids) - set(grouped)):
        checks.append({"item_id": compound_id, "field": "compound_total", "status": "FAIL", "reason": "compound total has no ingredient inputs"})
    for compound_id in sorted(set(raw_ids) - set(grouped)):
        checks.append({"item_id": compound_id, "field": "raw_reference_total", "status": "FAIL", "reason": "raw-reference total has no ingredient inputs"})
    for compound_id, group in sorted(grouped.items()):
        total = total_map.get(compound_id)
        if total is None:
            checks.append({"item_id": compound_id, "status": "FAIL", "reason": "compound total missing"})
            continue
        complete = all(row.get("calculation_status") == "Complete" for row in group)
        if not complete:
            status = "PASS" if total.get("calculation_status") != "Complete" and total.get("consumed_amount_low_mg", "") in (None, "") and total.get("consumed_amount_high_mg", "") in (None, "") else "FAIL"
            checks.append({"item_id": compound_id, "field": "compound_total_availability", "status": status,
                           "reason": "unresolved component correctly blocks numeric aggregate" if status == "PASS" else "unresolved component must block numeric aggregate"})
        else:
            if total.get("calculation_status") != "Complete":
                checks.append({"item_id": compound_id, "field": "calculation_status", "status": "FAIL",
                               "reason": "complete ingredient group must have a complete compound total"})
            else:
                expected_ids = sorted(str(row.get("estimate_id", "")) for row in group)
                if sorted(str(value) for value in total.get("input_estimate_ids", [])) != expected_ids:
                    checks.append({"item_id": compound_id, "field": "input_estimate_ids", "status": "FAIL",
                                   "reason": "compound total input estimate references do not match ingredients"})
                expected_type = "interval" if any(row.get("estimate_type") == "interval" for row in group) else "point"
                if total.get("estimate_type") != expected_type:
                    checks.append({"item_id": compound_id, "field": "estimate_type", "status": "FAIL",
                                   "reason": "compound total type does not match component estimate types"})
                expected_low = sum((_decimal(row.get("consumed_amount_low_mg"), "ingredient low") for row in group), Decimal(0))
                expected_high = sum((_decimal(row.get("consumed_amount_high_mg"), "ingredient high") for row in group), Decimal(0))
                for field, expected in (("consumed_amount_low_mg", expected_low), ("consumed_amount_high_mg", expected_high)):
                    actual = _decimal(total.get(field), f"compound total {field}")
                    checks.append({"item_id": compound_id, "field": field,
                                   "actual": str(actual), "expected": str(expected),
                                   "status": "PASS" if actual == expected else "FAIL"})
        raw = raw_map.get(compound_id)
        known = [row.get("raw_reference_consumed_amount_mg") for row in group]
        raw_complete = all(value not in (None, "") for value in known)
        if raw is None:
            checks.append({"item_id": compound_id, "field": "raw_reference_total", "status": "FAIL", "reason": "raw-reference total missing"})
        elif raw_complete:
            expected_ids = sorted(str(row.get("estimate_id", "")) for row in group)
            if sorted(str(value) for value in raw.get("input_estimate_ids", [])) != expected_ids:
                checks.append({"item_id": compound_id, "field": "raw_reference_input_estimate_ids", "status": "FAIL",
                               "reason": "raw-reference total input estimate references do not match ingredients"})
            expected_raw = sum((_decimal(value, "raw_reference_consumed_amount_mg") for value in known), Decimal(0))
            actual_raw = raw.get("raw_reference_amount_mg")
            status = "PASS" if actual_raw not in (None, "") and _decimal(actual_raw, "raw_reference_amount_mg") == expected_raw else "FAIL"
            checks.append({"item_id": compound_id, "field": "raw_reference_amount_mg", "actual": actual_raw or "",
                           "expected": str(expected_raw), "status": status})
        else:
            status = "PASS" if raw.get("calculation_status") != "Complete" and raw.get("raw_reference_amount_mg", "") in (None, "") else "FAIL"
            checks.append({"item_id": compound_id, "field": "raw_reference_total_availability", "status": status,
                           "reason": "missing component correctly withholds raw-reference total" if status == "PASS" else "missing component must withhold raw-reference total"})
    return {
        "output_id": str(output.get("recipe_id", output.get("meal_id", ""))),
        "validation_layer": "software_correctness",
        "checks": checks,
        "status": "PASS" if all(row["status"] == "PASS" for row in checks) else "FAIL",
        "external_validation_claim": False,
        "method": "independent aggregation of Phase 3 ingredient estimates; no published-data comparison",
    }


# Phase 1 public API retained for CLI and historical tests/releases.
def validate_food_records(records: list[dict[str, Any]], compound_ids: set[str] | None = None) -> list[dict[str, Any]]:
    from .compound_mapping import VERIFIED_STATUSES
    from .food_composition import FIELDS, validate_food_record

    errors = []
    seen = set()
    for index, record in enumerate(records):
        issues = validate_food_record(record)
        key = record.get("food_record_id", "")
        if key in seen:
            issues.append("duplicate food_record_id")
        seen.add(key)
        if compound_ids is not None:
            for field in ("compound_id", "mapping_review_compound_id"):
                compound_id = str(record.get(field, "")).strip()
                if compound_id and compound_id not in compound_ids:
                    issues.append(f"{field} does not resolve in Stage B: {compound_id}")
        if set(record) - set(FIELDS):
            issues.append("unexpected fields: " + ", ".join(sorted(set(record) - set(FIELDS))))
        if record.get("reported_concentration") not in (None, "") and record.get("normalized_concentration") not in (None, ""):
            try:
                from .unit_conversion import concentration_to_mg_per_kg, volume_concentration_to_mg_per_l
                source_unit = str(record.get("reported_unit", ""))
                volume_basis = any(token in source_unit.casefold() for token in ("/l", "/ml", "/100 ml", "/100ml"))
                converter = volume_concentration_to_mg_per_l if volume_basis else concentration_to_mg_per_kg
                expected = str(converter(record["reported_concentration"], source_unit))
                if expected != str(record["normalized_concentration"]):
                    issues.append("reported and normalized concentrations are inconsistent")
                expected_unit = "mg/L" if volume_basis else "mg/kg"
                if record.get("normalized_unit") != expected_unit:
                    issues.append(f"normalized unit must be {expected_unit}")
            except Exception as exc:
                issues.append(str(exc))
        if issues:
            errors.append({"index": index, "food_record_id": key, "errors": issues})
    return errors


def validate_mapping_records(mappings: list[dict[str, Any]], compound_ids: set[str], food_ids: set[str]) -> list[dict[str, str]]:
    from .compound_mapping import VERIFIED_STATUSES

    errors = []
    seen_mapping_ids: set[str] = set()
    for row in mappings:
        mapping_id = str(row.get("mapping_id", "")).strip()
        if not mapping_id:
            errors.append({"mapping_id": "", "error": "mapping_id is required"})
        elif mapping_id in seen_mapping_ids:
            errors.append({"mapping_id": mapping_id, "error": "duplicate mapping_id"})
        seen_mapping_ids.add(mapping_id)
        if row.get("compound_id") and row["compound_id"] not in compound_ids:
            errors.append({"mapping_id": row.get("mapping_id", ""), "error": "compound ID does not resolve in Stage B"})
        candidate_ids = {value.strip() for value in str(row.get("candidate_compound_ids", "")).split("|") if value.strip()}
        for candidate_id in sorted(candidate_ids - compound_ids):
            errors.append({"mapping_id": row.get("mapping_id", ""), "error": f"candidate compound ID does not resolve in Stage B: {candidate_id}"})
        if row.get("food_record_id") not in food_ids:
            errors.append({"mapping_id": row.get("mapping_id", ""), "error": "food record ID does not resolve"})
        if row.get("mapping_status") in VERIFIED_STATUSES and not row.get("rationale"):
            errors.append({"mapping_id": row.get("mapping_id", ""), "error": "verified mapping lacks rationale"})
        if row.get("mapping_status") == "Verified synonym match" and not row.get("mapping_source"):
            errors.append({"mapping_id": row.get("mapping_id", ""), "error": "verified synonym mapping lacks a source"})
    return errors


def validate_exposure_output(row: dict[str, Any]) -> list[str]:
    errors = []
    if row.get("calculation_status") == "Complete":
        for field in ("compound_id", "food_record_id", "source_concentration", "source_unit", "normalized_concentration", "initial_compound_amount", "estimated_consumed_amount", "calculation_method", "input_source_ids", "provenance"):
            if row.get(field) in (None, "", []):
                errors.append(f"complete exposure is missing {field}")
        if row.get("estimated_consumed_amount") in (0, "0", "0.0", "0.00"):
            if row.get("source_concentration") not in ("0", "0.0", "0.00") and str(row.get("consumed_fraction", "")) not in ("0", "0.0", "0.00"):
                errors.append("calculated zero conflicts with nonzero source concentration and consumed fraction")
    if str(row.get("calculation_status", "")).startswith("Incomplete") and row.get("estimated_consumed_amount") not in (None, ""):
        errors.append("incomplete estimate must not expose a numeric consumed amount")
    if row.get("consumed_fraction") not in (None, ""):
        try:
            fraction = Decimal(str(row["consumed_fraction"]))
            if not fraction.is_finite() or not 0 <= fraction <= 1:
                errors.append("consumed fraction is outside [0,1]")
        except Exception:
            errors.append("consumed fraction is not numeric")
    if "retention" in str(row.get("calculation_method", "")).casefold() or "cooking" in str(row.get("calculation_method", "")).casefold():
        errors.append("Phase 1 output must not apply cooking-retention calculations")
    return errors


def validate_all(food_records: list[dict[str, Any]], mappings: list[dict[str, Any]], exposures: list[dict[str, Any]], compound_ids: set[str]) -> dict[str, Any]:
    food_errors = validate_food_records(food_records, compound_ids)
    food_ids = {str(record.get("food_record_id", "")) for record in food_records}
    mapping_errors = validate_mapping_records(mappings, compound_ids, food_ids)
    exposure_errors = [{"estimate_id": row.get("estimate_id", ""), "errors": validate_exposure_output(row)}
                       for row in exposures if validate_exposure_output(row)]
    violations = []
    for row in food_records:
        if not row.get("reported_concentration") and row.get("normalized_concentration") not in (None, ""):
            violations.append({"food_record_id": row.get("food_record_id", ""), "error": "missing reported concentration was replaced by a normalized value"})
    return {"status": "PASS" if not (food_errors or mapping_errors or exposure_errors or violations) else "FAIL",
            "food_errors": food_errors, "mapping_errors": mapping_errors, "exposure_errors": exposure_errors,
            "scientific_integrity_violations": violations}
