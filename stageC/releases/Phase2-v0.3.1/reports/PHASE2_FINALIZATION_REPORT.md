# Phase 2 finalization report — Phase2-v0.3.1

## Decision

**COMPLETE_WITH_DOCUMENTED_LIMITATIONS.** The fixed Phase 2 scope was reviewed and validated. Completion means the bounded evidence review and software validation are complete; it does not mean every retention candidate is numerically usable. No cooked-concentration estimates met the required identity, matrix, conditions, basis, unit, and yield/mass-balance checks. The output remains zero rows by design.

## Fixed observed-pair scope

- 117 observed cooking pairs preserved: 33 turmeric and 84 pumpkin-leaf pairs; 24 analytes.
- 117/117 ratios independently recomputed from reported group means; all source-audit error-code fields are empty.
- The turmeric table-unit label was corrected from “mg/g fresh rhizome” to the source wording “mg/g plant material”. Fresh rhizome is the starting material; cooked-sample denominator and mass yield remain unavailable. No numeric values changed.
- Ratios remain apparent concentration ratios, not total analyte-mass retention.

## Retention evidence decisions

- 63/63 source-condition candidates reviewed: {'PENDING_MATRIX_COMPATIBILITY': 33, 'PENDING_SOURCE_BASIS': 30}. No candidate was accepted for numerical use.
- 22/22 food × evidence combinations finalized: {'PENDING_MATRIX_COMPATIBILITY': 11, 'PENDING_SOURCE_BASIS': 10, 'QUALITATIVE_ONLY': 1}.
- 584/584 Phase1B records received an applicability decision: {'NO_LINKED_RETENTION_EVIDENCE': 569, 'PENDING_MATRIX_COMPATIBILITY': 1, 'PENDING_SOURCE_BASIS_AND_MATRIX_COMPATIBILITY': 10, 'QUALITATIVE_ONLY': 4}.
- 197/197 identity-crosswalk rows reviewed: {'NO_STAGEB_CID_MATCH': 127, 'NO_CID': 5, 'ACCEPTED_STRICT_MATCH': 19, 'PENDING_STRUCTURE_EQUIVALENCE_REVIEW': 27, 'ACCEPTED_MANUAL_MATCH_WITH_CID_WARNING': 1, 'NEEDS_MANUAL_SOURCE_ADJUDICATION': 9, 'PENDING_NAME_AND_STRUCTURE_REVIEW': 9}. Twenty existing strict/manual matches remain usable; 177 remain no-match, pending, or manual-review outcomes. The Curcumin CID discrepancy remains visible.
- Phase2 cooked concentration output: 0 estimates. No unsupported retention factor, cooked mass, moisture correction, yield, or uncertainty was generated.

## Provenance and limits

The release depends on Phase1B-v1.3.2 with exact manifest SHA-256 `df3a95ae0957b68a89e38098c0824877196aa74ef7dd92573e6ab1f37e39b9b5`. The Stage A model was not accessed or run; model readiness is not required for this Phase 2 evidence closeout. Stage B remains a read-only dependency. Two historical test logs referenced by v0.2.0 were unavailable; exact paths and reasons are listed in `RELEASE_MANIFEST.json`.

Unresolved scientific issues are explicitly retained: turmeric analytical denominator/moisture bridge and cooked yield; turmeric+tamarind versus turmeric-only matrix compatibility; pepper source state/moisture basis; qualitative-only green-tea evidence; and unresolved cross-stage chemical identity/structure cases. These are limitations, not failed validation.
