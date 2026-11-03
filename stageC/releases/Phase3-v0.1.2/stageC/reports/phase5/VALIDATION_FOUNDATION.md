# Stage C Phase 5 — Validation Foundation

## Scope

This additive framework distinguishes arithmetic/software checks, comparisons with published data, and external scientific validation. It does not modify the Phase 3 calculation engine or CLI. The legacy Phase 1 validation functions remain available to existing callers.

## Implemented

- `src/stage_c/validation.py` includes an independent, Decimal-based hand calculation for supported mass- and volume-concentration units. It rejects mass/volume dimension mismatches and performs no implicit density conversion.
- `verify_phase3_ingredient_arithmetic()` recomputes raw and consumed amounts from normalized Phase 3 provenance; for cooked intervals it separately checks both exposure bounds using the recorded Phase 2 source evidence.
- `verify_phase3_aggregate_arithmetic()` checks Phase 3 recipe and meal compound totals by recomputing sums from ingredient results. Missing contributions must continue to block complete totals.
- `compare_to_reference()` allows a published-data comparison only with a reference ID, source reference, matching unit, and matching measurement basis. Incomparable records are rejected and are excluded from numeric comparison metrics.
- `summarize_validation()` keeps validation layers separate and requires source metadata for published comparisons. It rejects an external-validation `PASS`/`FAIL` claim from this arithmetic framework.

## Evidence boundaries

The Phase 3 arithmetic checks independently apply basic Decimal formulas to normalized inputs already present in Phase 3 results. They can expose calculation or aggregation mistakes, but they do not independently authenticate food-composition values, validate source extraction, or prove that the chosen inputs represent real-world consumption.

No published dataset was compared as part of this implementation. No external scientific validation was conducted. Accordingly, this report makes no published-data agreement or external-validation claim. Published-comparison metrics remain empty until commensurate published reference data are actually recorded and compared.

## Tests

`tests/test_phase4_phase5_foundations.py` covers manual mass/volume arithmetic, incompatible units and basis, real Phase 3 raw/cooked arithmetic, tamper detection, recipe/meal aggregation, mandatory published-reference metadata, separation of validation layers, and rejection of an external-validation claim. Its scientific fixtures are synthetic test data.
