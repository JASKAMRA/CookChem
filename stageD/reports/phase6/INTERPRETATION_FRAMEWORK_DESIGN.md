# Stage D Phase 6 — Nonclinical interpretation framework design

**Status:** Decision rules hardened and traceable; still a nonclinical research framework with no expert-approved policy.

## Purpose and limits

This module classifies the state of evidence review for a research record. It preserves evidence strength, mechanism, assay context, outcome polarity, dietary-exposure availability, comparability, uncertainty, conflicts, human relevance, and expert-review state as separate fields. Each assessment includes an ordered decision trace: every checked rule up to the first match, the matched rule, and its rationale. The output schema is additive version 1.1.0; input cases remain version 1.0.0. It does not calculate a numerical score, estimate patient risk, issue medication advice, or infer clinical significance from an in vitro mechanism.

The contract requires stable source references. A dietary-exposure reference is required when exposure is marked available, and a comparability-review reference is required when expert-supported comparability is claimed. Such fields record submitted review state; software does not authenticate an expert or source.

## Source basis and design choices

The source principles below inform the separation of evidence dimensions. The CookRisk thresholds and category ordering that follow are conservative design choices for this research tool; they are **not** rules prescribed or endorsed by FDA or ICH.

| Source-derived principle | Framework design choice |
|---|---|
| ICH M12 (2024) describes in vitro work as a way to identify possible enzyme/transporter mechanisms and places clinical DDI evaluation after mechanistic evaluation when warranted. It treats translation and clinical management as later evidence steps. | Mechanistic evidence is a terminal category in this design: it cannot promote itself to a human or dietary relevance conclusion. Evidence type and experimental context remain separate. |
| ICH M12 (2024, section 6) defines clinical relevance in terms of safety, effectiveness, or tolerability concerns from concomitant use and says risk assessment considers exposure-response relationships. | “Research relevance supported” is permitted only after a documented expert assessment of human evidence, dietary exposure, comparability, and bounded uncertainty. The category expressly does not mean clinical relevance or risk. |
| FDA’s May 2026 food-effect guidance concerns orally administered drug products. It describes food effects on systemic drug exposure and says the implications are assessed using exposure-response and dosing context; study meal, population, timing, and formulation matter. | Dietary exposure, study context, and comparability are separate required dimensions. A record about a different preparation, dose basis, or population cannot be silently treated as comparable. |
| FDA’s May 2026 guidance also distinguishes formulation-specific in vitro evaluation from in vivo evidence for some drug-product vehicles. | In vitro evidence is retained as experimental evidence, but it is not treated as proof of a human food-drug interaction. |

### Primary and official sources

- ICH, *Drug Interaction Studies, M12*, final version adopted 21 May 2024, especially sections 1.4, 2, 3–4, and 6: [official ICH guideline PDF](https://database.ich.org/sites/default/files/ICH_M12_Step4_Guideline_2024_0521_0.pdf). FDA lists the final M12 guidance at [FDA M12 guidance page](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/m12-drug-interaction-studies).
- FDA, *Assessing the Effects of Food on Drugs in INDs and NDAs — Clinical Pharmacology Considerations*, final guidance, May 2026, especially sections II–IV and VI: [FDA guidance page](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/assessing-effects-food-drugs-inds-and-ndas-clinical-pharmacology-considerations) and [final PDF](https://www.fda.gov/media/121313/download).

These sources address investigational drug-drug studies and food effects on drug products. Neither is a direct validation standard for inferring interaction risk from food-compound measurements or Stage B records. The framework adapts only the general need to keep mechanism, measured exposure, study context, and clinical consequence distinct.

## Decision table

Rules are applied top to bottom. The first matching state is returned. The ordered trace records each check up to that match, with the failed checks explaining why higher-priority transitions did not apply. The exact input dimensions are copied into the output so that the category never hides missingness, source contradictions, or original polarity.

| Order | Rule ID | Category on match | Transition rule |
|---:|---|---|---|
| 1 | `KNOWN_CONFLICT` | `REQUIRES_EXPERT_REVIEW` | A source discrepancy, conflicting studies, or explicitly conflicting outcome is kept visible and routed for adjudication, even if another field is missing. |
| 2 | `NO_INTERPRETABLE_RESULT` | `INSUFFICIENT_EVIDENCE` | No evidence level or no interpretable outcome. Missing values remain unknown and are never converted to negative findings. |
| 3 | `UNRESOLVED_REVIEW_GATES` | `REQUIRES_EXPERT_REVIEW` | For interpretable evidence, conflict status is unassessed, outcome is unclear, source identity is unverified, source review is incomplete, or expert review is in progress. |
| 4 | `MECHANISM_ONLY` | `MECHANISTIC_EVIDENCE_ONLY` | Mechanism evidence alone cannot establish dietary-exposure relevance or a human outcome, even if other fields claim those conditions. |
| 5 | `EXPERT_DOES_NOT_SUPPORT_RESEARCH_RELEVANCE` | `EXPERIMENTAL_EVIDENCE` | A completed, documented expert decision against research relevance leaves the evidence and tested context visible. |
| 6 | `COMPARABILITY_PENDING` | `EXPOSURE_COMPARABILITY_PENDING` | Evidence exists, but exposure comparability is not assessed or remains pending. |
| 7 | `RESEARCH_RELEVANCE_REQUIREMENTS_MET` | `RESEARCH_RELEVANCE_SUPPORTED` | Positive human PK/clinical evidence; full-text review; verified identity; no unresolved conflict; expert-supported comparison and referenced dietary exposure; bounded uncertainty; and completed, documented expert support. This is a research status only. |
| 8 | `POSITIVE_HUMAN_UNCERTAINTY_UNBOUNDED` | `REQUIRES_EXPERT_REVIEW` | Positive human evidence has an asserted exposure comparison, but uncertainty is material, unquantified, or unassessed. |
| 9 | `EXPERIMENTAL_EVIDENCE_DEFAULT` | `EXPERIMENTAL_EVIDENCE` | Other interpretable evidence. Null and negative outcomes are scoped to their tested conditions; incompatible comparison does not become dietary relevance. |

An unknown conflict state does not mean “no conflict.” A declared conflict takes precedence over missing outcome. When no conflict is recorded but no evidence or interpretable outcome exists, the result is insufficient rather than negative. For interpretable evidence, unassessed conflict status blocks further interpretation. Null and negative findings remain visible alongside conflict status and are never generalized beyond their conditions.

## Implementation and verification

- `stageD/src/stage_d/interpretation.py` implements dependency-free input validation, ordered decision traces, explicit category transitions, and the machine-readable decision table. Completed expert reviews require a named reference, rationale, and an explicit support/non-support adjudication. A claimed expert-supported comparator requires referenced comparability and available dietary exposure.
- `stageD/schemas/risk_interpretation.schema.json` is Draft 2020-12. It accepts version 1.0.0 input cases and version 1.1.0 assessments, validates trace structure, fixes the nonclinical claim boundary, and rejects extra fields such as a risk score.
- `stageD/examples/phase6/synthetic_interpretation_cases.json` provides 13 explicitly synthetic cases covering all six categories, negative/null outcomes, missing results, unassessed conflicts, conflict precedence, and expert non-support. Synthetic expert adjudications exercise rules only; they are not actual reviews.
- `stageD/tests/test_interpretation.py` tests all categories, trace ordering, category transitions, mechanism-only non-promotion, known and unassessed conflicts, null/missing-data preservation, review and identity gates, expert approval boundaries, comparability/uncertainty gates, malformed combinations, and both input/output schema forms.

Focused verification: **13 tests passed, 0 failed, 0 skipped** when run with the workspace's pinned `jsonschema` development dependency. The earlier dependency-free run passed its behavioral tests but skipped the formal schema test because `jsonschema` was not on the default interpreter path. No real expert review, clinical outcome validation, or scientific correctness claim follows from those software tests.

This framework remains a design foundation. It has no expert-approved policy thresholds, no validation against external clinical outcomes, and no production or patient-facing use authorization.
