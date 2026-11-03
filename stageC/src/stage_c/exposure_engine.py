"""Raw-food Phase 1 exposure calculations; no cooking retention or risk scoring."""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from . import __version__
from .compound_mapping import VERIFIED_STATUSES
from .provenance import deterministic_id, utc_timestamp
from .stage_b_connector import RELEASE_ID
from .unit_conversion import concentration_factor_to_mg_per_kg, concentration_to_mg_per_kg, mass_to_kg

COMPLETE = "Complete"


def _incomplete_base(item: dict[str, Any], status: str, missing: list[str], warnings: list[str]) -> dict[str, Any]:
    return {
        "estimate_id": item.get("estimate_id") or deterministic_id("EST", item),
        "compound_id": item.get("compound_id", ""), "compound_name": "", "food_record_id": item.get("food_record_id", ""),
        "ingredient_quantity": item.get("ingredient_quantity", ""), "ingredient_unit": item.get("ingredient_unit", ""),
        "source_concentration": "", "source_unit": "", "normalized_concentration": "", "normalized_unit": "mg/kg",
        "initial_compound_amount": "", "calculated_amount_unit": "mg", "compound_per_serving": "",
        "serving_mass": item.get("serving_mass", ""), "serving_unit": item.get("serving_unit", ""),
        "consumed_fraction": item.get("consumed_fraction", ""), "estimated_consumed_amount": "",
        "calculation_method": "mass concentration (mg/kg) × food mass (kg) × consumed fraction",
        "calculation_status": status, "input_source_ids": [], "stage_b_release_reference": RELEASE_ID,
        "warnings": warnings, "warning_identifiers": [], "missing_inputs": missing, "assumptions": [], "calculation_timestamp": utc_timestamp(),
        "software_version": __version__, "food_state": "", "moisture_basis": "", "period_id": item.get("period_id", ""),
        "provenance": {},
    }


def _with_inherited_warnings(result: dict[str, Any], compound: dict[str, Any]) -> dict[str, Any]:
    result["warning_identifiers"] = list(compound.get("StageC_Warning_Identifiers", []))
    return result


def calculate_exposure(item: dict[str, Any], food_records: dict[str, dict[str, Any]], mappings: list[dict[str, Any]], compounds: dict[str, dict[str, Any]], stage_b_manifest_sha256: str = "", timestamp: str | None = None) -> dict[str, Any]:
    """Calculate a single ingredient contribution, retaining incomplete outcomes."""
    out = _incomplete_base(item, "Invalid input", [], [])
    out["calculation_timestamp"] = timestamp or out["calculation_timestamp"]
    try:
        fraction = Decimal(str(item.get("consumed_fraction", "")))
        if not fraction.is_finite() or fraction < 0 or fraction > 1:
            raise ValueError("consumed_fraction must be explicitly supplied between 0 and 1")
        if not item.get("compound_id"):
            raise ValueError("compound_id is required")
        if not item.get("food_record_id"):
            raise ValueError("food_record_id is required")
        ingredient_raw = item.get("ingredient_quantity")
        if ingredient_raw in (None, ""):
            result = _incomplete_base(item, "Incomplete: missing ingredient mass", ["ingredient_quantity"], [])
            result["calculation_timestamp"] = timestamp or result["calculation_timestamp"]
            return result
        ingredient_kg = mass_to_kg(ingredient_raw, str(item.get("ingredient_unit", "")))
    except Exception as exc:
        out["warnings"] = [str(exc)]
        return out

    compound = compounds.get(str(item["compound_id"]))
    if compound is None:
        result = _incomplete_base(item, "Incomplete: unresolved identity", ["compound_id not found in Stage B"], ["No replacement identifier was generated."])
        result["calculation_timestamp"] = timestamp or result["calculation_timestamp"]
        return result
    if compound.get("StageC_Identity_Verification_Status", "Complete") != "Complete":
        result = _incomplete_base(item, "Incomplete: unresolved identity", ["manual Stage B chemical identity review"], ["Stage B marks this chemical identity as pending manual review."])
        result["compound_name"] = compound.get("Canonical_Name", "")
        result["calculation_timestamp"] = timestamp or result["calculation_timestamp"]
        return _with_inherited_warnings(result, compound)
    out["compound_name"] = compound.get("Canonical_Name", "")
    food = food_records.get(str(item["food_record_id"]))
    if food is None:
        result = _incomplete_base(item, "Incomplete: missing concentration", ["food_record_id not found in composition table"], [])
        result["compound_name"] = compound.get("Canonical_Name", "")
        result["calculation_timestamp"] = timestamp or result["calculation_timestamp"]
        return _with_inherited_warnings(result, compound)
    mapping = next((m for m in mappings if m.get("food_record_id") == item["food_record_id"] and m.get("compound_id") == item["compound_id"]), None)
    if mapping is None or mapping.get("mapping_status") not in VERIFIED_STATUSES:
        result = _incomplete_base(item, "Incomplete: unresolved identity", ["verified compound-food mapping"], ["Ambiguous, unmatched, and rejected mappings cannot produce exposure estimates."])
        result["compound_name"] = compound.get("Canonical_Name", "")
        result["calculation_timestamp"] = timestamp or result["calculation_timestamp"]
        return _with_inherited_warnings(result, compound)
    if not food.get("raw_or_processed_state") or not food.get("moisture_basis"):
        result = _incomplete_base(item, "Incomplete: incompatible units", ["explicit food state and moisture basis"], ["Wet-weight and dry-weight bases are never inferred or interconverted."])
        result["compound_name"] = compound.get("Canonical_Name", "")
        result["calculation_timestamp"] = timestamp or result["calculation_timestamp"]
        return _with_inherited_warnings(result, compound)
    concentration = food.get("normalized_concentration") or ""
    conc_unit = food.get("normalized_unit") or ""
    if not concentration or not food.get("reported_concentration") or not food.get("reported_unit"):
        # Missing means missing, including textual '<LOD'; it is never coerced to zero.
        result = _incomplete_base(item, "Incomplete: missing concentration", ["reported_concentration"], ["No quantitative food concentration is available; no numerical estimate was produced."])
        result["compound_name"] = compound.get("Canonical_Name", "")
        result["food_state"] = food.get("raw_or_processed_state", "")
        result["moisture_basis"] = food.get("moisture_basis", "")
        result["calculation_timestamp"] = timestamp or result["calculation_timestamp"]
        result["input_source_ids"] = [food.get("food_record_id", "")]
        return _with_inherited_warnings(result, compound)
    try:
        concentration_mg_kg = concentration_to_mg_per_kg(concentration, conc_unit)
        reported_mg_kg = concentration_to_mg_per_kg(food.get("reported_concentration"), food.get("reported_unit"))
        if reported_mg_kg != concentration_mg_kg:
            raise ValueError("reported and normalized concentrations do not agree")
        initial_mg = concentration_mg_kg * ingredient_kg
        serving_value = item.get("serving_mass", "")
        if serving_value not in (None, ""):
            serving_kg = mass_to_kg(serving_value, str(item.get("serving_unit", "")))
        else:
            serving_kg = ingredient_kg
        per_serving_mg = concentration_mg_kg * serving_kg
        consumed_mg = per_serving_mg * fraction
    except Exception as exc:
        result = _incomplete_base(item, "Incomplete: incompatible units", ["compatible concentration and food-mass units"], [str(exc)])
        result["compound_name"] = compound.get("Canonical_Name", "")
        result["calculation_timestamp"] = timestamp or result["calculation_timestamp"]
        return _with_inherited_warnings(result, compound)
    if food.get("source_verification_status", "").casefold() not in {"verified", "full-text verified", "database verified", "user verified"}:
        result = _incomplete_base(item, "Unverified input", [], ["Food concentration is not source-verified; calculated numeric amounts withheld."])
        result["compound_name"] = compound.get("Canonical_Name", "")
        result["calculation_timestamp"] = timestamp or result["calculation_timestamp"]
        return _with_inherited_warnings(result, compound)
    if food.get("source_classification", "") not in {"Primary analytical measurement", "Peer-reviewed secondary source", "Authoritative food-composition database", "Verified laboratory measurement", "User-supplied measurement"}:
        result = _incomplete_base(item, "Unverified input", [], ["Source classification is not eligible for quantitative estimation."])
        result["compound_name"] = compound.get("Canonical_Name", "")
        result["calculation_timestamp"] = timestamp or result["calculation_timestamp"]
        return _with_inherited_warnings(result, compound)
    if food.get("food_use_classification", "").casefold() not in {"ordinary food", "food ingredient", "prepared beverage"}:
        result = _incomplete_base(item, "Unverified input", [], ["Record is not explicitly verified as an ordinary food; supplement and medicinal-botanical data are excluded."])
        result["compound_name"] = compound.get("Canonical_Name", "")
        result["calculation_timestamp"] = timestamp or result["calculation_timestamp"]
        return _with_inherited_warnings(result, compound)
    method = "Food concentration (mg/kg) × ingredient mass (kg); per-serving amount × explicitly supplied consumed fraction"
    input_sources = [x for x in (food.get("food_record_id", ""), mapping.get("mapping_id", ""), food.get("doi", ""), food.get("pmid", ""), food.get("database_reference", "")) if x]
    out.update({
        "compound_name": compound.get("Canonical_Name", ""), "source_concentration": food.get("reported_concentration", ""),
        "source_unit": food.get("reported_unit", ""), "normalized_concentration": str(concentration_mg_kg), "normalized_unit": "mg/kg",
        "initial_compound_amount": str(initial_mg), "compound_per_serving": str(per_serving_mg),
        "estimated_consumed_amount": str(consumed_mg), "consumed_fraction": str(fraction),
        "calculation_status": COMPLETE, "calculation_method": method, "input_source_ids": input_sources,
        "food_state": food.get("raw_or_processed_state", ""), "moisture_basis": food.get("moisture_basis", ""),
        "warnings": ["Stage A cooking-retention adjustment is excluded from Phase 1."], "missing_inputs": [],
        "calculation_timestamp": timestamp or out["calculation_timestamp"],
        "provenance": {
            "compound_id": item["compound_id"], "stage_b_identity_source_file": "identity/identity_structure_audit.csv",
            "food_record_id": food.get("food_record_id", ""), "food_source_title": food.get("source_title", ""),
            "food_source_url": food.get("source_url", ""), "food_doi": food.get("doi", ""), "food_pmid": food.get("pmid", ""),
            "mapping_id": mapping.get("mapping_id", ""), "mapping_rationale": mapping.get("rationale", ""),
            "source_reported_concentration": food.get("reported_concentration", ""), "source_reported_unit": food.get("reported_unit", ""),
            "normalized_concentration": str(concentration_mg_kg), "normalized_unit": "mg/kg",
            "conversion_factor_to_mg_per_kg": str(concentration_factor_to_mg_per_kg(food.get("reported_unit", ""))),
            "ingredient_quantity": str(ingredient_raw), "ingredient_unit": str(item.get("ingredient_unit", "")),
            "serving_mass": str(serving_value if serving_value not in (None, "") else ingredient_raw),
            "serving_unit": str(item.get("serving_unit", "") if serving_value not in (None, "") else item.get("ingredient_unit", "")),
            "consumed_fraction": str(fraction), "formula": method, "stage_b_manifest_sha256": stage_b_manifest_sha256,
        },
    })
    # Estimate identifiers are stable for the same scientific input; timestamps are run metadata.
    out["estimate_id"] = item.get("estimate_id") or deterministic_id("EST", {k: item.get(k, "") for k in sorted(item)})
    return _with_inherited_warnings(out, compound)


def aggregate_exposures(exposures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate compatible, explicitly period-labelled contributions without double counting."""
    seen = set()
    groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
    for row in exposures:
        estimate_id = row.get("estimate_id", "")
        if not estimate_id or estimate_id in seen:
            raise ValueError("Each ingredient/meal requires a unique estimate_id; duplicates risk double counting")
        seen.add(estimate_id)
        period = row.get("period_id", "")
        if not period:
            raise ValueError("period_id is required to aggregate multiple ingredients or meals")
        key = (row.get("compound_id", ""), period, row.get("food_state", ""), row.get("moisture_basis", ""))
        groups.setdefault(key, []).append(row)
    results = []
    for (compound_id, period, state, basis), group in sorted(groups.items()):
        ids = [r["estimate_id"] for r in group]
        if any(r.get("calculation_status") != COMPLETE for r in group):
            results.append({"compound_id": compound_id, "period_id": period, "food_state": state, "moisture_basis": basis, "calculation_status": group[0].get("calculation_status", "Incomplete"), "estimated_consumed_amount": "", "calculated_amount_unit": "mg", "input_estimate_ids": ids, "warnings": ["Incomplete ingredient contributions were not summed."], "missing_inputs": sorted({x for r in group for x in r.get("missing_inputs", [])})})
            continue
        units = {r.get("calculated_amount_unit") for r in group}
        if len(units) != 1 or "mg" not in units:
            results.append({"compound_id": compound_id, "period_id": period, "food_state": state, "moisture_basis": basis, "calculation_status": "Incomplete: incompatible units", "estimated_consumed_amount": "", "calculated_amount_unit": "mg", "input_estimate_ids": ids, "warnings": ["Contributions do not share a compatible amount unit."], "missing_inputs": []})
            continue
        total = sum((Decimal(r["estimated_consumed_amount"]) for r in group), Decimal(0))
        results.append({"compound_id": compound_id, "period_id": period, "food_state": state, "moisture_basis": basis, "calculation_status": COMPLETE, "estimated_consumed_amount": str(total), "calculated_amount_unit": "mg", "input_estimate_ids": ids, "warnings": sorted({w for r in group for w in r.get("warnings", [])}), "missing_inputs": []})
    return results
