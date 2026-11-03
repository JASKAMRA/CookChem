# Methodology

Stage B is loaded from `stageB/release/StageB_FINALIZED` only after every entry in its exact-byte SHA-256 manifest verifies. The connector checks the registry and identity audit have the same 143 unique IDs and matching canonical names, PubChem CIDs, SMILES, InChIs, and InChIKeys. Stage C copies a fixed nine-file allowlist into the new versioned snapshot and detects later source or snapshot changes. Older snapshots remain historical.

Food composition is ingested from source-supported CSV records. No value is created from qualitative occurrence, an interaction result, a cooking-retention record, a supplement dose, or a missing cell. Source-reported values and units are preserved. Supported mass-per-mass units normalize to mg/kg and supported mass-per-volume units normalize to mg/L with decimal arithmetic; no density is assumed to convert between them, and food basis/state are not inferred.

`ordinary food` and `food ingredient` are distinct explicit food-use classifications, and both can support concentration × mass arithmetic when source, mapping, state, and basis checks pass. An ingredient estimate is only the analyte amount represented by the stated ingredient mass; recipe dilution, processing, cooking retention, and actual intake are not inferred. Existing classifications and records remain valid.

Mapping requires exact Stage B ID, exact canonical name, matching PubChem CID or full InChIKey, or a synonym with a supplied verification source. Conflicting identifiers are ambiguous. Any Stage B identity-pending record remains pending until a documented manual decision is supplied. No fuzzy chemical-name matching is used.

For an eligible record, `initial amount (mg) = concentration (mg/kg) × ingredient mass (kg)`. Per-serving amount uses serving mass when supplied (otherwise ingredient mass); estimated consumed amount multiplies it by an explicitly supplied fraction in [0,1]. Compatible contributions can be grouped only by compound, explicit period, food state, and moisture basis. Duplicate estimate IDs are rejected to prevent double counting. Phase 1 has no cooking adjustment.
