# v0.3 experimental model comparison

| model | validation | r2 | mae | rmse |
|---|---|---:|---:|---:|
| dummy_median | compound_grouped_5fold | -0.0128 | 58.1452 | 195.7094 |
| dummy_median | leave_one_source_out | -0.0145 | 60.2189 | 195.8693 |
| ridge | compound_grouped_5fold | 0.3853 | 59.3750 | 152.4694 |
| ridge | leave_one_source_out | -0.1005 | 81.0768 | 204.0052 |
| random_forest | compound_grouped_5fold | 0.2943 | 48.1166 | 163.3667 |
| random_forest | leave_one_source_out | -0.0512 | 62.1115 | 199.3835 |
| extra_trees | compound_grouped_5fold | 0.2848 | 49.6253 | 164.4583 |
| extra_trees | leave_one_source_out | -0.0326 | 59.5411 | 197.6105 |
| gradient_boosting | compound_grouped_5fold | -0.0813 | 58.8212 | 202.2208 |
| gradient_boosting | leave_one_source_out | -0.0140 | 60.2924 | 195.8246 |
| svr_rbf | compound_grouped_5fold | -0.0010 | 51.5135 | 194.5628 |
| svr_rbf | leave_one_source_out | -0.0184 | 57.7482 | 196.2499 |
| xgboost | compound_grouped_5fold | 0.1782 | 50.8855 | 176.2858 |
| xgboost | leave_one_source_out | -0.0367 | 60.4581 | 198.0013 |

Compound-group validation assesses unseen compounds only. Source LOSO is reported as a stress test, not a generalisation claim.
