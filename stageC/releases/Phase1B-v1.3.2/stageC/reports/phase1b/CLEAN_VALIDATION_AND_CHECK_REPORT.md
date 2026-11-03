# Clean validation and check report — Phase1B-v1.2.9

Audit date: 2026-11-03. Checks were run from a fresh temporary copy of this release package, leaving the project working tree and source release data unchanged.

## Results

- Release checksum verification: **PASS**, 1,320 package artifacts; manifest SHA-256 `54604bce2cbc073864bcdd85a38dbe11025d79e70ca6caa5fe8b6a359eeff183` at audit start.
- Phase 1 data validator: **PASS**; 143 Stage B compounds; 584 food records and 584 mappings; 125/130 identity-complete quantitative coverage; zero food errors, mapping errors, or Stage B snapshot changes; 13 identity review items; nine inherited mapping rows remain blocked by identity review.
- Current, data-independent regression modules (CLI, mapping, exposure, food composition, provenance, unit conversion, validation): **48/48 PASS**.
- Full embedded Phase1B suite: **70/86 passed, 11 failed, 5 errored**. Remaining failures/errors expect earlier snapshot paths, checkpoint fields, counts, release IDs, and historical batch states. The v1.3.2 embedded V20 data itself matches all 839 manifest-listed raw Git bytes; these inherited assertions were not edited or suppressed.

The data validation and release integrity gates pass. The complete regression suite is **not green** until its historical fixtures and pinned expectations are reconciled with the current Stage B V20 and Phase 1B state. Python's built-in `unittest` runner was used; `pytest` is not installed in this environment.

## Commands

```text
python3 verify_release.py
python3 stageC/scripts/validate_phase1.py
python3 -m unittest discover -s stageC/tests -p 'test_*.py' -v
python3 -m unittest -v test_cli test_compound_mapping test_exposure_engine test_food_composition test_provenance test_unit_conversion test_validation
```
