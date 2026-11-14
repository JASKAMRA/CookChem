# Model evaluation

The modelling target is `verified_concentration_ratio_percent = 100 * C_cooked / C_raw`. It is an apparent concentration ratio, not total-mass retention.

Historical XGBoost parameters were held fixed: 450 trees, depth 3, learning rate 0.03, min child weight 3, subsample and colsample 0.8, L2=5, seed 42, with log1p target fitting. Fold-local preprocessing uses median imputation/scaling for numeric variables and one-hot encoding for categorical variables.

The final schema lacks historical pressure, microwave power, sample weight, replicate count, assay, oil type, unit-standardization, and heavy-atom-count fields. This evaluation uses only explicit counterparts: temperature, time, raw concentration, class, medium, method, food matrix, and available descriptors. It is therefore not an exact historical-feature replay.

Molecular-grouped pooled R²: 0.059831; mean fold R²: 0.083504; MAE: 91.328150; RMSE: 406.117246.

Source-held-out pooled R²: -0.073710; mean fold R²: -0.253519; MAE: 115.432912; RMSE: 434.002111.

Every molecular-grouped fold's DOI overlap is in `molecular_grouped_fold_metrics.csv`; molecular grouping must not be read as unseen-source validation.
