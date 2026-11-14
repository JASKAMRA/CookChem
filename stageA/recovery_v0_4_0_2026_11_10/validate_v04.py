from pathlib import Path
import csv,hashlib,json,joblib,numpy as np,pandas as pd
R=Path(__file__).resolve().parent
with (R/'expanded_clean_stageA_dataset.csv').open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
assert len(rows)==374 and len({r['doi'] for r in rows})==7
new=[r for r in rows if r['doi']=='10.1016/j.heliyon.2023.e21709'];assert len(new)==36
assert all(r['measurement_basis']=='fresh weight (FW)' and r['Temperature_C']=='' for r in new)
assert all(r['target_name']=='apparent_concentration_ratio_percent' and r['total_mass_retention_status']=='NOT_ESTABLISHED' for r in rows)
m=json.loads((R/'model_package/model_manifest.json').read_text());a=R/'model_package/experimental_apparent_concentration_ratio_model.joblib';assert hashlib.sha256(a.read_bytes()).hexdigest()==m['artifact_sha256'];cols=m['features']['numeric']+m['features']['categorical'];x=pd.DataFrame([{c:rows[0][c] for c in cols}]);x[m['features']['numeric']]=x[m['features']['numeric']].apply(pd.to_numeric,errors='coerce');assert np.isfinite(joblib.load(a).predict(x)[0]);assert not m['stage_c_integration_authorized'];print('PASS: v0.4 traceability, target contract, artifact hash, and smoke prediction verified.')
