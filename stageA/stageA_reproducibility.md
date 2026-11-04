# Stage A Reproducibility

## Inputs
* Staged authoritative input: `stageA/input/cookchem_molecular_retention_preprocessed.csv` copied unchanged from `C:\Users\kamra\Desktop\BTP\CookChem\data\preprocessing\final\cookchem_molecular_retention_preprocessed.csv`.
* Historical read-only reference: Phase 2/3 artifacts under `data/ml/phase2` and `data/ml/phase3`.

## Environment

Use Python 3.12.14 and install the complete Python package set from `stageA/stageA-requirements-py312.lock`. The lock was captured from the isolated 2026-11-04 reproduction environment; it pins the four direct dependencies and their resolved transitive packages. The historical Stage A run did not record its full transitive environment, so its original package-level environment cannot be proven identical. Do not use Python 3.14 for this reproduction.

## Execute on macOS/Linux
```sh
brew install libomp  # macOS; validated with Homebrew libomp 23.1.5
python3.12 -m venv /tmp/cookrisk-stage-a-venv
. /tmp/cookrisk-stage-a-venv/bin/activate
python -m pip install -r stageA/stageA-requirements-py312.lock
python -m pip check
mkdir -p /tmp/cookrisk-stage-a-copy/stageA/outputs
cp -R stageA/input stageA/scripts /tmp/cookrisk-stage-a-copy/stageA/
python /tmp/cookrisk-stage-a-copy/stageA/scripts/run_stage_a.py
python /tmp/cookrisk-stage-a-copy/stageA/scripts/write_stage_a_docs.py
```

## Execute on Windows PowerShell

Install the current Microsoft Visual C++ Redistributable for the Windows architecture before importing XGBoost, as required by the [XGBoost installation guide](https://xgboost.readthedocs.io/en/stable/install.html). Use the official [Microsoft download page](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist).

```powershell
py -3.12 -m venv "$env:TEMP\cookrisk-stage-a-venv"
& "$env:TEMP\cookrisk-stage-a-venv\Scripts\Activate.ps1"
python -m pip install -r stageA/stageA-requirements-py312.lock
python -m pip check
New-Item -ItemType Directory -Force "$env:TEMP\cookrisk-stage-a-copy\stageA\outputs" | Out-Null
Copy-Item -Recurse stageA\input, stageA\scripts "$env:TEMP\cookrisk-stage-a-copy\stageA\"
python "$env:TEMP\cookrisk-stage-a-copy\stageA\scripts\run_stage_a.py"
python "$env:TEMP\cookrisk-stage-a-copy\stageA\scripts\write_stage_a_docs.py"
```

Windows and Linux execution have not been tested in this cycle. On Linux, ensure the platform OpenMP runtime (`libgomp`) is installed before importing XGBoost. Verify `python --version` is 3.12.14 and `python -m pip freeze` matches the lock before running. The canonical entrypoints are `stageA/scripts/run_stage_a.py` and `stageA/scripts/write_stage_a_docs.py`; do not run the duplicate copies under `stageA/scripts/scripts/`.

## Configuration
* Rows/groups: 1,124 / 197; target: `Retention_Final`; group: `Canonical_Molecular_ID`.
* CV: 5-fold GroupKFold; no group overlap; seed 42, with seed 123 sensitivity for the strongest tail-oriented alternative.
* This Stage A benchmark fits `log1p(Retention_Final)` and applies `expm1` before original-scale metrics. This is the Stage A comparison procedure; it does not reproduce the frozen Stage B artifact, whose manifest specifies a fold-fitted Yeo-Johnson PowerTransformer.
* Extra Trees reference: 300 estimators, `min_samples_leaf=2`, seed 42.
* Software: {"python": "3.12.14", "numpy": "2.5.3", "pandas": "3.0.6"}; `scikit-learn` 1.9.1; `xgboost` 3.4.1.
* Outputs are generated under `stageA/outputs`; `stageA_validation_audit.csv` and `stageA_qa.json` are programmatic QA evidence.
* Each new run also writes `stageA_run_manifest.json` with input/code/output hashes, input and feature column order, per-fold group/record assignment hashes, preprocessing contract, model configuration, package versions, and platform. Historical outputs do not contain this manifest, so it cannot retroactively identify their original fitted state.
