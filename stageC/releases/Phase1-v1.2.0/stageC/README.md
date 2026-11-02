# CookRisk Stage C Phase 1

Stage C Phase 1 is a Python backend for read-only Stage B integration, traceable food-composition ingestion, conservative compound-to-food mapping, mass-unit normalization, and raw-food exposure arithmetic. It does not estimate cooking retention, clinical effects, or risk.

## Current scientific data status

Phase 1B adds four USDA Flavonoid Database Release 3.3 aggregate measurements: catechin and epicatechin in raw apple with skin and unsweetened dry cocoa powder. These map exactly by stereospecific canonical names to two Stage B compounds. The database values are population aggregates, not lot-specific values or individual-study results; source and basis limitations are documented in `reports/phase1b/`. A numerical Phase 1 estimate is available when the user supplies a food mass and consumed fraction. Missing concentrations remain missing and are never interpreted as zero. Synthetic records are used only by tests and are labelled as such.

## Use

Run from the repository root with Python 3.14 (the implementation uses the standard library):

```powershell
py -3.14 stageC/scripts/inspect_stage_b.py
py -3.14 stageC/scripts/ingest_food_data.py path\to\verified_food_composition.csv
py -3.14 stageC/scripts/build_compound_mapping.py
py -3.14 stageC/scripts/run_exposure.py path\to\ingredients.json
py -3.14 stageC/scripts/validate_phase1.py
py -3.14 -m unittest discover -s stageC/tests -v
```

Food data must match the header in `data/food_composition/food_composition.csv`; source fields, identity checks, state, moisture basis, classification, and verification status are validated. Food-use classifications include `ordinary food` and `food ingredient`; both permit mass-based composition arithmetic, with no inferred cooking, recipe dilution, or retention adjustment. The exposure command accepts JSON with an `ingredients` array (or a list) and writes auditable JSON by default. See `documentation/` for field, method, provenance, and limitation details.

## Status

Software core: implemented and testable. Phase 1B data coverage is intentionally narrow: 4 accepted food records for 2 of 119 Stage B compounds. Release status and test evidence are in `reports/`.
