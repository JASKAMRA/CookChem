# Evidence and Data Selection

## Record-level dataset selected

The demonstrator's record-level explorer uses the existing Stage A file:

- Path: `stageA/verified_concentration_ratio_reconstruction/final_verified_master_dataset.csv`
- SHA-256 over current file bytes: `16dbbd9c38a21675a2644b415289004e5a8eb7091e97a96dae645ed2bf52be99`
- Rows: 1,016
- Target field: `target_value_percent`; documented equation `100 * cooked_concentration / raw_concentration`
- Supporting package files: `manifest.json`, `source_provenance_manifest.csv`, `final_dataset_eda_report.md`, `model_evaluation_report.md`
- Demonstrator evidence label: **REPORTED; current demonstrator file hash pinned; not owner-designated canonical; no new scientific validation performed**.

The file's hash is pinned in `research_data.py` so a changed file is not silently presented as the same snapshot. The demonstrator copies no dataset into its own folder and writes no changes to this Stage A source. This pinned hash is a demonstrator integrity control, not owner approval or a scientific endorsement.

## Separate dataset families

| Family | Target / identity | Demonstrator treatment | Provenance status |
|---|---|---|---|
| Historical benchmark, 1,124 rows | `Retention_Final`; not established as ACR | Saved metrics only | Input hash is documented; historical-vs-regenerated predictions remain discrepant. Prior repeated-run evidence is limited to this benchmark pipeline. |
| 439-row final-prototype family | ACR; 10 DOI families reported | Saved metrics only | Manifest parent hash does not establish linkage to current data bytes; BLOCKED/UNVERIFIED. |
| Batch021 master | ACR; current CSV SHA-256 `d866d0ffab8c335e0469f2815c3cdf518b3d019be1bdf2e37ba2ced2e7d5d3c1` | Status and saved results only; record-level source CSV is not loaded | The separate molecular/source audit records historical input SHA-256 `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8`; exact historical input unavailable. Current attribution BLOCKED/UNVERIFIED. |
| Verified concentration-ratio reconstruction | ACR; separate 1,016-row package | Selected record-level explorer | Its current bytes are pinned for this demonstrator. Equal row count does not establish identity with Batch021. |
| Strict 338-row source-verified subset | ACR; distinct inclusion tier | Summary/metric documentation only | No independent hash-pinned record table selected for this app. |
| Other recovery versions / evidence tiers | ACR; version-specific targets, filters, and evidence | Shown in documentation/catalog only | Not merged or presented as a single time series. |

No canonical ACR dataset is designated. No metrics are pooled across dataset families or target definitions.

## Metric sources shown

- Curated selected metrics: `research/CookRisk_Computational_Research_Prototype/tables/EXISTING_METRICS_SELECTED.csv`.
- Batch021 pooled validation summary: `stageA/molecular_vs_source_validation_audit/validation_summary.json` (reference only; the UI shows values copied into the academic review text and displays the saved fold table from the same audit).
- Batch021 fold-wise values: `stageA/molecular_vs_source_validation_audit/fold_metrics.csv`.

All saved ML values are labeled REPORTED unless a prior report specifically establishes reproduction. The demonstrator performs no model training, inference, or metric recalculation.
