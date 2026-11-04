# Phase 4 validation report — working registry v0.1.2

- Application-level validation covers unique IDs, evidence-to-source references, identity status consistency, numeric/qualitative separation, and acceptance gates.
- Phase 3 context selector excludes all six evidence records: identity is name-only, applicability is context-limited, and review remains pending.
- Five measured numeric evidence rows preserve source units, means, SDs, ranges, condition codes, denominator caveat, and Table 1 locations; one qualitative statistical result is a distinct row.
- No record is accepted and no Phase 4 value is integrated into Phase 3 exposure calculations.
- Phase 4 release remains `IN_PROGRESS`; see the v0.1.2 release metadata for package checksums and validation status.
- Formal JSON Schema Draft 2020-12 validation is **NOT RUN** unless the declared `jsonschema>=4.18,<5` development dependency is available. Application-level tests do not substitute for metaschema validation.
