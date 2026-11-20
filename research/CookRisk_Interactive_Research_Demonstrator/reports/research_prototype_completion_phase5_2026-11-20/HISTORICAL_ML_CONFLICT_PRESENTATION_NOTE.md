# Historical ML Conflict Presentation Note

## Presentation rule

Historical outputs are evidence records, not a current benchmark run. The application displays each dataset/target/protocol family separately, with **Pooled OOF R²** and **Mean-fold R²** in distinct fields and each metric's evidence status adjacent to its value. The UI does not choose a winner, merge split protocols, or present a cross-dataset leaderboard.

## Tuned XGBoost — historical Stage A `Retention_Final`

| Saved record | Pooled OOF R² | Mean-fold R² | Status / evidence |
|---|---:|---:|---|
| Initial benchmark record | 0.2832468313018399 | 0.40037582421724 | Conflicting saved evidence; no original sidecar |
| Separate replay | 0.27579634550899224 | 0.394286907871563 | Conflicting saved evidence; replay artifacts/checksums match, input SHA absent |

Both records and their fold evidence exist. No cause, preferred version, or overwrite is established. Both target the historical 1,124-row `Retention_Final`; equation, scale, and units remain unresolved. The ambiguous QA JSON `R² = 0.380460979215581` matches Extra Trees mean-fold evidence and is not treated as a second pooled metric.

## Batch021 post1000 aggregate conflict

Three combined files have hashes that do not match their recorded aggregate pins: `post1000_model_comparison.csv`, `post1000_fold_metrics.csv`, and `post1000_oof_predictions.csv`. Of 21 component/combined comparison rows, 12 differ and nine agree numerically. The alternate-writer explanation is plausible but unverified. The app preserves the conflicting saved evidence, exposes the 3/12/9 counts, and does not repair the artifact, rank models, or claim overwrite.

## Other saved evidence that must remain distinct

- Batch021 fixed-audit Extra Trees is the saved ACR reference: molecular-grouped pooled/mean-fold R² −0.0678329296938553 / −0.256216157206555; DOI/source-held-out −0.0656453820532739 / −0.206526781706722. Both values are verified from saved records; no fresh training was run.
- Reconstruction reduced-feature XGBoost is a distinct saved ACR result. Its pooled values have incomplete output provenance; mean-fold values are verified from saved folds.
- The 338-row strict subset has saved mean-fold R² −2.46284508675258. Pooled R² is **NOT ASSESSABLE** because no pooled OOF artifact/value was located.
- Friend-reported pooled 0.3301 and mean-fold 0.2990 are **UNVERIFIED**; no dataset/model/split supporting record was found. They are not included as achieved model results.

Source-of-truth detail remains in `../final_model_r2_consolidation_2026-11-20/` and the associated conflict register. This note is a presentation summary; it does not modify or recreate scientific results.
