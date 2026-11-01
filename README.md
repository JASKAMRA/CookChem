# CookRisk

Cooking-Induced Compound Retention Prediction & Risk Scoring.

Current implemented stages in this folder:

- Preprocessing: conservative validation/audit pipeline.
- Molecular features: compound-level PubChem/cache, SMILES validation, and RDKit descriptors.

Not implemented here yet: EDA, modelling, risk scoring, or application code.

Data lineage:

```text
data/raw/
-> data/preprocessing/intermediate/
-> data/preprocessing/final/
-> molecular_features/outputs/
-> data/molecular_features/
```

Raw data is never modified. Failed or ambiguous molecular identity resolution is flagged, not guessed.

## Stage B

See [`stageB/README.md`](stageB/README.md) for the organized Stage B workflow, authoritative evidence release, model experiments, and historical archive.
