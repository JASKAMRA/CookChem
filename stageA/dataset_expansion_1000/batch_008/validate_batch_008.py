from pathlib import Path
import json,pandas as pd
R=Path(__file__).resolve().parent;parent=pd.read_csv(R.parent/'batch_007'/'updated_master_dataset.csv');master=pd.read_csv(R/'updated_master_dataset.csv');new=pd.read_csv(R/'verified_observations.csv');m=json.loads((R/'manifest.json').read_text())
pd.testing.assert_frame_equal(parent.reset_index(drop=True),master.iloc[:len(parent)][parent.columns].reset_index(drop=True),check_dtype=False)
assert len(parent)==600 and len(master)==635 and len(new)==35 and master.doi.nunique()==21;assert set(new.doi)=={'10.1016/j.jff.2024.106380'}
assert (new.measurement_basis=='fresh matter (FM)').all() and new.canonical_molecular_id.notna().all() and not master.observation_id.duplicated().any();assert (new.target_value_percent.round(8)==(100*new.cooked_concentration/new.raw_concentration).round(8)).all();assert not m['target_1000_reached'] and not m['stage_c_integration_authorized']
print('PASS: batch 008 preserves 600 parent rows and adds 35 traceable individual HPLC-ESI-MS/MS/FM potato pairs from one new DOI family.')
