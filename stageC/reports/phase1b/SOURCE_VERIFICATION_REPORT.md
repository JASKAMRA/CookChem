# Source verification report

Accepted source databases in the active dataset: USDA Flavonoid Content of Selected Foods Release 3.3; USDA FoodData Central SR Legacy record 171890 / NDB 14209 accessed through the official API; and USDA Database on the Isoflavone Content of Selected Foods Release 2.1 separate table for other phytoestrogens. The USDA FNDDS 2017–2018 official analyte roster was used for scope screening only; no FNDDS food-code data were extracted.

The official FDC API confirms coffee caffeine at 40 mg/100g, nutrient ID 1057 / number 262, analytical derivation, eight data points, observed range 30–44 mg, and a one-cup mass of 237 g. Its description is brewed coffee prepared with tap water and its footnote says it includes fast-food and home-brewed coffee. The web data viewer could not extract the USDA downloadable ZIP, so the direct official USDA API record is the source used; no third-party mirror was used.

USDA isoflavone Release 2.1 documentation states the main daidzein/genistein/glycitein values combine free forms with glucosides converted to aglycone equivalents. Those rows were held. Separate positive source-table values for formononetin and biochanin A in raw alfalfa sprouts were ingested as the exact reported analytes; USDA did not report row-level N or method. USDA Flav3.3 tea rows cite unpublished source ref 272 (2002), low N=2 and unavailable underlying method. No primary study was independently retrieved for accepted aggregate database values.


## Batch 009 — 2026-11-02

- Five new quantitative records were verified against full primary-study tables and processed with the Stage C ingestion pipeline: 6-gingerol, 6-shogaol, xanthohumol, capsaicin, and piperine. Exact source locators and uncertainty flags are in `batches/batch_009_multimatrix_primary_food_composition/compound_screening.csv` and `new_primary_measurements.csv`.
- Nine records remain authoritative-database measurements from earlier batches; the five Batch 009 records are primary analytical measurements.
- Caffeine's FDC API record remains separately database-verified. The official SR Legacy April 2018 ZIP links were confirmed but not retrievable in this environment; no archive extraction was claimed.
- Garlic-paste sulfur measurements remain candidates because the study's raw control was prepared with added water and the source concentration denominator needs adjudication. Candidate rows are preserved in `CANDIDATES.csv`.
- Other held findings include the inconsistent broccoli I3C unit reports, licorice and cinnamon studies with inaccessible quantitative rows, and compounds with no eligible ordinary-food quantitative value located in this search pass.
