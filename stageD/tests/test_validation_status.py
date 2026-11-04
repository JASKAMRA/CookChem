from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

STAGE_D = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STAGE_D / "src"))

from stage_d.schema_validation import validate_draft_2020_12  # noqa: E402
from stage_d.reviewer_identity import reviewer_authorization_diagnostics  # noqa: E402


class ValidationStatusTests(unittest.TestCase):
    def test_json_syntax_is_not_reported_as_formal_schema_validation(self):
        result = validate_draft_2020_12({"ok": True}, '{"$schema":"https://json-schema.org/draft/2020-12/schema","type":"object"}')
        self.assertIn(result.status, {"VALID", "UNAVAILABLE"})
        if result.status == "UNAVAILABLE":
            self.assertIn("formal Draft 2020-12", result.errors[0])
            self.assertIsNone(result.validator)

    def test_invalid_schema_json_has_distinct_error_state(self):
        result = validate_draft_2020_12({}, "{")
        self.assertEqual(result.status, "INVALID_SCHEMA")
        self.assertTrue(result.errors)

    def test_available_validator_reports_instance_errors(self):
        try:
            import jsonschema  # noqa: F401
        except ImportError:
            self.skipTest("jsonschema is not installed; formal fixture check unavailable")
        schema = json.dumps({
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "required": ["record_id"],
            "properties": {"record_id": {"type": "string"}},
        })
        self.assertEqual(validate_draft_2020_12({"record_id": "R-1"}, schema).status, "VALID")
        rejected = validate_draft_2020_12({"record_id": 1}, schema)
        self.assertEqual(rejected.status, "INVALID")
        self.assertTrue(rejected.errors)

    def test_unconfigured_and_incomplete_identity_are_explicitly_blocked(self):
        self.assertEqual(reviewer_authorization_diagnostics(None)["status"], "BLOCKED")

        class IncompleteProvider:
            def authenticate(self, credentials):
                return None

        result = reviewer_authorization_diagnostics(IncompleteProvider())
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("sign_audit_event", result["missing_provider_methods"])


if __name__ == "__main__":
    unittest.main()
