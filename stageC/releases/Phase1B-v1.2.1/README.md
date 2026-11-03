# CookRisk Stage C — Phase 1B v1.2.1

Validated successor to Phase1B-v1.2.0. It integrates StageB_V20_20261103, accepted primary-source food measurements through Batch 115, 579 food-composition records, 579 rebuilt mappings, and **120/130** identity-complete compounds with accepted quantitative ordinary-food data. Thirteen of 143 registry compounds remain identity-pending.

Batch 115 adds the NHDC hard-candy market-survey summary (11 ± 10 mg/kg; three detections, only one above LOQ), with its censoring and LOQ/2 imputation limitation documented. This reaches the approximate 120 marker; the minimum target of 130 remains ten short. Batch 114 logs the original 11 gap decisions; Batch 115 updates NHDC, leaving ten identity-complete compounds without accepted data. This package is a validated progress checkpoint, not a target-complete closeout. Phase1B-v1.2.0, Phase1-v1.3.0, and StageB V20 remain unchanged.

## Inspect

- Progress and remaining gaps: `stageC/reports/phase1b/PHASE1B_PROGRESS_2026-11-03.md`
- Batch 115 decision: `stageC/reports/phase1b/batches/batch_115_italian_hard_candy_nhdc/SCREENING_REPORT.md`
- Accepted records: `stageC/data/food_composition/food_composition.csv`
- Rebuilt mappings: `stageC/data/compound_food_mapping/compound_food_mapping.csv`
- Validator output: `stageC/reports/validation/phase1_validation.json`

Phase 1 validation passes with zero food errors, zero mapping errors, and zero Stage B snapshot changes. The full regression suite was not run.
