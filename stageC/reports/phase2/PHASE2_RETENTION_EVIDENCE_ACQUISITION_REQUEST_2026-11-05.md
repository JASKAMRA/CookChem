# Phase 2 Retention Evidence Acquisition and Authorization Request

**Status: OPEN — no new evidence supplied or approved.**

This request is based on the Stage C release `Phase2-v0.3.1` only. It does not alter the accepted 117 observed cooking-pair records, authorize Stage A inference, or authorize any cooked-concentration calculation. The present `cooked_concentration_estimates.csv` contains no accepted estimates.

## Current disposition

The release records 22 food-compound-retention combinations:

| Disposition | Count | Meaning |
|---|---:|---|
| `PENDING_SOURCE_BASIS` | 10 | Turmeric-only source matrix broadly matches, but the concentration denominator/basis bridge is unresolved. |
| `PENDING_MATRIX_COMPATIBILITY` | 11 | Ten turmeric-with-tamarind combinations do not match the turmeric-only concentration matrix; the pepper combination also lacks established state/basis compatibility. |
| `QUALITATIVE_ONLY` | 1 | The green-tea source provides qualitative catechin behavior, not a quantitative EGCG retention value. |

The release summary reports 117 observed cooking pairs, 24 analytes, 63 retention candidates reviewed, 22 compatibility combinations, zero retention-based cooked-concentration outputs, and no model inference. These are distinct evidence sets; the observed pairs are not concentration estimates for the 22 combinations below.

## Unresolved numeric combinations

All 20 turmeric combinations below refer to compound `MOL-16B10569D6F0625E` (curcumin), Phase 1B concentration records for commercial turmeric powder, and the cited cooking study `10.1016/j.jfca.2006.10.002`.

| Phase 1B food record | Retention record | Combination ID | Current blocker |
|---|---|---|---|
| `PAUDEL2025-002-Co-T-1-CURCUMIN` | `P2-RET-002` | `PAUDEL2025-002-Co-T-1-CURCUMIN__P2-RET-002` | As-analyzed powder versus lyophilized cooked-sample basis; no verified moisture/denominator bridge, selected condition-level value, or yield. |
| `PAUDEL2025-002-Co-T-2-CURCUMIN` | `P2-RET-002` | `PAUDEL2025-002-Co-T-2-CURCUMIN__P2-RET-002` | Same basis, condition-selection, and yield gaps. |
| `PAUDEL2025-002-Co-T-3-CURCUMIN` | `P2-RET-002` | `PAUDEL2025-002-Co-T-3-CURCUMIN__P2-RET-002` | Same basis, condition-selection, and yield gaps. |
| `PAUDEL2025-002-Co-T-4-CURCUMIN` | `P2-RET-002` | `PAUDEL2025-002-Co-T-4-CURCUMIN__P2-RET-002` | Same basis, condition-selection, and yield gaps. |
| `PAUDEL2025-002-Co-T-5-CURCUMIN` | `P2-RET-002` | `PAUDEL2025-002-Co-T-5-CURCUMIN__P2-RET-002` | Same basis, condition-selection, and yield gaps. |
| `PAUDEL2025-002-Co-T-6-CURCUMIN` | `P2-RET-002` | `PAUDEL2025-002-Co-T-6-CURCUMIN__P2-RET-002` | Same basis, condition-selection, and yield gaps. |
| `PAUDEL2025-002-Co-T-7-CURCUMIN` | `P2-RET-002` | `PAUDEL2025-002-Co-T-7-CURCUMIN__P2-RET-002` | Same basis, condition-selection, and yield gaps. |
| `PAUDEL2025-002-Co-T-8-CURCUMIN` | `P2-RET-002` | `PAUDEL2025-002-Co-T-8-CURCUMIN__P2-RET-002` | Same basis, condition-selection, and yield gaps. |
| `PAUDEL2025-002-Co-T-9-CURCUMIN` | `P2-RET-002` | `PAUDEL2025-002-Co-T-9-CURCUMIN__P2-RET-002` | Same basis, condition-selection, and yield gaps. |
| `PAUDEL2025-002-Co-T-10-CURCUMIN` | `P2-RET-002` | `PAUDEL2025-002-Co-T-10-CURCUMIN__P2-RET-002` | Same basis, condition-selection, and yield gaps. |
| `PAUDEL2025-002-Co-T-1-CURCUMIN` | `P2-RET-003` | `PAUDEL2025-002-Co-T-1-CURCUMIN__P2-RET-003` | Evidence is turmeric cooked with tamarind; the concentration is turmeric-only. Do not transfer across matrices. Basis, condition selection, and yield are also unresolved. |
| `PAUDEL2025-002-Co-T-2-CURCUMIN` | `P2-RET-003` | `PAUDEL2025-002-Co-T-2-CURCUMIN__P2-RET-003` | Same matrix mismatch and unresolved basis/condition/yield. |
| `PAUDEL2025-002-Co-T-3-CURCUMIN` | `P2-RET-003` | `PAUDEL2025-002-Co-T-3-CURCUMIN__P2-RET-003` | Same matrix mismatch and unresolved basis/condition/yield. |
| `PAUDEL2025-002-Co-T-4-CURCUMIN` | `P2-RET-003` | `PAUDEL2025-002-Co-T-4-CURCUMIN__P2-RET-003` | Same matrix mismatch and unresolved basis/condition/yield. |
| `PAUDEL2025-002-Co-T-5-CURCUMIN` | `P2-RET-003` | `PAUDEL2025-002-Co-T-5-CURCUMIN__P2-RET-003` | Same matrix mismatch and unresolved basis/condition/yield. |
| `PAUDEL2025-002-Co-T-6-CURCUMIN` | `P2-RET-003` | `PAUDEL2025-002-Co-T-6-CURCUMIN__P2-RET-003` | Same matrix mismatch and unresolved basis/condition/yield. |
| `PAUDEL2025-002-Co-T-7-CURCUMIN` | `P2-RET-003` | `PAUDEL2025-002-Co-T-7-CURCUMIN__P2-RET-003` | Same matrix mismatch and unresolved basis/condition/yield. |
| `PAUDEL2025-002-Co-T-8-CURCUMIN` | `P2-RET-003` | `PAUDEL2025-002-Co-T-8-CURCUMIN__P2-RET-003` | Same matrix mismatch and unresolved basis/condition/yield. |
| `PAUDEL2025-002-Co-T-9-CURCUMIN` | `P2-RET-003` | `PAUDEL2025-002-Co-T-9-CURCUMIN__P2-RET-003` | Same matrix mismatch and unresolved basis/condition/yield. |
| `PAUDEL2025-002-Co-T-10-CURCUMIN` | `P2-RET-003` | `PAUDEL2025-002-Co-T-10-CURCUMIN__P2-RET-003` | Same matrix mismatch and unresolved basis/condition/yield. |
| `KOREA-PEPPER-2021-PIPERINE` | `P2-RET-001` | `KOREA-PEPPER-2021-PIPERINE__P2-RET-001` | Retail sample is as-received homogenized material; study used locally purchased powdered pepper in aqueous suspension. Moisture/denominator bridge, state equivalence, selected condition-level factor, and yield are unresolved. |

The tea record `USDA-FLAV33-NDB99069-EGCG__P2-RET-004` is explicitly `QUALITATIVE_ONLY`, not a pending numeric combination. A future numeric use requires a source providing quantitative EGCG-specific results under a compatible, documented infusion protocol.

## Evidence requested from source custodians

For the turmeric-only and turmeric-with-tamarind source conditions, provide the primary paper and any supplement/thesis containing the exact table, page, sample description, and condition-level values for:

1. Each separate condition: boiling for 10 minutes, boiling for 20 minutes, and pressure cooking for 10 minutes at 15 psi; do not provide only a pooled envelope. Include temperature, pressure definition, water-to-spice ratio, additives, sample collection, replicates, mean and uncertainty.
2. Raw and cooked concentration values, exact units, analyte identity/assay, and the numerator and denominator for each value.
3. Whether the raw commercial powders are as-received, as-analyzed, moisture-corrected, or dry-weight; moisture measurements and any stated conversion factor for the exact samples.
4. Whether cooked samples were lyophilized before measurement, and how the reported mg/g denominator relates to original spice mass, recovered cooked material, and dry solids.
5. Matched raw/cooked mass or cooking yield, if measured; otherwise an explicit statement that yield was not reported. Identify whether cooking liquid was retained, discarded, or included in the assay.
6. For `P2-RET-003`, confirm that the reported sample included tamarind and provide its amount and preparation details. This evidence cannot make a turmeric-only concentration matrix interchangeable with the turmeric-tamarind retention matrix; any proposed transfer needs a separately authorized, scientifically justified matrix decision.

For black pepper `P2-RET-001`, provide the same denominator, moisture, cooked-sample preparation, condition-level raw/cooked values, replicate/uncertainty, and yield/liquid-handling evidence. Confirm whether the retail record's sample state can be matched to the source's powdered pepper; do not assume that the mass-unit conversion `mg/kg` to `mg/g` resolves state or basis compatibility.

For any supplied evidence, retain the source file, stable locator, acquisition date, exact extract/transcription, and SHA-256. Do not replace or normalize the original source. A qualified reviewer must independently verify each transcription and record an explicit disposition for each affected combination.

## Required owner decisions

The project/scientific owner is requested to:

1. Authorize or decline acquisition and use of the cited primary paper's complete methods, tables, supplementary material, and any relevant thesis/lab records for this Stage C Phase 2 review.
2. Identify the authorized custodian who can provide the exact source extracts and any original sample-basis/yield records; if none exist, record those fields as unavailable.
3. Confirm the qualified scientific reviewer responsible for source transcription and compatibility adjudication. The owner must not substitute approval for qualified scientific review.
4. Confirm whether ordinary-food exposure calculations may include these spice/ingredient records. Current matrix rows label the turmeric records `food ingredient` and set `ordinary_dietary_eligible=false`; do not silently reclassify them.
5. Authorize no calculation until every applicable identity, matrix, state, condition, unit, measurement-basis, denominator, retention-quality, and yield requirement is either supported by evidence or explicitly shown not to be needed by the scientifically defined output.

## Semantics that must remain distinct

- **True/total-mass retention:** fraction of initial analyte mass remaining after cooking. To infer it from concentrations, matched raw/cooked concentrations and compatible measured mass or volume yield are required; a source may instead directly report the total-mass quantity with its method defined.
- **Concentration ratio:** cooked concentration divided by raw concentration. It can exceed 1 because water or other matrix mass changed, and does not by itself establish analyte mass retention.
- **Concentration-retention factor:** a source-defined factor applied to a compatible concentration basis. It is usable only when the source's numerator/denominator, matrix, food state, condition, units, and measurement basis match the target calculation.
- **Cooking yield:** cooked edible mass divided by initial raw edible mass (or a clearly defined equivalent volume yield). It is a measured input, not a synonym for retention and not derivable from an analyte concentration ratio.

The existing source records `P2-RET-001` to `P2-RET-003` contain reported loss intervals and their arithmetic complements, not a validated universal concentration factor or total-mass result for the Phase 1B records. `P2-RET-004` is qualitative only. No estimate is authorized by this request.

## Acceptance of any future evidence

For each combination, attach a row-level adjudication with source locator, quoted/transcribed raw and cooked values, units, measurement bases, exact cooking condition, matrix and state match, retention semantic, yield/liquid handling, uncertainty, reviewer identity/qualification, reviewer date, decision, and unresolved limitations. Recompute only in a separately authorized, versioned task after independent review. Preserve all current Phase 2 release files and the 117-observation boundary.
