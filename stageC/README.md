# CookRisk Stage C

## Current handoff

Phase 1B's authoritative closeout is the versioned [Phase1B-v1.3.0 release](releases/Phase1B-v1.3.0/README.md). It uses the V20 identity-adjudicated registry (143 total; 130 identity-complete; 13 pending), 584 food records/mappings, and 125 accepted quantitative food-covered compounds. The user accepted Phase 1B completion at 125/130: the approximate 120 target is met and the 130 minimum remains five short.

Phase 2 is active in `stageC/phase2/`. It includes an identity crosswalk and review ledger, separate observed-retention evidence, guarded interval arithmetic, and 117 source-transcribed raw/cooked group-mean concentration pairs for 24 analytes from two primary studies. These empirical pairs are not model predictions and are not joined to Phase 1B food concentrations. A frozen Stage B Extra Trees candidate exists, but its recorded training-input hash differs from the current Stage A input and the required runtime packages are unavailable; model inference remains blocked.

## Preserved Phase 1 working tree

The repository-root Phase 1 implementation remains the separately preserved `Phase1-v1.3.0` foundation connected to `StageB_FINALIZED`; it is not overwritten by the Phase1B V20 successor. Its older working-tree test fixtures and data are therefore not the Phase1B-v1.3.0 release dataset.

## Checks

The Phase1B-v1.3.0 package validator and manifest verifier pass. Phase 2 tests pass 9/9, and all 117 source-pair ratios match their Stage A retention fields within 0.01 percentage point. The earlier repository-wide suite ran 104 tests: 101 passed and three assertions remain pinned to earlier Phase1B working-tree counts (100 vs 101 coverage and 62 vs 63 source registry rows). Details are in `stageC/reports/phase2/PHASE2_KICKOFF_READINESS_AUDIT.md`.
