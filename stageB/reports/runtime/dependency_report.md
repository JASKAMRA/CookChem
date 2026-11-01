# Stage B isolated dependency report

## Runtime

- Python **3.14.7** at `stageB/.venv/Scripts/python.exe`.
- Stage B does not declare a Python-version constraint. Only Python 3.14.7 is installed; Stage A’s reproducibility record names Python 3.12.14.
- Isolated environment: `stageB/.venv/`. Global Python packages were not changed.

## Direct requirements and installed versions

| Package | Stage B declaration | Installed version |
|---|---|---:|
| `numpy` | `numpy` | `2.5.4` |
| `pandas` | `pandas` | `3.1.0` |
| `scikit-learn` | `scikit-learn` | `1.9.1` |
| `catboost` | `catboost` | `1.2.10` |
| `joblib` | `joblib` | `1.6.0` |
| `xgboost` | `xgboost==3.4.1` | `3.4.1` |

## Transitive packages installed for these requirements

`cloudpickle==3.1.2`, `contourpy==1.4.0`, `cycler==0.12.1`, `fonttools==4.68.0`, `graphviz==0.21`, `kiwisolver==1.5.1`, `matplotlib==3.11.2`, `narwhals==2.28.0`, `packaging==26.3`, `pillow==13.0.0`, `plotly==7.1.0`, `pyparsing==3.3.3`, `python-dateutil==4.0.0`, `scipy==1.18.1`, `six==1.17.0`, `threadpoolctl==3.7.0`, `tzdata==2026.6`

Installer: `pip==26.2.1`.

## Compatibility and limitations

- `pip check`: exit 0 — No broken requirements found.
- No pip resolver conflicts were found. Stage B imports `stageA/scripts/run_stage_a.py`, which imports XGBoost at module load. `xgboost==3.4.1` was added to the Stage B-specific requirements.
- Stage A records NumPy 2.5.3 and pandas 3.0.6; this environment resolved NumPy 2.5.4 and pandas 3.1.0 because Stage B leaves them unpinned. scikit-learn 1.9.1 matches. This is not a resolver conflict, but bit-for-bit model reproducibility against the documented Stage A environment is not established.
- Root `openpyxl` and RDKit requirements are not imported by the 14 active Stage B scripts and were not installed here. CatBoost plotting packages were installed transitively.
- No dependency was installed globally; `.venv/` is covered by the existing ignore rule.
