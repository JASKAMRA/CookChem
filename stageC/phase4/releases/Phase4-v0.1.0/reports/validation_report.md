# Phase 4 validation report — v0.1.0

- Application-level registry validation: planned and exercised in the Phase 4 unit tests. Checks duplicate IDs, evidence-to-source references, consistent identity status, numeric/qualitative separation, and acceptance gates.
- Phase 3 adapter gate: unresolved and pending evidence is excluded; only independently accepted context-only records with adjudicated identity and `APPLICABLE` scope can be returned. The adapter returns immutable copies and performs no exposure arithmetic.
- Versioned package manifest: every packaged artifact (excluding the manifest and its detached checksum) has a SHA-256 recorded in the manifest; the unit test recomputes each checksum.
- Draft 2020-12 JSON Schema validation: **NOT RUN in the current environment** because Python package `jsonschema` is not installed. `requirements-dev.txt` declares `jsonschema>=4.18,<5`; install it and rerun the Phase 4 tests for formal validation. JSON syntax parsing is not reported as schema validation.
- Scientific acceptance: zero records accepted. The record is abstract-only, name-only identity, context-limited, and pending second review.

The package is therefore `IN_PROGRESS`, not a complete or clinically accepted evidence release.
