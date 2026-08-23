# Project Architecture

```text
Literature
-> Raw Data
-> Preprocessing
-> Preprocessed Data
-> Molecular Features
-> EDA
-> Modelling
-> Risk Scoring
-> Application
```

Raw inputs live in `data/raw/`. Preprocessing outputs live in `data/preprocessing/`. Compound-level molecular features live in `molecular_features/outputs/`. Observation-level data merged with molecular features lives in `data/molecular_features/`.
