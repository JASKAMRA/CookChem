# Changelog

## 1.3.0 — 2026-11-03
- Updated the read-only connector to the exact-manifest-verified StageB_FINALIZED registry (143 compounds).
- Added registry-to-identity-audit consistency checks and guarded the authoritative source path.
- Created a versioned 143-compound snapshot path; preserved the earlier snapshots and all Phase 1B records and mappings.
- Added compound-reference and candidate-reference orphan checks, migration tests, and updated compatibility documentation.
- Kept unresolved identity and stereochemistry review items open; no food data or mapping was added.

## Phase1-v1.0.0

- Added checksum-verified, read-only Stage B connector and snapshot manifest.
- Added source-validated food-composition ingestion with preserved reported values and normalized mg/kg values.
- Added exact/synonym/identifier mapping with ambiguity and pending-identity safeguards.
- Added Decimal mass-based raw-food exposure calculations, serving and consumed-fraction handling, explicit-period aggregation, and provenance.
- Added integrity validation, CLI wrappers, schemas, scientific-integrity tests, documentation, and release manifest.
- No food concentration values were added because no qualifying dataset was available in the repository.

## Phase1-v1.1.0 (Phase 1B scientific data acquisition)

- Added four USDA Release 3.3 aggregate records for apple and unsweetened dry cocoa powder, with source values, units, table locators, sample counts, ranges, confidence codes, and limits retained.
- Added explicit `food ingredient` food-use classification; existing classifications and record columns remain backward compatible.
- Added ingredient eligibility regression and expanded integration coverage. No cooking, processing, recipe dilution, or retention factors are applied.

## Phase1B-v1.2.9 (2026-11-03)
- Batch 124 individually re-reviewed all five uncovered identity-complete compounds and recorded primary source decisions. Oroxylin A now has a directly verified table: positive root value is medicinal material; tea-use aerial parts are non-detects. No eligible new measurements; coverage remains 125/130.

## Phase1B-v1.3.0 (2026-11-03)
- Recorded user-approved Phase 1B closeout at 125/130 accepted quantitative food-covered compounds; the approximate 120 target is met and the 130 minimum remains five short.
- Updated current handoff/validation documents to the V20 and 584-record checkpoint.
- Phase 2 is authorized and started in the repository working tree with a strict identity crosswalk, observed-retention ledger, and gated interval arithmetic.
