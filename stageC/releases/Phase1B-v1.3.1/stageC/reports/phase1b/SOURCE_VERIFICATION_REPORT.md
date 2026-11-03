# Current dataset source audit — 2026-11-03

The active dataset has 539 accepted records spanning 66 distinct source-title/URL pairs. All records have source URL, title, explicit value and unit, basis description, analytical method and verification status (0 missing required source fields). 22 records have neither DOI nor PMID; their source title/URL and dataset/table locator remain available. Source-class counts are {'Authoritative food-composition database': 15, 'Primary analytical measurement': 519, 'Peer-reviewed secondary source': 5}. Batch 101's four accepted source articles and five held-source leads are documented in the active source registry and its screening note. The 28 new records retain source denominators and uncertainty; no moisture or density conversion was inferred.

The prior dated batch-level source notes below are historical verification records. The Batch 100 context findings remain separate from ordinary-food measurements.

---

# Source Verification Report

Batch 010 verified three primary studies: Kim JS (2018), DOI 10.3746/pnf.2018.23.1.35, Table 2 (free/esterified/bound berry fractions); Chun et al. (2017), DOI 10.1021/acs.jafc.7b01279, Table 4 (furocoumarins; n=3); and VanderMolen et al. (2013), DOI 10.1002/pca.2449, Table 3 (grapefruit juice in µM, retained for unit/basis review).

Batch 011 verified Gu et al. (2019), PMID 31533286, DOI 10.3390/antiox8090405, Tables 2–3 (HPLC-PDA and LC-ESI-QTOF/MS characterization across 16 foods; fresh-weight basis; triplicate).

Batch 012 verified Ali et al. (2021), PMID 34829641, DOI 10.3390/antiox10111770, §3.4/Table S1 (semi-quantified herb phenolics, µg/g dry weight, triplicate). Batch 013 verified Ali et al. (2023), PMID 36903854, DOI 10.3390/plants12050993, §2.6/Table S2 (native dried herbs/fruits, semi-quantitative values, triplicate).

Batch 014 verified Ali et al. (2023), PMID 36829816, DOI 10.3390/antiox12020254, §§2.2, 2.4 and 3.5/Table S2. The study analyzed whole-dried mountain pepper, freeze-dried rosella and lemon aspen, and finely ground strawberry gum using LC-ESI-QTOF-MS/MS; extractions were triplicate. Individual results are described as quantification/semi-quantification. Only exact food-specific numerical values explicitly stated in the full text were ingested; the reported µg/g sample values, SDs, and dried-source basis are preserved without fresh-weight conversion.

All accepted records carry source URL, DOI/PMID, table/section locator, reported units, food state, analytical method, sample size when available, and uncertainty notes.


Caffeine archive follow-up: the official [USDA FoodData Central download page](https://fdc.nal.usda.gov/download-datasets/) identifies SR Legacy as the April 2018 release and offers the CSV archive. The archive was downloaded from USDA and joined across `sr_legacy_food.csv`, `food.csv`, `nutrient.csv`, `food_nutrient.csv`, and `food_portion.csv`. It confirms FDC 171890 / NDB 14209, caffeine nutrient 1057 / 262 (MG), 40 mg/100 g, eight data points, range 30–44 mg, derivation code 1, and one 8-fl-oz cup = 237 g. Archive SHA-256 is recorded in Batch 009; the prior FDC API record remains an independent provenance path, not an additional measurement.


Batch 015 verified Mecha et al. (2020), PMID 31699168, DOI 10.1017/S0007114519002836, Table 2 and methods. Raw Moleiro common beans were quantified by UPLC-Q-TOF-MS against authentic standards, with external calibration and triplicate extraction. Accepted raw values are reported as µg/g raw-bean dry weight; paired cooked measurements are explicitly outside Phase 1B ingestion.



Batch 100 was independently reconciled from full-text tables: primary *Scutellaria* HPLC tables support six contextual target compounds on dry-root basis; the *Viburnum* amentoflavone study uses a dried-powder basis and reports Table 3 means ± SD with n=3 analytical measurements; the irilone value is secondary-source-only and held; the two remaining compounds lack exact numeric matrix values. None of these were added to ordinary-food composition.


## Batch 103 continuation state — 2026-11-03

All 143 Stage B IDs have at least one documented research/screening event. Accepted identity-complete quantitative coverage is 99/107; the 130 minimum remains unmet. Four quantitative identity-pending dye candidates and one qualitative-only NHDC finding are recorded separately. No release was created. See `batches/batch_103_final_screen/BATCH_103_SCREENING_REPORT.md` and the active checkpoint.


## Batch 104 eligible-gap audit — 2026-11-03

The eight remaining complete-identity gaps were re-audited against primary food-context sources. A 2026 widely-targeted Huangqin-tea study reports comparative baicalin and wogonoside findings, but no sample-level calibrated concentrations are accessible and study data are available on request. Prunin follow-up remains qualitative/untargeted or behind the primary table. Batch 104 logged 10 targeted searches and 12 source references; accepted coverage remains 99/107 with no food or mapping changes.
