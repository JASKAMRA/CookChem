# Phase 1B progress

## Completed modules
- Baseline/checkpoint capture and immutable Stage B verification.
- USDA Release 3.3 screening for all ten P2-priority flavonoid/catechin candidates.
- Batch 001 apple and Batch 002 cocoa accepted aggregate records.
- Prepared-beverage category added consistently across schema, validation, mapping and exposure logic.
- Batch 003 USDA standardized green tea infusion: EGCG and theaflavin ingested, mapped, and exposure-tested.
- P2 held/rejected decisions, source limits, search logs and coverage reports updated.

## Remaining modules
- Continue P3/P4 source discovery. Immediate next target: retrieve official USDA SR Legacy April 2018 data and directly verify caffeine for NDB 14209 brewed coffee.
- Broaden measurement coverage only when analyte identity, food state, concentration basis and provenance are verifiable.
- Phase 2 remains deferred: no Stage C roadmap/specification was found in repository; no complete validated matched matrix/compound pairs are established for retention integration.

## Tests and checks
- Focused food, mapping, exposure and integration suite: 32 passed after Batch 003; no failures.
- Full unittest suite: 49 passed, 0 failed. Active validation: PASS (6 records, 6 mappings). Clean-copy test suite: 49 passed; clean-copy validation: PASS. Protected Stage A/Stage B/history checksum recheck: PASS.
- Active data validation: PASS, 6 records and 6 mappings.

## Known limitations
- Accepted quantitative coverage is 4/119 Stage B compounds.
- Tea ref 272 is unpublished USDA source material (N=2); underlying analytic method and sample details are unavailable.
- USDA parsley/citrus values are held when they may represent glycoside-to-aglycone equivalents; parsley isorhamnetin is measured zero and not ingested.
- Caffeine SR Legacy value awaits direct extraction from an official USDA file.
- No cooking-retention, recipe, bioavailability, clinical or Stage D interpretation.
