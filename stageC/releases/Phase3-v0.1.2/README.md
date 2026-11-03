# CookRisk Phase 3 recipe and meal core — v0.1.2

Status: **COMPLETE_WITH_DOCUMENTED_LIMITATIONS**. This immutable successor hardens recipe and meal schemas, adds a provenance-gated Stage A output adapter, independent cooking-semantics checks, and Phase 4/5 uncertainty and validation foundations.

Run the isolated package tests from the repository root:

```powershell
python -m pip install -r stageC/releases/Phase3-v0.1.2/stageC/requirements-dev.txt
$env:PYTHONPATH = 'stageC/releases/Phase3-v0.1.2/stageC/src;stageC/releases/Phase3-v0.1.2/stageC/tests'
python -m unittest discover -s stageC/releases/Phase3-v0.1.2/stageC/tests -v
```

The package preserves Phase1B-v1.3.2, Phase2-v0.3.1, and Phase4-v0.1.2 as read-only upstream references. Phase2-v0.3.1 has zero quantitative cooked-concentration estimates. The inspected Stage A workspace has no serialized model artifact or defined `Retention_Final` denominator/measurement basis; no Stage A inference is run and model estimates remain blocked. Missing evidence, yield, or uncertainty remains explicit. This package makes no published-data or external-validation claim and performs no clinical interpretation.
