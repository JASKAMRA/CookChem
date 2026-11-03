"""Conservative adapter and calculation gates for supplied Stage A predictions.

The frozen Stage A code is never imported or executed here. Predictions are
accepted only as externally supplied, provenance-complete records and remain
blocked until scientific review and explicit compatibility checks pass.
"""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping


SEMANTICS = {
    "apparent_concentration_ratio",
    "concentration_retention",
    "total_mass_retention",
    "model_predicted_retention",
    "measured_retention",
}
GATES = (
    "compound_identity_match",
    "food_identity_match",
    "food_matrix_match",
    "food_state_match",
    "cooking_method_match",
    "cooking_conditions_match",
    "measurement_basis_compatible",
    "denominator_compatible",
)
HEX64 = re.compile(r"^[0-9a-f]{64}$")
MASS_UNITS = {"kg", "g", "mg", "ug", "µg", "μg", "ng"}
VOLUME_UNITS = {"l", "liter", "litre", "ml", "milliliter", "millilitre"}
STAGE_A_INPUT_SHA256 = "cd51de3286d9fea7c4d87ce45f4c9c4301214b1944f72bff19c3b41ce0358c27"
STAGE_A_RUNNER_SHA256 = "a2de32f24600d18df6a503aba001ce4484295f0802b2ba7d09bbaa6bfc704d0c"
# Read-only audit found no serialized model artifact or approved artifact hash.
STAGE_A_MODEL_ARTIFACT_SHA256: str | None = None


class CookingIntegrationError(ValueError):
    """Raised when supplied prediction metadata violate the handoff contract."""


def _finite_decimal(value: Any, label: str) -> Decimal:
    if isinstance(value, bool):
        raise CookingIntegrationError(f"{label} must be a finite decimal")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise CookingIntegrationError(f"{label} must be a finite decimal") from None
    if not result.is_finite():
        raise CookingIntegrationError(f"{label} must be a finite decimal")
    return result


def _measured_quantity(value: Any, label: str) -> tuple[Decimal, str]:
    if not isinstance(value, Mapping) or value.get("status") != "measured":
        raise CookingIntegrationError(f"{label} must be an explicit measured value")
    unit = value.get("unit")
    source = value.get("source_reference")
    if not isinstance(unit, str) or not unit.strip() or not isinstance(source, str) or not source.strip():
        raise CookingIntegrationError(f"{label} requires an explicit unit and source_reference")
    quantity = _finite_decimal(value.get("value"), f"{label}.value")
    if quantity < 0:
        raise CookingIntegrationError(f"{label} must be nonnegative")
    return quantity, unit.strip()


def _concentration_denominator(unit: str) -> str | None:
    normalized = "".join(unit.casefold().split()).replace("μg", "ug").replace("µg", "ug")
    if any(normalized.endswith(suffix) for suffix in ("/kg", "/g", "/100g")):
        return "mass"
    if any(normalized.endswith(suffix) for suffix in ("/l", "/ml", "/100ml")):
        return "volume"
    return None


def validate_prediction_record(record: Mapping[str, Any]) -> None:
    """Validate structure and provenance for a caller-supplied output record."""
    if not isinstance(record, Mapping):
        raise CookingIntegrationError("prediction record must be an object")
    required = {
        "schema_version", "prediction_id", "food_record_id", "compound_id", "food_matrix",
        "food_state", "cooking_conditions", "measurement_basis", "denominator",
        "prediction", "provenance", "scientific_review",
    }
    missing = sorted(required - set(record))
    if missing:
        raise CookingIntegrationError("missing required fields: " + ", ".join(missing))
    if record.get("schema_version") != "1.0.0":
        raise CookingIntegrationError("unsupported Stage A prediction contract version")
    for key in ("prediction_id", "food_record_id", "compound_id", "food_matrix", "food_state", "measurement_basis", "denominator"):
        if not isinstance(record.get(key), str) or not record[key].strip():
            raise CookingIntegrationError(f"{key} must be a nonempty string")
    conditions = record.get("cooking_conditions")
    if not isinstance(conditions, Mapping):
        raise CookingIntegrationError("cooking_conditions must be an object")
    if not isinstance(conditions.get("cooking_method"), str) or not conditions["cooking_method"].strip():
        raise CookingIntegrationError("cooking_conditions.cooking_method is required")
    for key in ("temperature_c", "duration_min", "pressure_kpa", "microwave_power_w"):
        if conditions.get(key) not in (None, ""):
            value = _finite_decimal(conditions[key], f"cooking_conditions.{key}")
            if key in {"duration_min", "pressure_kpa", "microwave_power_w"} and value < 0:
                raise CookingIntegrationError(f"cooking_conditions.{key} must be nonnegative")

    prediction = record.get("prediction")
    if not isinstance(prediction, Mapping):
        raise CookingIntegrationError("prediction must be an object")
    if prediction.get("semantic_type") not in SEMANTICS:
        raise CookingIntegrationError("prediction.semantic_type is unsupported or ambiguous")
    value = _finite_decimal(prediction.get("value"), "prediction.value")
    if value < 0:
        raise CookingIntegrationError("prediction.value must be nonnegative")
    if prediction.get("unit") not in {"percent", "fraction", "ratio"}:
        raise CookingIntegrationError("prediction.unit must be percent, fraction, or ratio")
    if prediction["semantic_type"] == "apparent_concentration_ratio" and prediction["unit"] not in {"fraction", "ratio"}:
        raise CookingIntegrationError("apparent concentration ratios require a ratio unit")
    if prediction["semantic_type"] != "apparent_concentration_ratio" and prediction["unit"] == "ratio":
        raise CookingIntegrationError("retention values require percent or fraction units")
    if prediction["semantic_type"] in {"model_predicted_retention", "measured_retention"}:
        basis = prediction.get("underlying_retention_semantics")
        if basis not in {None, "concentration_retention", "total_mass_retention"}:
            raise CookingIntegrationError("underlying_retention_semantics must be concentration_retention or total_mass_retention")

    provenance = record.get("provenance")
    if not isinstance(provenance, Mapping):
        raise CookingIntegrationError("provenance must be an object")
    if provenance.get("origin") not in {"mocked_fixture", "supplied_prediction", "measured_source_record"}:
        raise CookingIntegrationError("provenance.origin must explicitly identify mocked, supplied prediction, or measured source record")
    if provenance.get("origin") == "supplied_prediction" and prediction["semantic_type"] != "model_predicted_retention":
        raise CookingIntegrationError("supplied_prediction records must be labeled model_predicted_retention")
    if provenance.get("origin") == "measured_source_record" and prediction["semantic_type"] not in {"apparent_concentration_ratio", "concentration_retention", "total_mass_retention", "measured_retention"}:
        raise CookingIntegrationError("measured source records cannot be labeled as model predictions")
    if not isinstance(provenance.get("source_reference"), str) or not provenance["source_reference"].strip():
        raise CookingIntegrationError("provenance.source_reference is required")
    if provenance["origin"] == "supplied_prediction":
        for key in ("stage_a_input_sha256", "stage_a_code_sha256", "model_artifact_sha256", "output_sha256"):
            if not isinstance(provenance.get(key), str) or not HEX64.fullmatch(provenance[key].lower()):
                raise CookingIntegrationError(f"supplied Stage A prediction requires a valid {key}")
        if not isinstance(provenance.get("python_version"), str) or not provenance["python_version"].strip():
            raise CookingIntegrationError("supplied Stage A prediction requires python_version")
        if not isinstance(provenance.get("package_versions"), Mapping) or not provenance["package_versions"]:
            raise CookingIntegrationError("supplied Stage A prediction requires package_versions")
        if not isinstance(provenance.get("model_name"), str) or not provenance["model_name"].strip():
            raise CookingIntegrationError("supplied Stage A prediction requires model_name")
        if provenance["stage_a_input_sha256"].lower() != STAGE_A_INPUT_SHA256:
            raise CookingIntegrationError("supplied Stage A input hash does not match the inspected frozen input")
        if provenance["stage_a_code_sha256"].lower() != STAGE_A_RUNNER_SHA256:
            raise CookingIntegrationError("supplied Stage A code hash does not match the inspected frozen runner")
        if provenance["model_name"] != "XGBoost_tuned":
            raise CookingIntegrationError("only the documented selected Stage A model name is eligible for review")

    review = record.get("scientific_review")
    if not isinstance(review, Mapping) or review.get("status") not in {"pending", "approved", "rejected"}:
        raise CookingIntegrationError("scientific_review.status must be pending, approved, or rejected")
    if review.get("status") == "approved":
        if not isinstance(review.get("reviewer"), str) or not review["reviewer"].strip():
            raise CookingIntegrationError("approved prediction requires a named scientific reviewer")
        if not isinstance(review.get("review_reference"), str) or not review["review_reference"].strip():
            raise CookingIntegrationError("approved prediction requires a review reference")


def adapt_stage_a_output(record: Mapping[str, Any], compatibility: Mapping[str, bool | None]) -> dict[str, Any]:
    """Return a normalized, still review-gated view of a supplied record.

    Compatibility values must be explicit True/False/None decisions supplied
    by an upstream reviewer; this function does not infer chemical equivalence.
    """
    validate_prediction_record(record)
    if not isinstance(compatibility, Mapping) or set(compatibility) != set(GATES):
        missing = sorted(set(GATES) - set(compatibility)) if isinstance(compatibility, Mapping) else list(GATES)
        extra = sorted(set(compatibility) - set(GATES)) if isinstance(compatibility, Mapping) else []
        raise CookingIntegrationError(f"compatibility gate mismatch; missing={missing}, extra={extra}")
    for key, status in compatibility.items():
        if status is not None and type(status) is not bool:
            raise CookingIntegrationError(f"compatibility gate {key} must be true, false, or null")

    failed = [key for key, status in compatibility.items() if status is False]
    pending = [key for key, status in compatibility.items() if status is None]
    if failed:
        compatibility_status = "INCOMPATIBLE"
        reasons = [f"failed compatibility gate: {key}" for key in sorted(failed)]
    elif pending:
        compatibility_status = "PENDING_COMPATIBILITY"
        reasons = [f"compatibility data not established: {key}" for key in sorted(pending)]
    else:
        compatibility_status = "COMPATIBLE_PENDING_SCIENTIFIC_REVIEW"
        reasons = []

    origin = record["provenance"]["origin"]
    review_status = record["scientific_review"]["status"]
    if origin == "mocked_fixture":
        reasons.append("synthetic prediction fixture is not a real Stage A output")
    if origin == "supplied_prediction" and STAGE_A_MODEL_ARTIFACT_SHA256 is None:
        reasons.append("no serialized Stage A model artifact/hash is registered in the inspected package")
    semantic_type = record["prediction"]["semantic_type"]
    if semantic_type in {"model_predicted_retention", "measured_retention"} and not record["prediction"].get("underlying_retention_semantics"):
        reasons.append("retention measurement basis is not classified")
    if review_status != "approved":
        reasons.append(f"scientific review status is {review_status}")
    if compatibility_status != "COMPATIBLE_PENDING_SCIENTIFIC_REVIEW":
        reasons.append("compatibility requirements are not all explicitly satisfied")
    return {
        "prediction_id": record["prediction_id"],
        "food_record_id": record["food_record_id"],
        "compound_id": record["compound_id"],
        "prediction": dict(record["prediction"]),
        "cooking_conditions": dict(record["cooking_conditions"]),
        "provenance": dict(record["provenance"]),
        "scientific_review": dict(record["scientific_review"]),
        "compatibility": dict(compatibility),
        "compatibility_status": compatibility_status,
        "eligible_for_estimation": not reasons,
        "missing_data_reasons": reasons,
    }


def calculate_cooked_concentration(
    raw_concentration: Mapping[str, Any],
    record: Mapping[str, Any],
    compatibility: Mapping[str, bool | None],
    *,
    raw_mass: Mapping[str, Any] | None = None,
    cooked_mass: Mapping[str, Any] | None = None,
    raw_volume: Mapping[str, Any] | None = None,
    cooked_volume: Mapping[str, Any] | None = None,
) -> dict[str, str]:
    """Apply only an approved compatible retention with explicit semantics.

    No conversion is made from an apparent concentration ratio. Total-mass
    retention additionally requires measured raw and cooked mass in the same
    unit. Concentration and mass inputs require measured values, units, and
    source references. Model output cannot be applied unless its predicted-
    retention basis is explicitly classified as concentration or total-mass retention.
    """
    adapted = adapt_stage_a_output(record, compatibility)
    if not adapted.get("eligible_for_estimation"):
        return {"status": "INCOMPLETE", "cooked_concentration": "", "reason": "; ".join(adapted.get("missing_data_reasons", [])) or "prediction not eligible"}
    prediction = adapted.get("prediction", {})
    semantic = prediction.get("semantic_type")
    basis = prediction.get("underlying_retention_semantics")
    if semantic == "apparent_concentration_ratio":
        return {"status": "INCOMPLETE", "cooked_concentration": "", "reason": "apparent concentration ratio is not concentration retention or total mass retention"}
    if semantic in {"model_predicted_retention", "measured_retention"}:
        semantic = basis
        if semantic not in {"concentration_retention", "total_mass_retention"}:
            return {"status": "INCOMPLETE", "cooked_concentration": "", "reason": "retention measurement basis is not classified"}
    try:
        concentration, concentration_unit = _measured_quantity(raw_concentration, "raw_concentration")
        value = _finite_decimal(prediction.get("value"), "prediction.value")
        factor = value / Decimal(100) if prediction.get("unit") == "percent" else value
        if factor < 0:
            raise CookingIntegrationError("concentration and retention must be nonnegative")
        if semantic == "concentration_retention":
            cooked = concentration * factor
        elif semantic == "total_mass_retention":
            denominator = _concentration_denominator(concentration_unit)
            if denominator == "mass":
                if raw_mass is None or cooked_mass is None:
                    return {"status": "INCOMPLETE", "cooked_concentration": "", "reason": "mass-based concentration with total mass retention requires measured raw_mass and cooked_mass"}
                raw_amount, raw_unit = _measured_quantity(raw_mass, "raw_mass")
                cooked_amount, cooked_unit = _measured_quantity(cooked_mass, "cooked_mass")
            elif denominator == "volume":
                if raw_volume is None or cooked_volume is None:
                    return {"status": "INCOMPLETE", "cooked_concentration": "", "reason": "volume-based concentration with total mass retention requires measured raw_volume and cooked_volume"}
                raw_amount, raw_unit = _measured_quantity(raw_volume, "raw_volume")
                cooked_amount, cooked_unit = _measured_quantity(cooked_volume, "cooked_volume")
            else:
                return {"status": "INCOMPLETE", "cooked_concentration": "", "reason": "total mass retention requires a recognized mass- or volume-denominated raw concentration unit"}
            valid_units = MASS_UNITS if denominator == "mass" else VOLUME_UNITS
            raw_unit_key = raw_unit.casefold().replace("μg", "ug").replace("µg", "ug")
            cooked_unit_key = cooked_unit.casefold().replace("μg", "ug").replace("µg", "ug")
            if raw_unit_key not in valid_units or cooked_unit_key not in valid_units:
                return {"status": "INCOMPLETE", "cooked_concentration": "", "reason": f"{denominator} yield units are unsupported"}
            if raw_unit_key != cooked_unit_key:
                return {"status": "INCOMPLETE", "cooked_concentration": "", "reason": f"raw and cooked {denominator} units must match; no unverified conversion is performed"}
            if raw_amount <= 0 or cooked_amount <= 0:
                return {"status": "INCOMPLETE", "cooked_concentration": "", "reason": f"raw and cooked {denominator} must be greater than zero"}
            cooked = concentration * factor * raw_amount / cooked_amount
        else:
            return {"status": "INCOMPLETE", "cooked_concentration": "", "reason": f"unsupported retention semantics: {semantic}"}
        return {"status": "COMPLETE", "cooked_concentration": format(cooked.normalize(), "f"),
                "cooked_concentration_unit": concentration_unit,
                "reason": "approved compatible retention; explicit semantics and measured basis applied"}
    except CookingIntegrationError as exc:
        return {"status": "INCOMPLETE", "cooked_concentration": "", "reason": str(exc)}
