# CookRisk Interactive Research Demonstrator

A local, read-only Streamlit demonstrator for presenting existing CookRisk research evidence. It is not a product, validated predictor, deployment platform, risk-scoring system, or source of cooking advice.

## Run locally

From the repository root:

```bash
cd research/CookRisk_Interactive_Research_Demonstrator
python3 -m venv .venv
source .venv/bin/activate          # macOS/Linux
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL printed by Streamlit (normally `http://localhost:8501`). The demonstrator reads source files in the existing repository; run it from this checkout and do not move this folder out of the repository. The dedicated `.venv` keeps dependencies separate from the project's existing environments. No dependency was installed as part of creating this demonstrator.

## Data and evidence handling

The record-level explorer uses only:

`stageA/verified_concentration_ratio_reconstruction/final_verified_master_dataset.csv`

The application verifies its exact SHA-256 (`16dbbd9c38a21675a2644b415289004e5a8eb7091e97a96dae645ed2bf52be99`) and 1,016-row count before displaying records. It reads the source CSV without writing to it. If the bytes or row count differ, the record-level views fail closed with an explanation. The file is **not** owner-designated as the canonical ACR dataset and is not presented as interchangeable with the Batch021 master.

The app reads the academic prototype's curated `EXISTING_METRICS_SELECTED.csv`, `DATASET_SNAPSHOT_CATALOG.csv`, and the saved Stage A molecular-versus-source `fold_metrics.csv`. Those are displayed as saved evidence, not recalculated. The Batch021 audit prominently records historical input SHA-256 `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8` and current Batch021 CSV SHA-256 `d866d0ffab8c335e0469f2815c3cdf518b3d019be1bdf2e37ba2ced2e7d5d3c1`; current-snapshot attribution remains BLOCKED/UNVERIFIED.

The app does not load the historical 1,124-row or 439-row records into the evidence explorer. It shows their documented metrics and status separately. The 338-row strict subset and other recovery versions are also kept separate. No records are merged, normalized, converted, imputed, or silently removed.

## Modules

1. Research overview and scientific boundaries.
2. Evidence explorer with food, compound, method, and DOI filters and source-linked rows.
3. ACR distribution, summary counts, and retained outlier views.
4. Descriptive distributions by available cooking/compound/food/source categories, with a minimum group-size control.
5. Saved ML result catalog with filters for result family, target, and evaluation design.
6. Validation lab showing saved fold-wise values separately from pooled R² and prominently marking the Batch021 hash limitation.
7. Scientific limitations.
8. Reproducibility and evidence references.

ACR summaries in the ACR module are simple interactive descriptive summaries of the loaded stored `target_value_percent` values. They are not historical ML metrics or scientific validation. Model comparison metrics are displayed only from saved result tables; no models are trained or used for new-record inference.

## Dependencies and checks

Dependencies are limited to Streamlit and Plotly as listed in `requirements.txt`. Use a new virtual environment, not a global install and not a frozen project environment. No installation was performed during implementation because neither dependency is available in the current Python environment.

Basic syntax and read-only data integrity checks can be run from this folder:

```bash
python -m py_compile app.py research_data.py
python -c "from research_data import load_acr_dataset; rows, digest = load_acr_dataset(); print(len(rows), digest)"
```

The second command verifies the pinned CSV hash and row count. It does not train or validate a scientific model.

## Limitations

- The Batch021 saved validation audit's historical input bytes have not been recovered.
- The selected reconstruction's file hash pins the demonstrator's current source bytes; it does not make the file canonical or establish independent scientific validation.
- The 439-row family retains its parent-hash limitation.
- DOI-held-out is not equivalent to laboratory-independent validation.
- ACR is not total-mass retention, bioavailability, human exposure, clinical risk, or cooking advice.
- The app offers evidence exploration and descriptive views only; it is not an inference interface.

See `docs/EVIDENCE_AND_DATA_SELECTION.md` and `DEMONSTRATOR_COMPLETION_REPORT.md`.
