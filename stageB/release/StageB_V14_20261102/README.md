# CookRisk Stage B — V14 versioned release

**Release:** `StageB_V14_20261102`  
**Status:** partial; not ready for the 160-compound target.

V14 preserves the 123-compound V13 checkpoint and adds five evidence-led anchors: demethoxycurcumin, bisdemethoxycurcumin, sinensetin, eupatorin, and Allura Red AC. The registry contains 128 unique compounds and 299 interaction-evidence records. Newly added findings are in-vitro or animal only; no new human clinical interaction is claimed.

V13 remains unchanged. Stage A and Stage C were outside this release scope. No Stage C exposure integration or clinical food–drug inference was performed. See `RELEASE_STATUS.md` and `NEXT_STEPS.md` for batch gates, verification limits, and the remaining work.

## Release contents

- `data/` — compound, interaction-evidence, bibliography, study, warning, drug/probe, and inherited retention tables.
- `identity/` — chemical identity and structure audit.
- `provenance/` — screening log, selection decisions, source audits, and claim-support records.
- `validation/` — per-batch gate reports and inherited audit artifacts.
- `scripts/` — release validation and manifest verification utilities.
- `manifests/SHA256SUMS.json` — canonical-text, exact-binary release manifest.

## Verify

Run from this directory with Python 3:

```powershell
python -B scripts/manifest_integrity.py verify . --mode canonical
```

The release manifest is generated only after the final data and documentation changes.
