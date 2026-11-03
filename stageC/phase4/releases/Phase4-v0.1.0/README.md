# CookRisk Phase 4 evidence layer

Current status: **IN_PROGRESS**. There was no formal Phase 4/Stage D spec in the current top-level Stage C documentation, so the direction in `PROPOSED_SCOPE.md` is explicitly proposed. This v0.1.0 package demonstrates a traceable source/extraction/review pipeline with one primary human pharmacokinetic study registered and one abstract-level evidence record. It is not a comprehensive review.

## Data and workflow

- `data/source_registry.json` and `reports/source_bibliography.csv` hold bibliographic sources.
- `data/evidence_registry.json` holds extracted claims separately from source metadata.
- `schemas/` defines Draft 2020-12 source and evidence-record shapes.
- `src/phase4_registry.py` validates IDs and references and exposes a read-only Phase 3 context selector. It does not calculate dose, food concentration, cooking retention, risk, or clinical meaning.
- `reports/` records extraction, identity/applicability decisions, and pending review.
- `releases/Phase4-v0.1.0/` is a checksummed, independently testable `IN_PROGRESS` snapshot.

The registered source is White et al. 2016, PMID 27100333, DOI 10.3109/15563650.2016.1146740. Only the PubMed abstract was reviewed in this first extraction. The observed result is qualitative; numerical PK outcomes are null. The compound link is name-only, applicability is context-limited, quality is unrated, and second review is pending. Therefore the record is deliberately excluded from the Phase 3 context view.

## Validation

Run from the repository root:

```powershell
python -m unittest discover -s stageC/phase4/tests -v
```

The test suite validates cross-references, identity/applicability/review gates, qualitative-vs-numeric separation, and the package SHA-256 manifest. Formal JSON Schema Draft 2020-12 checks run when the development dependency in `requirements-dev.txt` is installed. The current environment did not have `jsonschema`; tests report that specific validation as not run rather than treating JSON parsing as schema validation.

Phase 1B v1.3.1 and Phase 2 v0.3.0 are recorded as version-scoped dependencies only. Their data, manifests, and conclusions are not modified or copied into this evidence layer. This package does not duplicate Stage B interaction evidence.
