# Preprocessing

Run from the project root:

```powershell
& "C:\Users\ayush\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" preprocessing/scripts/run_preprocessing.py
```

The pipeline reads one raw Excel/CSV file from `data/raw/`, preserves source columns, adds standardized helper columns and validation flags, and writes reproducible outputs under `data/preprocessing/` and `preprocessing/reports/`.

It does not delete rows, invent missing values, overwrite raw data, perform PubChem lookup, regenerate descriptors, or remove retention above 100%.
