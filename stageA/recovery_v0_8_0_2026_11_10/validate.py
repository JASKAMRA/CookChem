from pathlib import Path
import csv,json
R=Path(__file__).resolve().parent
with (R/'expanded_clean_stageA_dataset.csv').open(encoding='utf-8',newline='') as f:x=list(csv.DictReader(f))
n=[z for z in x if z['doi']=='10.1155/2020/8856260'];assert len(x)==439 and len(n)==32 and all(z['measurement_basis']=='fresh weight (FW)' for z in n);assert all(abs(float(z['target_value_percent'])-100*float(z['cooked_concentration'])/float(z['raw_concentration']))<1e-8 for z in n);assert not json.loads((R/'manifest.json').read_text())['stage_c_integration_authorized'];print('PASS v0.8 provenance and ratio checks')
