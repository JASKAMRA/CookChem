# Data dictionary

The CSV headers are authoritative for serialized files; JSON Schemas in `../schemas/` describe core structures. Empty cells mean missing or not supplied, never zero.

## Stage B snapshot

The snapshot contains the 9 allowlisted Stage B tables named in `data/stage_b_snapshot/import_manifest.json`. Original column names, IDs, identifiers, status fields, and missing cells are preserved. The manifest stores source and copied-file SHA-256 hashes, row counts, schemas, import time, and release identity.

## Food composition

`data/food_composition/food_composition.csv` stores one compound concentration observation per food record. It keeps `reported_concentration` and `reported_unit` separate from `normalized_concentration` and `normalized_unit`; supported mass-basis observations normalize to `mg/kg`, while volume-basis observations normalize to `mg/L`. No density-based conversion is inferred. Food identity and part, cultivar, geography, raw/processed state, compound identity, moisture basis, analytical/extraction methods, sample size, LOD/LOQ, source citation/database IDs, source class and verification, and uncertainty/extraction notes are represented as columns. Optional unknowns remain blank.

## Mapping

`data/compound_food_mapping/compound_food_mapping.csv` records mapping ID, Stage B compound ID, food record ID, candidates, method/basis, status, rationale, source, source-verification state, quantitative availability, and warnings. Name-only unverified aliases remain candidates.

## Exposure output

Each estimate retains original input quantities and concentration, normalized concentration, initial amount, per-serving amount, consumed amount, status, input source IDs, Stage B release reference, warning IDs, assumptions, timestamp, software version, and nested reconstruction provenance. Aggregates identify their input estimate IDs and explicit period.
