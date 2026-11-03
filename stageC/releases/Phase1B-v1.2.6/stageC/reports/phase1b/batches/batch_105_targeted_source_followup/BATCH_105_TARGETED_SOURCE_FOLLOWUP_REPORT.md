# Batch 105 — targeted source follow-up and baicalin promotion

**Outcome:** five source-verified baicalin measurements were accepted from a primary Huangqin herbal-tea leaf study. Coverage increased by one unique identity-complete compound, from 99/107 to **100/107**. Seven identity-complete gaps remain. No release was created.

## Research completed

Batch 105 followed up on all eight gaps from the Batch 104 register, reviewed the 42-row pending-identity candidate ledger and 36 identity adjudication proposals, and re-read all 44 prior general candidate-register rows. It added 11 focused search-log events and assessed four sources. The 57-row prior source registry was preserved and extended with two new unique primary-source URLs; the 2026 Huangqin-tea DOI already existed.

The open-access 2025 Huangqin herbal-tea study collected *Scutellaria baicalensis* leaves in Inner Mongolia and divided them across microwave, electric, charcoal, steam, and natural-drying treatments. Its Table 2 reports baicalin in mg/g using the HPLC external-standard column. The published table and method support five values in the processed tea-leaf ingredient matrix. The companion LC-MS column contains peak areas and was not used. The published data-availability statement says the underlying data are confidential; the Table 2 values remain accessible.

| HHT leaf treatment | Baicalin, mg/g sample | Reported SD, mg/g | Stored normalized value |
|---|---:|---:|---:|
| Microwave roasting | 1.11 | 0.08 | 1110 mg/kg sample |
| Electric roasting | 2.79 | 0.22 | 2790 mg/kg sample |
| Charcoal roasting | 3.11 | 0.09 | 3110 mg/kg sample |
| Steam roasting | 1.10 | 0.16 | 1100 mg/kg sample |
| Natural drying | 1.05 | 0.03 | 1050 mg/kg sample |

**Basis limitation:** the table denominator is reported sample mass (mg/g). The article does not state a fresh- or dry-weight correction or the independent replicate count for this HPLC table. Records therefore retain an as-analyzed processed leaf-powder basis and are not interpreted as brewed-infusion concentrations. The source describes Huangqin herbal tea as a beverage; the measured material is its tea-leaf ingredient.

Primary source: Ao Zhang et al., “Combined metabolomics and electronic tongue technology elucidated the mechanisms of regulation of color–taste characteristics of Huangqin (Scutellaria baicalensis Georgi) herbal tea after various roasting processes” ([DOI 10.1016/j.fochx.2025.103250](https://doi.org/10.1016/j.fochx.2025.103250), [full text in PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12657378/)), Table 2 and Methods §2.6.

### Other seven gaps

- Baicalein (`MOL-V10-5281605`), Scutellarein (`MOL-V10-5281697`), Wogonin (`MOL-V10-5281703`), Oroxylin A (`MOL-V10-5320315`), and Wogonoside (`MOL-V10-3084961`): no target-specific standard-calibrated sample-mass result was verified in the newly inspected HHT source. Relative or comparative metabolomic evidence remains non-quantitative for Phase 1B. For wogonoside, the 2026 HQT study still has no accessible sample-level values; a data request was drafted but not sent.
- 7-Methoxyflavanone (`MOL-V10-2825024`): exact-name follow-up found no eligible ordinary-food concentration; similar flavanones were not substituted.
- Prunin (`MOL-V17-CID-92794`): the 1993 primary paper’s numerical table remains inaccessible. A 2022 primary study supplies 13 run-level prunin yields after acid-catalyzed subcritical-water hydrolysis of immature citrus pomace, expressed per gram of dry starting sample. These process-generated/liberated yields are retained in the central candidate register and Batch 105 detail file as **held**, not native food concentrations and not active records.

Primary held source: Lim et al., “Organic Acid-Catalyzed Subcritical Water Hydrolysis of Immature Citrus unshiu Pomace” ([DOI 10.3390/foods11010018](https://doi.org/10.3390/foods11010018)), Table 1. No value was inferred from the 1993 abstract.

## Candidate and identity review

- The **42 pending-identity candidates** were individually reconciled to the current Stage B snapshot. All 42 belong to unresolved Stage B identities and remain separate from accepted food records; 39 have numeric values, one is qualitative-only, and two are method-only. No candidate was promoted across the identity gate.
- The **36 identity adjudication proposals** were joined to current Stage B identity status and candidate counts. All still require formal Stage B review or specialist adjudication; no identity change, manifest edit, or release edit was made.
- The **44 prior general candidate rows** were re-read against their recorded source-specific disposition and current coverage. Their prior states were retained; no newly verified Batch 105 evidence cleared their stated analyte, mass-basis, matrix, source-access, or identity blockers. Thirteen new prunin run values were added to this same held-candidate register.
- A structured data request for the 2026 Huangqin-tea study is saved at `author_data_request_2026_huangqin_tea.txt`. The contact and corresponding-author identity were not independently confirmed in this batch; the draft was not sent.

## Coverage and quality

| Metric | Batch 104 baseline | Batch 105 current |
|---|---:|---:|
| Stage B registry | 143 | 143 |
| Research screening | 143/143 | 143/143 |
| Food-composition records | 541 | 546 |
| Mapping rows | 541 | 546 |
| Unique quantitative mappings, including identity-pending | 115 | 116 |
| Identity-complete compounds | 107 | 107 |
| Accepted identity-complete quantitative coverage | 99/107 | **100/107** |
| Complete-identity gaps | 8 | **7** |
| Pending identities | 36 | 36 |
| Pending-identity candidate rows | 42 | 42 |
| Search-log events | 448 | 459 |
| Source-registry rows / unique URLs | 57 / 56 | 59 / 58 |
| Orphan mappings | 0 | 0 |

The 130-compound minimum remains unmet by 30. Even if all seven remaining complete-identity gaps are filled, at least 23 pending identities must be formally resolved and also obtain qualifying quantitative ordinary-food evidence. The 143 stretch target remains unmet by 43.

Validation passed with 546 food records and 546 mappings, zero food/mapping/orphan errors, 36 identity-review items, and zero Stage B snapshot changes. The mapping rebuild equals the active mapping file in all 546 rows; the earlier 511-record historical file prefix remains byte-identical. Focused regression tests passed 38/38 and the complete Stage C unittest suite passed 94/94. One initial ingestion-category error and stale regression assertions were corrected; no failures remain. Detailed results are in `validation_and_test_results.json`, the central checkpoint, and `PROGRESS.md`.

## Durable files

See `baseline.json`, `coverage_delta.json`, `screening_matrix.csv`, `source_assessment.csv`, `accepted_rows.csv`, `candidate_measurements.csv`, `pending_candidate_review.csv`, `identity_review_36.csv`, `existing_candidate_register_review.csv`, and `mapping_rebuild.csv`. Batch 104 report and research artifacts remain unchanged. `StageB_FINALIZED` and the Phase 1-v1.3.0 dependency remain read-only.
