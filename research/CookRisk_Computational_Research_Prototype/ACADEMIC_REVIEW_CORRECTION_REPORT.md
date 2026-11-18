# Academic Review Correction Report

## Scope

This documentation-only correction addresses independent review issues AR-01 through AR-07. No model training, experiment rerun, scientific validation test, dependency installation, dataset recalculation, or plot generation was performed. Saved numerical values and figure bytes were preserved. The historical Batch021 input file was not recovered, so its current-snapshot attribution remains blocked.

## Issue dispositions

| Issue | Original finding | Action and evidence | Files/sections changed | Status | Remaining limitation |
|---|---|---|---|---|---|
| AR-01 | The saved molecular-versus-source audit records input SHA-256 `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8`, while the current Batch021 CSV hashes to `d866d0ffab8c335e0469f2815c3cdf518b3d019be1bdf2e37ba2ced2e7d5d3c1`. The exact historical bytes are not available. | Searched 779 regular Stage A working-tree files for the recorded historical digest and checked available local archives; no byte-identical input or local zip/tar archive was found. Existing checksum/state records corroborate the historical expected digest, but do not contain the dataset bytes. Preserved the saved metrics and made their historical input hash and current-file mismatch explicit wherever the audit is presented. | `03_DATASET_AND_EVIDENCE_DEVELOPMENT.md` (Batch021 row); `05_EXISTING_ML_EXPERIMENTS.md` (fixed audit row); `06_VALIDATION_AND_GENERALIZATION.md` (audit note/table); `08_NEGATIVE_RESULTS_AND_LIMITATIONS.md`; `11_REPRODUCIBILITY_AND_EVIDENCE_REFERENCES.md`; `appendices/APPENDIX_C_STATUS_AND_ACCESS_BOUNDARIES.md`; `figures/FIGURE_SELECTION.csv` (figures 3–5); `figures/README.md`; `tables/EXISTING_METRICS_SELECTED.csv`; `ASSEMBLY_COMPLETION_REPORT.md`; this report and readiness assessment. | **BLOCKED** for dataset recovery and current-snapshot attribution; the documentation correction is complete. | Recover the exact file whose bytes hash to `111064…669c8`, with authoritative provenance, before asserting the saved audit represents the current CSV. Until then cite it only as a reported historical run. |
| AR-02 | Figure 3 is fold-wise R², includes a positive molecular-grouped fold, and must not be conflated with pooled R². | Caption now names the fold-wise view and notes one positive molecular fold. Pooled molecular-grouped (−0.067833) and DOI-held-out (−0.065645) R² are stated separately and marked as historical reported results with current-snapshot attribution blocked. Figure asset was not changed. | `06_VALIDATION_AND_GENERALIZATION.md`; `figures/FIGURE_SELECTION.csv`; `figures/README.md`; `ASSEMBLY_COMPLETION_REPORT.md`. | **PARTIALLY RESOLVED** | Interpretation is corrected; source-byte attribution remains blocked under AR-01. |
| AR-03 | Figure 2 showed only the top 15 of 32 DOI families, not all source families. | Figure 2 caption and package figure description now state “top 15 of 32 DOI families” and identify it as a partial view. | `figures/FIGURE_SELECTION.csv`; `figures/README.md`; `ASSEMBLY_COMPLETION_REPORT.md`. | **RESOLVED** | The omitted 17 families remain omitted from the original figure; no figure was regenerated. |
| AR-04 | Chapter 6/7 results lacked consistent row-level status, and the assembly report overstated that every result was labeled. | Chapter 6 audit rows distinguish `REPORTED` values from `BLOCKED/UNVERIFIED` current-snapshot attribution. Chapter 7 result rows carry explicit evidence status. Selected metrics catalog records status, and the assembly report now limits its statement to curated narrative tables and the figure catalog rather than claiming every repository result was re-audited. | `06_VALIDATION_AND_GENERALIZATION.md`; `07_FEATURE_ABLATION_AND_ERROR_ANALYSIS.md`; `tables/EXISTING_METRICS_SELECTED.csv`; `ASSEMBLY_COMPLETION_REPORT.md`. | **RESOLVED** for the curated package | This is a presentation correction, not an independent re-audit of every result in the repository. |
| AR-05 | “Five models were saved” could imply five serialized fitted estimators. | Wording now says five model evaluations are reported; the text distinguishes evaluation outputs from fitted/deployable artifacts. | `05_EXISTING_ML_EXPERIMENTS.md`. | **RESOLVED** | No deployable model or validated new-record inference is claimed. |
| AR-06 | ACR MAE/RMSE units were not explicit. | ACR MAE and RMSE are identified as **ACR percentage points**, not relative percentage error. Historical `Retention_Final` units remain unresolved rather than being inferred. | `05_EXISTING_ML_EXPERIMENTS.md`; `06_VALIDATION_AND_GENERALIZATION.md`; `07_FEATURE_ABLATION_AND_ERROR_ANALYSIS.md`; `appendices/APPENDIX_B_TERMS_AND_METRICS.md`; `tables/EXISTING_METRICS_SELECTED.csv`. | **RESOLVED** in curated numeric tables | Some narrative ACR descriptive statistics are percentages rather than prediction errors; they were left as reported. Historical `Retention_Final` scale remains unresolved. |
| AR-07 | Reproducibility language generalized beyond the narrow prior reproduction evidence. | Reproducibility claims now identify only the prior two-run 1,124-row `Retention_Final` benchmark in Python 3.12.14. They explicitly do not extend to ACR packages or the whole project; historical prediction equivalence remains blocked. | `02_RESEARCH_QUESTIONS.md`; `06_VALIDATION_AND_GENERALIZATION.md`; `09_SCIENTIFIC_CONTRIBUTIONS.md`; `11_REPRODUCIBILITY_AND_EVIDENCE_REFERENCES.md`; `appendices/APPENDIX_C_STATUS_AND_ACCESS_BOUNDARIES.md`; `ASSEMBLY_COMPLETION_REPORT.md`. | **RESOLVED** in the reviewed package | The prior report’s reproducibility evidence is cited, not rerun here; historical-vs-regenerated predictions remain discrepant. |

## Validation of this correction

- Checked curated Markdown references and CSV readability after editing.
- Confirmed all six packaged figure files retain the SHA-256 values recorded in `figures/FIGURE_SELECTION.csv`.
- Confirmed the original saved metric values were retained; status, units, and attribution text were changed without recalculation.
- No scientific experiment or test suite was run. This correction is not experimental validation.

## Files changed or created

Documentation/tables corrected:

- `01_RESEARCH_OVERVIEW.md`
- `02_RESEARCH_QUESTIONS.md`
- `03_DATASET_AND_EVIDENCE_DEVELOPMENT.md`
- `04_CONCENTRATION_AND_ACR_FINDINGS.md`
- `05_EXISTING_ML_EXPERIMENTS.md`
- `06_VALIDATION_AND_GENERALIZATION.md`
- `07_FEATURE_ABLATION_AND_ERROR_ANALYSIS.md`
- `08_NEGATIVE_RESULTS_AND_LIMITATIONS.md`
- `09_SCIENTIFIC_CONTRIBUTIONS.md`
- `11_REPRODUCIBILITY_AND_EVIDENCE_REFERENCES.md`
- `appendices/APPENDIX_B_TERMS_AND_METRICS.md`
- `appendices/APPENDIX_C_STATUS_AND_ACCESS_BOUNDARIES.md`
- `figures/FIGURE_SELECTION.csv`
- `figures/README.md`
- `tables/EXISTING_METRICS_SELECTED.csv`
- `ASSEMBLY_COMPLETION_REPORT.md`

Created:

- `ACADEMIC_REVIEW_CORRECTION_REPORT.md`
- `UPDATED_RESEARCH_READINESS_ASSESSMENT.md`

No dataset, model artifact, historical metric output, or original/curated figure image was changed.
