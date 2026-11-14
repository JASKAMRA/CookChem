from pathlib import Path
import csv, hashlib, json
import joblib, numpy as np, pandas as pd
ROOT=Path(__file__).resolve().parent
with (ROOT/'clean_stageA_dataset.csv').open(encoding='utf-8', newline='') as f: rows=list(csv.DictReader(f))
assert len(rows) >= 100
assert {r['target_name'] for r in rows} == {'apparent_concentration_ratio_percent'}
assert {r['total_mass_retention_status'] for r in rows} == {'NOT_ESTABLISHED'}
assert all(r['evidence_status']=='VERIFIED' for r in rows)
manifest=json.loads((ROOT/'model_package/model_manifest.json').read_text())
assert manifest['status']=='EXPERIMENTAL_NOT_DEPLOYABLE'
assert manifest['stage_c_integration_authorized'] is False
artifact=ROOT/'model_package/experimental_concentration_ratio_model.joblib'
assert hashlib.sha256(artifact.read_bytes()).hexdigest()==manifest['artifact_sha256']
model=joblib.load(artifact)
features=manifest['features']['numeric']+manifest['features']['categorical']
sample=pd.DataFrame([{key: rows[0][key] for key in features}])
for key in manifest['features']['numeric']:
    sample[key]=pd.to_numeric(sample[key], errors='coerce')
prediction=model.predict(sample)
assert len(prediction)==1 and np.isfinite(prediction[0])
print('PASS: v0.2 artifact hash and single-record prediction validate; package remains non-deployable.')
