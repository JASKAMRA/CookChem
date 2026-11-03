# CookRisk Stage B V9 handoff — 2026-10-29

## What was recovered

A broader search across the available Desktop and Documents project roots, attached task files, nested/older Stage B release folders, structured data, source caches, validation scripts and reports located the authoritative evidence in `Documents/CookChem/stageB/release_v8_20261015_quality`. Earlier V7, V6, V5, V4, expansion V2/V3, source and audit files were retained for comparison. Repository history was also checked: only `main`/`origin/main` was available, and the `stageB/` tree is untracked in the repository, so Git history could not establish provenance for those release files. V8 README and handoff establish the 60-anchor/189-record V8 dataset as the latest finalized baseline; older expansion tables were not concatenated because they overlap and predate V8.

The new release is a V8-based copy at `Documents/CookChem/stageB/release_v9_20261029`. The original V8 folder was left untouched. V9 preserves the original 189 evidence IDs and rows in order, then appends supported additions.

## Counts

- Verified baseline: **60 anchors**, **189 interaction evidence rows**, **87 distinct drug/probe labels**, **121 unique PMID publications**.
- V9: **74 anchors** (+14), **210 evidence rows** (+21), **130 unique PMID publications** (9 net new bibliography entries; one of the ten reviewed PMIDs was already indexed), and **103 distinct drug/probe labels**.
- Progress: **74/100 anchors**; **26** remain.
- Evidence classes in V9: `{"Human pharmacokinetic": 70, "In vitro": 85, "Animal": 51, "Controlled clinical": 4}.
- The inherited V8 review split was 21 selected-full-text records, 164 abstract records, and four qualitative abstracts with numeric table review pending. V9 adds 19 abstract-verified records and two phytosterol rows transcribed from a reviewed PMC full-text table. The four inherited resveratrol numerical holds remain held.

## Added anchors

- **6',7'-Dihydroxybergamottin** (PubChem CID 6440498): Named component of grapefruit juice; purified compound tested against CYP3A4 in a primary mechanistic study. Human juice-serum PK is not treated as isolated-compound evidence.
- **Astaxanthin** (PubChem CID 5281224): Food/supplement-associated xanthophyll with direct human CYP enzyme-panel testing and a separate human UGT panel; weak/null findings retained.
- **β-Cryptoxanthin** (PubChem CID 5281235): Food carotenoid with direct CYP and UGT interaction screening, including quantitative weak inhibition and a null/low-risk interpretation.
- **Canthaxanthin** (PubChem CID 5281227): Food colorant/nutritional supplement carotenoid with direct CYP and UGT inhibition screening; effects were weak in vitro.
- **Biochanin A** (PubChem CID 5280373): Principal red-clover isoflavone with CYP1A2 data and independent P-gp cell-transport evidence; rat P-gp substrate PK publication is not added here because metadata was ambiguous.
- **Formononetin** (PubChem CID 5280378): Principal red-clover isoflavone with direct human/rat microsomal CYP inhibition results; predicted in-vivo statements remain labeled as predictions.
- **Puerarin** (PubChem CID 5281807): Major kudzu-root isoflavone with human probe-drug observations, human/rat microsomal CYP3A work, rat buspirone PK, and cell-model CYP2D6 evidence. Herbal preparation and isolated compound are not equated.
- **Phloretin** (PubChem CID 4788): Diet-associated apple/pear chalcone with direct cellular P-gp efflux evidence; no human PK interaction is inferred.
- **Acacetin** (PubChem CID 5280442): Food-associated flavonoid directly screened against CYP3A4; strongest reported screening result in the source (95% inhibition at 1 μM).
- **Pinocembrin** (PubChem CID 68071): Food-associated flavanone with qualitative irreversible CYP3A4 inhibition in a primary aglycone screen; no numerical potency is claimed.
- **Isorhamnetin** (PubChem CID 5281654): Food-associated flavonol with qualitative irreversible CYP3A4 inhibition in a primary aglycone screen; no numerical potency is claimed.
- **Tectochrysin** (PubChem CID 5281954): Food-associated flavonoid tested as a pure aglycone and reported to irreversibly inhibit CYP3A4; no numerical potency is claimed.
- **β-Sitosterol** (PubChem CID 222284): Common dietary phytosterol with direct rat-microsome CYP3A4/CYP2D6 screening; weak activity is retained as in-vitro evidence only.
- **Stigmasterol** (PubChem CID 5280794): Common dietary phytosterol with direct rat-microsome CYP3A4/CYP2D6 screening; weak activity is retained as in-vitro evidence only.

## New evidence and interpretation

The 21 added records cover CYP and UGT enzyme panels, human P-glycoprotein cell assays, human puerarin probe-drug data, rat puerarin/buspirone pharmacokinetics, and a rat-microsome phytosterol screen. Records preserve null/weak findings and source-reported units. Positive in-vitro findings are not treated as clinical risk. The human felodipine increase in the grapefruit study was observed with grapefruit-derived juice serum; it is not represented as an isolated-DHB human interaction. Purified DHB’s separate CYP3A4 in-vitro arm is the evidence linked to that anchor.

Ten primary PMIDs were reviewed for additions: 15179411, 23669408, 27529203, 26278343, 12604704, 20195825, 24710899, 24786236, 30301254 and 26139922. PubMed abstracts were reviewed for metadata and claim-level extraction, except the β-sitosterol and stigmasterol IC50 values from PMID 26139922, which were checked in its full-text table (PMC4486538). The search was focused and is not a systematic review.

The candidate screen found a wrong proposed phloretin mapping: CID 5281614 is fisetin. Phloretin was admitted under CID 4788 after checking the PubChem structure record. This was corrected before the compound entered the release and is logged.

## Warnings and provenance

The 25 inherited warning entries (24 distinct codes) remain in the V9 ledger with their prior statuses. Three V9 warnings were added. **25 entries across 27 codes are unresolved or partially resolved**. Specifically, apigenin/rutin–paclitaxel preparation/attribution ambiguity, the apigenin Cmax discrepancy, daidzein reporting ambiguity, and daidzein/quercetin cooking-retention linkage limitations remain open. The original-nine selection dates and primary triggers remain unrecovered: the inherited ledger documents the prior search across local records; V9 does not invent historical dates. New compound rationales are explicitly retrospective and dated to this release.

Cooking-retention evidence is carried as a separate unchanged table; no cooking result was used to support a drug-interaction claim. New rows use unique PubChem CID plus name links. Phloretin has SMILES, InChI and InChIKey populated; for the other 13 new anchors those structure strings remain a follow-up item, so the registry warns against treating the CID/name audit as a complete exact-structure duplicate audit.

## Validation

- Existing V8 validator rerun after expansion: **26/26 checks passed**, **12/12 mutation tests detected**, **8,087 prior files checked**, **0 preservation mismatches**.
- V9-specific integrity validation: **PASS**, no errors; **7/7 mutation tests detected**. Checks cover baseline row preservation, IDs, mappings, source/cache traceability, bibliography uniqueness, selection rationale coverage, warnings and cooking-domain separation.
- The checks establish file integrity and relationships. They do not independently validate every scientific extraction or replace full-text review.

## Deliverables

Main files are in the release folder:

- `outputs/compound_registry_v9.csv`
- `outputs/stageB_food_drug_interactions_v9.csv`
- `outputs/drug_probe_registry_v9.csv`
- `outputs/study_registry_v9.csv`, `outputs/source_bibliography_v9.csv`
- `outputs/identity_structure_audit_v9.csv`
- `outputs/v9_selection_decisions.csv`, `outputs/v9_candidate_screening_log.csv`
- `outputs/v9_source_audit.csv`, `outputs/claim_support_and_verification_v9.csv`
- `outputs/warning_resolution_ledger_v9.csv`, `outputs/v9_change_log.csv`
- `outputs/cooking_retention_evidence_v9.csv`
- `audit/v9_validation_report.json`, `audit/v9_baseline_hash.json`
- Rebuild scripts: `build_v9_data.py`, `prepare_validate_v9.py`

Scope remained Stage B. Stage A models, Stage C exposure estimation and Stage D scoring were not changed or created.
