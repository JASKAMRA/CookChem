"""Source-traceable recipe and meal exposure foundations.

This layer reports food-compound exposure only. It does not infer cooked yield,
retention, nutrient loss, bioavailability, or clinical risk.
"""
from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from .compound_mapping import VERIFIED_STATUSES
from .exceptions import ValidationError
from .exposure_engine import COMPLETE, calculate_exposure
from .phase2_retention import PercentInterval, adjust_concentration_interval
from .provenance import deterministic_id
from .unit_conversion import (
    concentration_to_mg_per_kg,
    mass_to_kg,
    volume_concentration_to_mg_per_l,
)

MASS_UNITS = {"kg", "g", "mg", "ug", "µg", "μg", "ng"}
VOLUME_UNITS = {"l", "liter", "litre", "ml", "milliliter", "millilitre"}
VERIFIED_SOURCE_CLASSES = {
    "Primary analytical measurement", "Peer-reviewed secondary source",
    "Authoritative food-composition database", "Verified laboratory measurement",
    "User-supplied measurement",
}
VERIFIED_SOURCE_STATUSES = {"verified", "full-text verified", "database verified", "user verified"}


def _decimal(value: Any, label: str, *, minimum: Decimal = Decimal(0), maximum: Decimal | None = None) -> Decimal:
    if isinstance(value, bool):
        raise ValidationError(f"{label} must be a finite decimal")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValidationError(f"{label} must be a finite decimal") from None
    if not number.is_finite() or number < minimum or (maximum is not None and number > maximum):
        upper = f" and <= {maximum}" if maximum is not None else ""
        raise ValidationError(f"{label} must be finite, >= {minimum}{upper}")
    return number


def _unit_key(unit: str) -> str:
    return " ".join(str(unit).strip().lower().split())


def _is_mass(unit: str) -> bool:
    return _unit_key(unit).replace("μg", "ug").replace("µg", "ug") in MASS_UNITS


def _is_volume(unit: str) -> bool:
    return _unit_key(unit) in VOLUME_UNITS


def _volume_to_l(value: Any, unit: str) -> Decimal:
    number = _decimal(value, "volume")
    key = _unit_key(unit)
    if key in {"l", "liter", "litre"}:
        return number
    if key in {"ml", "milliliter", "millilitre"}:
        return number / Decimal("1000")
    raise ValidationError(f"Unsupported volume unit: {unit!r}")


def _measurement_kg(measurement: dict[str, Any], label: str) -> Decimal:
    if measurement.get("status") != "measured" or measurement.get("value") in (None, "") or not measurement.get("unit"):
        raise ValidationError(f"{label} is not explicitly measured")
    return mass_to_kg(measurement["value"], str(measurement["unit"]))


def _measurement_l(measurement: dict[str, Any], label: str) -> Decimal:
    if measurement.get("status") != "measured" or measurement.get("value") in (None, "") or not measurement.get("unit"):
        raise ValidationError(f"{label} is not explicitly measured")
    return _volume_to_l(measurement["value"], str(measurement["unit"]))


def _measurement_g(measurement: dict[str, Any], label: str) -> Decimal:
    return _measurement_kg(measurement, label) * Decimal("1000")


def _decimal_text(value: Decimal) -> str:
    return format(value.normalize(), "f") if value else "0"


def _measured_g(balance: dict[str, Any], field: str, label: str) -> Decimal | None:
    measurement = balance.get(field, {})
    if not isinstance(measurement, dict) or measurement.get("status") != "measured":
        return None
    return _measurement_g(measurement, label)


def analyze_recipe_mass_balance(recipe: dict[str, Any]) -> dict[str, Any]:
    """Report mass accounting from measurements only; never fill or repair inputs.

    Residuals are shown against their named equations. A positive residual is
    unaccounted measured mass, not an inferred cooking loss or transfer.
    """
    balance = recipe.get("mass_balance", {}) if isinstance(recipe, dict) else {}
    ingredients = recipe.get("ingredients", []) if isinstance(recipe, dict) else []
    measured_raw = [_measured_g(item.get("mass_balance", {}), "raw_mass", f"ingredients[{i}].raw_mass")
                    for i, item in enumerate(ingredients) if isinstance(item, dict)]
    recipe_raw = _measured_g(balance, "raw_mass", "mass_balance.raw_mass")
    ingredient_raw = sum(measured_raw, Decimal(0)) if measured_raw and all(v is not None for v in measured_raw) else None
    raw_value = recipe_raw if recipe_raw is not None else ingredient_raw
    raw_source = "recipe.mass_balance.raw_mass" if recipe_raw is not None else (
        "sum of measured ingredient raw_mass" if ingredient_raw is not None else "not fully reported")

    cooked = _measured_g(balance, "cooked_mass", "mass_balance.cooked_mass")
    batch_yield = _measured_g(balance, "batch_yield", "mass_balance.batch_yield")
    edible = _measured_g(balance, "edible_portion_mass", "mass_balance.edible_portion_mass")
    discarded = _measured_g(balance, "discarded_portion_mass", "mass_balance.discarded_portion_mass")
    serving = _measured_g(balance, "serving_mass", "mass_balance.serving_mass")
    leftovers = _measured_g(balance, "leftovers_mass", "mass_balance.leftovers_mass")
    count = None
    count_record = recipe.get("servings_count", {}) if isinstance(recipe, dict) else {}
    if isinstance(count_record, dict) and count_record.get("status") == "measured":
        count = _decimal(count_record.get("value"), "servings_count.value", minimum=Decimal("0.0000000001"))
    cooked_volume_record = recipe.get("cooked_volume", {"status": "not_reported"}) if isinstance(recipe, dict) else {}
    serving_volume_record = recipe.get("serving_volume", {"status": "not_reported"}) if isinstance(recipe, dict) else {}
    leftovers_volume_record = recipe.get("leftovers_volume", {"status": "not_reported"}) if isinstance(recipe, dict) else {}
    cooked_volume_l = _measurement_l(cooked_volume_record, "cooked_volume") if cooked_volume_record.get("status") == "measured" else None
    serving_volume_l = _measurement_l(serving_volume_record, "serving_volume") if serving_volume_record.get("status") == "measured" else None
    leftovers_volume_l = _measurement_l(leftovers_volume_record, "leftovers_volume") if leftovers_volume_record.get("status") == "measured" else None

    checks: list[dict[str, Any]] = []

    def compare(check_id: str, observed: Decimal | None, expected: Decimal | None, equation: str) -> Decimal | None:
        if observed is None or expected is None:
            checks.append({"check_id": check_id, "status": "INCOMPLETE", "equation": equation,
                           "difference_g": "", "reason": "one or more required measurements were not reported"})
            return None
        difference = observed - expected
        checks.append({"check_id": check_id,
                       "status": "CONSISTENT" if difference == 0 else "INCONSISTENT",
                       "equation": equation, "observed_g": _decimal_text(observed), "expected_g": _decimal_text(expected),
                       "difference_g": _decimal_text(difference),
                       "reason": "measured values agree" if difference == 0 else "measured values do not agree; no value was changed"})
        return difference

    if recipe_raw is not None and ingredient_raw is not None:
        compare("RAW_INPUTS", recipe_raw, ingredient_raw,
                "recipe raw_mass = sum(measured ingredient raw_mass)")
    else:
        checks.append({"check_id": "RAW_INPUTS", "status": "INCOMPLETE",
                       "equation": "recipe raw_mass = sum(measured ingredient raw_mass)",
                       "difference_g": "", "reason": "recipe total or all ingredient raw masses are not reported"})
    if cooked is not None and batch_yield is not None:
        compare("COOKED_OUTPUT_VS_BATCH_YIELD", cooked, batch_yield,
                "cooked_mass = batch_yield")
    else:
        checks.append({"check_id": "COOKED_OUTPUT_VS_BATCH_YIELD", "status": "INCOMPLETE",
                       "equation": "cooked_mass = batch_yield", "difference_g": "",
                       "reason": "cooked mass or batch yield is not reported"})

    portion_residual = None
    if cooked is not None and edible is not None and discarded is not None:
        portion_residual = cooked - edible - discarded
        portion_status = "CONSISTENT" if portion_residual == 0 else (
            "UNACCOUNTED_MASS" if portion_residual > 0 else "INCONSISTENT")
        checks.append({"check_id": "COOKED_PORTION_ALLOCATION", "status": portion_status,
                       "equation": "cooked_mass = edible_portion_mass + discarded_portion_mass",
                       "observed_g": _decimal_text(cooked), "expected_g": _decimal_text(edible + discarded),
                       "difference_g": _decimal_text(portion_residual),
                       "reason": "positive residual is unallocated measured output mass" if portion_residual > 0 else (
                           "measured portions exceed cooked output; no value was changed" if portion_residual < 0 else "measured values agree")})
    else:
        checks.append({"check_id": "COOKED_PORTION_ALLOCATION", "status": "INCOMPLETE",
                       "equation": "cooked_mass = edible_portion_mass + discarded_portion_mass",
                       "difference_g": "", "reason": "cooked, edible, and discarded masses must all be measured"})

    serving_residual = None
    if cooked is not None and serving is not None and count is not None and leftovers is not None:
        allocated = serving * count + leftovers
        serving_residual = cooked - allocated
        serving_status = "CONSISTENT" if serving_residual == 0 else (
            "UNACCOUNTED_MASS" if serving_residual > 0 else "INCONSISTENT")
        checks.append({"check_id": "SERVINGS_AND_LEFTOVERS", "status": serving_status,
                       "equation": "cooked_mass = serving_mass × servings_count + leftovers_mass",
                       "observed_g": _decimal_text(cooked), "expected_g": _decimal_text(allocated),
                       "difference_g": _decimal_text(serving_residual),
                       "reason": "positive residual is unallocated measured output mass" if serving_residual > 0 else (
                           "servings and leftovers exceed cooked output; no value was changed" if serving_residual < 0 else "measured values agree")})
    else:
        checks.append({"check_id": "SERVINGS_AND_LEFTOVERS", "status": "INCOMPLETE",
                       "equation": "cooked_mass = serving_mass × servings_count + leftovers_mass",
                       "difference_g": "", "reason": "cooked mass, serving mass, servings count, and leftovers mass are all required"})

    volume_residual = None
    volume_was_reported = any(record.get("status") == "measured" for record in
                              (cooked_volume_record, serving_volume_record, leftovers_volume_record))
    if volume_was_reported:
        if cooked_volume_l is not None and serving_volume_l is not None and count is not None and leftovers_volume_l is not None:
            allocated_volume = serving_volume_l * count + leftovers_volume_l
            volume_residual = cooked_volume_l - allocated_volume
            volume_status = "CONSISTENT" if volume_residual == 0 else (
                "UNACCOUNTED_VOLUME" if volume_residual > 0 else "INCONSISTENT")
            checks.append({"check_id": "VOLUME_SERVINGS_AND_LEFTOVERS", "status": volume_status,
                           "equation": "cooked_volume = serving_volume × servings_count + leftovers_volume",
                           "observed_l": _decimal_text(cooked_volume_l), "expected_l": _decimal_text(allocated_volume),
                           "difference_l": _decimal_text(volume_residual),
                           "reason": "positive residual is unallocated measured output volume" if volume_residual > 0 else (
                               "serving and leftover volumes exceed cooked output; no value was changed" if volume_residual < 0 else "measured volumes agree")})
        else:
            checks.append({"check_id": "VOLUME_SERVINGS_AND_LEFTOVERS", "status": "INCOMPLETE",
                           "equation": "cooked_volume = serving_volume × servings_count + leftovers_volume",
                           "difference_l": "", "reason": "cooked volume, serving volume, servings count, and leftovers volume are all required"})

    states = {row["status"] for row in checks}
    if "INCONSISTENT" in states:
        status = "INCONSISTENT"
    elif "UNACCOUNTED_MASS" in states or "UNACCOUNTED_VOLUME" in states:
        status = "INCOMPLETE_WITH_UNACCOUNTED_OUTPUT"
    elif "INCOMPLETE" in states:
        status = "INCOMPLETE"
    else:
        status = "CONSISTENT"
    residual = portion_residual if portion_residual is not None else serving_residual
    residual_basis = ("cooked_mass - edible_portion_mass - discarded_portion_mass" if portion_residual is not None else
                      "cooked_mass - serving_mass × servings_count - leftovers_mass" if serving_residual is not None else "")
    return {
        "status": status,
        "raw_ingredient_mass_g": "" if raw_value is None else _decimal_text(raw_value),
        "raw_mass_source": raw_source,
        "cooked_output_mass_g": "" if cooked is None and batch_yield is None else _decimal_text(cooked if cooked is not None else batch_yield),
        "serving_mass_g": "" if serving is None else _decimal_text(serving),
        "servings_count": "" if count is None else _decimal_text(count),
        "leftovers_mass_g": "" if leftovers is None else _decimal_text(leftovers),
        "cooked_output_volume_l": "" if cooked_volume_l is None else _decimal_text(cooked_volume_l),
        "serving_volume_l": "" if serving_volume_l is None else _decimal_text(serving_volume_l),
        "leftovers_volume_l": "" if leftovers_volume_l is None else _decimal_text(leftovers_volume_l),
        "unaccounted_mass_g": "" if residual is None else _decimal_text(residual),
        "unaccounted_mass_basis": residual_basis,
        "unaccounted_volume_l": "" if volume_residual is None else _decimal_text(volume_residual),
        "checks": checks,
        "method": "measured-only mass equations; no raw-to-cooked equivalence, loss, transfer, or missing measurement is inferred",
    }


def _validate_measurement(value: Any, label: str, *, volume: bool = False) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict) or value.get("status") not in {"measured", "not_reported"}:
        return [f"{label} requires a measured or not_reported status object"]
    if value["status"] == "measured":
        unit = str(value.get("unit", ""))
        if not unit or (not _is_volume(unit) if volume else not _is_mass(unit)):
            errors.append(f"{label} has an unsupported or missing {'volume' if volume else 'mass'} unit")
        if not str(value.get("source_reference", "")).strip():
            errors.append(f"{label}.source_reference is required for measured values")
        try:
            _decimal(value.get("value"), label)
        except ValidationError as exc:
            errors.append(str(exc))
    elif value.get("value") not in (None, "") or value.get("unit") not in (None, ""):
        errors.append(f"{label} cannot contain a numeric value when status is not_reported")
    return errors


MASS_BALANCE_FIELDS = (
    "raw_mass", "prepared_mass", "cooked_mass", "edible_portion_mass", "discarded_portion_mass",
    "cooking_liquid_retained_mass", "cooking_liquid_discarded_mass", "cooking_oil_retained_mass",
    "cooking_oil_discarded_mass",
)
RECIPE_MASS_FIELDS = (*MASS_BALANCE_FIELDS, "batch_yield", "serving_mass", "leftovers_mass")


def _validate_mass_balance(balance: Any, label: str, fields: tuple[str, ...]) -> list[str]:
    if not isinstance(balance, dict):
        return [f"{label} must be an explicit mass-balance object"]
    errors = []
    for field in fields:
        errors.extend(_validate_measurement(balance.get(field), f"{label}.{field}"))
    return errors


def _validate_operations(operations: Any, label: str) -> list[str]:
    if not isinstance(operations, list):
        return [f"{label} must be a list"]
    errors = []
    seen: set[str] = set()
    for index, operation in enumerate(operations):
        prefix = f"{label}[{index}]"
        if not isinstance(operation, dict):
            errors.append(f"{prefix} must be an object")
            continue
        raw_op_id = operation.get("operation_id", "")
        op_id = raw_op_id if isinstance(raw_op_id, str) else ""
        if not op_id.strip():
            errors.append(f"{prefix}.operation_id must be a nonempty string")
        elif op_id in seen:
            errors.append(f"{prefix}.operation_id is duplicated")
        seen.add(op_id)
        if not isinstance(operation.get("method"), str) or not operation["method"].strip():
            errors.append(f"{prefix}.method must be a nonempty string")
    return errors


def _validate_ingredient(ingredient: Any, label: str) -> list[str]:
    if not isinstance(ingredient, dict):
        return [f"{label} must be an object"]
    errors: list[str] = []
    for required in ("ingredient_id", "food_record_id", "compound_ids", "quantity", "food_state", "serving_fraction", "consumed_fraction", "mass_balance", "cooking_operations", "provenance"):
        if required not in ingredient:
            errors.append(f"{label}.{required} is required")
    for identifier in ("ingredient_id", "food_record_id"):
        value = ingredient.get(identifier)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{label}.{identifier} must be a nonempty string")
    compounds = ingredient.get("compound_ids")
    if not isinstance(compounds, list) or not compounds or any(not isinstance(c, str) or not c.strip() for c in compounds):
        errors.append(f"{label}.compound_ids must be a nonempty list of explicit IDs")
    if isinstance(compounds, list) and all(isinstance(c, str) for c in compounds) and len(compounds) != len(set(compounds)):
        errors.append(f"{label}.compound_ids contains duplicates")
    quantity = ingredient.get("quantity")
    if not isinstance(quantity, dict):
        errors.append(f"{label}.quantity must contain value and unit")
    else:
        raw_unit = quantity.get("unit", "")
        unit = raw_unit if isinstance(raw_unit, str) else ""
        if not unit or not (_is_mass(unit) or _is_volume(unit)):
            errors.append(f"{label}.quantity.unit is unsupported or ambiguous; use an explicitly supported mass or volume unit (received {unit!r})")
        try:
            _decimal(quantity.get("value"), f"{label}.quantity.value")
        except ValidationError as exc:
            errors.append(str(exc))
    if ingredient.get("food_state") not in {"raw", "processed", "cooked", "fermented", "dried", "frozen", "other"}:
        errors.append(f"{label}.food_state must be an explicit documented state")
    for fraction in ("serving_fraction", "consumed_fraction"):
        try:
            _decimal(ingredient.get(fraction), f"{label}.{fraction}", maximum=Decimal(1))
        except ValidationError as exc:
            errors.append(str(exc))
    errors.extend(_validate_mass_balance(ingredient.get("mass_balance"), f"{label}.mass_balance", MASS_BALANCE_FIELDS))
    errors.extend(_validate_operations(ingredient.get("cooking_operations", []), f"{label}.cooking_operations"))
    if "cooked_volume" in ingredient:
        errors.extend(_validate_measurement(ingredient["cooked_volume"], f"{label}.cooked_volume", volume=True))
    if not isinstance(ingredient.get("provenance"), dict):
        errors.append(f"{label}.provenance must be an object")
    density = ingredient.get("density")
    if density is not None:
        if not isinstance(density, dict) or not density.get("source_reference") or str(density.get("verification_status", "")).casefold() not in VERIFIED_SOURCE_STATUSES:
            errors.append(f"{label}.density requires a verified density source")
        else:
            try:
                if _decimal(density.get("kg_per_l"), f"{label}.density.kg_per_l") == 0:
                    errors.append(f"{label}.density.kg_per_l must be greater than zero")
            except ValidationError as exc:
                errors.append(str(exc))
    return errors


def validate_recipe(recipe: dict[str, Any]) -> list[str]:
    """Validate recipe structure and scientific state/mass-balance requirements."""
    if not isinstance(recipe, dict):
        return ["recipe must be an object"]
    errors: list[str] = []
    for required in ("recipe_id", "name", "ingredients", "cooking_operations", "servings_count", "mass_balance", "provenance"):
        if required not in recipe:
            errors.append(f"{required} is required")
    if not isinstance(recipe.get("recipe_id"), str) or not recipe["recipe_id"].strip():
        errors.append("recipe_id must be a nonempty string")
    if not isinstance(recipe.get("name"), str) or not recipe["name"].strip():
        errors.append("name must be a nonempty string")
    ingredients = recipe.get("ingredients")
    if not isinstance(ingredients, list) or not ingredients:
        errors.append("ingredients must be a nonempty list")
    else:
        ids = [str(i.get("ingredient_id", "")) for i in ingredients if isinstance(i, dict)]
        if len(ids) != len(set(ids)):
            errors.append("ingredient_id values must be unique within a recipe")
        for index, ingredient in enumerate(ingredients):
            errors.extend(_validate_ingredient(ingredient, f"ingredients[{index}]"))
    errors.extend(_validate_operations(recipe.get("cooking_operations", []), "cooking_operations"))
    servings = recipe.get("servings_count")
    if not isinstance(servings, dict) or servings.get("status") not in {"measured", "not_reported"}:
        errors.append("servings_count requires measured or not_reported status")
    elif servings.get("status") == "measured":
        try:
            if _decimal(servings.get("value"), "servings_count.value") == 0:
                errors.append("servings_count.value must be greater than zero")
        except ValidationError as exc:
            errors.append(str(exc))
    elif servings.get("value") not in (None, ""):
        errors.append("servings_count.value cannot be supplied when status is not_reported")
    errors.extend(_validate_mass_balance(recipe.get("mass_balance"), "mass_balance", RECIPE_MASS_FIELDS))
    for volume_field in ("cooked_volume", "serving_volume", "leftovers_volume"):
        if volume_field in recipe:
            errors.extend(_validate_measurement(recipe[volume_field], volume_field, volume=True))
    if not isinstance(recipe.get("provenance"), dict):
        errors.append("provenance must be an object")
    return errors


def validate_meal(meal: dict[str, Any], recipes: dict[str, dict[str, Any]] | None = None) -> list[str]:
    if not isinstance(meal, dict):
        return ["meal must be an object"]
    errors: list[str] = []
    if not isinstance(meal.get("meal_id"), str) or not meal["meal_id"].strip():
        errors.append("meal_id must be a nonempty string")
    if "provenance" not in meal or not isinstance(meal.get("provenance"), dict):
        errors.append("provenance object is required")
    components = meal.get("components")
    if not isinstance(components, list) or not components:
        return errors + ["components must be a nonempty list"]
    ids = [c.get("component_id") for c in components if isinstance(c, dict) and isinstance(c.get("component_id"), str)]
    if len(ids) != len(set(ids)):
        errors.append("component_id values must be unique within a meal")
    seen_recipes: set[str] = set()
    direct_pairs: set[tuple[str, str]] = set()
    recipe_pairs: set[tuple[str, str]] = set()
    for index, component in enumerate(components):
        label = f"components[{index}]"
        if not isinstance(component, dict):
            errors.append(f"{label} must be an object")
            continue
        if not isinstance(component.get("component_id"), str) or not component["component_id"].strip():
            errors.append(f"{label}.component_id must be a nonempty string")
        kind = component.get("kind")
        if kind == "recipe":
            raw_recipe_id = component.get("recipe_id", "")
            recipe_id = raw_recipe_id if isinstance(raw_recipe_id, str) else ""
            if "servings_consumed" not in component:
                errors.append(f"{label}.servings_consumed is required")
            if not recipe_id or (recipes is not None and recipe_id not in recipes):
                errors.append(f"{label}.recipe_id is unresolved")
            if recipe_id in seen_recipes:
                errors.append("a recipe may appear only once per meal; use one recipe component and set servings_consumed")
            seen_recipes.add(recipe_id)
            recipe_record = recipes.get(recipe_id) if recipes is not None and recipe_id in recipes else None
            if recipe_record is not None:
                errors.extend(f"{label}.recipe: {error}" for error in validate_recipe(recipe_record))
            try:
                _decimal(component.get("consumed_fraction"), f"{label}.consumed_fraction", maximum=Decimal(1))
            except ValidationError as exc:
                errors.append(str(exc))
            try:
                servings = _decimal(component.get("servings_consumed"), f"{label}.servings_consumed")
                leftover_servings = _decimal(component.get("leftovers_servings_consumed", "0"), f"{label}.leftovers_servings_consumed")
                if servings + leftover_servings == 0:
                    errors.append(f"{label} must include consumed servings or consumed leftover servings")
                if leftover_servings > 0:
                    recipe_record = recipes.get(recipe_id, {}) if recipes and recipe_id in recipes else {}
                    recipe_balance_value = recipe_record.get("mass_balance", {}) if isinstance(recipe_record, dict) else {}
                    recipe_balance = recipe_balance_value if isinstance(recipe_balance_value, dict) else {}
                    serving_mass = _measured_g(recipe_balance, "serving_mass", f"{label}.recipe.serving_mass")
                    leftovers_mass = _measured_g(recipe_balance, "leftovers_mass", f"{label}.recipe.leftovers_mass")
                    serving_volume_record = recipe_record.get("serving_volume", {"status": "not_reported"})
                    leftovers_volume_record = recipe_record.get("leftovers_volume", {"status": "not_reported"})
                    serving_volume = (_measurement_l(serving_volume_record, f"{label}.recipe.serving_volume")
                                      if isinstance(serving_volume_record, dict) and serving_volume_record.get("status") == "measured" else None)
                    leftovers_volume = (_measurement_l(leftovers_volume_record, f"{label}.recipe.leftovers_volume")
                                        if isinstance(leftovers_volume_record, dict) and leftovers_volume_record.get("status") == "measured" else None)
                    if serving_mass is not None and leftovers_mass is not None:
                        if leftover_servings * serving_mass > leftovers_mass:
                            errors.append(f"{label}.leftovers_servings_consumed exceeds the measured leftover mass")
                    elif serving_volume is not None and leftovers_volume is not None:
                        if leftover_servings * serving_volume > leftovers_volume:
                            errors.append(f"{label}.leftovers_servings_consumed exceeds the measured leftover volume")
                    else:
                        errors.append(f"{label}.leftovers_servings_consumed requires measured recipe serving_mass and leftovers_mass, or serving_volume and leftovers_volume")
                recipe_record = recipes.get(recipe_id, {}) if recipes and recipe_id in recipes else {}
                recipe_servings_value = recipe_record.get("servings_count", {}) if isinstance(recipe_record, dict) else {}
                recipe_servings = recipe_servings_value if isinstance(recipe_servings_value, dict) else {}
                if isinstance(recipe_servings, dict) and recipe_servings.get("status") == "measured":
                    available = _decimal(recipe_servings.get("value"), f"recipes[{recipe_id}].servings_count.value")
                    if servings > available:
                        errors.append(f"{label}.servings_consumed exceeds the recipe's measured servings_count")
            except ValidationError as exc:
                errors.append(str(exc))
            if recipes and recipe_id in recipes:
                recipe_record = recipes[recipe_id]
                recipe_ingredients = recipe_record.get("ingredients", []) if isinstance(recipe_record, dict) else []
                if isinstance(recipe_ingredients, list):
                    for ingredient in recipe_ingredients:
                        if not isinstance(ingredient, dict):
                            continue
                        food_id = ingredient.get("food_record_id")
                        compound_ids = ingredient.get("compound_ids", [])
                        if isinstance(food_id, str) and isinstance(compound_ids, list):
                            recipe_pairs.update((food_id, cid) for cid in compound_ids if isinstance(cid, str))
        elif kind == "food":
            for required in ("food_record_id", "compound_ids", "quantity", "consumed_fraction"):
                if required not in component:
                    errors.append(f"{label}.{required} is required")
            compound_ids = component.get("compound_ids", [])
            food_record_id = component.get("food_record_id")
            if isinstance(compound_ids, list) and isinstance(food_record_id, str):
                for cid in compound_ids:
                    if not isinstance(cid, str):
                        continue
                    pair = (food_record_id, cid)
                    if pair in direct_pairs:
                        errors.append(f"duplicate direct food/compound pair could double count: {pair[0]} / {pair[1]}")
                    direct_pairs.add(pair)
            direct_ingredient = {
                "ingredient_id": component.get("component_id"), "food_record_id": component.get("food_record_id"),
                "compound_ids": component.get("compound_ids"), "quantity": component.get("quantity"),
                "food_state": component.get("food_state", "raw"), "serving_fraction": "1",
                "consumed_fraction": component.get("consumed_fraction"), "mass_balance": component.get("mass_balance", _empty_mass_balance()),
                "cooking_operations": component.get("cooking_operations", []), "provenance": component.get("provenance", {}),
                "density": component.get("density"),
            }
            errors.extend(_validate_ingredient(direct_ingredient, label))
        else:
            errors.append(f"{label}.kind must be recipe or food")
    if direct_pairs & recipe_pairs:
        errors.append("meal includes a direct food/compound pair already included in a recipe; this could double count exposure")
    return errors


def _empty_mass_balance() -> dict[str, dict[str, str]]:
    return {field: {"status": "not_reported"} for field in MASS_BALANCE_FIELDS}


def save_recipe(recipe: dict[str, Any], path: Path) -> Path:
    errors = validate_recipe(recipe)
    if errors:
        raise ValidationError("Invalid recipe: " + "; ".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(recipe, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_recipe(path: Path) -> dict[str, Any]:
    recipe = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_recipe(recipe)
    if errors:
        raise ValidationError("Invalid stored recipe: " + "; ".join(errors))
    return recipe


def save_meal(meal: dict[str, Any], path: Path, recipes: dict[str, dict[str, Any]] | None = None) -> Path:
    errors = validate_meal(meal, recipes)
    if errors:
        raise ValidationError("Invalid meal: " + "; ".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(meal, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_meal(path: Path, recipes: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    meal = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_meal(meal, recipes)
    if errors:
        raise ValidationError("Invalid stored meal: " + "; ".join(errors))
    return meal


def _verified_food_concentration(food: dict[str, Any], compound_id: str, mappings: list[dict[str, Any]], compounds: dict[str, dict[str, Any]]) -> tuple[Decimal, str, dict[str, Any]]:
    compound = compounds.get(compound_id)
    if not compound:
        raise ValidationError("compound identity is unresolved in Stage B")
    if compound.get("StageC_Identity_Verification_Status", "Complete") != "Complete":
        raise ValidationError("Stage B chemical identity is pending review")
    mapping = next((m for m in mappings if m.get("food_record_id") == food.get("food_record_id") and m.get("compound_id") == compound_id), None)
    if not mapping or mapping.get("mapping_status") not in VERIFIED_STATUSES:
        raise ValidationError("a verified food-compound mapping is required")
    if food.get("food_use_classification", "").casefold() not in {"ordinary food", "food ingredient", "prepared beverage"}:
        raise ValidationError("food record is not in an eligible food context")
    if food.get("source_verification_status", "").casefold() not in VERIFIED_SOURCE_STATUSES:
        raise ValidationError("food-composition source is not verified")
    if food.get("source_classification") not in VERIFIED_SOURCE_CLASSES:
        raise ValidationError("food-composition source class is not eligible")
    if not (food.get("source_title") or food.get("source_url") or food.get("database_reference")):
        raise ValidationError("verified food concentration requires source provenance")
    if not food.get("raw_or_processed_state") or not food.get("moisture_basis"):
        raise ValidationError("explicit food state and moisture basis are required")
    value = food.get("normalized_concentration") or food.get("reported_concentration")
    unit = food.get("normalized_unit") or food.get("reported_unit")
    if value in (None, "") or unit in (None, "") or food.get("reported_concentration") in (None, "") or not food.get("reported_unit"):
        raise ValidationError("quantitative food concentration is missing")
    normalized_unit = str(unit)
    if normalized_unit.casefold() == "mg/kg":
        concentration = concentration_to_mg_per_kg(value, normalized_unit)
        if food.get("reported_concentration") not in (None, ""):
            reported = concentration_to_mg_per_kg(food["reported_concentration"], food.get("reported_unit", ""))
            if reported != concentration:
                raise ValidationError("reported and normalized concentrations disagree")
        return concentration, "mg/kg", mapping
    if normalized_unit.casefold() == "mg/l":
        concentration = volume_concentration_to_mg_per_l(value, normalized_unit)
        if food.get("reported_concentration") not in (None, ""):
            reported = volume_concentration_to_mg_per_l(food["reported_concentration"], food.get("reported_unit", ""))
            if reported != concentration:
                raise ValidationError("reported and normalized concentrations disagree")
        return concentration, "mg/L", mapping
    raise ValidationError(f"Unsupported normalized food concentration unit: {normalized_unit}")


def _quantity_measure(quantity: dict[str, Any], concentration_unit: str, density: dict[str, Any] | None) -> tuple[Decimal, str]:
    value, unit = quantity.get("value"), str(quantity.get("unit", ""))
    if _is_mass(unit):
        if concentration_unit == "mg/kg":
            return mass_to_kg(value, unit), "kg"
        if not density:
            raise ValidationError("mg/L food concentration with mass quantity requires an explicit verified density")
        kg = mass_to_kg(value, unit)
        return kg / _decimal(density.get("kg_per_l"), "density.kg_per_l"), "L"
    if _is_volume(unit):
        liters = _volume_to_l(value, unit)
        if concentration_unit == "mg/L":
            return liters, "L"
        if not density:
            raise ValidationError("mg/kg food concentration with volume quantity requires an explicit verified density")
        return liters * _decimal(density.get("kg_per_l"), "density.kg_per_l"), "kg"
    raise ValidationError(f"Unsupported quantity unit: {unit!r}")


def _interval_evidence(evidence: dict[str, Any], concentration: Decimal) -> tuple[Decimal, Decimal, str]:
    retention = PercentInterval(evidence.get("retention_low_percent"), evidence.get("retention_high_percent"))
    adjusted = adjust_concentration_interval(
        concentration, retention,
        exact_compound_match=evidence.get("exact_compound_match") is True,
        food_matrix_match=evidence.get("food_matrix_match") is True,
        cooking_condition_match=evidence.get("cooking_condition_match") is True,
        measurement_basis_compatible=evidence.get("measurement_basis_compatible") is True,
    )
    evidence_id = str(evidence.get("evidence_id", ""))
    if not evidence_id or not evidence.get("source_reference"):
        raise ValidationError("compatible Phase 2 evidence requires an evidence_id and source_reference")
    return adjusted.low, adjusted.high, evidence_id


def _calculate_ingredient(
    ingredient: dict[str, Any], food_records: dict[str, dict[str, Any]], mappings: list[dict[str, Any]],
    compounds: dict[str, dict[str, Any]], phase2_evidence: dict[str, dict[str, Any]],
    *, stage_b_manifest_sha256: str = "", serving_multiplier: Decimal = Decimal(1),
) -> list[dict[str, Any]]:
    food_id = str(ingredient.get("food_record_id", ""))
    food = food_records.get(food_id)
    results = []
    for compound_id in ingredient.get("compound_ids", []):
        estimate_id = deterministic_id("REX", {"ingredient_id": ingredient.get("ingredient_id"), "food_record_id": food_id, "compound_id": compound_id})
        base = {
            "estimate_id": estimate_id, "ingredient_id": ingredient.get("ingredient_id", ""), "food_record_id": food_id,
            "compound_id": compound_id, "calculation_status": "Incomplete", "raw_reference_amount_mg": "",
            "consumed_amount_low_mg": "", "consumed_amount_high_mg": "", "estimate_type": "unavailable",
            "raw_concentration": "", "raw_concentration_unit": "", "cooked_concentration_low": "",
            "cooked_concentration_high": "", "cooked_concentration_unit": "", "cooked_exposure_status": "NOT_APPLICABLE",
            "raw_reference_consumed_amount_mg": "",
            "input_source_ids": [], "retention_evidence_id": "", "warnings": [], "missing_inputs": [], "uncertainty_status": "No probability distribution or unsupported uncertainty added.",
            "stage_b_manifest_sha256": stage_b_manifest_sha256,
            "calculation_method": "food concentration × explicit serving mass/volume × explicit consumed fraction; cooked foods require compatible Phase2 evidence and measured cooked mass/volume",
            "provenance": {},
        }
        if food is None:
            base.update(calculation_status="Incomplete: missing food record", missing_inputs=["food_record_id"])
            results.append(base)
            continue
        try:
            concentration, concentration_unit, mapping = _verified_food_concentration(food, compound_id, mappings, compounds)
            quantity, quantity_unit = _quantity_measure(ingredient["quantity"], concentration_unit, ingredient.get("density"))
            sf = _decimal(ingredient.get("serving_fraction"), "serving_fraction", maximum=Decimal(1))
            consumed = _decimal(ingredient.get("consumed_fraction"), "consumed_fraction", maximum=Decimal(1)) * serving_multiplier
            if consumed > 1:
                raise ValidationError("combined consumed fraction cannot exceed 1")
            portion_quantity = quantity * sf
            raw_mg = concentration * portion_quantity
            amount = raw_mg * consumed
            source_ids = [x for x in (food_id, mapping.get("mapping_id", ""), food.get("doi", ""), food.get("pmid", ""), food.get("database_reference", "")) if x]
            if concentration_unit == "mg/kg" and quantity_unit == "kg":
                phase1 = calculate_exposure({
                    "estimate_id": estimate_id, "compound_id": compound_id, "food_record_id": food_id,
                    "ingredient_quantity": str(portion_quantity), "ingredient_unit": "kg",
                    "serving_mass": str(portion_quantity), "serving_unit": "kg",
                    "consumed_fraction": str(consumed), "period_id": str(ingredient.get("ingredient_id", "recipe")),
                }, food_records, mappings, compounds, stage_b_manifest_sha256=stage_b_manifest_sha256)
                if phase1.get("calculation_status") != COMPLETE:
                    raise ValidationError("Phase 1 exposure engine withheld contribution: " + "; ".join(phase1.get("warnings", []) + phase1.get("missing_inputs", [])))
                raw_mg = Decimal(phase1["initial_compound_amount"])
                amount = Decimal(phase1["estimated_consumed_amount"])
                source_ids = phase1.get("input_source_ids", source_ids)
            base.update({"raw_concentration": str(concentration), "raw_concentration_unit": concentration_unit,
                         "raw_reference_amount_mg": str(raw_mg), "raw_reference_consumed_amount_mg": str(amount), "input_source_ids": source_ids,
                         "ingredient_quantity": str(ingredient["quantity"].get("value", "")), "ingredient_unit": ingredient["quantity"].get("unit", ""),
                         "serving_fraction": str(sf), "consumed_fraction": str(consumed)})
            if _is_mass(str(ingredient["quantity"].get("unit", ""))):
                quantity_conversion = "stage_c.unit_conversion.mass_to_kg"
            elif concentration_unit == "mg/L":
                quantity_conversion = "recipe_engine.volume_to_liter"
            else:
                quantity_conversion = "recipe_engine.volume_to_liter × verified kg_per_l density"
            base["provenance"] = {
                "food_record_id": food_id, "compound_id": compound_id, "mapping_id": mapping.get("mapping_id", ""),
                "mapping_rationale": mapping.get("rationale", ""),
                "food_source_title": food.get("source_title", ""), "food_source_url": food.get("source_url", ""),
                "food_doi": food.get("doi", ""), "food_pmid": food.get("pmid", ""),
                "reported_concentration": food.get("reported_concentration", ""), "reported_unit": food.get("reported_unit", ""),
                "normalized_concentration": str(concentration), "normalized_unit": concentration_unit,
                "quantity": ingredient["quantity"], "serving_fraction": str(sf), "consumed_fraction": str(consumed),
                "normalized_ingredient_quantity": str(quantity), "normalized_ingredient_quantity_unit": quantity_unit,
                "normalized_portion_quantity": str(portion_quantity), "normalized_portion_unit": quantity_unit,
                "quantity_conversion_method": quantity_conversion, "density": ingredient.get("density", {}),
                "uncertainty_inputs": (ingredient.get("provenance", {}).get("uncertainty_inputs", {})
                                       if isinstance(ingredient.get("provenance"), dict) else {}),
                "ingredient_state": ingredient.get("food_state", ""),
                "preparation_description": ingredient.get("preparation_description", ""),
                "cooking_operations": ingredient.get("cooking_operations", []),
                "mass_balance": ingredient.get("mass_balance", {}),
                "stage_b_manifest_sha256": stage_b_manifest_sha256,
            }
            cooked = bool(ingredient.get("cooking_operations")) or ingredient.get("food_state") == "cooked"
            if not cooked:
                base.update(calculation_status=COMPLETE, consumed_amount_low_mg=str(amount), consumed_amount_high_mg=str(amount), estimate_type="point", cooked_exposure_status="RAW_FOOD_NO_COOKING_ADJUSTMENT")
            else:
                evidence = phase2_evidence.get(str(ingredient.get("ingredient_id"))) or phase2_evidence.get(f"{food_id}|{compound_id}")
                if not evidence:
                    base.update(calculation_status="Incomplete: cooked concentration unavailable", cooked_exposure_status="UNAVAILABLE_NO_COMPATIBLE_PHASE2_EVIDENCE", warnings=["Raw reference amount is not a cooked-food exposure estimate; no retention factor was substituted."], missing_inputs=["compatible Phase2 retention evidence"])
                else:
                    low_conc, high_conc, evidence_id = _interval_evidence(evidence, concentration)
                    cooked_mass = ingredient.get("mass_balance", {}).get("cooked_mass", {"status": "not_reported"})
                    cooked_volume = ingredient.get("cooked_volume", {"status": "not_reported"})
                    if concentration_unit == "mg/kg":
                        normalized_cooked_quantity = _measurement_kg(cooked_mass, "cooked_mass")
                        portion_cooked = normalized_cooked_quantity * sf
                        cooked_unit = "mg/kg"
                    else:
                        normalized_cooked_quantity = _measurement_l(cooked_volume, "cooked_volume")
                        portion_cooked = normalized_cooked_quantity * sf
                        cooked_unit = "mg/L"
                    base.update({"calculation_status": COMPLETE, "consumed_amount_low_mg": str(low_conc * portion_cooked * consumed),
                                 "consumed_amount_high_mg": str(high_conc * portion_cooked * consumed), "estimate_type": "interval",
                                 "cooked_concentration_low": str(low_conc), "cooked_concentration_high": str(high_conc),
                                 "cooked_concentration_unit": cooked_unit, "cooked_exposure_status": "COMPLETE_COMPATIBLE_PHASE2_INTERVAL",
                                 "retention_evidence_id": evidence_id, "input_source_ids": source_ids + [evidence_id],
                                 "warnings": ["Retention bounds are intervals, not probability distributions."]})
                    base["provenance"]["retention_evidence"] = {
                        "evidence_id": evidence_id, "source_reference": evidence.get("source_reference", ""),
                        "retention_low_percent": evidence.get("retention_low_percent"),
                        "retention_high_percent": evidence.get("retention_high_percent"),
                        "compatibility_gates": {key: evidence.get(key) for key in ("exact_compound_match", "food_matrix_match", "cooking_condition_match", "measurement_basis_compatible")},
                        "cooked_mass_or_volume": cooked_mass if concentration_unit == "mg/kg" else cooked_volume,
                        "normalized_cooked_quantity": str(normalized_cooked_quantity),
                        "normalized_cooked_quantity_unit": "kg" if concentration_unit == "mg/kg" else "L",
                        "normalized_cooked_portion_quantity": str(portion_cooked),
                        "normalized_cooked_portion_unit": "kg" if concentration_unit == "mg/kg" else "L",
                        "quantity_conversion_method": "stage_c.unit_conversion.mass_to_kg" if concentration_unit == "mg/kg" else "recipe_engine.volume_to_liter",
                    }
        except Exception as exc:
            base.update(calculation_status="Incomplete: scientific or unit compatibility", cooked_exposure_status="UNAVAILABLE", warnings=[str(exc)], missing_inputs=[str(exc)])
        results.append(base)
    return results


def _aggregate(results: list[dict[str, Any]], period_id: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in results:
        grouped.setdefault(row["compound_id"], []).append(row)
    totals = []
    for cid, group in sorted(grouped.items()):
        identifiers = [row["estimate_id"] for row in group]
        if any(row["calculation_status"] != COMPLETE for row in group):
            totals.append({"compound_id": cid, "period_id": period_id, "calculation_status": "Incomplete: one or more components unresolved", "estimate_type": "unavailable", "consumed_amount_low_mg": "", "consumed_amount_high_mg": "", "input_estimate_ids": identifiers, "input_source_ids": sorted({x for row in group for x in row["input_source_ids"]}), "missing_inputs": sorted({x for row in group for x in row["missing_inputs"]}), "warnings": sorted({x for row in group for x in row["warnings"]})})
            continue
        low = sum((Decimal(row["consumed_amount_low_mg"]) for row in group), Decimal(0))
        high = sum((Decimal(row["consumed_amount_high_mg"]) for row in group), Decimal(0))
        estimate_type = "interval" if any(row["estimate_type"] == "interval" for row in group) else "point"
        totals.append({"compound_id": cid, "period_id": period_id, "calculation_status": COMPLETE, "estimate_type": estimate_type,
                       "consumed_amount_low_mg": str(low), "consumed_amount_high_mg": str(high), "input_estimate_ids": identifiers,
                       "input_source_ids": sorted({x for row in group for x in row["input_source_ids"]}), "missing_inputs": [],
                       "warnings": sorted({x for row in group for x in row["warnings"]})})
    return totals


def _aggregate_raw_reference(results: list[dict[str, Any]], period_id: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in results:
        grouped.setdefault(row["compound_id"], []).append(row)
    totals = []
    for compound_id, group in sorted(grouped.items()):
        known = [Decimal(row["raw_reference_consumed_amount_mg"]) for row in group
                 if row.get("raw_reference_consumed_amount_mg") not in (None, "")]
        complete = len(known) == len(group)
        totals.append({
            "compound_id": compound_id, "period_id": period_id,
            "calculation_status": COMPLETE if complete else "INCOMPLETE: one or more raw-reference components unavailable",
            "raw_reference_amount_mg": str(sum(known, Decimal(0))) if complete else "",
            "known_component_subtotal_mg": str(sum(known, Decimal(0))),
            "input_estimate_ids": [row["estimate_id"] for row in group],
            "missing_estimate_ids": [row["estimate_id"] for row in group if row.get("raw_reference_consumed_amount_mg") in (None, "")],
            "input_source_ids": sorted({source for row in group for source in row.get("input_source_ids", [])}),
            "interpretation": "raw-food reference amount for the consumed portion; not a cooked-food exposure estimate",
        })
    return totals


def calculate_recipe_exposure(
    recipe: dict[str, Any], food_records: dict[str, dict[str, Any]], mappings: list[dict[str, Any]],
    compounds: dict[str, dict[str, Any]], phase2_evidence: dict[str, dict[str, Any]] | None = None,
    *, stage_b_manifest_sha256: str = "", consumed_fraction: Decimal | str = Decimal(1),
    phase2_release_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    errors = validate_recipe(recipe)
    if errors:
        raise ValidationError("Invalid recipe: " + "; ".join(errors))
    fraction = _decimal(consumed_fraction, "recipe consumed_fraction", maximum=Decimal(1))
    evidence = phase2_evidence or {}
    results = []
    for ingredient in recipe["ingredients"]:
        # Preserve a runtime portion/leftover fraction without mutating the stored recipe.
        results.extend(_calculate_ingredient(ingredient, food_records, mappings, compounds, evidence,
                                             stage_b_manifest_sha256=stage_b_manifest_sha256,
                                             serving_multiplier=fraction))
    return {"recipe_id": recipe["recipe_id"], "calculation_status": "COMPLETE" if all(r["calculation_status"] == COMPLETE for r in results) else "INCOMPLETE_WITH_VISIBLE_COMPONENTS",
            "ingredient_results": results, "compound_totals": _aggregate(results, recipe["recipe_id"]),
            "raw_reference_totals": _aggregate_raw_reference(results, recipe["recipe_id"]),
            "mass_balance": analyze_recipe_mass_balance(recipe), "provenance": {"recipe_provenance": recipe.get("provenance", {}),
            "stage_b_manifest_sha256": stage_b_manifest_sha256, "phase2_evidence_ids": sorted({r["retention_evidence_id"] for r in results if r["retention_evidence_id"]}),
            "phase2_release": (phase2_release_metadata or {}).get("release_id", ""),
            "phase2_manifest_sha256": (phase2_release_metadata or {}).get("manifest_sha256", ""),
            "calculation_method": "validated source concentration × explicit quantity/portion fraction × explicit consumed fraction; cooked intervals require compatible Phase 2 gates and measured cooked mass or volume"}}


def calculate_meal_exposure(
    meal: dict[str, Any], recipes: dict[str, dict[str, Any]], food_records: dict[str, dict[str, Any]],
    mappings: list[dict[str, Any]], compounds: dict[str, dict[str, Any]], phase2_evidence: dict[str, dict[str, Any]] | None = None,
    *, stage_b_manifest_sha256: str = "", phase2_release_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    errors = validate_meal(meal, recipes)
    if errors:
        raise ValidationError("Invalid meal: " + "; ".join(errors))
    evidence = phase2_evidence or {}
    all_results: list[dict[str, Any]] = []
    component_results = []
    for component in meal["components"]:
        if component["kind"] == "recipe":
            output = calculate_recipe_exposure(recipes[component["recipe_id"]], food_records, mappings, compounds, evidence,
                                               stage_b_manifest_sha256=stage_b_manifest_sha256,
                                               consumed_fraction=component["consumed_fraction"],
                                               phase2_release_metadata=phase2_release_metadata)
            results = output["ingredient_results"]
            serving_count = _decimal(component["servings_consumed"], "servings_consumed")
            leftover_count = _decimal(component.get("leftovers_servings_consumed", "0"), "leftovers_servings_consumed")
            total_serving_equivalents = serving_count + leftover_count
            for result in results:
                for key in ("consumed_amount_low_mg", "consumed_amount_high_mg", "raw_reference_amount_mg"):
                    if result.get(key) not in (None, ""):
                        result[key] = str(Decimal(result[key]) * total_serving_equivalents)
                if result.get("raw_reference_consumed_amount_mg") not in (None, ""):
                    result["raw_reference_consumed_amount_mg"] = str(Decimal(result["raw_reference_consumed_amount_mg"]) * total_serving_equivalents)
                result["servings_consumed"] = str(serving_count)
                result["leftovers_servings_consumed"] = str(leftover_count)
                result["provenance"]["servings_consumed"] = str(serving_count)
                result["provenance"]["leftovers_servings_consumed"] = str(leftover_count)
        else:
            direct = {
                "ingredient_id": component["component_id"], "food_record_id": component["food_record_id"],
                "compound_ids": component["compound_ids"], "quantity": component["quantity"],
                "food_state": component.get("food_state", "raw"), "serving_fraction": "1",
                "consumed_fraction": component["consumed_fraction"], "mass_balance": component.get("mass_balance", _empty_mass_balance()),
                "cooking_operations": component.get("cooking_operations", []), "provenance": component.get("provenance", {}),
                "density": component.get("density"), "cooked_volume": component.get("cooked_volume", {"status": "not_reported"}),
            }
            results = _calculate_ingredient(direct, food_records, mappings, compounds, evidence,
                                            stage_b_manifest_sha256=stage_b_manifest_sha256)
            output = {"ingredient_results": results, "calculation_status": "COMPLETE" if all(r["calculation_status"] == COMPLETE for r in results) else "INCOMPLETE_WITH_VISIBLE_COMPONENTS"}
        for result in results:
            result["meal_component_id"] = component["component_id"]
        all_results.extend(results)
        component_results.append({"component_id": component["component_id"], "kind": component["kind"], "calculation_status": output["calculation_status"], "ingredient_results": results})
    return {"meal_id": meal["meal_id"], "calculation_status": "COMPLETE" if all(r["calculation_status"] == COMPLETE for r in all_results) else "INCOMPLETE_WITH_VISIBLE_COMPONENTS",
            "component_results": component_results, "compound_totals": _aggregate(all_results, meal["meal_id"]),
            "raw_reference_totals": _aggregate_raw_reference(all_results, meal["meal_id"]),
            "provenance": {"meal_provenance": meal.get("provenance", {}), "stage_b_manifest_sha256": stage_b_manifest_sha256,
                           "phase2_release": (phase2_release_metadata or {}).get("release_id", ""),
                           "phase2_manifest_sha256": (phase2_release_metadata or {}).get("manifest_sha256", ""),
                           "recipe_ids": sorted({c["recipe_id"] for c in meal["components"] if c["kind"] == "recipe"}),
                           "calculation_method": "sum unique recipe or direct-food component estimates in mg; any unresolved contribution blocks a complete aggregate"}}
