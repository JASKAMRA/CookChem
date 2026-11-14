# Source-confounding report

## Design

v0.6 is a controlled diagnostic over the exact v0.5 dataset (SHA-256 `72b1f7d547b19b40a58eb43db773d64996dfb1e6c4d5cb44d38c7d3845bb9cc0`). It changes no observations. Random Forest, fixed seed, fold-safe imputation/one-hot encoding, and identical group definitions are used across ablations. DOI is never a predictor.

## Findings

- Source-LOSO is negative for the full feature set and remains the decisive non-generalisation result.
- `cooking_medium` carries a high-cardinality, source-linked protocol label. The `Microwave` category is concentrated in the source-by-medium matrix; its full-fit importance must not be interpreted causally.
- The best source-LOSO ablation by MAE is **molecular_plus_cooking** (R² -0.0412, MAE 56.0980, RMSE 187.7090). Selection does not authorize deployment.
- Exact DOI/compound/food/method/basis matrices and source profiles are included in this package. They show that most source families occupy distinct compound–matrix–protocol regions, making a held-out DOI largely an extrapolation task rather than an independent replication.

## Interpretation

This evidence supports a combination of source-specific measurement/protocol effects and sparse experimental overlap. It does not establish that microwave cooking has a causal effect of the magnitude implied by feature importance. Required harmonisation information includes matched basis, yield/moisture, food preparation detail, and independent replications of the same compound–food–method cells.

## Decision

**RESEARCH PROTOTYPE / NOT VALIDATED FOR DEPLOYMENT.** One general-purpose model is not supported by the current overlap structure. Continue acquisition only for primary studies that replicate existing compound–matrix–method cells across independent laboratories. Stage C remains untouched.
