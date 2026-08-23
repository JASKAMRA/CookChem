# Molecular Features

Run from the project root after preprocessing:

```powershell
& "C:\Users\ayush\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" molecular_features/scripts/run_molecular_features.py
```

The module extracts unique compounds from the preprocessed dataset, reuses `pubchem_cache.csv`, retrieves missing PubChem identities where needed, validates SMILES with RDKit, and calculates a documented descriptor set for valid molecules only.

Molecular descriptors are calculated from validated molecular structures and are not manually entered into the dataset.

Outputs are written to `molecular_features/outputs/`, `molecular_features/reports/`, and the optional merged observation-level dataset in `data/molecular_features/`.
