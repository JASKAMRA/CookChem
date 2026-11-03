# Phase 4 evidence layer — proposed scope

**Status: PROPOSED, not previously approved.** A search of the current Stage C top-level documentation and directories found no formal Phase 4/Stage D specification or Phase 4 implementation. Existing downstream boundaries are specified by the Phase 3 architecture: Phase 1B provides food/compound identity and quantitative food records; Phase 2 provides cooking-retention evidence; Phase 3 calculates intake estimates and does not perform clinical interpretation.

## Proposed purpose

Maintain a versioned, source-traceable research evidence registry for evidence that contextualizes compound exposure beyond food composition and cooking retention. The first category is human pharmacokinetics and food-matrix context. Future categories may include occurrence, bioavailability, metabolism, dose-response, and toxicology only after they receive explicit review rules. Phase 4 is not a clinical decision or risk-classification stage.

## Boundaries and dependencies

- Phase 1B-v1.3.1 is the read-only source of mapped compound and food identifiers. Identity-complete mapping is not equivalent to quantitative eligibility.
- Phase2-v0.3.0 is the read-only source of cooking evidence. Phase 4 does not duplicate or reinterpret its retention records.
- Stage B interaction records remain exclusively in the Stage B registry; this registry must not duplicate them.
- Phase 3 may eventually request eligible Phase 4 contextual records through a read-only selector. It must not use human PK records as a food concentration, retention factor, or direct recipe-dose multiplier.
- A valid source claim can remain non-applicable to a specific calculation. Identity and applicability are independent gates.

## Evidence states and release rules

Source registration, extraction, unit/denominator checks, identity review, applicability review, quality review, and acceptance are separate states. Only a human-reviewed record with a resolved identity and applicable conditions is eligible for downstream contextual display. No record in the initial package is accepted for calculation. Abstract-only extraction is retained with its narrower limitations. Missing values remain null; qualitative conclusions never become numeric estimates.

The initial package is a workflow demonstration with one primary human study registered and one abstract-level record. It is **IN_PROGRESS**, not a comprehensive literature review and not an accepted clinical evidence base.

## Proposed evidence categories

`human_pharmacokinetics`, `food_matrix_bioavailability`, `food_compound_occurrence`, `mechanistic_metabolism`, `dose_response`, `toxicology_safety`, and `clinical_outcomes`. Categories do not imply evidence strength or calculation applicability. Each record also stores study type and measured/derived/qualitative result type.

## Review workflow

1. Register a stable source identifier and bibliographic fields.
2. Extract only claims supported by the cited source section and preserve source access level.
3. Check units, dose, route, denominator, population/model, and outcome definition.
4. Assess identity match separately from applicability (food matrix, preparation, route, dose, population, and conditions).
5. Assign quality and review status; independent human review is required before acceptance.
6. Validate cross-references and schema, create a versioned package and checksum manifest.

The workflow explicitly keeps extraction pending until a reviewer records a decision and rationale. Automated/LLM extraction is not self-accepting.
