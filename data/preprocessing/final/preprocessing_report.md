# CookRisk Preprocessing Report

## 1. Objective

Build a deterministic preprocessing pipeline for the reviewed molecular retention dataset without overwriting the reviewed source file or using stale legacy outputs.

## 2. Input Dataset

- Source file: `data\reviewed\cookchem_molecular_retention_master.csv`
- Input rows: 1128
- Input columns: 111
- Unique canonical molecular identities: 198

## 3. Dataset Dimensions

| Metric | Value |
| --- | --- |
| Rows | 1128 |
| Columns | 111 |
| Duplicate full rows | 0 |
| Duplicate Record_ID | 0 |
| Rows excluded from supervised output | 4 |
| Final output rows | 1124 |

## 4. Data Integrity Checks

| Check | Result |
| --- | --- |
| All rows molecularly eligible | PASS |
| Duplicate Record_ID | PASS |
| Duplicate full rows | PASS |
| Descriptor conflicts within Canonical_Molecular_ID | PASS |
| Scientific value integrity after preprocessing | PASS |

## 5. Molecular Identity Validation

- Unique `Canonical_Molecular_ID`: 198
- Minimum observations per compound: 1
- Maximum observations per compound: 102
- Mean observations per compound: 5.5567
- Median observations per compound: 4.0

| Canonical_Molecular_ID | Canonical_Compound_Name | observation_count |
| --- | --- | --- |
| MOL-CF1446AA0DE93D24 | Vitamin C | 102 |
| MOL-6213BC022378CC3A | Chlorogenic Acid | 51 |
| MOL-4211365770E800E7 | Beta-Carotene | 40 |
| MOL-3027440F3B4AE891 | Lutein | 31 |
| MOL-25F8CD05AD250A06 | Ferulic Acid | 27 |
| MOL-348EAB954862D4A9 | Cyanidin-3-Glucoside | 25 |
| MOL-0D386D6E093BCAC9 | P-Coumaric Acid | 22 |
| MOL-25F875E0BC8D5FF1 | Caffeic Acid | 22 |
| MOL-E735D9075DA5F7EA | Alpha-Tocopherol (Vitamin E) | 20 |
| MOL-16B10569D6F0625E | Curcumin | 19 |

## 6. Molecular Descriptor Validation

- Rows with complete RDKit descriptors: 1114
- Rows with incomplete RDKit descriptors: 14
- Unique compounds with incomplete RDKit descriptors: 2

| Canonical_Molecular_ID | Canonical_Compound_Name | rows_affected | missing_descriptor_columns |
| --- | --- | --- | --- |
| PUBCHEM_441674 | Cyanidin-3-O-rutinoside | 7 | RDKit_Hydroxyl_Groups |
| PUBCHEM_443654 | Peonidin-3-O-glucoside | 7 | RDKit_Hydroxyl_Groups |

## 7. Target Definition

- Target column: `Retention_Final`
- Target missing in reviewed input: 4
- Target missing in final supervised output: 0
- Rows with no valid reviewed target were preserved in `data/preprocessing/intermediate/excluded_from_target_model.csv`.

## 8. Apparent-Increase Handling

- `Apparent_Increase = 1` rows: 189
- Retention values above 100% were preserved unchanged.

## 9. Categorical Standardization

- Category mapping file: `data\preprocessing\intermediate\category_mappings.json`
- Only obvious formatting inconsistencies were standardized.

## 10. Unit Standardization

- Unit conversion log: `data\preprocessing\intermediate\unit_conversion_log.csv`
- Only unambiguous unit-label normalizations were applied.

## 11. Missing Data

- No imputation was performed.
- Optional predictor missingness was preserved as missing.
- Rows missing the reviewed target were excluded only from the supervised output.

| column | missing_count | missing_percent | non_missing_count | unique_count | dtype |
| --- | --- | --- | --- | --- | --- |
| Pressure_kPa | 1114 | 99.1103 | 10 | 3 | Float64 |
| Microwave_Power_W | 1056 | 93.9502 | 68 | 7 | Float64 |
| Oil_Type_Standardized | 942 | 83.8078 | 182 | 10 | string |
| Food_Water_Ratio | 803 | 71.4413 | 321 | 18 | str |
| PubChem_CID_Resolved | 567 | 50.4448 | 557 | 112 | Float64 |
| Temperature_C | 403 | 35.8541 | 721 | 30 | Float64 |
| Sample_Weight_g | 248 | 22.0641 | 876 | 9 | Float64 |
| Cooking_Time_min | 229 | 20.3737 | 895 | 43 | Float64 |
| Replicates_n | 200 | 17.7936 | 924 | 4 | Float64 |
| PubChem_CID | 77 | 6.8505 | 1047 | 196 | Float64 |
| Initial_Concentration | 54 | 4.8043 | 1070 | 359 | Float64 |
| Initial_Unit | 46 | 4.0925 | 1078 | 16 | str |
| Initial_Unit_Standardized | 46 | 4.0925 | 1078 | 15 | string |
| Assay_Method_Standardized | 44 | 3.9146 | 1080 | 35 | string |
| Country | 40 | 3.5587 | 1084 | 30 | str |

## 12. Numerical Validation

- Numeric parsing log rows: 1128
- Suspicious-value log rows: 333

## 13. Outlier Investigation

- Potential outliers were flagged and preserved rather than removed automatically.

| Record_ID | Canonical_Molecular_ID | Compound_Name | column | value | issue | decision |
| --- | --- | --- | --- | --- | --- | --- |
| R102 | MOL-EABE7B2CDF5CDDAD | Alpha-carotene | Retention_Final | 105.25 | apparent_increase_reviewed | preserved_reviewed_target |
| R109 | MOL-4211365770E800E7 | Beta-Carotene | Retention_Final | 107.9 | apparent_increase_reviewed | preserved_reviewed_target |
| R115 | MOL-4211365770E800E7 | Beta-carotene | Retention_Final | 140.0 | apparent_increase_reviewed | preserved_reviewed_target |
| R117 | MOL-4211365770E800E7 | Beta-carotene | Retention_Final | 178.22 | apparent_increase_reviewed | preserved_reviewed_target |
| R123 | MOL-4211365770E800E7 | Beta-carotene | Retention_Final | 192.12 | apparent_increase_reviewed | preserved_reviewed_target |
| R124 | MOL-4211365770E800E7 | Beta-carotene | Retention_Final | 174.2 | apparent_increase_reviewed | preserved_reviewed_target |
| R125 | MOL-4211365770E800E7 | Beta-carotene | Retention_Final | 174.2 | apparent_increase_reviewed | preserved_reviewed_target |
| R128 | MOL-4211365770E800E7 | Beta-carotene | Retention_Final | 128.3 | apparent_increase_reviewed | preserved_reviewed_target |
| R130 | MOL-4211365770E800E7 | Beta-carotene | Retention_Final | 212.37 | apparent_increase_reviewed | preserved_reviewed_target |
| R133 | MOL-4211365770E800E7 | Beta-carotene | Retention_Final | 160.9 | apparent_increase_reviewed | preserved_reviewed_target |
| R134 | MOL-4211365770E800E7 | Beta-carotene | Retention_Final | 529.16 | apparent_increase_reviewed | preserved_reviewed_target |
| R141 | MOL-603E2B29B718C431 | Capsanthin | Retention_Final | 101.4 | apparent_increase_reviewed | preserved_reviewed_target |
| R151 | MOL-3027440F3B4AE891 | Lutein | Retention_Final | 101.0 | apparent_increase_reviewed | preserved_reviewed_target |
| R161 | MOL-3027440F3B4AE891 | Lutein | Retention_Final | 100.5 | apparent_increase_reviewed | preserved_reviewed_target |
| R186 | MOL-DAA2C6ED52278E68 | Lycopene | Retention_Final | 101.4 | apparent_increase_reviewed | preserved_reviewed_target |

## 14. Feature Leakage Audit

| Column | Role | Included in X? | Reason |
| --- | --- | --- | --- |
| Data_Readiness_Status | audit | No | Audit, eligibility, or review field excluded from X. |
| Descriptor_Status | audit | No | Audit, eligibility, or review field excluded from X. |
| Duplicate_Review_Status | audit | No | Audit, eligibility, or review field excluded from X. |
| Duplicate_Status | audit | No | Audit, eligibility, or review field excluded from X. |
| Final_ML_Eligible_Reviewed | audit | No | Audit, eligibility, or review field excluded from X. |
| Final_ML_Status_Reviewed | audit | No | Audit, eligibility, or review field excluded from X. |
| Final_Preprocessing_Eligible | audit | No | Audit, eligibility, or review field excluded from X. |
| Final_Preprocessing_Status | audit | No | Audit, eligibility, or review field excluded from X. |
| Molecular_Descriptor_Consistency | audit | No | Audit, eligibility, or review field excluded from X. |
| Molecular_Descriptor_Status | audit | No | Audit, eligibility, or review field excluded from X. |
| Molecular_Feature_Eligible | audit | No | Audit, eligibility, or review field excluded from X. |
| Molecular_Identity_Status | audit | No | Audit, eligibility, or review field excluded from X. |
| Molecular_Model_Eligible | audit | No | Audit, eligibility, or review field excluded from X. |
| Paper_ID_DOI_Status | audit | No | Audit, eligibility, or review field excluded from X. |
| Review_Automatic_Acceptance | audit | No | Audit, eligibility, or review field excluded from X. |
| SMILES_Validation_Status | audit | No | Audit, eligibility, or review field excluded from X. |
| Source_Identity_Status | audit | No | Audit, eligibility, or review field excluded from X. |
| Source_Status | audit | No | Audit, eligibility, or review field excluded from X. |
| Source_Verification_Required | audit | No | Audit, eligibility, or review field excluded from X. |
| Unit_Compatibility_Status | audit | No | Audit, eligibility, or review field excluded from X. |
| Assay_Method_Standardized | categorical_predictor | Yes | Categorical predictor retained in X after standardization. |
| Compound_Class_Standardized | categorical_predictor | Yes | Categorical predictor retained in X after standardization. |
| Cooking_Medium_Standardized | categorical_predictor | Yes | Categorical predictor retained in X after standardization. |
| Cooking_Method_Standardized | categorical_predictor | Yes | Categorical predictor retained in X after standardization. |
| Food_Name_Standardized | categorical_predictor | Yes | Categorical predictor retained in X after standardization. |
| Initial_Unit_Standardized | categorical_predictor | Yes | Categorical predictor retained in X after standardization. |
| Molecular_Entity_Type_Standardized | categorical_predictor | No | Categorical predictor retained in X after standardization. |
| Oil_Type_Standardized | categorical_predictor | Yes | Categorical predictor retained in X after standardization. |
| Cooking_Time_min | cooking_predictor | Yes | Numeric cooking-condition predictor retained in X. |
| Initial_Concentration | cooking_predictor | Yes | Numeric cooking-condition predictor retained in X. |
| Microwave_Power_W | cooking_predictor | Yes | Numeric cooking-condition predictor retained in X. |
| Pressure_kPa | cooking_predictor | Yes | Numeric cooking-condition predictor retained in X. |
| Replicates_n | cooking_predictor | Yes | Numeric cooking-condition predictor retained in X. |
| Sample_Weight_g | cooking_predictor | Yes | Numeric cooking-condition predictor retained in X. |
| Temperature_C | cooking_predictor | Yes | Numeric cooking-condition predictor retained in X. |
| Apparent_Increase | derived_feature | No | Derived from reviewed retention target; kept for EDA and excluded from X. |
| Aromatic_Rings | excluded | No | Source descriptor reference excluded in favor of the RDKit descriptor set. |
| Assay_Method | excluded | No | Not retained in final dataset. |
| Canonical_Compound_Class | excluded | No | Not retained in final dataset. |
| Canonical_Cooking_Method | excluded | No | Not retained in final dataset. |

## 15. Constant/Duplicate Features

| Metric | Value |
| --- | --- |
| Constant features removed from X | Molecular_Entity_Type_Standardized |
| Duplicate feature pairs removed from X | None |
| Near-zero-variance features flagged | None |

## 16. Compound Frequency

| Canonical_Molecular_ID | Canonical_Compound_Name | observation_count |
| --- | --- | --- |
| MOL-CF1446AA0DE93D24 | Vitamin C | 102 |
| MOL-6213BC022378CC3A | Chlorogenic Acid | 51 |
| MOL-4211365770E800E7 | Beta-Carotene | 40 |
| MOL-3027440F3B4AE891 | Lutein | 31 |
| MOL-25F8CD05AD250A06 | Ferulic Acid | 27 |
| MOL-348EAB954862D4A9 | Cyanidin-3-Glucoside | 25 |
| MOL-0D386D6E093BCAC9 | P-Coumaric Acid | 22 |
| MOL-25F875E0BC8D5FF1 | Caffeic Acid | 22 |
| MOL-E735D9075DA5F7EA | Alpha-Tocopherol (Vitamin E) | 20 |
| MOL-16B10569D6F0625E | Curcumin | 19 |
| MOL-6243166476332BE3 | Beta-Sitosterol | 16 |
| MOL-7EE1F4B0FE7C2F8F | Rutins | 16 |
| MOL-9D2BAF33FD7B681F | Stigmasterol | 16 |
| MOL-A243F0B3B6C746C6 | Demethoxycurcumin | 16 |
| MOL-B0407F74EE4A3526 | Campesterol | 16 |

## 17. Transformations Applied

| Transformation | Count |
| --- | --- |
| Categorical standardization | 11 |
| Unit-label standardizations logged | 36 |
| Numeric parsing operations logged | 1128 |
| Derived columns | 1 |

## 18. Rows Excluded From ML

| Record_ID | Canonical_Molecular_ID | Compound_Name | Original_Target_State | Exclusion_Reason |
| --- | --- | --- | --- | --- |
| R214 | MOL-70C3BF5054D2B2B9 | Acrylamide | NOT_APPLICABLE_NEOFORMED_COMPOUND | No valid retention target because the compound is neoformed during cooking. |
| R215 | MOL-70C3BF5054D2B2B9 | Acrylamide | NOT_APPLICABLE_NEOFORMED_COMPOUND | No valid retention target because the compound is neoformed during cooking. |
| R395 | MOL-4F1A943C959BC640 | PhIP | NOT_APPLICABLE_NEOFORMED_COMPOUND | No valid retention target because the compound is neoformed during cooking. |
| R704 | MOL-70C3BF5054D2B2B9 | Acrylamide | NOT_APPLICABLE_NEOFORMED_COMPOUND | No valid retention target because the compound is neoformed during cooking. |

## 19. Final Dataset

- Final CSV: `data\preprocessing\final\cookchem_molecular_retention_preprocessed.csv`
- Final rows: 1124
- Final columns: 47
- Predictor columns retained in X: 23

## 20. Remaining Issues

- Four neoformed-compound observations have no meaningful retention target and remain excluded from the supervised output.
- RDKit descriptor missingness remains for 2 compounds; no imputation or recomputation was performed.
- Final concentration and retention helper columns remain excluded because they would leak the supervised target.

## 21. Recommendation for EDA

- Check missingness patterns across cooking-condition predictors and the compounds with incomplete RDKit hydroxyl-group values.
- Evaluate compound-level observation imbalance because a small subset of compounds contributes many repeated observations.
- Use `Canonical_Molecular_ID` as the grouping key for future unseen-compound validation splits.
