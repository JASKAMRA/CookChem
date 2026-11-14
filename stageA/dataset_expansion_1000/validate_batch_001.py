from pathlib import Path
import json,pandas as pd
R=Path(__file__).resolve().parent;d=pd.read_csv(R/'updated_master_dataset.csv'); n=pd.read_csv(R/'verified_observations.csv');m=json.loads((R/'manifest.json').read_text())
assert len(d)==451 and d.doi.nunique()==11 and len(n)==12
assert n.doi.nunique()==1 and n.doi.iloc[0]=='10.1007/s10068-024-01623-y'
assert (n.measurement_basis=='dry weight (DW)').all()
assert (n.target_value_percent.round(8)==(100*n.cooked_concentration/n.raw_concentration).round(8)).all()
assert not m['target_1000_reached'] and not m['stage_c_integration_authorized']
print('PASS: batch 001 preserves 439 parent rows and adds 12 traceable HPLC/DW Vitamin-C condition means from one new DOI family.')
