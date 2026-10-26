# CookRisk Phase 2 Starting Report

- Generated from Phase 1 artifacts on 2026-08-30 20:32:43
- Baseline root: `C:\Users\kamra\Desktop\BTP\CookChem\data\ml\baseline`
- Baseline report: `C:\Users\kamra\Desktop\BTP\CookChem\data\ml\baseline\baseline_report.md`

## Phase 1 benchmark

- Best model: `hist_gradient_boosting`
- Best features: `molecular_plus_process`
- Best target: `log1p`
- MAE: 40.995285
- RMSE: 129.015456
- R2: 0.311207

## Phase 1 models tested

| model                  | feature_group          | target_representation | mae_mean           | rmse_mean          | r2_mean             |
| ---------------------- | ---------------------- | --------------------- | ------------------ | ------------------ | ------------------- |
| hist_gradient_boosting | molecular_plus_process | log1p                 | 40.995284952387095 | 129.01545556092358 | 0.3112074140061137  |
| hist_gradient_boosting | molecular_plus_process | raw                   | 50.26587585881828  | 132.38067163033503 | 0.2670222418539397  |
| hist_gradient_boosting | process_only           | log1p                 | 40.34792499069575  | 133.0086386341776  | 0.243212009003456   |
| hist_gradient_boosting | process_only           | raw                   | 50.97635299437089  | 135.9686124092971  | 0.2261700025498931  |
| ridge                  | process_only           | log1p                 | 42.77918650483262  | 137.81255634277127 | 0.1761067616921469  |
| dummy                  | molecular_only         | raw                   | 50.71075003534811  | 151.7317891115137  | -0.0039438050154422 |
| dummy                  | molecular_plus_process | raw                   | 50.71075003534811  | 151.7317891115137  | -0.0039438050154422 |
| dummy                  | process_only           | raw                   | 50.71075003534811  | 151.7317891115137  | -0.0039438050154422 |
| ridge                  | molecular_only         | raw                   | 53.639198423000366 | 152.27845806980656 | -0.0245661189453491 |
| hist_gradient_boosting | molecular_only         | log1p                 | 47.23269532037764  | 152.48846893952472 | -0.0260203802892241 |
| ridge                  | molecular_only         | log1p                 | 46.85173470359858  | 152.99455263209046 | -0.0321519444077686 |
| dummy                  | molecular_only         | log1p                 | 46.525770884377536 | 154.1884470474983  | -0.0498924156323126 |
| dummy                  | molecular_plus_process | log1p                 | 46.525770884377536 | 154.1884470474983  | -0.0498924156323126 |
| dummy                  | process_only           | log1p                 | 46.525770884377536 | 154.1884470474983  | -0.0498924156323126 |
| hist_gradient_boosting | molecular_only         | raw                   | 56.24424862995918  | 156.2815606354009  | -0.0912645855888441 |
| ridge                  | molecular_plus_process | log1p                 | 74.95987238434822  | 380.3724961422269  | -53.6377510640245   |
| ridge                  | molecular_plus_process | raw                   | 361.3570513850394  | 4641.872389826631  | -16277.865091930758 |
| ridge                  | process_only           | raw                   | 415.1253708211392  | 5459.949021757546  | -22687.124784711727 |

## Current predictor set entering Phase 2

- `molecular_plus_process` predictor columns:
- Temperature_C, Cooking_Time_min, Pressure_kPa, Microwave_Power_W, Sample_Weight_g, Initial_Concentration, Replicates_n, Assay_Method_Standardized, Compound_Class_Standardized, Cooking_Medium_Standardized, Cooking_Method_Standardized, Food_Name_Standardized, Initial_Unit_Standardized, Oil_Type_Standardized, RDKit_Molecular_Weight, RDKit_LogP, RDKit_TPSA, RDKit_HBond_Donors, RDKit_HBond_Acceptors, RDKit_Rotatable_Bonds, RDKit_Aromatic_Rings, RDKit_Hydroxyl_Groups, RDKit_Heavy_Atom_Count

## Current missingness

| column                      | missing_count | missing_percentage | unique_non_null_values |
| --------------------------- | ------------- | ------------------ | ---------------------- |
| Pressure_kPa                | 1114          | 99.1103            | 3                      |
| Microwave_Power_W           | 1056          | 93.9502            | 7                      |
| Oil_Type_Standardized       | 942           | 83.8078            | 10                     |
| Temperature_C               | 403           | 35.8541            | 30                     |
| Sample_Weight_g             | 248           | 22.0641            | 9                      |
| Cooking_Time_min            | 229           | 20.3737            | 43                     |
| Replicates_n                | 200           | 17.7936            | 4                      |
| Initial_Concentration       | 54            | 4.8043             | 359                    |
| Initial_Unit_Standardized   | 46            | 4.0925             | 15                     |
| Assay_Method_Standardized   | 44            | 3.9146             | 35                     |
| Cooking_Medium_Standardized | 39            | 3.4698             | 30                     |
| RDKit_Hydroxyl_Groups       | 14            | 1.2456             | 16                     |
| Compound_Class_Standardized | 0             | 0.0                | 51                     |
| Cooking_Method_Standardized | 0             | 0.0                | 37                     |
| Food_Name_Standardized      | 0             | 0.0                | 158                    |
| RDKit_Aromatic_Rings        | 0             | 0.0                | 9                      |
| RDKit_HBond_Acceptors       | 0             | 0.0                | 21                     |
| RDKit_HBond_Donors          | 0             | 0.0                | 16                     |
| RDKit_Heavy_Atom_Count      | 0             | 0.0                | 50                     |
| RDKit_LogP                  | 0             | 0.0                | 182                    |
| RDKit_Molecular_Weight      | 0             | 0.0                | 168                    |
| RDKit_Rotatable_Bonds       | 0             | 0.0                | 21                     |
| RDKit_TPSA                  | 0             | 0.0                | 122                    |

## Current limitations carried forward from Phase 1

- Sparse predictors remain unresolved: Pressure_kPa, Microwave_Power_W, Oil_Type_Standardized.
- Food_Name_Standardized remains high-cardinality at 158 observed categories.
- Descriptor redundancy is plausible and must be tested under grouped CV rather than assumed from correlation tables alone.
- The benchmark favors log1p target modeling, but Phase 2 should still compare raw versus log1p when the feature recipe stabilizes.
