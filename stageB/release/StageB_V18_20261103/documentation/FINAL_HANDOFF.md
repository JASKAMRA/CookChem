# CookRisk Stage B final consolidation handoff

**Authoritative directory:** `StageB_Final`  
**Baseline:** immutable V12 release, independently recounted during consolidation.  
**Release state:** `PASS_WITH_WARNINGS` for structural/reproducibility checks; scientific review remains incomplete.

## Verified dataset counts

- 119 compound anchors; 286 interaction-evidence records.
- 127 drug/probe labels; 153 study-registry rows.
- 151 PMID-linked publications and 148 distinct nonblank DOIs among evidence rows.
- 55 warning rows; warning statuses and source notes are retained.
- Evidence classes: {"Animal": 51, "Controlled clinical": 4, "Human pharmacokinetic": 70, "In vitro": 160, "Other human clinical": 1}.
- Claim-support registry covers 286 distinct evidence IDs; the inherited source-audit file contains 76 distinct evidence IDs, leaving 210 rows without a separate source-audit row.

V12 handoff reports target 150 and is 31 anchors short. This consolidation did not add research records.

## Consolidation decisions

V12 current data tables were copied to one canonical location each under `data/`, `provenance/`, and `identity/`. V12 source/audit artifacts not represented by canonical tables were retained verbatim once; exact duplicate files were mapped to their retained copy in `history/v12_file_disposition.csv`. The full original V12 release and V2–V11 releases remain in place, untouched. No older data rows were reintroduced. The V12 change log and direct V9–V12 stable-ID diff are under `history/`. `history/legacy_release_record_reconciliation.csv` compares available V2–V11 evidence and compound IDs against V12; all available evidence IDs and compound IDs were found in V12, with non-identical historical rows and schema differences listed. V2 compound coverage is name/alias-only because it has no compound registry. V7 contains 188 evidence rows while its clean-copy snapshot has 189; both counts are preserved as observed. `history/release_transition_summary.csv` and `history/release_transition_record_changes.csv` attribute adjacent-version additions and field changes, including changes to quantitative outcomes and verification fields. An inherited `v10_release_summary.json` in V12 contains stale V10/V9 labels and counts; it is archived as a historical artifact and was not used for authoritative counts.

## Validation and mutation results

The packaged validator checks identifier uniqueness, core foreign keys, study/publication links, evidence classes, source/claim/selection coverage, duplicate structures and contexts, warning identifiers, and separation of cooking-retention data. It records warnings separately from structural failures. Twelve isolated mutations are run against temporary copies; each must trigger its intended validation code. Clean-copy results are reported in `validation/clean_copy_comparison.csv`.

The V12 baseline reported 32/32 automated checks, 34/34 mutations, 15/15 preservation checks, and 12/12 byte-identical clean-copy outputs. Those results are preserved in `validation/audit/`. The final package also reports its own 16 structural checks and 12 mutation cases. The final package flags 210 missing source-audit rows, 90 blank quantitative-outcome fields, and 13 numeric/unit review items; these are recorded separately from the 55-row warning ledger.

## Remaining scientific limitations

V12 reports only two claims as full-text/table verified. Its six inherited manual checks are partial or incomplete, including inherited food-occurrence review, chemical-form/stereochemistry adjudication, numerical/table verification, source-to-claim review, warning-source review, and cohort overlap. Three inherited automated review signals concern direction/text mismatches, repeated contexts, and missing numeric units. Eleven inherited compound evidence-count fields did not reconcile and were preserved with discrepancies documented. See `validation/manual_review_status.csv` and `validation/audit/`.

The consolidation found no basis to declare all historical publication records independent studies; PMID/DOI identifiers are not cohort identifiers. No inherited warning was artificially closed. No data correction or historical rationale was invented. Exact duplicates are documented; non-identical observations remain separate.

## Stage C / Stage D interface

Use stable `Compound_ID`, `Evidence_ID`, and `Study_ID` values and preserve PMID/DOI, source locators, evidence class, direction, outcomes/units, verification status, limitations, and warning flags. Stage B does not calculate dietary exposure, cooking-retained dose, or patient-specific risk. In-vitro and animal results must remain distinguishable from clinical evidence. No Stage C or Stage D code is included.

## File map

See `README.md`, `documentation/data_dictionary.md`, `history/release_lineage.csv`, `history/legacy_release_record_reconciliation.csv`, `history/release_transition_summary.csv`, `history/release_transition_record_changes.csv`, `history/cross_release_record_diff_v9_v12.csv`, `history/v12_file_disposition.csv`, and `manifests/SHA256SUMS.json`.
