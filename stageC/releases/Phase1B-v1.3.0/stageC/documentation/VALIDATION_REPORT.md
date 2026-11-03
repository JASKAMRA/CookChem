# Phase 1B v1.3.0 validation

Clean-copy validation passed against StageB_V20_20261103: 143 compounds; 584 food records and 584 mappings; 125/130 identity-complete quantitative coverage; 13 identity-pending; nine inherited mapping rows remain blocked; zero food errors, zero mapping errors and zero snapshot changes. The release checksum verifier passed.

Focused current regression modules passed 48/48. The full inherited suite is not green: 70/86 passed, 14 fail and 2 setup errors because several tests pin earlier intermediate counts, release IDs, hashes or snapshot paths. Details are in `stageC/reports/phase1b/CLEAN_VALIDATION_AND_CHECK_REPORT.md`.
