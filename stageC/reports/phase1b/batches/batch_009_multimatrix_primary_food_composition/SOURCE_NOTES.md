# Batch 009 — Multi-matrix primary food composition

## Acquisitions

Five new records were submitted to the existing Stage C ingestion pipeline: 6-gingerol and 6-shogaol in fresh Japanese ginger rhizomes; xanthohumol in hop flowers; capsaicin in Habanero chili on a dry-weight basis; and piperine in retail black pepper. Values and source locators are preserved in `new_primary_measurements.csv`. The expanded cumulative pipeline input is `accepted_food_records.csv`.

Primary measurement studies: Koch et al., 2017, DOI 10.3390/ijms18020452 (Table 2); Rodríguez et al., 2019, DOI 10.3390/foods8100435 (Table 5); Pandey et al., 2026, DOI 10.3389/fpls.2026.1749488 (Table 1); Lee et al., 2021, DOI 10.1007/s10068-020-00860-1 (Table 2).

No exposure estimate was calculated for the new records. Ginger and pepper concentrations are source-specific, and the chili value is dry-weight basis without a matching dry-serving input. Piperine paper reports population exposure separately using Korean dietary survey data, not an individual serving input.

## Caffeine downloadable archive verification

Retrieved the official USDA April 2018 SR Legacy CSV archive from `https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_csv_2018-04.zip` (SHA-256: `b80817294b8850530aaedf2e515c02593b1824f763a0ff356e5c2081643e6fd0`). The archive was joined directly across `sr_legacy_food.csv`, `food.csv`, `nutrient.csv`, `food_nutrient.csv`, and `food_portion.csv`. It confirms FDC 171890 / NDB 14209, the food description “Beverages, coffee, brewed, prepared with tap water”, nutrient ID 1057 / nutrient number 262 (Caffeine, MG), 40 mg/100 g, 8 data points, 30–44 mg observed range, derivation ID 1, and one cup (8 fl oz) = 237 g. The earlier official FDC API response remains separate corroborating provenance and was not counted as a second measurement.

## Screening scope

`compound_screening.csv` records 25 distinct Stage B compounds screened in this batch, their source/search scope, and the disposition. Candidate findings are not added to the quantitative active dataset. In particular, garlic paste values are held because the control was prepared with added water and the concentration basis could not be verified; the broccoli I3C table has an unresolved unit discrepancy; and no caffeine archive package was extracted.
