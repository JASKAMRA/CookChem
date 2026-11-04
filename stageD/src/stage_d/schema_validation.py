"""Explicit Draft 2020-12 validation status, separate from app contracts."""
from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any


@dataclass(frozen=True)
class SchemaValidationResult:
    status: str
    errors: tuple[str, ...] = ()
    validator: str | None = None


def validate_draft_2020_12(instance: Any, schema_text: str) -> SchemaValidationResult:
    """Validate with jsonschema when present; never equate parsing with validation."""
    try:
        schema = json.loads(schema_text)
    except (TypeError, json.JSONDecodeError) as exc:
        return SchemaValidationResult("INVALID_SCHEMA", (str(exc),))
    try:
        from jsonschema import Draft202012Validator  # type: ignore[import-not-found]
    except ImportError:
        return SchemaValidationResult(
            "UNAVAILABLE",
            ("Install the repository-approved jsonschema dependency to run formal Draft 2020-12 validation.",),
        )
    try:
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        errors = tuple(
            f"{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
            for error in validator.iter_errors(instance)
        )
    except Exception as exc:
        return SchemaValidationResult("INVALID_SCHEMA", (str(exc),), "Draft202012Validator")
    return SchemaValidationResult("INVALID" if errors else "VALID", errors, "Draft202012Validator")
