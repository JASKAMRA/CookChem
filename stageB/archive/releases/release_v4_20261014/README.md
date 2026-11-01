# CookRisk Stage B v4

Start with reports/CookRisk_StageB_v4_Report.pdf. The main output is outputs/stageB_food_drug_interactions_v4.csv. There are 14 compounds, 73 records, 36 drugs/probes and 53 primary PMIDs. No additions/removals were forced. SB-0067 alone has nine documented field changes; all original 64 rows are unchanged. V3 and supplied inputs are immutable.

## Offline reproduction

Keep this incremental release at stageB/release_v4_20261014 in the supplied workspace. No Git repository is required. The actual supplied stageB/expansion_v3_20261014 and its source dependencies are required. Run with Python 3.11+:

```text
python stageB/release_v4_20261014/build.py
python stageB/release_v4_20261014/validate.py
python stageB/release_v4_20261014/report.py
python stageB/release_v4_20261014/package.py
```

Build and validation need the standard library; report.py needs reportlab and Windows Arial fonts. collect.py performs optional public online retrieval. It caches successful responses, preserves retrieval errors and does not supply evidence merely by downloading it. Do not refresh the preservation manifest to conceal changes. Validation calls the v3 validation function read-only; it does not invoke its writing main routine. Supplied v3 files are never rewritten.

## Schemas and provenance rules

The evidence CSV retains all 36 supplied columns and stable SB IDs. Blank means unavailable or unextracted, never zero. Evidence_Type is Human pharmacokinetic, Controlled clinical, Animal or In vitro. PMID-based Study_ID groups reports, not necessarily independent trials. Preparation, co-compounds, dose, population, endpoint, units, uncertainty and limitations remain source-specific. Mechanisms are proposed unless demonstrated in the relevant experiment. Do not pool incompatible endpoints or infer meal exposure or risk.

The compound registry retains stable IDs and aliases and adds v4 review fields. Selection sources and interaction references are separate. Original-nine selection dates remain unknown; release dates are not historical addition dates. V3 additions have dated decision records. Daidzein remains separate from glycosides; standalone quercetin remains separate from mixed total-flavonol observations. Processing publications are outside the interaction count and establish no automatic master retention links.

## Audits and source levels

record_source_review_audit.csv records all 73 review levels: 62 metadata-only inherited outcomes, eight abstracts, two selected inherited full-text checks and one selected full-text re-extraction. claim_support_and_outcome_audit.csv preserves exact claims and source locators. evidence_change_log.csv documents every changed field. warning_resolution_ledger.csv retains all v3 warning entries plus the new Cmax discrepancy. Eight distinct open codes cover nine entries. PASS_WITH_WARNINGS is technical consistency, not scientific certainty.

The all-14 provenance audit, original-nine reference map, processing provenance audit and quercetin mixed-group source inventory document unresolved identity/source issues. The full text of the apigenin/rutin paclitaxel article was unavailable; the publisher preview does not resolve individual attribution. Retrieved processing studies use hydrolysis or conjugate/total-analyte measures; they do not validate native parent retention.

## Future changes

Create a new version folder. Reserve explicit new stable IDs only when identity and primary evidence justify them. Record dated selection decisions independently from interaction evidence. Save exact acquisition queries/URLs and locators. Preserve source units, CI, p-values and null findings; missing values stay missing. Compare abstract and tables, flag conflicting prose and distinguish human from preclinical contexts. Append a field-level change ledger rather than silently altering inherited records. Add a mutation test only for a demonstrated validation gap. Run actual validation and report counts from final files. Keep inherited outcome review scope explicit. Do not implement Stage A retraining, outlier analysis, Stage C or Stage D here.
