# CookRisk Interactive Research Demonstrator

A local, read-only Streamlit application for inspecting CookRisk research records and saved evaluation evidence. It is an academic research prototype, not a validated predictor, deployment platform, risk-scoring system, clinical tool, or source of cooking advice.

## Start on Windows

Open PowerShell at the repository root and run:

```powershell
Set-Location .\research\CookRisk_Interactive_Research_Demonstrator
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Open <http://127.0.0.1:8501/>. Keep the PowerShell window open while using the app. If PowerShell blocks environment activation, use the environment's interpreter directly after creating it:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

If port 8501 is already in use, stop only the CookRisk process that owns that port or choose a free port and update the browser URL. Do not change any dataset hash pin to work around a data-loading error.

## Modules

1. Research Overview — research question, workflow, target definition, and boundaries.
2. Evidence Explorer — read-only record exploration from the approved Reconstruction.
3. ACR Distributions — descriptive summaries of the Reconstruction's stored target values.
4. Cooking & Compound Patterns — descriptive, noncausal group summaries with support counts.
5. Existing ML Results — separate saved evidence for the historical Stage A benchmark, Batch021 ACR, Reconstruction ACR, and strict verified subset; conflicts and evidence labels remain visible.
6. Validation & Generalization — split-design limits, fold records, provenance, strict subset, and post1000 conflict evidence.
7. Scientific Limitations — evidence, interpretation effects, status, and handling for the known scientific limitations.
8. Reproducibility & Evidence — registry, dataset roles, evidence labels, saved registers, and provenance gaps.

## Dataset roles and safeguards

The Reconstruction file at `stageA/verified_concentration_ratio_reconstruction/final_verified_master_dataset.csv` is approved only for live record-level exploration in Evidence Explorer, ACR Distributions, and Cooking & Compound Patterns. Its expected SHA-256 is `f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0` (1,016 × 43). It is not designated canonical and is not independently scientifically validated.

Batch021 at `stageA/dataset_expansion_1000/batch_021/updated_master_dataset.csv` is a separate historical ACR reference with expected SHA-256 `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8` (1,016 × 38). It is used for its saved historical results and metadata only. It is never a fallback for live exploration.

The historical 1,124-row Stage A `Retention_Final` benchmark, Reconstruction ACR results, Batch021 ACR results, and 338-row strict subset have different dataset/target roles. They are never combined into a common leaderboard. The original `Retention_Final` source CSV is not loaded by the app. Historical model results are displayed from the final Phase 4 evidence consolidation; the app does not train models, generate predictions, or recalculate saved ML metrics.

For live Reconstruction loading, the app checks the registered dataset ID and approval scope, full SHA-256, row count, ordered schema, unique observation IDs, and row-level target name/equation/semantics. Missing files, unknown IDs, schema/target problems, or hash mismatch fail closed. There is no replacement dataset fallback.

## Interpreting targets and model evidence

`ACR (%) = 100 × C_cooked / C_raw`. ACR is an apparent concentration ratio, not total-mass retention. ACR above 100% does not by itself establish an increase in total analyte mass. Compatible paired food masses or validated yield and compatible measurement bases would be needed to establish total-mass retention.

Pooled OOF R² and arithmetic mean-fold R² are distinct summaries. The app displays them in separate columns and keeps each value's evidence status visible. The status labels mean:

- **VERIFIED FROM SAVED RECORDS** — the value is supported by the referenced saved records; no fresh model run is implied.
- **REPORTED — PROVENANCE INCOMPLETE** — a saved value exists, but run/input identity or other provenance is incomplete.
- **CONFLICTING SAVED EVIDENCE** — preserved records disagree; no version is selected.
- **UNVERIFIED** — supporting records or essential identity details were not found.
- **NOT ASSESSABLE** — available saved evidence cannot establish the requested value.

The tuned XGBoost initial result and separately checksummed replay are both shown as conflicting saved evidence. The initial historical benchmark's pooled values retain incomplete provenance. The 338-row subset has no located pooled OOF artifact/value. Friend-reported `0.3301` pooled and `0.2990` mean-fold claims remain unverified and are not included as model achievements. Post1000 aggregate checksum and row-level conflicts are displayed without selecting or ranking either view.

DOI/source-held-out evaluation is only a source-family proxy and does not prove independent-laboratory, external, prospective, or real-world validation. Negative R² means performance is below the evaluated-data mean-prediction baseline; it is not evidence by itself that a result was overwritten.

## Tests and local environment

Use the same Python environment as the app:

```powershell
python -m py_compile app.py research_data.py tests\test_dataset_registry.py tests\test_research_evidence.py
python -m unittest discover -s tests -v
```

The environment used for local verification is not part of this documentation's setup commands. No packages or dependency files were changed during Phase 5. `requirements.txt` remains the dependency source for creating a separate local environment.

## Limitations and preserved history

Source-specific units/bases, paired raw/cooked compatibility, assay and replicate information, and some target precision remain unresolved. Outlier flags are review indicators, not deletion rules. No causal, clinical, patient-specific, bioavailability, exposure, nutrition, consumer-ready, or deployment claim is supported.

See [Evidence and Data Selection](docs/EVIDENCE_AND_DATA_SELECTION.md) and the Phase 5 completion report under `reports/research_prototype_completion_phase5_2026-11-20/`. `DEMONSTRATOR_COMPLETION_REPORT.md` records the initial demonstrator build state and is retained as historical documentation; the current behavior is described here and in the evidence-selection guide.
