# Evidence schema

One row is a distinct study/compound/drug/evidence context. Blank means not extracted or not available, never zero or no interaction.

- **Evidence_ID**: Stable evidence-record key.
- **Compound**: Source-extracted compound; use alongside preparation, evidence type and limitations.
- **Compound_ID**: Original CookRisk molecular group key; no groups merged.
- **Drug**: Source-extracted drug; use alongside preparation, evidence type and limitations.
- **Interaction_Effect**: Source-extracted interaction effect; use alongside preparation, evidence type and limitations.
- **Mechanism**: Source-extracted mechanism; use alongside preparation, evidence type and limitations.
- **Evidence_Type**: Source-extracted evidence type; use alongside preparation, evidence type and limitations.
- **Evidence_Level**: Preparation specificity (compound, extract, food preparation), not quality rank.
- **Direction**: Source-extracted direction; use alongside preparation, evidence type and limitations.
- **Quantitative_Outcome**: Reported units, ratios, assay constants or statistical intervals; affected entity must be read.
- **Dose**: Source-extracted dose; use alongside preparation, evidence type and limitations.
- **Population**: Source-extracted population; use alongside preparation, evidence type and limitations.
- **Study_Design**: Source-extracted study design; use alongside preparation, evidence type and limitations.
- **Source_Title**: Source-extracted source title; use alongside preparation, evidence type and limitations.
- **Authors**: Source-extracted authors; use alongside preparation, evidence type and limitations.
- **Year**: Source-extracted year; use alongside preparation, evidence type and limitations.
- **DOI**: Source-extracted doi; use alongside preparation, evidence type and limitations.
- **PMID**: Source-extracted pmid; use alongside preparation, evidence type and limitations.
- **Source_Type**: Source-extracted source type; use alongside preparation, evidence type and limitations.
- **Limitations**: Source-extracted limitations; use alongside preparation, evidence type and limitations.
- **Confidence**: Descriptive support/generalizability assessment, not a risk score.
- **Notes**: Source-extracted notes; use alongside preparation, evidence type and limitations.
- **Study_ID**: Primary PMID grouping key.
- **Source_URL**: Source-extracted source url; use alongside preparation, evidence type and limitations.
- **Source_Cache**: Cache path relative to stageB root.
- **Source_Locator**: Source-extracted source locator; use alongside preparation, evidence type and limitations.
- **Preparation**: Source-extracted preparation; use alongside preparation, evidence type and limitations.
- **Co_Compounds**: Source-extracted co compounds; use alongside preparation, evidence type and limitations.
- **Affected_Entity**: Source-extracted affected entity; use alongside preparation, evidence type and limitations.
- **Perpetrator**: Source-extracted perpetrator; use alongside preparation, evidence type and limitations.
- **Outcome**: Source-extracted outcome; use alongside preparation, evidence type and limitations.
- **Conflict_Group**: Context/regimen divergence synthesis key; blank does not prove consistency.
- **Identity_Status**: Source-extracted identity status; use alongside preparation, evidence type and limitations.
- **Release_Origin**: Initial evidence versus new expansion.
- **Clinical_Extrapolation**: Guard against automatic clinical inference.
- **CookRisk_Exposure_Link**: Identity scope and remaining source constraints for later linkage.