# CookRisk application readiness — Stage C Phase 6

**Status: REQUIREMENTS DRAFT — NOT A PRODUCTION APPLICATION**  
API contract: [`API_CONTRACT_DRAFT.json`](API_CONTRACT_DRAFT.json)

## Stage C workflows

1. **Choose food and compound.** Search by the exact food-record and compound identifiers. Show the source food name, matrix, reported concentration and unit, normalized value and unit (if present), analytical/source notes, mapping rationale, and unresolved identity state. Do not silently select a fuzzy match.
2. **Build a recipe.** Capture ingredient quantity and unit, serving fraction, consumed fraction, food state, and preparation operations. Preserve the entered value and the normalized value with the conversion method. Keep unavailable mass, volume, or density fields visibly missing.
3. **Describe cooking.** Capture method, time, temperature, equipment, liquid/oil handling, and measured raw/cooked mass or volume where available. Show whether evidence satisfies the Phase 2 matrix and condition requirements. If no compatible accepted retention record exists, return a blocked cooked estimate with exact missing gates; never substitute a raw value as a cooked prediction.
4. **Review the result.** Show raw-reference concentration, cooked estimate only when supported, consumed amount and units, interval type, all input records, release IDs and hashes, warnings, missing inputs, and calculation method. Distinguish source-reported bounds, analytical variability, literature ranges, scenario bounds, prediction uncertainty, and unknown uncertainty. No probability distribution is implied by a range.
5. **Export.** Generate a provenance-complete JSON record and a human-readable report. Tabular CSV is an optional companion, not a replacement for source IDs, units, bounds, uncertainty class, or provenance.

## Stage D workflows

1. Select one Stage C estimate and one Stage B Evidence_ID. Display both records independently, including exact compound IDs, source release/hash, and study context.
2. Present the study's dose text verbatim beside dietary exposure values. Keep experimental dose and experimental concentration as separate typed fields. Do not convert or compare dimensions unless a qualified reviewer documents a valid basis.
3. Ask a reviewer to adjudicate the six comparability gates with a source/reference note: compound identity, route, dose units and basis, time window, population/model, and preparation/matrix.
4. Show **PENDING**, **REJECTED**, or **READY_FOR_REVIEW**. The last state means only that all listed gates were explicitly marked true; a human scientific review remains necessary. Display “No clinical interpretation performed.”
5. Export the assessment with the original evidence fields, review decisions, rationale, reviewer reference, and provenance. Never show a clinical significance badge or patient-specific medication advice.

## Display and data-handling requirements

- Render `null`, empty source text, and unavailable measurements as **not reported** or **not assessed**, never as zero.
- Preserve positive, negative, null, conflicting, ambiguous, and absent evidence as distinct states.
- Display source title, locator, DOI/PMID/URL, source record ID, study design, model/population, dose text, outcome text, source limitations, and review state.
- Show the source release and SHA-256 near every derived result. Exports must retain the exact Stage B Evidence_ID/Compound_ID and Stage C estimate/release identifiers.
- Identify synthetic or illustrative values on every screen and export. Synthetic examples must never be included in scientific-data searches by default.
- Never aggregate incompatible matrices or measurement bases without an explicit rejection or unresolved gate.
- Exports must be deterministic for identical inputs and contract versions. Include generation timestamp, application/build version, schema version, dependency lock reference, and canonical input hash when an implementation exists.

## Export formats

- **JSON (required):** machine-readable record, schema version, exact values/units, nulls, bounds and uncertainty classifications, warnings, calculation method, source identifiers, release/hash chain, and review state.
- **CSV (optional):** one row per ingredient/compound estimate or evidence comparison; separate low/high/unit columns; include record IDs, status, uncertainty class, and provenance keys. Never place different units in one numeric column.
- **PDF/HTML (optional):** readable summary with inputs, calculations, units, uncertainty/missingness, source citations, release hashes, warnings, and explicit limitations. Do not create a “risk score” section.

## Production UI prerequisites

1. Complete the Phase 2 scientific and deployment acceptance checklist, including an approved, hash-verified model package and a resolved target/denominator definition. No Stage A inference is authorized by this document.
2. Complete Phase 4 uncertainty-source coverage and Phase 5 benchmark comparability criteria; publish no external-validation claim until real matched data have been compared.
3. Add authentication, authorization, audit logging, privacy review, input validation, immutable export storage, dependency/security review, operational monitoring, and accessibility review.
4. Freeze and publish API schemas and test client/server compatibility. The included OpenAPI draft is a design aid only; it has no running service or production guarantee.

