"""Stage D schema/implementation checks using synthetic inputs only.

This module reads Stage D schema definitions and constructs synthetic candidate
records in memory. It does not open the protected Stage B source or Stage D's
source-derived registries.
"""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

STAGE_D = Path(__file__).resolve().parents[1]
TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS))

from jsonschema import Draft202012Validator, FormatChecker, ValidationError  # noqa: E402
from test_mechanisms import synthetic_record  # noqa: E402
from test_review_authorization import SyntheticProvider  # noqa: E402
from stage_d.evidence_queue import SOURCE_RELEASE, SOURCE_SHA256, build_queue_from_rows  # noqa: E402
from stage_d.evidence_review_workflow import (  # noqa: E402
    append_review_action,
    build_assignment_export,
    build_coverage_dashboard,
)


class StageDSyntheticSchemaConsistencyTests(unittest.TestCase):
    @staticmethod
    def _synthetic_queue():
        fields = {
            "Compound": "Synthetic compound",
            "Compound_ID": "MOL-SYN-001",
            "Drug": "Synthetic probe",
            "Interaction_Effect": "Synthetic effect text",
            "Mechanism": "Synthetic assay text",
            "Evidence_Type": "In vitro",
            "Evidence_Level": "compound",
            "Direction": "Synthetic direction",
            "Quantitative_Outcome": "Synthetic value retained as text",
            "Dose": "Synthetic dose context",
            "Population": "Synthetic model",
            "Study_Design": "Synthetic design",
            "Source_Title": "Synthetic source",
            "Authors": "Synthetic authors",
            "Year": "2026",
            "DOI": "10.0000/synthetic",
            "PMID": "00000000",
            "Source_Type": "Synthetic fixture",
            "Limitations": "Synthetic only",
            "Confidence": "Not assessed",
            "Notes": "Synthetic fixture only",
            "Study_ID": "SYN-STUDY-001",
            "Source_URL": "https://example.invalid/source",
            "Source_Cache": "",
            "Source_Locator": "Synthetic Table 1",
            "Preparation": "Synthetic preparation",
            "Co_Compounds": "",
            "Affected_Entity": "Synthetic probe",
            "Perpetrator": "Synthetic compound",
            "Outcome": "observed effect",
            "Conflict_Group": "",
            "Identity_Status": "verified_exact",
            "Release_Origin": "synthetic fixture",
            "Clinical_Extrapolation": "None",
            "CookRisk_Exposure_Link": "Not assessed",
        }
        rows = []
        for index in range(1, 318):
            row = {**fields, "Evidence_ID": f"SB-SYN-{index:04d}"}
            if index == 1:
                row["Conflict_Group"] = "SYNTHETIC-CONFLICT"
            rows.append(row)
        return build_queue_from_rows(
            rows, source_sha256=SOURCE_SHA256, source_release=SOURCE_RELEASE
        )

    def test_synthetic_queue_coverage_and_assignment_outputs_match_schemas(self):
        queue = self._synthetic_queue()
        checker = FormatChecker()
        queue_schema = json.loads((STAGE_D / "schemas" / "evidence_review_queue.schema.json").read_text(encoding="utf-8"))
        coverage_schema = json.loads((STAGE_D / "schemas" / "evidence_review_coverage.schema.json").read_text(encoding="utf-8"))
        assignment_schema = json.loads((STAGE_D / "schemas" / "evidence_review_assignment.schema.json").read_text(encoding="utf-8"))

        Draft202012Validator(queue_schema, format_checker=checker).validate(queue)
        coverage = build_coverage_dashboard(queue, [])
        Draft202012Validator(coverage_schema, format_checker=checker).validate(coverage)
        assignment = build_assignment_export(queue)
        Draft202012Validator(assignment_schema, format_checker=checker).validate(assignment)
        self.assertEqual(coverage["record_count"], 317)
        self.assertEqual(assignment["purpose_and_limits"]["decisions_created"], False)

    def test_synthetic_signed_review_action_matches_schema(self):
        queue = self._synthetic_queue()
        record = queue["records"][0]
        action = {
            "action_id": "SYN-SCHEMA-ACTION-1",
            "review_id": record["review_id"],
            "evidence_id": record["source_reference"]["evidence_id"],
            "resulting_status": "CONFLICT_REVIEW",
            "reviewer_name": "Synthetic Reviewer",
            "reviewer_role": "reviewer",
            "review_date": "2026-11-05",
            "source_locator": "Synthetic Table 1",
            "rationale": "Synthetic schema contract test only.",
            "review_assessment": {
                "supporting_findings": [],
                "contradicting_findings": [],
                "uncertainty_and_limitations": ["Synthetic test; no evidence was reviewed."],
                "exposure_comparability_status": "NOT_ASSESSED",
            },
        }
        provider = SyntheticProvider()
        with tempfile.TemporaryDirectory(prefix=".stage-d-schema-action-", dir=STAGE_D / "tests") as directory:
            log_path = Path(directory) / "actions.jsonl"
            event = append_review_action(
                log_path, queue, action,
                identity_provider=provider,
                credentials="valid-synthetic-credential",
            )
        schema = json.loads((STAGE_D / "schemas" / "evidence_review_action.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(event)
        self.assertEqual(event["schema_version"], "1.2.0")

    def test_all_stage_d_schema_definitions_are_draft_2020_12_valid(self):
        schema_paths = sorted((STAGE_D / "schemas").glob("*.schema.json"))
        self.assertEqual(len(schema_paths), 9)
        for path in schema_paths:
            with self.subTest(schema=path.name):
                schema = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
                Draft202012Validator.check_schema(schema)

    def test_synthetic_mechanism_record_matches_schema_and_unsafe_state_fails(self):
        record = synthetic_record()
        # The schema intentionally requires a sufficiently complete preserved
        # raw record; these in-memory fields are explicitly synthetic fillers.
        filler = 0
        while len(record["raw_stage_b_record"]) < 30:
            record["raw_stage_b_record"][f"synthetic_field_{filler}"] = "synthetic fixture only"
            filler += 1
        schema = json.loads((STAGE_D / "schemas" / "mechanism_evidence.schema.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        validator.validate(record)

        unsafe = copy.deepcopy(record)
        unsafe["review_state"]["acceptance"] = "accepted"
        with self.assertRaises(ValidationError):
            validator.validate(unsafe)

        invalid_candidate = copy.deepcopy(record)
        invalid_candidate["mechanism_candidate"]["candidate_family"] = "automatic_causal_finding"
        with self.assertRaises(ValidationError):
            validator.validate(invalid_candidate)

    def test_synthetic_mechanism_registry_envelope_matches_schema_and_bad_digest_fails(self):
        record = synthetic_record()
        filler = 0
        while len(record["raw_stage_b_record"]) < 30:
            record["raw_stage_b_record"][f"synthetic_field_{filler}"] = "synthetic fixture only"
            filler += 1
        registry = {
            "schema_version": "1.0.0",
            "release_id": "StageB_V20_20261103",
            "source_file": "SYNTHETIC-FIXTURE-ONLY.csv",
            "source_file_sha256": "a" * 64,
            "source_row_count": 1,
            "selected_record_count": 1,
            "warning": "Synthetic fixture; no source data loaded.",
            "records": [record],
        }
        schema = json.loads((STAGE_D / "schemas" / "mechanism_registry.schema.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        validator.validate(registry)

        invalid = copy.deepcopy(registry)
        invalid["source_file_sha256"] = "not-a-digest"
        with self.assertRaises(ValidationError):
            validator.validate(invalid)


if __name__ == "__main__":
    unittest.main()
