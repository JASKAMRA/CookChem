# CookRisk Stage C — Phase 1B v1.1.0

This versioned successor integrates the identity-adjudicated `StageB_V20_20261103` registry and the accepted, source-backed Phase 1B measurement batches through Batch 111. It contains **570 food-composition records**, **570 rebuilt mappings**, and quantitative coverage for **115 of 130 identity-complete compounds** in the 143-compound registry.

The user’s approximate 120 target is five compounds short; the previously specified 130 minimum is fifteen compounds short. The release closes this bounded continuation with that limitation stated explicitly. It does not claim the numerical target was achieved. `Phase1B-v1.0.0` and `Phase1-v1.3.0` remain unchanged.

## Inspect

- Closeout: `stageC/reports/phase1b/PHASE1B_CLOSEOUT_2026-11-03.md`
- Accepted food records: `stageC/data/food_composition/food_composition.csv`
- Rebuilt mappings: `stageC/data/compound_food_mapping/compound_food_mapping.csv`
- Validation: `stageC/reports/validation/phase1_validation.json`
- Batch 109–111 evidence and count proof: `stageC/reports/phase1b/batches/`
- Stage B V20 source package: `stageB/release/StageB_V20_20261103/`

## Verify

Run from this directory with Python 3:

```sh
python3 verify_release.py
python3 stageC/scripts/validate_phase1.py
```

The validation passed with zero food errors, zero mapping errors, nine inherited mapping rows blocked by identity review, thirteen identity-pending compounds, and zero Stage B snapshot changes. This release-building step did not run the full regression test suite.
