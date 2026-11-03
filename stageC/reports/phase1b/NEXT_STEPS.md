# Next steps — post Batch 106

Current checkpoint: Phase1B-2026-11-03-batch-106-prunin-source-followup. Research screening is 143/143; accepted identity-complete quantitative coverage is 100/107; seven complete-identity gaps remain; 36 Stage B identities are pending. The 130 minimum is not achieved.

## Batch 107 priorities

1. Retrieve and inspect Ceci et al. 2021 Supplementary Table S1, linked from the [PMC article](https://pmc.ncbi.nlm.nih.gov/articles/PMC8230845/) and [official MDPI supplement page](https://www.mdpi.com/article/10.3390/metabo11060378/s1) (DOI 10.3390/metabo11060378). Batch 106 retried these source paths; the file viewer returned a cache miss/access failure, so values remain untranscribed. The paper identifies authentic naringenin-7-glucoside/prunin, states compound-specific external calibration, and reports apple-pulp means ± SD (n=10) in mg/100 g FW. No values were available in Batch 106; obtain the exact table file before promotion.
2. Keep the nine orange by-product values in Batch 106 held. The fermentation paper does not state prunin-specific calibration; the PEF paper lists only five non-prunin standards without assigning a response curve to prunin. Do not count proxy-calibrated or process-specific values as accepted ordinary-food composition.
3. Continue the six other identity-complete gaps with genuinely new primary-table or official-dataset leads. Do not repeat completed Batch 104/105 searches without new evidence.
4. Continue candidate research for the 36 pending Stage B identities. Keep them outside active accepted data and prepare source-based adjudication proposals without editing StageB_FINALIZED.
5. If numeric apple Table S1 values become available, validate exact prunin identity, units, fresh-weight basis, sample counts and standard curve; ingest through the normalizer, rebuild mappings, update the coverage register and rerun tests.

## Validation after any accepted-data change

Run affected Phase 1B tests, Phase 1 regression tests, food ingestion validation, independent mapping rebuild comparison, and validate_phase1.py. Verify current active data hashes and Stage B snapshot hashes. Do not create a Phase 1B release until the release gate is genuinely met.

## Remaining identity-complete gaps

- MOL-V10-5281605 Baicalein
- MOL-V10-5281697 Scutellarein
- MOL-V10-5281703 Wogonin
- MOL-V10-5320315 Oroxylin A
- MOL-V10-2825024 7-Methoxyflavanone
- MOL-V10-3084961 Wogonoside
- MOL-V17-CID-92794 Prunin — strong apple-pulp quantitative source found, but exact S1 numbers still need direct retrieval.
