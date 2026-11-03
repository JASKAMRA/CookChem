from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from stage_c.cooking_integration import (
    CookingIntegrationError,
    GATES,
    STAGE_A_INPUT_SHA256,
    STAGE_A_RUNNER_SHA256,
    adapt_stage_a_output,
    calculate_cooked_concentration,
    validate_prediction_record,
)


def record(*, origin="mocked_fixture", semantic="model_predicted_retention", value="50", unit="percent", basis=None):
    prediction = {"semantic_type": semantic, "value": value, "unit": unit}
    if basis is not None:
        prediction["underlying_retention_semantics"] = basis
    provenance = {"origin": origin, "source_reference": "synthetic fixture; not a real Stage A result"}
    if origin == "supplied_prediction":
        provenance.update({
            "stage_a_input_sha256": STAGE_A_INPUT_SHA256,
            "stage_a_code_sha256": STAGE_A_RUNNER_SHA256,
            "model_artifact_sha256": "c" * 64,
            "output_sha256": "d" * 64,
            "model_name": "XGBoost_tuned",
            "python_version": "3.12.14",
            "package_versions": {"numpy": "2.5.3"},
        })
    return {
        "schema_version": "1.0.0", "prediction_id": "P-SYN-1", "food_record_id": "F-SYN-1",
        "compound_id": "C-SYN-1", "food_matrix": "synthetic food matrix", "food_state": "fresh raw",
        "cooking_conditions": {"cooking_method": "boiling", "temperature_c": "100", "duration_min": "10", "cooking_medium": "water"},
        "measurement_basis": "synthetic explicit concentration basis", "denominator": "per kg cooked edible food",
        "prediction": prediction, "provenance": provenance,
        "scientific_review": {"status": "pending"},
    }


def all_gates(value=True):
    return {gate: value for gate in GATES}


def measured(value, unit, source="synthetic test measurement"):
    return {"status": "measured", "value": str(value), "unit": unit, "source_reference": source}


class CookingIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((ROOT / "schemas" / "stage_a_prediction.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(cls.schema)

    def test_schema_is_formal_draft_2020_12_and_accepts_mock_fixture(self):
        candidate = record()
        self.validator.validate(candidate)
        validate_prediction_record(candidate)

    def test_schema_and_contract_reject_missing_identity_type_and_provenance(self):
        for mutate in (
            lambda value: value.pop("compound_id"),
            lambda value: value.update(compound_id=17),
            lambda value: value["provenance"].update(origin="mystery"),
        ):
            candidate = record()
            mutate(candidate)
            with self.assertRaises((ValidationError, CookingIntegrationError)):
                self.validator.validate(candidate)
                validate_prediction_record(candidate)

    def test_supplied_prediction_requires_reproducibility_metadata(self):
        candidate = record(origin="supplied_prediction")
        self.validator.validate(candidate)
        validate_prediction_record(candidate)
        del candidate["provenance"]["model_artifact_sha256"]
        with self.assertRaises((ValidationError, CookingIntegrationError)):
            self.validator.validate(candidate)
            validate_prediction_record(candidate)

    def test_stage_a_supplied_prediction_stays_blocked_without_a_registered_model_artifact(self):
        candidate = record(origin="supplied_prediction", basis="concentration_retention")
        candidate["scientific_review"] = {"status": "approved", "reviewer": "Synthetic reviewer", "review_reference": "TEST-REVIEW-6"}
        result = adapt_stage_a_output(candidate, all_gates())
        self.assertFalse(result["eligible_for_estimation"])
        self.assertTrue(any("no serialized Stage A model artifact" in reason for reason in result["missing_data_reasons"]))
        candidate["provenance"]["stage_a_input_sha256"] = "e" * 64
        with self.assertRaises(CookingIntegrationError):
            validate_prediction_record(candidate)

    def test_mock_output_stays_ineligible_even_if_all_compatibility_gates_pass(self):
        result = adapt_stage_a_output(record(), all_gates())
        self.assertEqual(result["compatibility_status"], "COMPATIBLE_PENDING_SCIENTIFIC_REVIEW")
        self.assertFalse(result["eligible_for_estimation"])
        self.assertTrue(any("synthetic" in reason for reason in result["missing_data_reasons"]))
        calculated = calculate_cooked_concentration(measured("10", "mg/kg"), record(), all_gates())
        self.assertEqual(calculated["status"], "INCOMPLETE")
        self.assertEqual(calculated["cooked_concentration"], "")

    def test_failed_and_unknown_compatibility_gates_are_distinguished(self):
        incompatible = all_gates()
        incompatible["food_matrix_match"] = False
        result = adapt_stage_a_output(record(), incompatible)
        self.assertEqual(result["compatibility_status"], "INCOMPATIBLE")
        self.assertTrue(any("food_matrix_match" in reason for reason in result["missing_data_reasons"]))
        incomplete = all_gates()
        incomplete["cooking_conditions_match"] = None
        result = adapt_stage_a_output(record(), incomplete)
        self.assertEqual(result["compatibility_status"], "PENDING_COMPATIBILITY")

    def test_compatibility_contract_rejects_missing_or_non_boolean_gate(self):
        with self.assertRaises(CookingIntegrationError):
            adapt_stage_a_output(record(), {"compound_identity_match": True})
        invalid = all_gates()
        invalid["food_state_match"] = "yes"
        with self.assertRaises(CookingIntegrationError):
            adapt_stage_a_output(record(), invalid)

    def test_apparent_concentration_ratio_is_never_converted_to_retention(self):
        candidate = record(origin="measured_source_record", semantic="apparent_concentration_ratio", value="1.5", unit="ratio")
        candidate["scientific_review"] = {"status": "approved", "reviewer": "Synthetic reviewer", "review_reference": "TEST-REVIEW-0"}
        result = calculate_cooked_concentration(measured("10", "mg/kg"), candidate, all_gates())
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertIn("not concentration retention", result["reason"])

    def test_concentration_retention_formula_independent_expected_value(self):
        candidate = record(origin="measured_source_record", semantic="concentration_retention", value="50", unit="percent")
        candidate["scientific_review"] = {"status": "approved", "reviewer": "Synthetic reviewer", "review_reference": "TEST-REVIEW-1"}
        result = calculate_cooked_concentration(measured("10", "mg/kg"), candidate, all_gates())
        self.assertEqual(result, {"status": "COMPLETE", "cooked_concentration": "5", "cooked_concentration_unit": "mg/kg",
                                  "reason": "approved compatible retention; explicit semantics and measured basis applied"})

    def test_total_mass_retention_requires_measured_yield_and_uses_mass_ratio(self):
        candidate = record(origin="measured_source_record", semantic="total_mass_retention", value="50", unit="percent")
        candidate["scientific_review"] = {"status": "approved", "reviewer": "Synthetic reviewer", "review_reference": "TEST-REVIEW-2"}
        missing = calculate_cooked_concentration(measured("10", "mg/kg"), candidate, all_gates())
        self.assertEqual(missing["status"], "INCOMPLETE")
        self.assertIn("raw_mass and cooked_mass", missing["reason"])
        result = calculate_cooked_concentration(measured("10", "mg/kg"), candidate, all_gates(),
                                                raw_mass=measured("2", "kg"), cooked_mass=measured("1", "kg"))
        self.assertEqual(result["cooked_concentration"], "10")
        mismatched = calculate_cooked_concentration(measured("10", "mg/kg"), candidate, all_gates(),
                                                    raw_mass=measured("2", "kg"), cooked_mass=measured("1000", "g"))
        self.assertEqual(mismatched["status"], "INCOMPLETE")
        self.assertIn("units must match", mismatched["reason"])

    def test_volume_based_total_mass_retention_requires_measured_volume_yield(self):
        candidate = record(origin="measured_source_record", semantic="total_mass_retention", value="50", unit="percent")
        candidate["scientific_review"] = {"status": "approved", "reviewer": "Synthetic reviewer", "review_reference": "TEST-REVIEW-7"}
        missing = calculate_cooked_concentration(measured("10", "mg/L"), candidate, all_gates())
        self.assertIn("raw_volume and cooked_volume", missing["reason"])
        result = calculate_cooked_concentration(measured("10", "mg/L"), candidate, all_gates(),
                                                raw_volume=measured("2", "L"), cooked_volume=measured("1", "L"))
        self.assertEqual(result["cooked_concentration"], "10")

    def test_unclassified_model_target_cannot_be_applied(self):
        candidate = record(origin="supplied_prediction", semantic="model_predicted_retention", value="50", unit="percent")
        candidate["scientific_review"] = {"status": "approved", "reviewer": "Synthetic reviewer", "review_reference": "TEST-REVIEW-3"}
        result = calculate_cooked_concentration(measured("10", "mg/kg"), candidate, all_gates())
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertIn("basis is not classified", result["reason"])

    def test_measured_retention_requires_an_explicit_underlying_basis(self):
        candidate = record(origin="measured_source_record", semantic="measured_retention", value="50", unit="percent")
        candidate["scientific_review"] = {"status": "approved", "reviewer": "Synthetic reviewer", "review_reference": "TEST-REVIEW-4"}
        blocked = calculate_cooked_concentration(measured("10", "mg/kg"), candidate, all_gates())
        self.assertIn("basis is not classified", blocked["reason"])
        candidate["prediction"]["underlying_retention_semantics"] = "concentration_retention"
        self.assertEqual(calculate_cooked_concentration(measured("10", "mg/kg"), candidate, all_gates())["cooked_concentration"], "5")

    def test_raw_concentration_requires_measured_value_unit_and_provenance(self):
        candidate = record(origin="measured_source_record", semantic="concentration_retention", value="50", unit="percent")
        candidate["scientific_review"] = {"status": "approved", "reviewer": "Synthetic reviewer", "review_reference": "TEST-REVIEW-5"}
        absent = calculate_cooked_concentration({"value": "10", "unit": "mg/kg"}, candidate, all_gates())
        self.assertEqual(absent["status"], "INCOMPLETE")
        self.assertIn("explicit measured value", absent["reason"])


if __name__ == "__main__":
    unittest.main()
