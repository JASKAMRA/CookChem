from pathlib import Path
import json, pandas as pd
R=Path(__file__).resolve().parent
parent=pd.read_csv(R.parent/'batch_008'/'updated_master_dataset.csv')
master=pd.read_csv(R/'updated_master_dataset.csv')
new=pd.read_csv(R/'verified_observations.csv')
m=json.loads((R/'manifest.json').read_text())
pd.testing.assert_frame_equal(parent.reset_index(drop=True),master.iloc[:len(parent)][parent.columns].reset_index(drop=True),check_dtype=False)
assert len(parent)==635 and len(master)==667 and len(new)==32 and master.doi.nunique()==22
assert set(new.doi)=={'10.17113/ftb.56.04.18.5709'}
assert (new.measurement_basis=='fresh mass (FM)').all() and new.canonical_molecular_id.notna().all()
assert set(new.compound)=={'Protocatechuic Acid','Caffeic acid','p-Coumaric acid','Ferulic Acid'}
assert set(new.cooking_method_normalized)=={'blanching','frying'} and set(new.Cooking_Time_min)=={2,5,8,10}
assert not master.observation_id.duplicated().any()
assert (new.target_value_percent.round(8)==(100*new.cooked_concentration/new.raw_concentration).round(8)).all()
assert not m['target_1000_reached'] and not m['stage_c_integration_authorized']
print('PASS: batch 009 preserves 635 parent rows and adds 32 traceable individual HPLC fresh-mass garlic pairs from one new DOI family.')
