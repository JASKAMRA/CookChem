# Stage C Phase 1B verification report

## Active repository

- Full Stage C `unittest` suite: **61 passed, 0 failed, 0 blocked**.
- Focused mapping, food-composition, unit-conversion, exposure-engine, and integration tests: **48 passed**; both CLI portability tests also passed (50/50 across focused modules).
- Phase 1 validation: **PASS**, 511 food-composition rows, 511 mappings, 119 Stage B compounds, zero mapping or scientific-integrity errors.
- Independent mapping rebuild: output CSV matches the active mapping file byte-for-byte; recomputed ordinary-food coverage is 109/119.
- Stage B connector: PASS against 710 manifest entries and 119 compounds.
- Stage B portable validator: 16/16 checks passed, 0 errors, 313 warnings. The inherited warnings remain documented.

Clean-copy suite and validation are recorded in `reports/phase1b/PHASE1B_COMPLETION_REPORT.md` and packaged `VALIDATION_RESULTS.json` in `releases/Phase1B-v1.0.0/`.

All source-backed records are positive quantitative observations; the validator preserves missing as missing and tests that no value is fabricated from missing data. Tests also cover ordinary-food eligibility, contextual separation, exact chemical identity, unit conversion, exposure formulas, provenance, and read-only Stage B connector integrity.
