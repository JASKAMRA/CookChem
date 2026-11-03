# Stage C Phase 1B closeout — 2026-11-03

## Decision

The bounded Phase 1B continuation is closed at the best evidence currently validated in the StageB_V20 successor probe. The verified accepted quantitative ordinary-food coverage is **115 of 130 identity-complete compounds** in a 143-compound registry. This is five short of the user's approximate 120 target and fifteen short of the earlier 130 minimum. The target is **not achieved**; the numerical result is reported as-is.

## Counts

| Measure | Count |
|---|---:|
| Total Stage B compounds in V20 registry | 143 |
| Identity-complete after V20 adjudication | 130 |
| Identity-pending | 13 |
| Compounds with accepted quantitative ordinary-food measurements | 115 |
| Identity-complete compounds still without accepted quantitative measurements | 15 |
| Active food-composition records in isolated successor probe | 570 |
| Rebuilt food-compound mappings in isolated successor probe | 570 |

The accepted count is unique compounds, not the number of rows or observations. Batch 109 added vanillic acid and sinensetin; Batch 110 added BHT; Batch 111 added all-trans-β-carotene. The cumulative clean Phase 1 validation passed with zero food errors, zero mapping errors and zero Stage B snapshot changes. Nine inherited mapping rows remain blocked by identity review.

## Scope and integrity

This successor uses the separately versioned StageB_V20_20261103 identity-adjudicated registry. The counts do not apply to the active StageB_FINALIZED working-tree connector, which remains preserved. Stage A, StageB_FINALIZED, and Phase1-v1.3.0 were not modified. Historical Phase1B-v1.0.0 remains unchanged. All accepted records retain the source's food matrix, analytical basis, unit and uncertainty; dry-weight values were not converted to fresh weight, and ginkgo spiked standards, medicinal-botanical-only leads, and inaccessible/unverified numeric tables remain excluded.

## Remaining evidence gaps

Fifteen identity-complete compounds remain uncovered. The 13 identity-pending compounds remain separate and do not count toward the quantitative coverage. The 120 and 130 thresholds cannot be declared met from candidates, permitted-use limits, method-validation spikes, structural analogues, or values without retrievable exact numeric source rows.

## Reproducibility

The clean V20 probe validation is preserved with Batch 111 in `batches/batch_111_all_trans_beta_carotene_sweet_potato/coverage_count_proof.json`. The versioned Phase 1B successor release records its complete checksums and validation result. No Stage A outputs or cooking-retention data are part of this closeout.
