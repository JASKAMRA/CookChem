from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST_DEPS = ROOT / ".test-deps"
if TEST_DEPS.exists():
    sys.path.insert(0, str(TEST_DEPS))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from stage_c.exceptions import ValidationError
from stage_c.recipe_engine import calculate_meal_exposure, calculate_recipe_exposure
from stage_c.uncertainty import (
    assess_phase3_estimate_uncertainty,
    assess_phase3_structured_input_uncertainty,
    assess_phase3_uncertainty_coverage,
    build_uncertainty_gap_registry,
    propagate_product_interval,
    rank_additive_interval_sensitivity,
    rank_multi_compound_interval_sensitivity,
)
from test_recipe_engine import COMPOUNDS, FOOD, MAPPINGS, recipe, retention_evidence


class UncertaintyCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads((ROOT / "tests" / "fixtures" / "synthetic_uncertainty_recipe_meal.json").read_text(encoding="utf-8"))
        cls.recipe, cls.retention = cls.build_recipe()
        cls.recipe_output = calculate_recipe_exposure(
            cls.recipe, FOOD, MAPPINGS, COMPOUNDS, cls.retention,
            stage_b_manifest_sha256="a" * 64,
        )
        cls.meal = {
            "meal_id": "M-SYN-UNCERTAINTY-01",
            "provenance": {"fixture": cls.fixture["label"]},
            "components": [{
                "component_id": "MC-SYN-01", "kind": "recipe", "recipe_id": cls.recipe["recipe_id"],
                "servings_consumed": "1", "consumed_fraction": "1",
            }],
        }
        cls.meal_output = calculate_meal_exposure(
            cls.meal, {cls.recipe["recipe_id"]: cls.recipe}, FOOD, MAPPINGS, COMPOUNDS, cls.retention,
            stage_b_manifest_sha256="a" * 64,
        )

    @classmethod
    def build_recipe(cls):
        fixture = json.loads((ROOT / "tests" / "fixtures" / "synthetic_uncertainty_recipe_meal.json").read_text(encoding="utf-8"))
        base = recipe(cooked=True, cooked_mass="measured", quantity=fixture["recipe"]["ingredients"][0]["quantity"])
        base["recipe_id"] = fixture["recipe"]["recipe_id"]
        first = base["ingredients"][0]
        first.update({
            "ingredient_id": fixture["recipe"]["ingredients"][0]["ingredient_id"],
            "food_record_id": fixture["recipe"]["ingredients"][0]["food_record_id"],
            "quantity": {"value": fixture["recipe"]["ingredients"][0]["quantity"], "unit": fixture["recipe"]["ingredients"][0]["quantity_unit"]},
            "serving_fraction": fixture["recipe"]["ingredients"][0]["serving_fraction"],
            "consumed_fraction": fixture["recipe"]["ingredients"][0]["consumed_fraction"],
            "mass_balance": {**first["mass_balance"], "cooked_mass": {"status": "measured", "value": "200", "unit": "g", "source_reference": "SYNTHETIC fixture"}},
        })
        second = copy.deepcopy(first)
        second_config = fixture["recipe"]["ingredients"][1]
        second.update({
            "ingredient_id": second_config["ingredient_id"],
            "food_record_id": second_config["food_record_id"],
            "quantity": {"value": second_config["quantity"], "unit": second_config["quantity_unit"]},
            "serving_fraction": second_config["serving_fraction"],
            "consumed_fraction": second_config["consumed_fraction"],
            "mass_balance": {**second["mass_balance"], "cooked_mass": {"status": "measured", "value": "100", "unit": "g", "source_reference": "SYNTHETIC fixture"}},
        })
        base["ingredients"] = [first, second]
        ev = {}
        for config in fixture["recipe"]["ingredients"]:
            ev[config["ingredient_id"]] = retention_evidence(
                retention_low_percent=config["retention_low_percent"],
                retention_high_percent=config["retention_high_percent"],
                evidence_id=config["evidence_id"],
                source_reference=config["source_reference"],
            )
        return base, ev

    def test_synthetic_recipe_and_meal_uncertainty_propagates_with_coverage(self):
        expected = self.fixture["expected"]
        for row, target in zip(self.recipe_output["ingredient_results"], expected["ingredient_amounts_mg"]):
            self.assertEqual(Decimal(row["consumed_amount_low_mg"]), Decimal(target["low"]))
            self.assertEqual(Decimal(row["consumed_amount_high_mg"]), Decimal(target["high"]))
        for output, level in ((self.recipe_output, "recipe"), (self.meal_output, "meal")):
            total = output["compound_totals"][0]
            self.assertEqual(Decimal(total["consumed_amount_low_mg"]), Decimal(expected[f"{level}_amount_mg"]["low"]))
            self.assertEqual(Decimal(total["consumed_amount_high_mg"]), Decimal(expected[f"{level}_amount_mg"]["high"]))
            coverage = assess_phase3_uncertainty_coverage(output)
            self.assertEqual(coverage["record_type"], level)
            self.assertEqual(coverage["ingredient_estimate_count"], 2)
            dimensions = {row["dimension"]: row for row in coverage["dimensions"]}
            self.assertEqual(dimensions["cooking_retention"]["coverage_status"], "AVAILABLE")
            self.assertEqual(dimensions["cooking_retention"]["supported_count"], 2)
            self.assertEqual(dimensions["food_concentration"]["coverage_status"], "MISSING")
            self.assertEqual(coverage["aggregate_coverage"]["status"], "AVAILABLE")

            estimates = output.get("ingredient_results") or [
                row for component in output.get("component_results", [])
                for row in component.get("ingredient_results", [])
            ]
            assessments = [assess_phase3_estimate_uncertainty(row) for row in estimates]
            sensitivity = rank_additive_interval_sensitivity(assessments, output_id=coverage["output_id"])
            self.assertTrue(sensitivity["aggregate_interval_complete"])
            self.assertEqual(Decimal(sensitivity["amount_low"]), Decimal(expected[f"{level}_amount_mg"]["low"]))
            self.assertEqual(Decimal(sensitivity["amount_high"]), Decimal(expected[f"{level}_amount_mg"]["high"]))
            ingredient_for_estimate = {row["estimate_id"]: row["ingredient_id"] for row in estimates}
            self.assertEqual([ingredient_for_estimate[row["estimate_id"]] for row in sensitivity["ranked_contributors"]],
                             self.fixture["expected"]["sensitivity_rank_by_width"])

    def test_point_input_uncertainty_is_withheld_from_additive_total_and_ranked_separately(self):
        bounded = [assess_phase3_estimate_uncertainty(row) for row in self.recipe_output["ingredient_results"]]
        point_output = calculate_recipe_exposure(recipe(), FOOD, MAPPINGS, COMPOUNDS)
        point = assess_phase3_estimate_uncertainty(point_output["ingredient_results"][0])
        result = rank_additive_interval_sensitivity([*bounded, point])
        self.assertFalse(result["aggregate_interval_complete"])
        self.assertEqual(result["status"], "PARTIAL_INTERVAL_SENSITIVITY_ONLY")
        self.assertEqual((result["amount_low"], result["amount_high"]), ("", ""))
        self.assertEqual(len(result["unavailable_contributors"]), 1)
        self.assertEqual(len(result["ranked_contributors"]), 2)

    def test_mixed_units_and_reversed_bounds_fail_closed(self):
        assessments = [assess_phase3_estimate_uncertainty(row) for row in self.recipe_output["ingredient_results"]]
        wrong_unit = copy.deepcopy(assessments[0])
        wrong_unit["unit"] = "L"
        with self.assertRaisesRegex(ValidationError, "does not match"):
            rank_additive_interval_sensitivity([assessments[1], wrong_unit])
        reversed_bounds = copy.deepcopy(assessments[0])
        reversed_bounds["amount_low"], reversed_bounds["amount_high"] = "2", "1"
        with self.assertRaisesRegex(ValidationError, "reversed"):
            rank_additive_interval_sensitivity([reversed_bounds])
        first_compound = copy.deepcopy(assessments[0])
        second_compound = copy.deepcopy(assessments[1])
        first_compound["compound_id"] = "C-1"
        second_compound["compound_id"] = "C-2"
        with self.assertRaisesRegex(ValidationError, "different compounds"):
            rank_additive_interval_sensitivity([first_compound, second_compound])

    @staticmethod
    def _factor(name, value, unit, low, high):
        return {"name": name, "value": str(value), "unit": unit,
                "bounds": {"low": str(low), "high": str(high), "type": "measured_interval",
                           "source_type": "measured", "source_reference": f"synthetic measurement for {name}"}}

    def test_structured_raw_input_bounds_propagate_and_add_across_recipe_and_meal(self):
        raw = recipe(cooked=False, quantity="200")
        second = copy.deepcopy(raw["ingredients"][0])
        second.update({"ingredient_id": "I-2", "food_record_id": "F-2",
                       "quantity": {"value": "100", "unit": "g"},
                       "serving_fraction": "0.5", "consumed_fraction": "0.5"})
        raw["ingredients"] = [raw["ingredients"][0], second]
        bounds = [
            {"food_concentration": self._factor("food_concentration", "5", "mg/kg", "4", "6"),
             "ingredient_quantity": self._factor("ingredient_quantity", "0.2", "kg", "0.18", "0.22"),
             "serving_fraction": self._factor("serving_fraction", "0.5", "fraction", "0.4", "0.6"),
             "consumed_fraction": self._factor("consumed_fraction", "0.5", "fraction", "0.5", "0.8")},
            {"food_concentration": self._factor("food_concentration", "10", "mg/kg", "8", "12"),
             "ingredient_quantity": self._factor("ingredient_quantity", "0.1", "kg", "0.08", "0.12"),
             "serving_fraction": self._factor("serving_fraction", "0.5", "fraction", "0.4", "0.6"),
             "consumed_fraction": self._factor("consumed_fraction", "0.5", "fraction", "0.4", "0.7")},
        ]
        for ingredient, inputs in zip(raw["ingredients"], bounds):
            ingredient["provenance"]["uncertainty_inputs"] = inputs
        raw["provenance"]["uncertainty_inputs"] = {
            "recipe_level": self._factor("recipe_level", "1", "fraction", "0.9", "1.1")
        }
        recipe_output = calculate_recipe_exposure(raw, FOOD, MAPPINGS, COMPOUNDS, stage_b_manifest_sha256="a" * 64)
        assessments = [assess_phase3_structured_input_uncertainty(row) for row in recipe_output["ingredient_results"]]
        self.assertEqual(Decimal(assessments[0]["amount_low"]), Decimal("0.144"))
        self.assertEqual(Decimal(assessments[0]["amount_high"]), Decimal("0.6336"))
        sensitivity = rank_additive_interval_sensitivity(assessments, output_id=raw["recipe_id"])
        self.assertEqual(Decimal(sensitivity["amount_low"]), Decimal("0.2464"))
        self.assertEqual(Decimal(sensitivity["amount_high"]), Decimal("1.2384"))

        meal = {"meal_id": "M-SYN-RAW-INTERVAL", "provenance": {}, "components": [{
            "component_id": "MC-1", "kind": "recipe", "recipe_id": raw["recipe_id"],
            "servings_consumed": "1", "consumed_fraction": "1",
        }]}
        meal_output = calculate_meal_exposure(meal, {raw["recipe_id"]: raw}, FOOD, MAPPINGS, COMPOUNDS,
                                               stage_b_manifest_sha256="a" * 64)
        meal_rows = meal_output["component_results"][0]["ingredient_results"]
        meal_assessments = [assess_phase3_structured_input_uncertainty(row) for row in meal_rows]
        meal_sensitivity = rank_additive_interval_sensitivity(meal_assessments, output_id=meal["meal_id"])
        self.assertEqual(Decimal(meal_sensitivity["amount_low"]), Decimal("0.2464"))
        self.assertEqual(Decimal(meal_sensitivity["amount_high"]), Decimal("1.2384"))
        meal["provenance"]["uncertainty_inputs"] = {
            "meal_aggregation": self._factor("meal_aggregation", "1", "fraction", "0.9", "1.1")
        }
        meal_output_with_aggregation_bounds = calculate_meal_exposure(
            meal, {raw["recipe_id"]: raw}, FOOD, MAPPINGS, COMPOUNDS,
            stage_b_manifest_sha256="a" * 64)
        meal_coverage = assess_phase3_uncertainty_coverage(meal_output_with_aggregation_bounds)
        meal_dimensions = {row["dimension"]: row for row in meal_coverage["dimensions"]}
        self.assertEqual(meal_dimensions["meal_aggregation"]["coverage_status"], "AVAILABLE")
        coverage = assess_phase3_uncertainty_coverage(recipe_output)
        dimensions = {row["dimension"]: row for row in coverage["dimensions"]}
        self.assertEqual(dimensions["food_concentration"]["coverage_status"], "AVAILABLE")
        self.assertEqual(dimensions["ingredient_quantity"]["supported_count"], 2)
        self.assertEqual(dimensions["serving_fraction"]["coverage_status"], "AVAILABLE")
        self.assertEqual(dimensions["recipe_level"]["coverage_status"], "AVAILABLE")
        self.assertEqual(coverage["aggregate_coverage"]["status"], "AVAILABLE")

    def test_structured_bounds_missing_or_mismatched_points_never_fill_as_zero(self):
        output = calculate_recipe_exposure(recipe(), FOOD, MAPPINGS, COMPOUNDS)
        estimate = output["ingredient_results"][0]
        missing = assess_phase3_structured_input_uncertainty(estimate)
        self.assertEqual(missing["uncertainty_status"], "NOT_QUANTIFIABLE")
        self.assertEqual(missing["amount_low"], "")
        self.assertEqual(missing["amount_high"], "")
        estimate["provenance"]["uncertainty_inputs"] = {
            "food_concentration": self._factor("food_concentration", "4", "mg/kg", "3", "6")
        }
        with self.assertRaisesRegex(ValidationError, "does not match"):
            assess_phase3_structured_input_uncertainty(estimate)

    def test_coverage_and_sensitivity_schemas_validate_positive_and_reject_tampering(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema is not installed; deterministic coverage assertions still run")
        coverage_schema = json.loads((ROOT / "schemas" / "uncertainty_coverage.schema.json").read_text(encoding="utf-8"))
        sensitivity_schema = json.loads((ROOT / "schemas" / "uncertainty_sensitivity.schema.json").read_text(encoding="utf-8"))
        inputs_schema = json.loads((ROOT / "schemas" / "uncertainty_inputs.schema.json").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(coverage_schema)
        jsonschema.Draft202012Validator.check_schema(sensitivity_schema)
        jsonschema.Draft202012Validator.check_schema(inputs_schema)
        coverage = assess_phase3_uncertainty_coverage(self.recipe_output)
        sensitivity = rank_additive_interval_sensitivity(
            [assess_phase3_estimate_uncertainty(row) for row in self.recipe_output["ingredient_results"]],
            output_id=coverage["output_id"],
        )
        jsonschema.validate(coverage, coverage_schema)
        jsonschema.validate(sensitivity, sensitivity_schema)
        broken = copy.deepcopy(sensitivity)
        broken["probabilistic"] = True
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(broken, sensitivity_schema)
        valid_inputs = {"food_concentration": self._factor("food_concentration", "5", "mg/kg", "4", "6")}
        valid_inputs["analytical_variability"] = self._factor("analytical_variability", "0.1", "fraction", "0.05", "0.2")
        valid_inputs["cooking_yield"] = self._factor("cooking_yield", "0.8", "fraction", "0.7", "0.9")
        jsonschema.validate(valid_inputs, inputs_schema)
        broken_inputs = copy.deepcopy(valid_inputs)
        broken_inputs["food_concentration"]["bounds"]["source_reference"] = ""
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(broken_inputs, inputs_schema)

    def test_gap_registry_is_source_linked_and_preserves_missingness_categories(self):
        registry = build_uncertainty_gap_registry([self.recipe_output, self.meal_output])
        self.assertEqual(registry["output_count"], 2)
        dimensions = {row["dimension"]: row for row in registry["dimensions"]}
        for name in ("food_concentration", "analytical_variability", "ingredient_quantity",
                     "cooking_retention", "cooking_yield", "serving_size", "consumed_fraction"):
            self.assertIn(name, dimensions)
        missing = dimensions["analytical_variability"]["gaps"]
        self.assertTrue(missing)
        self.assertEqual(missing[0]["gap_status"], "MISSING")
        self.assertEqual(missing[0]["food_record_id"], "F-1")
        self.assertEqual(missing[0]["compound_id"], "C-1")
        self.assertEqual(missing[0]["food_source_url"], "https://example.invalid/source")
        self.assertFalse(registry["uncertainty_representation"]["probability_distributions_assumed"])
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema is not installed; deterministic registry assertions still run")
        schema = json.loads((ROOT / "schemas" / "uncertainty_gap_registry.schema.json").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(registry, schema)

    def test_three_ingredient_multi_compound_meal_keeps_sensitivity_separate(self):
        fixture = json.loads((ROOT / "tests" / "fixtures" / "synthetic_multicompound_uncertainty_meal.json").read_text(encoding="utf-8"))
        compounds = {**COMPOUNDS, "C-2": {"Compound_ID": "C-2", "Canonical_Name": "Second test compound"}}
        foods = copy.deepcopy(FOOD)
        for spec in fixture["ingredients"]:
            food_id = spec["food_record_id"]
            if food_id not in foods:
                foods[food_id] = {**foods["F-1"], "food_record_id": food_id, "food_name": "Third synthetic food"}
            foods[food_id]["normalized_concentration"] = spec["concentration_mg_kg"]
            foods[food_id]["reported_concentration"] = spec["concentration_mg_kg"]
        mappings = copy.deepcopy(MAPPINGS)
        for spec in fixture["ingredients"]:
            for compound_id in spec["compound_ids"]:
                if any(row["food_record_id"] == spec["food_record_id"] and row["compound_id"] == compound_id for row in mappings):
                    continue
                mappings.append({"mapping_id": f"MAP-SYN-{spec['ingredient_id']}-{compound_id}",
                                 "food_record_id": spec["food_record_id"], "compound_id": compound_id,
                                 "mapping_status": "Exact identity match", "rationale": "synthetic fixture"})
        base_recipe = recipe(cooked=False, quantity="100")
        raw = {**base_recipe, "recipe_id": fixture["recipe_id"]}
        ingredients = []
        fractions = fixture["fractions"]
        for spec in fixture["ingredients"]:
            item = copy.deepcopy(base_recipe["ingredients"][0])
            item.update({"ingredient_id": spec["ingredient_id"], "food_record_id": spec["food_record_id"],
                         "compound_ids": spec["compound_ids"],
                         "quantity": {"value": spec["quantity_g"], "unit": "g"},
                         "serving_fraction": fractions["serving_fraction"],
                         "consumed_fraction": fractions["consumed_fraction"]})
            ingredients.append(item)
        for item in ingredients:
            spec = next(row for row in fixture["ingredients"] if row["ingredient_id"] == item["ingredient_id"])
            item["provenance"]["uncertainty_inputs"] = {
                "food_concentration": self._factor("food_concentration", spec["concentration_mg_kg"], "mg/kg",
                                                    spec["concentration_low"], spec["concentration_high"]),
                "ingredient_quantity": self._factor("ingredient_quantity", str(Decimal(spec["quantity_g"]) / Decimal(1000)), "kg",
                                                     str(Decimal(spec["quantity_g"]) / Decimal(1000) * Decimal("0.9")),
                                                     str(Decimal(spec["quantity_g"]) / Decimal(1000) * Decimal("1.1"))),
                "serving_fraction": self._factor("serving_fraction", fractions["serving_fraction"], "fraction",
                                                  fractions["serving_fraction_low"], fractions["serving_fraction_high"]),
                "consumed_fraction": self._factor("consumed_fraction", fractions["consumed_fraction"], "fraction",
                                                   fractions["consumed_fraction_low"], fractions["consumed_fraction_high"]),
            }
        raw["ingredients"] = ingredients
        recipe_result = calculate_recipe_exposure(raw, foods, mappings, compounds, stage_b_manifest_sha256="a" * 64)
        meal = {"meal_id": fixture["meal_id"], "provenance": {}, "components": [{
            "component_id": "MC-1", "kind": "recipe", "recipe_id": raw["recipe_id"],
            "servings_consumed": "1", "consumed_fraction": "1",
        }]}
        meal_result = calculate_meal_exposure(meal, {raw["recipe_id"]: raw}, foods, mappings, compounds,
                                               stage_b_manifest_sha256="a" * 64)
        meal_estimates = meal_result["component_results"][0]["ingredient_results"]
        assessments = [assess_phase3_structured_input_uncertainty(row) for row in meal_estimates]
        report = rank_multi_compound_interval_sensitivity(assessments, output_id=meal["meal_id"])
        by_compound = {row["compound_id"]: row["analysis"] for row in report["compound_reports"]}
        self.assertEqual(set(by_compound), {"C-1", "C-2"})
        self.assertEqual(by_compound["C-1"]["supported_contributor_count"], 2)
        self.assertEqual(by_compound["C-2"]["supported_contributor_count"], 2)
        self.assertTrue(all(row["analysis"]["aggregate_interval_complete"] for row in report["compound_reports"]))
        recipe_points = {row["compound_id"]: row["consumed_amount_low_mg"] for row in recipe_result["compound_totals"]}
        self.assertEqual({key: Decimal(value) for key, value in recipe_points.items()},
                         {key: Decimal(value["point_mg"]) for key, value in fixture["expected"].items()})
        estimate_ingredients = {row["estimate_id"]: row["ingredient_id"] for row in meal_estimates}
        for compound_id, expected in fixture["expected"].items():
            ranked_ingredients = [estimate_ingredients[row["estimate_id"]]
                                  for row in by_compound[compound_id]["ranked_contributors"]]
            self.assertEqual(sorted(ranked_ingredients), sorted(expected["ingredient_ids"]))
            self.assertEqual(Decimal(by_compound[compound_id]["amount_low"]), Decimal(expected["low_mg"]))
            self.assertEqual(Decimal(by_compound[compound_id]["amount_high"]), Decimal(expected["high_mg"]))
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema is not installed; deterministic sensitivity assertions still run")
        schema = json.loads((ROOT / "schemas" / "multi_compound_sensitivity.schema.json").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(report, schema)

    def test_multi_compound_sensitivity_rejects_missing_compound_identity(self):
        estimate = assess_phase3_estimate_uncertainty(self.recipe_output["ingredient_results"][0])
        estimate.pop("compound_id")
        with self.assertRaisesRegex(ValidationError, "lacks compound_id"):
            rank_multi_compound_interval_sensitivity([estimate])
        with self.assertRaisesRegex(ValidationError, "requires compound_id"):
            rank_additive_interval_sensitivity([estimate])

    def test_gap_registry_builder_cli_reads_phase3_json_and_writes_report(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            input_path = Path(folder) / "phase3_output.json"
            output_path = Path(folder) / "uncertainty_gaps.json"
            input_path.write_text(json.dumps(self.recipe_output), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_uncertainty_gap_registry.py"),
                 str(input_path), "--output", str(output_path)],
                cwd=ROOT.parent, capture_output=True, text=True, check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            registry = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(registry["output_count"], 1)
            self.assertEqual(registry["outputs"][0]["output_id"], self.recipe["recipe_id"])

    def test_duplicate_ingredients_remain_distinct_source_linked_gaps(self):
        raw = recipe(cooked=False, quantity="100")
        duplicate = copy.deepcopy(raw["ingredients"][0])
        duplicate["ingredient_id"] = "I-DUPLICATE-02"
        raw["ingredients"].append(duplicate)
        output = calculate_recipe_exposure(raw, FOOD, MAPPINGS, COMPOUNDS, stage_b_manifest_sha256="a" * 64)
        self.assertEqual(len(output["ingredient_results"]), 2)
        self.assertNotEqual(output["ingredient_results"][0]["estimate_id"], output["ingredient_results"][1]["estimate_id"])
        coverage = assess_phase3_uncertainty_coverage(output)
        quantity = next(row for row in coverage["dimensions"] if row["dimension"] == "ingredient_quantity")
        self.assertEqual(quantity["missing_count"], 2)
        self.assertEqual({row["ingredient_id"] for row in quantity["missing_records"]}, {"I-1", "I-DUPLICATE-02"})

    def test_zero_quantity_factor_propagates_zero_without_turning_missing_into_zero(self):
        result = propagate_product_interval([
            self._factor("ingredient_quantity", "0", "kg", "0", "0"),
            self._factor("food_concentration", "5", "mg/kg", "4", "6"),
        ], result_unit="mg", estimate_id="SYN-ZERO-01")
        self.assertEqual(result["uncertainty_status"], "BOUNDED_INTERVAL")
        self.assertEqual((result["amount_low"], result["amount_high"]), ("0", "0"))
        self.assertFalse(result["distribution_assumed"])


if __name__ == "__main__":
    unittest.main()
