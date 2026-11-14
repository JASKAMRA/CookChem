from pathlib import Path
import csv,json,hashlib,joblib,numpy as np,pandas as pd
R=Path(__file__).resolve().parent
with (R/'expanded_clean_stageA_dataset.csv').open(encoding='utf-8',newline='') as f:r=list(csv.DictReader(f))
assert len(r)==379 and len({x['doi'] for x in r})==8
n=[x for x in r if x['doi']=='10.1007/s11130-020-00808-0'];assert len(n)==5 and all(x['measurement_basis']=='dry weight (DW)' for x in n)
assert all(abs(float(x['target_value_percent'])-100*float(x['cooked_concentration'])/float(x['raw_concentration']))<1e-8 for x in n)
m=json.loads((R/'model_package/model_manifest.json').read_text());a=R/'model_package/experimental_apparent_concentration_ratio_model.joblib';assert hashlib.sha256(a.read_bytes()).hexdigest()==m['artifact_sha256'];cols=m['features']['numeric']+m['features']['categorical'];x=pd.DataFrame([{c:r[0][c] for c in cols}]);x[m['features']['numeric']]=x[m['features']['numeric']].apply(pd.to_numeric,errors='coerce');assert np.isfinite(joblib.load(a).predict(x)[0]);assert not m['stage_c_integration_authorized'];print('PASS: v0.5 target, provenance, artifact hash, and smoke prediction verified.')
