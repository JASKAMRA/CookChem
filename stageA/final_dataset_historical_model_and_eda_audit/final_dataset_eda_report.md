# Final dataset EDA audit

## Audit finding
- Earlier EDA/diagnostic artifacts exist for historical and 439-row recovery datasets (`diagnostics_v0_1`, `recovery_v0_9`, and `final_prototype`). Batch 021 contains coverage and post-1,000 model-evaluation outputs, but no comprehensive final-1,016 EDA script/report with the requested distribution, missingness, source, food, descriptor and visual analyses was found. This package supplies that missing final-dataset EDA.

## Dataset structure
- Rows: 1016. Compound labels: 51. Canonical molecular IDs: 48. DOI families: 32. Food matrices: 66. Normalized cooking methods: 41.
- Exact duplicate experiment keys: 0.
- Largest DOI family contributes 84 rows (8.27%); top three contribute 246 (24.21%).

## Target
- `Retention_Final` is absent from this final dataset. It is therefore not silently recreated or analysed as a final target. The separate `historical_retention_final_distribution.csv` and plot are historical-only context.
- `target_value_percent` is the retained apparent concentration-ratio target. Mean 156.66, median 88.38, SD 419.05, range 0.00–6536.36.
- Values above 100: 346; zero: 2; negative: 0; IQR outliers: 97. Values above 100 represent a reported concentration increase, not automatically a total-mass-retention increase.

## Coverage and missingness
- Compounds with exactly one observation: 0; at least 2: 51; at least 5: 33; at least 10: 29; at least 20: 15.
- All eight molecular descriptor columns are finite for 1016/1016 rows. The master does not carry canonical SMILES, so this audit confirms descriptor completeness rather than independently revalidating chemical structures.
- The principal experimental-field gaps are temperature (578) and cooking time (206).

## Interpretation limits
- Plots and correlations are descriptive. They do not establish causal effects of cooking method, food, source, or molecular properties.
- The dataset retains source and measurement-basis heterogeneity. EDA demonstrates composition and imbalance, not that any one factor explains held-out performance.
