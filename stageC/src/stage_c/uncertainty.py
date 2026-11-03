"""Conservative interval uncertainty and one-at-a-time sensitivity helpers.

This module accepts only explicit, source-referenced factor bounds. It does not
infer SDs, distributions, correlations, confidence levels, or default error bars.
Evidence retention intervals remain bounds and are never interpreted as
probability distributions.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from .exceptions import ValidationError


_BOUND_SOURCE = {
    "reported_interval": "reported",  # backward-compatible label
    "source_reported_range": "reported",
    "measured_interval": "measured",  # backward-compatible label
    "analytical_measurement_variability": "measured",
    "derived_interval": "derived",  # backward-compatible label
    "literature_derived_range": "literature",
    "assumed_scenario": "assumed",  # backward-compatible label
    "scenario_bound": "assumed",
    "model_prediction_uncertainty": "model_prediction",
}
_ALLOWED_BOUND_TYPES = set(_BOUND_SOURCE)
_SUPPORTED_SOURCES = set(_BOUND_SOURCE.values())


def _missing_reason(code: str, factor: str, reason: str) -> dict[str, str]:
    """Build a stable, machine-readable explanation for withheld bounds."""
    return {"code": code, "factor": factor, "reason": reason}


def _decimal(value: Any, label: str) -> Decimal:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValidationError(f"{label} must be a finite decimal") from None
    if not number.is_finite() or number < 0:
        raise ValidationError(f"{label} must be finite and nonnegative")
    return number


def _factor_interval(factor: dict[str, Any]) -> tuple[Decimal, Decimal, Decimal, dict[str, Any]]:
    if not isinstance(factor, dict):
        raise ValidationError("each factor must be an object")
    name = str(factor.get("name", "")).strip()
    unit = str(factor.get("unit", "")).strip()
    if not name or not unit:
        raise ValidationError("each factor requires a name and unit")
    point = _decimal(factor.get("value"), f"{name}.value")
    bounds = factor.get("bounds")
    if not isinstance(bounds, dict):
        raise ValidationError(f"{name}.bounds must be an explicit source-referenced interval")
    low = _decimal(bounds.get("low"), f"{name}.bounds.low")
    high = _decimal(bounds.get("high"), f"{name}.bounds.high")
    if not low <= point <= high:
        raise ValidationError(f"{name}: bounds must contain the reported point value")
    bound_type = bounds.get("type")
    if bound_type not in _ALLOWED_BOUND_TYPES:
        raise ValidationError(f"{name}.bounds.type must identify a supported interval or scenario")
    source_type = bounds.get("source_type")
    if source_type not in _SUPPORTED_SOURCES:
        raise ValidationError(f"{name}.bounds.source_type must be reported, measured, derived, or assumed")
    expected_source = _BOUND_SOURCE[bound_type]
    if source_type != expected_source:
        raise ValidationError(f"{name}: {bound_type} requires source_type={expected_source!r}")
    reference = str(bounds.get("source_reference", "")).strip()
    if not reference:
        raise ValidationError(f"{name}.bounds.source_reference is required")
    method = str(bounds.get("method", "")).strip()
    if source_type in {"derived", "literature", "model_prediction"} and not method:
        raise ValidationError(f"{name}.bounds.method is required for {source_type} bounds")
    prediction_metadata: dict[str, str] = {}
    if source_type == "model_prediction":
        for field in ("model_artifact_sha256", "target_contract_sha256"):
            digest = str(bounds.get(field, "")).strip().lower()
            if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
                raise ValidationError(f"{name}.bounds.{field} must be a 64-character SHA-256 digest")
            prediction_metadata[field] = digest
        prediction_reference = str(bounds.get("prediction_reference", "")).strip()
        if not prediction_reference:
            raise ValidationError(f"{name}.bounds.prediction_reference is required for model-prediction bounds")
        prediction_metadata["prediction_reference"] = prediction_reference
    metadata = {
        "name": name,
        "unit": unit,
        "type": bound_type,
        "source_type": source_type,
        "source_reference": reference,
        "method": method,
        **prediction_metadata,
    }
    return point, low, high, metadata


def propagate_product_interval(
    factors: list[dict[str, Any]], *, result_unit: str, estimate_id: str = ""
) -> dict[str, Any]:
    """Propagate explicit nonnegative bounds through a multiplicative formula.

    Every factor must carry a source-referenced interval. Inputs are expected in
    already-normalized compatible units, e.g. mg/kg × kg × fraction. Positive
    factor products are monotone, so the conservative product interval is the
    product of lower and upper endpoints. No distribution is assumed.
    """
    if not isinstance(factors, list) or not factors:
        raise ValidationError("factors must be a nonempty list")
    if not str(result_unit).strip():
        raise ValidationError("result_unit is required")
    point_total = Decimal(1)
    low_total = Decimal(1)
    high_total = Decimal(1)
    metadata: list[dict[str, Any]] = []
    for factor in factors:
        point, low, high, record = _factor_interval(factor)
        point_total *= point
        low_total *= low
        high_total *= high
        metadata.append(record)
    assumed = any(row["source_type"] == "assumed" or row["type"] == "assumed_scenario" for row in metadata)
    return {
        "estimate_id": estimate_id,
        "uncertainty_status": "SCENARIO_ENVELOPE" if assumed else "BOUNDED_INTERVAL",
        "central_amount": str(point_total),
        "amount_low": str(low_total),
        "amount_high": str(high_total),
        "unit": result_unit,
        "interval_kind": "assumption-dependent scenario range" if assumed else "source-supported conservative bound; not a probability interval",
        "distribution_assumed": False,
        "correlation_assumed": False,
        "factors": metadata,
        "missing_uncertainty_reasons": [],
        "limitations": [
            "Inputs must be normalized to dimensionally compatible units before propagation.",
            "No probability distribution, confidence level, or independence assumption was used.",
            "An assumed input produces a scenario envelope, not measured uncertainty.",
        ],
    }


def assess_uncertainty_availability(
    factors: list[dict[str, Any]], *, estimate_id: str = "", result_unit: str = "mg"
) -> dict[str, Any]:
    """Report why total uncertainty is or is not quantifiable.

    Point values without uncertainty bounds are retained as deterministic inputs;
    they are never silently treated as exact measurements.
    """
    if not isinstance(factors, list) or not factors:
        raise ValidationError("factors must be a nonempty list")
    missing: list[str] = []
    missing_reasons: list[dict[str, str]] = []
    known: list[dict[str, Any]] = []
    for i, factor in enumerate(factors):
        if not isinstance(factor, dict) or not str(factor.get("name", "")).strip():
            raise ValidationError(f"factors[{i}] requires a name")
        if "value" not in factor:
            raise ValidationError(f"factors[{i}].value is required")
        _decimal(factor["value"], f"{factor['name']}.value")
        if factor.get("bounds") is None:
            name = str(factor["name"])
            missing.append(name)
            missing_reasons.append(_missing_reason(
                "NO_SUPPORTED_BOUNDS", name,
                "No source-supported interval was supplied for this required factor."))
        else:
            _, _, _, meta = _factor_interval(factor)
            known.append(meta)
    if not missing:
        return propagate_product_interval(factors, result_unit=result_unit, estimate_id=estimate_id)
    return {
        "estimate_id": estimate_id,
        "uncertainty_status": "PARTIALLY_QUANTIFIABLE" if known else "NOT_QUANTIFIABLE",
        "amount_low": "",
        "amount_high": "",
        "unit": result_unit,
        "distribution_assumed": False,
        "correlation_assumed": False,
        "known_uncertainty_factors": known,
        "missing_uncertainty_factors": missing,
        "missing_uncertainty_reasons": missing_reasons,
        "limitations": ["A total interval is withheld because at least one required factor has no supported uncertainty bounds."],
    }


def assess_phase3_estimate_uncertainty(estimate: dict[str, Any]) -> dict[str, Any]:
    """Classify uncertainty already represented by a Phase 3 ingredient result.

    Phase 3 currently emits either a point estimate or a retention-bounded
    interval. A Phase 2 interval is accepted only when its evidence ID and
    source reference are carried through the Phase 3 provenance. The result is
    explicitly conditional on the point-valued recipe quantities and fractions;
    absent measurement uncertainty is never filled in.
    """
    if not isinstance(estimate, dict):
        raise ValidationError("estimate must be a Phase 3 ingredient-result object")
    estimate_id = str(estimate.get("estimate_id", ""))
    common = {
        "estimate_id": estimate_id,
        "compound_id": str(estimate.get("compound_id", "")),
        "distribution_assumed": False,
        "correlation_assumed": False,
        "basis": "Phase 3 ingredient result; uncertainty in unreported inputs is not quantified",
    }
    if estimate.get("calculation_status") != "Complete":
        missing_inputs = estimate.get("missing_inputs")
        missing_inputs = [str(item) for item in missing_inputs if str(item).strip()] if isinstance(missing_inputs, list) else []
        reasons = [_missing_reason("PHASE3_ESTIMATE_INCOMPLETE", item,
                                   "Phase 3 did not calculate this estimate because a required input was unresolved.")
                   for item in missing_inputs]
        if not reasons:
            reasons = [_missing_reason("PHASE3_ESTIMATE_INCOMPLETE", "Phase 3 estimate",
                                       "The Phase 3 result is incomplete; its missing inputs are not itemized.")]
        return {
            **common,
            "uncertainty_status": "NOT_QUANTIFIABLE",
            "amount_low": "",
            "amount_high": "",
            "unit": "mg",
            "missing_uncertainty_factors": missing_inputs or ["incomplete Phase 3 estimate"],
            "missing_uncertainty_reasons": reasons,
        }
    kind = estimate.get("estimate_type")
    if kind == "point":
        point = estimate.get("consumed_amount_low_mg")
        if point in (None, "") or str(point) != str(estimate.get("consumed_amount_high_mg", "")):
            raise ValidationError("Phase 3 point estimate must have equal, nonempty low and high amounts")
        _decimal(point, "consumed_amount_mg")
        return {
            **common,
            "uncertainty_status": "POINT_ESTIMATE_ONLY",
            "point_amount": str(point),
            "amount_low": "",
            "amount_high": "",
            "unit": "mg",
            "missing_uncertainty_factors": [
                "food concentration analytical uncertainty",
                "ingredient quantity measurement uncertainty",
                "serving and consumed fraction uncertainty",
            ],
            "missing_uncertainty_reasons": [
                _missing_reason("NO_ANALYTICAL_UNCERTAINTY", "food concentration analytical uncertainty",
                                "The current food-composition record does not provide a structured supported interval."),
                _missing_reason("NO_QUANTITY_UNCERTAINTY", "ingredient quantity measurement uncertainty",
                                "The recipe quantity is a point input and has no supported measurement interval."),
                _missing_reason("NO_FRACTION_UNCERTAINTY", "serving and consumed fraction uncertainty",
                                "The recipe fractions are point inputs and have no supported uncertainty interval."),
            ],
            "limitations": ["A point estimate is not treated as an exact value or a zero-width uncertainty interval."],
        }
    if kind != "interval":
        raise ValidationError(f"unsupported Phase 3 estimate_type: {kind!r}")
    low = _decimal(estimate.get("consumed_amount_low_mg"), "consumed_amount_low_mg")
    high = _decimal(estimate.get("consumed_amount_high_mg"), "consumed_amount_high_mg")
    if high < low:
        raise ValidationError("Phase 3 interval high amount cannot be less than low amount")
    provenance = estimate.get("provenance")
    retention = provenance.get("retention_evidence") if isinstance(provenance, dict) else None
    if (not isinstance(retention, dict) or not str(retention.get("evidence_id", "")).strip()
            or not str(retention.get("source_reference", "")).strip()):
        raise ValidationError("Phase 3 interval lacks source-referenced Phase 2 retention evidence")
    gates = retention.get("compatibility_gates")
    required_gates = ("exact_compound_match", "food_matrix_match", "cooking_condition_match", "measurement_basis_compatible")
    if not isinstance(gates, dict) or any(gates.get(key) is not True for key in required_gates):
        raise ValidationError("Phase 3 interval lacks all passing Phase 2 compatibility gates")
    raw_unit = str(provenance.get("normalized_unit", "")).strip().casefold()
    cooked_unit = str(estimate.get("cooked_concentration_unit", "")).strip().casefold()
    if raw_unit != cooked_unit or raw_unit not in {"mg/kg", "mg/l"}:
        raise ValidationError("Phase 3 cooked interval must preserve a supported concentration basis")
    retention_low = _decimal(retention.get("retention_low_percent"), "retention_low_percent")
    retention_high = _decimal(retention.get("retention_high_percent"), "retention_high_percent")
    if retention_high > 100 or retention_low > retention_high:
        raise ValidationError("Phase 2 retention bounds must satisfy 0 <= low <= high <= 100")
    raw_concentration = _decimal(provenance.get("normalized_concentration"), "normalized_concentration")
    expected_concentrations = (raw_concentration * retention_low / Decimal(100),
                               raw_concentration * retention_high / Decimal(100))
    cooked_concentrations = (_decimal(estimate.get("cooked_concentration_low"), "cooked_concentration_low"),
                             _decimal(estimate.get("cooked_concentration_high"), "cooked_concentration_high"))
    if cooked_concentrations != expected_concentrations:
        raise ValidationError("Phase 3 cooked concentration bounds do not match retained Phase 2 percentages")
    cooked_portion = _decimal(retention.get("normalized_cooked_portion_quantity"), "normalized_cooked_portion_quantity")
    portion_unit = str(retention.get("normalized_cooked_portion_unit", "")).strip().casefold()
    expected_portion_unit = "kg" if raw_unit == "mg/kg" else "l"
    if portion_unit != expected_portion_unit:
        raise ValidationError("Phase 3 cooked portion unit does not match its concentration basis")
    consumed_fraction = _decimal(provenance.get("consumed_fraction"), "consumed_fraction")
    if consumed_fraction > 1:
        raise ValidationError("Phase 3 provenance consumed_fraction must be in [0,1]")
    serving_multiplier = Decimal(1)
    if estimate.get("servings_consumed") not in (None, ""):
        serving_multiplier = _decimal(estimate.get("servings_consumed"), "servings_consumed")
        serving_multiplier += _decimal(estimate.get("leftovers_servings_consumed", "0"), "leftovers_servings_consumed")
    expected_amounts = tuple(concentration * cooked_portion * consumed_fraction * serving_multiplier
                             for concentration in expected_concentrations)
    if (low, high) != expected_amounts:
        raise ValidationError("Phase 3 exposure interval does not match its source bounds and normalized portions")
    return {
        **common,
        "uncertainty_status": "BOUNDED_INTERVAL_CONDITIONAL_ON_RECIPE_INPUTS",
        "amount_low": str(low),
        "amount_high": str(high),
        "unit": "mg",
        "interval_kind": "Phase 2 retention evidence bounds propagated through Phase 3; not a probability interval",
        "supporting_evidence": [{"evidence_id": retention["evidence_id"], "source_reference": retention["source_reference"]}],
        "missing_uncertainty_factors": [
            "food concentration analytical uncertainty",
            "ingredient quantity measurement uncertainty",
            "serving and consumed fraction uncertainty",
        ],
        "missing_uncertainty_reasons": [
            _missing_reason("NO_ANALYTICAL_UNCERTAINTY", "food concentration analytical uncertainty",
                            "The interval covers retention only; the food-composition input has no structured analytical interval."),
            _missing_reason("NO_QUANTITY_UNCERTAINTY", "ingredient quantity measurement uncertainty",
                            "The interval is conditional on point-valued recipe quantities without a supported measurement interval."),
            _missing_reason("NO_FRACTION_UNCERTAINTY", "serving and consumed fraction uncertainty",
                            "The interval is conditional on point-valued recipe fractions without a supported uncertainty interval."),
        ],
        "limitations": [
            "The interval reflects retention bounds only, conditional on reported food concentration, cooked quantity, serving fraction, and consumed fraction.",
            "No analytical, quantity-measurement, or fraction uncertainty was inferred.",
            "No probability distribution, confidence level, or correlation assumption was used.",
        ],
    }


def assess_phase3_structured_input_uncertainty(estimate: dict[str, Any]) -> dict[str, Any]:
    """Propagate explicit raw-food concentration, quantity and fraction bounds.

    The Stage C calculation remains authoritative for the point amount. This
    helper only creates a bound when every multiplicative raw-input factor has
    explicit source-referenced bounds. It does not treat unsupported factors as
    exact. Cooked estimates retain their separate Phase 2 interval pathway.
    """
    if not isinstance(estimate, dict):
        raise ValidationError("estimate must be a Phase 3 ingredient-result object")
    estimate_id = str(estimate.get("estimate_id", ""))
    compound_id = str(estimate.get("compound_id", ""))
    if estimate.get("calculation_status") != "Complete":
        return {"estimate_id": estimate_id, "compound_id": compound_id, "uncertainty_status": "NOT_QUANTIFIABLE",
                "amount_low": "", "amount_high": "", "unit": "mg",
                "missing_uncertainty_factors": ["complete Phase 3 estimate"],
                "limitations": ["Incomplete exposure estimates cannot receive propagated input bounds."]}
    provenance = estimate.get("provenance")
    if not isinstance(provenance, dict):
        raise ValidationError("Phase 3 estimate provenance must be an object")
    if estimate.get("estimate_type") != "point" or estimate.get("cooked_exposure_status") != "RAW_FOOD_NO_COOKING_ADJUSTMENT":
        return {"estimate_id": estimate_id, "compound_id": compound_id, "uncertainty_status": "NOT_QUANTIFIABLE",
                "amount_low": "", "amount_high": "", "unit": "mg",
                "missing_uncertainty_factors": ["cooked retention or prepared-food factor intervals"],
                "missing_uncertainty_reasons": [
                    _missing_reason("COOKED_INPUT_PROPAGATION_NOT_AVAILABLE", "cooked exposure inputs",
                                    "Cooked results use the separate compatible Phase 2 pathway; structured cooked-input uncertainty has no validated combined propagation contract.")],
                "limitations": ["Use the existing Phase 2 retention interval assessment; no cooked-input interval is inferred."]}

    expected = {
        "food_concentration": (estimate.get("raw_concentration"), estimate.get("raw_concentration_unit")),
        "ingredient_quantity": (provenance.get("normalized_ingredient_quantity"), provenance.get("normalized_ingredient_quantity_unit")),
        "serving_fraction": (provenance.get("serving_fraction"), "fraction"),
        "consumed_fraction": (provenance.get("consumed_fraction"), "fraction"),
    }
    source_inputs = provenance.get("uncertainty_inputs")
    source_inputs = source_inputs if isinstance(source_inputs, dict) else {}
    factors: list[dict[str, Any]] = []
    for name, (point, unit) in expected.items():
        if point in (None, "") or unit in (None, ""):
            raise ValidationError(f"Phase 3 provenance lacks the point value or unit for {name}")
        source_factor = source_inputs.get(name)
        if source_factor is None:
            factors.append({"name": name, "value": str(point), "unit": str(unit)})
            continue
        if not isinstance(source_factor, dict):
            raise ValidationError(f"uncertainty_inputs.{name} must be an object")
        if str(source_factor.get("name", "")) != name:
            raise ValidationError(f"uncertainty_inputs.{name}.name must equal {name!r}")
        if str(source_factor.get("unit", "")) != str(unit):
            raise ValidationError(f"uncertainty_inputs.{name}.unit must be {unit!r}")
        supplied_point = _decimal(source_factor.get("value"), f"uncertainty_inputs.{name}.value")
        if supplied_point != _decimal(point, f"Phase 3 {name} point"):
            raise ValidationError(f"uncertainty_inputs.{name}.value does not match the calculated Phase 3 input")
        factors.append(source_factor)

    result = assess_uncertainty_availability(factors, estimate_id=estimate_id, result_unit="mg")
    result["basis"] = "food concentration × normalized ingredient quantity × serving fraction × consumed fraction"
    result["compound_id"] = compound_id
    result["calculated_point_amount"] = str(estimate.get("consumed_amount_low_mg", ""))
    result["limitations"] = list(result.get("limitations", [])) + [
        "All four factors must have explicit source-referenced intervals before total lower and upper amounts are reported.",
        "Source-reported ranges and scenario bounds retain their type; no probability distribution is assumed.",
    ]
    result["supporting_factor_metadata"] = [
        {"name": factor["name"], "unit": factor["unit"],
         "bounds": factor.get("bounds")}
        for factor in factors if factor.get("bounds") is not None
    ]
    if result.get("uncertainty_status") in {"BOUNDED_INTERVAL", "SCENARIO_ENVELOPE"}:
        if _decimal(result["amount_low"], "propagated amount low") > _decimal(estimate["consumed_amount_low_mg"], "Phase 3 point amount"):
            raise ValidationError("propagated lower bound exceeds the Phase 3 point amount")
        if _decimal(result["amount_high"], "propagated amount high") < _decimal(estimate["consumed_amount_high_mg"], "Phase 3 point amount"):
            raise ValidationError("propagated upper bound is below the Phase 3 point amount")
    return result


def assess_phase3_output_uncertainty(output: dict[str, Any]) -> dict[str, Any]:
    """Summarize uncertainty for a Phase 3 recipe or meal output structure."""
    if not isinstance(output, dict):
        raise ValidationError("output must be a Phase 3 recipe or meal result")
    results = output.get("ingredient_results")
    if results is None and isinstance(output.get("component_results"), list):
        results = [row for component in output["component_results"]
                   if isinstance(component, dict)
                   for row in component.get("ingredient_results", [])]
    if not isinstance(results, list):
        raise ValidationError("output does not contain Phase 3 ingredient_results")
    classified = [assess_phase3_estimate_uncertainty(row) for row in results]
    counts: dict[str, int] = {}
    for row in classified:
        key = row["uncertainty_status"]
        counts[key] = counts.get(key, 0) + 1
    by_estimate = {str(source.get("estimate_id", "")): uncertainty
                   for source, uncertainty in zip(results, classified)}
    compound_summaries = []
    for total in output.get("compound_totals", []):
        if not isinstance(total, dict):
            continue
        references = [by_estimate.get(str(identifier))
                      for identifier in total.get("input_estimate_ids", [])]
        references = [row for row in references if row is not None]
        base = {"compound_id": str(total.get("compound_id", "")),
                "uncertainty_status": "NOT_QUANTIFIABLE", "amount_low": "", "amount_high": "", "unit": "mg",
                "distribution_assumed": False, "correlation_assumed": False}
        if total.get("calculation_status") != "Complete":
            missing_inputs = total.get("missing_inputs") if isinstance(total.get("missing_inputs"), list) else []
            reasons = [_missing_reason("PHASE3_TOTAL_INCOMPLETE", str(value),
                                       "At least one compound contribution is unresolved.") for value in missing_inputs]
            if not reasons:
                reasons = [_missing_reason("PHASE3_TOTAL_INCOMPLETE", "compound total",
                                           "The Phase 3 compound total is incomplete.")]
            compound_summaries.append({**base,
                                       "missing_uncertainty_factors": [str(value) for value in missing_inputs] or ["incomplete Phase 3 compound total"],
                                       "missing_uncertainty_reasons": reasons})
            continue
        if total.get("estimate_type") == "point":
            point_low = _decimal(total.get("consumed_amount_low_mg"), "compound total low")
            point_high = _decimal(total.get("consumed_amount_high_mg"), "compound total high")
            if point_low != point_high:
                raise ValidationError("Phase 3 point compound total must have equal low and high values")
            reasons = [reason for row in references for reason in row.get("missing_uncertainty_reasons", [])]
            if not reasons:
                reasons = [_missing_reason("COMPONENT_UNCERTAINTY_UNAVAILABLE", "component measurement uncertainty",
                                           "Component point values do not include structured measurement uncertainty.")]
            compound_summaries.append({**base, "uncertainty_status": "POINT_ESTIMATE_ONLY",
                                       "point_amount": str(point_low),
                                       "missing_uncertainty_factors": ["component measurement uncertainty"],
                                       "missing_uncertainty_reasons": reasons})
            continue
        if total.get("estimate_type") != "interval":
            raise ValidationError(f"unsupported Phase 3 compound total estimate_type: {total.get('estimate_type')!r}")
        interval_sources = [row for row in references if row.get("uncertainty_status") == "BOUNDED_INTERVAL_CONDITIONAL_ON_RECIPE_INPUTS"]
        if not interval_sources:
            raise ValidationError("Phase 3 interval compound total has no source-supported interval component")
        missing_reasons = [reason for row in references for reason in row.get("missing_uncertainty_reasons", [])]
        unique_reasons = {(reason.get("code"), reason.get("factor"), reason.get("reason")): reason
                          for reason in missing_reasons}
        compound_summaries.append({
            **base,
            "uncertainty_status": "BOUNDED_INTERVAL_CONDITIONAL_ON_RECIPE_INPUTS",
            "amount_low": str(_decimal(total.get("consumed_amount_low_mg"), "compound total low")),
            "amount_high": str(_decimal(total.get("consumed_amount_high_mg"), "compound total high")),
            "supporting_evidence": [source for row in interval_sources for source in row.get("supporting_evidence", [])],
            "missing_uncertainty_reasons": list(unique_reasons.values()),
            "limitations": ["The compound interval inherits Phase 2 retention bounds and is conditional on all point-valued recipe inputs."],
        })
    return {
        "output_id": str(output.get("recipe_id", output.get("meal_id", ""))),
        "record_type": "meal" if "component_results" in output else "recipe",
        "estimate_count": len(classified),
        "status_counts": counts,
        "estimates": classified,
        "compound_totals": compound_summaries,
        "interpretation": "Phase 3 estimate bounds are retained only where source-supported; missing uncertainty remains explicit.",
    }


_COVERAGE_INPUTS = (
    ("food_concentration", "food_concentration"),
    ("analytical_variability", "analytical_variability"),
    ("ingredient_quantity", "ingredient_quantity"),
    ("cooked_quantity", "cooked_quantity"),
    ("cooking_yield", "cooking_yield"),
    ("serving_size", "serving_size"),
    ("serving_fraction", "serving_fraction"),
    ("consumed_fraction", "consumed_fraction"),
    ("serving_count", "serving_count"),
)


def _coverage_record(estimate: dict[str, Any], *, reason: str = "", source_reference: str = "", evidence_id: str = "") -> dict[str, Any]:
    """Retain record identity and source locators alongside each gap."""
    provenance = estimate.get("provenance") if isinstance(estimate.get("provenance"), dict) else {}
    record: dict[str, Any] = {
        "estimate_id": str(estimate.get("estimate_id", "")),
        "compound_id": str(estimate.get("compound_id", "")),
        "ingredient_id": str(estimate.get("ingredient_id", "")),
        "food_record_id": str(estimate.get("food_record_id", "")),
        "input_source_ids": [str(value) for value in estimate.get("input_source_ids", []) if value],
        "food_source_title": str(provenance.get("food_source_title", "")),
        "food_source_url": str(provenance.get("food_source_url", "")),
        "food_doi": str(provenance.get("food_doi", "")),
    }
    if reason:
        record["reason"] = reason
    if source_reference:
        record["source_reference"] = source_reference
    if evidence_id:
        record["evidence_id"] = evidence_id
    return record


def assess_phase3_uncertainty_coverage(output: dict[str, Any]) -> dict[str, Any]:
    """Report uncertainty-input coverage without treating points as known bounds.

    Structured factor bounds, when present, live under each ingredient's
    `provenance.uncertainty_inputs` mapping and must pass the same provenance
    checks as interval propagation. Cooking retention is assessed from the
    existing Phase 2 evidence path. Recipe/meal totals are reported separately.
    """
    summary = assess_phase3_output_uncertainty(output)
    results = output.get("ingredient_results")
    if results is None and isinstance(output.get("component_results"), list):
        results = [row for component in output["component_results"]
                   if isinstance(component, dict)
                   for row in component.get("ingredient_results", [])]
    if not isinstance(results, list):
        raise ValidationError("output does not contain Phase 3 ingredient_results")

    dimensions: list[dict[str, Any]] = []
    for public_name, metadata_name in _COVERAGE_INPUTS:
        supported: list[dict[str, str]] = []
        missing: list[dict[str, str]] = []
        invalid: list[dict[str, str]] = []
        not_applicable: list[dict[str, str]] = []
        for estimate in results:
            estimate_id = str(estimate.get("estimate_id", ""))
            provenance = estimate.get("provenance") if isinstance(estimate, dict) else None
            state = str(provenance.get("ingredient_state", "")).strip().casefold() if isinstance(provenance, dict) else ""
            if public_name == "cooked_quantity" and state == "raw":
                not_applicable.append(_coverage_record(estimate,
                                       reason="Raw-reference estimate has no cooked quantity input."))
                continue
            inputs = provenance.get("uncertainty_inputs") if isinstance(provenance, dict) else None
            factor = inputs.get(metadata_name) if isinstance(inputs, dict) else None
            if factor is None:
                missing.append(_coverage_record(estimate,
                                reason=f"No structured {public_name} interval is present; the reported point input is not treated as exact."))
                continue
            try:
                _factor_interval(factor)
            except ValidationError as exc:
                invalid.append(_coverage_record(estimate, reason=str(exc)))
                continue
            supported.append(_coverage_record(estimate,
                              source_reference=str(factor["bounds"]["source_reference"])))
        state = ("INVALID_METADATA" if invalid else "PARTIAL" if supported and missing
                 else "AVAILABLE" if supported else "NOT_APPLICABLE" if not_applicable and not missing
                 else "MISSING")
        dimensions.append({"dimension": public_name, "coverage_status": state,
                           "total_estimates": len(results), "supported_count": len(supported),
                           "missing_count": len(missing), "invalid_count": len(invalid),
                           "not_applicable_count": len(not_applicable), "supported_records": supported,
                           "missing_records": missing, "invalid_records": invalid})

    retention_supported: list[dict[str, str]] = []
    retention_missing: list[dict[str, str]] = []
    retention_na: list[dict[str, str]] = []
    for estimate in results:
        estimate_id = str(estimate.get("estimate_id", ""))
        provenance = estimate.get("provenance") if isinstance(estimate, dict) else None
        state = str(provenance.get("ingredient_state", "")).strip().casefold() if isinstance(provenance, dict) else ""
        cooked_status = str(estimate.get("cooked_exposure_status", "")).strip() if isinstance(estimate, dict) else ""
        classification = next((row for row in summary["estimates"]
                               if row.get("estimate_id") == estimate_id), {})
        if cooked_status == "RAW_FOOD_NO_COOKING_ADJUSTMENT" or state == "raw":
            retention_na.append(_coverage_record(estimate, reason="No cooking adjustment applies to this raw-food result."))
        elif classification.get("uncertainty_status") == "BOUNDED_INTERVAL_CONDITIONAL_ON_RECIPE_INPUTS":
            evidence = (classification.get("supporting_evidence") or [{}])[0]
            retention_supported.append(_coverage_record(estimate,
                                        source_reference=str(evidence.get("source_reference", "")),
                                        evidence_id=str(evidence.get("evidence_id", ""))))
        else:
            retention_missing.append(_coverage_record(estimate,
                                      reason="No accepted, source-linked compatible cooking-retention interval supports this prepared/cooked estimate."))
    retention_state = "PARTIAL" if retention_supported and retention_missing else "AVAILABLE" if retention_supported else "NOT_APPLICABLE" if retention_na and not retention_missing else "MISSING"
    dimensions.append({"dimension": "cooking_retention", "coverage_status": retention_state,
                       "total_estimates": len(results), "supported_count": len(retention_supported),
                       "missing_count": len(retention_missing), "invalid_count": 0,
                       "not_applicable_count": len(retention_na), "supported_records": retention_supported,
                       "missing_records": retention_missing, "invalid_records": []})

    output_provenance = output.get("provenance") if isinstance(output.get("provenance"), dict) else {}
    for dimension, parent_key, input_key in (
        ("recipe_level", "recipe_provenance", "recipe_level"),
        ("meal_aggregation", "meal_provenance", "meal_aggregation"),
    ):
        parent = output_provenance.get(parent_key)
        inputs = parent.get("uncertainty_inputs") if isinstance(parent, dict) else None
        factor = inputs.get(input_key) if isinstance(inputs, dict) else None
        supported: list[dict[str, str]] = []
        missing: list[dict[str, str]] = []
        invalid: list[dict[str, str]] = []
        if parent is None:
            continue
        output_id = str(output.get("recipe_id", output.get("meal_id", "")))
        if factor is None:
            missing.append({"estimate_id": output_id,
                            "reason": f"No structured {dimension} interval is present; the aggregation input is not treated as exact."})
        else:
            try:
                _factor_interval(factor)
                supported.append({"estimate_id": output_id,
                                  "source_reference": str(factor["bounds"]["source_reference"])})
            except ValidationError as exc:
                invalid.append({"estimate_id": output_id, "reason": str(exc)})
        status = "INVALID_METADATA" if invalid else "AVAILABLE" if supported else "MISSING"
        dimensions.append({"dimension": dimension, "coverage_status": status,
                           "total_estimates": 1, "supported_count": len(supported),
                           "missing_count": len(missing), "invalid_count": len(invalid),
                           "not_applicable_count": 0, "supported_records": supported,
                           "missing_records": missing, "invalid_records": invalid})

    structured_assessments: dict[str, dict[str, Any]] = {}
    for estimate in results:
        estimate_id = str(estimate.get("estimate_id", ""))
        try:
            structured_assessments[estimate_id] = assess_phase3_structured_input_uncertainty(estimate)
        except ValidationError as exc:
            structured_assessments[estimate_id] = {"uncertainty_status": "INVALID_METADATA", "error": str(exc)}

    total_statuses: dict[str, int] = {}
    summary_totals = {str(row.get("compound_id", "")): row for row in summary.get("compound_totals", [])}
    totals = output.get("compound_totals", [])
    for total in totals:
        summary_total = summary_totals.get(str(total.get("compound_id", "")), {})
        status = str(summary_total.get("uncertainty_status", "NOT_QUANTIFIABLE"))
        if total.get("calculation_status") == "Complete" and total.get("estimate_type") == "point":
            identifiers = [str(value) for value in total.get("input_estimate_ids", [])]
            component_assessments = [structured_assessments.get(value, {}) for value in identifiers]
            component_statuses = [row.get("uncertainty_status", "NOT_QUANTIFIABLE") for row in component_assessments]
            bounded_statuses_for_inputs = {"BOUNDED_INTERVAL", "SCENARIO_ENVELOPE"}
            if component_assessments and all(value in bounded_statuses_for_inputs for value in component_statuses):
                status = "SCENARIO_ENVELOPE" if "SCENARIO_ENVELOPE" in component_statuses else "BOUNDED_INTERVAL"
            elif any(value in bounded_statuses_for_inputs or value == "PARTIALLY_QUANTIFIABLE" for value in component_statuses):
                status = "PARTIALLY_QUANTIFIABLE"
            elif any(value == "INVALID_METADATA" for value in component_statuses):
                status = "INVALID_METADATA"
            else:
                status = "POINT_ESTIMATE_ONLY"
        total_statuses[status] = total_statuses.get(status, 0) + 1
    bounded_statuses = {"BOUNDED_INTERVAL", "BOUNDED_INTERVAL_CONDITIONAL_ON_RECIPE_INPUTS", "SCENARIO_ENVELOPE"}
    bounded_count = sum(count for status, count in total_statuses.items() if status in bounded_statuses)
    partial_count = total_statuses.get("PARTIALLY_QUANTIFIABLE", 0)
    aggregate_state = "NOT_AVAILABLE" if not totals else "PARTIAL" if (bounded_count or partial_count) and bounded_count < len(totals) else "AVAILABLE" if bounded_count == len(totals) else "POINT_OR_MISSING_ONLY"
    return {
        "schema_version": "1.0.0",
        "output_id": summary["output_id"],
        "record_type": summary["record_type"],
        "ingredient_estimate_count": len(results),
        "dimensions": dimensions,
        "aggregate_coverage": {
            "level": summary["record_type"],
            "status": aggregate_state,
            "compound_total_count": len(totals),
            "bounded_total_count": bounded_count,
            "status_counts": total_statuses,
        },
        "limitations": [
            "Point-valued inputs are counted as missing uncertainty, not as exact measurements or zero-width bounds.",
            "Coverage reports presence and structural validity of provenance; they do not authenticate cited sources.",
            "Retention bounds do not include analytical, quantity, serving, or consumed-fraction uncertainty unless those intervals are explicitly supplied.",
            "Recipe-level and meal-aggregation bounds are inventoried but are not numerically applied without a validated aggregation-factor contract.",
            "Cooking-yield and analytical-variability bounds are coverage-only pending a validated source-specific propagation contract.",
            "Intervals and point estimates are reported distinctly; no probability distribution is inferred.",
        ],
    }


def build_uncertainty_gap_registry(outputs: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate source-linked missingness across supplied recipe/meal outputs."""
    if not isinstance(outputs, list):
        raise ValidationError("outputs must be a list of Phase 3 recipe/meal outputs")
    output_ids: set[str] = set()
    dimensions: dict[str, dict[str, Any]] = {}
    output_summaries: list[dict[str, Any]] = []
    for index, output in enumerate(outputs):
        if not isinstance(output, dict):
            raise ValidationError(f"outputs[{index}] must be an object")
        coverage = assess_phase3_uncertainty_coverage(output)
        output_id = str(coverage.get("output_id", ""))
        if not output_id:
            raise ValidationError(f"outputs[{index}] has no recipe_id or meal_id")
        if output_id in output_ids:
            raise ValidationError(f"duplicate output_id in uncertainty gap registry: {output_id}")
        output_ids.add(output_id)
        output_summaries.append({"output_id": output_id, "record_type": coverage["record_type"],
                                 "ingredient_estimate_count": coverage["ingredient_estimate_count"],
                                 "aggregate_coverage": coverage["aggregate_coverage"]})
        for row in coverage["dimensions"]:
            dimension = str(row["dimension"])
            target = dimensions.setdefault(dimension, {
                "dimension": dimension, "total_estimates": 0, "supported_count": 0,
                "missing_count": 0, "invalid_count": 0, "not_applicable_count": 0,
                "coverage_by_output": [], "gaps": [],
            })
            target["total_estimates"] += int(row["total_estimates"])
            for count_key in ("supported_count", "missing_count", "invalid_count", "not_applicable_count"):
                target[count_key] += int(row[count_key])
            target["coverage_by_output"].append({"output_id": output_id,
                                                  "record_type": coverage["record_type"],
                                                  "coverage_status": row["coverage_status"]})
            for status_key, records_key in (("MISSING", "missing_records"), ("INVALID_METADATA", "invalid_records")):
                for record in row[records_key]:
                    target["gaps"].append({"output_id": output_id, "record_type": coverage["record_type"],
                                           "gap_status": status_key, **record})
    dimension_rows = []
    for name in sorted(dimensions):
        row = dimensions[name]
        row["coverage_status"] = ("INVALID_METADATA" if row["invalid_count"] else
                                  "PARTIAL" if row["supported_count"] and row["missing_count"] else
                                  "AVAILABLE" if row["supported_count"] else
                                  "NOT_APPLICABLE" if row["not_applicable_count"] and not row["missing_count"] else "MISSING")
        dimension_rows.append(row)
    return {
        "schema_version": "1.0.0",
        "output_count": len(output_summaries),
        "outputs": output_summaries,
        "dimension_count": len(dimension_rows),
        "dimensions": dimension_rows,
        "uncertainty_representation": {
            "point_estimates": "retained as points; never treated as exact zero-width intervals",
            "interval_bounds": "deterministic source-bounded endpoints only",
            "probability_distributions_assumed": False,
        },
        "limitations": [
            "The registry summarizes only the supplied Phase 3 outputs; it does not imply catalog-wide source review.",
            "Source locators identify provenance supplied by the calculation and are not independently authenticated here.",
            "Cooking-yield and analytical-variability dimensions are tracked but are not numerically propagated.",
            "No missing input was replaced with zero, a default range, or a negative finding.",
        ],
    }


def rank_multi_compound_interval_sensitivity(
    assessments: list[dict[str, Any]], *, output_id: str = ""
) -> dict[str, Any]:
    """Return separate additive interval sensitivity reports for each compound."""
    if not isinstance(assessments, list) or not assessments:
        raise ValidationError("assessments must be a nonempty list")
    grouped: dict[str, list[dict[str, Any]]] = {}
    for index, row in enumerate(assessments):
        if not isinstance(row, dict):
            raise ValidationError(f"assessments[{index}] must be an object")
        compound_id = str(row.get("compound_id", "")).strip()
        if not compound_id:
            raise ValidationError(f"assessments[{index}] lacks compound_id; sensitivity aggregation is unsafe")
        grouped.setdefault(compound_id, []).append(row)
    return {
        "schema_version": "1.0.0",
        "output_id": output_id,
        "compound_reports": [
            {"compound_id": compound_id,
             "analysis": rank_additive_interval_sensitivity(rows, output_id=output_id)}
            for compound_id, rows in sorted(grouped.items())
        ],
        "limitations": [
            "Contributors are aggregated only within the same explicit compound identifier.",
            "Ranked interval widths are deterministic endpoint widths, not probabilities or variance contributions.",
        ],
    }


def rank_additive_interval_sensitivity(
    contributors: list[dict[str, Any]], *, output_id: str = "", unit: str = "mg"
) -> dict[str, Any]:
    """Rank supported ingredient interval widths in a recipe/meal sum.

    Missing component uncertainty is never given zero width. If any contributor
    lacks a supported interval, overall amount bounds are withheld; the returned
    ranking is explicitly limited to the supported subset.
    """
    if not isinstance(contributors, list) or not contributors:
        raise ValidationError("contributors must be a nonempty list")
    if not str(unit).strip():
        raise ValidationError("unit is required")
    compound_ids = {str(row.get("compound_id", "")).strip() for row in contributors
                    if isinstance(row, dict)}
    if "" in compound_ids:
        raise ValidationError("every contributor requires compound_id before aggregation")
    if len(compound_ids) > 1:
        raise ValidationError("contributors from different compounds cannot be added in one sensitivity total")
    interval_statuses = {"BOUNDED_INTERVAL", "BOUNDED_INTERVAL_CONDITIONAL_ON_RECIPE_INPUTS", "SCENARIO_ENVELOPE"}
    supported: list[dict[str, Any]] = []
    unavailable: list[dict[str, Any]] = []
    for index, contributor in enumerate(contributors):
        if not isinstance(contributor, dict):
            raise ValidationError(f"contributors[{index}] must be an uncertainty assessment object")
        estimate_id = str(contributor.get("estimate_id", ""))
        estimate_unit = str(contributor.get("unit", ""))
        if estimate_unit and estimate_unit != unit:
            raise ValidationError(f"contributors[{index}] unit {estimate_unit!r} does not match result unit {unit!r}")
        status = str(contributor.get("uncertainty_status", "NOT_QUANTIFIABLE"))
        if status not in interval_statuses:
            unavailable.append({"estimate_id": estimate_id, "uncertainty_status": status,
                                "missing_uncertainty_reasons": contributor.get("missing_uncertainty_reasons", [])})
            continue
        low = _decimal(contributor.get("amount_low"), f"contributors[{index}].amount_low")
        high = _decimal(contributor.get("amount_high"), f"contributors[{index}].amount_high")
        if low > high:
            raise ValidationError(f"contributors[{index}] amount bounds are reversed")
        supported.append({"estimate_id": estimate_id, "low": low, "high": high,
                          "width": high - low, "uncertainty_status": status,
                          "supporting_evidence": contributor.get("supporting_evidence", [])})

    supported_width = sum((row["width"] for row in supported), Decimal(0))
    ranked = sorted(supported, key=lambda row: (-row["width"], row["estimate_id"]))
    results = []
    for rank, row in enumerate(ranked, start=1):
        results.append({"rank": rank, "estimate_id": row["estimate_id"],
                        "uncertainty_status": row["uncertainty_status"],
                        "interval_width": str(row["width"]), "unit": unit,
                        "share_of_supported_width": str(row["width"] / supported_width) if supported_width else "0",
                        "supporting_evidence": row["supporting_evidence"]})
    complete = len(supported) == len(contributors)
    all_conditional = all(row["uncertainty_status"] == "BOUNDED_INTERVAL_CONDITIONAL_ON_RECIPE_INPUTS" for row in supported)
    status = "NO_SUPPORTED_INTERVALS" if not supported else "PARTIAL_INTERVAL_SENSITIVITY_ONLY" if not complete else "COMPLETE_CONDITIONAL_INTERVAL_SENSITIVITY" if all_conditional else "COMPLETE_INTERVAL_SENSITIVITY"
    return {
        "output_id": output_id,
        "status": status,
        "method": "additive endpoint width by contributor; rank by high-minus-low width; no probability or variance decomposition",
        "probabilistic": False,
        "aggregate_interval_complete": complete,
        "amount_low": str(sum((row["low"] for row in supported), Decimal(0))) if complete else "",
        "amount_high": str(sum((row["high"] for row in supported), Decimal(0))) if complete else "",
        "unit": unit,
        "supported_contributor_count": len(supported),
        "unavailable_contributors": unavailable,
        "ranked_contributors": results,
        "limitations": [
            "A ranked width only describes supplied intervals and is not a variance contribution or probability.",
            "Overall additive bounds are withheld when any contributor lacks supported uncertainty bounds.",
        ],
    }


def rank_interval_sensitivity(
    factors: list[dict[str, Any]], *, result_unit: str, estimate_id: str = ""
) -> dict[str, Any]:
    """Return deterministic one-factor-at-a-time impact widths.

    All factors require explicit bounds. This is interval sensitivity analysis,
    not a probabilistic variance decomposition.
    """
    if not factors:
        raise ValidationError("factors must be a nonempty list")
    parsed = [_factor_interval(factor) for factor in factors]
    points = [row[0] for row in parsed]
    impacts = []
    for index, (_, low, high, metadata) in enumerate(parsed):
        other_product = Decimal(1)
        for other_index, point in enumerate(points):
            if other_index != index:
                other_product *= point
        low_effect = other_product * low
        high_effect = other_product * high
        impacts.append({
            "factor": metadata["name"],
            "low_effect": str(low_effect),
            "high_effect": str(high_effect),
            "impact_width": str(high_effect - low_effect),
            "unit": result_unit,
            "source_reference": metadata["source_reference"],
            "source_type": metadata["source_type"],
        })
    impacts.sort(key=lambda row: Decimal(row["impact_width"]), reverse=True)
    return {
        "estimate_id": estimate_id,
        "status": "INTERVAL_SENSITIVITY_ONLY",
        "method": "one-factor-at-a-time bounds; other factors held at reported point values",
        "probabilistic": False,
        "results": impacts,
        "limitations": ["Ranking depends on supplied bounds and does not represent variance contribution or probability."],
    }
