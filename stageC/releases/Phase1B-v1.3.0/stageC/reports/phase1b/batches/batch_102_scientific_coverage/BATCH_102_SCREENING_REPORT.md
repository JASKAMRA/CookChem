# Batch 102 — scientific coverage continuation

**Status:** `PHASE1B_BATCH_COMPLETE`. Stage B and Phase 1 foundations remain read-only.

## Batch scope and result

Batch 102 screened 15 targets: Apigetrin, Myricitrin, Prunin, three ginkgolic-acid homologues, Vanillic acid, Demethoxycurcumin, Bisdemethoxycurcumin, Sinensetin, Eupatorin, all-trans-β-Carotene, Butylated hydroxytoluene, Dodecyl gallate, and Octyl gallate. Twelve of these had no prior search-log event; the three Stage B-complete leads were rechecked against new source paths.

Two direct quantitative values were accepted: Apigetrin in lamb’s lettuce, 0.012 µg/g FW (Table 3), and Myricitrin in spinach, 398.2 mg/kg on the paper’s as-analyzed sample-mass basis. The latter is not labelled FW or DW because the paper does not report moisture correction. Myricitrin’s distinct spinach value does not resolve the article’s conflicting apple values; neither apple value was ingested.

Active records and mappings now total **541 each**; unique quantitative mappings including pending identities are **115**; accepted identity-complete coverage is **99/107**. Research coverage is **138/143**. The 130 minimum remains **not achieved**.

## Pending-identity candidate findings

All numerical candidate findings are in `PENDING_IDENTITY_CANDIDATES.csv` and the batch-specific copy. They are not exposure-eligible. They include indexed ginkgolic-acid values in skimmed powder (primary paper not accessible), a strong rosehip vanillic-acid FW result, hydrolysis-derived soybean conjugates (different analyte form), abstract-only turmeric ranges with unclear mass basis, 15 sinensetin measurements in clementine peel by-products, an extract-only eupatorin lead, carrot β-carotene food values requiring source/isomer confirmation, and palm-oil BHT with a journal-year/issue conflict. Dodecyl and octyl gallate searches found method-only leads, not actual food-sample concentrations.

Prunin remains unquantified: occurrence or qualitative by-product detection is not converted to a concentration. The Batch 101 candidates and all prior search history are preserved.

## Identity adjudication

`IDENTITY_ADJUDICATION_PROPOSALS_2026-11-03.csv` contains the 36 currently pending Stage B identities, their exact snapshot notes/identifiers, source leads where available, the remaining uncertainty, and a recommendation to retain pending status pending independent parsing and formal specialist review. It proposes no Stage B edits.

## Cumulative state

- Stage B universe: 143; identity complete 107; identity pending 36.
- Research/screening: 138/143.
- Quantitative mappings (including pending): 115 unique compounds.
- Identity-complete accepted quantitative coverage: 99/107; 10 baseline gaps reduced by two to 8.
- Food records/mapping rows: 541/541; orphan mappings: 0; blocked legacy mapping rows: 46.
- Numeric pending-identity candidate rows: 27; these do not count as accepted coverage.
- Minimum/stretch targets: 130/143; neither achieved. The current Stage B identity ceiling is 107.

## Verification

The accepted append script verified the exact pre-Batch 102 file hashes, record counts, complete Stage B identity status, CID, full InChIKey, exact mappings and unique IDs before append; both original active data files remain byte-identical prefixes. `python stageC/scripts/validate_phase1.py` passed on 541 records and mappings, with 99 eligible compounds, zero food/mapping errors, zero orphans and no Stage B snapshot changes. Built-in `unittest` focused tests passed: food composition 7/7 and compound mapping 9/9. The environment does not have pytest installed; no pytest result is claimed. Independent full-file mapping reconstruction remains pending.
