# Batch 100 — contextual reconciliation for the final 10 targets

## Outcome

Completed a second pass focused on locating quantitative plant-material/context values for all ten gaps. Eight targets now have some quantitative contextual lead: six in medicinal *Scutellaria* roots, amentoflavone in *Viburnum* vegetative tissues, and irilone in a secondary red-clover leaf table. The irilone primary numeric row/statistics remain unverified. No record was added to the ordinary-food tables, so official coverage correctly remains 109/119 (511 records and mappings; validation PASS). Exact quantitative values were not established for 7-methoxyflavanone or the exact pentamethoxyflavone.

## Contextual values captured

- *Scutellaria baicalensis* 1-year-old dry medicinal roots (HPLC table): baicalein 2.691, baicalin 124.371, scutellarein 0.017, wogonin 0.642, and wogonoside 22.037 mg/g. The table presents ± values; their statistical interpretation was not verified here. These are medicinal raw-material concentrations, not ordinary-food measurements.
- *S. baicalensis* experimental dry root control (HPLC, mean ± SD, n=6): oroxylin A 2.96 ± 0.04 mg/g dry matter. This is a medicinal plant experiment, not an edible-food composition sample.
- *Viburnum lantana* leaves: amentoflavone 0.1104 ± 0.0006%; branches 0.0061 ± 0.0005%. *V. opulus* leaves: 0.0066 ± 0.0002%. The full paper states samples were dried and powdered before extraction and Table 3 reports mean ± SD from n=3 analytical measurements. These values are thus on the dried plant-powder basis; a single collection site/specimen set is not a market-sample series. The paper reports the fruits as not possessing amentoflavone; that qualitative non-detection is not entered as numeric zero.
- Red-clover leaves: a secondary monograph reproduces irilone 0.06 mg/g dry weight and attributes it to Tsao et al. (2006). The primary paper confirms cultivar/plant-part HPLC profiling and irilone occurrence, but the secondary numeric row and statistics were not independently confirmed; retain only as a provisional context lead.

## Remaining two without exact numeric values

- 7-Methoxyflavanone (PubChem CID 2825024): no exact-identity, matrix-specific quantitative value found. Similar hydroxy/methoxyflavanones were excluded as different compounds.
- 5,4′-Dihydroxy-3,6,7,8,3′-pentamethoxyflavone (PubChem CID 100625): occurrence catalogs associate it with citrus, but the located citrus papers quantified other PMFs or aggregate PMFs; no numeric concentration for this exact analyte was verified.

## Scope and release decision

Phase 1B final-target screening is complete. These contextual leads do not satisfy the current ordinary-food eligibility rule and are held in this batch only. No medicinal, supplement, or plant-tissue concentration was copied into `food_composition.csv` or counted as a food mapping. Official verified food coverage remains 109/119, with 10 documented gaps. Closing the remaining two numeric leads requires new exact-analyte quantitative evidence; reaching 119/119 verified food coverage is not supported by the sources found in this pass.

## Sources

- Gao et al. (2020), *S. baicalensis* root flavonoids by HPLC, Table 1: https://pmc.ncbi.nlm.nih.gov/articles/PMC7604031/
- S. baicalensis NaCl experiment, HPLC root contents, Table 1: https://pmc.ncbi.nlm.nih.gov/articles/PMC11673518/
- Altun et al. (2007), HPLC analysis of amentoflavone in *Viburnum*, pp. 161–169: https://dergipark.org.tr/en/download/article-file/424419
- Tsao et al. (2006), red-clover cultivar/plant-part profiling: https://doi.org/10.1021/jf0614589
- Secondary red-clover monograph containing 0.06 mg/g irilone: https://www.pharmaguri.co.il/_Uploads/dbsAttachedFiles/AHPTrifoliumMonograph.pdf
- Citrus PMF quantification source, where PMF mix/other analytes do not establish the exact Stage B target: https://www.spkx.net.cn/CN/10.7506/spkx1002-6630-20181006-026
