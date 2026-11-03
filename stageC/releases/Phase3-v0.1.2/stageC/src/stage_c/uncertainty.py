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


_ALLOWED_BOUND_TYPES = {"reported_interval", "measured_interval", "derived_interval", "assumed_scenario"}
_SUPPORTED_SOURCES = {"reported", "measured", "derived", "assumed"}


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
    expected_source = {
        "reported_interval": "reported",
        "measured_interval": "measured",
        "derived_interval": "derived",
        "assumed_scenario": "assumed",
    }[bound_type]
    if source_type != expected_source:
        raise ValidationError(f"{name}: {bound_type} requires source_type={expected_source!r}")
    reference = str(bounds.get("source_reference", "")).strip()
    if not reference:
        raise ValidationError(f"{name}.bounds.source_reference is required")
    method = str(bounds.get("method", "")).strip()
    if source_type == "derived" and not method:
        raise ValidationError(f"{name}.bounds.method is required for derived bounds")
    metadata = {
        "name": name,
        "unit": unit,
        "type": bound_type,
        "source_type": source_type,
        "source_reference": reference,
        "method": method,
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
    known: list[dict[str, Any]] = []
    for i, factor in enumerate(factors):
        if not isinstance(factor, dict) or not str(factor.get("name", "")).strip():
            raise ValidationError(f"factors[{i}] requires a name")
        if "value" not in factor:
            raise ValidationError(f"factors[{i}].value is required")
        _decimal(factor["value"], f"{factor['name']}.value")
        if factor.get("bounds") is None:
            missing.append(str(factor["name"]))
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
        "distribution_assumed": False,
        "correlation_assumed": False,
        "basis": "Phase 3 ingredient result; uncertainty in unreported inputs is not quantified",
    }
    if estimate.get("calculation_status") != "Complete":
        return {
            **common,
            "uncertainty_status": "NOT_QUANTIFIABLE",
            "amount_low": "",
            "amount_high": "",
            "unit": "mg",
            "missing_uncertainty_factors": ["incomplete Phase 3 estimate"],
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
        "limitations": [
            "The interval reflects retention bounds only, conditional on reported food concentration, cooked quantity, serving fraction, and consumed fraction.",
            "No analytical, quantity-measurement, or fraction uncertainty was inferred.",
            "No probability distribution, confidence level, or correlation assumption was used.",
        ],
    }


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
                "uncertainty_status": "NOT_QUANTIFIABLE", "amount_low": "", "amount_high": "", "unit": "mg"}
        if total.get("calculation_status") != "Complete":
            compound_summaries.append({**base, "missing_uncertainty_factors": ["incomplete Phase 3 compound total"]})
            continue
        if total.get("estimate_type") == "point":
            point_low = _decimal(total.get("consumed_amount_low_mg"), "compound total low")
            point_high = _decimal(total.get("consumed_amount_high_mg"), "compound total high")
            if point_low != point_high:
                raise ValidationError("Phase 3 point compound total must have equal low and high values")
            compound_summaries.append({**base, "uncertainty_status": "POINT_ESTIMATE_ONLY",
                                       "point_amount": str(point_low),
                                       "missing_uncertainty_factors": ["component measurement uncertainty"]})
            continue
        if total.get("estimate_type") != "interval":
            raise ValidationError(f"unsupported Phase 3 compound total estimate_type: {total.get('estimate_type')!r}")
        interval_sources = [row for row in references if row.get("uncertainty_status") == "BOUNDED_INTERVAL_CONDITIONAL_ON_RECIPE_INPUTS"]
        if not interval_sources:
            raise ValidationError("Phase 3 interval compound total has no source-supported interval component")
        compound_summaries.append({
            **base,
            "uncertainty_status": "BOUNDED_INTERVAL_CONDITIONAL_ON_RECIPE_INPUTS",
            "amount_low": str(_decimal(total.get("consumed_amount_low_mg"), "compound total low")),
            "amount_high": str(_decimal(total.get("consumed_amount_high_mg"), "compound total high")),
            "supporting_evidence": [source for row in interval_sources for source in row.get("supporting_evidence", [])],
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
