# Source verification report — preliminary, fail-closed

## Ledger result

- Historical supervised rows: **1124**
- `VERIFIED`: **117** — all are verified apparent concentration ratios, not total-mass retention.
- `DOI_MISMATCH`: **18**
- Other unresolved rows: **989**
- Stored targets matching a raw/final concentration calculation: **989**

## Primary-source evidence used

1. Zagórska et al. (2023), *Impact of Thermal Processing on the Composition of Curcuma longa Rhizome*, DOI `10.3390/foods12163086`, [primary full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC10453412/), Table 1. Phase 2 confirms the 33 linked records are concentration ratios and documents missing cooked yield.
2. Stryjecka et al. (2026), *Effects of Household Cooking Methods on the Nutritional, Phytochemical and Functional Properties of Cucurbita maxima Leaves*, DOI `10.3390/molecules31162740`, [PubMed record](https://pubmed.ncbi.nlm.nih.gov/42653823/), Tables 2–3. Phase 2 confirms the 84 linked records are dry-weight concentration ratios and documents missing cooked yield.

## Independently checked DOI mismatches

- `10.1016/j.lwt.2021.111500`: [publisher record](https://www.sciencedirect.com/science/article/pii/S0023643821006538) is fish oil-gelatin electrospun membranes, not avocado/Persin cooking.
- `10.1016/j.foodchem.2015.04.132`: [PubMed record](https://pubmed.ncbi.nlm.nih.gov/26041169/) is melamine determination in dairy products, not potato/antheraxanthin cooking.
- `10.1016/j.foodcont.2023.109800`: [publisher record](https://www.sciencedirect.com/science/article/abs/pii/S0956713523002001) is alpha-lactalbumin ELISA in hypoallergenic formula, not kimchi/capsaicin cooking.
- `10.1016/j.lwt.2022.113400`: [publisher record](https://www.sciencedirect.com/science/article/pii/S0023643822003358) is maize nixtamalization/acrylamide precursors, not black-pepper/piperine cooking.

## Limit

This is a machine-readable ledger for every supervised row, not a claim that every DOI has now been independently re-extracted. Rows without a primary-source table locator and reproducible transformation remain unresolved by design.
