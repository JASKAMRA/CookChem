# Stage B data dictionary and downstream interface

## Authoritative files

| File | Meaning |
|---|---|
| `data/compound_registry.csv` | One row per stable Compound_ID; identity, food-context, selection and record-count fields. |
| `data/interaction_evidence.csv` | One row per stable Evidence_ID; Compound_ID, Study_ID, PMID/DOI, evidence class, direction, outcome and source location. |
| `data/drug_probe_registry.csv` | Probe labels and their evidence-record counts; label identity is descriptive and not a prescribing recommendation. |
| `data/study_registry.csv` | Study_ID to publication and evidence-row relationship; one publication may have multiple rows and is not assumed to represent independent cohorts. |
| `data/publication_bibliography.csv` | PMID/DOI indexed publication metadata; PMID and DOI counts are separate measures. |
| `data/warning_ledger.csv` | Warnings and residual uncertainties; unresolved and inherited issues remain visible. |
| `data/cooking_retention_evidence.csv` | Stage A cooking/retention evidence kept separate from drug-interaction evidence. |

## Stable relationships

Use `Compound_ID`, `Evidence_ID`, `Study_ID`, PMID, and DOI as stored. Preserve IDs exactly. Join evidence to compounds by `Compound_ID`, to studies by `Study_ID`, and to publication metadata using PMID/DOI. Drug/probe labels are values in `drug_probe_registry.csv`; do not reinterpret them as clinical treatment recommendations.

Stage B is a literature evidence resource. It does not calculate dietary exposure, retained doses, or patient-specific clinical risk. In-vitro and animal findings are not demonstrated human clinical interactions. Verification status and warning limitations must travel with any downstream record. Descriptive fields and assay outcomes are suitable for evidence retrieval; they are not exposure estimates or risk scores.

## Evidence classes

- `Human pharmacokinetic`: pharmacokinetic measurements in human participants.
- `Controlled clinical`: controlled intervention in human participants.
- `Other human clinical`: human evidence not classified as pharmacokinetic or controlled clinical in this schema.
- `Animal`: nonhuman in-vivo evidence.
- `In vitro`: enzyme, cell, microsome, or transporter assay.

These classes describe study design and must not be collapsed into a single clinical-evidence category.

## Verification levels

Verification status describes how the source was checked; it is not a confidence score. Current values include `Full-text table verified`, `Abstract verified`, `Abstract verified; numeric/claim-level review limited to stated locator`, `Article abstract located; full extraction not completed`, `Partially verified`, and inherited V8 review status. The latter directs users to the inherited claim-level audit. Only two records are marked full-text/table verified in the V12 baseline. Unverified and abstract-only claims must remain identifiable downstream.

## Open audit flags

The warning ledger contains 55 entries. The final structural audit separately emitted 313 review flags: 210 evidence rows lack a separate source-audit row, 90 have a blank quantitative-outcome field, and 13 numeric outcome strings lack a readily identified unit/statistic. Claim-support rows exist for all 286 evidence IDs, but source-audit coverage is partial. These counts are audit flags, not extra entries in the warning ledger.
