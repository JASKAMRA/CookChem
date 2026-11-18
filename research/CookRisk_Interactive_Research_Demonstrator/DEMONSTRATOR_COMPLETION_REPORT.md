# Demonstrator Completion Report

## Built

Created a local Streamlit academic research demonstrator with eight navigable modules:

1. Research overview, title, question, ACR definition, workflow, and non-claims.
2. Evidence explorer for the pinned reconstruction, with food, compound, method, and DOI filters and source-context columns.
3. Interactive ACR distributions, filtered descriptive summaries, counts below/equal/above 100%, and outlier-preserving plots.
4. Descriptive cooking, compound, food, and DOI group views with a minimum-support filter.
5. Existing saved ML metric catalog filtered by result family, target, and validation design.
6. Validation lab separating pooled R² from fold-wise R² and highlighting the Batch021 hash mismatch.
7. Scientific limitations.
8. Reproducibility, dataset-family status, and local source references.

## Data sources and integrity

No dataset was copied into the demonstrator folder. The record-level explorer reads the existing Stage A file `stageA/verified_concentration_ratio_reconstruction/final_verified_master_dataset.csv` in read-only mode. Current SHA-256 is pinned as `16dbbd9c38a21675a2644b415289004e5a8eb7091e97a96dae645ed2bf52be99`; the app checks this exact hash and the 1,016-row count before displaying it. The reconstruction is presented as a distinct, REPORTED evidence family, not as a canonical ACR dataset or as identical to Batch021.

Saved metrics come from `research/CookRisk_Computational_Research_Prototype/tables/EXISTING_METRICS_SELECTED.csv`. Fold values come from `stageA/molecular_vs_source_validation_audit/fold_metrics.csv`. The demonstrator displays those results as reported historical evidence and does not train models, load fitted models, infer predictions, or recalculate ML metrics.

The Batch021 audit is labeled **REPORTED HISTORICAL RESULT — CURRENT SNAPSHOT ATTRIBUTION BLOCKED/UNVERIFIED**. Historical audit input SHA-256: `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8`. Current Batch021 CSV SHA-256: `d866d0ffab8c335e0469f2815c3cdf518b3d019be1bdf2e37ba2ced2e7d5d3c1`. The 439-row family is separately shown with its unresolved manifest parent-hash linkage. The 1,124-row `Retention_Final` target remains separate from ACR.

## Interactive figures

- ACR histogram and box plot, with all outliers retained.
- Counts below, equal to, and above 100% for the active filtered data.
- Box plots by selected recorded method, compound, food matrix, or DOI family when groups meet the selected minimum support.
- Saved model metric bars only after selecting exactly one result family and one target; rows are never pooled across snapshots or target definitions.
- Saved fold-wise R² by validation strategy, shown separately from the reported pooled values.

## Launch instructions

From `research/CookRisk_Interactive_Research_Demonstrator/`, create a dedicated virtual environment, activate it, run `python -m pip install -r requirements.txt`, and then run `streamlit run app.py`. The app URL is printed by Streamlit and is normally `http://localhost:8501`. Full commands for macOS/Linux and Windows PowerShell are in `README.md`.

## Software checks performed

- Python syntax compilation for the source modules.
- Read-only load and validation of the pinned ACR dataset hash, row count, required columns, and record structure.
- CSV parsing checks for the metric and dataset catalogs and fold-metric source.
- Static reference checks for the documented local evidence paths.

Streamlit and Plotly are not installed in the current Python environment. No dependency was installed, and the live Streamlit UI/browser was not run in this cycle. The application can be launched after creating the documented dedicated environment and installing `requirements.txt`.

## Limitations and deliberately absent features

- No model training, scientific experiment, scientific validation, or historical metric recalculation was performed.
- No predictor, fitted-model loading, new-record prediction, risk score, cooking advice, authentication, database, API, cloud deployment, or production infrastructure is provided.
- The selected reconstruction is not canonical and has no owner designation.
- Historical Batch021 validation attribution and 439-row prototype parent linkage remain blocked/unverified.
- ACR is not total-mass retention, bioavailability, human exposure, clinical risk, or a causal cooking effect.
- Local documentation paths are shown for inspection in the repository; the browser does not expose them as remote links.

## Files created

- `app.py`
- `research_data.py`
- `requirements.txt`
- `README.md`
- `docs/EVIDENCE_AND_DATA_SELECTION.md`
- `DEMONSTRATOR_COMPLETION_REPORT.md`

No existing research prototype files, scientific datasets, historical metrics, model artifacts, or figures were modified by this demonstrator build. No Stage B or restricted Stage C/D content was accessed.
