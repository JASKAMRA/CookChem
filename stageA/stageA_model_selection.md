# Stage A Model Selection

## Locked comparison conditions

All models use the frozen Phase 2 feature recipe: 22 source predictors (process, context and RDKit descriptors after Heavy Atom Count removal) plus five deterministic engineered features: Temperature x Time, log Cooking Time, log Initial Concentration, LogP x Temperature, and TPSA x Cooking Time. Numeric median imputation/scaling and categorical missing-value encoding/one-hot encoding are fit within each outer training fold. The target is `log1p(Retention_Final)` and predictions are inverse transformed before original-scale metrics are calculated. Splits are the same 5-fold `GroupKFold` by `Canonical_Molecular_ID`.

| Model | Literature/CookRisk justification | Expected strength | Main risk |
|---|---|---|---|
| Extra Trees reference | Current selected benchmark among Phase 1-3 configurations. | Strong nonlinear baseline with mixed encoded features. | Rare extremes strongly affect RMSE/R2. |
| Random Forest | Controlled bagged-tree comparison against Extra Trees. | May reduce split randomisation sensitivity. | Can be less diverse / slower; already close in Phase 2. |
| RBF-SVR | Nonlinear-kernel baseline for scaled chemical/process descriptors. | Smooth nonlinear response surface. | One-hot food context can be high-dimensional; sensitive to kernel settings. |
| XGBoost | Chen & Guestrin (2016); regularised boosted trees and sparse features. | Regularisation may improve tail-sensitive RMSE/R2. | Can trade MAE for tail fitting; must not be selected on R2 alone. |

## Rejected or deferred

HistGradientBoosting and Extra Trees tuning were already evaluated in Phase 2, so Stage A did not repeat them as new discovery experiments. CatBoost and LightGBM were literature-considered but deferred because their packages were not in the isolated reproducibility environment; no external package was silently substituted. Stacking was not tested because no pair of candidates showed a complementary error pattern with clear overall improvement.
