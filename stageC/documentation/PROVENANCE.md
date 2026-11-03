# Provenance and reproducibility

Stage B import manifests record the `StageB_FINALIZED` release ID, exact source-manifest checksum, original paths, snapshot paths, per-file SHA-256, record counts, schemas, 143-compound count, and UTC import time. Source changes are detectable and do not rewrite the snapshot. Imported records retain their original IDs and values.

Food ingestion manifests record input/output paths and hashes, timestamp, row counts, and source-classification counts. Exposure results retain source concentration, source unit, normalized value/unit, conversion factor, input masses, formula, food and mapping IDs, citation/database identifiers, Stage B manifest checksum, warning identifiers, software version, and calculation timestamp. Estimate IDs are deterministic from the input record when not supplied; timestamps are run metadata. Synthetic test data are not project measurements.
