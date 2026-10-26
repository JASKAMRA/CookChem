# CookRisk Stage A Report

## 1. Objective

Determine whether a literature-guided alternative improves molecular retention prediction under the locked CookRisk molecular-grouped validation protocol, without changing the data, target, features, outlier handling, or Phase 1-3 artifacts.

## 2. Existing CookRisk benchmark

The historical Phase 2 selected candidate is Extra Trees (`n_estimators=300`, `min_samples_leaf=2`, seed 42, `log1p` target): mean fold MAE **31.959809**, RMSE **123.073056**, R2 **0.380461**. These are historical fold-mean results. Stage A also independently reproduced Extra Trees and reports aggregate OOF metrics below; these aggregations should not be conflated.

## 3-6. Literature, candidate selection and methodology

See `stageA_literature_review.md` and `stageA_model_selection.md`. Stage A used 1,124 records and 197 molecular groups. Every model was evaluated with 5-fold GroupKFold by `Canonical_Molecular_ID`; no group overlap was recorded. All preprocessing was fit only within each training fold. The reported OOF metrics are on the original retention scale after inverse transformation.

## 7. Aggregate OOF benchmark results

| Model | MAE | RMSE | R2 | Fold_R2_Mean | Fold_R2_STD | Delta_MAE | Delta_RMSE | Delta_R2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ExtraTrees_reference | 31.964078 | 141.308626 | 0.255978 | 0.380461 | 0.235382 | 0.000000 | 0.000000 | 0.000000 |
| RandomForest | 33.026848 | 143.092541 | 0.237074 | 0.341500 | 0.198143 | 1.062770 | 1.783916 | -0.018904 |
| RBF_SVR | 34.781659 | 141.439687 | 0.254597 | 0.379352 | 0.221709 | 2.817580 | 0.131061 | -0.001381 |
| XGBoost | 35.419174 | 139.489410 | 0.275012 | 0.383296 | 0.188818 | 3.455096 | -1.819216 | 0.019034 |
| XGBoost_tuned | 34.611876 | 138.694923 | 0.283247 | 0.400376 | 0.188982 | 2.647798 | -2.613703 | 0.027269 |

`Delta_*` values are versus the independent Extra Trees aggregate OOF reference, so comparisons are like-for-like. XGBoost tuning used a compact nested 3-fold GroupKFold search within each outer-training fold; it did not select using final OOF predictions.

## 8. Hyperparameter tuning

The tuned XGBoost configuration was selected from a small grid over `n_estimators` (250/450), `max_depth` (2/3), and `min_child_weight` (3/8), with learning rate 0.03, subsampling 0.8, column subsampling 0.8 and L2 regularisation 5. Exact inner-CV records are in `stageA_tuning_results.csv`.

## 9. Robustness analysis

For tuned XGBoost, seed 42/123 gave MAE 34.612/34.901, RMSE 138.695/139.133 and R2 0.283/0.279. Removing the highest 1% of actual retention (sensitivity only; not primary analysis) improved tuned-XGBoost metrics to MAE 25.161, RMSE 46.020 and R2 0.364, confirming that rare extreme targets dominate tail-sensitive metrics. The complete range, cooking-method and compound-class results are in `stageA_robustness.csv`.

## 10-11. Feature engineering and ensembles

No new feature engineering was added: the five literature-plausible Phase 2 interactions were already locked in the fair feature recipe. No ensemble was tested because no alternative delivered an unambiguous overall improvement.

## 12. Final comparison and decision

Tuned XGBoost reduced aggregate OOF RMSE by 2.614 (1.85%) and increased R2 by 0.027, but increased MAE by 2.648 (8.28%). Random Forest and RBF-SVR were worse on all primary aggregate OOF metrics. Because XGBoost’s tail-oriented RMSE/R2 gain comes with a materially worse typical error (MAE), and the historical fold-mean benchmark remains stronger than every Stage A alternative on MAE, **RETAIN EXTRA TREES** as the current selected benchmark. This is a negative but informative Stage A result.

## 13. Limitations

The supplied literature base contained six, not eight, documented papers; no missing citations were invented. The dataset is heterogeneous, has sparse process variables and only 197 molecular groups. Twelve extreme-retention observations disproportionately influence RMSE/R2. CatBoost/LightGBM were documented as deferred rather than treated as tested.

## 14-15. Conclusion and recommended next step

Stage A found no replacement that improved MAE, RMSE and R2 together under strict grouped validation. Retain Extra Trees and prioritise data expansion, harmonisation of extreme retention measurements, and external/source-held-out validation before further algorithm expansion.
