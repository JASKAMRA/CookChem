from __future__ import annotations

import sys
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from stage_c.exceptions import ValidationError
from stage_c.uncertainty import (
    assess_phase3_estimate_uncertainty,
    assess_phase3_output_uncertainty,
    assess_uncertainty_availability,
    propagate_product_interval,
    rank_interval_sensitivity,
)
from stage_c.validation import (
    compare_to_reference,
    independent_reference_exposure_mg,
    summarize_validation,
    verify_phase3_aggregate_arithmetic,
    verify_phase3_ingredient_arithmetic,
)

# Reuse the established Phase 3 fixtures and public calculation path.
from test_recipe_engine import COMPOUNDS, FOOD, MAPPINGS, recipe, retention_evidence
from stage_c.recipe_engine import calculate_meal_exposure, calculate_recipe_exposure


class UncertaintyFoundationTests(unittest.TestCase):
    def test_phase3_point_estimate_does_not_become_zero_width_uncertainty(self):
        output = calculate_recipe_exposure(recipe(), FOOD, MAPPINGS, COMPOUNDS)
        result = assess_phase3_estimate_uncertainty(output["ingredient_results"][0])
        self.assertEqual(result["uncertainty_status"], "POINT_ESTIMATE_ONLY")
        self.assertEqual(result["amount_low"], "")
        self.assertEqual(result["amount_high"], "")
        self.assertIn("food concentration analytical uncertainty", result["missing_uncertainty_factors"])

    def test_phase3_retention_interval_is_reported_as_conditional_bound(self):
        cooked = recipe(cooked=True, cooked_mass="measured")
        output = calculate_recipe_exposure(cooked, FOOD, MAPPINGS, COMPOUNDS, {"I-1": retention_evidence()})
        estimate = output["ingredient_results"][0]
        result = assess_phase3_estimate_uncertainty(estimate)
        self.assertEqual(result["uncertainty_status"], "BOUNDED_INTERVAL_CONDITIONAL_ON_RECIPE_INPUTS")
        self.assertEqual(Decimal(result["amount_low"]), Decimal("0.1"))
        self.assertEqual(Decimal(result["amount_high"]), Decimal("0.15"))
        self.assertEqual(result["supporting_evidence"][0]["evidence_id"], "P2-TEST-1")
        self.assertFalse(result["distribution_assumed"])
        self.assertIn("not a probability interval", result["interval_kind"])

    def test_phase3_beverage_retention_interval_keeps_volume_basis(self):
        beverage = recipe("B-1", cooked=True, quantity="250", unit="mL")
        beverage["ingredients"][0]["cooked_volume"] = {
            "status": "measured", "value": "250", "unit": "mL", "source_reference": "synthetic measured volume"}
        output = calculate_recipe_exposure(beverage, FOOD, MAPPINGS, COMPOUNDS, {"I-1": retention_evidence()})
        estimate = output["ingredient_results"][0]
        result = assess_phase3_estimate_uncertainty(estimate)
        self.assertEqual(result["uncertainty_status"], "BOUNDED_INTERVAL_CONDITIONAL_ON_RECIPE_INPUTS")
        self.assertEqual(Decimal(result["amount_low"]), Decimal("0.05"))
        self.assertEqual(Decimal(result["amount_high"]), Decimal("0.075"))

    def test_phase3_interval_without_source_provenance_is_rejected(self):
        output = calculate_recipe_exposure(recipe(cooked=True, cooked_mass="measured"), FOOD, MAPPINGS, COMPOUNDS,
                                           {"I-1": retention_evidence()})
        estimate = output["ingredient_results"][0]
        del estimate["provenance"]["retention_evidence"]["source_reference"]
        with self.assertRaises(ValidationError):
            assess_phase3_estimate_uncertainty(estimate)

    def test_phase3_interval_requires_compatible_gates_and_consistent_bounds(self):
        output = calculate_recipe_exposure(recipe(cooked=True, cooked_mass="measured"), FOOD, MAPPINGS, COMPOUNDS,
                                           {"I-1": retention_evidence()})
        estimate = output["ingredient_results"][0]
        estimate["provenance"]["retention_evidence"]["compatibility_gates"]["food_matrix_match"] = False
        with self.assertRaises(ValidationError):
            assess_phase3_estimate_uncertainty(estimate)
        estimate["provenance"]["retention_evidence"]["compatibility_gates"]["food_matrix_match"] = True
        estimate["consumed_amount_high_mg"] = "999"
        with self.assertRaises(ValidationError):
            assess_phase3_estimate_uncertainty(estimate)

    def test_phase3_cooked_compound_total_retains_source_supported_interval(self):
        output = calculate_recipe_exposure(recipe(cooked=True, cooked_mass="measured"), FOOD, MAPPINGS, COMPOUNDS,
                                           {"I-1": retention_evidence()})
        summary = assess_phase3_output_uncertainty(output)
        total = summary["compound_totals"][0]
        self.assertEqual(total["uncertainty_status"], "BOUNDED_INTERVAL_CONDITIONAL_ON_RECIPE_INPUTS")
        self.assertEqual(total["supporting_evidence"][0]["evidence_id"], "P2-TEST-1")

    def test_interval_metadata_cannot_claim_mismatched_source_class(self):
        factor = {"name": "x", "value": "1", "unit": "mg", "bounds": {
            "low": "0.5", "high": "1.5", "type": "reported_interval", "source_type": "measured", "source_reference": "source"}}
        with self.assertRaises(ValidationError):
            propagate_product_interval([factor], result_unit="mg")

    def test_explicit_bounds_propagate_without_probability_assumptions(self):
        factors = [{"name": "concentration", "value": "5", "unit": "mg/kg", "bounds": {
            "low": "4", "high": "6", "type": "reported_interval", "source_type": "reported", "source_reference": "paper/table-1"}},
            {"name": "mass", "value": "0.2", "unit": "kg", "bounds": {
            "low": "0.2", "high": "0.2", "type": "measured_interval", "source_type": "measured", "source_reference": "scale-1"}},
            {"name": "fraction", "value": "0.5", "unit": "1", "bounds": {
            "low": "0.5", "high": "0.5", "type": "reported_interval", "source_type": "reported", "source_reference": "recipe-1"}}]
        result = propagate_product_interval(factors, result_unit="mg", estimate_id="E-1")
        self.assertEqual(Decimal(result["amount_low"]), Decimal("0.4"))
        self.assertEqual(Decimal(result["amount_high"]), Decimal("0.6"))
        self.assertFalse(result["distribution_assumed"])
        self.assertFalse(result["correlation_assumed"])

    def test_missing_factor_uncertainty_withholds_total_interval(self):
        factors = [{"name": "concentration", "value": "5", "unit": "mg/kg", "bounds": {
            "low": "4", "high": "6", "type": "reported_interval", "source_type": "reported", "source_reference": "table-1"}},
            {"name": "mass", "value": "0.2", "unit": "kg"}]
        result = assess_uncertainty_availability(factors, result_unit="mg")
        self.assertEqual(result["uncertainty_status"], "PARTIALLY_QUANTIFIABLE")
        self.assertEqual(result["amount_low"], "")
        self.assertEqual(result["amount_high"], "")
        self.assertEqual(result["missing_uncertainty_factors"], ["mass"])

    def test_assumed_scenario_is_not_misrepresented_as_evidence_bound(self):
        factor = {"name": "retention", "value": "0.5", "unit": "fraction", "bounds": {
            "low": "0.2", "high": "0.8", "type": "assumed_scenario", "source_type": "assumed", "source_reference": "user scenario"}}
        result = propagate_product_interval([factor], result_unit="mg")
        self.assertEqual(result["uncertainty_status"], "SCENARIO_ENVELOPE")
        self.assertIn("assumption-dependent", result["interval_kind"])

    def test_interval_sensitivity_is_deterministic_and_ranked(self):
        factors = [{"name": "A", "value": "5", "unit": "1", "bounds": {
            "low": "4", "high": "6", "type": "reported_interval", "source_type": "reported", "source_reference": "A"}},
            {"name": "B", "value": "10", "unit": "1", "bounds": {
            "low": "9", "high": "11", "type": "reported_interval", "source_type": "reported", "source_reference": "B"}}]
        result = rank_interval_sensitivity(factors, result_unit="mg")
        self.assertFalse(result["probabilistic"])
        self.assertEqual(result["results"][0]["factor"], "A")

    def test_recipe_and_meal_outputs_are_summarized_using_phase3_shape(self):
        recipe_output = calculate_recipe_exposure(recipe(), FOOD, MAPPINGS, COMPOUNDS)
        recipe_summary = assess_phase3_output_uncertainty(recipe_output)
        self.assertEqual(recipe_summary["record_type"], "recipe")
        self.assertEqual(recipe_summary["estimate_count"], 1)
        meal = {"meal_id": "M-1", "provenance": {}, "components": [{
            "component_id": "MC-1", "kind": "recipe", "recipe_id": "R-1", "servings_consumed": "1", "consumed_fraction": "0.5"}]}
        meal_output = calculate_meal_exposure(meal, {"R-1": recipe()}, FOOD, MAPPINGS, COMPOUNDS)
        meal_summary = assess_phase3_output_uncertainty(meal_output)
        self.assertEqual(meal_summary["record_type"], "meal")
        self.assertEqual(meal_summary["estimate_count"], 1)


class ValidationFoundationTests(unittest.TestCase):
    def test_independent_hand_calculations_for_mass_and_volume_basis(self):
        self.assertEqual(independent_reference_exposure_mg("5", "mg/kg", "200", "g", "0.5"), Decimal("0.5"))
        self.assertEqual(independent_reference_exposure_mg("10", "mg/L", "250", "mL", "0.4"), Decimal("1.0"))

    def test_independent_hand_check_rejects_implicit_density_or_dimension_mismatch(self):
        with self.assertRaises(ValidationError):
            independent_reference_exposure_mg("5", "mg/kg", "250", "mL")
        with self.assertRaises(ValidationError):
            independent_reference_exposure_mg("5", "mg/L", "200", "g")

    def test_phase3_raw_recipe_arithmetic_verifies_then_detects_tampering(self):
        output = calculate_recipe_exposure(recipe(), FOOD, MAPPINGS, COMPOUNDS)
        estimate = output["ingredient_results"][0]
        check = verify_phase3_ingredient_arithmetic(estimate)
        self.assertEqual(check["status"], "PASS")
        estimate["consumed_amount_low_mg"] = "999"
        check = verify_phase3_ingredient_arithmetic(estimate)
        self.assertEqual(check["status"], "FAIL")

    def test_phase3_cooked_interval_arithmetic_uses_retention_provenance(self):
        output = calculate_recipe_exposure(recipe(cooked=True, cooked_mass="measured"), FOOD, MAPPINGS, COMPOUNDS,
                                           {"I-1": retention_evidence()})
        check = verify_phase3_ingredient_arithmetic(output["ingredient_results"][0])
        self.assertEqual(check["status"], "PASS")
        self.assertEqual(len(check["comparisons"]), 4)

    def test_phase3_beverage_interval_arithmetic_keeps_volume_basis(self):
        beverage = recipe("B-1", cooked=True, quantity="250", unit="mL")
        beverage["ingredients"][0]["cooked_volume"] = {
            "status": "measured", "value": "250", "unit": "mL", "source_reference": "synthetic measured volume"}
        output = calculate_recipe_exposure(beverage, FOOD, MAPPINGS, COMPOUNDS, {"I-1": retention_evidence()})
        check = verify_phase3_ingredient_arithmetic(output["ingredient_results"][0])
        self.assertEqual(check["status"], "PASS")

    def test_phase3_recipe_and_meal_totals_are_recomputed_from_components(self):
        recipe_output = calculate_recipe_exposure(recipe(), FOOD, MAPPINGS, COMPOUNDS)
        self.assertEqual(verify_phase3_aggregate_arithmetic(recipe_output)["status"], "PASS")
        meal = {"meal_id": "M-1", "provenance": {}, "components": [{
            "component_id": "MC-1", "kind": "recipe", "recipe_id": "R-1", "servings_consumed": "2", "consumed_fraction": "0.5"}]}
        meal_output = calculate_meal_exposure(meal, {"R-1": recipe()}, FOOD, MAPPINGS, COMPOUNDS)
        self.assertEqual(verify_phase3_aggregate_arithmetic(meal_output)["status"], "PASS")
        bad = dict(meal_output)
        bad["compound_totals"] = [dict(meal_output["compound_totals"][0], consumed_amount_high_mg="999")]
        self.assertEqual(verify_phase3_aggregate_arithmetic(bad)["status"], "FAIL")

    def test_published_data_comparison_requires_source_and_reference_and_basis_match(self):
        with self.assertRaises(ValidationError):
            compare_to_reference(item_id="E-1", actual="1", reference="1", unit="mg", reference_unit="mg",
                                 measurement_basis="wet weight", reference_basis="wet weight", layer="published_data_comparison")
        mismatch = compare_to_reference(item_id="E-1", actual="1", reference="1", unit="mg", reference_unit="mg",
                                        measurement_basis="wet weight", reference_basis="dry weight",
                                        layer="published_data_comparison", reference_id="T1", source_reference="doi:example")
        self.assertEqual(mismatch["status"], "REJECTED_INCOMPARABLE")

    def test_external_validation_cannot_be_established_by_numeric_pair(self):
        record = compare_to_reference(item_id="E-1", actual="1", reference="1", unit="mg", reference_unit="mg",
                                      measurement_basis="wet weight", reference_basis="wet weight",
                                      layer="external_scientific_validation")
        self.assertEqual(record["status"], "NOT_ESTABLISHED")
        self.assertFalse(record["external_validation_claim"])

    def test_summary_keeps_validation_layers_separate(self):
        records = [
            {"validation_layer": "software_correctness", "status": "PASS"},
            {"validation_layer": "published_data_comparison", "status": "PASS", "absolute_error": "0.2",
             "reference_id": "TABLE-1", "source_reference": "doi:10.1234/example", "unit": "mg/kg", "measurement_basis": "wet weight"},
        ]
        summary = summarize_validation(records)
        self.assertEqual(summary["validation_layers"]["software_correctness"]["PASS"], 1)
        self.assertEqual(summary["validation_layers"]["published_data_comparison"]["PASS"], 1)
        self.assertEqual(summary["published_comparison_metrics"]["n"], 1)
        self.assertEqual(summary["external_scientific_validation"], "NOT_ESTABLISHED")
        self.assertFalse(summary["external_validation_claim"])

    def test_external_validation_pass_cannot_enter_arithmetic_summary(self):
        with self.assertRaises(ValidationError):
            summarize_validation([{"validation_layer": "external_scientific_validation", "status": "PASS"}])


if __name__ == "__main__":
    unittest.main()
