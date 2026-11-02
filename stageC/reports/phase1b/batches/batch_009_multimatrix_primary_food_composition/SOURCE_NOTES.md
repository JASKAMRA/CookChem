# Batch 009 — Multi-matrix primary food composition

## Acquisitions

Five new records were submitted to the existing Stage C ingestion pipeline: 6-gingerol and 6-shogaol in fresh Japanese ginger rhizomes; xanthohumol in hop flowers; capsaicin in Habanero chili on a dry-weight basis; and piperine in retail black pepper. Values and source locators are preserved in `new_primary_measurements.csv`. The expanded cumulative pipeline input is `accepted_food_records.csv`.

Primary measurement studies: Koch et al., 2017, DOI 10.3390/ijms18020452 (Table 2); Rodríguez et al., 2019, DOI 10.3390/foods8100435 (Table 5); Pandey et al., 2026, DOI 10.3389/fpls.2026.1749488 (Table 1); Lee et al., 2021, DOI 10.1007/s10068-020-00860-1 (Table 2).

No exposure estimate was calculated for the new records. Ginger and pepper concentrations are source-specific, and the chili value is dry-weight basis without a matching dry-serving input. Piperine paper reports population exposure separately using Korean dietary survey data, not an individual serving input.

## Caffeine archive attempt

USDA lists the April 2018 SR Legacy release on its official download page. The official JSON and CSV ZIP package links could not be retrieved here: the web reader does not support ZIP content and the local downloader failed DNS resolution. No third-party mirror was used and archive extraction is not claimed. The previously accepted USDA FoodData Central API record remains separate; the archive attempt did not duplicate or change it.

## Screening scope

`compound_screening.csv` records 25 distinct Stage B compounds screened in this batch, their source/search scope, and the disposition. Candidate findings are not added to the quantitative active dataset. In particular, garlic paste values are held because the control was prepared with added water and the concentration basis could not be verified; the broccoli I3C table has an unresolved unit discrepancy; and no caffeine archive package was extracted.
