# CookRisk Stage B release v3 20261014

Open reports/CookRisk_StageB_v3_Expansion_Report.pdf first. The main table is outputs/stageB_food_drug_interactions_v3.csv. Original supplied files are not overwritten. This is Stage B evidence only.

## What changed

Added five compounds and nine evidence rows, SB-0065 through SB-0073. All 64 baseline rows and all 36 original columns are preserved. The result has 73 rows, 14 anchors, 36 drugs/probes and 53 primary PMIDs. Human records: 55 PK/probe plus two controlled clinical; animal 10; in vitro six. One apigenin/rutin record remains provisional for preparation attribution.

Selection sources are in selection_sources.csv and the compound registry; interaction sources are in study_registry.csv. An interaction paper is not evidence of historical selection. For the original five anchors, original selection sources remain unresolved; the four v2 additions have a documented general rationale but not a specific historical primary-paper trigger. Unknown original dates stay blank.

## Rebuild and validate offline

Keep this folder at stageB/expansion_v3_20261014 in the supplied workspace. The scripts do not require Git or the original remote repository. They discover their paths relative to their own saved location. They read the available stageB/inputs, stageB/outputs, stageB/expansion_v2 and inherited source caches. The package is an incremental release, not a replacement for the supplied workspace. Python 3.11+ standard library suffices for core build and validation; document search additionally needs pypdf and python-docx; PDF generation needs reportlab and Arial fonts on Windows.

Run in order from the workspace root:

```text
python stageB/expansion_v3_20261014/scripts/audit_selection_documents.py
python stageB/expansion_v3_20261014/scripts/build_release.py
python stageB/expansion_v3_20261014/scripts/validate_release.py
python stageB/expansion_v3_20261014/scripts/test_validation.py
python stageB/expansion_v3_20261014/scripts/document_release.py
```

Use the supplied Python runtime if python is not on PATH. collect_sources.py is optional online collection, not needed for offline reproduction. Existing cache files, including recorded failures, are not silently replaced. A new retrieval attempt should use a new dated cache or explicitly versioned collection script. The supplied-file hash manifest is created only once and is never refreshed to conceal changes.

## Add a compound or evidence record

1. Create the next versioned output folder; preserve supplied releases. Reuse a verified stable compound ID where chemically appropriate. For a genuinely new canonical chemical, reserve an explicit ID and record PubChem CID, synonyms, structure, InChIKey and identity source. Do not merge salt, stereoisomer, glycoside or mixed-analyte groups by name alone.
2. Record a dated selection decision, dietary relevance, human/preclinical evidence availability, retention coverage, identity confidence and feasibility. Add each supporting paper and its actual role to the selection-source ledger. Leave unavailable historical dates and references blank with an explicit unresolved status.
3. Save exact search queries, search date, caps, results and source responses. Record incomplete screening honestly. Cache primary MED metadata/abstract or verified full text and an exact locator. Check bibliographic metadata and correction/retraction notices where available.
4. Append curated records to curation.py with primary identifiers, preparation, co-interventions, doses, population, drug endpoint, direction, numerical units, uncertainty, null/conflict context and limitations. Update the registry specifications. Reserve the next unused SB ID; never renumber inherited rows. This builder assigns SB-0065 onward in fixed list order; do not reorder existing entries. For later releases, use an explicit ID map rather than inserting into this list.
5. For numerical claims, preserve reported endpoint, units, p-values and intervals; add source support. Do not convert metabolic ratios into AUC or animal/cell findings into human outcomes. Retain no-effect results and context differences. Missing values are not zero. Mechanisms must be labelled proposed unless directly supported.
6. Rebuild and run validation plus mutation tests. Resolve errors. Retain provenance gaps and reviewed source limitations as warnings; never relabel PASS_WITH_WARNINGS as complete source adjudication. Review new source claims manually because literal token checks do not establish scientific meaning. Update documentation using generated counts.

## Important limitations

Standalone quercetin CHEM-PUBCHEM-5280343 is intentionally not linked to the mixed master group MOL-FDB10E6B0C4171D1. Daidzein CHEM-PUBCHEM-5281708 has no exact master aglycone group; daidzin and acetyldaidzin are different compounds. Three other added compounds reuse inherited exact mappings. Original-nine selection history, apigenin/rutin group preparation, some abstract doses/sample sizes, inherited food provenance and unavailable Crossref lookups remain unresolved. Baseline numerical outcomes were retained, not independently re-extracted. No complete cross-paper trial independence audit, systematic review, second-reviewer adjudication, Stage A training, Stage C or Stage D work is claimed.

## File map

- outputs/file_inventory.csv: full metadata and row-count inventory; inventory_key_files.csv: short key-file inventory.
- outputs/selection_document_search.csv: text search of supplied narrative documents.
- outputs/compound_registry.csv, selection_sources.csv and compound_selection_provenance_audit.csv: identity, current decisions and unresolved history.
- outputs/original_nine_interaction_reference_map.csv: retained references, explicitly separate from selection history.
- outputs/stageB_food_drug_interactions_v3.csv and new_evidence_records.csv: full and incremental evidence.
- outputs/study_registry.csv and interaction_evidence_source_audit.csv: primary references and verification scope.
- outputs/claim_support_ledger.csv and outcome_validation_audit.csv: source support and extraction limitations.
- outputs/literature_search_log.csv, source_screening_log.csv and inventory_candidate_decisions.csv: search and candidate decisions.
- outputs/conflict_synthesis.csv, processing_selection_context.csv and release_summary.json: context and actual totals.
- audit/validation_report.json and validation_self_tests.json: reproducible checks.
- audit/supplied_file_manifest.json: unchanged source-file hashes. sources: raw public snapshots. scripts: collection, extraction, build, validation and report generation.
