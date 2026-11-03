# Phase 4 evidence layer — proposed scope

**Status: PROPOSED, not previously approved.** No formal Phase 4/Stage D specification was present in the current project documentation. This proposal continues the documented boundaries: Phase 1B provides source-verified food/compound records, Phase 2 provides cooking evidence, and Phase 3 calculates exposure without clinical interpretation.

## Purpose and boundaries

Maintain a versioned, source-traceable research evidence registry that can later contextualize exposure. The initial category is human pharmacokinetics and food-matrix context. Candidate future categories include food/compound occurrence, bioavailability, metabolism, cooking/preparation, dose-response, toxicology, and clinical outcomes. A category does not imply calculation or clinical applicability.

- Phase1B-v1.3.1 remains the read-only compound/food identity dependency. Identity-complete does not imply quantitative eligibility.
- Phase2-v0.3.0 remains the read-only cooking evidence dependency. Phase 4 does not duplicate or reinterpret it.
- Stage B interaction evidence remains exclusively in its own registry.
- Human plasma PK values are not food concentration, cooking retention, or direct recipe-dose multipliers.
- Evidence validity, identity match, applicability, and review acceptance remain separate states.

## Workflow and evidence states

Source registration, extraction, unit/denominator verification, identity assessment, applicability assessment, quality review, and acceptance are separately recorded. Automated extraction cannot accept evidence. Only independently human-reviewed records with adjudicated identity and applicability can enter a context-only downstream view. Quantitative PK access requires a separate future contract; the current Phase 3 adapter intentionally exposes no quantitative PK values.

## Current proposed scope demonstration

The working v0.1.1 registry contains one primary human study with publisher full text and Table 1 reviewed: five condition-level Cmax rows plus a separate qualitative statistical comparison. All six remain pending review, name-only in identity, context-limited, and excluded downstream. The source's participant denominator discrepancy is preserved. Phase4-v0.1.0 remains the immutable abstract-only predecessor.

This is an initial workflow demonstration, not a complete literature review, accepted scientific evidence base, or clinical interpretation stage.
