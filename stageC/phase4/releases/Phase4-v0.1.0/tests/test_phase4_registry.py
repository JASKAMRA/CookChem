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
        self.assertEqual(len(self.evidence), 1)

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
        evidence_status = validate_jsonschema_if_installed(PHASE4 / "schemas" / "evidence.schema.json", self.evidence[0])
        if source_status.startswith("NOT_RUN"):
            self.assertEqual(source_status, evidence_status)
        else:
            self.assertTrue(source_status.startswith("PASS"))
            self.assertTrue(evidence_status.startswith("PASS"))


if __name__ == "__main__":
    unittest.main()
