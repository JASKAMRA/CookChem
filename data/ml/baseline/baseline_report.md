# CookRisk Phase 1 Baseline Report

## 1. Dataset used

- Source dataset: `data/preprocessing/final/cookchem_molecular_retention_preprocessed.csv`
- Repository root: `C:\Users\kamra\Desktop\BTP\CookChem`
- Rows: 1124
- Unique `Canonical_Molecular_ID`: 197

## 2. Dataset statistics

- Target missingness: 0
- Target range: 1.464346 to 3650.000000
- Target median: 78.000000
- Target mean: 96.402367
- Target standard deviation: 163.896255
- Target skewness: 13.868923
- Apparent increases (>100%): 189
- Group size min/median/mean/max: 1 / 4.00 / 5.71 / 102

### Candidate predictor missingness

| column                      | dtype   | missing_count | missing_percentage | non_missing_count | unique_non_null_values |
| --------------------------- | ------- | ------------- | ------------------ | ----------------- | ---------------------- |
| Pressure_kPa                | float64 | 1114          | 99.1103            | 10                | 3                      |
| Microwave_Power_W           | float64 | 1056          | 93.9502            | 68                | 7                      |
| Oil_Type_Standardized       | str     | 942           | 83.8078            | 182               | 10                     |
| Temperature_C               | float64 | 403           | 35.8541            | 721               | 30                     |
| Sample_Weight_g             | float64 | 248           | 22.0641            | 876               | 9                      |
| Cooking_Time_min            | float64 | 229           | 20.3737            | 895               | 43                     |
| Replicates_n                | float64 | 200           | 17.7936            | 924               | 4                      |
| Initial_Concentration       | float64 | 54            | 4.8043             | 1070              | 359                    |
| Initial_Unit_Standardized   | str     | 46            | 4.0925             | 1078              | 15                     |
| Assay_Method_Standardized   | str     | 44            | 3.9146             | 1080              | 35                     |
| Cooking_Medium_Standardized | str     | 39            | 3.4698             | 1085              | 30                     |
| RDKit_Hydroxyl_Groups       | float64 | 14            | 1.2456             | 1110              | 16                     |
| Compound_Class_Standardized | str     | 0             | 0.0                | 1124              | 51                     |
| Cooking_Method_Standardized | str     | 0             | 0.0                | 1124              | 37                     |
| Food_Name_Standardized      | str     | 0             | 0.0                | 1124              | 158                    |
| RDKit_Aromatic_Rings        | float64 | 0             | 0.0                | 1124              | 9                      |
| RDKit_HBond_Acceptors       | float64 | 0             | 0.0                | 1124              | 21                     |
| RDKit_HBond_Donors          | float64 | 0             | 0.0                | 1124              | 16                     |
| RDKit_Heavy_Atom_Count      | float64 | 0             | 0.0                | 1124              | 50                     |
| RDKit_LogP                  | float64 | 0             | 0.0                | 1124              | 182                    |
| RDKit_Molecular_Weight      | float64 | 0             | 0.0                | 1124              | 168                    |
| RDKit_Rotatable_Bonds       | float64 | 0             | 0.0                | 1124              | 21                     |
| RDKit_TPSA                  | float64 | 0             | 0.0                | 1124              | 122                    |

## 3. Predictor groups

- `process_only`: Temperature_C, Cooking_Time_min, Pressure_kPa, Microwave_Power_W, Sample_Weight_g, Initial_Concentration, Replicates_n, Assay_Method_Standardized, Compound_Class_Standardized, Cooking_Medium_Standardized, Cooking_Method_Standardized, Food_Name_Standardized, Initial_Unit_Standardized, Oil_Type_Standardized
- `molecular_only`: RDKit_Molecular_Weight, RDKit_LogP, RDKit_TPSA, RDKit_HBond_Donors, RDKit_HBond_Acceptors, RDKit_Rotatable_Bonds, RDKit_Aromatic_Rings, RDKit_Hydroxyl_Groups, RDKit_Heavy_Atom_Count
- `molecular_plus_process`: Temperature_C, Cooking_Time_min, Pressure_kPa, Microwave_Power_W, Sample_Weight_g, Initial_Concentration, Replicates_n, Assay_Method_Standardized, Compound_Class_Standardized, Cooking_Medium_Standardized, Cooking_Method_Standardized, Food_Name_Standardized, Initial_Unit_Standardized, Oil_Type_Standardized, RDKit_Molecular_Weight, RDKit_LogP, RDKit_TPSA, RDKit_HBond_Donors, RDKit_HBond_Acceptors, RDKit_Rotatable_Bonds, RDKit_Aromatic_Rings, RDKit_Hydroxyl_Groups, RDKit_Heavy_Atom_Count

## 4. Leakage audit

- `Canonical_Molecular_ID` used only as the grouping variable and never as a predictor.
- `Apparent_Increase` excluded because it is derived from the reviewed retention target.
- Explicit leakage exclusions from preprocessing manifest: Apparent_Increase, Calculated_Retention_Percent, Canonical_Molecular_ID, Data_Readiness_Status, Degradation_Percent, Descriptor_Status, Duplicate_Review_Status, Duplicate_Status, Final_Concentration, Final_ML_Eligible_Reviewed, Final_ML_Status_Reviewed, Final_Preprocessing_Eligible, Final_Preprocessing_Status, Final_Unit, Molecular_Descriptor_Consistency, Molecular_Descriptor_Status, Molecular_Feature_Eligible, Molecular_Identity_Status, Molecular_Model_Eligible, Paper_ID_DOI_Status, Reported_Retention_Percent, Retention_Calculated_Percent, Retention_Calculation_Delta, Retention_Eligibility_Promotion_Reason, Retention_Final, Retention_Final_Status, Retention_Model_Eligible, Retention_Model_Eligible_Previous, Retention_Model_Eligible_Reviewed, Retention_Percent, Retention_Review_Reason, Retention_Review_Required, Retention_Source_Evidence, Retention_Validation_Status, Review_Automatic_Acceptance, SMILES_Validation_Status, Source_Identity_Status, Source_Status, Source_Verification_Required, Unit_Compatibility_Status
- Identifier/provenance exclusions from X: Authors, Canonical_Compound_Name, Canonical_Molecular_ID, Canonical_SMILES, Compound_Class, Compound_Name, Cooking_Method, Country, DOI, DOI_Normalized, Food_Name, Initial_Unit, Journal, Paper_ID, Plant_Part, PubChem_CID, PubChem_CID_Resolved, Record_ID, Scientific_Name, Source_Paper_Key, Year

## 5. Validation strategy

- Cross-validation: `GroupKFold(n_splits=5)`
- Grouping column: `Canonical_Molecular_ID`
- Programmatic train/validation group-overlap check: PASS

| model                  | feature_group          | target_representation | fold | train_rows | validation_rows | train_groups | validation_groups | group_intersection_count |
| ---------------------- | ---------------------- | --------------------- | ---- | ---------- | --------------- | ------------ | ----------------- | ------------------------ |
| dummy                  | molecular_only         | log1p                 | 1    | 899        | 225             | 161          | 36                | 0                        |
| dummy                  | molecular_only         | log1p                 | 2    | 899        | 225             | 157          | 40                | 0                        |
| dummy                  | molecular_only         | log1p                 | 3    | 899        | 225             | 157          | 40                | 0                        |
| dummy                  | molecular_only         | log1p                 | 4    | 899        | 225             | 156          | 41                | 0                        |
| dummy                  | molecular_only         | log1p                 | 5    | 900        | 224             | 157          | 40                | 0                        |
| dummy                  | molecular_only         | raw                   | 1    | 899        | 225             | 161          | 36                | 0                        |
| dummy                  | molecular_only         | raw                   | 2    | 899        | 225             | 157          | 40                | 0                        |
| dummy                  | molecular_only         | raw                   | 3    | 899        | 225             | 157          | 40                | 0                        |
| dummy                  | molecular_only         | raw                   | 4    | 899        | 225             | 156          | 41                | 0                        |
| dummy                  | molecular_only         | raw                   | 5    | 900        | 224             | 157          | 40                | 0                        |
| dummy                  | molecular_plus_process | log1p                 | 1    | 899        | 225             | 161          | 36                | 0                        |
| dummy                  | molecular_plus_process | log1p                 | 2    | 899        | 225             | 157          | 40                | 0                        |
| dummy                  | molecular_plus_process | log1p                 | 3    | 899        | 225             | 157          | 40                | 0                        |
| dummy                  | molecular_plus_process | log1p                 | 4    | 899        | 225             | 156          | 41                | 0                        |
| dummy                  | molecular_plus_process | log1p                 | 5    | 900        | 224             | 157          | 40                | 0                        |
| dummy                  | molecular_plus_process | raw                   | 1    | 899        | 225             | 161          | 36                | 0                        |
| dummy                  | molecular_plus_process | raw                   | 2    | 899        | 225             | 157          | 40                | 0                        |
| dummy                  | molecular_plus_process | raw                   | 3    | 899        | 225             | 157          | 40                | 0                        |
| dummy                  | molecular_plus_process | raw                   | 4    | 899        | 225             | 156          | 41                | 0                        |
| dummy                  | molecular_plus_process | raw                   | 5    | 900        | 224             | 157          | 40                | 0                        |
| dummy                  | process_only           | log1p                 | 1    | 899        | 225             | 161          | 36                | 0                        |
| dummy                  | process_only           | log1p                 | 2    | 899        | 225             | 157          | 40                | 0                        |
| dummy                  | process_only           | log1p                 | 3    | 899        | 225             | 157          | 40                | 0                        |
| dummy                  | process_only           | log1p                 | 4    | 899        | 225             | 156          | 41                | 0                        |
| dummy                  | process_only           | log1p                 | 5    | 900        | 224             | 157          | 40                | 0                        |
| dummy                  | process_only           | raw                   | 1    | 899        | 225             | 161          | 36                | 0                        |
| dummy                  | process_only           | raw                   | 2    | 899        | 225             | 157          | 40                | 0                        |
| dummy                  | process_only           | raw                   | 3    | 899        | 225             | 157          | 40                | 0                        |
| dummy                  | process_only           | raw                   | 4    | 899        | 225             | 156          | 41                | 0                        |
| dummy                  | process_only           | raw                   | 5    | 900        | 224             | 157          | 40                | 0                        |
| hist_gradient_boosting | molecular_only         | log1p                 | 1    | 899        | 225             | 161          | 36                | 0                        |
| hist_gradient_boosting | molecular_only         | log1p                 | 2    | 899        | 225             | 157          | 40                | 0                        |
| hist_gradient_boosting | molecular_only         | log1p                 | 3    | 899        | 225             | 157          | 40                | 0                        |
| hist_gradient_boosting | molecular_only         | log1p                 | 4    | 899        | 225             | 156          | 41                | 0                        |
| hist_gradient_boosting | molecular_only         | log1p                 | 5    | 900        | 224             | 157          | 40                | 0                        |
| hist_gradient_boosting | molecular_only         | raw                   | 1    | 899        | 225             | 161          | 36                | 0                        |
| hist_gradient_boosting | molecular_only         | raw                   | 2    | 899        | 225             | 157          | 40                | 0                        |
| hist_gradient_boosting | molecular_only         | raw                   | 3    | 899        | 225             | 157          | 40                | 0                        |
| hist_gradient_boosting | molecular_only         | raw                   | 4    | 899        | 225             | 156          | 41                | 0                        |
| hist_gradient_boosting | molecular_only         | raw                   | 5    | 900        | 224             | 157          | 40                | 0                        |
| hist_gradient_boosting | molecular_plus_process | log1p                 | 1    | 899        | 225             | 161          | 36                | 0                        |
| hist_gradient_boosting | molecular_plus_process | log1p                 | 2    | 899        | 225             | 157          | 40                | 0                        |
| hist_gradient_boosting | molecular_plus_process | log1p                 | 3    | 899        | 225             | 157          | 40                | 0                        |
| hist_gradient_boosting | molecular_plus_process | log1p                 | 4    | 899        | 225             | 156          | 41                | 0                        |
| hist_gradient_boosting | molecular_plus_process | log1p                 | 5    | 900        | 224             | 157          | 40                | 0                        |
| hist_gradient_boosting | molecular_plus_process | raw                   | 1    | 899        | 225             | 161          | 36                | 0                        |
| hist_gradient_boosting | molecular_plus_process | raw                   | 2    | 899        | 225             | 157          | 40                | 0                        |
| hist_gradient_boosting | molecular_plus_process | raw                   | 3    | 899        | 225             | 157          | 40                | 0                        |
| hist_gradient_boosting | molecular_plus_process | raw                   | 4    | 899        | 225             | 156          | 41                | 0                        |
| hist_gradient_boosting | molecular_plus_process | raw                   | 5    | 900        | 224             | 157          | 40                | 0                        |
| hist_gradient_boosting | process_only           | log1p                 | 1    | 899        | 225             | 161          | 36                | 0                        |
| hist_gradient_boosting | process_only           | log1p                 | 2    | 899        | 225             | 157          | 40                | 0                        |
| hist_gradient_boosting | process_only           | log1p                 | 3    | 899        | 225             | 157          | 40                | 0                        |
| hist_gradient_boosting | process_only           | log1p                 | 4    | 899        | 225             | 156          | 41                | 0                        |
| hist_gradient_boosting | process_only           | log1p                 | 5    | 900        | 224             | 157          | 40                | 0                        |
| hist_gradient_boosting | process_only           | raw                   | 1    | 899        | 225             | 161          | 36                | 0                        |
| hist_gradient_boosting | process_only           | raw                   | 2    | 899        | 225             | 157          | 40                | 0                        |
| hist_gradient_boosting | process_only           | raw                   | 3    | 899        | 225             | 157          | 40                | 0                        |
| hist_gradient_boosting | process_only           | raw                   | 4    | 899        | 225             | 156          | 41                | 0                        |
| hist_gradient_boosting | process_only           | raw                   | 5    | 900        | 224             | 157          | 40                | 0                        |
| ridge                  | molecular_only         | log1p                 | 1    | 899        | 225             | 161          | 36                | 0                        |
| ridge                  | molecular_only         | log1p                 | 2    | 899        | 225             | 157          | 40                | 0                        |
| ridge                  | molecular_only         | log1p                 | 3    | 899        | 225             | 157          | 40                | 0                        |
| ridge                  | molecular_only         | log1p                 | 4    | 899        | 225             | 156          | 41                | 0                        |
| ridge                  | molecular_only         | log1p                 | 5    | 900        | 224             | 157          | 40                | 0                        |
| ridge                  | molecular_only         | raw                   | 1    | 899        | 225             | 161          | 36                | 0                        |
| ridge                  | molecular_only         | raw                   | 2    | 899        | 225             | 157          | 40                | 0                        |
| ridge                  | molecular_only         | raw                   | 3    | 899        | 225             | 157          | 40                | 0                        |
| ridge                  | molecular_only         | raw                   | 4    | 899        | 225             | 156          | 41                | 0                        |
| ridge                  | molecular_only         | raw                   | 5    | 900        | 224             | 157          | 40                | 0                        |
| ridge                  | molecular_plus_process | log1p                 | 1    | 899        | 225             | 161          | 36                | 0                        |
| ridge                  | molecular_plus_process | log1p                 | 2    | 899        | 225             | 157          | 40                | 0                        |
| ridge                  | molecular_plus_process | log1p                 | 3    | 899        | 225             | 157          | 40                | 0                        |
| ridge                  | molecular_plus_process | log1p                 | 4    | 899        | 225             | 156          | 41                | 0                        |
| ridge                  | molecular_plus_process | log1p                 | 5    | 900        | 224             | 157          | 40                | 0                        |
| ridge                  | molecular_plus_process | raw                   | 1    | 899        | 225             | 161          | 36                | 0                        |
| ridge                  | molecular_plus_process | raw                   | 2    | 899        | 225             | 157          | 40                | 0                        |
| ridge                  | molecular_plus_process | raw                   | 3    | 899        | 225             | 157          | 40                | 0                        |
| ridge                  | molecular_plus_process | raw                   | 4    | 899        | 225             | 156          | 41                | 0                        |
| ridge                  | molecular_plus_process | raw                   | 5    | 900        | 224             | 157          | 40                | 0                        |
| ridge                  | process_only           | log1p                 | 1    | 899        | 225             | 161          | 36                | 0                        |
| ridge                  | process_only           | log1p                 | 2    | 899        | 225             | 157          | 40                | 0                        |
| ridge                  | process_only           | log1p                 | 3    | 899        | 225             | 157          | 40                | 0                        |
| ridge                  | process_only           | log1p                 | 4    | 899        | 225             | 156          | 41                | 0                        |
| ridge                  | process_only           | log1p                 | 5    | 900        | 224             | 157          | 40                | 0                        |
| ridge                  | process_only           | raw                   | 1    | 899        | 225             | 161          | 36                | 0                        |
| ridge                  | process_only           | raw                   | 2    | 899        | 225             | 157          | 40                | 0                        |
| ridge                  | process_only           | raw                   | 3    | 899        | 225             | 157          | 40                | 0                        |
| ridge                  | process_only           | raw                   | 4    | 899        | 225             | 156          | 41                | 0                        |
| ridge                  | process_only           | raw                   | 5    | 900        | 224             | 157          | 40                | 0                        |

## 6. Missing-value strategy

- No rows were dropped for predictor missingness.
- Numerical predictors: fold-safe median imputation within each training fold.
- Categorical predictors: fold-safe constant `Missing` category, then one-hot encoding with `handle_unknown='ignore'`.
- `RDKit_Hydroxyl_Groups` retained with fold-safe imputation; missing rows explicitly reported in the audit.

## 7. Models

- `dummy`: `DummyRegressor(strategy='mean')`
- `ridge`: `Ridge(alpha=1.0)`
- `hist_gradient_boosting`: `HistGradientBoostingRegressor(random_state=42)`

## 8. Target representations

- `raw`: modelled directly on `Retention_Final`.
- `log1p`: trained on `log1p(Retention_Final)` and inverse-transformed with `expm1` before computing MAE, RMSE, and R2 on the original scale.

## 9. Complete experiment matrix

| model                  | feature_group          | target_representation | folds |
| ---------------------- | ---------------------- | --------------------- | ----- |
| dummy                  | molecular_only         | log1p                 | 5     |
| dummy                  | molecular_only         | raw                   | 5     |
| dummy                  | molecular_plus_process | log1p                 | 5     |
| dummy                  | molecular_plus_process | raw                   | 5     |
| dummy                  | process_only           | log1p                 | 5     |
| dummy                  | process_only           | raw                   | 5     |
| hist_gradient_boosting | molecular_only         | log1p                 | 5     |
| hist_gradient_boosting | molecular_only         | raw                   | 5     |
| hist_gradient_boosting | molecular_plus_process | log1p                 | 5     |
| hist_gradient_boosting | molecular_plus_process | raw                   | 5     |
| hist_gradient_boosting | process_only           | log1p                 | 5     |
| hist_gradient_boosting | process_only           | raw                   | 5     |
| ridge                  | molecular_only         | log1p                 | 5     |
| ridge                  | molecular_only         | raw                   | 5     |
| ridge                  | molecular_plus_process | log1p                 | 5     |
| ridge                  | molecular_plus_process | raw                   | 5     |
| ridge                  | process_only           | log1p                 | 5     |
| ridge                  | process_only           | raw                   | 5     |

## 10. Fold-wise metrics

| model                  | feature_group          | target_representation | fold | mae                | rmse               | r2                      |
| ---------------------- | ---------------------- | --------------------- | ---- | ------------------ | ------------------ | ----------------------- |
| dummy                  | process_only           | raw                   | 1    | 55.24895885037992  | 161.53241876895115 | -0.012972583475981736   |
| dummy                  | process_only           | raw                   | 2    | 64.58942180922676  | 255.0214976993593  | -0.001229021732960689   |
| dummy                  | process_only           | raw                   | 3    | 43.615389004891064 | 97.23738004633637  | -1.2433119260579772e-05 |
| dummy                  | process_only           | raw                   | 4    | 48.36677905253757  | 165.6430873068584  | -0.004922461981871296   |
| dummy                  | process_only           | raw                   | 5    | 41.733201459705256 | 79.2245617360634   | -0.0005825247671371603  |
| ridge                  | process_only           | raw                   | 1    | 84.55972368808979  | 162.7103960443744  | -0.027800685727703778   |
| ridge                  | process_only           | raw                   | 2    | 54.18030690944684  | 247.0008703019965  | 0.06075949648462742     |
| ridge                  | process_only           | raw                   | 3    | 50.29683203898702  | 91.35584763451328  | 0.11730309231966596     |
| ridge                  | process_only           | raw                   | 4    | 56.85734221180927  | 123.26380024725464 | 0.44351043280840774     |
| ridge                  | process_only           | raw                   | 5    | 1829.732649257363  | 26675.414194559587 | -113436.21769589452     |
| hist_gradient_boosting | process_only           | raw                   | 1    | 81.83815231177125  | 168.13989948837522 | -0.09753875805641088    |
| hist_gradient_boosting | process_only           | raw                   | 2    | 60.14274724869916  | 247.78024905498063 | 0.054822845376086615    |
| hist_gradient_boosting | process_only           | raw                   | 3    | 30.88346812787782  | 63.699516997655245 | 0.5708479605816198      |
| hist_gradient_boosting | process_only           | raw                   | 4    | 45.950255981393816 | 130.6140387632628  | 0.3751645832924565      |
| hist_gradient_boosting | process_only           | raw                   | 5    | 36.06714130211243  | 69.60935774221153  | 0.2275533815557138      |
| dummy                  | process_only           | log1p                 | 1    | 40.58644376448241  | 160.6366380998037  | -0.001768823125051222   |
| dummy                  | process_only           | log1p                 | 2    | 60.04298751317236  | 256.73537528622455 | -0.014731806002105774   |
| dummy                  | process_only           | log1p                 | 3    | 41.66332716593558  | 100.8843220138836  | -0.07643116121301219    |
| dummy                  | process_only           | log1p                 | 4    | 49.37174336682473  | 169.42071496826387 | -0.051281304411122      |
| dummy                  | process_only           | log1p                 | 5    | 40.96435261147262  | 83.26518486931582  | -0.10524898341027211    |
| ridge                  | process_only           | log1p                 | 1    | 46.57784561698101  | 144.20439749525673 | 0.1926993401745115      |
| ridge                  | process_only           | log1p                 | 2    | 48.99327242258537  | 251.02711002314692 | 0.029889738983116643    |
| ridge                  | process_only           | log1p                 | 3    | 39.140905309007344 | 84.24316754614595  | 0.24940048741921783     |
| ridge                  | process_only           | log1p                 | 4    | 40.83333654272676  | 132.42602649897955 | 0.35770784591700133     |
| ridge                  | process_only           | log1p                 | 5    | 38.35057263286266  | 77.16208015032714  | 0.050836395966887604    |
| hist_gradient_boosting | process_only           | log1p                 | 1    | 42.589189171973366 | 143.8286945281156  | 0.19690046233610703     |
| hist_gradient_boosting | process_only           | log1p                 | 2    | 52.628646061953454 | 242.38300263577744 | 0.09555082258258651     |
| hist_gradient_boosting | process_only           | log1p                 | 3    | 31.539773594750535 | 70.3283692359972   | 0.47688159948634545     |
| hist_gradient_boosting | process_only           | log1p                 | 4    | 41.27901787329893  | 133.2372049455019  | 0.34981499727712995     |
| hist_gradient_boosting | process_only           | log1p                 | 5    | 33.702998251502486 | 75.26592182549587  | 0.09691216333511132     |
| dummy                  | molecular_only         | raw                   | 1    | 55.24895885037992  | 161.53241876895115 | -0.012972583475981736   |
| dummy                  | molecular_only         | raw                   | 2    | 64.58942180922676  | 255.0214976993593  | -0.001229021732960689   |
| dummy                  | molecular_only         | raw                   | 3    | 43.615389004891064 | 97.23738004633637  | -1.2433119260579772e-05 |
| dummy                  | molecular_only         | raw                   | 4    | 48.36677905253757  | 165.6430873068584  | -0.004922461981871296   |
| dummy                  | molecular_only         | raw                   | 5    | 41.733201459705256 | 79.2245617360634   | -0.0005825247671371603  |
| ridge                  | molecular_only         | raw                   | 1    | 47.413627921089144 | 159.77106470063825 | 0.00899793974683305     |
| ridge                  | molecular_only         | raw                   | 2    | 63.98436791711648  | 253.54821218085064 | 0.010305969161010453    |
| ridge                  | molecular_only         | raw                   | 3    | 52.846937508450274 | 99.79357816926023  | -0.053280616129075975   |
| ridge                  | molecular_only         | raw                   | 4    | 54.009842162239735 | 165.97431512931556 | -0.008945462082721178   |
| ridge                  | molecular_only         | raw                   | 5    | 49.94121660610619  | 82.30512016896816  | -0.0799084254227922     |
| hist_gradient_boosting | molecular_only         | raw                   | 1    | 40.57649587513343  | 159.7418477083891  | 0.009360351453614912    |
| hist_gradient_boosting | molecular_only         | raw                   | 2    | 72.54793620570024  | 257.79665182660335 | -0.023138414502193116   |
| hist_gradient_boosting | molecular_only         | raw                   | 3    | 45.596541225033306 | 96.89204427906071  | 0.007077984743701249    |
| hist_gradient_boosting | molecular_only         | raw                   | 4    | 65.42871957313503  | 176.2716499636436  | -0.13802253023237032    |
| hist_gradient_boosting | molecular_only         | raw                   | 5    | 57.071550270793864 | 90.70560939930768  | -0.3116003194069734     |
| dummy                  | molecular_only         | log1p                 | 1    | 40.58644376448241  | 160.6366380998037  | -0.001768823125051222   |
| dummy                  | molecular_only         | log1p                 | 2    | 60.04298751317236  | 256.73537528622455 | -0.014731806002105774   |
| dummy                  | molecular_only         | log1p                 | 3    | 41.66332716593558  | 100.8843220138836  | -0.07643116121301219    |
| dummy                  | molecular_only         | log1p                 | 4    | 49.37174336682473  | 169.42071496826387 | -0.051281304411122      |
| dummy                  | molecular_only         | log1p                 | 5    | 40.96435261147262  | 83.26518486931582  | -0.10524898341027211    |
| ridge                  | molecular_only         | log1p                 | 1    | 41.55890336573182  | 160.56497115183942 | -0.0008751577716348269  |
| ridge                  | molecular_only         | log1p                 | 2    | 59.60333732985647  | 254.4828920086273  | 0.002995705882161692    |
| ridge                  | molecular_only         | log1p                 | 3    | 41.29232519850657  | 100.04652078219239 | -0.05862679565967399    |
| ridge                  | molecular_only         | log1p                 | 4    | 49.55893735369938  | 167.8704743415577  | -0.032130367230615464   |
| ridge                  | molecular_only         | log1p                 | 5    | 42.24517027019869  | 82.0079048762354   | -0.07212310725908044    |
| hist_gradient_boosting | molecular_only         | log1p                 | 1    | 42.14892557945822  | 160.77719811149606 | -0.003522722412675483   |
| hist_gradient_boosting | molecular_only         | log1p                 | 2    | 59.19426205061012  | 251.88433351146895 | 0.02325283666064093     |
| hist_gradient_boosting | molecular_only         | log1p                 | 3    | 42.08419922528014  | 102.72854279814051 | -0.11614638634253627    |
| hist_gradient_boosting | molecular_only         | log1p                 | 4    | 49.94512242301764  | 167.7123325221451  | -0.03018665326952652    |
| hist_gradient_boosting | molecular_only         | log1p                 | 5    | 42.79096732352208  | 79.33993775437298  | -0.0034989760820234306  |
| dummy                  | molecular_plus_process | raw                   | 1    | 55.24895885037992  | 161.53241876895115 | -0.012972583475981736   |
| dummy                  | molecular_plus_process | raw                   | 2    | 64.58942180922676  | 255.0214976993593  | -0.001229021732960689   |
| dummy                  | molecular_plus_process | raw                   | 3    | 43.615389004891064 | 97.23738004633637  | -1.2433119260579772e-05 |
| dummy                  | molecular_plus_process | raw                   | 4    | 48.36677905253757  | 165.6430873068584  | -0.004922461981871296   |
| dummy                  | molecular_plus_process | raw                   | 5    | 41.733201459705256 | 79.2245617360634   | -0.0005825247671371603  |
| ridge                  | molecular_plus_process | raw                   | 1    | 76.09527706211325  | 155.1927688870184  | 0.06497922132651601     |
| ridge                  | molecular_plus_process | raw                   | 2    | 55.09029692709301  | 242.86050927928787 | 0.09198369205509893     |
| ridge                  | molecular_plus_process | raw                   | 3    | 49.15154714905657  | 89.77857860912098  | 0.14751969795705178     |
| ridge                  | molecular_plus_process | raw                   | 4    | 60.397929017663344 | 126.0429396005166  | 0.41813401802524763     |
| ridge                  | molecular_plus_process | raw                   | 5    | 1566.0502067692712 | 22595.487152757207 | -81390.04807628316      |
| hist_gradient_boosting | molecular_plus_process | raw                   | 1    | 78.327835372415    | 164.68806891478903 | -0.05293745122306115    |
| hist_gradient_boosting | molecular_plus_process | raw                   | 2    | 57.78277367936797  | 244.69879222468197 | 0.07818558055879621     |
| hist_gradient_boosting | molecular_plus_process | raw                   | 3    | 29.267352942155437 | 60.1202078104104   | 0.6177215219540808      |
| hist_gradient_boosting | molecular_plus_process | raw                   | 4    | 46.87206107243194  | 124.08317601372694 | 0.4360874980797459      |
| hist_gradient_boosting | molecular_plus_process | raw                   | 5    | 39.07935622772102  | 68.31311318806678  | 0.25605405990013674     |
| dummy                  | molecular_plus_process | log1p                 | 1    | 40.58644376448241  | 160.6366380998037  | -0.001768823125051222   |
| dummy                  | molecular_plus_process | log1p                 | 2    | 60.04298751317236  | 256.73537528622455 | -0.014731806002105774   |
| dummy                  | molecular_plus_process | log1p                 | 3    | 41.66332716593558  | 100.8843220138836  | -0.07643116121301219    |
| dummy                  | molecular_plus_process | log1p                 | 4    | 49.37174336682473  | 169.42071496826387 | -0.051281304411122      |
| dummy                  | molecular_plus_process | log1p                 | 5    | 40.96435261147262  | 83.26518486931582  | -0.10524898341027211    |
| ridge                  | molecular_plus_process | log1p                 | 1    | 39.26554198558798  | 141.63786046656367 | 0.2211801456141309      |
| ridge                  | molecular_plus_process | log1p                 | 2    | 48.80874964993172  | 246.47739540046965 | 0.06473638795616332     |
| ridge                  | molecular_plus_process | log1p                 | 3    | 37.84177757527133  | 80.71058247675221  | 0.31103070831033774     |
| ridge                  | molecular_plus_process | log1p                 | 4    | 40.461480623370534 | 131.2503197265137  | 0.36906203474934673     |
| ridge                  | molecular_plus_process | log1p                 | 5    | 208.42181208757953 | 1301.786322640835  | -269.15476459675244     |
| hist_gradient_boosting | molecular_plus_process | log1p                 | 1    | 47.1532464674527   | 135.37886630105922 | 0.2884915789884186      |
| hist_gradient_boosting | molecular_plus_process | log1p                 | 2    | 52.64564336302713  | 240.33716168641078 | 0.11075444773733578     |
| hist_gradient_boosting | molecular_plus_process | log1p                 | 3    | 31.0247186342642   | 68.4851940574991   | 0.5039421992481605      |
| hist_gradient_boosting | molecular_plus_process | log1p                 | 4    | 41.25876876418668  | 136.11647362677166 | 0.32141024374698435     |
| hist_gradient_boosting | molecular_plus_process | log1p                 | 5    | 32.89404753300476  | 64.75958213287716  | 0.33143860030966954     |

## 11. Mean +- SD metrics

| model                  | feature_group          | target_representation | mae_mean           | mae_sd             | rmse_mean          | rmse_sd            | r2_mean               | r2_sd                 |
| ---------------------- | ---------------------- | --------------------- | ------------------ | ------------------ | ------------------ | ------------------ | --------------------- | --------------------- |
| dummy                  | molecular_only         | log1p                 | 46.525770884377536 | 8.376500515115964  | 154.1884470474983  | 68.30247526380344  | -0.049892415632312656 | 0.04278648224195805   |
| dummy                  | molecular_only         | raw                   | 50.71075003534811  | 9.349433084480333  | 151.7317891115137  | 69.2554674743486   | -0.003943805015442292 | 0.0053990866846165796 |
| dummy                  | molecular_plus_process | log1p                 | 46.525770884377536 | 8.376500515115964  | 154.1884470474983  | 68.30247526380344  | -0.049892415632312656 | 0.04278648224195805   |
| dummy                  | molecular_plus_process | raw                   | 50.71075003534811  | 9.349433084480333  | 151.7317891115137  | 69.2554674743486   | -0.003943805015442292 | 0.0053990866846165796 |
| dummy                  | process_only           | log1p                 | 46.525770884377536 | 8.376500515115964  | 154.1884470474983  | 68.30247526380344  | -0.049892415632312656 | 0.04278648224195805   |
| dummy                  | process_only           | raw                   | 50.71075003534811  | 9.349433084480333  | 151.7317891115137  | 69.2554674743486   | -0.003943805015442292 | 0.0053990866846165796 |
| hist_gradient_boosting | molecular_only         | log1p                 | 47.23269532037764  | 7.458502092359316  | 152.48846893952472 | 67.09464362341814  | -0.026020380289224154 | 0.05380813824053679   |
| hist_gradient_boosting | molecular_only         | raw                   | 56.24424862995918  | 13.320109913638152 | 156.2815606354009  | 68.08856554351699  | -0.09126458558884414  | 0.13708752246812864   |
| hist_gradient_boosting | molecular_plus_process | log1p                 | 40.995284952387095 | 9.2027578103763    | 129.01545556092358 | 71.19720769837569  | 0.31120741400611374   | 0.13996204567915124   |
| hist_gradient_boosting | molecular_plus_process | raw                   | 50.265875858818276 | 18.85186654903275  | 132.38067163033503 | 75.9180532595402   | 0.2670222418539397    | 0.2691313976405632    |
| hist_gradient_boosting | process_only           | log1p                 | 40.34792499069575  | 8.343334038312898  | 133.0086386341776  | 69.53940406190068  | 0.24321200900345605   | 0.1668216898351655    |
| hist_gradient_boosting | process_only           | raw                   | 50.97635299437089  | 20.541079009267357 | 135.9686124092971  | 76.1443991575049   | 0.22617000254989317   | 0.2622743809190393    |
| ridge                  | molecular_only         | log1p                 | 46.85173470359858  | 7.906861722930543  | 152.99455263209046 | 67.86214988686466  | -0.032151944407768605 | 0.03358648082657908   |
| ridge                  | molecular_only         | raw                   | 53.639198423000366 | 6.328909534676942  | 152.27845806980656 | 67.36135648053322  | -0.02456611894534917  | 0.040230295550640116  |
| ridge                  | molecular_plus_process | log1p                 | 74.95987238434822  | 74.72942490844025  | 380.37249614222685 | 518.6002037264351  | -53.6377510640245     | 120.47772788719672    |
| ridge                  | molecular_plus_process | raw                   | 361.3570513850394  | 673.5183504584471  | 4641.872389826631  | 10036.53521255623  | -16277.865091930758   | 36398.81682937467     |
| ridge                  | process_only           | log1p                 | 42.77918650483262  | 4.734995190215326  | 137.81255634277127 | 69.70574793468893  | 0.17610676169214698   | 0.1375666383449531    |
| ridge                  | process_only           | raw                   | 415.12537082113914 | 790.9052695274231  | 5459.949021757546  | 11859.948669878535 | -22687.124784711727   | 50730.28516177466     |

## 12. Best baseline

- Selection rule: lowest mean RMSE on the original retention scale; ties broken by lower mean MAE, then higher mean R2.
- Best model: `hist_gradient_boosting`
- Feature group: `molecular_plus_process`
- Target representation: `log1p`
- MAE: 40.995285 +- 9.202758
- RMSE: 129.015456 +- 71.197208
- R2: 0.311207 +- 0.139962
- OOF rows for best baseline: 1124

## 13. Limitations

- Pressure, microwave power, and oil type remain scientifically plausible but extremely sparse, so baseline estimates for their utility remain unstable.
- Food name is high-cardinality and may add variance without necessarily improving unseen-compound generalization.
- Grouped validation is honest for unseen-compound performance, but repeated-compound imbalance still means a few compounds dominate the sample count.
- Descriptor correlations from EDA remain exploratory; the grouped-CV baseline is the first actual predictive test.

## 14. Recommendations for Phase 2

- Revisit whether ultra-sparse process variables should be grouped, excluded, or re-expressed after inspecting the baseline results.
- Explore feature engineering only after locking the Phase 1 benchmark and its exact leakage-safe feature lists.
- Consider controlled comparisons that reduce food-cardinality burden without leaking compound identity.
- Reserve SHAP, detailed error analysis, and broader model tuning for the next phase only.

## Supplementary audit outputs

- Column audit: `C:\Users\kamra\Desktop\CookChem\data\ml\baseline\audit\column_audit.csv`
- Candidate predictor missingness: `C:\Users\kamra\Desktop\CookChem\data\ml\baseline\audit\candidate_predictor_missingness.csv`
- Group observation counts: `C:\Users\kamra\Desktop\CookChem\data\ml\baseline\audit\group_observation_counts.csv`
- Dataset audit JSON: `C:\Users\kamra\Desktop\CookChem\data\ml\baseline\audit\dataset_audit.json`

## Predictor role audit

| column                      | dtype   | role                  | missing_count | missing_percentage | non_missing_count | unique_non_null_values |
| --------------------------- | ------- | --------------------- | ------------- | ------------------ | ----------------- | ---------------------- |
| Oil_Type_Standardized       | str     | categorical_predictor | 942           | 83.8078            | 182               | 10                     |
| Initial_Unit_Standardized   | str     | categorical_predictor | 46            | 4.0925             | 1078              | 15                     |
| Assay_Method_Standardized   | str     | categorical_predictor | 44            | 3.9146             | 1080              | 35                     |
| Cooking_Medium_Standardized | str     | categorical_predictor | 39            | 3.4698             | 1085              | 30                     |
| Compound_Class_Standardized | str     | categorical_predictor | 0             | 0.0                | 1124              | 51                     |
| Cooking_Method_Standardized | str     | categorical_predictor | 0             | 0.0                | 1124              | 37                     |
| Food_Name_Standardized      | str     | categorical_predictor | 0             | 0.0                | 1124              | 158                    |
| PubChem_CID_Resolved        | float64 | identifier            | 567           | 50.4448            | 557               | 112                    |
| PubChem_CID                 | float64 | identifier            | 77            | 6.8505             | 1047              | 196                    |
| Initial_Unit                | str     | identifier            | 46            | 4.0925             | 1078              | 16                     |
| Country                     | str     | identifier            | 40            | 3.5587             | 1084              | 30                     |
| Authors                     | str     | identifier            | 0             | 0.0                | 1124              | 107                    |
| Canonical_Compound_Name     | str     | identifier            | 0             | 0.0                | 1124              | 198                    |
| Canonical_Molecular_ID      | str     | identifier            | 0             | 0.0                | 1124              | 197                    |
| Canonical_SMILES            | str     | identifier            | 0             | 0.0                | 1124              | 197                    |
| Compound_Class              | str     | identifier            | 0             | 0.0                | 1124              | 52                     |
| Compound_Name               | str     | identifier            | 0             | 0.0                | 1124              | 219                    |
| Cooking_Method              | str     | identifier            | 0             | 0.0                | 1124              | 46                     |
| DOI                         | str     | identifier            | 0             | 0.0                | 1124              | 183                    |
| DOI_Normalized              | str     | identifier            | 0             | 0.0                | 1124              | 183                    |
| Food_Name                   | str     | identifier            | 0             | 0.0                | 1124              | 160                    |
| Journal                     | str     | identifier            | 0             | 0.0                | 1124              | 36                     |
| Paper_ID                    | str     | identifier            | 0             | 0.0                | 1124              | 183                    |
| Plant_Part                  | str     | identifier            | 0             | 0.0                | 1124              | 62                     |
| Record_ID                   | str     | identifier            | 0             | 0.0                | 1124              | 1124                   |
| Scientific_Name             | str     | identifier            | 0             | 0.0                | 1124              | 117                    |
| Source_Paper_Key            | str     | identifier            | 0             | 0.0                | 1124              | 183                    |
| Year                        | float64 | identifier            | 0             | 0.0                | 1124              | 25                     |
| Apparent_Increase           | int64   | leakage               | 0             | 0.0                | 1124              | 2                      |
| Pressure_kPa                | float64 | numeric_predictor     | 1114          | 99.1103            | 10                | 3                      |
| Microwave_Power_W           | float64 | numeric_predictor     | 1056          | 93.9502            | 68                | 7                      |
| Temperature_C               | float64 | numeric_predictor     | 403           | 35.8541            | 721               | 30                     |
| Sample_Weight_g             | float64 | numeric_predictor     | 248           | 22.0641            | 876               | 9                      |
| Cooking_Time_min            | float64 | numeric_predictor     | 229           | 20.3737            | 895               | 43                     |
| Replicates_n                | float64 | numeric_predictor     | 200           | 17.7936            | 924               | 4                      |
| Initial_Concentration       | float64 | numeric_predictor     | 54            | 4.8043             | 1070              | 359                    |
| RDKit_Hydroxyl_Groups       | float64 | numeric_predictor     | 14            | 1.2456             | 1110              | 16                     |
| RDKit_Aromatic_Rings        | float64 | numeric_predictor     | 0             | 0.0                | 1124              | 9                      |
| RDKit_HBond_Acceptors       | float64 | numeric_predictor     | 0             | 0.0                | 1124              | 21                     |
| RDKit_HBond_Donors          | float64 | numeric_predictor     | 0             | 0.0                | 1124              | 16                     |
| RDKit_Heavy_Atom_Count      | float64 | numeric_predictor     | 0             | 0.0                | 1124              | 50                     |
| RDKit_LogP                  | float64 | numeric_predictor     | 0             | 0.0                | 1124              | 182                    |
| RDKit_Molecular_Weight      | float64 | numeric_predictor     | 0             | 0.0                | 1124              | 168                    |
| RDKit_Rotatable_Bonds       | float64 | numeric_predictor     | 0             | 0.0                | 1124              | 21                     |
| RDKit_TPSA                  | float64 | numeric_predictor     | 0             | 0.0                | 1124              | 122                    |
| Food_Water_Ratio            | str     | other                 | 803           | 71.4413            | 321               | 18                     |
| Retention_Final             | float64 | target                | 0             | 0.0                | 1124              | 835                    |
