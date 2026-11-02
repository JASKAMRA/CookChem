# Stage B V13 continuation checkpoint

## Verified complete

- StageB_Final integrity contract, count discrepancy, five checksum dispositions, deterministic manifest and checksum mutation tests.
- V13 versioned copy preserving all 119 baseline compounds and 286 evidence rows.
- Controlled Batch 1: three ginkgolic-acid homologues and vanillic acid reviewed; four admitted with in-vitro-only limitations; C13:0 null result retained.
- Sinapinic acid CID 1549091 held because it is the cis-(Z) entity while the primary assay source does not specify isomer geometry; inherited record remains intact with V13-W02.
- V13 registry now has 123 unique compounds, 290 evidence records, 57 warnings. Structural validator 16/16 passed with zero errors; mutation checks detected 12/12 defects; Stage B unit suite 39/39 passed. Canonical manifest and clean-copy exact verification passed.

## Remaining work

1. Conduct candidate screening for Batch 2 from existing Stage B priorities and primary papers; deduplicate against the 123-compound registry and the held sinapinic entry. Do not use Stage C food-composition data as interaction evidence.
2. For each proposed candidate, verify exact identity (PubChem CID, InChIKey, InChI, structure, relevant stereochemistry), primary evidence, assay context, outcomes and food/supplement context before deciding. Preserve null and negative results.
3. Ingest Batch 2 only after its identity and source review passes; update all dependent Stage B registries, warning ledger, study evidence-ID lists, provenance, tests and manifest. Run focused tests and validator before opening Batch 3.
4. Repeat this gate for Batches 3–5. The target is 160; the remaining arithmetic gap is 37, not a screened or justified scientific shortfall. Report fewer additions only after candidate review supports that decision.
5. After the final batch, compare all inherited StageB_Final records with V13, run the full Stage B suite, mutation checks and a fresh clean-copy exact manifest verification. Update the release readiness honestly.

No commit or push has been made. Stage A and Stage C have not been executed or modified.
