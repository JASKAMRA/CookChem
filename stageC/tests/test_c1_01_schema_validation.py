"""Focused Draft 2020-12 fixtures for the C1-01 validation environment.

These use only in-memory URI registries. No HTTP/network reference retrieval is
configured, so an unregistered external $ref must fail closed.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, FormatChecker, SchemaError, ValidationError
    from referencing import Registry, Resource
except ImportError:
    Draft202012Validator = None
    FormatChecker = None
    SchemaError = ValidationError = None
    Registry = Resource = None


FIXTURES = Path(__file__).parent / "fixtures" / "c1_01_schema_validation"
ROOT_URI = "https://cookrisk.invalid/schemas/root.schema.json"
MEASUREMENT_URI = "https://cookrisk.invalid/schemas/measurement.schema.json"


def _read_json(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@unittest.skipUnless(
    Draft202012Validator is not None and Registry is not None and Resource is not None,
    "C1-01 BLOCKED: approved jsonschema/referencing environment is unavailable",
)
class Draft202012C101Tests(unittest.TestCase):
    def _validator(self):
        root = _read_json("root.schema.json")
        measurement = _read_json("measurement.schema.json")
        registry = Registry().with_resource(
            MEASUREMENT_URI,
            Resource.from_contents(measurement),
        )
        Draft202012Validator.check_schema(root)
        Draft202012Validator.check_schema(measurement)
        return Draft202012Validator(root, registry=registry, format_checker=FormatChecker())

    def test_positive_fixture_passes_internal_and_cross_file_refs(self):
        self._validator().validate(_read_json("valid_measurement.json"))

    def test_negative_data_fixture_fails_closed(self):
        validator = self._validator()
        instance = _read_json("invalid_measurement.json")
        self.assertFalse(validator.is_valid(instance))
        with self.assertRaises(ValidationError):
            validator.validate(instance)

    def test_invalid_schema_fixture_is_rejected(self):
        with self.assertRaises(SchemaError):
            Draft202012Validator.check_schema(_read_json("invalid_schema.json"))

    def test_uri_and_date_time_format_checkers_are_present_and_reject_invalid_values(self):
        checker = FormatChecker()
        missing_checkers = {"uri", "date-time"} - set(checker.checkers)
        self.assertFalse(missing_checkers, f"format-validation dependencies missing: {sorted(missing_checkers)}")
        with self.assertRaises(ValidationError):
            self._validator().validate(_read_json("invalid_format.json"))

    def test_cross_file_reference_without_registered_resource_fails_closed(self):
        schema = _read_json("unresolved_ref.schema.json")
        validator = Draft202012Validator(schema, registry=Registry())
        with self.assertRaises(Exception) as caught:
            validator.validate({"measurement": {"value": 2, "unit": "mg/kg"}})
        self.assertIn("missing.schema.json", str(caught.exception))

    def test_invalid_cross_file_referenced_data_is_rejected(self):
        validator = self._validator()
        invalid_measurement = _read_json("invalid_measurement.json")
        with self.assertRaises(ValidationError):
            validator.validate(invalid_measurement)


if __name__ == "__main__":
    unittest.main()
