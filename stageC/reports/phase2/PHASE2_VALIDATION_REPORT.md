# Phase 2 Validation Report — 2026-11-03

## Source-pair audit

`python3 stageC/scripts/audit_phase2_source_pairs.py` compares all 117 existing pairs to values transcribed from the original turmeric Table 1 and pumpkin-leaf Tables 2–3. It validates raw/cooked means and SDs, replicate count, treatment/table unit, and independently recalculates each ratio. Result: **117/117 primary-table numeric comparisons pass**. Thirty-three turmeric records carry `VERIFIED_WITH_BASIS_LIMITATION`, because the legacy unit field over-specifies the cooked denominator; 84 pumpkin rows are `VERIFIED_AGAINST_PRIMARY_TABLE`.

Maximum difference between the stored rounded ratio percentage and independent ratio percentage: 0.004822 percentage points. The ratio formula is cooked group mean / raw group mean; no total-mass retention or Phase1B cooked outputs are inferred.

## Tests

- Source audit regression test: 1 passed.
- Phase 2 focused suite: **15 passed, 0 failed**.
- Full Stage C suite: **114 total, 111 passed, 3 failed**. Failures are legacy Phase 1B register/checkpoint expected counts (coverage 100 vs 101 twice; source rows 62 vs 63). No Phase 2 test fails; no expected count was changed.

## Release and copy integrity

Phase2-v0.1.0: 19/19 manifest files verified; zero mismatches. Phase1B-v1.3.0: 1,321/1,321 SHA-256 entries and byte counts verified. A disposable clean copy regenerated v0.1.0 outputs without overwriting and generated the source-audit CSV byte-for-byte identically. The copy is an isolated Phase 2 fixture, not a complete repository clone.

## Scientific validation

Twenty turmeric candidates, one pepper/piperine candidate with three distinct scenarios, and one EGCG combination remain unresolved/rejected as shown in the record-level compatibility matrix. Accepted cooked concentrations: **0**. No unsupported moisture conversion, qualitative-to-numeric translation, or model inference was used.
