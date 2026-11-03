# CookRisk Stage C — Phase 1B v1.3.2 byte-integrity patch

This versioned successor records the user-accepted Phase 1B closeout and preserves the Phase1B-v1.2.9 dataset unchanged. It uses the read-only StageB_V20_20261103 registry: 143 total compounds, 130 identity-complete, 13 identity-pending. The dataset contains 584 food records and 584 mappings, with 116 scientifically eligible quantitative compounds across all food classes; 80 are eligible in ordinary food. The 125 identity-complete mapped IDs are a separate measure.

The earlier v1.3.0 closeout recorded 125 identity-complete mapped IDs as coverage. This successor distinguishes that from scientific quantitative eligibility: 116 compounds are eligible across all classes, including 80 ordinary-food compounds. The approximate 120 and 130 minimums are not met on the corrected eligibility measure. The prior v1.3.0 closeout authorization remains recorded; its 125 figure referred to identity-complete mapped IDs rather than scientifically eligible quantitative coverage. No data were forced to meet the 130 target.

- Phase 1B closeout: `stageC/reports/phase1b/PHASE1B_CLOSEOUT_2026-11-03.md`
- Phase 2 intake audit: `stageC/reports/phase2/PHASE2_KICKOFF_READINESS_AUDIT.md` (project-root development artifact)
- Validation/check audit: `stageC/reports/phase1b/CLEAN_VALIDATION_AND_CHECK_REPORT.md`

Phase 1 validator and package checksum pass. The earlier focused regression modules pass 48/48; the v1.3.2 reconciliation and embedded V20 byte-integrity tests pass 4/4. The embedded historical Phase1B suite ran 86 tests: 70 passed, 11 failed, and 5 errored. The remaining failures/errors are inherited assertions for earlier snapshots, checkpoints, counts, and IDs; the V20 byte-integrity test passes. The current repository Stage C suite separately passes 151/154 with three optional schema-validation skips. Stage A remains unchanged.


## Package integrity correction

Phase1B-v1.3.2 succeeds Phase1B-v1.3.1 without changing food values, mappings, identity decisions, or scientific conclusions. The embedded StageB_V20_20261103 package is restored from raw Git objects and matches all 839 entries in its own SHA256SUMS manifest.
