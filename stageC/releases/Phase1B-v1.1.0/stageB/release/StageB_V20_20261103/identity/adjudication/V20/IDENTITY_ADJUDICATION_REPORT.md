# Stage B V20 identity adjudication — 2026-11-03

## Scope and lineage

This versioned identity-only successor is copied from the exact-manifest-verified `StageB_V19_20261103`, which descends from the preserved Stage B finalized lineage. `StageB_FINALIZED` and V19 remain unchanged. No interaction evidence, warnings, drug/probe rows, study rows, bibliography rows, selection history, or source-audit claims were edited.

## Results

- Registry compounds: 143 (all original IDs preserved).
- Complete identity anchors before review: 107.
- Outcomes across all pending identities: 23 resolved, 11 partially resolved, 2 manual-review-required, 0 unresolved.
- Identity-complete after review: 130/143.
- Still pending: 13/143.
- Existing food-composition measurements and mappings were not changed. Identity resolution does not count as food coverage.

## Method and limits

All 36 V19 pending rows were individually matched by Compound_ID to the V20 decision ledger. Resolved outcomes require a unique PubChem CID record whose preferred name/synonyms, IUPAC nomenclature and stored formula/InChI/InChIKey support a discrete, sufficiently specified registry identity. Positional isomers and stereoisomers were kept distinct. A current PubChem InChIKey discrepancy for tartrazine was corrected in this successor from `UJMBCXLDXJUMFB-UHFFFAOYSA-K` to `UJMBCXLDXJUMFB-GLCFPVLVSA-K`; the archived InChI text was preserved. Tartrazine remains pending because the azo geometry is unspecified.

This was a documented desk review of authoritative database structure records, not an independent RDKit/Open Babel graph parse or expert chemist sign-off. It adjudicates registry anchors only; it does not revise study-level interaction claims. Partially resolved/manual/unresolved entries remain ineligible for identity-complete coverage.

## Decision package

See `identity/adjudication/V20/identity_adjudication_decisions.csv` for all 36 decisions, prior and proposed identifiers, source references, structural checks, rationale, confidence, reviewer status, and follow-up.

## Release gate note

The Stage C Phase 1 v1.3.0 package has a pre-existing artifact checksum mismatch. Under the project release gate, no Phase 1 connector successor or food-record promotion is made in this continuation until that package discrepancy is resolved. This Stage B identity successor does not claim Phase 1B food coverage completion.
