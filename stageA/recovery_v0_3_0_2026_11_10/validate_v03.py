from pathlib import Path
import csv,json,hashlib,joblib,numpy as np,pandas as pd
R=Path(__file__).resolve().parent
with (R/'expanded_clean_stageA_dataset.csv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
assert len(rows)>117 and len({x['doi'] for x in rows})>=6
assert all(x['target_name']=='apparent_concentration_ratio_percent' and x['total_mass_retention_status']=='NOT_ESTABLISHED' for x in rows)
m=json.loads((R/'model_package/model_manifest.json').read_text());a=R/'model_package/experimental_apparent_concentration_ratio_model.joblib';assert hashlib.sha256(a.read_bytes()).hexdigest()==m['artifact_sha256'];model=joblib.load(a);cols=m['features']['numeric']+m['features']['categorical'];sample=pd.DataFrame([{c:rows[0][c] for c in cols}]);sample[m['features']['numeric']]=sample[m['features']['numeric']].apply(pd.to_numeric,errors='coerce');assert np.isfinite(model.predict(sample)[0]);assert not m['stage_c_integration_authorized'];print('PASS: expanded v0.3 model validated as experimental apparent-ratio only.')
