# Stage C compatibility assessment

## Decision

**Compatible for controlled integration of identity, evidence, bibliography, and provenance metadata. Stage B is not a food-composition or dietary-exposure dataset.** Keep all verification and warning fields; do not use interaction outcomes as measured food concentrations.

## Safe Stage B files and fields to ingest

| File | Safe fields/keys | Conditions |
|---|---|---|
| `data/compound_registry.csv` | `Compound_ID`, canonical name, aliases, PubChem CID, SMILES, InChI, InChIKey, identity status/source, food context, provenance status | Unique stable IDs and all listed identity fields are present. Preserve status; 19 entries need manual chemical review. |
| `identity/identity_structure_audit.csv` | `Compound_ID`, returned/registry InChIKey, exact-key status, review status, notes and source | Audit table only; not blanket chemical adjudication. |
| `provenance/food_context_audit.csv` | compound ID, context, class, review status, source | Context only. 105 inherited occurrence reviews remain incomplete; 14 targeted review records. Not a concentration table. |
| `data/interaction_evidence.csv` | Evidence ID, compound ID, Study_ID, PMID/DOI, evidence class, outcome, source URL/locator, verification and limitations | Literature drug-interaction evidence. Keep type and verification fields. Not nutrition data. |
| `data/publication_bibliography.csv`; `data/study_registry.csv` | PMID/DOI, Study_ID, publication metadata and evidence links | Preserve study-level distinctions; publication IDs do not prove cohort independence. |
| `provenance/source_audit.csv`; `provenance/claim_support_and_verification.csv` | evidence ID, locator, verification status, limitations | Claim support covers 286/286; separate source audit covers 76/286. Preserve missing audit links. |
| `data/warning_ledger.csv` | warning ID, affected record, status/action and limitations | Preserve all 55 release warning rows. The 313 validator warnings are separately reported. |
| `data/cooking_retention_evidence.csv` | processing ID, molecular ID, food, conditions, retention result/source | Separate cooking-retention domain; three rows are not raw-food concentrations or universal retention factors. |

## Coverage and unresolved issues

- **Compound registry:** 119 unique stable IDs; aliases are present for 119/119. PubChem CID, SMILES, InChI, InChIKey, identity source, and identity status are present for all.
- **Identity review:** 100 marked complete; 19 still pending manual chemical review. All registry IDs match identity-audit IDs.
- **Food context:** 119 records; 105 retain inherited occurrence-review gaps; 17 are supplement/medicinal-botanical.
- **Evidence/provenance:** 286 unique evidence IDs; 286 claim-support rows; 76 source-audit evidence IDs.
- **Bibliography:** 153 bibliography rows and 153 study rows; 151 distinct nonblank evidence PMIDs. Evidence outcomes are free text; there is no normalized numeric-outcome/unit field.
- **Raw-food concentrations:** no raw-food concentration dataset is present. The 90 blank outcomes and 13 unit-review flags concern interaction evidence. Stage C must obtain food concentrations from an independently verified source.
- The release provides a data dictionary and structural validator, but no packaged machine-readable JSON Schema files.
- **Coverage target:** 119 anchors are present; the release handoff notes a target of 150, leaving a 31-anchor gap.

## Conditions for Stage C

1. Join on Compound_ID, Evidence_ID, and Study_ID exactly as recorded.
2. Preserve identity status, source verification, evidence class, food-context review, limitations, and warning fields.
3. Calculate dietary exposure only from separately verified raw-food composition data with explicit analyte, food state, units, and provenance.
4. Keep supplements/medicinal botanical context separate from ordinary-food occurrence.
5. Keep interaction evidence, cooking-retention findings, and food-composition measurements in separate data domains.
