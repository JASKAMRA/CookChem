# CookRisk Stage B V12 handoff

**Release:** `release_v12_20261030`  
**Status:** **PASS_WITH_WARNINGS**  
**Scope:** literature evidence only. No exposure, retained-dose, or patient-specific risk estimation.

## Dataset

V11 was independently recounted at 105 anchors, 272 evidence rows, 121 probe labels, 144 PMID-linked publications, 141 unique nonblank DOI values in evidence, and 41 warnings. V11 audit files report 43 automated assertions and six pending manual checks; the V11 handoff's 45/45 figure conflicts with those underlying results.

V12 contains **119 anchors** (14 added), **286 evidence rows** (14 added), 127 probe labels, 151 PMID publications, 148 unique nonblank DOIs, and 55 warning rows over 40 codes. The release is **31 anchors short of 150**.

New anchors: 1,5-Dicaffeoylquinic acid, 1,3-Dicaffeoylquinic acid, 18β-Glycyrrhetinic acid, Indole-3-carbinol, Phenethyl isothiocyanate, Irilone, 5,4′-Dihydroxy-3,6,7,8,3′-pentamethoxyflavone, Gossypetin, Herbacetin, (-)-Epicatechin gallate, (-)-Epigallocatechin, (-)-Catechin gallate, (+)-Gallocatechin, (+)-Gallocatechin gallate. They were admitted with food-context/assay limits and source locators. 1,3- and 1,5-dicaffeoylquinic acids are distinct positional/stereochemical entities; 18β-glycyrrhetinic acid is identified as a licorice-derived metabolite; irilone is supplement-associated; herbacetin free-aglycone exposure is uncertain; the citrus peel flavone and gossypetin remain in-vitro-only. Indole-3-carbinol's human probe result used 800 mg/day supplement dosing and must not be interpreted as a food-dose interaction.

## Validation and preservation

- Automated V12 suite: 32/32 pass, 0 fail.
- Mutation tests: 34/34 intended defects detected in isolated temporary fixtures (100.0%); no misses. The clean data also triggers three inherited review signals (direction/text mismatch candidates, repeated contexts, and missing numeric units); these are listed for scientific review, not counted as false positives.
- Clean-copy rebuild: 12/12 core outputs byte-identical.
- Regression: 15/15 preservation checks pass; 1032 shared V11 package files were hash-compared with no changes. The cooking-retention file is byte-identical.
- Eleven V11 anchor `Evidence_Records` summary fields do not match their own evidence-row counts; inherited values were preserved unchanged and discrepancies are listed in `audit/v12_inherited_count_discrepancies.csv`.

## Scientific review

- Claims marked full-text/table verified: 2; no inherited claim was upgraded and no new evidence row was marked full-text/table verified.
- Numeric outcome screening: 159 records queued in `audit/v12_numerical_discrepancy_screen.csv`; selected new values were checked against the cited primary-source locator. Inherited numeric holds remain.
- Food-context coverage: all 119 anchors have a displayed context row, but the 105 inherited contexts were not independently source-verified one by one; all 14 additions carry explicit context limitations.
- Chemical identity: 119 identity rows and 0 exact duplicate InChIKeys found by string check. No full graph comparison or expert stereochemistry review was available; known near-duplicate cases remain flagged.
- Cohort overlap: not adjudicated; separate publication identifiers are not treated as independent cohorts.
- Three automated baseline signals (direction/text mismatch candidates, repeated contexts, and missing numeric units) are detailed in `audit/v12_inherited_validation_findings.csv` for source review.

## Six inherited manual checks

- **FC-01 — PARTIAL:** Full source-to-occurrence verification for every inherited row not completed.
- **CH-05 — PARTIAL:** No complete graph, tautomer, salt, protonation, or stereochemistry adjudication.
- **NX-05 — PARTIAL:** Full-text verification of every inherited numeric record is not complete.
- **CL-03 — PARTIAL:** All inherited claims not individually source-verified.
- **PV-07 — NOT COMPLETED:** Distinct PMIDs/DOIs are not proof of independent cohorts.
- **WA-03 — PARTIAL:** Full primary-source validation of every closure remains pending.

The full original scopes were not completed. No inherited full-text verification status was upgraded. Source-to-claim review, complete numeric/table re-extraction, one-by-one inherited food occurrence review, expert structure adjudication, and cohort-overlap review remain incomplete.

## Warning ledger

The V11 ledger's 41 rows were carried forward without closure. V12 adds 14 explicit limitations. Current status counts: Not applicable: 2, Partially resolved: 13, Resolved: 1, Unresolved: 39. No V11 warning was closed in V12.

## Reproducibility and files

The rebuild and mutation scripts use the Python standard library. See `build_v12.py`, `mutation_test_v12.py`, `audit/v12_test_plan.csv`, `audit/v12_test_results.csv`, `audit/v12_mutation_test_results.csv`, `audit/v12_regression_report.csv`, and `audit/v12_clean_rebuild_comparison.csv`. File hashes are in `SHA256SUMS_V12.json`.

**Assessment:** PASS_WITH_WARNINGS is appropriate: structural checks, mutation injection, regression and clean rebuild pass, but the anchor target is unmet and the scientific/manual review backlog remains. This dataset is not clinical decision support.
