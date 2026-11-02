# CookRisk Stage B — V15 versioned continuation

**Release:** `StageB_V15_20261102`  
**Status:** partial; not ready for the 160-compound target.

V15 is a separate continuation from V14. It preserves inherited V14 compound, evidence, and warning records, then adds eight food-additive anchors in two controlled batches. The release contains 136 unique compounds and 310 interaction-evidence records. New findings are in-vitro transporter or Caco-2 results; none demonstrate a human food–drug interaction.

V13 and V14 remain historical checkpoints. Stage A and Stage C are outside this release. No Stage C exposure integration or clinical food–drug inference was performed. See `RELEASE_STATUS.md`, `NEXT_STEPS.md`, and the batch review records for evidence limits and remaining work.

## Release contents

- `data/` — compound, interaction-evidence, bibliography, study, warning, drug/probe, and inherited retention tables.
- `identity/` — chemical identity and structure audit.
- `provenance/` — screening log, selection decisions, source audits, and claim-support records.
- `validation/` — per-batch gate reports and inherited audit artifacts.
- `scripts/` — release validation, controlled ingestion, and manifest verification utilities.
- `manifests/SHA256SUMS.json` — canonical-text, exact-binary release manifest.

## Verify

Run from this directory with Python 3:

```powershell
python -B scripts/manifest_integrity.py verify . --mode exact
python -B scripts/validate_v15.py
python -B -m unittest discover -s tests -p 'test_v15_release.py' -v
```

The manifest is generated only after final data and documentation changes.
