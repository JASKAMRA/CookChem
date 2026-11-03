from __future__ import annotations

import json
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from stage_c.cli import (
    build_parser, command_meal_create, command_meal_validate, command_recipe_add_ingredient,
    command_recipe_create, command_recipe_validate,
)


class RecipeCliTests(unittest.TestCase):
    def test_cli_registers_recipe_and_meal_commands(self):
        parser = build_parser()
        parsed = parser.parse_args(["recipe", "validate", "recipe.json"])
        self.assertEqual(parsed.recipe_command, "validate")
        parsed_meal = parser.parse_args(["meal", "calculate", "meal.json", "--recipes-dir", "recipes"])
        self.assertEqual(parsed_meal.meal_command, "calculate")

    def test_recipe_create_add_ingredient_and_validate_workflow(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            directory = Path(folder)
            recipe_file = directory / "recipe.json"
            recipe_source = json.loads((ROOT / "examples" / "recipe_apples_epicatechin.json").read_text(encoding="utf-8"))
            source = directory / "source.json"
            source.write_text(json.dumps(recipe_source), encoding="utf-8")
            saved = command_recipe_create(Namespace(input=source, output=recipe_file))
            self.assertEqual(saved["status"], "SAVED")
            ingredient = dict(recipe_source["ingredients"][0])
            ingredient["ingredient_id"] = "apple-2"
            ingredient["quantity"] = {"value": "50", "unit": "g", "source_reference": "synthetic CLI fixture"}
            ingredient_file = directory / "ingredient.json"
            ingredient_file.write_text(json.dumps(ingredient), encoding="utf-8")
            result = command_recipe_add_ingredient(Namespace(recipe=recipe_file, ingredient=ingredient_file, output=None))
            self.assertEqual(result["ingredient_count"], 2)
            validation = command_recipe_validate(Namespace(recipe=recipe_file))
            self.assertEqual(validation["status"], "PASS")

    def test_meal_create_and_validate_workflow_resolves_recipe_and_checks_duplicates(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            directory = Path(folder)
            recipe_file = directory / "recipe.json"
            recipe_file.write_text((ROOT / "examples" / "recipe_apples_epicatechin.json").read_text(encoding="utf-8"), encoding="utf-8")
            meal_source = directory / "meal_source.json"
            meal_source.write_text((ROOT / "examples" / "meal_apple_and_cocoa.json").read_text(encoding="utf-8"), encoding="utf-8")
            meal_output = directory / "meal.json"
            result = command_meal_create(Namespace(input=meal_source, output=meal_output, recipes_dir=directory))
            self.assertEqual(result["status"], "SAVED")
            validation = command_meal_validate(Namespace(meal=meal_output, recipes_dir=directory))
            self.assertEqual(validation["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
