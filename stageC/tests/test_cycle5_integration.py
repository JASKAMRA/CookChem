from __future__ import annotations

import sys
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT.parent / "stageD" / "src"))

from stage_c.recipe_engine import calculate_meal_exposure, calculate_recipe_exposure
from stage_c.uncertainty import assess_phase3_uncertainty_coverage
from stage_d.contracts import ContractError, build_cross_stage_comparison, normalize_stage_b_record
from test_recipe_engine import COMPOUNDS, FOOD, MAPPINGS, recipe


class Cycle5CrossStageIntegrationTests(unittest.TestCase):
    def test_recipe_meal_coverage_flows_and_transient_result_is_not_linked_to_evidence(self):
        stage_b_hash = "a" * 64
        recipe_input = recipe(cooked=False, quantity="200")
        recipe_output = calculate_recipe_exposure(
            recipe_input, FOOD, MAPPINGS, COMPOUNDS, stage_b_manifest_sha256=stage_b_hash)
        meal_input = {"meal_id": "M-SYN-CYCLE5-01", "provenance": {}, "components": [{
            "component_id": "MC-SYN-CYCLE5-01", "kind": "recipe",
            "recipe_id": recipe_input["recipe_id"], "servings_consumed": "1", "consumed_fraction": "1",
        }]}
        meal_output = calculate_meal_exposure(
            meal_input, {recipe_input["recipe_id"]: recipe_input}, FOOD, MAPPINGS, COMPOUNDS,
            stage_b_manifest_sha256=stage_b_hash)
        coverage = assess_phase3_uncertainty_coverage(meal_output)
        self.assertEqual(coverage["record_type"], "meal")
        self.assertEqual(coverage["ingredient_estimate_count"], 1)
        self.assertEqual(coverage["aggregate_coverage"]["status"], "POINT_OR_MISSING_ONLY")
        self.assertEqual(Decimal(meal_output["compound_totals"][0]["consumed_amount_low_mg"]), Decimal("0.25"))

        raw_evidence = {"Evidence_ID": "SB-SYN-CYCLE5-01", "Compound_ID": "C-1",
                        "Evidence_Type": "in vitro", "Compound": "Test compound",
                        "Drug": "Test drug", "Source_Title": "Synthetic fixture"}
        normalized = normalize_stage_b_record(
            raw_evidence, stage_b_release="StageB_SYNTHETIC", stage_b_manifest_sha256=stage_b_hash)
        transient_result = dict(recipe_output)
        transient_result["calculation_status"] = "COMPLETE"
        with self.assertRaisesRegex(ContractError, "manifest must be verified"):
            build_cross_stage_comparison(
                transient_result,
                exposure_id=recipe_output["ingredient_results"][0]["estimate_id"],
                normalized_evidence=normalized,
                criteria={key: None for key in (
                    "compound_identity", "exposure_route", "dose_units_and_basis", "time_window",
                    "population_or_model", "preparation_or_matrix",
                )},
                phase3_release_id="TRANSIENT_ONLY",
                phase3_manifest_sha256=stage_b_hash,
                phase3_manifest_verification="not_verified",
                stage_b_release="StageB_SYNTHETIC",
                stage_b_manifest_sha256=stage_b_hash,
            )


if __name__ == "__main__":
    unittest.main()
