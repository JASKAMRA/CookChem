# Stage C Phase 2 Completion Report — v0.1.0

## A. Executive summary

A reproducible integration release was built, but Phase 2 is **NOT COMPLETE**. The release joins and classifies all 584 Phase 1B measurement rows, keeps non-ordinary ingredient/beverage records separate, records explicit identity status, validates all 117 source-published group-mean cooking ratios, and refuses unsupported retention adjustment.

## B. Starting status

Phase 1B input: 584 rows from Phase1B-v1.3.0. Existing Phase 2 intake: 117 experimental cooking pairs over 24 analytes; 4 Stage B retention records (3 quantitative intervals and 1 qualitative record); 45 identity candidates plus 19 strict crosswalks and one Curcumin CID discrepancy.

## C. Identity resolution

Strict accepted Stage A–B matches: 19. Manual-review match accepted: 1 (Curcumin). Possible matches: 27. Identity conflicts: 9. Unresolved: 9 plus non-strict crosswalk rows. Candidate review records were not auto-promoted. Curcumin is linked by the same stable molecular ID, canonical name, and canonical SMILES, while the Stage A raw CID 55215 vs Stage B/PubChem CID 969516 discrepancy is preserved as a warning; the CID itself is not used as a join key.

## D. Food concentration integration

All Phase 1B rows integrated: 584. Ordinary-food eligible rows: 335. Food ingredient/prepared beverage records are kept separately: 249. Quantitative original/normalized values, units, basis, edible part, source, and mapping statuses are retained. Rows without a confirmed Stage A–B link remain available as Phase 1B raw concentration data but cannot enter cross-phase retention joins.

## E. Experimental cooking pairs

117 group-mean pairs across 24 analytes: 33 curcuminoid pairs in fresh turmeric rhizome and 84 pumpkin-leaf phytochemical/amino-acid pairs. Ratios are cooked concentration divided by raw concentration and are labeled apparent concentration ratios, not mass retention. Group means are not individually paired replicates. Source links and locators are included per record.

## F. Cooked concentration integration

Valid retention-adjusted cooked concentration outputs: 0; interval outputs: 0; qualitative-only records: 1; Phase 1B rows marked unavailable or not applied: 584. The three numeric Stage B intervals were not applied to potential turmeric/pepper rows because the study matrix, sample state, condition, and analytical basis are not sufficiently compatible with the Phase 1B measurements. Missing retention is never treated as 100%.

## G. Model inference

Frozen Stage B model validated for inference: no. Inference run: no. Its artifact checksum matches its own manifest, but its recorded training-input hash differs from current Stage A (`BLOCKED: frozen artifact input hash differs from current Stage A data hash; required runtime unavailable; no inference performed`); dependencies are also absent. Stage A OOF predictions were not used for inference.

## H. Validation and tests

Build-time integrity: 117/117 ratios recalculated from group means and matched stored values within 0.011 percentage points; negative/non-positive raw concentration check passed for all source pairs; all 584 rows were emitted exactly once. Phase 2 tests: 14 passed. Full Stage C suite: 110 passed, 3 failed (stale Phase 1B coverage expectation 100 vs 101; Phase 1B source-registry checkpoint 62 vs active 63; corresponding continuation coverage expectation 100 vs 101). The three assertions concern the pre-existing Phase 1B working tree; none are Phase 2 failures.

## I. Limitations and remaining work

The key missing scientific connection is compatible ordinary-food raw values and cooking evidence for the same food part/state, process, and analytical basis. Most Phase 1B rows are foods not represented among the two experimental matrices. Identity candidates remain unresolved without structure-complete evidence. The frozen model cannot be used until its source snapshot and runtime are reconciled. No recipes, meal exposure, bioavailability, or health-risk calculations are in scope.

## J. Exit decision

**NOT COMPLETE.** The tables and guarded reproducible pipeline are released as v0.1.0, but valid retention-based cooked concentration outputs and validated model inference are both zero.
