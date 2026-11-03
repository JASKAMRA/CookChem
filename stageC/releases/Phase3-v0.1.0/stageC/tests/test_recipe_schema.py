from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from stage_c.recipe_engine import validate_meal, validate_recipe
from test_recipe_engine import recipe

try:
    from jsonschema import Draft202012Validator
except ImportError:
    Draft202012Validator = None


@unittest.skipUnless(Draft202012Validator, "install stageC/requirements-dev.txt for formal Draft 2020-12 validation")
class Draft202012SchemaTests(unittest.TestCase):
    def test_recipe_schema_and_synthetic_recipe(self):
        schema = json.loads((ROOT / "schemas" / "recipe.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(recipe())

    def test_meal_schema_accepts_recipe_and_direct_food_components(self):
        schema = json.loads((ROOT / "schemas" / "meal.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        meal = {"meal_id": "M-SCHEMA", "provenance": {}, "components": [
            {"component_id": "R", "kind": "recipe", "recipe_id": "R-1", "servings_consumed": "1", "consumed_fraction": "1"},
            {"component_id": "F", "kind": "food", "food_record_id": "F-2", "compound_ids": ["C-1"],
             "quantity": {"value": "1", "unit": "g"}, "consumed_fraction": "1"},
        ]}
        self.assertEqual(validate_meal(meal, {"R-1": recipe()}), [])
        Draft202012Validator(schema).validate(meal)

    def test_invalid_fraction_is_rejected_by_schema(self):
        schema = json.loads((ROOT / "schemas" / "recipe.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        invalid = recipe()
        invalid["ingredients"][0]["consumed_fraction"] = "1.5"
        with self.assertRaises(Exception):
            Draft202012Validator(schema).validate(invalid)


if __name__ == "__main__":
    unittest.main()
