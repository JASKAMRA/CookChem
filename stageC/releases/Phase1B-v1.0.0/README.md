# CookRisk Stage C — Phase 1B v1.0.0

This is a self-contained, reproducible snapshot of Stage C Phase 1B with the exact Stage B input package used for mapping. It includes 511 accepted quantitative ordinary-food records and mappings covering 109/119 Stage B targets. Ten ordinary-food gaps remain documented. Batch 100 stores contextual botanical measurements separately; they do not count as ordinary-food coverage.

## Inspect

- Final report: `stageC/reports/phase1b/PHASE1B_COMPLETION_REPORT.md`
- Accepted ordinary-food data: `stageC/data/food_composition/food_composition.csv`
- Compound-food mappings: `stageC/data/compound_food_mapping/compound_food_mapping.csv`
- Priority/search registers: `stageC/reports/phase1b/COMPOUND_PRIORITY_REGISTER.csv`, `SEARCH_LOG.csv`
- Final 10 target register: `stageC/reports/phase1b/coverage_gap_register.csv`
- Contextual values and scope: `stageC/reports/phase1b/batches/batch_100_contextual_reconciliation/`
- All 100 numbered source batches: `stageC/reports/phase1b/batches/`
- Stage B snapshot: `stageC/data/stage_b_snapshot_20261102/`

The active dataset has 491 primary analytical records, 15 authoritative food-composition database records, and 5 peer-reviewed secondary-source records. Source units, matrix state, method, and limitations stay with each row and batch note. Medicinal roots, supplements, extracts, and other contextual materials are not ordinary-food measurements.

## Reproduce checks

Run from this directory with Python 3.14 or compatible Python 3:

```sh
python3 verify_release.py
python3 stageC/scripts/inspect_stage_b.py
python3 stageC/scripts/validate_phase1.py
python3 -m unittest discover -s stageC/tests -v
python3 stageC/scripts/build_compound_mapping.py --composition stageC/data/food_composition/food_composition.csv --output /tmp/phase1b_mapping_rebuilt.csv --report /tmp/phase1b_mapping_coverage.json
cmp /tmp/phase1b_mapping_rebuilt.csv stageC/data/compound_food_mapping/compound_food_mapping.csv
```

`CHECKSUMS.json` covers every packaged artifact except itself and its detached digest. `CHECKSUMS.sha256` gives the digest of the checksum manifest. To regenerate both after an intentional package update, run `python3 build_checksums.py`, then verify again.

## Scope

Phase 1B does not apply Stage A cooking retention. It does not establish population dietary exposure, bioavailability, clinical effects, or health risk. Two final targets have no exact quantitative matrix value; missing is not zero. See the completion report for the explicit exit decision and inherited Stage B warnings.
