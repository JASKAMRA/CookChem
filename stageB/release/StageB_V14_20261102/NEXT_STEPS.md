# V14 continuation checkpoint

## Completed

- Verified V13 baseline: 123 unique compounds; 290 interaction records; 127 drug/probe rows; 153 bibliography and study rows; 57 warnings; canonical manifest 716/716.
- Preserved V13 as a historical checkpoint and created this separate V14 copy.
- Completed sequential candidate batches and recorded per-batch decisions/reports.
- Added five compounds (two curcuminoids, sinensetin, eupatorin, and Allura Red AC) with nine source-linked records. Retained a right-censored CYP2C9 result (`IC50 > 50 μM`) and a dose-dependent mouse result for Red 40 without translating either into human dietary risk.
- Updated candidate, identity, evidence, study, bibliography, probe, warning, and release metadata records.
- Added V14 structural/provenance checks and synthetic mutation checks.

## Current counts

- Compounds: 128 unique Compound_ID/InChIKey records; 32 below the numerical 160 target.
- Interaction evidence: 299 unique Evidence_IDs.
- Drug/probe labels: 128.
- Bibliography: 157 rows, 155 unique nonblank PMIDs.
- Study registry: 157 rows.
- Warning ledger: 61 rows (57 inherited, four V14 batch warnings).
- New V14 additions: four in-vitro compounds plus one food-color additive; eight in-vitro records plus one animal record.
- Readiness remains `PARTIAL_NOT_READY_FOR_160`.

## Batch record

| Batch | Accepted | New evidence | Decisions held | Gate |
|---|---|---:|---|---|
| 2 | Demethoxycurcumin; bisdemethoxycurcumin | 4 | none | PASS |
| 3 | Sinensetin | 2 | none | PASS |
| 4 | Eupatorin | 1 | none | PASS |
| 5 | Allura Red AC (FD&C Red No. 40) | 2 | GF-I-1, GF-I-4, Paradisin B, Imperatorin | PASS |

Batch 5 uses the primary paper's named inhibitor and mouse finding. Its numerical Ki was omitted because the exact supplementary table could not be directly retrieved and checked in this execution. The release does not treat that as a verified numeric value.

## Remaining candidate work

1. Resolve GF-I-1, GF-I-4, Paradisin B, and Imperatorin only after exact identity and primary-source linkage are available.
2. The V13 candidate log also has category-level priorities (xanthophylls, red-clover isoflavones, flavonoid aglycones, phytosterols). These are not compound admissions; identify exact entities and test claims before considering them.
3. The primary OATP2B1 food/additive inhibitor paper reports 24 validated inhibitors. Four additional named candidates surfaced in a secondary reproduction of its supplement (FD&C Yellow 6, FD&C Blue 1, FD&C Red 3, and neohesperidin dihydrochalcone). Do not ingest them until the primary SI table and each PubChem structure are directly checked. The supplementary Ki values were intentionally not copied into V14.
4. Continue deduplication against all 128 V14 identities, then form a new sequential batch plan. Do not infer clinical or ordinary-food effects from in-vitro screens, supplements, or mouse studies.
5. After further batches pass, run the complete Stage B suite, identity/provenance/reference audits, mutation checks, canonical manifest verification, and normalized clean-copy exact verification. Keep V13 unchanged and update this checkpoint.

## Checks already run

- V13 canonical manifest: PASS, 716/716 before continuation.
- Existing Stage B full suite: 39/39 passed after Batch 2.
- V14 full Stage B regression suite after Batch 5 and documentation updates: 45 passed, 0 failed, 0 skipped, 0 blocked.
- V14 structural/provenance validator after all four batches: PASS, 0 errors.
- V14 synthetic mutation assertions: 8/8 intended defects detected; V13 inherited mutation suite was previously reported 12/12.
- V14 batch gates: 4/4 PASS.
- V14 final manifest and exact clean-copy checks: run after the final manifest build; see `validation/V14_final_validation_report.json`.

No protected-stage work is included in this continuation. No Git operations were performed.
