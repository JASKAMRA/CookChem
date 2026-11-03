from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PHASE4 = HERE.parent
sys.path.insert(0, str(PHASE4 / "src"))
from phase4_registry import (  # noqa: E402
    phase3_context_records,
    validate_jsonschema_if_installed,
    validate_registry,
)


class Phase4RegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = json.loads((PHASE4 / "data" / "source_registry.json").read_text(encoding="utf-8"))
        cls.evidence = json.loads((PHASE4 / "data" / "evidence_registry.json").read_text(encoding="utf-8"))

    def test_current_registry_has_valid_references_and_gates(self):
        self.assertEqual(validate_registry(self.sources, self.evidence), [])
        self.assertEqual(len(self.sources), 1)
        self.assertEqual(len(self.evidence), 6)
        self.assertEqual(self.sources[0]["access_status"], "full_text_reviewed")
        self.assertEqual(sum(row["outcome"]["result_type"] == "measured_numeric" for row in self.evidence), 5)
        self.assertEqual(sum(row["outcome"]["result_type"] == "qualitative_observation" for row in self.evidence), 1)
        self.assertEqual(sum(row["review"]["status"] == "pending_second_reviewer" for row in self.evidence), 6)
        self.assertTrue(all(row["identity_assessment"]["match_status"] == "NAME_ONLY_MATCH" for row in self.evidence))
        self.assertTrue(all(row["applicability_assessment"]["status"] == "CONTEXT_LIMITED" for row in self.evidence))

    def test_published_arm_level_cmax_values_and_uncertainty_are_preserved(self):
        observed = {row["outcome"]["condition_code"]: row["outcome"] for row in self.evidence if "condition_code" in row["outcome"]}
        self.assertEqual(set(observed), {"A", "B", "C", "D", "E"})
        self.assertEqual(observed["A"]["numeric_value"], 3.74)
        self.assertEqual(observed["A"]["standard_deviation"], 1.09)
        self.assertEqual(observed["A"]["range_min"], 1.96)
        self.assertEqual(observed["A"]["range_max"], 5.95)
        self.assertIn("denominator discrepancy is unresolved", observed["A"]["denominator"])

    def test_full_text_records_require_full_text_source_status(self):
        sources = copy.deepcopy(self.sources)
        sources[0]["access_status"] = "abstract_only_reviewed"
        self.assertTrue(any("full-text-reviewed source" in error for error in validate_registry(sources, self.evidence)))

    def test_unresolved_record_does_not_enter_phase3_context_view(self):
        self.assertEqual(phase3_context_records(self.evidence), ())

    def test_duplicate_source_ids_rejected(self):
        errors = validate_registry(self.sources + [copy.deepcopy(self.sources[0])], self.evidence)
        self.assertIn("duplicate source_id", errors)

    def test_orphan_evidence_source_rejected(self):
        evidence = copy.deepcopy(self.evidence)
        evidence[0]["source_id"] = "SRC-MISSING"
        self.assertTrue(any("does not reference" in error for error in validate_registry(self.sources, evidence)))

    def test_qualitative_claim_cannot_be_promoted_to_numeric(self):
        evidence = copy.deepcopy(self.evidence)
        evidence[0]["outcome"]["numeric_value"] = 12.0
        self.assertTrue(any("cannot carry a numeric_value" in error for error in validate_registry(self.sources, evidence)))

    def test_measured_numeric_record_requires_value_unit_and_denominator(self):
        evidence = copy.deepcopy(self.evidence)
        evidence[1]["outcome"]["numeric_value"] = None
        self.assertTrue(any("numeric evidence requires" in error for error in validate_registry(self.sources, evidence)))

    def test_accepted_record_requires_identity_and_applicability(self):
        evidence = copy.deepcopy(self.evidence)
        evidence[0]["review"].update(status="accepted_context_only", decision_rationale="accepted")
        errors = validate_registry(self.sources, evidence)
        self.assertTrue(any("unresolved identity" in error for error in errors))
        self.assertTrue(any("not marked applicable" in error for error in errors))

    def test_accepted_quantitative_record_requires_value_unit_and_denominator(self):
        evidence = copy.deepcopy(self.evidence)
        row = evidence[0]
        row["compound_reference"]["match_status"] = "STRICT_IDENTITY_MATCH"
        row["identity_assessment"].update(match_status="STRICT_IDENTITY_MATCH", review_status="adjudicated")
        row["applicability_assessment"]["status"] = "APPLICABLE"
        row["review"].update(status="accepted_quantitative", decision_rationale="reviewed")
        errors = validate_registry(self.sources, evidence)
        self.assertTrue(any("requires a numeric result, unit, and denominator" in error for error in errors))

    def test_versioned_package_manifest_hashes(self):
        package = PHASE4 / "releases" / "Phase4-v0.1.0"
        if not package.exists():  # Same test runs inside the self-contained release.
            package = PHASE4
        manifest = json.loads((package / "release_manifest.json").read_text(encoding="utf-8"))
        for item in manifest["files"]:
            path = package / item["path"]
            self.assertTrue(path.is_file(), item["path"])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), item["sha256"], item["path"])
        stated_manifest_hash = (package / "release_manifest.sha256").read_text(encoding="ascii").split()[0]
        self.assertEqual(hashlib.sha256((package / "release_manifest.json").read_bytes()).hexdigest(), stated_manifest_hash)

    def test_schema_validation_uses_draft202012_when_installed(self):
        source_status = validate_jsonschema_if_installed(PHASE4 / "schemas" / "source.schema.json", self.sources[0])
        evidence_statuses = [validate_jsonschema_if_installed(PHASE4 / "schemas" / "evidence.schema.json", row) for row in self.evidence]
        evidence_status = evidence_statuses[0]
        self.assertTrue(all(status == evidence_status for status in evidence_statuses))
        if source_status.startswith("NOT_RUN"):
            self.assertEqual(source_status, evidence_status)
        else:
            self.assertTrue(source_status.startswith("PASS"))
            self.assertTrue(evidence_status.startswith("PASS"))


if __name__ == "__main__":
    unittest.main()
