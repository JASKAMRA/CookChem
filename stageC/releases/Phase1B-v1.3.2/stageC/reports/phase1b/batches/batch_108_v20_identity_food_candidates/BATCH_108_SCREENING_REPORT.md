# Batch 108 — V20 identity-linked food candidate recheck

**Status:** screening documented; no active food rows or mappings promoted.

## Purpose

Recheck held Batch 102/105 food candidates after Stage B V20 expanded the identity-complete set. The active Phase 1 v1.3.0 package verifier still reports artifact hash/size mismatches, so the documented integrity gate remains closed for connector-dependent promotion. This batch preserves candidate findings only.

## Results

- Vanillic acid in rosehip fruit: the primary 2025 paper reports 76.1 ± 1.6 µg/g fresh weight and provides analyte-specific HPLC-DAD validation. Candidate remains outside active data pending exact pipeline recheck.
- Sinensetin in clementine peel: the primary paper reports 15 sample values in Table 7 in mg/100 g FW. Identity is complete in V20; food-use classification of the peel by-product still needs a rule-based decision.
- BHT in retail palm oil: the accessible primary conference paper resolves the 2009/2020 metadata conflict and Table 1 provides three palm-oil values (86.1 ± 0.2, 18.0 ± 0.1 and 6.8 ± 0.1 µg/g). The paper identifies its GC-MS method and BHT reference standard; quantitative calibration detail still needs review against ingestion criteria.
- All-trans beta-carotene in carrot: the held source reports beta-carotene concentrations, but exact all-trans specificity was not verified. It remains ineligible for exact-identity mapping.

Full source details and dispositions are in `candidate_recheck.csv`.

## Integrity and coverage

No active food records, mappings, connector snapshots, or release files were changed. Their pre/post hashes remain as recorded in `source_tree_baseline.json`. Current accepted coverage therefore remains 100 compounds, 546 records, and 546 mappings. The expanded Stage B identity set and the old connector are not silently treated as reconciled.

The Phase 1 v1.3.0 verifier result is preserved in `phase1_v13_verification_20261103.json`: **FAIL**, 1,203 artifacts scanned, 632 errors across 316 paths (one hash mismatch and one size mismatch per path). This is the concrete release-owner reconciliation blocker; no checksums were rewritten. A read-only comparison found 210 mismatched package paths byte-identical to the current Stage C tree, 99 different from it, and 7 release-local metadata/scripts. Details are in `phase1_v13_counterpart_comparison.json`; the different files require reconciliation rather than a blind checksum refresh.

The new V20 identities do expose existing food/mapping rows for 11 compounds that were previously identity-pending. These are candidates for a future connector reconciliation, not counted as accepted coverage until the connector/release gate is passed.
