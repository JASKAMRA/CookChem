# Reproduction

    Run `python build_batch_002.py`, then `python validate_batch_002.py`.
    The build reads only Batch 001's immutable master, produces a new master in
    this directory, and uses the explicitly transcribed source values listed in
    the script and candidate registry. It performs no remote, Git, Stage-B/C/D,
    or historical-package modification.
