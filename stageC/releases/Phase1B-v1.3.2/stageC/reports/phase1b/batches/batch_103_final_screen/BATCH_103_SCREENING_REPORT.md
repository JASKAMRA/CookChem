# Batch 103 — final five first-pass screens

**Status:** `PHASE1B_BATCH_COMPLETE`; the full 143-ID research screen is complete. No identity-pending value was ingested.

## Targets and findings

Batch 103 screened Allura Red AC, Brilliant Blue FCF, Azorubine, Neohesperidin dihydrochalcone, and Tartrazine. Four have quantitative candidates in confectionery/snacks; all remain outside accepted data because their Stage B identities are pending and exact tested salt/structure equivalence is not independently established. The fifth has qualitative detection evidence but no accessible exact concentration.

- **Allura Red AC:** four Table 2 food values (gummy bears, red chewing gum, and two sweets candies), 19.9–70.0 mg/kg product mass, mean ± SD, n=3.
- **Tartrazine:** three Table 2 values (yellow chewing gum, ice pops, sweets candy 1), 13.3–127.5 mg/kg product mass, mean ± SD, n=3.
- **Brilliant Blue FCF:** four reported food values: 36.4 and 13.0 mg/kg in two candy products, 31.1 mg/kg chocolate candy, and 2.6 mg/kg baked green pea.
- **Azorubine:** candy mean 181.22 ± 20.22 mg/kg reported in a 1998 food-dye study; sample count and individual values are not exposed in the accessible summary.
- **Neohesperidin dihydrochalcone:** Janvier et al. reports detection in three hard candies, quantifiable in one, but accessible Table 4 does not expose that sample's amount. The reported 10 µg/kg LOQ is not substituted for a measurement.

Exact rows, source locators, methods, and limitations are in `pending_identity_candidates.csv` and the cumulative `PENDING_IDENTITY_CANDIDATES.csv`. No candidate was added to the accepted food table or mappings.

## Coverage after Batch 103

- Stage B universe screened: **143/143**.
- Identity-complete quantitative coverage: **99/107**.
- Pending identity reviews: **36**; candidate measurement rows across Batches 102–103: **39 numeric** plus **3 nonnumeric/method-only rows**.
- Active accepted records/mappings: **541/541**; unique quantitative mapping IDs including identity-pending records: **115**; blocked legacy mapping rows: 46; orphan mappings: 0.
- The **130 minimum is not achieved**. At 99 accepted identity-complete compounds, 31 additional eligible compounds are needed. The current 107-identity ceiling leaves a maximum of eight additional complete-identity compounds; reaching 130 also requires at least 23 pending Stage B identities to be formally resolved and have qualifying food measurements.

## Validation and next justified work

Final validation passed on 541 food records and 541 mappings: zero data or mapping errors, zero orphans, 36 identity reviews pending, 46 legacy mappings blocked, and no Stage B snapshot changes. Focused `unittest` checks passed 29/29 (food composition 7, mapping 9, Batch 101 regression 8, continuation 5). An independent reconstruction matched all 541 active mappings row for row, including the historical 539-row Batch 101 prefix. `pytest` is unavailable in this environment; the focused tests ran with Python's standard-library runner. The 143 first-pass screens are complete; future acquisition should follow genuinely new source leads or formal Stage B identity adjudications. No release was created.
