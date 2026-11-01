# CookRisk Stage B v5

Open reports/CookRisk_StageB_v5_Report.pdf first. The release contains 26 compounds, 118 evidence records, 58 drugs/probes and 80 unique primary PMIDs. Added 12 compounds, 45 records and 27 primary reports; no inherited evidence changes or removals. All 73 v4 records remain identical. Historical release-origin and review-date fields are intentionally retained on inherited records.

## Offline reproduction

Keep this incremental folder at stageB/release_v5_20261014 in the supplied workspace. No remote repository is needed. Existing stageB inputs, v2/v3/v4 registries and cached sources are required. Use Python 3.11+ (the bundled runtime is suitable):

```text
python stageB/release_v5_20261014/build.py
python stageB/release_v5_20261014/verify_rebuild.py
python stageB/release_v5_20261014/validate.py
python stageB/release_v5_20261014/report.py
python stageB/release_v5_20261014/package.py
```

Core scripts require the standard library. Report generation needs reportlab and Windows Arial; packaging PDF verification needs pypdf. Do not refresh audit/preservation_manifest.json to conceal changes. Offline rebuild uses saved snapshots and is tested byte-for-byte. Actual v4 validation functions are invoked read-only for baseline compatibility; their writing main routines are never invoked. Validation preserves eight prior mutation scenarios and adds three identified expansion risks.

Optional online acquisition sequence: collect.py, targeted.py, exact.py, supplement.py, food_sources.py. These cache public PubChem, MED/Crossref and accessible XML sources; caches can include failures and are not silently replaced. Run acquisition only in a new versioned workspace. Search logs retain exact queries/limits/URLs and distinguish incomplete screening. Exploratory web queries are listed separately. Source download availability alone is not scientific review.

## Schemas and review levels

The interaction CSV retains all 36 original fields. Stable IDs SB-0001 through SB-0073 are inherited; SB-0074 through SB-0118 are the fixed-order v5 additions. Do not reorder the curation list for future additions; reserve explicit IDs in a new version. Evidence_Type is Human pharmacokinetic, Controlled clinical, Animal or In vitro. Chrysin's uncontrolled pilot is Human pharmacokinetic, not Controlled clinical. Study_ID groups unique primary PMIDs and is not proof of independent trial participants.

Selection sources document a dated decision independently from interaction citations. Original-nine historical selection sources and dates remain unresolved or only retrospectively described. Newly selected compounds have current dated rationale and primary support. Seven new compounds reuse verified inventory identities; five use standalone external parent IDs. Naringenin CID 932 is a generic parent/racemate representation; natural (S)-naringenin CID 439246 is not silently substituted. No uncertain myricetin or naringenin master group is repaired by assigning literature. Naringenin is distinct from naringin. Existing daidzein/glycoside and quercetin/total-flavonol restrictions remain.

new_evidence_records.csv and claim_support_and_outcome_audit.csv cover 45 additions: 37 primary abstract extractions and eight selected full-text reviews. inherited_v4_claim_support.csv retains earlier claims; all_record_review_audit.csv covers all 118 rows with explicit review inheritance. Source locators state actual abstract or selected-section scope. Literal numeric checks complement manual review and do not prove meaning. No complete full-paper review or independent second reviewer is claimed.

Missing values are unknown or unextracted, never zero. No synergy is not no interaction. Nonsignificant means are not established effect directions. Metabolic ratios, inhibition constants, combination indices and AUC are different endpoints. CI in the fisetin record is a combination index, not a confidence interval. Reverse interactions retain the compound as Affected_Entity. Drug/probe counts include experimental transport substrates, not only prescribed medicines.

Processing and food-composition sources are separate from interaction studies and cannot establish native parent retention or meal exposure. Inherited food labels are not newly certified measurements. Supplement, injected animal and cell concentrations must not become clinical risk thresholds. No Stage A, outlier, Stage C or Stage D work is included.

## File map

- compound_registry.csv: 26 selected compounds; candidate_selection.csv: 16 decisions (12 selected, four deferred, zero rejected).
- stageB_food_drug_interactions_v5.csv: 118 rows; new_evidence_records.csv: 45 additions.
- study_registry.csv: 80 primary PMIDs; interaction_evidence_source_audit.csv: verification status.
- compound_selection_provenance_audit.csv and selection_sources.csv: decision lineage; original_nine_interaction_reference_map.csv: experimental citations, not historical selection triggers.
- identity_structure_audit.csv: stable identity keys and restrictions; processing_provenance_audit.csv: separate food/processing context.
- search_log.csv, exact_source_log.csv, food_processing_source_log.csv and screening_log.csv: capped discovery and adjudication states. Unreviewed candidates are not excluded.
- claim_support_and_outcome_audit.csv, inherited_v4_claim_support.csv and all_record_review_audit.csv: new versus inherited source scopes.
- context_comparison_audit.csv: differing drug/preparation/species contexts, not automatic direct contradictions.
- evidence_change_log.csv and registry_change_log.csv: every new evidence ID and registry field change.
- warning_resolution_ledger.csv: inherited unresolved limitations plus new issues; prior resolved warnings remain as history.
- file_inventory.csv and baseline_key_file_inventory.csv: actual paths, row counts, source fields and inspection status.
- audit/verified_v4_baseline.json, validation_report.json, mutation_tests.json, rebuild_verification.json and preservation_manifest.json: machine-readable checks.
- sources: public response snapshots; curation.py: explicit manual extraction; build.py/validate.py: reproducible release logic; reports: PDF and Markdown.

## Future additions

Create the next version without overwriting v5. Verify identity and food relevance, record a dated selection decision, cache exact primary identifiers and source locators, and preserve original experimental units and context. Require relevant drug/probe endpoints; exclude predictions and unverified review claims. Separate doses/endpoints only when genuinely different compound/drug/context experiments justify a record, and share primary Study_ID. Record nulls and incompatible contexts without pooling. Keep changes auditable, run the complete validation and mutation suite, verify deterministic rebuilding, and report actual counts plus unresolved limitations. The unmet 150-record target does not justify duplicate or speculative rows.
