# Data dictionary

The Phase 1B v1.3.0 snapshot contains 584 food-composition rows and 584 compound-food mappings. See the accompanying CSV headers and `stageC/schemas/` for their field definitions. The 143-compound StageB_V20_20261103 registry contains 130 identity-complete and 13 identity-pending compounds.

Phase 2 data are developed at repository root under `stageC/phase2/data/`. `stagea_stageb_identity_crosswalk.csv` marks strict CID/name/canonical-SMILES matches separately from conflicts and candidates. `observed_retention_evidence.csv` preserves source-reported loss, derived complementary retention intervals where numeric, and limitations. These records do not become food-composition measurements.
