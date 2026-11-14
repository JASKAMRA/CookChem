# v0.4 experimental model comparison

| model | validation | R² | MAE | RMSE |
|---|---|---:|---:|---:|
| dummy_median | compound_grouped_5fold | -0.0111 | 53.9672 | 186.1671 |
| dummy_median | leave_one_source_out | -0.0118 | 55.4510 | 186.2323 |
| ridge | compound_grouped_5fold | 0.4123 | 57.1244 | 141.9360 |
| ridge | leave_one_source_out | -0.1135 | 80.1558 | 195.3686 |
| random_forest | compound_grouped_5fold | 0.3172 | 44.2003 | 152.9941 |
| random_forest | leave_one_source_out | -0.0524 | 57.3258 | 189.9320 |
| extra_trees | compound_grouped_5fold | 0.3317 | 44.0411 | 151.3577 |
| extra_trees | leave_one_source_out | -0.0420 | 57.9199 | 188.9914 |
| gradient_boosting | compound_grouped_5fold | 0.1248 | 54.9119 | 173.2035 |
| gradient_boosting | leave_one_source_out | -0.0109 | 55.6311 | 186.1543 |
| svr_rbf | compound_grouped_5fold | 0.0128 | 47.9710 | 183.9578 |
| svr_rbf | leave_one_source_out | -0.0112 | 51.9691 | 186.1770 |

Source LOSO remains a stress test, not a claim of deployment-level unseen-source generalisation.
