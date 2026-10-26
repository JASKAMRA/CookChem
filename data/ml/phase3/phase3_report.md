# CookRisk Phase 3 Report

## 1. Executive summary

- Final candidate: `extra_trees` with the Phase 2 selected recipe and `log1p` target.
- Primary OOF performance: MAE 31.959809, RMSE 123.073056, R2 0.380461.
- The Phase 2 gain over Phase 1 is genuine in aggregate, but performance varies substantially across grouped folds.
- Model status: Conditionally suitable as a validated candidate for downstream CookRisk risk-scoring development, but not yet strong enough to describe as production-ready.

## 2. Phase 1 benchmark

- MAE: 40.995285
- RMSE: 129.015456
- R2: 0.311207

## 3. Phase 2 optimization

- Winning interventions from Phase 2 were descriptor compaction plus targeted engineered features, followed by the model-family switch to ExtraTrees.
- Sparse-feature removal and food simplification did not improve the benchmark under grouped validation.

## 4. Phase 3 validation objective

- Assess whether the locked Phase 2 candidate is reliable enough for downstream CookRisk development.
- Diagnose where the model fails without changing the validation philosophy or tuning the model again.

## 5. Validation integrity

| check                                       | status | value                                                          |
| ------------------------------------------- | ------ | -------------------------------------------------------------- |
| dataset_rows                                | PASS   | 1124                                                           |
| unique_groups                               | PASS   | 197                                                            |
| target_column_present                       | PASS   | Retention_Final                                                |
| group_column_present                        | PASS   | Canonical_Molecular_ID                                         |
| oof_rows_phase2_candidate                   | PASS   | 1124                                                           |
| oof_unique_record_ids_phase2                | PASS   | 1124                                                           |
| oof_unique_record_ids_phase1                | PASS   | 1124                                                           |
| no_target_derived_predictor_in_final_recipe | PASS   | Retention-derived fields excluded; Apparent_Increase excluded. |
| leakage_columns_not_in_candidate_recipe     | PASS   |                                                                |
| group_used_only_for_grouping                | PASS   | Canonical_Molecular_ID                                         |
| all_records_have_phase2_oof_fold            | PASS   | 0                                                              |

| Fold | validation_rows | training_rows | validation_groups | training_groups | group_intersection_count | status |
| ---- | --------------- | ------------- | ----------------- | --------------- | ------------------------ | ------ |
| 1    | 225             | 899           | 36                | 161             | 0                        | PASS   |
| 2    | 225             | 899           | 40                | 157             | 0                        | PASS   |
| 3    | 225             | 899           | 40                | 157             | 0                        | PASS   |
| 4    | 225             | 899           | 41                | 156             | 0                        | PASS   |
| 5    | 224             | 900           | 40                | 157             | 0                        | PASS   |

## 6. Final candidate performance

| model_stage                    | mae       | rmse       | r2       |
| ------------------------------ | --------- | ---------- | -------- |
| Phase 1 frozen benchmark       | 40.995285 | 129.015456 | 0.311207 |
| Phase 2 locked final candidate | 31.959809 | 123.073056 | 0.380461 |

## 7. Fold stability

| Fold | n   | unique_groups | mae                | rmse               | r2                  | target_mean        | target_median | target_max  | extreme_retention_count | temperature_missing_pct | time_missing_pct   | pressure_reported_n | microwave_power_reported_n |
| ---- | --- | ------------- | ------------------ | ------------------ | ------------------- | ------------------ | ------------- | ----------- | ----------------------- | ----------------------- | ------------------ | ------------------- | -------------------------- |
| 1    | 225 | 36            | 34.34940167927474  | 124.39553624559038 | 0.39925814400861526 | 81.78169084094667  | 69.7          | 2226.086957 | 3                       | 35.55555555555556       | 12.0               | 7                   | 11                         |
| 2    | 225 | 40            | 42.04427715922847  | 249.38578236010284 | 0.04253429617216187 | 103.54870017689335 | 74.8          | 3650.0      | 3                       | 32.44444444444444       | 18.22222222222222  | 0                   | 19                         |
| 3    | 225 | 40            | 23.91173985571974  | 53.95904556855867  | 0.692059067482945   | 96.12813796853332  | 81.0          | 1035.0      | 3                       | 35.55555555555556       | 20.0               | 1                   | 12                         |
| 4    | 225 | 41            | 32.33250660776859  | 122.01151884622833 | 0.4547601524835947  | 105.67475554206223 | 82.71         | 2247.619048 | 2                       | 36.44444444444444       | 27.555555555555557 | 0                   | 8                          |
| 5    | 224 | 40            | 27.161119533653597 | 65.61339777396017  | 0.3136932359305856  | 94.87174945990179  | 82.5          | 851.8072289 | 1                       | 39.285714285714285      | 24.107142857142858 | 2                   | 18                         |

Fold 2 remains the hardest fold by a wide margin, while Fold 3 is much easier. The fold-composition tables below show that this difference is associated with different molecular-group mixes and different target/extreme-value composition rather than a validation breach.

## 8. OOF error analysis

| Record_ID | Canonical_Molecular_ID | Compound_Class_Standardized | Cooking_Method_Standardized | Actual_Retention | Predicted_Retention | Absolute_Error     | Signed_Error        | Fold |
| --------- | ---------------------- | --------------------------- | --------------------------- | ---------------- | ------------------- | ------------------ | ------------------- | ---- |
| R754      | MOL-E735D9075DA5F7EA   | Vitamin                     | Frying                      | 3650.0           | 59.73423118446019   | 3590.26576881554   | 3590.26576881554    | 2    |
| EXP931    | MOL-25F8CD05AD250A06   | Phenolic Acid               | Microwaving                 | 2247.619048      | 653.2890446698353   | 1594.3300033301648 | 1594.3300033301648  | 4    |
| EXP951    | MOL-3811F42D3C15ED32   | Flavonoid                   | Microwaving                 | 2226.086957      | 771.5232217205416   | 1454.5637352794583 | 1454.5637352794583  | 1    |
| R753      | MOL-E735D9075DA5F7EA   | Vitamin                     | Stir-frying                 | 850.0            | 70.46745233500353   | 779.5325476649965  | 779.5325476649965   | 2    |
| R6-019    | MOL-ED743FD15F645421   | Flavonoid                   | Boiling                     | 821.0962145      | 68.7974048991695    | 752.2988096008305  | 752.2988096008305   | 1    |
| EXP946    | MOL-AD185038A3D0E63D   | Phenolic Acid               | Microwaving                 | 487.5            | 1192.8463448224525  | 705.3463448224525  | -705.3463448224525  | 5    |
| EXP936    | MOL-25433E39C2198405   | Stilbenoid                  | Microwaving                 | 252.2727273      | 808.22225482543     | 555.94952752543    | -555.94952752543    | 1    |
| EXP906    | MOL-C208ADB38D658E40   | Phenolic Acid               | Microwaving                 | 435.9195402      | 962.8019245764352   | 526.8823843764353  | -526.8823843764353  | 4    |
| R6-023    | MOL-2EDC7AF9A9DB2D85   | Flavonoid                   | Boiling                     | 566.0483871      | 76.65598016165538   | 489.3924069383446  | 489.3924069383446   | 1    |
| EXP956    | MOL-7EE1F4B0FE7C2F8F   | Flavonoid                   | Microwaving                 | 392.5480769      | 825.7232732834408   | 433.1751963834408  | -433.1751963834408  | 4    |
| R4_04_03  | CID:156155             | Isoflavone                  | Dry-Heating                 | 512.2977346      | 154.4851413950525   | 357.8125932049475  | 357.8125932049475   | 3    |
| EXP921    | MOL-EEA321586E21AFFF   | Phenolic Acid               | Microwaving                 | 1035.0           | 687.9143009259205   | 347.08569907407946 | 347.08569907407946  | 3    |
| R746      | MOL-E735D9075DA5F7EA   | Vitamin                     | Deep-frying                 | 493.01           | 151.49358764967434  | 341.51641235032565 | 341.51641235032565  | 2    |
| R134      | MOL-4211365770E800E7   | Carotenoid                  | Deep-frying                 | 529.16           | 192.26715912134887  | 336.8928408786511  | 336.8928408786511   | 3    |
| R768      | MOL-57965F338647B48F   | Vitamin                     | Deep-frying                 | 150.33           | 485.938146380032    | 335.60814638003194 | -335.60814638003194 | 4    |

## 9. Molecular-group analysis

| Canonical_Molecular_ID | Canonical_Compound_Name      | observation_count | mae                | rmse               | mean_signed_error   | actual_retention_min | actual_retention_max | actual_retention_std | class_mode        | method_mode | mean_rdkit_hydroxyl_groups | mean_rdkit_logp    |
| ---------------------- | ---------------------------- | ----------------- | ------------------ | ------------------ | ------------------- | -------------------- | -------------------- | -------------------- | ----------------- | ----------- | -------------------------- | ------------------ |
| MOL-2EDC7AF9A9DB2D85   | Taxifolin                    | 1                 | 489.3924069383446  | 489.3924069383446  | 489.3924069383446   | 566.0483871          | 566.0483871          | 0.0                  | Flavonoid         | Boiling     | 5.0                        | 1.1863             |
| MOL-3811F42D3C15ED32   | Kaempferol                   | 6                 | 338.352872778269   | 607.6671419568027  | 338.352872778269    | 77.2                 | 2226.086957          | 771.0245757107681    | Flavonoid         | Boiling     | 4.0                        | 2.2823999999999995 |
| MOL-E735D9075DA5F7EA   | Alpha-Tocopherol (Vitamin E) | 20                | 278.88687773564027 | 829.0719086143052  | 277.33802650421364  | 88.3                 | 3650.0               | 772.6387028066547    | Vitamin           | Boiling     | 1.0                        | 8.84026            |
| MOL-AD185038A3D0E63D   | Cinnamic acid                | 5                 | 195.63984841166047 | 323.9321898169093  | -86.49868951732051  | 56.25                | 487.5                | 151.3997192863976    | Phenolic Acid     | Boiling     | 1.0                        | 1.7844000000000002 |
| MOL-ED743FD15F645421   | Hyperoside                   | 6                 | 145.4851701534491  | 308.5553887376317  | 133.33456110183116  | 13.24963575          | 821.0962145          | 291.08715592365735   | Flavonoid         | Boiling     | 8.0                        | -0.5389            |
| CID:156155             | Acetyldaidzin                | 8                 | 114.10520639527336 | 168.3653361368642  | 109.87516280432686  | 182.8478964          | 512.2977346          | 115.07949097379921   | Isoflavone        | Dry-Heating | 0.0                        | 0.9151             |
| MOL-C6EE40B369C1FFEC   | Epicatechin                  | 7                 | 112.38817427843654 | 146.6346653412724  | -112.38817427843654 | 5.812091285          | 134.5565749          | 43.50071719196714    | Flavonoid         | Boiling     | 5.0                        | 1.5461000000000003 |
| MOL-C208ADB38D658E40   | Protocatechuic Acid          | 7                 | 94.32184977914632  | 200.34349881030948 | -69.8821175732547   | 11.7816092           | 435.9195402          | 133.1657095197116    | Phenolic Acid     | Boiling     | 3.0                        | 0.7960000000000002 |
| MOL-25F8CD05AD250A06   | Ferulic Acid                 | 32                | 90.57184612894692  | 287.0070275776092  | 83.04762379629594   | 19.7                 | 2247.619048          | 376.3875505542304    | Phenolic Acid     | Boiling     | 2.0                        | 1.4986             |
| MOL-8C5B998537EAA56A   | Pelargonidin                 | 2                 | 82.77430275956164  | 84.67164898701613  | 82.77430275956164   | 152.2648084          | 180.1393728          | 13.937282199999999   | Anthocyanidin     | Boiling     | 4.0                        | 3.2033             |
| MOL-25433E39C2198405   | Resveratrol                  | 8                 | 79.91367862517193  | 197.172941274011   | -67.44481810859827  | 15.90909091          | 252.2727273          | 67.86226358621951    | Stilbenoid        | Boiling     | 3.0                        | 2.9738             |
| MOL-EEA321586E21AFFF   | Syringic acid                | 6                 | 75.63994075863529  | 143.64839301102265 | 40.05529226605787   | 13.33333333          | 1035.0               | 367.25433461954617   | Phenolic Acid     | Boiling     | 2.0                        | 1.1076             |
| MOL-4AF82040FB3DD1CD   | Isoflavone Beta-Glucosides   | 4                 | 74.01312200631176  | 97.41308620258759  | 74.01312200631176   | 84.6                 | 326.1                | 96.4110049475681     | Isoflavone        | Boiling     | 6.0                        | 0.0499             |
| CID:187808             | Glycitin                     | 8                 | 73.51462128022092  | 78.94569080076181  | 24.910151967460624  | 102.3904382          | 229.747676           | 40.085018537585555   | Isoflavone        | Dry-Heating | 0.0                        | 0.3529             |
| MOL-B74926EE11388959   | Catechol                     | 5                 | 69.5103732235913   | 70.44276425334435  | -69.5103732235913   | 6.93877551           | 14.28571429          | 2.595610302688093    | Phenolic compound | Microwaving | 2.0                        | 1.0978             |

## 10. Cooking-method analysis

| Cooking_Method_Standardized | n     | unique_groups | mae                | rmse               | r2                    | mean_signed_error    |
| --------------------------- | ----- | ------------- | ------------------ | ------------------ | --------------------- | -------------------- |
| Frying                      | 76.0  | 41.0          | 75.93457424070048  | 414.52025416388176 | -0.02395944262024763  | 46.697123597974056   |
| Microwaving                 | 125.0 | 72.0          | 62.153806691334395 | 223.13540863337738 | 0.4744661978002954    | 12.435577046351893   |
| Pressure Cooking            | 22.0  | 17.0          | 35.73731889411865  | 56.50824220097152  | -0.050086941431547016 | 7.047677579629149    |
| Boiling                     | 319.0 | 127.0         | 27.060761660222298 | 63.631740637055415 | 0.4043565422543868    | 4.985428757027814    |
| Sous-vide                   | 39.0  | 24.0          | 24.28229817433361  | 44.57010931950234  | 0.6323879129688437    | -0.3732763656437463  |
| Stir-frying                 | 76.0  | 57.0          | 18.982340068044756 | 90.58172920326791  | 0.03218066979320178   | 11.150726379700808   |
| Baking                      | 59.0  | 31.0          | 16.47743677581333  | 26.179207913512133 | 0.1389330432506246    | -0.32808407883948987 |
| Steaming                    | 215.0 | 110.0         | 14.593659979014994 | 20.984660658854494 | 0.69900108780239      | 3.3882662664912577   |
| Roasting                    | 29.0  | 22.0          | 11.850392864528493 | 21.587586344542917 | 0.536746237589925     | 0.20414835997553038  |
| Air frying                  | 27.0  | 18.0          | 11.197952078334113 | 20.0122733002137   | -0.05169810804237884  | 4.735097329390579    |

## 11. Compound-class analysis

| Compound_Class_Standardized   | n     | unique_groups | mae                | rmse               | r2                    | mean_signed_error    |
| ----------------------------- | ----- | ------------- | ------------------ | ------------------ | --------------------- | -------------------- |
| Flavonoid                     | 111.0 | 29.0          | 58.88084481264243  | 177.47342837118933 | 0.4151129624542813    | 17.048565473886683   |
| Isoflavone                    | 39.0  | 8.0           | 57.49560724777086  | 91.91482915454549  | 0.3530297149044398    | 26.81069589096518    |
| Vitamin                       | 162.0 | 13.0          | 52.73159790693833  | 293.4203966457342  | -0.014685662169373392 | 30.3056311709372     |
| Phenolic Acid                 | 150.0 | 16.0          | 46.807498849946946 | 156.82435076115448 | 0.4964722858926649    | 16.027669734247482   |
| Diarylheptanoid (curcuminoid) | 38.0  | 3.0           | 39.90456420347359  | 53.04432920408673  | -0.23893520790062284  | -4.770721423822655   |
| Phytosterol                   | 48.0  | 3.0           | 39.57916460189212  | 61.18946791047974  | 0.7966547904454079    | -0.8632726231092686  |
| Glucosinolate                 | 69.0  | 12.0          | 22.91671890766904  | 30.191817587241356 | -0.0193092762219651   | 6.193410970671522    |
| Carotenoid                    | 127.0 | 21.0          | 19.024837510248922 | 40.0195212168775   | 0.40322741319993927   | 8.620029858575148    |
| Phenolic                      | 32.0  | 3.0           | 11.560520722735188 | 17.354692506470904 | 0.22601505512735864   | -6.804958667521339   |
| Polyphenol                    | 29.0  | 11.0          | 8.730950996637693  | 15.859569766704823 | 0.425376609553219     | -0.3461445026362963  |
| Anthocyanin                   | 72.0  | 13.0          | 7.2441737323280835 | 10.656279817030418 | 0.8258074216917286    | -3.848286608192822   |
| Amino acid                    | 68.0  | 17.0          | 2.176436336830623  | 4.743492402030349  | 0.2815543231969878    | -0.42944528843304797 |

## 12. Retention-range analysis

| Retention_Range | n     | mae                | rmse               | mean_signed_error   | actual_min  | actual_max  |
| --------------- | ----- | ------------------ | ------------------ | ------------------- | ----------- | ----------- |
| low             | 283.0 | 19.652861585073047 | 27.49743637580042  | -16.020977105078018 | 1.46434635  | 56.8        |
| moderate        | 560.0 | 12.351556246873907 | 23.547453655645878 | 1.4010307395721444  | 57.0        | 94.4        |
| high            | 269.0 | 50.000923352851395 | 98.07576409457309  | 16.206252579625847  | 94.41964286 | 512.2977346 |
| extreme         | 12.0  | 833.2286883120349  | 1269.258783918469  | 828.0165274429138   | 529.16      | 3650.0      |

## 13. Temperature/time error analysis

- Absolute errors were plotted against `Temperature_C` and `Cooking_Time_min` to look for patterned deterioration regions.
- The observed patterns are descriptive and should not be interpreted as causal effects of temperature or time.

## 14. Robustness checks

| analysis                               | dataset                      | random_seed | mae                | rmse               | r2                  | notes                                                                               |
| -------------------------------------- | ---------------------------- | ----------- | ------------------ | ------------------ | ------------------- | ----------------------------------------------------------------------------------- |
| primary_phase2_candidate               | full                         | 42          | 31.959809          | 123.073056         | 0.380461            | Frozen Phase 2 OOF predictions for the locked final candidate.                      |
| sensitivity_without_top_1pct_retention | full_minus_extreme_retention | 42          | 21.720460086668254 | 41.56945089152035  | 0.4812113954138333  | Sensitivity only; excluded observations with Retention_Final >= 525.281679.         |
| sensitivity_alternative_model_seed     | full                         | 123         | 31.954354079605096 | 141.18536873071707 | 0.25727528147165235 | Sensitivity only; same model, same grouped folds, different ExtraTrees random seed. |
| group_size_bin_11_plus                 | full                         | 42          | 38.92934966808676  | 183.02748546963008 | 0.211283925645399   | Performance aggregated over groups with observation count bin 11_plus.              |
| group_size_bin_2_to_3                  | full                         | 42          | 27.303116639126046 | 38.13183960876773  | 0.39711594056440447 | Performance aggregated over groups with observation count bin 2_to_3.               |
| group_size_bin_4_to_10                 | full                         | 42          | 27.369318643453106 | 97.6087694504045   | 0.3756479683869679  | Performance aggregated over groups with observation count bin 4_to_10.              |
| group_size_bin_single                  | full                         | 42          | 17.187180433086432 | 55.38623485810092  | 0.01425064641179763 | Performance aggregated over groups with observation count bin single.               |

## 15. SHAP interpretation

| feature                                                    | mean_abs_shap      |
| ---------------------------------------------------------- | ------------------ |
| num__RDKit_Hydroxyl_Groups                                 | 0.0569053853744021 |
| num__RDKit_LogP                                            | 0.0444406097097604 |
| cat__Cooking_Method_Standardized_Boiling                   | 0.0440104196689859 |
| cat__Cooking_Medium_Standardized_Microwave                 | 0.0425905642162608 |
| cat__Initial_Unit_Standardized_mg/100g                     | 0.0391972523160552 |
| cat__Food_Name_Standardized_Cheddar Cauliflower            | 0.0357061008123964 |
| num__FE_Log_Initial_Concentration                          | 0.0321464987218171 |
| num__FE_Temperature_x_Time                                 | 0.0247169033122974 |
| num__FE_Log_Cooking_Time                                   | 0.0207496631158925 |
| cat__Food_Name_Standardized_Common Bean - Nero di Caposele | 0.0178003516524248 |

The leading SHAP features align with parts of the error analysis: descriptor-heavy chemistry features and boiling/microwave preparation contexts matter to the model, and several of the hardest observations occur in those same high-leverage regions.

## 16. Main strengths

- Phase 2 improved over Phase 1 on all three main metrics using the same GroupKFold philosophy.
- OOF predictions exist for every one of the 1124 modelling observations and remain genuinely out-of-fold.
- The final candidate uses both molecular and process/context information, and the error analysis still points to useful molecular contribution.

## 17. Main limitations

- Fold stability is only moderate because Fold 2 remains much harder than Fold 3.
- Extreme-retention observations contribute disproportionately to RMSE and to several of the worst residuals.
- A small number of repeated molecular groups still contribute a large share of the data, which limits how broadly the results should be generalized.
- SHAP is descriptive of the fitted model and should not be interpreted causally.

## 18. Suitability for downstream CookRisk risk-scoring development

- Conditionally suitable as a validated candidate for downstream CookRisk risk-scoring development, but not yet strong enough to describe as production-ready.
- The model is best described as a validated final candidate rather than a production-ready model.

## 19. Recommended next steps

- Use the saved OOF diagnostics to design Phase 4-style deployment safeguards rather than further unconstrained tuning.
- Examine whether the hardest molecular groups or cooking contexts need explicit uncertainty communication in downstream scoring.
- Add external or prospective validation before making strong claims about generalization beyond the current literature-derived dataset.

## Executive answers

1. Did Phase 2 genuinely improve over Phase 1? Yes, on MAE, RMSE, and R2 under the same grouped-validation framework.
2. By how much? MAE improved by 9.035476, RMSE by 5.942400, and R2 by 0.069254.
3. Which Phase 2 intervention contributed most? The model-family switch to ExtraTrees after targeted engineered features produced the largest additional gain.
4. Which interventions did not help? Sparse-feature ablation, food simplification, and supervised feature selection did not improve the grouped-CV benchmark.
5. Is the improvement stable across molecular groups? It is real but not uniformly stable; Fold 2 and several molecular groups remain much harder than others.
6. Where does the model fail? The largest errors concentrate in a subset of molecular groups and in some extreme-retention observations.
7. Are extreme retention values a major source of error? Yes, they are a major contributor to RMSE sensitivity and several of the worst residuals.
8. Are particular cooking methods/classes difficult? Some methods and classes show higher error, but the interpretation is limited to categories with adequate sample counts.
9. What are the most influential features? RDKit_Hydroxyl_Groups, RDKit_LogP, boiling, microwave-related context, and engineered concentration/time features.
10. What are the major limitations? Fold instability, repeated-group imbalance, extreme-target sensitivity, sparse process fields, and non-causal interpretability.
11. Is the model ready for downstream CookRisk risk-scoring integration? It is suitable as a cautious candidate for further integration work, but not as a production-ready model.
12. What must happen before making strong claims from the model? External-style validation, clearer uncertainty handling, and explicit reporting of hard groups and sensitivity to extremes.
