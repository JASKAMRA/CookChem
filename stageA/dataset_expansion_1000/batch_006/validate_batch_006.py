"""Read-only integrity checks for controlled expansion batch 006 outputs."""
from pathlib import Path
import json,pandas as pd
R=Path(__file__).resolve().parent
parent=pd.read_csv(R.parent/'batch_005'/'updated_master_dataset.csv');master=pd.read_csv(R/'updated_master_dataset.csv');new=pd.read_csv(R/'verified_observations.csv');manifest=json.loads((R/'manifest.json').read_text())
pd.testing.assert_frame_equal(parent.reset_index(drop=True),master.iloc[:len(parent)][parent.columns].reset_index(drop=True),check_dtype=False)
assert len(parent)==539 and len(master)==573 and len(new)==34 and master.doi.nunique()==18
assert set(new.doi)=={'10.1155/2013/367819'} and (new.measurement_basis=='dry weight (DW)').all()
assert new.canonical_molecular_id.notna().all() and not master.observation_id.duplicated().any()
assert (new.target_value_percent.round(8)==(100*new.cooked_concentration/new.raw_concentration).round(8)).all()
assert not manifest['target_1000_reached'] and not manifest['stage_c_integration_authorized']
print('PASS: batch 006 preserves 539 parent rows and adds 34 traceable individual HPLC/DW cauliflower pairs from one new DOI family.')
