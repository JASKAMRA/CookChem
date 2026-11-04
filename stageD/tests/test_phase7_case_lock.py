from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

STAGE_D = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STAGE_D / "scripts"))
from prepare_phase7_case_lock import prepare_case_lock  # noqa: E402
from stage_d.schema_validation import SchemaValidationResult  # noqa: E402


def fixture_bytes():
    case_id = "SYN-LOCK-001"
    input_case = {"schema_version": "1.0.0", "assessment_id": case_id}
    data = {"schema_version": "1.0.0", "case_set_id": "SYN-ONLY", "protocol_version": "1.0.0",
            "cases": [{"case_id": case_id, "input": input_case, "reference_category": "EXPERIMENTAL_EVIDENCE",
                       "independent_review_refs": ["review-a", "review-b"], "adjudication_reference": "adjudication-a"}]}
    return json.dumps(data, sort_keys=True).encode()


class Phase7CaseLockTests(unittest.TestCase):
    def test_exact_bytes_locked_as_candidate_but_never_approved(self):
        raw = fixture_bytes()
        with patch("prepare_phase7_case_lock.validate_draft_2020_12",
                   return_value=SchemaValidationResult("VALID", (), "synthetic-test-only")):
            lock = prepare_case_lock(raw, "synthetic-schema")
        self.assertEqual(lock["case_set_sha256_exact_bytes"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(lock["status"], "CANDIDATE_NOT_APPROVED")
        self.assertIsNone(lock["owner_approval_reference"])
        self.assertIsNone(lock["thresholds"])

    def test_unavailable_formal_schema_validation_fails_closed(self):
        with patch("prepare_phase7_case_lock.validate_draft_2020_12",
                   return_value=SchemaValidationResult("UNAVAILABLE", ("dependency missing",), None)):
            with self.assertRaisesRegex(ValueError, "formal schema validation failed or unavailable"):
                prepare_case_lock(fixture_bytes(), "schema")

    def test_malformed_utf8_and_duplicate_keys_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "not valid UTF-8 JSON"):
            prepare_case_lock(b"\xff", "schema")
        with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
            prepare_case_lock(b'{"case_set_id":"one","case_set_id":"two"}', "schema")

    def test_duplicate_case_ids_and_non_string_categories_are_rejected(self):
        raw = json.loads(fixture_bytes())
        raw["cases"].append(dict(raw["cases"][0]))
        valid_schema = SchemaValidationResult("VALID", (), "synthetic-test-only")
        with patch("prepare_phase7_case_lock.validate_draft_2020_12", return_value=valid_schema):
            with self.assertRaisesRegex(ValueError, "lacks unique identity"):
                prepare_case_lock(json.dumps(raw).encode(), "synthetic")
        raw = json.loads(fixture_bytes())
        raw["cases"][0]["reference_category"] = ["malformed"]
        with patch("prepare_phase7_case_lock.validate_draft_2020_12", return_value=valid_schema):
            with self.assertRaisesRegex(ValueError, "lacks unique identity"):
                prepare_case_lock(json.dumps(raw).encode(), "synthetic")


if __name__ == "__main__":
    unittest.main()
