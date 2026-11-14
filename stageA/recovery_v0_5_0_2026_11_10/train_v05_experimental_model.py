"""Reuse the immutable v0.4 training protocol against this package's paths."""
from pathlib import Path
source=Path(__file__).resolve().parents[1]/'recovery_v0_4_0_2026_11_10'/'train_v04_experimental_model.py'
code=source.read_text(encoding='utf-8').replace('# v0.4 experimental model comparison','# v0.5 experimental model comparison')
scope={'__name__':'__main__','__file__':str(Path(__file__).resolve())}
exec(compile(code,str(source),'exec'),scope)
