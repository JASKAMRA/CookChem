# Validation report

Validation checks food-record fields and units, duplicate IDs, reported/normalized consistency, mapping foreign keys and rationale, exposure output completeness, missing-as-zero violations, consumed-fraction bounds, and exclusion of retention/cooking methods. The repository database has zero food-composition rows and zero mappings; the empty database is valid and correctly reports missing quantitative data. The Stage B release manifest has 708 entries and is checksum-verified by the connector. Runtime validation results are recorded in `../reports/validation/phase1_validation.json` and `../reports/validation/stage_b_release_validation.json`.

The final validation status applies to structural and scientific-integrity checks only; it does not imply empirical food coverage.
