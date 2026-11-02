# CookRisk Stage C

Stage C Phase 1 provides a read-only Stage B connector, traceable food-composition records, conservative compound mappings, unit normalization, raw-food exposure arithmetic, provenance, and validation. Cooking retention, recipe-level exposure validation, bioavailability, clinical effects, and risk calculations are outside Phase 1.

## Phase 1B data status

The current Phase 1B dataset contains **511 source-backed quantitative ordinary-food records** and **511 exact or reviewed compound mappings**, covering **109 of 119 Stage B compounds**. The remaining ten have no accepted ordinary-food measurements. Missing values stay missing and are never replaced with zero.

Separately, Batch 100 records contextual quantitative evidence for seven targets in medicinal *Scutellaria* roots and vegetative *Viburnum* tissues, plus a secondary-source irilone lead. Those measurements do not count as ordinary-food coverage or dietary exposure. Two targets still have no exact quantitative matrix value. See `reports/phase1b/PHASE1B_COMPLETION_REPORT.md` and `reports/phase1b/batches/batch_100_contextual_reconciliation/`.

Values retain source units and sample basis. Conversions are arithmetic only; the pipeline does not infer food density, fresh-weight equivalence, cooking retention, recipe dilution, or market/population representativeness. Study-specific experimental matrices are not automatically consumer foods.

## Validate and test

Run from the repository root with Python 3.14 or compatible Python 3:

```sh
python3 stageC/scripts/inspect_stage_b.py
python3 stageC/scripts/validate_phase1.py
python3 -m unittest discover -s stageC/tests -v
```

This directory is the Stage C component bundled in the Phase1B-v1.0.0 release. See the top-level `README.md` for clean-copy instructions and `CHECKSUMS.json` for artifact verification.
