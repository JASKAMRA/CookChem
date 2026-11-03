from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from stage_c.recipe_engine import validate_meal, validate_recipe
from test_recipe_engine import recipe


def load_schema(name: str) -> dict:
    return json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))


def valid_meal() -> dict:
    return {
        "meal_id": "M-SCHEMA",
        "provenance": {},
        "components": [
            {"component_id": "R", "kind": "recipe", "recipe_id": "R-1",
             "servings_consumed": "1", "consumed_fraction": "1"},
            {"component_id": "F", "kind": "food", "food_record_id": "F-2", "compound_ids": ["C-1"],
             "quantity": {"value": "1", "unit": "g"}, "consumed_fraction": "1"},
        ],
    }


class Draft202012SchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.recipe_schema = load_schema("recipe.schema.json")
        cls.meal_schema = load_schema("meal.schema.json")
        for schema in (cls.recipe_schema, cls.meal_schema):
            Draft202012Validator.check_schema(schema)
        cls.current_schema_paths = sorted((ROOT / "schemas").glob("*.schema.json")) + sorted((ROOT / "phase4" / "schemas").glob("*.schema.json"))
        cls.recipe_validator = Draft202012Validator(cls.recipe_schema)
        cls.meal_validator = Draft202012Validator(cls.meal_schema)

    def assert_schema_valid(self, validator, instance):
        validator.validate(instance)

    def assert_schema_invalid(self, validator, instance):
        with self.assertRaises(ValidationError):
            validator.validate(instance)

    def test_both_schemas_are_draft_2020_12_and_their_nested_refs_resolve(self):
        self.assertEqual(self.recipe_schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(self.meal_schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        Draft202012Validator.check_schema(self.recipe_schema)
        Draft202012Validator.check_schema(self.meal_schema)
        self.assert_schema_valid(self.recipe_validator, recipe())
        self.assert_schema_valid(self.meal_validator, valid_meal())

    def test_every_current_stage_c_schema_passes_draft_2020_12_meta_validation(self):
        self.assertEqual(len(self.current_schema_paths), 7)
        for path in self.current_schema_paths:
            with self.subTest(schema=path.relative_to(ROOT).as_posix()):
                schema = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
                Draft202012Validator.check_schema(schema)

    def test_positive_recipe_fixture_passes_schema_and_semantic_validator(self):
        candidate = recipe()
        self.assert_schema_valid(self.recipe_validator, candidate)
        self.assertEqual(validate_recipe(candidate), [])

    def test_positive_mixed_meal_fixture_passes_schema_and_semantic_validator(self):
        candidate = valid_meal()
        self.assert_schema_valid(self.meal_validator, candidate)
        self.assertEqual(validate_meal(candidate, {"R-1": recipe()}), [])

    def test_recipe_required_fields_and_types_are_enforced(self):
        missing = recipe()
        del missing["name"]
        self.assert_schema_invalid(self.recipe_validator, missing)
        wrong_type = recipe()
        wrong_type["name"] = ["not", "a", "string"]
        self.assert_schema_invalid(self.recipe_validator, wrong_type)
        self.assertTrue(validate_recipe(wrong_type))

    def test_recipe_nested_constraints_cover_refs_units_and_measurement_states(self):
        bad_unit = recipe()
        bad_unit["ingredients"][0]["quantity"]["unit"] = "cup"
        self.assert_schema_invalid(self.recipe_validator, bad_unit)
        bad_measurement = recipe()
        bad_measurement["mass_balance"]["cooked_mass"] = {"status": "measured", "value": "4", "unit": "g"}
        self.assert_schema_invalid(self.recipe_validator, bad_measurement)
        contradictory_measurement = recipe()
        contradictory_measurement["mass_balance"]["cooked_mass"] = {"status": "not_reported", "value": "0"}
        self.assert_schema_invalid(self.recipe_validator, contradictory_measurement)

    def test_fraction_bounds_apply_to_numbers_and_numeric_strings(self):
        for invalid_value in (1.01, "1.01", "1.5", "-0.1", "abc"):
            with self.subTest(value=invalid_value):
                candidate = copy.deepcopy(recipe())
                candidate["ingredients"][0]["consumed_fraction"] = invalid_value
                self.assert_schema_invalid(self.recipe_validator, candidate)
        for valid_value in (0, 1, 0.25, "0", "0.25", "1", "1.000"):
            with self.subTest(value=valid_value):
                candidate = copy.deepcopy(recipe())
                candidate["ingredients"][0]["consumed_fraction"] = valid_value
                self.assert_schema_valid(self.recipe_validator, candidate)

    def test_quantity_density_and_count_reject_negative_or_zero_string_values_as_applicable(self):
        for invalid_value in ("-1", "abc"):
            candidate = copy.deepcopy(recipe())
            candidate["ingredients"][0]["quantity"]["value"] = invalid_value
            self.assert_schema_invalid(self.recipe_validator, candidate)
        zero_count = copy.deepcopy(recipe())
        zero_count["servings_count"]["value"] = "0.0"
        self.assert_schema_invalid(self.recipe_validator, zero_count)
        bad_density = copy.deepcopy(recipe())
        bad_density["ingredients"][0]["density"] = {
            "kg_per_l": "0", "verification_status": "Verified", "source_reference": "fixture"
        }
        self.assert_schema_invalid(self.recipe_validator, bad_density)

    def test_meal_component_one_of_and_component_references_are_enforced(self):
        missing_component_field = valid_meal()
        del missing_component_field["components"][0]["recipe_id"]
        self.assert_schema_invalid(self.meal_validator, missing_component_field)
        invalid_kind = valid_meal()
        invalid_kind["components"][0]["kind"] = "unknown"
        self.assert_schema_invalid(self.meal_validator, invalid_kind)
        invalid_fraction = valid_meal()
        invalid_fraction["components"][0]["consumed_fraction"] = "1.2"
        self.assert_schema_invalid(self.meal_validator, invalid_fraction)
        unresolved_recipe = valid_meal()
        self.assert_schema_valid(self.meal_validator, unresolved_recipe)
        self.assertTrue(validate_meal(unresolved_recipe, {}))

    def test_meal_food_quantity_and_duplicate_compound_ids_are_constrained(self):
        invalid_food = valid_meal()
        invalid_food["components"][1]["quantity"]["unit"] = "serving"
        self.assert_schema_invalid(self.meal_validator, invalid_food)
        duplicate_compounds = valid_meal()
        duplicate_compounds["components"][1]["compound_ids"] = ["C-1", "C-1"]
        self.assert_schema_invalid(self.meal_validator, duplicate_compounds)


if __name__ == "__main__":
    unittest.main()
