from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from stage_d.interpretation import (  # noqa: E402
    INTERPRETATION_CATEGORIES,
    InterpretationError,
    classify_interpretation,
    decision_table,
    validate_interpretation_case,
)


class InterpretationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads((ROOT / "examples" / "phase6" / "synthetic_interpretation_cases.json").read_text(encoding="utf-8"))
        cls.cases = {row["case_id"]: row for row in cls.fixture["cases"]}
        cls.schema = json.loads((ROOT / "schemas" / "risk_interpretation.schema.json").read_text(encoding="utf-8"))

    def test_synthetic_fixture_marks_non_evidence_and_covers_every_category(self):
        self.assertTrue(self.fixture["not_scientific_evidence"])
        self.assertTrue(self.fixture["not_clinical_advice"])
        observed = set()
        for row in self.fixture["cases"]:
            assessment = classify_interpretation(row["input"])
            observed.add(assessment["category"])
            self.assertEqual(assessment["category"], row["expected_category"])
            self.assertEqual(assessment["schema_version"], "1.1.0")
            self.assertEqual(assessment["decision_trace"]["checks"][-1]["matched"], True)
            self.assertEqual(assessment["decision_trace"]["matched_rule_id"], assessment["decision_trace"]["checks"][-1]["rule_id"])
            self.assertEqual([step["order"] for step in assessment["decision_trace"]["checks"]], list(range(1, len(assessment["decision_trace"]["checks"]) + 1)))
            self.assertFalse(any(step["matched"] for step in assessment["decision_trace"]["checks"][:-1]))
            self.assertEqual(assessment["claim_boundary"]["clinical_interpretation"], "not_performed")
            self.assertEqual(assessment["claim_boundary"]["risk_score"], "not_calculated")
        self.assertEqual(observed, INTERPRETATION_CATEGORIES)

    def test_mechanism_only_cannot_be_promoted_even_with_all_other_gates_set(self):
        case = copy.deepcopy(self.cases["mechanism_only"]["input"])
        assessment = classify_interpretation(case)
        self.assertEqual(assessment["category"], "MECHANISTIC_EVIDENCE_ONLY")
        self.assertFalse(assessment["claim_boundary"]["mechanism_only_sufficient"])

    def test_conflicts_abstract_only_and_unverified_identity_require_review(self):
        base = copy.deepcopy(self.cases["experimental_positive"]["input"])
        for field, value in (("conflict_status", "source_discrepancy"),
                             ("source_review_status", "abstract_only"),
                             ("source_identity_status", "pending")):
            mutated = copy.deepcopy(base)
            mutated[field] = value
            self.assertEqual(classify_interpretation(mutated)["category"], "REQUIRES_EXPERT_REVIEW")

    def test_negative_and_null_findings_are_preserved_not_generalized(self):
        for case_id, polarity in (("negative_under_tested_conditions", "negative"), ("null_under_tested_conditions", "null")):
            assessment = classify_interpretation(self.cases[case_id]["input"])
            self.assertEqual(assessment["dimensions"]["outcome"], polarity)
            self.assertEqual(assessment["category"], "EXPERIMENTAL_EVIDENCE")
            self.assertTrue(assessment["claim_boundary"]["negative_or_null_is_not_generalized"])
            self.assertTrue(any("tested conditions" in reason for reason in assessment["decision_reason"]))

    def test_positive_human_evidence_needs_comparability_and_bounded_uncertainty(self):
        case = copy.deepcopy(self.cases["expert_supported_research_relevance"]["input"])
        case["exposure_comparability"] = "pending"
        self.assertEqual(classify_interpretation(case)["category"], "EXPOSURE_COMPARABILITY_PENDING")
        case["exposure_comparability"] = "supported_by_expert"
        case["uncertainty_status"] = "unquantified"
        self.assertEqual(classify_interpretation(case)["category"], "REQUIRES_EXPERT_REVIEW")

    def test_research_relevance_requires_explicit_completed_expert_adjudication(self):
        case = copy.deepcopy(self.cases["expert_supported_research_relevance"]["input"])
        case["expert_review"] = {"status": "not_reviewed", "adjudication": "not_assessed", "reviewer_reference": "", "rationale": ""}
        self.assertNotEqual(classify_interpretation(case)["category"], "RESEARCH_RELEVANCE_SUPPORTED")
        case["expert_review"] = {"status": "completed", "adjudication": "supports_research_relevance", "reviewer_reference": "", "rationale": ""}
        with self.assertRaisesRegex(InterpretationError, "reviewer reference"):
            classify_interpretation(case)

    def test_mutated_unknown_category_and_input_field_are_rejected(self):
        case = copy.deepcopy(self.cases["experimental_positive"]["input"])
        case["outcome"] = "weak_positive"
        with self.assertRaisesRegex(InterpretationError, "outcome"):
            validate_interpretation_case(case)
        case = copy.deepcopy(self.cases["experimental_positive"]["input"])
        case["outcome"] = ["positive"]
        with self.assertRaisesRegex(InterpretationError, "outcome"):
            validate_interpretation_case(case)
        case = copy.deepcopy(self.cases["experimental_positive"]["input"])
        case["invented_score"] = 4
        with self.assertRaisesRegex(InterpretationError, "fields mismatch"):
            validate_interpretation_case(case)

    def test_schema_is_draft_2020_12_and_both_contract_forms_are_valid(self):
        self.assertEqual(self.schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema is not installed; dependency-free rules and fixture tests still ran")
        jsonschema.Draft202012Validator.check_schema(self.schema)
        for row in self.fixture["cases"]:
            input_case = row["input"]
            jsonschema.validate(input_case, self.schema)
            jsonschema.validate(classify_interpretation(input_case), self.schema)
        invalid = classify_interpretation(self.cases["mechanism_only"]["input"])
        invalid["claim_boundary"]["clinical_interpretation"] = "likely"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(invalid, self.schema)
        invalid_trace = classify_interpretation(self.cases["experimental_positive"]["input"])
        invalid_trace["decision_trace"]["checks"][-1]["order"] = 0
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(invalid_trace, self.schema)

    def test_decision_table_is_explicit_and_has_no_score_or_clinical_category(self):
        rows = decision_table()
        self.assertEqual([int(row["order"]) for row in rows], list(range(1, len(rows) + 1)))
        self.assertEqual({row["category"] for row in rows}, INTERPRETATION_CATEGORIES)
        self.assertEqual(len({row["rule_id"] for row in rows}), len(rows))
        text = json.dumps(rows).casefold()
        self.assertNotIn("risk score", text)
        self.assertNotIn("clinical_risk", text)

    def test_conflicts_and_unassessed_conflicts_route_to_review_without_erasing_nulls(self):
        for case_id in ("conflicting_source", "unassessed_conflict_with_positive_result", "conflict_precedes_missing_outcome", "null_outcome_with_conflicting_studies"):
            with self.subTest(case_id=case_id):
                result = classify_interpretation(self.cases[case_id]["input"])
                self.assertEqual(result["category"], "REQUIRES_EXPERT_REVIEW")
                expected_rule = "UNRESOLVED_REVIEW_GATES" if case_id == "unassessed_conflict_with_positive_result" else "KNOWN_CONFLICT"
                self.assertEqual(result["decision_trace"]["matched_rule_id"], expected_rule)
        null_conflict = classify_interpretation(self.cases["null_outcome_with_conflicting_studies"]["input"])
        self.assertEqual(null_conflict["dimensions"]["outcome"], "null")
        self.assertIn("conflicting_studies", null_conflict["dimensions"]["conflict_status"])

    def test_missing_result_is_insufficient_not_negative_and_has_trace(self):
        result = classify_interpretation(self.cases["missing_outcome_is_not_negative"]["input"])
        self.assertEqual(result["category"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(result["dimensions"]["outcome"], "not_reported")
        self.assertEqual(result["decision_trace"]["matched_rule_id"], "NO_INTERPRETABLE_RESULT")
        self.assertIn("not coded as a negative", result["decision_reason"][0])

    def test_completed_expert_review_requires_explicit_disposition_and_audit_fields(self):
        case = copy.deepcopy(self.cases["experimental_positive"]["input"])
        case["expert_review"] = {"status": "completed", "adjudication": "not_assessed", "reviewer_reference": "", "rationale": ""}
        with self.assertRaisesRegex(InterpretationError, "explicit adjudication"):
            validate_interpretation_case(case)
        case["expert_review"] = {"status": "completed", "adjudication": "does_not_support_research_relevance", "reviewer_reference": "", "rationale": ""}
        with self.assertRaisesRegex(InterpretationError, "reviewer reference"):
            validate_interpretation_case(case)
        result = classify_interpretation(self.cases["expert_does_not_support_research_relevance"]["input"])
        self.assertEqual(result["category"], "EXPERIMENTAL_EVIDENCE")
        self.assertEqual(result["decision_trace"]["matched_rule_id"], "EXPERT_DOES_NOT_SUPPORT_RESEARCH_RELEVANCE")

    def test_inconsistent_evidence_and_comparability_inputs_are_rejected(self):
        case = copy.deepcopy(self.cases["insufficient"]["input"])
        case["outcome"] = "positive"
        with self.assertRaisesRegex(InterpretationError, "no-evidence records"):
            validate_interpretation_case(case)
        case = copy.deepcopy(self.cases["conflicting_source"]["input"])
        case["conflict_status"] = "none_known"
        with self.assertRaisesRegex(InterpretationError, "conflicting outcome requires"):
            validate_interpretation_case(case)
        case = copy.deepcopy(self.cases["expert_supported_research_relevance"]["input"])
        case["dietary_exposure_status"] = "unavailable"
        case["dietary_exposure_reference"] = ""
        with self.assertRaisesRegex(InterpretationError, "requires available dietary exposure"):
            validate_interpretation_case(case)


if __name__ == "__main__":
    unittest.main()
