# Stage A Literature Review

## Evidence inventory and traceability

The repository supplied `literature/week 1.pdf`, a Week 1 team review of **six** papers, not eight. No separate eight-paper review was found in the repository or provided attachments. This report therefore records the six supplied entries as review-level evidence (their bibliographic details were not all present in the PDF) and distinguishes them from the additional original methodological papers below. No missing author, year, DOI, dataset size, or performance result has been fabricated.

| Supplied review entry | Evidence stated in the Week 1 PDF | Relevance to CookRisk |
|---|---|---|
| Palermo, Pellegrini & Fogliano (2014) | Cooking effects can reflect degradation and extractability; food matrix, compound, method and conditions matter. | Supports molecular + food + process predictors and retaining apparent increases. |
| Murador et al. (2018) | Method effects on polyphenols and antioxidant activity need not align. | Supports retaining a compound-retention target rather than substituting antioxidant activity. |
| Miglio et al. (2008) | Vegetable responses vary within the same method; no universally superior method. | Supports interactions and subgroup diagnostics. |
| Kourouma et al. (2019) | Method, duration and compound identity jointly affect retention. | Supports time and molecular descriptor features. |
| Rothwell et al. (2015) | Literature retention varies by food, compounds and processing; values >100% are not automatically errors. | Supports source-aware validation and no automatic outlier deletion. |
| Fratianni et al. (2021) | Apparent concentration increases may reflect solids/weight change rather than compound formation. | Supports the Phase 3 extreme-value sensitivity analysis. |

## Additional literature used for Stage A model selection

* Chen, T. & Guestrin, C. (2016), *XGBoost: A Scalable Tree Boosting System*, KDD, DOI: 10.1145/2939672.2939785. This original paper describes regularised gradient-tree boosting and sparsity-aware learning. It motivated one controlled XGBoost comparison, not an assumption that it would win.
* Prokhorenkova, L. et al. (2018), *CatBoost: unbiased boosting with categorical features*, NeurIPS 31. The paper describes ordered boosting and categorical-feature processing designed to address prediction shift. CatBoost was considered but not benchmarked because no compatible package was installed in the isolated execution environment; Stage A did not substitute an unverified implementation.
* Ke, G. et al. (2017), *LightGBM: A Highly Efficient Gradient Boosting Decision Tree*, NeurIPS 30. LightGBM was considered for histogram boosting and sparse one-hot features, but was not benchmarked because its package was unavailable; its large-data efficiency motivation is less decisive for 1,124 records.

## Synthesis

The supplied literature supports heterogeneous, nonlinear relationships among molecular identity, food context and cooking conditions, and warns against removing apparent increases. The methodological literature justifies a compact comparison of a regularised gradient-boosted tree (XGBoost), a nonlinear kernel method (RBF-SVR), and a randomised-tree comparator (Random Forest). It does **not** justify replacing molecular-grouped validation, removing rare high-retention observations, or expecting any model to outperform Extra Trees a priori.
