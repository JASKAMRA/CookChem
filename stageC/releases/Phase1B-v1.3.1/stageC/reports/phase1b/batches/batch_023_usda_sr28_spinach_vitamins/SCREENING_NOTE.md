# Batch 023 — USDA SR28 vitamin C and phylloquinone in raw spinach

## Screening decision

Two authoritative USDA food-composition values were extracted as candidates. Phylloquinone is an exact analyte-name match to Stage B. The ascorbic-acid value remains held for target-scope review because USDA nutrient 401 is labelled “Vitamin C, total ascorbic acid” and its source-specific form composition/method is not provided. The USDA SR28 report for NDB 11457 lists raw spinach, Vitamin C total ascorbic acid 28.1 mg/100 g edible portion (SE 4.129; n=7), and Vitamin K (phylloquinone) 482.9 µg/100 g (n=1). The report’s 30 g cup measures are 8.4 mg Vitamin C and 144.9 µg phylloquinone.

## Source

USDA National Nutrient Database for Standard Reference Release 28, NDB 11457, “Spinach, raw” (food group report). Official report: https://www.ars.usda.gov/ARSUserFiles/80400535/Data/SR/SR28/reports/sr28fg11.pdf. The same legacy food item is FDC SR Legacy ID 168462. Table values are per 100 g edible portion; the source labels the analytes distinctly.

## Scope and uncertainty

Values are copied from an authoritative food-composition record, not a new primary analysis. The report does not provide cultivar, lot, geography, or method details in this food report. Vitamin C has seven data points and a standard error; phylloquinone is listed as one data point without a standard error. Both are raw-food reference values and should not be treated as lot-specific. The ascorbic acid candidate is explicitly kept from auto-mapping pending the total-vitamin-C versus exact Stage B structure review.

## Pipeline gate

Candidate CSV only. These records are not appended to cumulative food composition or counted as accepted coverage until the Stage B checksum mismatch is reconciled and the connector passes.


## Method-scope follow-up (2026-11-02)

The USDA SR documentation labels nutrient 401 “Vitamin C, total ascorbic acid.” SR25 documentation says nearly all nutrient 401 records were determined by the microfluorometric method (AOAC 967.22), while older unupdated values were mainly reduced ascorbic acid by AOAC 967.21. AOAC 967.22 oxidizes ascorbic acid and quantifies the product; authoritative food-analysis guidance describes this class of method as measuring both ascorbic acid and dehydroascorbic acid. Because this specific SR28 spinach record does not expose its source reference/method, the applicability is indirect. The observed database number should stay an unmapped total-vitamin-C candidate, not an exact Stage B reduced-ascorbic-acid concentration. Keep candidate held; do not promote coverage. Sources: USDA SR25 documentation (https://www.ars.usda.gov/ARSUserFiles/80400535/DATA/sr25/sr25_doc.pdf); FAO food-composition analytical methods (https://www.fao.org/4/y4705e/y4705e12.htm).


## Current disposition (2026-11-02)
The exact USDA spinach phylloquinone record was promoted into active Stage C coverage (Batch 077). Total vitamin C remains held because its source nutrient scope is not an exact match to reduced ascorbic acid.
