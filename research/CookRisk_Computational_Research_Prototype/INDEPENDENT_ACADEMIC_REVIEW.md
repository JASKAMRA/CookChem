# Independent Academic Quality Review

**Reviewed:** `research/CookRisk_Computational_Research_Prototype/`  
**Review type:** read-only academic and evidence-consistency review; this is not experimental validation.  
**Access boundary:** Stage B and restricted Stage C/D sources were not accessed.

## Verdict

# Requires substantial revision

The package is coherent, has a clear research question, maintains the distinction between ACR and total-mass retention, separates historical `Retention_Final` from ACR, and generally presents negative validation results and limitations honestly. Most checked numerical claims agree with their cited Stage A report or result table.

Before treating the package as professor-ready, its central molecular-versus-source validation results and associated figures need an explicit dataset-hash qualification. The saved validation summary records input SHA-256 `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8`; the current `stageA/dataset_expansion_1000/batch_021/updated_master_dataset.csv` hashes to `d866d0ffab8c335e0469f2815c3cdf518b3d019be1bdf2e37ba2ced2e7d5d3c1`. The saved audit's own script states that this hash is computed from the Batch021 CSV bytes. Until the exact input snapshot is located or the result is clearly scoped to the recorded historical hash, those metrics cannot be represented as verified results on the current Batch021 file. The package should then update figure captions/status labels and clarify whether the Stage A benchmark language means saved evaluation outputs or serialized model artifacts.

This verdict concerns research-result provenance and presentation, not whether the reported arithmetic in the saved metrics tables is correct.

## Review scope and method

Read all 11 chapters, all three appendices, both package result tables, the figure-selection records and all six selected image files, plus the assembly completion report. Cross-checked the package against the master inventory, full metrics catalog, gaps/limitations report, professor shortlist, and relevant original Stage A comparison tables, evaluation reports, manifests and validation scripts. Figure copies were checked against their original paths and recorded SHA-256 values. No files were changed before creating these two review outputs; no models, tests, or experiments were run.

## Findings

### Scientific accuracy and endpoint discipline

- The primary ACR formula is correctly stated as `100 × C_cooked / C_raw`; the text consistently says that ACR is a concentration ratio and not total-mass retention.
- Historical `Retention_Final` is kept distinct and described as unresolved in the historical contract. Cooked-concentration comparisons are also treated separately.
- The 1,124-row, 439-row, two separate 1,016-row families, 338-row strict subset, and evidence-tier datasets remain separated in the narrative and tables. Equal row counts are not used as proof of identity.
- The checked quantitative claims for the 1,124-row benchmark, v0.2–v0.6 ACR comparisons, 439-row prototype, 1,016-row reconstruction, 338-row strict subset, ACR distribution, and Batch021 fixed ExtraTrees summary agree with the cited saved result tables/reports to the displayed precision. The metrics catalog contains corresponding source rows for the principal cited comparisons.
- Negative source-held-out metrics, the historical prediction discrepancy, zero strict cross-source replication, and non-deployable model status are preserved. Conclusions do not claim clinical, nutritional, exposure, or cooking-advice utility.

### Attribution and reproducibility

- Prior reproduction is clearly distinguished from work performed during assembly. The package does not claim that results were freshly rerun.
- Historical benchmark fresh-run repeatability and its unresolved historical mismatch are described separately.
- The key limitation is narrower but important: the saved molecular-versus-source audit is tied by its own `validation_summary.json` to input SHA-256 `111064…`, while the currently available Batch021 CSV is `d866d0…`. The current document says “Batch021 master” without displaying the saved input hash. This prevents the reader from knowing whether the figures and scores represent current bytes or a prior snapshot. The reports remain **REPORTED** outputs, but their link to the current named snapshot is **BLOCKED/UNVERIFIED**.

### Figures, tables, and evidence labels

- All six copied figures are present, and their recorded SHA-256 values match their cited originals. The source paths are present and point to the referenced images.
- Figure 3 is a **fold-wise R² plot**, not a plot of pooled R². Its chart title makes that distinction, but the package selection caption emphasizes that the pooled scores are both negative without saying that the displayed fold-wise plot includes a positive molecular-grouped fold. The caption should explain the two views separately.
- Figure 2 uses `verified_concentration_ratio_reconstruction/eda_plots/source_counts.png`. Its source-generation code uses `.value_counts().head(15)`, while the reconstruction reports 32 DOI families. The current caption does not say that the plot shows only the top 15 of 32.
- Explicit status labels are not consistently attached to all numeric result tables: Chapter 6 and Chapter 7 tables present saved results but do not have a per-row `REPORTED` / `BLOCKED/UNVERIFIED` status. This conflicts with the completion report's statement that every result is labeled.
- Chapter 5 says “Five models were saved under” the benchmark split. The evidence cited is a model-comparison/OOF result table; the Stage A reproduction audit says no fitted Stage A deployment model was generated. Rephrase to “five model evaluations are reported” unless serialized fitted models are cited.
- ACR MAE/RMSE units are implied by the target but should be stated as ACR percentage points wherever those numbers are presented.

### Research narrative and academic suitability

The research question and supported contribution are clear: the project studies source-linked reported concentration changes and tests whether saved ML patterns transfer across compounds and research sources. Limitations are appropriately stated. The narrative is suitable as a research draft, but the hash-to-result mismatch is central to its strongest validation comparison; resolve or explicitly qualify it before presenting those figures as current-snapshot evidence.

## Issue register

The full actionable findings, evidence, impact, and recommendations are in `ACADEMIC_REVIEW_ISSUES.csv`. No scientific claim was silently corrected during this review.

## What this review did not establish

This review did not re-run any analysis, reproduce metrics, validate source measurements against original scientific literature, establish a canonical dataset, or determine the cause/date of the Batch021 hash mismatch. It did not inspect protected Stage B content or restricted Stage C/D sources. It should not be described as experimental validation.
