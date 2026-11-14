# Model comparison

All preprocessing and bounded hyperparameter selection occur inside the training portion of every outer fold. Models: Dummy mean baseline, Ridge, Random Forest, Extra Trees, and XGBoost. Random split is diagnostic only. Compound-, food-, and source-held-out metrics are reported in CSV form with every fold's training/test counts and held-out groups.

The selected diagnostic source-held-out row is `random_forest`: R² -0.0475; MAE 51.58; RMSE 175.39. This is not a deployment selection.
