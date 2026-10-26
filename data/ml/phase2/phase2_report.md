# CookRisk Phase 2 Report

## 1. Phase 1 benchmark

- Model: `hist_gradient_boosting`
- Features: `molecular_plus_process`
- Target: `log1p`
- MAE: 40.995285
- RMSE: 129.015456
- R2: 0.311207

## 2. Phase 2 objectives

- Preserve the GroupKFold unseen-compound validation logic.
- Test sparse-feature decisions, food-cardinality handling, descriptor redundancy, engineered features, selection, and tuning under the same grouped-CV framework.
- Improve the benchmark only when the trade-off is clear on RMSE, MAE, R2, and fold stability.

## 3. Sparse-feature investigation

| experiment_id             | feature_set_name           | model                  | target_representation | mae_mean          | rmse_mean          | r2_mean            |
| ------------------------- | -------------------------- | ---------------------- | --------------------- | ----------------- | ------------------ | ------------------ |
| A01_full_sparse_reference | full_phase1_feature_recipe | hist_gradient_boosting | log1p                 | 40.99680593522899 | 129.01606784187157 | 0.3112009780240709 |
| A02_no_pressure           | no_pressure                | hist_gradient_boosting | log1p                 | 40.99680593522899 | 129.01606784187157 | 0.3112009780240709 |
| A03_no_microwave          | no_microwave               | hist_gradient_boosting | log1p                 | 40.99680593522899 | 129.01606784187157 | 0.3112009780240709 |
| A04_no_oil                | no_oil                     | hist_gradient_boosting | log1p                 | 40.06009146023755 | 129.6930624361766  | 0.3044961470249156 |
| A05_no_sparse_features    | no_sparse_features         | hist_gradient_boosting | log1p                 | 40.06009146023755 | 129.6930624361766  | 0.3044961470249156 |

- Stage winner: `A01_full_sparse_reference`

## 4. High-cardinality food investigation

| experiment_id        | feature_set_name | food_strategy | mae_mean          | rmse_mean          | r2_mean             |
| -------------------- | ---------------- | ------------- | ----------------- | ------------------ | ------------------- |
| B01_food_current     | food_current     | current       | 40.99680593522899 | 129.01606784187157 | 0.3112009780240709  |
| B02_food_excluded    | food_excluded    | exclude       | 41.32906570846486 | 131.38524691951247 | 0.2829919190913097  |
| B03_food_top20_other | food_top20_other | top_k_other   | 41.3807898821731  | 132.09193591755178 | 0.27487522930996683 |

- Stage winner: `B01_food_current`

## 5. Molecular descriptor redundancy analysis

| RDKit_Molecular_Weight | RDKit_LogP | RDKit_TPSA | RDKit_HBond_Donors | RDKit_HBond_Acceptors | RDKit_Rotatable_Bonds | RDKit_Aromatic_Rings | RDKit_Hydroxyl_Groups | RDKit_Heavy_Atom_Count |
| ---------------------- | ---------- | ---------- | ------------------ | --------------------- | --------------------- | -------------------- | --------------------- | ---------------------- |
| 1.0                    | 0.311      | 0.528      | 0.495              | 0.582                 | 0.634                 | 0.413                | 0.463                 | 0.995                  |
| 0.311                  | 1.0        | -0.605     | -0.58              | -0.563                | 0.559                 | -0.254               | -0.511                | 0.371                  |
| 0.528                  | -0.605     | 1.0        | 0.962              | 0.98                  | -0.035                | 0.665                | 0.884                 | 0.479                  |
| 0.495                  | -0.58      | 0.962      | 1.0                | 0.934                 | -0.091                | 0.64                 | 0.947                 | 0.455                  |
| 0.582                  | -0.563     | 0.98       | 0.934              | 1.0                   | 0.019                 | 0.668                | 0.867                 | 0.534                  |
| 0.634                  | 0.559      | -0.035     | -0.091             | 0.019                 | 1.0                   | -0.142               | -0.105                | 0.632                  |
| 0.413                  | -0.254     | 0.665      | 0.64               | 0.668                 | -0.142                | 1.0                  | 0.553                 | 0.42                   |
| 0.463                  | -0.511     | 0.884      | 0.947              | 0.867                 | -0.105                | 0.553                | 1.0                   | 0.425                  |
| 0.995                  | 0.371      | 0.479      | 0.455              | 0.534                 | 0.632                 | 0.42                 | 0.425                 | 1.0                    |

| experiment_id                    | feature_set_name               | removed_features                             | mae_mean          | rmse_mean          | r2_mean             |
| -------------------------------- | ------------------------------ | -------------------------------------------- | ----------------- | ------------------ | ------------------- |
| C02_drop_heavy_atom_count        | descriptor_no_heavy_atom_count | RDKit_Heavy_Atom_Count                       | 41.34635699192292 | 128.49170033152245 | 0.31246377844447154 |
| C01_keep_all_descriptors         | descriptor_full                |                                              | 40.99680593522899 | 129.01606784187157 | 0.3112009780240709  |
| C04_drop_heavy_atom_and_hydroxyl | descriptor_compact_pair        | RDKit_Heavy_Atom_Count|RDKit_Hydroxyl_Groups | 41.25374296941648 | 129.16504128500128 | 0.30862264244159326 |
| C03_drop_hydroxyl_groups         | descriptor_no_hydroxyl_groups  | RDKit_Hydroxyl_Groups                        | 41.73334556716704 | 129.80094420666668 | 0.29864448626455475 |

- Stage winner: `C02_drop_heavy_atom_count`

## 6. Feature engineering

| experiment_id             | engineered_features                                                                                                        | mae_mean           | rmse_mean          | r2_mean             |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------- | ------------------ | ------------------ | ------------------- |
| D03_targeted_interactions | temperature_time_interaction|log_cooking_time|log_initial_concentration|logp_temperature_interaction|tpsa_time_interaction | 40.87545917091109  | 127.32633338404257 | 0.32884992008548275 |
| D01_no_engineering        |                                                                                                                            | 41.34635699192292  | 128.49170033152245 | 0.31246377844447154 |
| D02_temp_time_interaction | temperature_time_interaction|log_cooking_time                                                                              | 41.317747300633094 | 130.7866739653195  | 0.2849212115698848  |

- Stage winner: `D03_targeted_interactions`

## 7. Feature selection

| experiment_id                    | selection_strategy     | avg_features_after_processing | mae_mean          | rmse_mean          | r2_mean             |
| -------------------------------- | ---------------------- | ----------------------------- | ----------------- | ------------------ | ------------------- |
| E01_full_engineered_features     | none                   | 325.2                         | 40.87545917091109 | 127.32633338404257 | 0.32884992008548275 |
| E02_selected_engineered_features | tree_importance_median | 162.8                         | 40.87545917091109 | 127.32633338404257 | 0.32884992008548275 |

- Stage winner: `E01_full_engineered_features`

## 8. Model comparison

| experiment_id                    | model                  | target_representation | mae_mean           | rmse_mean          | r2_mean             | rmse_sd            |
| -------------------------------- | ---------------------- | --------------------- | ------------------ | ------------------ | ------------------- | ------------------ |
| F05_extra_trees_log1p            | extra_trees            | log1p                 | 31.959808967129028 | 123.07305615888808 | 0.38046097921558053 | 77.5179647195115   |
| F04_random_forest_log1p          | random_forest          | log1p                 | 33.02381054962257  | 126.45517589791476 | 0.3415001807863328  | 74.75228195877698  |
| F03_hist_gradient_boosting_log1p | hist_gradient_boosting | log1p                 | 40.87545917091109  | 127.32633338404257 | 0.32884992008548275 | 72.36320215133999  |
| F02_gradient_boosting_log1p      | gradient_boosting      | log1p                 | 36.448425771274046 | 127.54940121865323 | 0.32963875509726426 | 74.00994010214336  |
| F06_hist_gradient_boosting_raw   | hist_gradient_boosting | raw                   | 51.112223886827415 | 133.40147907157956 | 0.25455071516258576 | 76.64892967204037  |
| F01_ridge_log1p                  | ridge                  | log1p                 | 433652.40995372634 | 6489788.447128836  | -33503824004.126465 | 14493454.245960694 |

- Stage winner: `F05_extra_trees_log1p`

## 9. Hyperparameter optimization

| experiment_id                    | model                  | target_representation | mae_mean           | rmse_mean          | r2_mean             | rmse_sd           |
| -------------------------------- | ---------------------- | --------------------- | ------------------ | ------------------ | ------------------- | ----------------- |
| G02_extra_trees_tuned            | extra_trees            | log1p                 | 32.608194729376336 | 123.88093957190395 | 0.3908553140516363  | 79.39720951865877 |
| G01_hist_gradient_boosting_tuned | hist_gradient_boosting | log1p                 | 40.21075371720237  | 137.051457832771   | 0.20161589902341986 | 68.6680885715361  |

- Stage winner: `G02_extra_trees_tuned`

## 10. SHAP interpretation

- SHAP was run only for the final selected candidate, after model selection.
- Top SHAP features: num__RDKit_Hydroxyl_Groups, num__RDKit_LogP, cat__Cooking_Method_Standardized_Boiling

| feature                                                    | mean_abs_shap        |
| ---------------------------------------------------------- | -------------------- |
| num__RDKit_Hydroxyl_Groups                                 | 0.05690538537440211  |
| num__RDKit_LogP                                            | 0.04444060970976043  |
| cat__Cooking_Method_Standardized_Boiling                   | 0.0440104196689859   |
| cat__Cooking_Medium_Standardized_Microwave                 | 0.04259056421626086  |
| cat__Initial_Unit_Standardized_mg/100g                     | 0.03919725231605521  |
| cat__Food_Name_Standardized_Cheddar Cauliflower            | 0.03570610081239644  |
| num__FE_Log_Initial_Concentration                          | 0.03214649872181717  |
| num__FE_Temperature_x_Time                                 | 0.024716903312297443 |
| num__FE_Log_Cooking_Time                                   | 0.020749663115892557 |
| cat__Food_Name_Standardized_Common Bean - Nero di Caposele | 0.017800351652424867 |

## 11. Final candidate model

- Experiment ID: `F05_extra_trees_log1p`
- Model: `extra_trees`
- Feature set: `selected_phase2_recipe`
- Target representation: `log1p`
- Selection strategy: `none`
- Mean MAE: 31.959809 +- 6.988283
- Mean RMSE: 123.073056 +- 77.517965
- Mean R2: 0.380461 +- 0.235382

## 12. Comparison with Phase 1 baseline

- Delta MAE: -9.035476 (-22.04%)
- Delta RMSE: -5.942400 (-4.61%)
- Delta R2: 0.069254

## 13. Fold-wise performance

| fold | mae                | rmse               | r2                   |
| ---- | ------------------ | ------------------ | -------------------- |
| 1    | 34.34940167927474  | 124.39553624559038 | 0.39925814400861537  |
| 2    | 42.04427715922847  | 249.38578236010284 | 0.042534296172161756 |
| 3    | 23.91173985571974  | 53.959045568558686 | 0.6920590674829449   |
| 4    | 32.33250660776859  | 122.01151884622833 | 0.4547601524835946   |
| 5    | 27.161119533653594 | 65.61339777396016  | 0.31369323593058585  |

## 14. Mean +- SD performance

| experiment_id                    | stage                   | model                  | feature_set_name               | target_representation | mae_mean           | mae_sd            | rmse_mean          | rmse_sd            | r2_mean             | r2_sd               |
| -------------------------------- | ----------------------- | ---------------------- | ------------------------------ | --------------------- | ------------------ | ----------------- | ------------------ | ------------------ | ------------------- | ------------------- |
| F05_extra_trees_log1p            | F_model_comparison      | extra_trees            | selected_phase2_recipe         | log1p                 | 31.959808967129028 | 6.988282912842619 | 123.07305615888808 | 77.5179647195115   | 0.38046097921558053 | 0.23538237180200072 |
| G02_extra_trees_tuned            | G_hyperparameter_tuning | extra_trees            | selected_phase2_recipe_tuned   | log1p                 | 32.608194729376336 | 7.223610905257326 | 123.88093957190395 | 79.39720951865877  | 0.3908553140516363  | 0.2511211111977569  |
| F04_random_forest_log1p          | F_model_comparison      | random_forest          | selected_phase2_recipe         | log1p                 | 33.02381054962257  | 5.824167475435581 | 126.45517589791476 | 74.75228195877698  | 0.3415001807863328  | 0.19814316502968962 |
| D03_targeted_interactions        | D_feature_engineering   | hist_gradient_boosting | targeted_interactions          | log1p                 | 40.87545917091109  | 8.929562308677633 | 127.32633338404257 | 72.36320215133999  | 0.32884992008548275 | 0.16897320166035287 |
| E01_full_engineered_features     | E_feature_selection     | hist_gradient_boosting | full_engineered_features       | log1p                 | 40.87545917091109  | 8.929562308677633 | 127.32633338404257 | 72.36320215133999  | 0.32884992008548275 | 0.16897320166035287 |
| E02_selected_engineered_features | E_feature_selection     | hist_gradient_boosting | selected_engineered_features   | log1p                 | 40.87545917091109  | 8.929562308677633 | 127.32633338404257 | 72.36320215133999  | 0.32884992008548275 | 0.16897320166035287 |
| F03_hist_gradient_boosting_log1p | F_model_comparison      | hist_gradient_boosting | selected_phase2_recipe         | log1p                 | 40.87545917091109  | 8.929562308677633 | 127.32633338404257 | 72.36320215133999  | 0.32884992008548275 | 0.16897320166035287 |
| F02_gradient_boosting_log1p      | F_model_comparison      | gradient_boosting      | selected_phase2_recipe         | log1p                 | 36.448425771274046 | 6.725988205475654 | 127.54940121865323 | 74.00994010214336  | 0.32963875509726426 | 0.1695300679978096  |
| C02_drop_heavy_atom_count        | C_descriptor_redundancy | hist_gradient_boosting | descriptor_no_heavy_atom_count | log1p                 | 41.34635699192292  | 8.987076199648063 | 128.49170033152245 | 70.67439229952856  | 0.31246377844447154 | 0.14082474795604802 |
| D01_no_engineering               | D_feature_engineering   | hist_gradient_boosting | no_engineering                 | log1p                 | 41.34635699192292  | 8.987076199648063 | 128.49170033152245 | 70.67439229952856  | 0.31246377844447154 | 0.14082474795604802 |
| A01_full_sparse_reference        | A_sparse_ablation       | hist_gradient_boosting | full_phase1_feature_recipe     | log1p                 | 40.99680593522899  | 9.204030544707019 | 129.01606784187157 | 71.19727611649189  | 0.3112009780240709  | 0.1399633521125005  |
| A02_no_pressure                  | A_sparse_ablation       | hist_gradient_boosting | no_pressure                    | log1p                 | 40.99680593522899  | 9.204030544707019 | 129.01606784187157 | 71.19727611649189  | 0.3112009780240709  | 0.1399633521125005  |
| A03_no_microwave                 | A_sparse_ablation       | hist_gradient_boosting | no_microwave                   | log1p                 | 40.99680593522899  | 9.204030544707019 | 129.01606784187157 | 71.19727611649189  | 0.3112009780240709  | 0.1399633521125005  |
| B01_food_current                 | B_food_cardinality      | hist_gradient_boosting | food_current                   | log1p                 | 40.99680593522899  | 9.204030544707019 | 129.01606784187157 | 71.19727611649189  | 0.3112009780240709  | 0.1399633521125005  |
| C01_keep_all_descriptors         | C_descriptor_redundancy | hist_gradient_boosting | descriptor_full                | log1p                 | 40.99680593522899  | 9.204030544707019 | 129.01606784187157 | 71.19727611649189  | 0.3112009780240709  | 0.1399633521125005  |
| C04_drop_heavy_atom_and_hydroxyl | C_descriptor_redundancy | hist_gradient_boosting | descriptor_compact_pair        | log1p                 | 41.25374296941648  | 9.11431973310207  | 129.16504128500128 | 71.4468607889924   | 0.30862264244159326 | 0.14086426334379804 |
| A04_no_oil                       | A_sparse_ablation       | hist_gradient_boosting | no_oil                         | log1p                 | 40.06009146023755  | 7.841151834175133 | 129.6930624361766  | 71.9010252348885   | 0.3044961470249156  | 0.14830127226135656 |
| A05_no_sparse_features           | A_sparse_ablation       | hist_gradient_boosting | no_sparse_features             | log1p                 | 40.06009146023755  | 7.841151834175133 | 129.6930624361766  | 71.9010252348885   | 0.3044961470249156  | 0.14830127226135656 |
| C03_drop_hydroxyl_groups         | C_descriptor_redundancy | hist_gradient_boosting | descriptor_no_hydroxyl_groups  | log1p                 | 41.73334556716704  | 8.75499299873714  | 129.80094420666668 | 70.80918440899693  | 0.29864448626455475 | 0.12948715368711508 |
| D02_temp_time_interaction        | D_feature_engineering   | hist_gradient_boosting | temp_time_interaction          | log1p                 | 41.317747300633094 | 8.427646999724718 | 130.7866739653195  | 71.21393830344965  | 0.2849212115698848  | 0.1481985150201008  |
| B02_food_excluded                | B_food_cardinality      | hist_gradient_boosting | food_excluded                  | log1p                 | 41.32906570846486  | 8.57607805045411  | 131.38524691951247 | 70.92471681996965  | 0.2829919190913097  | 0.12308293553435048 |
| B03_food_top20_other             | B_food_cardinality      | hist_gradient_boosting | food_top20_other               | log1p                 | 41.3807898821731   | 8.572010197447506 | 132.09193591755178 | 71.02227135129732  | 0.27487522930996683 | 0.12205615757857026 |
| F06_hist_gradient_boosting_raw   | F_model_comparison      | hist_gradient_boosting | selected_phase2_recipe         | raw                   | 51.112223886827415 | 20.15513574434234 | 133.40147907157956 | 76.64892967204037  | 0.25455071516258576 | 0.28449972157063463 |
| G01_hist_gradient_boosting_tuned | G_hyperparameter_tuning | hist_gradient_boosting | selected_phase2_recipe_tuned   | log1p                 | 40.21075371720237  | 7.359144059215965 | 137.051457832771   | 68.6680885715361   | 0.20161589902341986 | 0.07474381263452222 |
| F01_ridge_log1p                  | F_model_comparison      | ridge                  | selected_phase2_recipe         | log1p                 | 433652.40995372634 | 968387.6996556243 | 6489788.447128836  | 14493454.245960694 | -33503824004.126465 | 74916807073.53908   |

## 15. Remaining limitations

- Grouped validation is scientifically stronger than row-wise splits, but the dataset still has repeated-compound imbalance and only 197 unique molecular groups.
- Sparse process variables remain difficult to estimate because their non-missing support is tiny even when retained.
- High-cardinality context features can still hurt transfer if future foods differ from the observed standardized food space.
- SHAP explains model behavior for the selected model; it does not prove causal cooking mechanisms.

## 16. Recommended Phase 3 work

- Perform deeper error analysis on the saved genuine OOF predictions.
- Inspect whether the remaining hardest compounds or conditions cluster in specific food or compound classes.
- Validate the final candidate against additional robustness checks before any downstream risk-scoring claims.
