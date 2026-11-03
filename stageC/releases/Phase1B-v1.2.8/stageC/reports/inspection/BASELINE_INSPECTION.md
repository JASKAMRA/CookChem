# Stage C baseline inspection

- Repository: `C:\Users\dakshant\Desktop\CookChem`.
- Authoritative Stage B release: `stageB/release/StageB_Final`; readiness `READY_WITH_WARNINGS`.
- Release manifest: 708 entries; connector verification: 0 mismatches. Snapshot allowlist: 9 CSVs, listed in `data/stage_b_snapshot/import_manifest.json`.
- Counts: 119 compounds, 119 identity audit rows, 119 food-context rows, 286 interaction evidence, 153 bibliography, 55 warnings, 76 source audits, 286 claim-support rows, 14 source-register rows.
- IDs: all 119 Compound_ID values preserved. Evidence_ID/Study_ID fields remain in the imported evidence table. Exact schemas and IDs are retained in `baseline_inspection.json` and the import manifest.
- Inherited limits: 19 pending identity reviews, 105 incomplete occurrence reviews, 17 supplement/medicinal contexts, 13 high numeric/unit flags, source audit coverage 76/286. Stage B has no quantitative food-composition data; three retention records are separate.
- Runtime: Python 3.14.7; no pytest in the Stage B virtual environment. Stage C uses standard-library runtime and unittest.
- Baseline Stage C tests before current fixes: 40 passed. Stage B release data are connected read-only; no Stage A/B files were modified by Stage C work.

The JSON baseline contains compound IDs, actual source columns, detailed warning counts and known limitations.
