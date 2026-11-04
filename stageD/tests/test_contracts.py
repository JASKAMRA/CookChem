from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

STAGE_D = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STAGE_D / "src"))
from stage_d.contracts import ContractError, build_cross_stage_comparison, evaluate_comparability, normalize_stage_b_record, validate_normalized_record


STAGE_B_HASH = "db630b3134126df723494c7ebb58db64e1c61099660b0c6391a4602c3e7deec2"


def row(**overrides):
    base = {
        "Evidence_ID": "SB-SYN-0001",
        "Compound_ID": "MOL-SYN-001",
        "Compound": "Synthetic compound",
        "Identity_Status": "source identity retained; not re-adjudicated",
        "Drug": "Synthetic probe",
        "Evidence_Type": "Human pharmacokinetic",
        "Outcome": "observed effect",
        "Direction": "increased probe exposure",
        "Quantitative_Outcome": "AUC increased in source study",
        "Evidence_Level": "compound",
        "Study_Design": "synthetic controlled crossover",
        "Dose": "synthetic dose; source-reported basis retained",
        "Population": "synthetic adult volunteers",
        "Affected_Entity": "probe exposure",
        "Perpetrator": "compound_or_preparation",
        "Limitations": "synthetic fixture; no clinical inference",
        "Clinical_Extrapolation": "No automatic clinical risk classification",
        "Confidence": "Moderate: source-text field; no score assigned",
        "Conflict_Group": "",
        "Mechanism": "Mechanism proposed by source authors",
        "Study_ID": "PMID:00000000",
        "Source_Title": "Synthetic test source",
        "Authors": "Example A",
        "Year": "2020",
        "DOI": "10.0000/synthetic",
        "PMID": "00000000",
        "Source_URL": "https://example.invalid/source",
        "Source_Locator": "Table 1",
        "Source_Type": "Primary research",
    }
    base.update(overrides)
    return base


class EvidenceNormalizationTests(unittest.TestCase):
    def normalize(self, source):
        return normalize_stage_b_record(source, stage_b_release="StageB_V20_20261103", stage_b_manifest_sha256=STAGE_B_HASH)

    def test_normalizes_known_study_type_and_preserves_provenance(self):
        normalized = self.normalize(row())
        validate_normalized_record(normalized)
        self.assertEqual(normalized["study_type"]["normalized_category"], "human_pharmacokinetic")
        self.assertEqual(normalized["finding"]["raw_quantitative_outcome"], "AUC increased in source study")
        self.assertEqual(normalized["study_context"]["dose"], "synthetic dose; source-reported basis retained")
        self.assertEqual(normalized["study_context"]["source_confidence_text"], "Moderate: source-text field; no score assigned")
        self.assertEqual(normalized["source_provenance"]["source_record_id"], "SB-SYN-0001")
        self.assertEqual(normalized["source_provenance"]["stage_b_manifest_sha256"], STAGE_B_HASH)
        self.assertEqual(normalized["review_state"]["acceptance_status"], "pending")
        self.assertTrue(normalized["review_state"]["manual_review_required"] is False)

    def test_unknown_type_and_ambiguous_result_remain_pending_review(self):
        normalized = self.normalize(row(Evidence_Type="Human study; type not classified", Outcome="Complex mixed result"))
        self.assertEqual(normalized["study_type"]["normalized_category"], "other_unclassified")
        self.assertEqual(normalized["finding"]["polarity"], "unclear")
        self.assertTrue(normalized["review_state"]["manual_review_required"])
        self.assertEqual(normalized["review_state"]["acceptance_status"], "pending")

    def test_explicit_null_and_conflict_group_are_separate(self):
        null_record = self.normalize(row(Outcome="No significant effect on probe AUC"))
        conflict_record = self.normalize(row(Outcome="observed effect", Conflict_Group="CONFLICT-1"))
        self.assertEqual(null_record["finding"]["polarity"], "null")
        self.assertEqual(conflict_record["finding"]["polarity"], "conflicting")
        self.assertTrue(conflict_record["review_state"]["manual_review_required"])

    def test_explicit_no_effect_is_negative_and_not_a_risk_judgment(self):
        record = self.normalize(row(Outcome="No inhibition reported under tested microsomal conditions"))
        self.assertEqual(record["finding"]["polarity"], "negative")
        self.assertIn("no_effect", record["finding"]["normalization_rule"])

    def test_invalid_identifiers_and_hash_are_rejected(self):
        with self.assertRaises(ContractError):
            self.normalize(row(Evidence_ID=""))
        with self.assertRaises(ContractError):
            normalize_stage_b_record(row(), stage_b_release="StageB_V20_20261103", stage_b_manifest_sha256="not-a-hash")
        invalid = self.normalize(row())
        invalid["study_context"].pop("dose")
        with self.assertRaises(ContractError):
            validate_normalized_record(invalid)

    def test_schema_files_are_valid_json_and_have_draft_2020_12_declaration(self):
        for path in (STAGE_D / "schemas" / "normalized_evidence.schema.json", STAGE_D / "schemas" / "exposure_comparison.schema.json"):
            schema = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_formal_schema_positive_and_negative_fixtures_when_validator_available(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("jsonschema is not installed; pure contract validation still runs")
        evidence_schema = json.loads((STAGE_D / "schemas" / "normalized_evidence.schema.json").read_text(encoding="utf-8"))
        comparison_schema = json.loads((STAGE_D / "schemas" / "exposure_comparison.schema.json").read_text(encoding="utf-8"))
        normalized = self.normalize(row())
        Draft202012Validator.check_schema(evidence_schema)
        Draft202012Validator.check_schema(comparison_schema)
        Draft202012Validator(evidence_schema).validate(normalized)
        invalid = dict(normalized)
        invalid["review_state"] = {**normalized["review_state"], "acceptance_status": "accepted"}
        self.assertTrue(list(Draft202012Validator(evidence_schema).iter_errors(invalid)))
        valid_comparison = {
            "schema_version": "1.0.0", "comparison_id": "CMP-SYN-001", "exposure_id": "EXP-SYN-001",
            "evidence_id": "SB-SYN-0001",
            "criteria": {key: True for key in (
                "compound_identity", "exposure_route", "dose_units_and_basis", "time_window",
                "population_or_model", "preparation_or_matrix",
            )},
            "decision": "READY_FOR_REVIEW", "decision_reason": "synthetic all-gates fixture",
            "review_status": "automated_check_only", "clinical_interpretation": "not_performed",
        }
        Draft202012Validator(comparison_schema).validate(valid_comparison)
        invalid_comparison = {**valid_comparison, "criteria": {"compound_identity": True}}
        self.assertTrue(list(Draft202012Validator(comparison_schema).iter_errors(invalid_comparison)))


class ComparabilityGateTests(unittest.TestCase):
    def criteria(self):
        return {
            "compound_identity": True,
            "exposure_route": True,
            "dose_units_and_basis": True,
            "time_window": True,
            "population_or_model": True,
            "preparation_or_matrix": True,
        }

    def test_unknown_criteria_remain_pending(self):
        criteria = self.criteria()
        criteria["time_window"] = None
        result = evaluate_comparability(criteria)
        self.assertEqual(result["decision"], "PENDING")
        self.assertEqual(result["clinical_interpretation"], "not_performed")
        self.assertEqual(result["gate_results"]["time_window"]["result"], "PENDING")
        self.assertTrue(result["gate_results"]["time_window"]["reason"])

    def test_failed_criterion_rejects_comparison(self):
        criteria = self.criteria()
        criteria["dose_units_and_basis"] = False
        result = evaluate_comparability(criteria)
        self.assertEqual(result["decision"], "REJECTED")
        self.assertIn("dose_units_and_basis", result["decision_reason"])
        self.assertEqual(result["gate_results"]["dose_units_and_basis"]["result"], "FAIL")

    def test_all_positive_criteria_only_ready_for_human_review(self):
        result = evaluate_comparability(self.criteria())
        self.assertEqual(result["decision"], "READY_FOR_REVIEW")
        self.assertEqual(result["review_status"], "automated_check_only")
        self.assertIn("No dose equivalence", result["decision_reason"])
        self.assertTrue(all(
            result["gate_results"][gate]["result"] == "PASS_PENDING_HUMAN_REVIEW"
            for gate in self.criteria()
        ))

    def test_missing_or_mistyped_comparison_criteria_rejected(self):
        with self.assertRaises(ContractError):
            evaluate_comparability({"compound_identity": True})
        criteria = self.criteria()
        criteria["time_window"] = "compatible"
        with self.assertRaises(ContractError):
            evaluate_comparability(criteria)

    def test_every_comparability_gate_fails_closed_individually(self):
        for gate in self.criteria():
            with self.subTest(gate=gate, state=False):
                criteria = self.criteria()
                criteria[gate] = False
                result = evaluate_comparability(criteria)
                self.assertEqual(result["decision"], "REJECTED")
                self.assertIn(gate, result["decision_reason"])
            with self.subTest(gate=gate, state=None):
                criteria = self.criteria()
                criteria[gate] = None
                result = evaluate_comparability(criteria)
                self.assertEqual(result["decision"], "PENDING")
                self.assertIn(gate, result["decision_reason"])


class CrossStageComparisonTests(unittest.TestCase):
    def setUp(self):
        self.phase3 = {
            "recipe_id": "RECIPE-SYN-001",
            "calculation_status": "COMPLETE",
            "provenance": {"stage_b_manifest_sha256": STAGE_B_HASH},
            "upstream_releases": {
                "phase1b": {"release_id": "Phase1B-SYN-v1", "manifest_sha256": "b" * 64, "stage_b_release": "StageB_V20_20261103", "stage_b_manifest_sha256": STAGE_B_HASH},
                "phase2": {"release_id": "Phase2-SYN-v1", "manifest_sha256": "c" * 64},
                "phase4": {"release_id": "Phase4-SYN-v1", "manifest_sha256": "d" * 64},
            },
            "ingredient_results": [{
                "estimate_id": "EXP-SYN-001",
                "compound_id": "MOL-SYN-001",
                "calculation_status": "Complete",
                "consumed_amount_low_mg": "2.5000",
                "consumed_amount_high_mg": "3.7500",
                "raw_reference_amount_mg": "3.7500",
                "raw_concentration": "25.0",
                "raw_concentration_unit": "mg/kg",
                "cooked_exposure_status": "SYNTHETIC_RAW_FIXTURE",
                "retention_evidence_id": "",
                "missing_inputs": [],
                "warnings": ["SYNTHETIC fixture only"],
                "input_source_ids": ["FOOD-SYN-001", "SOURCE-SYN-001"],
                "calculation_method": "SYNTHETIC arithmetic fixture",
                "stage_b_manifest_sha256": STAGE_B_HASH,
                "provenance": {
                    "compound_id": "MOL-SYN-001",
                    "food_record_id": "FOOD-SYN-001",
                    "mapping_id": "MAP-SYN-001",
                    "food_source_title": "Synthetic source",
                    "food_source_url": "https://example.invalid/synthetic",
                    "food_doi": "",
                    "food_pmid": "",
                    "stage_b_manifest_sha256": STAGE_B_HASH,
                },
            }],
        }
        self.exposure = self.phase3["ingredient_results"][0]
        self.evidence = normalize_stage_b_record(
            row(Compound_ID=self.exposure["compound_id"]),
            stage_b_release="StageB_V20_20261103",
            stage_b_manifest_sha256=STAGE_B_HASH,
        )
        self.criteria = {key: True for key in (
            "compound_identity", "exposure_route", "dose_units_and_basis", "time_window",
            "population_or_model", "preparation_or_matrix",
        )}

    def build(self, phase3=None, evidence=None, criteria=None, **kwargs):
        args = {
            "phase3_result": phase3 or self.phase3,
            "exposure_id": self.exposure["estimate_id"],
            "normalized_evidence": evidence or self.evidence,
            "criteria": self.criteria if criteria is None else criteria,
            "phase3_release_id": "Phase3-SYN-v0.0.0",
            "phase3_manifest_sha256": "a" * 64,
            "phase3_manifest_verification": "verified",
            "stage_b_release": "StageB_V20_20261103",
            "stage_b_manifest_sha256": STAGE_B_HASH,
        }
        args.update(kwargs)
        return build_cross_stage_comparison(**args)

    def test_binds_exact_ids_hashes_and_separate_exposure_types(self):
        result = self.build()
        self.assertEqual(result["schema_version"], "1.2.0")
        self.assertEqual(result["decision"], "READY_FOR_REVIEW")
        self.assertEqual(result["exposure_reference"]["estimate_id"], self.exposure["estimate_id"])
        self.assertEqual(result["exposure_reference"]["stage_b_compound_id"], self.exposure["compound_id"])
        self.assertEqual(result["exposure_reference"]["upstream_releases"]["phase2"]["release_id"], "Phase2-SYN-v1")
        self.assertEqual(result["exposure_reference"]["input_source_ids"], ["FOOD-SYN-001", "SOURCE-SYN-001"])
        self.assertEqual(result["dietary_exposure"]["unit"], "mg")
        self.assertEqual(result["dietary_exposure"]["raw_food_concentration_unit"], "mg/kg")
        self.assertIsNone(result["dietary_exposure"]["cooked_food_concentration_lower"])
        self.assertEqual(result["dietary_exposure"]["food_state"], "unknown")
        self.assertEqual(result["dietary_exposure"]["source_warnings"], ["SYNTHETIC fixture only"])
        self.assertEqual(result["experimental_exposure"]["reported_dose_text"], self.evidence["study_context"]["dose"])
        self.assertIsNone(result["experimental_exposure"]["normalized_dose_value"])
        self.assertIsNone(result["experimental_exposure"]["experimental_concentration_value"])
        self.assertEqual(result["clinical_interpretation"], "not_performed")

    def test_mismatched_compound_and_source_provenance_fail_closed(self):
        mismatch = normalize_stage_b_record(row(Compound_ID="CHEM-DIFFERENT"), stage_b_release="StageB_V20_20261103", stage_b_manifest_sha256=STAGE_B_HASH)
        with self.assertRaisesRegex(ContractError, "do not match"):
            self.build(evidence=mismatch)
        bad_hash = dict(self.phase3)
        bad_hash["provenance"] = {**bad_hash["provenance"], "stage_b_manifest_sha256": "0" * 64}
        with self.assertRaisesRegex(ContractError, "result provenance"):
            self.build(phase3=bad_hash)
        with self.assertRaisesRegex(ContractError, "Source record ID"):
            bad_record = json.loads(json.dumps(self.evidence))
            bad_record["source_provenance"]["source_record_id"] = "SB-OTHER"
            self.build(evidence=bad_record)

    def test_incomplete_or_unverified_releases_are_rejected(self):
        with self.assertRaisesRegex(ContractError, "must be verified"):
            self.build(phase3_manifest_verification="unverified")
        incomplete = dict(self.phase3)
        incomplete["calculation_status"] = "PARTIAL"
        with self.assertRaisesRegex(ContractError, "not complete"):
            self.build(phase3=incomplete)
        with self.assertRaisesRegex(ContractError, "exactly one"):
            self.build(exposure_id="missing-estimate")

    def test_missing_quantities_units_and_reversed_bounds_are_rejected_not_zero_filled(self):
        for key, value in (("consumed_amount_low_mg", ""), ("raw_concentration_unit", "")):
            result = json.loads(json.dumps(self.phase3))
            result["ingredient_results"][0][key] = value
            with self.subTest(key=key), self.assertRaises(ContractError):
                self.build(phase3=result)
        result = json.loads(json.dumps(self.phase3))
        result["ingredient_results"][0]["consumed_amount_low_mg"] = "12"
        result["ingredient_results"][0]["consumed_amount_high_mg"] = "11"
        with self.assertRaisesRegex(ContractError, "lower bound"):
            self.build(phase3=result)

    def test_raw_and_cooked_concentrations_keep_separate_units_and_provenance(self):
        result = json.loads(json.dumps(self.phase3))
        exposure = result["ingredient_results"][0]
        exposure.update({
            "cooked_concentration_low": "10.0",
            "cooked_concentration_high": "15.0",
            "cooked_concentration_unit": "mg/kg",
            "raw_concentration_basis": "as-received",
            "cooked_concentration_basis": "as-received",
            "cooked_exposure_status": "SUPPORTED_SYNTHETIC_INTERVAL",
            "retention_evidence_id": "EVID-SYN-001",
        })
        comparison = self.build(phase3=result)
        dietary = comparison["dietary_exposure"]
        self.assertEqual(dietary["raw_food_concentration"], "25.0")
        self.assertEqual(dietary["raw_food_concentration_unit"], "mg/kg")
        self.assertEqual(dietary["cooked_food_concentration_lower"], "10.0")
        self.assertEqual(dietary["cooked_food_concentration_upper"], "15.0")
        self.assertEqual(dietary["cooked_food_concentration_unit"], "mg/kg")
        self.assertEqual(dietary["raw_food_concentration_basis"], "as-received")
        self.assertEqual(dietary["cooked_food_concentration_basis"], "as-received")
        self.assertEqual(dietary["retention_evidence_id"], "EVID-SYN-001")
        for invalid_update, message in (
            ({"retention_evidence_id": ""}, "retention_evidence_id"),
            ({"cooked_concentration_unit": ""}, "explicit unit"),
            ({"raw_concentration_basis": ""}, "explicit measurement bases"),
            ({"cooked_concentration_basis": "dry-weight"}, "bases differ"),
            ({"cooked_concentration_unit": "mg/g"}, "units differ"),
        ):
            invalid = json.loads(json.dumps(result))
            invalid["ingredient_results"][0].update(invalid_update)
            with self.subTest(invalid_update=invalid_update), self.assertRaisesRegex(ContractError, message):
                self.build(phase3=invalid)

    def test_pending_or_failed_gate_does_not_become_ready(self):
        criteria = dict(self.criteria)
        criteria["time_window"] = None
        self.assertEqual(self.build(criteria=criteria)["decision"], "PENDING")
        criteria["time_window"] = False
        self.assertEqual(self.build(criteria=criteria)["decision"], "REJECTED")

    def test_phase3_release_v11_schema_accepts_complete_and_rejects_tampering(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("jsonschema is not installed; structural contract tests still run")
        schema = json.loads((STAGE_D / "schemas" / "exposure_comparison.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        result = self.build()
        Draft202012Validator(schema).validate(result)
        invalid = json.loads(json.dumps(result))
        invalid["exposure_reference"]["phase3_manifest_sha256"] = "tampered"
        self.assertTrue(list(Draft202012Validator(schema).iter_errors(invalid)))


if __name__ == "__main__":
    unittest.main()
