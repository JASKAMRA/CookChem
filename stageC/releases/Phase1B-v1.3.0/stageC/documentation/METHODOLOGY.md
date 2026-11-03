# Methodology

The Phase 1B v1.3.0 package reads the identity-adjudicated `StageB_V20_20261103` snapshot through the versioned Stage C connector. It preserves stable IDs, identity status, identifiers and provenance, then validates food records, mappings, units and snapshot hashes. The 584 source-backed food records and 584 mappings remain within the Phase 1 data domain.

Phase 1B coverage counts unique identity-complete compounds with accepted quantitative ordinary-food measurements. Current accepted coverage is 125/130. Held values, spikes, non-detects, medicinal-only records, identity-pending compounds, and unverified isomers do not count.

Phase 2 stores cooking-retention evidence separately from raw-food concentration. The initial interval helper only complements a source-reported loss range and applies it to a concentration if exact compound, food matrix, cooking conditions, and measurement basis are verified. The Phase 2 kickoff currently applies no retention interval to Phase 1B food values.
