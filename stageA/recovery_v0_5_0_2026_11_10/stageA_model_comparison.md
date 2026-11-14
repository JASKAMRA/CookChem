# v0.5 experimental model comparison

| model | validation | R² | MAE | RMSE |
|---|---|---:|---:|---:|
| dummy_median | compound_grouped_5fold | -0.0120 | 53.7168 | 185.0648 |
| dummy_median | leave_one_source_out | -0.0116 | 54.8795 | 185.0221 |
| ridge | compound_grouped_5fold | 0.3628 | 58.9136 | 146.8487 |
| ridge | leave_one_source_out | -0.1118 | 79.1345 | 193.9671 |
| random_forest | compound_grouped_5fold | 0.3847 | 41.3572 | 144.2958 |
| random_forest | leave_one_source_out | -0.0628 | 57.3620 | 189.6486 |
| extra_trees | compound_grouped_5fold | 0.3431 | 41.4367 | 149.1026 |
| extra_trees | leave_one_source_out | -0.0393 | 56.9408 | 187.5419 |
| gradient_boosting | compound_grouped_5fold | 0.2633 | 45.4678 | 157.8981 |
| gradient_boosting | leave_one_source_out | -0.0091 | 55.0108 | 184.7939 |
| svr_rbf | compound_grouped_5fold | 0.0021 | 47.6221 | 183.7696 |
| svr_rbf | leave_one_source_out | -0.0097 | 50.8882 | 184.8456 |

Source LOSO remains a stress test, not a claim of deployment-level unseen-source generalisation.
