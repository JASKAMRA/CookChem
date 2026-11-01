# CookRisk Stage B V7 - clean restart release

Release date: 15 October 2026. Target achieved: **60 distinct reference anchors**. Final status: **PASS_WITH_WARNINGS**.

## Restart handling

The interrupted `stageB/release_v7_20261014/` and its earlier `v6_suite_sandbox/` are preserved in place. No old V7 output table or successful test result was adopted as a completed clean-build output. The restart inventoried and hashed the interrupted files, parsed 354 CSV/JSON/XML/Python files without format errors, identified missing report/documentation/archive artifacts, and treated previous validation as stale relative to later script edits. Access-error JSON records are explicit retrieval failures, not corrupted files.

This separate directory was built from actual V6 inputs. V6's original release manifest was checked; the existing V6 suite was executed before and after expansion in `stageB/v6_suite_restart_20261015/`, an isolated newly created copy. All frozen prior project files, including V6 and the interrupted work, remain unchanged. The restart audits document the exact files and hashes. Reviewed code templates were reused only after inspection; primary MED records were refreshed independently and compared with the earlier cached bibliographic/abstract fields. Twenty-eight refreshed source snapshots had no relevant-field mismatch. All candidate claims were re-reviewed, and the selected full-text tables/methods were checked again.

## Verified results

| Metric | V6 | V7 |
|---|---:|---:|
| Reference anchors | 44 | 60 |
| Interaction evidence records | 147 | 189 |
| Distinct drug/probe labels | 71 | 87 |
| Primary publications (unique PMID) | 101 | 121 |
| Distinct nonempty DOI | 98 | 116 |
| Human PK records | 64 | 69 |
| Controlled clinical records | 2 | 4 |
| Animal records | 37 | 50 |
| In-vitro records | 44 | 66 |
| Numerical outcome records | 84 | 97 |
| Selected-full-text outcome review | 11 | 19 |
| Abstract outcome review | 74 | 112 |
| Metadata-only in latest outcome audit | 62 | 58 |
| Open warning entries / codes | 17 / 16 | 20 / 19 |

There were no discrepancies between recomputed V6 counts and its saved summary. V6 has no separate drug registry; its baseline drug count was derived directly from the evidence table. Drug/probe counts refer to distinct recorded labels, including the explicitly stereoselective S-warfarin assay, and are not a count of unique parent pharmaceutical ingredients.

Sixteen anchors and 42 records were added, covering 20 newly represented publications. New evidence consists of five human PK, two controlled clinical, thirteen animal and twenty-two in-vitro records. Of the 42 new records, six were verified against selected full-text passages and 36 against primary abstracts. Three records expand inherited berberine/luteolin coverage. Six inherited review scopes were upgraded without altering their evidence fields.

Review-level counts are conservative latest documented outcome-audit scopes assembled from V4/V5/V6 record audits, not a claim that all historical papers were newly re-extracted. The 58 remaining metadata-audit-only records retain historical extraction limitations; no new interaction claim is admitted from metadata alone or a secondary summary.

## Added anchors

Diosmetin; rutin; pterostilbene; ursolic acid; oleanolic acid; sesamin; nobiletin; tangeretin; ascorbic acid; folic acid; phylloquinone; vanillin; oleuropein; allyl isothiocyanate; zeaxanthin; lutein.

Selection rationales, food-source associations and primary experimental references are separate ledgers. Folic acid denotes the oxidized monoglutamate used in fortified foods/supplements, not total natural food folate. Ascorbic acid and folic acid are not linked to uncertain mixed master analyte groups. Phylloquinone is a vitamin K1 reference; its intravenous experiment is not a dietary intervention. Reference stereochemistry does not universally certify the exact study-tested purity or isomer.

The only shared-connectivity anchor pair is inherited (+)-catechin/(-)-epicatechin, with distinct stereochemical keys. New glycoside/aglycone or related-triterpene entries have independently distinct structures and experimental support; preparations, salts and aliases are not counted as new anchors.

## Search and source review

Fresh search date/cutoff: 15 October 2026. A 32-candidate pipeline spans several dietary chemical families. There were 64 capped queries, two per candidate: a broad primary title search and a historical pre-2021 search. Each retrieved at most 100 records; 4,805 occurrences were logged. Sixteen candidates were selected, fourteen deferred, and two nonspecific class/mixture names excluded. Unreviewed discoveries remain labelled `candidate_not_fully_screened`. No exhaustive systematic-review claim is made.

The source cache contains exact Europe PMC MED metadata/abstract snapshots, PubChem reference properties, Crossref results, available open XML and explicit access-error records. NIH ODS food-context sources were independently checked and their concise findings recorded. Full-text availability alone is not recorded as outcome verification. Five interaction publications lack a supplied DOI; their PMIDs remain valid references.

Primary abstract and selected full-text extraction is single-reviewer work. Numerical-token matching supplements manual endpoint/unit/arm review; it cannot replace that review. Claimed values remain source-reported, with no calculated clinical effects or exposure estimates. The folic-acid abstract writes “Twenty-one percent”; the source's wording is retained. Lutein Table 3 null-arm Cmax/AUC values preserve the reported units and precision.

## Important scientific distinctions

- Folic acid prevention of gingival overgrowth in children and treatment of established overgrowth in adults are different contexts; the latter trial's null is retained.
- Pterostilbene includes anticonvulsant nulls and bounded microsomal inhibition; the abstract's broad summary is not substituted for the full-text threshold.
- Sesamin's cited earlier 0.2 microM result is not attributed to the current 15.7/13.1 microM experiment.
- Non-SNEDDS lutein's warfarin null is retained; positive surfactant/formulation effects are not assigned to pure lutein.
- Vanillin's mouse tumor experiment and rat nephrotoxicity experiment are separate records, not independent publications.
- Oleuropein/doxorubicin arms use unequal doxorubicin doses; no equal-dose synergy magnitude is calculated.
- Historical apigenin/rutin attribution, apigenin table/prose discrepancies and daidzein/quercetin retention restrictions remain visible. Admission of rutin using a different isolated-compound experiment does not resolve the historical paclitaxel preparation ambiguity.

## Files

- `reports/CookRisk_StageB_v7_Report.pdf`: four-page report, comparison, new-anchor rationales and process flowchart.
- `reports/CookRisk_StageB_v7_Findings.md`: concise machine-readable-friendly findings summary.
- `outputs/compound_registry.csv`: 60 anchors; inherited identities/IDs retained.
- `outputs/stageB_food_drug_interactions_v7.csv`: preserved 36-column schema; all 147 V6 evidence rows identical; new IDs SB-0148 to SB-0189.
- `outputs/drug_probe_registry.csv`, `study_registry.csv`: drug/probe and unique-publication metadata.
- `outputs/selection_provenance_ledger.csv`, `food_context_source_audit.csv`, `candidate_selection.csv`: current decisions, food associations, exclusions and deferrals.
- `outputs/identity_structure_audit.csv`, `near_duplicate_identity_audit.csv`: reference identity and mapping scope. New SMILES are connectivity SMILES; reference InChI carries stereochemical information.
- `outputs/claim_support_and_outcome_audit.csv`, `all_record_review_audit.csv`: 42 new and six reverified claims, source passages/locations and per-record review scope.
- `outputs/evidence_change_log.csv`, `registry_change_log.csv`: additions, verification upgrades and derived registry evidence-count updates. No inherited scientific field was corrected, merged or removed.
- `outputs/cooking_retention_evidence.csv`, `processing_provenance_audit.csv`: inherited processing domain, preserved separately. No new coefficient or master-measurement certification.
- `outputs/inherited_quality_audit.csv`, `warning_resolution_ledger.csv`, `bibliographic_discrepancy_audit.csv`: inherited gaps, status history and adjudicated Crossref title differences.
- `outputs/search_log.csv`, `screening_log.csv`: reproducible bounded discovery and screening status.
- `audit/`: restart inventories, baseline counts, original V6 manifest verification, refreshed-source comparison, before/after V6 results, V7 validation/mutations, rebuild verification, report QA and final hashes.
- `inputs/`: immutable V6 table snapshots and reconstructed baseline review levels.
- `sources/`, `inherited_sources/`, `inherited_audits/`: exact current sources and preserved earlier source/audit closure.

## Executed validation

Fresh V7 result: **42/42 checks, zero errors; 10/10 mutation tests**. Critical mutations include duplicate IDs, broken references/source paths, wrong bibliography, inherited edits, missing selection, duplicate chemical keys, false study classification, relabelled nulls and invented numerical claims.

The existing V6 suite reported **90/90 checks and 20/20 mutation results** before and after the clean expansion. Its implementation freshly executes 37 checks and nine mutations, while incorporating 53 checks and eleven mutations saved in its older V5 audit. The latter are historical results, not newly executed V7 tests. Separate before/after reports preserve this distinction; they are not added together to inflate the V7 test count.

V7 checks include exact inherited preservation, unique IDs, structure consistency/near-duplicates, foreign keys, bibliography, DOI/PMID syntax, full-text article PMID identity, source-cache resolution, numerical tokens/units, study classification, negative/context-dependent results, separate evidence domains, provenance, change logs, correct counts and byte-identical rebuilding. Warnings remain: 20 entries across 19 codes. No fixed evidence-row quota was applied.

## Reproduction and portability

Python 3 and its standard library rebuild CSV outputs and run validation; ReportLab/pypdf are needed only for PDF regeneration. From this release directory:

```text
python -B build.py
python -B validate.py
python -B report.py
python -B package.py
```

`build.py` deterministically regenerates tables from immutable V6 input snapshots, manually re-reviewed curation and cached primary sources. It never overwrites an existing input snapshot. `validate.py` verifies outputs and compares original frozen project files; that last preservation check requires the original project path. For portable table validation, import `checks()` from validate.py and pass the evidence, registry and claim tables. The packaged executed audit retains the historical preservation result.

New evidence `Source_Cache` paths are Stage B relative, beginning `release_v7_20261015_clean/`. In the original project, resolve all evidence caches as `stageB / Source_Cache`. In an extracted archive, resolve new caches to `release_directory / sources / pmid_{PMID}.json`, and inherited caches to `release_directory / inherited_sources / Source_Cache`. Processing-source resolution is archived in `inherited_audits/v6/processing_source_resolution.csv`. Claim-ledger paths are directly relative to this release directory.

The existing before/after V6 suite runs were isolated copies, preserving V6. `restart_audit.py` documents the initial restart event; **do not rerun it over the frozen initial preservation manifest**. Source collector scripts can repeat online retrieval into a separate directory; current cached snapshots are reused by default. `package.py` gathers inherited closure from the original project, generates SHA-256 hashes and verifies every ZIP entry against the manifest. Portable readers already have the inherited closure. Report generation is independent of terminal TeX or Word installations.

The archive excludes rendering previews and Python bytecode. Stage A was neither modified nor re-evaluated. Stage C exposure estimation and Stage D risk scoring were not implemented. This is a literature evidence resource with explicit uncertainty, not a validated clinical decision tool.
