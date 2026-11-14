"""Fail-closed Stage A prediction entry point.

No model artifact is intentionally distributed because final source-held-out validation
does not support predictive generalisation.  This guard prevents accidental use of an
exploratory fit as a deployed cooking-retention predictor.
"""
from pathlib import Path
import json

manifest=json.loads((Path(__file__).resolve().parent/'manifest.json').read_text())
if not manifest['saved_model']:
    raise SystemExit(
        'No prediction model is released. Stage A is a research prototype only: '
        'source-held-out validation did not establish generalisation, and apparent '
        'concentration ratio must not be treated as total-mass retention.'
    )
raise SystemExit('Unexpected artifact state; inspect manifest before any use.')
