# Reproducibility

Run from repository root:

```powershell
python stageA/recovery_v0_1_0_2026_11_10/build_recovery_package.py
python stageA/recovery_v0_1_0_2026_11_10/validate_recovery.py
```

The build reads only historical CSV inputs and overwrites only generated files inside this versioned recovery directory.
