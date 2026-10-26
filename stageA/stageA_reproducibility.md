# Stage A Reproducibility

## Inputs
* Staged authoritative input: `stageA/input/cookchem_molecular_retention_preprocessed.csv` copied unchanged from `C:\Users\kamra\Desktop\BTP\CookChem\data\preprocessing\final\cookchem_molecular_retention_preprocessed.csv`.
* Historical read-only reference: Phase 2/3 artifacts under `data/ml/phase2` and `data/ml/phase3`.

## Execute
```powershell
python -m pip install -r stageA\stageA_requirements.txt
python stageA\scripts\run_stage_a.py
python stageA\scripts\write_stage_a_docs.py
```

## Configuration
* Rows/groups: 1,124 / 197; target: `Retention_Final`; group: `Canonical_Molecular_ID`.
* CV: 5-fold GroupKFold; no group overlap; seed 42, with seed 123 sensitivity for the strongest tail-oriented alternative.
* Target transform: `log1p`, inverse transformed using `expm1` before original-scale metrics.
* Extra Trees reference: 300 estimators, `min_samples_leaf=2`, seed 42.
* Software: {"python": "3.12.14", "numpy": "2.5.3", "pandas": "3.0.6"}; `scikit-learn` 1.9.1; `xgboost` 3.4.1.
* Outputs are generated under `stageA/outputs`; `stageA_validation_audit.csv` and `stageA_qa.json` are programmatic QA evidence.
