# CookRisk Exploratory Data Analysis

## 1. Dataset Overview

| input_path | observations | columns | unique_compounds | unique_foods | unique_cooking_methods | unique_cooking_media | unique_assay_methods | target_column | numerical_feature_count | categorical_feature_count | generated_at_utc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| data\preprocessing\final\cookchem_molecular_retention_preprocessed.csv | 1124 | 47 | 197 | 158 | 37 | 30 | 35 | Retention_Final | 21 | 26 | 2026-08-25T19:09:27.726035+00:00 |

## 2. Data Quality

- The input dataset was read only from `data/preprocessing/final/cookchem_molecular_retention_preprocessed.csv`.
- No imputation, filtering, scaling, encoding, or model training was performed.

## 3. Missingness

| column | dtype | non_null_values | missing_values | missing_percentage | unique_values |
| --- | --- | --- | --- | --- | --- |
| Pressure_kPa | float64 | 10 | 1114 | 99.1103 | 3 |
| Microwave_Power_W | float64 | 68 | 1056 | 93.9502 | 7 |
| Oil_Type_Standardized | str | 182 | 942 | 83.8078 | 10 |
| Food_Water_Ratio | str | 321 | 803 | 71.4413 | 18 |
| PubChem_CID_Resolved | float64 | 557 | 567 | 50.4448 | 112 |
| Temperature_C | float64 | 721 | 403 | 35.8541 | 30 |
| Sample_Weight_g | float64 | 876 | 248 | 22.0641 | 9 |
| Cooking_Time_min | float64 | 895 | 229 | 20.3737 | 43 |
| Replicates_n | float64 | 924 | 200 | 17.7936 | 4 |
| PubChem_CID | float64 | 1047 | 77 | 6.8505 | 196 |
| Initial_Concentration | float64 | 1070 | 54 | 4.8043 | 359 |
| Initial_Unit | str | 1078 | 46 | 4.0925 | 16 |
| Initial_Unit_Standardized | str | 1078 | 46 | 4.0925 | 15 |
| Assay_Method_Standardized | str | 1080 | 44 | 3.9146 | 35 |
| Country | str | 1084 | 40 | 3.5587 | 30 |

## 4. Retention Distribution

| count | mean | median | std | min | max | skewness | kurtosis | P1 | P5 | P10 | P25 | P75 | P90 | P95 | P99 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1124 | 96.40236734690035 | 78.0 | 163.89625531291318 | 1.46434635 | 3650.0 | 13.86892347930299 | 250.51309502430692 | 6.35289752316 | 15.1323359785 | 31.423348068000003 | 56.8 | 94.404910715 | 141.11800000000002 | 192.81143633499997 | 525.2816789579997 |

## 5. Apparent Increase (>100%) Analysis

| group | apparent_increase | count | percentage | mean_retention | median_retention | min_retention | max_retention |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Retention <= 100 | 0 | 935 | 83.18505338078292 | 66.2118341136 | 72.15537986 | 1.46434635 | 100.0 |
| Retention > 100 | 1 | 189 | 16.814946619217082 | 245.7576508026455 | 155.4529915 | 100.3781368 | 3650.0 |

## 6. Extreme Retention Values

| Record_ID | Compound_Name | Canonical_Molecular_ID | Food_Name | Cooking_Method_Standardized | Temperature_C | Cooking_Time_min | Retention_Final | Apparent_Increase |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R754 | Alpha-tocopherol (Vitamin E) | MOL-E735D9075DA5F7EA | Onion | Frying |  |  | 3650.0 | 1 |
| EXP931 | Ferulic acid | MOL-25F8CD05AD250A06 | Broccoli | Microwaving |  |  | 2247.619048 | 1 |
| EXP951 | Kaempferol | MOL-3811F42D3C15ED32 | Broccoli | Microwaving |  |  | 2226.086957 | 1 |
| EXP921 | Syringic acid | MOL-EEA321586E21AFFF | Broccoli | Microwaving |  |  | 1035.0 | 1 |
| EXP926 | p-Coumaric acid | MOL-0D386D6E093BCAC9 | Broccoli | Microwaving |  |  | 966.6666667 | 1 |
| EXP916 | Caffeic acid | MOL-25F875E0BC8D5FF1 | Broccoli | Microwaving |  |  | 851.8072289 | 1 |
| R753 | Alpha-tocopherol (Vitamin E) | MOL-E735D9075DA5F7EA | Onion | Stir-frying |  |  | 850.0 | 1 |
| R6-019 | Hyperoside | MOL-ED743FD15F645421 | Common Bean - Volturara | Boiling |  |  | 821.0962145 | 1 |
| R_ROUND5_040 | Stigmasterol | MOL-9D2BAF33FD7B681F | Cheddar Cauliflower | Boiling |  | 25.0 | 745.4545455 | 1 |
| EXP941 | Quercetin | MOL-FDB10E6B0C4171D1 | Broccoli | Microwaving |  |  | 698.5074627 | 1 |
| R6-023 | Taxifolin | MOL-2EDC7AF9A9DB2D85 | Common Bean - Cannellino Rosso | Boiling |  |  | 566.0483871 | 1 |
| R134 | Beta-carotene | MOL-4211365770E800E7 | Unripe hot pepper | Deep-frying |  |  | 529.16 | 1 |
| R4_04_03 | Acetyldaidzin | CID:156155 | Soybean | Dry-Heating | 100.0 | 90.0 | 512.2977346 | 1 |
| R_ROUND5_032 | Campesterol | MOL-B0407F74EE4A3526 | Cheddar Cauliflower | Boiling |  | 25.0 | 512.037037 | 1 |
| R_ROUND5_048 | Beta-Sitosterol | MOL-6243166476332BE3 | Cheddar Cauliflower | Boiling |  | 25.0 | 505.2136752 | 1 |
| R746 | Alpha-tocopherol (Vitamin E) | MOL-E735D9075DA5F7EA | Crown daisy | Deep-frying |  |  | 493.01 | 1 |
| EXP946 | Cinnamic acid | MOL-AD185038A3D0E63D | Broccoli | Microwaving |  |  | 487.5 | 1 |
| R757 | Alpha-tocopherol (Vitamin E) | MOL-E735D9075DA5F7EA | Unripe hot pepper | Deep-frying |  |  | 446.24 | 1 |
| EXP906 | 3,4-Dihydroxybenzoic acid | MOL-C208ADB38D658E40 | Broccoli | Microwaving |  |  | 435.9195402 | 1 |
| R4_04_04 | Acetyldaidzin | CID:156155 | Soybean | Dry-Heating | 100.0 | 120.0 | 395.7928803 | 1 |

## 7. Compound Frequency and Repetition

| min_observations_per_compound | max_observations_per_compound | mean_observations_per_compound | median_observations_per_compound | P10 | P25 | P75 | P90 | P95 | compounds_with_1_observation | compounds_with_le_2_observations | compounds_with_le_5_observations | compounds_with_ge_10_observations | compounds_with_ge_20_observations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 102 | 5.7055837563451774 | 4.0 | 1.0 | 1.0 | 6.0 | 10.400000000000006 | 16.599999999999966 | 83 | 89 | 146 | 32 | 9 |

| metric | value |
| --- | --- |
| total_observations | 1124.0 |
| unique_compounds | 197.0 |
| observations_from_n_eq_1 | 83.0 |
| observations_from_n_le_2 | 95.0 |
| observations_from_n_le_5 | 347.0 |
| observations_from_n_ge_10 | 640.0 |
| observations_from_n_ge_20 | 355.0 |
| percent_observations_top_5_compounds | 22.77580071174377 |
| percent_observations_top_10_compounds | 33.27402135231316 |
| percent_observations_top_20_compounds | 46.263345195729535 |

## 8. Compound Classes

| Compound_Class_Standardized | observation_count | unique_compounds | mean_retention | median_retention | std_retention |
| --- | --- | --- | --- | --- | --- |
| Vitamin | 162 | 13 | 108.97586419753087 | 74.3 | 292.19252891474883 |
| Phenolic Acid | 150 | 16 | 118.38423883618002 | 81.91091954000001 | 221.74523900724503 |
| Carotenoid | 127 | 21 | 93.73118110236221 | 86.2 | 52.00966348874958 |
| Flavonoid | 111 | 29 | 116.64969219115315 | 77.2 | 233.11084975556415 |
| Anthocyanin | 72 | 13 | 51.01687073431944 | 58.25 | 25.71152676218845 |
| Glucosinolate | 69 | 12 | 53.30558909726087 | 66.83172402 | 30.12356445395685 |
| Amino acid | 68 | 17 | 92.23906342205883 | 92.96614227 | 5.637912045886905 |
| Phytosterol | 48 | 3 | 181.51939800979167 | 162.6851852 | 137.12965821778263 |
| Isoflavone | 39 | 8 | 132.50722817794872 | 84.6 | 115.76677163146307 |
| Diarylheptanoid (curcuminoid) | 38 | 3 | 109.08105263157894 | 107.11 | 48.29538144721802 |
| Phenolic | 32 | 3 | 55.455625 | 57.43 | 20.04217310629216 |
| Polyphenol | 29 | 11 | 58.862758620689654 | 64.0 | 21.292160679553888 |
| Alkaloid | 15 | 4 | 80.82 | 89.3 | 20.66339759090939 |
| Phenolic compound | 11 | 2 | 35.736274309 | 25.60846561 | 27.92767581679344 |
| Terpene | 11 | 11 | 77.43636363636364 | 76.0 | 10.128995283568132 |

## 9. Cooking Methods

| Cooking_Method_Standardized | observation_count | unique_compounds | mean_retention | median_retention | std_retention | percentage_gt_100 |
| --- | --- | --- | --- | --- | --- | --- |
| Boiling | 319 | 127 | 85.96988200176489 | 78.28663643 | 82.57762669402807 | 18.808777429467085 |
| Steaming | 215 | 110 | 90.8897032184186 | 85.1 | 38.33820991031512 | 13.023255813953488 |
| Microwaving | 125 | 72 | 154.173453401968 | 88.69 | 309.03831626192795 | 19.2 |
| Frying | 76 | 41 | 129.15025353676316 | 76.505 | 412.36380903084546 | 18.421052631578945 |
| Stir-frying | 76 | 57 | 82.11918636332895 | 74.6 | 92.68717072848003 | 5.263157894736842 |
| Baking | 59 | 31 | 64.23237288135593 | 58.69 | 28.454440435180793 | 8.47457627118644 |
| Sous-vide | 39 | 24 | 86.86182850589744 | 56.5 | 74.47136484267453 | 25.64102564102564 |
| Roasting | 29 | 22 | 54.62413793103448 | 45.5 | 32.27859280846334 | 13.793103448275861 |
| Air frying | 27 | 18 | 62.22555555555555 | 63.2 | 19.885938273705893 | 7.4074074074074066 |
| Pressure Cooking | 22 | 17 | 54.355895242772725 | 35.35 | 56.44180085735774 | 13.636363636363635 |
| Grilling | 17 | 17 | 61.22941176470589 | 58.5 | 9.579128659870529 | 0.0 |
| Wet-Heating | 16 | 4 | 116.355113631875 | 113.93014289 | 92.07370976329375 | 50.0 |
| Dry-Heating | 16 | 4 | 152.662505051875 | 82.73858193000001 | 146.18156378786674 | 50.0 |
| Pasteurization | 14 | 4 | 80.68571428571428 | 82.2 | 8.287790569715947 | 0.0 |
| Sautéing | 14 | 6 | 73.84642857142856 | 74.7 | 18.703494369992782 | 0.0 |

## 10. Temperature

| count | mean | median | std | min | max | skewness | kurtosis | P25 | P75 | missing_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 721 | 123.61442441054092 | 100.0 | 40.3748548326618 | 25.0 | 220.0 | 0.8568964945000616 | -0.6136816970191159 | 100.0 | 170.0 | 403 |

## 11. Cooking Time

| count | mean | median | std | min | max | skewness | kurtosis | P25 | P75 | missing_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 895 | 17.47163128491732 | 10.0 | 52.61966731472919 | 0.01 | 1440.0 | 22.598990626570274 | 600.7461072603976 | 5.0 | 16.0 | 229 |

## 12. Molecular Descriptors

| count | mean | median | std | min | max | skewness | kurtosis | P25 | P75 | descriptor | missing_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1124 | 358.7156708185053 | 354.311 | 180.89398067181486 | 71.079 | 1101.31 | 1.0131178308926496 | 2.1241051436674647 | 180.159 | 464.379 | RDKit_Molecular_Weight | 0 |
| 1124 | 2.3269896797153025 | 1.063 | 4.264254678114798 | -5.2252 | 22.4677 | 1.2017321743907068 | 0.5999250713486228 | -0.6459 | 3.3613 | RDKit_LogP | 0 |
| 1124 | 110.83431494661923 | 93.06 | 85.84959165915232 | 0.0 | 526.6 | 1.5427102967479467 | 4.301233644386759 | 57.53 | 166.11 | RDKit_TPSA | 0 |
| 1124 | 3.790035587188612 | 3.0 | 3.0185606305193806 | 0.0 | 17.0 | 1.3432583885390512 | 2.7239343694552725 | 2.0 | 5.0 | RDKit_HBond_Donors | 0 |
| 1124 | 5.970640569395018 | 5.0 | 5.04053304814383 | 0.0 | 30.0 | 1.6676848677741554 | 4.44945357409937 | 2.0 | 9.0 | RDKit_HBond_Acceptors | 0 |
| 1124 | 5.1886120996441285 | 4.0 | 3.8516587809647143 | 0.0 | 40.0 | 1.488601130266724 | 6.039034481606732 | 2.0 | 7.0 | RDKit_Rotatable_Bonds | 0 |
| 1124 | 1.24644128113879 | 1.0 | 1.3826091216218508 | 0.0 | 8.0 | 1.4212982378639663 | 3.589340928344444 | 0.0 | 2.0 | RDKit_Aromatic_Rings | 0 |
| 1110 | 3.4234234234234235 | 2.0 | 3.0879782301753624 | 0.0 | 17.0 | 1.4544086989153213 | 2.9023862311671373 | 1.0 | 5.0 | RDKit_Hydroxyl_Groups | 14 |
| 1124 | 25.487544483985765 | 25.0 | 13.034539554261517 | 5.0 | 78.0 | 0.9869915944380004 | 1.9480039079631153 | 13.0 | 33.0 | RDKit_Heavy_Atom_Count | 0 |

## 13. Descriptor-Retention Relationships

| descriptor | pearson_r | pearson_p_approx | pearson_n | spearman_r | spearman_p_approx | spearman_n | limitation_note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RDKit_LogP | 0.12823064438498707 | 1.5809227186133154e-05 | 1124 | 0.3125132190183562 | 2.6076116920918727e-27 | 1124 | Repeated observations of the same compound violate independence assumptions; correlations are exploratory only. |
| RDKit_TPSA | -0.10890622144697192 | 0.0002513845011335407 | 1124 | -0.3363894811850882 | 1.0187395720981264e-31 | 1124 | Repeated observations of the same compound violate independence assumptions; correlations are exploratory only. |
| RDKit_HBond_Donors | -0.10885867555536995 | 0.0002529699603383554 | 1124 | -0.3321674368714557 | 6.582254220997134e-31 | 1124 | Repeated observations of the same compound violate independence assumptions; correlations are exploratory only. |
| RDKit_HBond_Acceptors | -0.10017372705324376 | 0.0007647789021452011 | 1124 | -0.34456433519897023 | 2.5141128015838947e-33 | 1124 | Repeated observations of the same compound violate independence assumptions; correlations are exploratory only. |
| RDKit_Hydroxyl_Groups | -0.0991602870203319 | 0.0009326261640523036 | 1110 | -0.3195204159175248 | 3.1762963954434987e-28 | 1110 | Repeated observations of the same compound violate independence assumptions; correlations are exploratory only. |
| RDKit_Rotatable_Bonds | 0.04020661102256457 | 0.1780133320785269 | 1124 | 0.1411392738734801 | 1.9620900870129714e-06 | 1124 | Repeated observations of the same compound violate independence assumptions; correlations are exploratory only. |
| RDKit_Heavy_Atom_Count | 0.007317073440635457 | 0.8064643431491922 | 1124 | 0.031764229572979016 | 0.2873890414157575 | 1124 | Repeated observations of the same compound violate independence assumptions; correlations are exploratory only. |
| RDKit_Aromatic_Rings | -0.006152567880483655 | 0.8367918450516295 | 1124 | -0.11040905123734852 | 0.0002058113154819009 | 1124 | Repeated observations of the same compound violate independence assumptions; correlations are exploratory only. |
| RDKit_Molecular_Weight | -0.002261528160967022 | 0.9396425656640325 | 1124 | -0.0003206162061343527 | 0.9914351450440851 | 1124 | Repeated observations of the same compound violate independence assumptions; correlations are exploratory only. |

- Pearson and Spearman p-values are approximate Fisher-z two-sided values because `scipy` is unavailable in the runtime.
- Repeated observations of the same compound violate independence assumptions, so these correlations are exploratory only.

## 14. Numerical Feature Correlations

| feature_1 | feature_2 | n | pearson_r | spearman_r | max_abs_correlation | high_correlation_flag |
| --- | --- | --- | --- | --- | --- | --- |
| Temperature_C | Pressure_kPa | 10 | -0.9998016180994239 | -0.14433756729740646 | 0.9998016180994239 | True |
| RDKit_Molecular_Weight | RDKit_Heavy_Atom_Count | 1124 | 0.9945468833708982 | 0.9912662830128346 | 0.9945468833708982 | True |
| RDKit_TPSA | RDKit_HBond_Acceptors | 1124 | 0.979943112039185 | 0.9742833108509662 | 0.979943112039185 | True |
| RDKit_TPSA | RDKit_HBond_Donors | 1124 | 0.9623932579987167 | 0.9601586848859301 | 0.9623932579987167 | True |
| RDKit_HBond_Donors | RDKit_Hydroxyl_Groups | 1110 | 0.947253705478361 | 0.8868629921871963 | 0.947253705478361 | True |
| Cooking_Time_min | Pressure_kPa | 10 | 0.9412999717504951 | -0.14433756729740643 | 0.9412999717504951 | True |
| RDKit_HBond_Donors | RDKit_HBond_Acceptors | 1124 | 0.933951387133014 | 0.915371649566883 | 0.933951387133014 | True |
| RDKit_TPSA | RDKit_Hydroxyl_Groups | 1110 | 0.8842543362528483 | 0.8213644179206432 | 0.8842543362528483 | True |
| Pressure_kPa | Sample_Weight_g | 7 | -0.8689879856362772 | -0.16666666666666669 | 0.8689879856362772 | True |
| RDKit_HBond_Acceptors | RDKit_Hydroxyl_Groups | 1110 | 0.8666555865620211 | 0.7950589632690847 | 0.8666555865620211 | True |
| Pressure_kPa | RDKit_Aromatic_Rings | 10 | -0.16321430719762478 | -0.8553337321327791 | 0.8553337321327791 | True |
| Pressure_kPa | RDKit_Molecular_Weight | 10 | -0.21600590069758038 | -0.75955452531275 | 0.75955452531275 | False |
| RDKit_LogP | RDKit_TPSA | 1124 | -0.6052177820521459 | -0.7255654843877594 | 0.7255654843877594 | False |
| RDKit_Molecular_Weight | RDKit_Rotatable_Bonds | 1124 | 0.6341245935465295 | 0.7186773713655068 | 0.7186773713655068 | False |
| RDKit_Rotatable_Bonds | RDKit_Heavy_Atom_Count | 1124 | 0.6320466388106907 | 0.7050095963509968 | 0.7050095963509968 | False |
| RDKit_LogP | RDKit_HBond_Donors | 1124 | -0.5803573863824762 | -0.699216610787955 | 0.699216610787955 | False |
| RDKit_LogP | RDKit_HBond_Acceptors | 1124 | -0.5629106771622033 | -0.6917069848693466 | 0.6917069848693466 | False |
| RDKit_HBond_Acceptors | RDKit_Aromatic_Rings | 1124 | 0.667638960789748 | 0.5591826530966112 | 0.667638960789748 | False |
| RDKit_TPSA | RDKit_Aromatic_Rings | 1124 | 0.6652427335023536 | 0.5454678650846706 | 0.6652427335023536 | False |
| RDKit_HBond_Donors | RDKit_Aromatic_Rings | 1124 | 0.6399124773370182 | 0.5079057761793908 | 0.6399124773370182 | False |

## 15. Food Distribution

| Food_Name_Standardized | observation_count | unique_compounds |
| --- | --- | --- |
| Pumpkin leaves | 84 | 21 |
| Red cabbage | 65 | 8 |
| Coffee | 57 | 3 |
| Carrot | 55 | 8 |
| Turmeric | 46 | 3 |
| Soybean | 39 | 9 |
| Spinach | 39 | 9 |
| Onion | 36 | 7 |
| Broccoli | 35 | 11 |
| Barley | 31 | 1 |
| Tomato | 28 | 5 |
| Depurple Cauliflower | 24 | 3 |
| Cheddar Cauliflower | 24 | 3 |
| Blueberry | 17 | 3 |
| Avocado | 15 | 3 |
| Red Pepper | 15 | 2 |
| Potato | 14 | 5 |
| Sweet Potato | 14 | 2 |
| Artemide black rice | 14 | 2 |
| Chicory | 13 | 5 |

## 16. Missingness vs Retention

| variable | group | count | group_percent | mean_retention | median_retention | std_retention |
| --- | --- | --- | --- | --- | --- | --- |
| Pressure_kPa | Missing | 1114 | 99.11032028469751 | 96.81579972882943 | 78.09001485499999 | 164.55342073593863 |
| Pressure_kPa | Reported | 10 | 0.8896797153024912 | 50.346000000000004 | 45.07 | 27.851154055482553 |
| Microwave_Power_W | Missing | 1056 | 93.95017793594306 | 96.86977652944223 | 76.15076346000001 | 168.9994137121868 |
| Microwave_Power_W | Reported | 68 | 6.049822064056939 | 89.14377768860292 | 90.26431718 | 21.3524047487369 |
| Oil_Type_Standardized | Missing | 942 | 83.80782918149467 | 94.04053310692038 | 80.2 | 112.7493284921736 |
| Oil_Type_Standardized | Reported | 182 | 16.19217081850534 | 108.62680610547801 | 73.75 | 316.8489129954576 |
| Food_Water_Ratio | Missing | 803 | 71.44128113879003 | 97.36004772581569 | 78.0 | 167.3691489172804 |
| Food_Water_Ratio | Reported | 321 | 28.558718861209965 | 94.00667468562617 | 78.3 | 155.09530417113464 |

## 17. Important EDA Findings

- Repeated-compound imbalance: top 10 compounds contribute 33.3% of observations
- Sparse predictors: Pressure_kPa, Microwave_Power_W, Oil_Type_Standardized
- Apparent increases preserved: retention >100% observations remain in the dataset
- Descriptor-retention correlations are exploratory only because repeated compounds violate independence assumptions

## 18. Potential Problems

- High missingness in process-condition variables may make naive row-level comparisons misleading.
- Observation-level counts substantially exceed unique-compound counts, so many rows are repeated compounds rather than independent molecular identities.

## 19. Implications for ML

- Compound-level grouped validation will matter because repeated compounds dominate parts of the dataset.
- Apparent increases should remain in the response variable and be investigated scientifically, not capped mechanically.
- Descriptor-retention relationships should be re-evaluated later with grouped validation rather than ordinary row-level assumptions.

## 20. Recommended Next Steps

- Use this EDA as the read-only baseline for grouped validation design.
- Regenerate molecular-feature stage outputs against the current 1124-row preprocessing output before downstream modeling.
- Review high-missingness predictors and decide later whether each should be modeled, grouped, or left out in specific experiments.
