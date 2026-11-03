from __future__ import annotations

import json
import sys
import tempfile
import unittest
from argparse import Namespace
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from stage_c.cli import command_recipe_calculate
from stage_c.recipe_engine import calculate_meal_exposure, calculate_recipe_exposure, load_recipe
from stage_c.release_adapters import load_phase1b_v131_inputs, load_phase2_v030_evidence, load_phase4_context_evidence


class PinnedReleaseIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.foods, cls.mappings, cls.compounds, cls.phase1b = load_phase1b_v131_inputs()
        cls.phase2_evidence, cls.phase2 = load_phase2_v030_evidence()
        cls.phase4_context, cls.phase4 = load_phase4_context_evidence()
        cls.recipe = load_recipe(ROOT / "examples" / "recipe_apples_epicatechin.json")
        cls.meal = json.loads((ROOT / "examples" / "meal_apple_and_cocoa.json").read_text(encoding="utf-8"))

    def test_recipe_example_uses_immutable_release_records_and_reproducible_amount(self):
        result = calculate_recipe_exposure(self.recipe, self.foods, self.mappings, self.compounds,
                                           self.phase2_evidence,
                                           stage_b_manifest_sha256=self.phase1b["stage_b_manifest_sha256"],
                                           phase2_release_metadata=self.phase2)
        self.assertEqual(Decimal(result["ingredient_results"][0]["consumed_amount_low_mg"]), Decimal("11.29500"))
        self.assertEqual(result["provenance"]["phase2_release"], "Phase2-v0.3.1")
        self.assertEqual(result["provenance"]["phase2_manifest_sha256"], "2b72e4df095002952fcf2eef2af3381425384317d6ea259b81676ed8c243746e")
        self.assertEqual(result["raw_reference_totals"][0]["calculation_status"], "Complete")

    def test_mixed_meal_example_aggregates_recipe_and_direct_food(self):
        result = calculate_meal_exposure(self.meal, {self.recipe["recipe_id"]: self.recipe}, self.foods,
                                         self.mappings, self.compounds, self.phase2_evidence,
                                         stage_b_manifest_sha256=self.phase1b["stage_b_manifest_sha256"],
                                         phase2_release_metadata=self.phase2)
        self.assertEqual(Decimal(result["compound_totals"][0]["consumed_amount_low_mg"]), Decimal("21.11650"))
        self.assertEqual(len(result["component_results"]), 2)

    def test_cli_writes_calculation_with_pinned_provenance(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            output = Path(folder) / "recipe_result.json"
            status = command_recipe_calculate(Namespace(recipe=ROOT / "examples" / "recipe_apples_epicatechin.json", output=output))
            saved = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(status["complete_estimates"], 1)
            self.assertEqual(saved["upstream_releases"]["phase1b"]["release_id"], "Phase1B-v1.3.2")
            self.assertEqual(saved["upstream_releases"]["phase4"]["release_id"], "Phase4-v0.1.2")
            self.assertEqual(saved["phase4_context_records"], [])
            self.assertEqual(saved["ingredient_results"][0]["provenance"]["food_source_title"], "USDA Database for the Flavonoid Content of Selected Foods, Release 3.3")

    def test_pinned_phase2_layer_has_no_quantitative_cooking_factors_to_apply(self):
        self.assertEqual(self.phase2["numeric_records"], 0)
        self.assertEqual(self.phase2["accepted_cooking_evidence"], 0)
        self.assertEqual(self.phase2_evidence, {})

    def test_phase4_context_package_is_verified_and_numeric_records_are_not_selected(self):
        self.assertEqual(self.phase4["release_id"], "Phase4-v0.1.2")
        self.assertEqual(self.phase4["evidence_record_count"], 6)
        self.assertEqual(self.phase4["selected_context_record_count"], 0)
        self.assertEqual(self.phase4_context, [])
        self.assertEqual(self.phase4["manifest_sha256"], "9d6a3a13d6567a872bfb890cf02ea118648a8572c92ebdd8e33b970d0f889fba")


if __name__ == "__main__":
    unittest.main()
