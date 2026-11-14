# Training and evaluation scripts

The reproducible scripts are intentionally one directory above this index:

- `../build_dataset.py` constructs only the verified apparent-concentration-ratio dataset.
- `../train_experimental_model.py` runs five-fold compound-grouped benchmarking and writes an explicitly non-deployable package.
- `../validate_recovery_v02.py` checks data semantics, artifact hash, and a one-record prediction.

They are kept beside the generated artifacts so their relative input/output paths are deterministic.
