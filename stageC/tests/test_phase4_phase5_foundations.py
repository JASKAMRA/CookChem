from __future__ import annotations

import copy
import json
import sys
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
TEST_DEPS = ROOT / ".test-deps"
if TEST_DEPS.exists():
    sys.path.insert(0, str(TEST_DEPS))
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
        self.assertEqual({row["code"] for row in result["missing_uncertainty_reasons"]}, {
            "NO_ANALYTICAL_UNCERTAINTY", "NO_QUANTITY_UNCERTAINTY", "NO_FRACTION_UNCERTAINTY"})

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

    def test_phase3_interval_boundaries_accept_zero_and_full_retention(self):
        evidence = retention_evidence(retention_low_percent="0", retention_high_percent="100")
        output = calculate_recipe_exposure(recipe(cooked=True, cooked_mass="measured"), FOOD, MAPPINGS, COMPOUNDS,
                                           {"I-1": evidence})
        result = assess_phase3_estimate_uncertainty(output["ingredient_results"][0])
        self.assertEqual(Decimal(result["amount_low"]), Decimal(0))
        self.assertEqual(Decimal(result["amount_high"]), Decimal("0.25"))
        self.assertEqual(result["uncertainty_status"], "BOUNDED_INTERVAL_CONDITIONAL_ON_RECIPE_INPUTS")

    def test_tampered_phase3_retention_endpoint_is_rejected(self):
        output = calculate_recipe_exposure(recipe(cooked=True, cooked_mass="measured"), FOOD, MAPPINGS, COMPOUNDS,
                                           {"I-1": retention_evidence()})
        estimate = output["ingredient_results"][0]
        estimate["provenance"]["retention_evidence"]["retention_high_percent"] = "101"
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

    def test_multi_ingredient_retention_intervals_aggregate_endpoints(self):
        cooked_recipe = recipe(cooked=True, cooked_mass="measured")
        second = copy.deepcopy(cooked_recipe["ingredients"][0])
        second.update(ingredient_id="I-2", quantity={"value": "100", "unit": "g"})
        second["mass_balance"]["cooked_mass"].update(value="100")
        cooked_recipe["ingredients"].append(second)
        output = calculate_recipe_exposure(cooked_recipe, FOOD, MAPPINGS, COMPOUNDS,
                                           {"I-1": retention_evidence(), "I-2": retention_evidence()})
        total = output["compound_totals"][0]
        self.assertEqual(Decimal(total["consumed_amount_low_mg"]), Decimal("0.150"))
        self.assertEqual(Decimal(total["consumed_amount_high_mg"]), Decimal("0.225"))
        self.assertEqual(verify_phase3_aggregate_arithmetic(output)["status"], "PASS")
        self.assertEqual(assess_phase3_output_uncertainty(output)["compound_totals"][0]["uncertainty_status"],
                         "BOUNDED_INTERVAL_CONDITIONAL_ON_RECIPE_INPUTS")

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
        self.assertEqual(result["missing_uncertainty_reasons"][0]["code"], "NO_SUPPORTED_BOUNDS")
        self.assertEqual(result["missing_uncertainty_reasons"][0]["factor"], "mass")

    def test_nonnegative_interval_boundary_with_zero_is_valid(self):
        factor = {"name": "zero-capable", "value": "0", "unit": "mg", "bounds": {
            "low": "0", "high": "0", "type": "measured_interval", "source_type": "measured", "source_reference": "synthetic-zero"}}
        result = propagate_product_interval([factor], result_unit="mg")
        self.assertEqual(result["amount_low"], "0")
        self.assertEqual(result["amount_high"], "0")

    def test_reversed_or_point_excluding_bounds_are_rejected(self):
        reversed_bounds = {"name": "x", "value": "1", "unit": "mg", "bounds": {
            "low": "2", "high": "0", "type": "reported_interval", "source_type": "reported", "source_reference": "synthetic"}}
        excluded_point = {"name": "x", "value": "3", "unit": "mg", "bounds": {
            "low": "0", "high": "2", "type": "reported_interval", "source_type": "reported", "source_reference": "synthetic"}}
        with self.assertRaises(ValidationError):
            propagate_product_interval([reversed_bounds], result_unit="mg")
        with self.assertRaises(ValidationError):
            propagate_product_interval([excluded_point], result_unit="mg")

    def test_assumed_scenario_is_not_misrepresented_as_evidence_bound(self):
        factor = {"name": "retention", "value": "0.5", "unit": "fraction", "bounds": {
            "low": "0.2", "high": "0.8", "type": "assumed_scenario", "source_type": "assumed", "source_reference": "user scenario"}}
        result = propagate_product_interval([factor], result_unit="mg")
        self.assertEqual(result["uncertainty_status"], "SCENARIO_ENVELOPE")
        self.assertIn("assumption-dependent", result["interval_kind"])

    def test_reported_measured_literature_scenario_and_model_prediction_bounds_stay_distinct(self):
        factor_specs = [
            ("source_reported_range", "reported", "primary source table", ""),
            ("analytical_measurement_variability", "measured", "assay replicate record", ""),
            ("literature_derived_range", "literature", "systematic literature source", "reported study bounds"),
            ("scenario_bound", "assumed", "SYNTHETIC scenario input", ""),
            ("model_prediction_uncertainty", "model_prediction", "SYNTHETIC model output", "documented model interval method"),
        ]
        factors = []
        for index, (bound_type, source_type, source_reference, method) in enumerate(factor_specs):
            bounds = {
                "low": "0.4", "high": "0.6", "type": bound_type,
                "source_type": source_type, "source_reference": source_reference,
            }
            if method:
                bounds["method"] = method
            if source_type == "model_prediction":
                bounds.update({
                    "model_artifact_sha256": "a" * 64,
                    "target_contract_sha256": "b" * 64,
                    "prediction_reference": "SYN-PRED-001",
                })
            factors.append({"name": f"factor-{index}", "value": "0.5", "unit": "1", "bounds": bounds})

        result = propagate_product_interval(factors, result_unit="mg")
        output_metadata = result["factors"]
        self.assertEqual([row["type"] for row in output_metadata], [spec[0] for spec in factor_specs])
        self.assertEqual([row["source_type"] for row in output_metadata], [spec[1] for spec in factor_specs])
        model_row = output_metadata[-1]
        self.assertEqual(model_row["prediction_reference"], "SYN-PRED-001")
        self.assertEqual(model_row["target_contract_sha256"], "b" * 64)
        self.assertFalse(result["distribution_assumed"])

        schema = json.loads((REPO_ROOT / "stageC" / "schemas" / "uncertainty_assessment.schema.json").read_text(encoding="utf-8"))
        try:
            import jsonschema
        except ImportError:
            return
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(result, schema)
        tampered = copy.deepcopy(result)
        tampered["factors"][-1]["model_artifact_sha256"] = "unverified"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(tampered, schema)

    def test_model_prediction_interval_requires_artifact_target_and_output_provenance(self):
        base = {"name": "prediction", "value": "0.5", "unit": "fraction", "bounds": {
            "low": "0.4", "high": "0.6", "type": "model_prediction_uncertainty",
            "source_type": "model_prediction", "source_reference": "synthetic prediction package",
            "method": "synthetic interval method", "target_contract_sha256": "b" * 64,
            "prediction_reference": "SYN-PRED-001"}}
        with self.assertRaisesRegex(ValidationError, "model_artifact_sha256"):
            propagate_product_interval([base], result_unit="mg")
        base["bounds"]["model_artifact_sha256"] = "not-a-hash"
        with self.assertRaisesRegex(ValidationError, "model_artifact_sha256"):
            propagate_product_interval([base], result_unit="mg")

    def test_interval_sensitivity_is_deterministic_and_ranked(self):
        factors = [{"name": "A", "value": "5", "unit": "1", "bounds": {
            "low": "4", "high": "6", "type": "reported_interval", "source_type": "reported", "source_reference": "A"}},
            {"name": "B", "value": "10", "unit": "1", "bounds": {
            "low": "9", "high": "11", "type": "reported_interval", "source_type": "reported", "source_reference": "B"}}]
        result = rank_interval_sensitivity(factors, result_unit="mg")
        self.assertFalse(result["probabilistic"])
        self.assertEqual(result["results"][0]["factor"], "A")

    def test_synthetic_benchmark_fixture_is_explicit_and_arithmetic_is_deterministic(self):
        fixture_path = ROOT / "tests" / "fixtures" / "synthetic_validation_benchmark.json"
        schema_path = REPO_ROOT / "stageC" / "schemas" / "synthetic_validation_benchmark.schema.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.assertEqual(fixture["label"], "SYNTHETIC — TEST FIXTURE ONLY")
        self.assertEqual(fixture["scientific_validation_claim"], "NONE")
        self.assertTrue(fixture["not_real_world_evidence"])
        self.assertTrue(fixture["not_for_published_data_comparison"])
        self.assertTrue(fixture["not_for_external_validation"])
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(len(fixture["records"]), 3)
        self.assertEqual(schema["properties"]["label"]["const"], fixture["label"])
        try:
            import jsonschema
        except ImportError:
            self.assertEqual(schema["properties"]["scientific_validation_claim"]["const"], "NONE")
        else:
            jsonschema.Draft202012Validator.check_schema(schema)
            jsonschema.validate(fixture, schema)
            with self.assertRaises(jsonschema.ValidationError):
                jsonschema.validate({**fixture, "label": "PUBLISHED BENCHMARK"}, schema)
            with self.assertRaises(jsonschema.ValidationError):
                jsonschema.validate({**fixture, "external_validation_protocol": "example"}, schema)
        for row in fixture["records"][:2]:
            inputs = row["inputs"]
            amount = independent_reference_exposure_mg(inputs["concentration"], inputs["concentration_unit"],
                                                       inputs["quantity"], inputs["quantity_unit"], inputs["consumed_fraction"])
            self.assertEqual(amount, Decimal(row["expected_output"]["amount_mg"]))
        interval = fixture["records"][2]
        data = interval["inputs"]
        expected = interval["expected_output"]
        low_concentration = Decimal(data["concentration"]) * Decimal(data["retention_low_percent"]) / Decimal(100)
        high_concentration = Decimal(data["concentration"]) * Decimal(data["retention_high_percent"]) / Decimal(100)
        low_amount = low_concentration * Decimal(data["cooked_portion_quantity"]) * Decimal(data["consumed_fraction"])
        high_amount = high_concentration * Decimal(data["cooked_portion_quantity"]) * Decimal(data["consumed_fraction"])
        self.assertEqual(low_concentration, Decimal(expected["cooked_concentration_low"]))
        self.assertEqual(high_concentration, Decimal(expected["cooked_concentration_high"]))
        self.assertEqual(low_amount, Decimal(expected["amount_low_mg"]))
        self.assertEqual(high_amount, Decimal(expected["amount_high_mg"]))

    def test_uncertainty_schema_documents_machine_readable_gaps(self):
        schema_path = REPO_ROOT / "stageC" / "schemas" / "uncertainty_assessment.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        reason = schema["$defs"]["missingReason"]
        self.assertEqual(reason["required"], ["code", "factor", "reason"])
        self.assertIn("NO_ANALYTICAL_UNCERTAINTY", reason["properties"]["code"]["enum"])
        try:
            import jsonschema
        except ImportError:
            return
        jsonschema.Draft202012Validator.check_schema(schema)
        point_output = calculate_recipe_exposure(recipe(), FOOD, MAPPINGS, COMPOUNDS)
        assessment = assess_phase3_estimate_uncertainty(point_output["ingredient_results"][0])
        jsonschema.validate(assessment, schema)
        bad_reason = copy.deepcopy(assessment)
        bad_reason["missing_uncertainty_reasons"][0]["code"] = "ASSUMED_ZERO_UNCERTAINTY"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(bad_reason, schema)
        cooked_output = calculate_recipe_exposure(recipe(cooked=True, cooked_mass="measured"), FOOD, MAPPINGS, COMPOUNDS,
                                                  {"I-1": retention_evidence()})
        bounded = assess_phase3_estimate_uncertainty(cooked_output["ingredient_results"][0])
        jsonschema.validate(bounded, schema)
        jsonschema.validate(assess_phase3_output_uncertainty(cooked_output)["compound_totals"][0], schema)
        partial = assess_uncertainty_availability([{"name": "measured factor", "value": "2", "unit": "mg"}], result_unit="mg")
        jsonschema.validate(partial, schema)
        scenario_factor = {"name": "scenario", "value": "0.5", "unit": "fraction", "bounds": {
            "low": "0.2", "high": "0.8", "type": "assumed_scenario", "source_type": "assumed", "source_reference": "synthetic test"}}
        jsonschema.validate(propagate_product_interval([scenario_factor], result_unit="mg"), schema)
        incomplete_output = calculate_recipe_exposure(recipe(cooked=True), FOOD, MAPPINGS, COMPOUNDS)
        incomplete = assess_phase3_estimate_uncertainty(incomplete_output["ingredient_results"][0])
        jsonschema.validate(incomplete, schema)

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
        self.assertEqual(independent_reference_exposure_mg("5", "mg/kg", "200", "g", "0"), Decimal(0))
        self.assertEqual(independent_reference_exposure_mg("5", "mg/kg", "200", "g", "1"), Decimal(1))

    def test_hand_check_supported_concentration_unit_families(self):
        self.assertEqual(independent_reference_exposure_mg("1", "mg/g", "10", "g"), Decimal("10"))
        self.assertEqual(independent_reference_exposure_mg("100", "µg/100 g", "100", "g"), Decimal("0.1"))
        self.assertEqual(independent_reference_exposure_mg("1", "mg/mL", "250", "mL"), Decimal("250"))
        self.assertEqual(independent_reference_exposure_mg("1", "µg/mL", "250", "mL"), Decimal("0.25"))

    def test_hand_check_rejects_unknown_units_and_invalid_fraction_boundaries(self):
        with self.assertRaises(ValidationError):
            independent_reference_exposure_mg("1", "g/kg", "100", "g")
        with self.assertRaises(ValidationError):
            independent_reference_exposure_mg("1", "mg/kg", "100", "g", "1.01")
        with self.assertRaises(ValidationError):
            independent_reference_exposure_mg("-1", "mg/kg", "100", "g")
        with self.assertRaises(ValidationError):
            independent_reference_exposure_mg("NaN", "mg/kg", "100", "g")

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
        self.assertEqual(len(check["comparisons"]), 7)

    def test_cooked_arithmetic_check_detects_concentration_and_gate_tampering(self):
        output = calculate_recipe_exposure(recipe(cooked=True, cooked_mass="measured"), FOOD, MAPPINGS, COMPOUNDS,
                                           {"I-1": retention_evidence()})
        estimate = output["ingredient_results"][0]
        estimate["cooked_concentration_high"] = "9"
        self.assertEqual(verify_phase3_ingredient_arithmetic(estimate)["status"], "FAIL")
        estimate = calculate_recipe_exposure(recipe(cooked=True, cooked_mass="measured"), FOOD, MAPPINGS, COMPOUNDS,
                                             {"I-1": retention_evidence()})["ingredient_results"][0]
        estimate["provenance"]["retention_evidence"]["compatibility_gates"]["exact_compound_match"] = False
        self.assertEqual(verify_phase3_ingredient_arithmetic(estimate)["status"], "FAIL")

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

    def test_aggregate_interval_bounds_and_raw_reference_tampering_are_detected(self):
        cooked = calculate_recipe_exposure(recipe(cooked=True, cooked_mass="measured"), FOOD, MAPPINGS, COMPOUNDS,
                                           {"I-1": retention_evidence()})
        cooked["compound_totals"][0]["consumed_amount_low_mg"] = "0.11"
        self.assertEqual(verify_phase3_aggregate_arithmetic(cooked)["status"], "FAIL")
        cooked = calculate_recipe_exposure(recipe(cooked=True, cooked_mass="measured"), FOOD, MAPPINGS, COMPOUNDS,
                                           {"I-1": retention_evidence()})
        cooked["raw_reference_totals"][0]["raw_reference_amount_mg"] = "999"
        self.assertEqual(verify_phase3_aggregate_arithmetic(cooked)["status"], "FAIL")
        cooked = calculate_recipe_exposure(recipe(), FOOD, MAPPINGS, COMPOUNDS)
        cooked["compound_totals"][0]["input_estimate_ids"] = []
        self.assertEqual(verify_phase3_aggregate_arithmetic(cooked)["status"], "FAIL")
        cooked = calculate_recipe_exposure(recipe(), FOOD, MAPPINGS, COMPOUNDS)
        cooked["compound_totals"].append(dict(cooked["compound_totals"][0], compound_id="ORPHAN"))
        self.assertEqual(verify_phase3_aggregate_arithmetic(cooked)["status"], "FAIL")

    def test_incomplete_component_must_block_aggregate_amount(self):
        output = calculate_recipe_exposure(recipe(cooked=True), FOOD, MAPPINGS, COMPOUNDS,
                                           {"I-1": retention_evidence()})
        self.assertEqual(output["compound_totals"][0]["calculation_status"], "Incomplete: one or more components unresolved")
        self.assertEqual(verify_phase3_aggregate_arithmetic(output)["status"], "PASS")
        uncertainty = assess_phase3_output_uncertainty(output)
        self.assertEqual(uncertainty["estimates"][0]["uncertainty_status"], "NOT_QUANTIFIABLE")
        self.assertEqual(uncertainty["estimates"][0]["missing_uncertainty_reasons"][0]["code"], "PHASE3_ESTIMATE_INCOMPLETE")
        self.assertEqual(uncertainty["compound_totals"][0]["missing_uncertainty_reasons"][0]["code"], "PHASE3_TOTAL_INCOMPLETE")

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
