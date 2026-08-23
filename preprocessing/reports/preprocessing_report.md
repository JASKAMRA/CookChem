# CookChem Preprocessing Report

Generated: 2026-08-23 09:50:39 UTC

## Input

- Source file: `data\raw\CookChem_Dataset_Molecular_Data_Filled.xlsx`
- Raw rows: 823
- Raw columns: 41

The raw file was read only. It was not overwritten or modified.

## Retention Summary

- Minimum retention: 4.0
- Median retention: 80.5
- Mean retention: 95.0419
- Maximum retention: 3650.0
- Records with retention >100%: 140
- Records with retention >200%: 38
- Records with retention >500%: 6

Retention values greater than 100% were flagged for review, not removed.

## Duplicate Review

0 records were flagged for duplicate review.

## Top Missingness

| column | missing_count | missing_percent | dtype |
| --- | --- | --- | --- |
| Pressure_kPa | 809 | 98.3 | float64 |
| Microwave_Power_W | 750 | 91.13 | float64 |
| Food_Water_Ratio | 745 | 90.52 | str |
| Oil_Type | 705 | 85.66 | str |
| Sample_Weight_g | 316 | 38.4 | float64 |
| Temperature_C | 293 | 35.6 | float64 |
| PubChem_CID | 251 | 30.5 | float64 |
| Cooking_Time_min | 114 | 13.85 | float64 |
| Replicates_n | 113 | 13.73 | float64 |
| Retention_Calculation_Delta | 107 | 13.0 | object |
| Calculated_Retention_Percent | 107 | 13.0 | object |
| Assay_Method | 79 | 9.6 | str |
| Country | 73 | 8.87 | str |
| Initial_Concentration | 68 | 8.26 | float64 |
| Final_Concentration | 63 | 7.65 | float64 |

## Validation Flag Summary

| flag | count | percent |
| --- | --- | --- |
| Flag_PubChem_CID_Missing | 251 | 30.5 |
| Flag_Missing_Required_Field | 142 | 17.25 |
| Flag_Retention_GT_100 | 140 | 17.01 |
| Flag_Retention_Calculation_Not_Checkable | 107 | 13.0 |
| Flag_Assay_Method_Missing | 79 | 9.6 |
| Flag_Retention_GT_200 | 38 | 4.62 |
| Flag_Initial_Final_Unit_Mismatch | 34 | 4.13 |
| Flag_Retention_GT_500 | 6 | 0.73 |
| Flag_SMILES_Missing | 4 | 0.49 |
| Flag_Molecular_Descriptor_Incomplete | 4 | 0.49 |
| Flag_Retention_Negative | 0 | 0.0 |
| Flag_Degradation_Retention_Sum_Check | 0 | 0.0 |
| Flag_Retention_Calculation_Mismatch | 0 | 0.0 |
| Flag_Encoding_Suspect | 0 | 0.0 |
| Flag_Potential_Duplicate_Key | 0 | 0.0 |

## Scientific Handling Rules Applied

- Source-reported columns were preserved.
- Standardized values were added in new columns.
- Missing values were not invented.
- Retention >100% was not treated as an automatic error.
- Raw data was not overwritten.
- Molecular descriptors were not regenerated.
- No external paper or PubChem lookup was performed.
