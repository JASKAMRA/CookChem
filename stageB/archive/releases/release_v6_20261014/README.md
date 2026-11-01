# CookRisk Stage B v6

Release date: 14 October 2026. This is a new Stage B evidence release; V5 is unchanged.

## Verified result

| Metric | V5 | V6 |
|---|---:|---:|
| Anchors | 26 | 44 |
| Evidence rows | 118 | 147 |
| Drugs/probes | 58 | 71 |
| Primary publications (unique PMID) | 80 | 101 |
| Human PK | 61 | 64 |
| Controlled clinical | 2 | 2 |
| Animal | 27 | 37 |
| In vitro | 28 | 44 |
| Numerical outcome rows | 73 | 84 |
| Open warning entries / distinct codes | 15 / 14 | 17 / 16 |

18 anchors and 29 evidence rows added, with 21 newly represented primary publications. Three new rows are human PK, ten animal and sixteen in vitro. All new interaction claims are abstract-verified; none is claimed as fully re-extracted from full text. The existing V5 suite was actually rerun first: 53/53 checks and 11/11 mutation tests. Extended result: 90/90 checks, zero errors; 20/20 mutation tests; PASS_WITH_WARNINGS. Frozen prior workspace files, including V5, were hash-compared without changes. Inspect the audit files for executed details.

The target is **not reached**: 44/50. Six candidates are deferred, not rejected as universally unsupported: baicalein, rutin, pterostilbene, ursolic acid, oleanolic acid and glycyrrhetinic acid. Their remaining dietary scope, arm/preparation extraction and identity tasks are in candidate_selection.csv. Capped retrieval is not an exhaustive systematic review; no independent second reviewer adjudicated extraction.

## Read the outputs

- reports/CookRisk_StageB_v6_Report.pdf: four-page findings report and process flowchart.
- outputs/compound_registry.csv: 44 reference anchors; original IDs and registry values retained. New IDs use CHEM-PUBCHEM-{CID}.
- outputs/stageB_food_drug_interactions_v6.csv: established 36-column schema, 118 V5 rows unchanged, new SB-0119 through SB-0147.
- outputs/claim_support_and_outcome_audit.csv: 29 new record claims with exact supporting abstracts, access level and limitations. Numerical token checks supplement manual context review; they do not prove endpoint semantics.
- outputs/candidate_selection.csv and compound_selection_provenance_audit.csv: current selection reasoning, sources, dates and deferrals. Experimental sources are listed separately from selection/food sources; a selection source is not interaction proof.
- outputs/identity_structure_audit.csv: reference identity and mapping restrictions. New anchors are standalone literature entities, not repaired master observation links. SMILES in new registry rows are connectivity SMILES; InChI and InChIKey carry reference stereochemistry. Where study purity is unspecified it remains flagged.
- outputs/cooking_retention_evidence.csv: inherited processing evidence, preserved separately. No new coefficients, exposure estimates or master-link certification.
- outputs/processing_provenance_audit.csv and processing_source_resolution.csv: inherited analyte/method restrictions and exact archived cache paths. Food context alone is not cooking-retention evidence.
- outputs/supplemental_food_context_sources.csv: authoritative ChEBI descriptions through PubChem, supplementing primary food-context references.
- outputs/interaction_evidence_source_audit.csv and study_registry.csv: unique PMID publication ledger. Repeated records/endpoints are not independent publications or trials.
- outputs/correction_notice_audit.csv: complete eugenol correction notice inspected; affiliation only. Not counted as a new interaction publication.
- outputs/warning_resolution_ledger.csv: all inherited entries retained with exact requested status vocabulary. No new inherited scientific issue claimed resolved; the prior resolved Crossref item is history. Old 150-row aspiration is not applicable to V6.
- outputs/evidence_change_log.csv and registry_change_log.csv: all additions; no inherited correction, merge or removal.
- outputs/all_record_review_audit.csv and inherited_audits/: prior extraction details retained, not presented as fresh full-text review.
- audit/: executed baseline/V6 validation, mutation results, deterministic rebuild, preservation and final SHA-256 manifest.
- sources/: exact primary MED metadata/abstracts, Crossref responses, PubChem identity responses, capped discovery results, selected open XML and access-error records. XML availability alone does not imply full-text claim verification.
- inherited_sources/: unchanged source bytes supporting inherited interaction and processing records, retaining their original Stage B relative paths.

## Source paths and portable use

The inherited evidence Source_Cache field remains Stage B relative for exact V5 preservation. In the original project, resolve as `stageB / Source_Cache`. In an extracted package, resolve new rows as `release_directory / sources / pmid_{PMID}.json`; resolve inherited rows as `release_directory / inherited_sources / Source_Cache`. Processing audit paths are resolved explicitly in processing_source_resolution.csv. Input snapshots allow an offline rebuild without changing V5.

## Reproduction

Python 3 with the standard library is sufficient for CSV builds and validation; ReportLab and pypdf are needed only to regenerate the report. Run commands from this release directory:

```text
python -B build.py
python -B validate.py
python -B report.py
python -B package.py
```

`build.py` deterministically rebuilds tables from immutable inputs and cached primary sources. Existing input snapshots are never overwritten. `validate.py` additionally checks the original frozen project paths and hashes; that preservation check intentionally requires the original project. In a portable extracted archive, the embedded baseline validation results document the historical checks, while `checks()` can validate the tables independently. `baseline.py` reruns the historical V5 suite using its original inputs and redirects only the two report writes into V6; it must only be run in the original project before any expansion. Do not rerun it to replace the frozen initial baseline audit.

`collect.py`, `targeted.py`, `exact.py` and `supplement.py` document public retrieval calls. Cached responses are reused. Searches: 24 broad title discovery queries plus 24 pre-2021 targeted primary title queries, first 100 results each. Search hit counts are not screened-study counts. screening_log.csv explicitly labels unreviewed results. Exact primary lookups, food-context references and correction notices extend discovery; PMIDs selected for evidence are in curation.py. The two initially broad catechin queries are not stereoisomer-specific searches; exact study attribution determines admission.

`package.py` archives inherited source closure and audits, writes a SHA-256 manifest, creates the ZIP and verifies every archived manifest entry. To regenerate the package's inherited source copies, the original Stage B project is required. Portable readers already have those copies.

## Evidence boundaries

Human cells/microsomes are in vitro, not human PK. Uncontrolled human before/after studies are human PK, not controlled clinical trials. Thymol partial synergy, catechin/epicatechin nulls, thymoquinone model dependence and reverse rifampin-to-glycyrrhizin direction are explicit. Missing quantities remain missing; no source ambiguities are silently resolved. No Stage A model changes, Stage C exposure estimation, Stage D scoring or clinical decision tool was produced.
