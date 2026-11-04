# CookRisk Phase 4 evidence layer

Current status: **IN_PROGRESS**. There was no approved Phase 4/Stage D specification in the current top-level Stage C documentation, so `PROPOSED_SCOPE.md` remains explicitly proposed.

The working registry contains one publisher-full-text-reviewed primary human caffeine PK source and six separate extracted evidence records: five condition-level measured Cmax outcomes from Table 1 and one qualitative statistical comparison. All records remain `NAME_ONLY_MATCH`, `CONTEXT_LIMITED`, and `pending_second_reviewer`; the Phase 3 selector returns none. These plasma PK results cannot be used as food concentrations, recipe-dose multipliers, cooking-retention values, safety thresholds, or clinical advice.

The package records the article's abstract-versus-methods participant-count discrepancy and author funding/consultancy disclosures. Exact table rows are preserved without pooling or unit conversion. See `reports/extraction_report.md`, `reports/identity_applicability_review.md`, and `reports/pending_evidence_register.csv`.

`data/` holds bibliographic and evidence registries; `schemas/` declares Draft 2020-12; `src/phase4_registry.py` performs application-level validation and exposes a read-only selector that excludes numerical PK outcomes. No Stage B or Phase 2 records are copied into this layer. Phase 1B-v1.3.1 and Phase2-v0.3.0 are version-scoped dependencies only.

Run working-tree tests from the repository root:

```powershell
python -m unittest discover -s stageC/phase4/tests -v
```

Install `stageC/phase4/requirements-dev.txt` to run the optional formal JSON Schema validator. Phase4-v0.1.0 remains an immutable abstract-only historical snapshot; Phase4-v0.1.1 is the initial full-text continuation; Phase4-v0.1.2 tightens the Phase 3 context-only selector.
