# V15 continuation checkpoint

## Completed

- Verified V13 at 123 compounds / 290 evidence records and V14 at 128 / 299 in the preceding continuation; V15 was created as a separate copy of V14.
- V15 Batch 6 added four compounds and seven source-linked records from the 2025 food-additive transporter paper (PMID 40773056).
- V15 Batch 7 added four compounds and four source-linked Caco-2 null findings from Figure 3 of the same primary paper.
- Retained null outcomes as categorical text; did not substitute zero for unreported effect sizes.
- Added identity audit, provenance, candidate decisions, warning record, per-batch reviews, batch gates, V15 validator, and focused tests.
- V14 inherited compound, evidence, and warning records pass exact row-preservation checks in `scripts/validate_v15.py`.

## Current verified counts

- Compounds: 136 unique Compound_ID and InChIKey records; 24 below the numerical target of 160.
- Evidence: 310 unique Evidence_ID records (299 inherited from V14 plus 11 V15 records).
- Drug/probe rows: 133.
- Bibliography: 158 rows; 156 unique nonblank PMIDs.
- Studies: 158 rows.
- Warning ledger: 64 rows (63 inherited from V14 plus one Batch 7 limitation warning).
- V15 additions: eight compounds and 11 records (Batch 6: 4/7; Batch 7: 4/4).
- Readiness: `PARTIAL_NOT_READY_FOR_160`.

## Batch history

| Batch | Accepted | New evidence | Gate |
|---|---|---:|---|
| 2 (V14) | Demethoxycurcumin; bisdemethoxycurcumin | 4 | PASS |
| 3 (V14) | Sinensetin | 2 | PASS |
| 4 (V14) | Eupatorin | 1 | PASS |
| 5 (V14) | Allura Red AC | 2 | PASS |
| 6 (V15) | all-trans-beta-carotene; BHT; dodecyl gallate; octyl gallate | 7 | PASS |
| 7 (V15) | Brilliant Blue FCF; azorubine/carmoisine; neohesperidin dihydrochalcone; tartrazine | 4 | PASS |

The user's supplied V13→V15 prompt described batches 2–5; those had already been completed and recorded in V14 before this continuation. V15 therefore did not repeat or rewrite them.

## Checks run in this continuation

- Batch 7 focused V15 tests: 5 passed, 0 failed, 0 skipped, 0 blocked.
- V15 structural/provenance validator: PASS, 0 errors; 136 compounds, 310 evidence records; inherited V14 records unchanged.
- Full Stage B root regression suite: 45 passed, 0 failed, 0 skipped, 0 blocked.
- V15 exact-byte manifest: PASS, 736/736; zero missing, unexpected, mismatched, or raw-byte-mismatched entries.
- V15 clean-copy exact verification: PASS, 736/736; the temporary verification copy was removed after checking.
- V14 historical manifest: exact-byte PASS, 725/725.
- V13 historical manifest: canonical PASS, 716/716; raw exact mode differs on 650 text files due to line endings, while canonicalized hashes all match. No historical manifest was rebuilt.
- RDKit is unavailable in the local Python environment; structures were cross-checked against PubChem CID, name, InChI, InChIKey, and SMILES, but no local structure-parser validation is claimed.
- Final V15 validation details are recorded in `validation/V15_final_validation_report.json`.

## Research holds and next work

Do not admit compounds merely to reach 160. The following require new primary-source/identity review before promotion:

1. Resolve GF-I-1, GF-I-4, Paradisin B, and Imperatorin only if exact tested entities and source-linked food–drug evidence can be established.
2. The 2020 OATP2B1 additive study's original supplementary rows for FD&C Yellow 6, FD&C Blue 1, FD&C Red 3, and NHDC need direct source-table verification before transferring any Ki values. Batch 7 NHDC's Figure 3 null permeability finding is a separate endpoint and must not be represented as that Ki evidence.
3. Sunset Yellow FCF remains held because retrieved PubChem records gave ambiguous CIDs/salt forms; resolve the tested form before registering it.
4. Other candidate additions need direct primary evidence and exact identities. Existing priority categories and food occurrence alone are not admission evidence.
5. If more scientifically qualified compounds are found, continue in a new controlled batch, test it, update this checkpoint, and only then consider readiness.

## Resume procedure

1. Work only in `stageB/release/StageB_V15_20261102` (or create a new versioned release). Keep V13, V14, Stage A, and Stage C untouched.
2. Recheck the latest `release_metadata.json`, candidate decisions, evidence/provenance rows, and V15 manifest before edits; do not repeat Batch 6 or 7.
3. Verify held sources and exact identity forms. Record unsupported candidates as held rather than creating placeholder rows.
4. Ingest one batch at a time, update all linked tables, add focused tests, run the V15 validator and full Stage B regression, then verify manifest integrity.
5. Report the final unique registry count honestly. The current 24-compound gap is not yet a scientifically justified ceiling.
