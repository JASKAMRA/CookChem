# Changelog

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
