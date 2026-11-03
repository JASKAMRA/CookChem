from __future__ import annotations

import json
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from stage_c.exceptions import ValidationError
from stage_c.recipe_engine import (
    calculate_meal_exposure,
    calculate_recipe_exposure,
    analyze_recipe_mass_balance,
    load_recipe,
    save_recipe,
    validate_meal,
    validate_recipe,
)


COMPOUNDS = {"C-1": {"Compound_ID": "C-1", "Canonical_Name": "Test compound"}}
FOOD = {
    "F-1": {"food_record_id": "F-1", "food_name": "Test food", "reported_concentration": "5", "reported_unit": "mg/kg",
            "normalized_concentration": "5", "normalized_unit": "mg/kg", "raw_or_processed_state": "raw", "moisture_basis": "wet weight",
            "food_use_classification": "ordinary food", "source_verification_status": "Verified",
            "source_classification": "Primary analytical measurement", "source_title": "Synthetic fixture", "source_url": "https://example.invalid/source", "doi": "10.1234/example"},
    "F-2": {"food_record_id": "F-2", "food_name": "Second food", "reported_concentration": "10", "reported_unit": "mg/kg",
            "normalized_concentration": "10", "normalized_unit": "mg/kg", "raw_or_processed_state": "raw", "moisture_basis": "wet weight",
            "food_use_classification": "ordinary food", "source_verification_status": "Verified",
            "source_classification": "Primary analytical measurement", "source_title": "Synthetic fixture 2", "source_url": "https://example.invalid/source2"},
    "B-1": {"food_record_id": "B-1", "food_name": "Test beverage", "reported_concentration": "2", "reported_unit": "mg/L",
            "normalized_concentration": "2", "normalized_unit": "mg/L", "raw_or_processed_state": "processed", "moisture_basis": "as-consumed beverage",
            "food_use_classification": "prepared beverage", "source_verification_status": "Verified",
            "source_classification": "Authoritative food-composition database", "source_title": "Synthetic beverage fixture", "source_url": "https://example.invalid/beverage"},
}
MAPPINGS = [
    {"mapping_id": "MAP-1", "food_record_id": "F-1", "compound_id": "C-1", "mapping_status": "Exact identity match", "rationale": "synthetic fixture"},
    {"mapping_id": "MAP-2", "food_record_id": "F-2", "compound_id": "C-1", "mapping_status": "Exact identity match", "rationale": "synthetic fixture"},
    {"mapping_id": "MAP-3", "food_record_id": "B-1", "compound_id": "C-1", "mapping_status": "Exact identity match", "rationale": "synthetic fixture"},
]


def measure_not_reported():
    return {"status": "not_reported"}


def mass_balance(cooked="not_reported", cooked_value=None, cooked_unit="g"):
    result = {key: measure_not_reported() for key in (
        "raw_mass", "prepared_mass", "cooked_mass", "edible_portion_mass", "discarded_portion_mass",
        "cooking_liquid_retained_mass", "cooking_liquid_discarded_mass", "cooking_oil_retained_mass", "cooking_oil_discarded_mass",
    )}
    if cooked == "measured":
        result["cooked_mass"] = {"status": "measured", "value": str(cooked_value), "unit": cooked_unit, "source_reference": "synthetic measured cooked batch"}
    return result


def recipe(food_id="F-1", *, cooked=False, cooked_mass="not_reported", quantity="200", unit="g"):
    operations = [{"operation_id": "OP-1", "method": "boil", "duration_min": "10", "medium": "water"}] if cooked else []
    ingredient = {
        "ingredient_id": "I-1", "food_record_id": food_id, "compound_ids": ["C-1"],
        "quantity": {"value": quantity, "unit": unit}, "food_state": "cooked" if cooked else "raw",
        "preparation_description": "synthetic fixture", "serving_fraction": "0.5", "consumed_fraction": "0.5",
        "mass_balance": mass_balance(cooked_mass, 200 if cooked_mass == "measured" else None),
        "cooking_operations": operations, "provenance": {"fixture": "synthetic"},
    }
    recipe_balance = {key: measure_not_reported() for key in (
        "raw_mass", "prepared_mass", "cooked_mass", "edible_portion_mass", "discarded_portion_mass",
        "cooking_liquid_retained_mass", "cooking_liquid_discarded_mass", "cooking_oil_retained_mass", "cooking_oil_discarded_mass",
        "batch_yield", "serving_mass", "leftovers_mass",
    )}
    return {"recipe_id": "R-1", "name": "Synthetic recipe", "ingredients": [ingredient],
            "cooking_operations": operations, "servings_count": {"status": "not_reported"},
            "mass_balance": recipe_balance, "provenance": {"fixture": "synthetic"}}


def retention_evidence(**overrides):
    result = {"retention_low_percent": "40", "retention_high_percent": "60", "evidence_id": "P2-TEST-1",
              "source_reference": "synthetic test fixture", "exact_compound_match": True, "food_matrix_match": True,
              "cooking_condition_match": True, "measurement_basis_compatible": True}
    result.update(overrides)
    return result


class RecipeEngineTests(unittest.TestCase):
    def test_schema_json_parses_and_recipe_validates(self):
        recipe_schema = json.loads((ROOT / "schemas/recipe.schema.json").read_text(encoding="utf-8"))
        meal_schema = json.loads((ROOT / "schemas/meal.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(recipe_schema["$schema"], meal_schema["$schema"])
        self.assertEqual(validate_recipe(recipe()), [])

    def test_recipe_storage_round_trip(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            path = save_recipe(recipe(), Path(folder) / "R-1.json")
            self.assertEqual(load_recipe(path), recipe())

    def test_raw_recipe_uses_phase1_verified_exposure_and_explicit_fractions(self):
        result = calculate_recipe_exposure(recipe(), FOOD, MAPPINGS, COMPOUNDS, stage_b_manifest_sha256="a" * 64)
        ingredient = result["ingredient_results"][0]
        self.assertEqual(ingredient["calculation_status"], "Complete")
        self.assertEqual(Decimal(ingredient["raw_reference_amount_mg"]), Decimal("0.5"))
        self.assertEqual(Decimal(ingredient["consumed_amount_low_mg"]), Decimal("0.25"))
        self.assertEqual(result["compound_totals"][0]["calculation_status"], "Complete")
        self.assertEqual(ingredient["provenance"]["stage_b_manifest_sha256"], "a" * 64)

    def test_cooked_recipe_without_phase2_evidence_has_no_cooked_number(self):
        result = calculate_recipe_exposure(recipe(cooked=True), FOOD, MAPPINGS, COMPOUNDS)
        ingredient = result["ingredient_results"][0]
        self.assertEqual(ingredient["cooked_exposure_status"], "UNAVAILABLE_NO_COMPATIBLE_PHASE2_EVIDENCE")
        self.assertEqual(ingredient["calculation_status"], "Incomplete: cooked concentration unavailable")
        self.assertEqual(ingredient["consumed_amount_low_mg"], "")
        self.assertNotEqual(ingredient["raw_reference_amount_mg"], "")

    def test_cooked_mass_and_all_gates_are_required_for_phase2_interval(self):
        r = recipe(cooked=True, cooked_mass="measured")
        evidence = {"I-1": retention_evidence()}
        result = calculate_recipe_exposure(r, FOOD, MAPPINGS, COMPOUNDS, evidence)
        estimate = result["ingredient_results"][0]
        self.assertEqual(estimate["calculation_status"], "Complete")
        self.assertEqual(estimate["estimate_type"], "interval")
        self.assertEqual(Decimal(estimate["consumed_amount_low_mg"]), Decimal("0.1"))
        self.assertEqual(Decimal(estimate["consumed_amount_high_mg"]), Decimal("0.15"))
        blocked = calculate_recipe_exposure(r, FOOD, MAPPINGS, COMPOUNDS, {"I-1": retention_evidence(food_matrix_match=False)})
        self.assertNotEqual(blocked["ingredient_results"][0]["calculation_status"], "Complete")
        self.assertEqual(blocked["ingredient_results"][0]["consumed_amount_low_mg"], "")

    def test_volume_beverage_requires_no_density_for_mg_per_l(self):
        beverage = recipe("B-1", quantity="250", unit="mL")
        item = beverage["ingredients"][0]
        item["serving_fraction"] = "1"
        item["consumed_fraction"] = "0.5"
        result = calculate_recipe_exposure(beverage, FOOD, MAPPINGS, COMPOUNDS)
        estimate = result["ingredient_results"][0]
        self.assertEqual(estimate["calculation_status"], "Complete")
        self.assertEqual(Decimal(estimate["consumed_amount_low_mg"]), Decimal("0.25"))

    def test_volume_to_mass_requires_verified_density(self):
        liquid_food = {"F-3": {**FOOD["F-1"], "food_record_id": "F-3"}}
        mappings = MAPPINGS + [{"mapping_id": "MAP-3", "food_record_id": "F-3", "compound_id": "C-1", "mapping_status": "Exact identity match"}]
        item = recipe("F-3", quantity="250", unit="mL")["ingredients"][0]
        item["serving_fraction"] = "1"
        item["consumed_fraction"] = "1"
        result = calculate_recipe_exposure({**recipe("F-3", quantity="250", unit="mL"), "ingredients": [item]}, liquid_food, mappings, COMPOUNDS)
        self.assertEqual(result["ingredient_results"][0]["calculation_status"], "Incomplete: scientific or unit compatibility")
        item["density"] = {"kg_per_l": "0.8", "verification_status": "Verified", "source_reference": "synthetic measured density"}
        result = calculate_recipe_exposure({**recipe("F-3", quantity="250", unit="mL"), "ingredients": [item]}, liquid_food, mappings, COMPOUNDS)
        self.assertEqual(result["ingredient_results"][0]["consumed_amount_low_mg"], "1.000")

    def test_meal_aggregates_multiple_components_and_blocks_double_counting(self):
        r = recipe()
        meal = {"meal_id": "M-1", "provenance": {}, "components": [
            {"component_id": "C-RECIPE", "kind": "recipe", "recipe_id": "R-1", "servings_consumed": "1", "consumed_fraction": "0.5"},
            {"component_id": "C-FOOD", "kind": "food", "food_record_id": "F-2", "compound_ids": ["C-1"],
             "quantity": {"value": "100", "unit": "g"}, "consumed_fraction": "0.5", "food_state": "raw", "provenance": {}},
        ]}
        output = calculate_meal_exposure(meal, {"R-1": r}, FOOD, MAPPINGS, COMPOUNDS)
        total = output["compound_totals"][0]
        self.assertEqual(total["calculation_status"], "Complete")
        self.assertEqual(Decimal(total["consumed_amount_low_mg"]), Decimal("0.625"))
        overlapping = {"meal_id": "M-2", "provenance": {}, "components": [meal["components"][0],
            {"component_id": "C-DUP", "kind": "food", "food_record_id": "F-1", "compound_ids": ["C-1"],
             "quantity": {"value": "100", "unit": "g"}, "consumed_fraction": "1", "food_state": "raw"}]}
        self.assertTrue(any("double count" in error for error in validate_meal(overlapping, {"R-1": r})))
        with self.assertRaises(ValidationError):
            calculate_meal_exposure(overlapping, {"R-1": r}, FOOD, MAPPINGS, COMPOUNDS)

    def test_unreported_cooked_mass_is_not_derived_from_raw_mass(self):
        r = recipe(cooked=True)
        result = calculate_recipe_exposure(r, FOOD, MAPPINGS, COMPOUNDS, {"I-1": retention_evidence()})
        estimate = result["ingredient_results"][0]
        self.assertNotEqual(estimate["calculation_status"], "Complete")
        self.assertEqual(estimate["consumed_amount_low_mg"], "")

    def test_multi_ingredient_recipe_returns_independently_calculated_total(self):
        r = recipe()
        second = dict(r["ingredients"][0])
        second.update(ingredient_id="I-2", food_record_id="F-2", quantity={"value": "100", "unit": "g"},
                      serving_fraction="1", consumed_fraction="1")
        r["ingredients"].append(second)
        result = calculate_recipe_exposure(r, FOOD, MAPPINGS, COMPOUNDS)
        self.assertEqual(len(result["ingredient_results"]), 2)
        self.assertEqual(Decimal(result["raw_reference_totals"][0]["raw_reference_amount_mg"]), Decimal("1.25"))
        self.assertEqual(Decimal(result["compound_totals"][0]["consumed_amount_low_mg"]), Decimal("1.25"))

    def test_meal_with_multiple_recipes_sums_distinct_recipe_exposures(self):
        first = recipe()
        second = recipe("F-2", quantity="100", unit="g")
        second["recipe_id"] = "R-2"
        second["ingredients"][0]["serving_fraction"] = "1"
        second["ingredients"][0]["consumed_fraction"] = "1"
        meal = {"meal_id": "M-MULTI", "provenance": {}, "components": [
            {"component_id": "CR-1", "kind": "recipe", "recipe_id": "R-1", "servings_consumed": "1", "consumed_fraction": "1"},
            {"component_id": "CR-2", "kind": "recipe", "recipe_id": "R-2", "servings_consumed": "1", "consumed_fraction": "1"},
        ]}
        output = calculate_meal_exposure(meal, {"R-1": first, "R-2": second}, FOOD, MAPPINGS, COMPOUNDS)
        self.assertEqual(Decimal(output["compound_totals"][0]["consumed_amount_low_mg"]), Decimal("1.25"))
        self.assertEqual(Decimal(output["raw_reference_totals"][0]["raw_reference_amount_mg"]), Decimal("1.25"))

    def test_leftover_serving_equivalents_require_and_respect_measured_mass(self):
        r = recipe()
        r["mass_balance"]["serving_mass"] = {"status": "measured", "value": "100", "unit": "g", "source_reference": "fixture"}
        r["mass_balance"]["leftovers_mass"] = {"status": "measured", "value": "50", "unit": "g", "source_reference": "fixture"}
        r["servings_count"] = {"status": "measured", "value": "2"}
        meal = {"meal_id": "M-LEFT", "provenance": {}, "components": [
            {"component_id": "CR-LEFT", "kind": "recipe", "recipe_id": "R-1", "servings_consumed": "0.5",
             "leftovers_servings_consumed": "0.5", "consumed_fraction": "0.5"}
        ]}
        result = calculate_meal_exposure(meal, {"R-1": r}, FOOD, MAPPINGS, COMPOUNDS)
        self.assertEqual(Decimal(result["compound_totals"][0]["consumed_amount_low_mg"]), Decimal("0.125"))
        meal["components"][0]["leftovers_servings_consumed"] = "0.6"
        self.assertTrue(any("exceeds the measured leftover mass" in error for error in validate_meal(meal, {"R-1": r})))

    def test_measured_mass_balance_matches_raw_output_servings_and_leftovers(self):
        r = recipe()
        def measured(value):
            return {"status": "measured", "value": str(value), "unit": "g", "source_reference": "synthetic scale"}
        r["ingredients"][0]["mass_balance"]["raw_mass"] = measured(200)
        for field, value in {"raw_mass": 200, "cooked_mass": 300, "batch_yield": 300,
                             "edible_portion_mass": 280, "discarded_portion_mass": 20,
                             "serving_mass": 100, "leftovers_mass": 100}.items():
            r["mass_balance"][field] = measured(value)
        r["servings_count"] = {"status": "measured", "value": "2"}
        report = analyze_recipe_mass_balance(r)
        self.assertEqual(report["status"], "CONSISTENT")
        self.assertEqual(report["raw_ingredient_mass_g"], "200")
        self.assertEqual(report["cooked_output_mass_g"], "300")
        self.assertEqual(report["unaccounted_mass_g"], "0")

    def test_mass_balance_flags_conflict_and_positive_unaccounted_mass(self):
        r = recipe()
        def measured(value):
            return {"status": "measured", "value": str(value), "unit": "g", "source_reference": "synthetic scale"}
        r["ingredients"][0]["mass_balance"]["raw_mass"] = measured(250)
        r["mass_balance"]["raw_mass"] = measured(200)
        r["mass_balance"]["cooked_mass"] = measured(300)
        r["mass_balance"]["edible_portion_mass"] = measured(200)
        r["mass_balance"]["discarded_portion_mass"] = measured(20)
        report = analyze_recipe_mass_balance(r)
        self.assertEqual(report["status"], "INCONSISTENT")
        self.assertEqual(report["unaccounted_mass_g"], "80")
        self.assertTrue(any(row["check_id"] == "RAW_INPUTS" and row["status"] == "INCONSISTENT" for row in report["checks"]))

    def test_recipe_volume_balance_is_explicit_and_never_converted_to_mass(self):
        r = recipe()
        def measured(value, unit):
            return {"status": "measured", "value": str(value), "unit": unit, "source_reference": "synthetic volumetric measure"}
        r["cooked_volume"] = measured(1000, "mL")
        r["serving_volume"] = measured(250, "mL")
        r["leftovers_volume"] = measured(500, "mL")
        r["servings_count"] = {"status": "measured", "value": "2"}
        report = analyze_recipe_mass_balance(r)
        volume_check = next(row for row in report["checks"] if row["check_id"] == "VOLUME_SERVINGS_AND_LEFTOVERS")
        self.assertEqual(volume_check["status"], "CONSISTENT")
        self.assertEqual(report["cooked_output_volume_l"], "1")
        self.assertEqual(report["unaccounted_mass_g"], "")
        self.assertEqual(report["unaccounted_volume_l"], "0")

    def test_beverage_leftovers_use_volume_only_with_measured_serving_and_leftover_volumes(self):
        r = recipe()
        def measured(value, unit):
            return {"status": "measured", "value": str(value), "unit": unit, "source_reference": "synthetic volumetric measure"}
        r["serving_volume"] = measured(250, "mL")
        r["leftovers_volume"] = measured(500, "mL")
        r["servings_count"] = {"status": "measured", "value": "2"}
        meal = {"meal_id": "M-VOL-LEFT", "provenance": {}, "components": [
            {"component_id": "CR-VOL", "kind": "recipe", "recipe_id": "R-1", "servings_consumed": "0.5",
             "leftovers_servings_consumed": "2", "consumed_fraction": "1"}
        ]}
        self.assertEqual(validate_meal(meal, {"R-1": r}), [])
        meal["components"][0]["leftovers_servings_consumed"] = "2.1"
        self.assertTrue(any("measured leftover volume" in error for error in validate_meal(meal, {"R-1": r})))

    def test_unsupported_unit_is_rejected_instead_of_assumed(self):
        r = recipe()
        r["ingredients"][0]["quantity"] = {"value": "1", "unit": "cup"}
        self.assertTrue(any("unsupported" in error for error in validate_recipe(r)))

    def test_missing_identity_mapping_keeps_exposure_unavailable(self):
        compounds = {"C-1": {"Compound_ID": "C-1", "StageC_Identity_Verification_Status": "Pending review"}}
        output = calculate_recipe_exposure(recipe(), FOOD, MAPPINGS, compounds)
        estimate = output["ingredient_results"][0]
        self.assertEqual(estimate["calculation_status"], "Incomplete: scientific or unit compatibility")
        self.assertIn("identity is pending review", estimate["missing_inputs"][0])
        self.assertEqual(estimate["raw_reference_amount_mg"], "")

    def test_missing_mapping_is_reported_without_inferred_food_identity(self):
        output = calculate_recipe_exposure(recipe(), FOOD, [], COMPOUNDS)
        estimate = output["ingredient_results"][0]
        self.assertNotEqual(estimate["calculation_status"], "Complete")
        self.assertEqual(estimate["raw_reference_amount_mg"], "")
        self.assertTrue(estimate["missing_inputs"])

    def test_missing_batch_yield_stays_incomplete_and_is_not_derived(self):
        report = analyze_recipe_mass_balance(recipe())
        self.assertEqual(report["status"], "INCOMPLETE")
        self.assertEqual(report["cooked_output_mass_g"], "")
        self.assertEqual(report["unaccounted_mass_g"], "")
        batch_check = next(row for row in report["checks"] if row["check_id"] == "COOKED_OUTPUT_VS_BATCH_YIELD")
        self.assertEqual(batch_check["status"], "INCOMPLETE")
        self.assertEqual(batch_check["reason"], "cooked mass or batch yield is not reported")

    def test_incompatible_cooking_condition_is_visible_and_blocks_numeric_cooked_amount(self):
        r = recipe(cooked=True, cooked_mass="measured")
        output = calculate_recipe_exposure(r, FOOD, MAPPINGS, COMPOUNDS,
                                            {"I-1": retention_evidence(cooking_condition_match=False)})
        estimate = output["ingredient_results"][0]
        self.assertNotEqual(estimate["calculation_status"], "Complete")
        self.assertEqual(estimate["consumed_amount_low_mg"], "")
        self.assertTrue(any("cooking conditions" in reason for reason in estimate["missing_inputs"]))

    def test_raw_reference_total_is_explicitly_separate_from_cooked_exposure(self):
        output = calculate_recipe_exposure(recipe(cooked=True), FOOD, MAPPINGS, COMPOUNDS)
        self.assertEqual(Decimal(output["raw_reference_totals"][0]["raw_reference_amount_mg"]), Decimal("0.25"))
        self.assertEqual(output["compound_totals"][0]["consumed_amount_low_mg"], "")
        self.assertIn("not a cooked-food exposure estimate", output["raw_reference_totals"][0]["interpretation"])


if __name__ == "__main__":
    unittest.main()
