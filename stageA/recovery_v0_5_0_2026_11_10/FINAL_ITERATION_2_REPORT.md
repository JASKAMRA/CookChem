# Stage A recovery — Iteration 2

## Outcome

v0.5 adds one independently authored primary study and five auditable vitamin-C observations. The dataset now contains 379 observations from eight DOI families, 46 compound groups, 15 food matrices, and 15 normalized cooking methods. The addition is real source diversity, but narrow: one potato cultivar and one compound across five treatments.

## Admission and exclusions

- **Admitted:** Narwojsz et al. (2020), DOI `10.1007/s11130-020-00808-0`; Table 2 reports raw and cooked vitamin C in mg/100 g dry weight. The methods report boiling, two steaming configurations, microwaving, and grilling conditions. Five ratios were calculated directly from those pairs.
- **Excluded:** Managa et al. (2020), DOI `10.3389/fnut.2020.580550`; the raw/cooked phenolic table says mg/kg but does not specify fresh- or dry-weight basis, while the assay uses freeze-dried material.
- **Pending:** Lee et al. (2018), DOI `10.1007/s10068-017-0281-1`; publication identity is verified, but primary table/method access was not obtained. No search-snippet values were used.

## Validation decision

Random Forest has the lowest compound-grouped MAE among the standard experimental comparison (41.36 percentage points; R² 0.3847; RMSE 144.30). Extra Trees is close (MAE 41.44; R² 0.3431). Random Forest source-LOSO R² is -0.0628 and Extra Trees source-LOSO R² is -0.0393; neither supports a claim of unseen-source generalisation.

XGBoost 3.2.0 was available and evaluated with the same fold-safe feature pipeline: compound-grouped R² 0.2978, MAE 44.2117, RMSE 154.1576; source-LOSO R² -0.0275, MAE 55.6289, RMSE 186.4758. It was not selected.

The additional food-matrix grouped pooled R² is -0.0464. Cooking-method LOSO pooled R² is -0.0098; singleton held-out methods have undefined R² and must not be interpreted as positive evidence. The transformed feature `c__cooking_medium_Microwave` accounts for 0.6725 of full-fit Random Forest importance, confirming it is a dominant protocol/source proxy, not a causal finding.

**Status: RESEARCH PROTOTYPE / NOT VALIDATED FOR DEPLOYMENT.** The target remains apparent concentration ratio only. Stage C was neither modified nor authorized for integration.
