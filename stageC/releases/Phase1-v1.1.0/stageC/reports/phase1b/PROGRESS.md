# Phase 1B progress

## Completed modules
- Baseline/checkpoint capture and immutable Stage B verification.
- USDA Release 3.3 discovery/screening framework and 119-compound priority register.
- Batch 001 apple catechin/epicatechin ingestion and exposure calculations.
- Backward-compatible `food ingredient` classification across schema, validation, mapping, exposure, and regression tests.
- Batch 002 cocoa catechin/epicatechin ingestion and exposure calculations.
- Search, source, mapping, coverage, acceptance, exposure, recovery, and resume reports.

## Remaining modules
- Expand source discovery beyond the current four accepted measurements and resolve two held candidates if evidence permits; detailed prioritized resume tasks are in `NEXT_STEPS.md`. This is the next research checkpoint, not completed work.
- Versioned Phase 1B release packaging and packaged-copy validation completed.

## Tests and checks
- Focused food/mapping/exposure tests: 27 passed.
- Full unittest suite: 47 passed, 0 failed. One initial run failed only because a pre-expansion integration assertion expected two rows; the assertion was corrected to cover all four records and the rerun passed.
- Active data validation: PASS (4 records, 4 mappings, no integrity errors).
- Cocoa independent formula check: PASS (2/2). Clean-copy suite and validation: PASS. Protected baseline: PASS.

## Known limitations/blockers
- Only 2 of 119 Stage B compounds have accepted quantitative food data.
- USDA source-reference IDs behind aggregate summaries were not retraced to individual papers; underlying Access dataset not accessed.
- Stage B warning V11-W02 remains relevant to catechin/epicatechin identity adjudication; entries are separate and not merged.
- No processing, recipe dilution, cooking retention, bioavailability, or health-risk interpretation.

## Remaining work
- Stable checkpoint preserved. Broader analyte-by-analyte evidence expansion remains; do not infer coverage for the 117 compounds without accepted quantitative measurements.
