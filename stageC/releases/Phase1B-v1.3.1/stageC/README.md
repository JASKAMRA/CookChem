# CookRisk Stage C — Phase 1B closeout and Phase 2 start

The current Phase 1B successor is `Phase1B-v1.3.0`, based on the exact-manifest-verified `StageB_V20_20261103` snapshot. It contains 143 compounds: 130 identity-complete and 13 identity-pending; 584 food-composition records and 584 mappings; 125 unique identity-complete compounds with accepted quantitative food data.

The user accepted Phase 1B closure at 125/130. The approximate 120 target is met; the 130 minimum is five short. Five uncovered compounds stay explicitly documented. This closeout does not treat identity-only decisions, screening candidates, or non-quantitative evidence as food coverage.

Stage C Phase 1 remains the software foundation. Phase 2 has started with a read-only Stage A–Stage B identity crosswalk, a source-backed cooking-retention evidence ledger, and guarded interval arithmetic. The kickoff audit found no deployable fitted Stage A model artifact. OOF predictions are validation results and are not used as inference outputs. No cooked concentrations are generated until exact compound, matrix, condition, and measurement-basis compatibility are established.

Run `python3 scripts/validate_phase1.py` from this package root to validate the Phase 1 connector and food data. Phase 2 kickoff artifacts are under the repository-root `stageC/phase2/` and `stageC/reports/phase2/`.
