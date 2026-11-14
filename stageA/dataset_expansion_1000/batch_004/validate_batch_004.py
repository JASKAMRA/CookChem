"""Read-only integrity checks for controlled expansion batch 004 outputs."""
from pathlib import Path
import json
import pandas as pd
R=Path(__file__).resolve().parent
parent=pd.read_csv(R.parent/'batch_003'/'updated_master_dataset.csv')
master=pd.read_csv(R/'updated_master_dataset.csv')
new=pd.read_csv(R/'verified_observations.csv')
manifest=json.loads((R/'manifest.json').read_text(encoding='utf-8'))
pd.testing.assert_frame_equal(parent.reset_index(drop=True),master.iloc[:len(parent)][parent.columns].reset_index(drop=True),check_dtype=False)
assert len(parent)==488 and len(master)==524 and len(new)==36 and master.doi.nunique()==15
assert set(new.doi)=={'10.3390/plants10102192'} and (new.measurement_basis=='dry weight (DW)').all()
assert (new.food_matrix=='Sweet chestnut edible seed (Castanea sativa)').all() and new.canonical_molecular_id.notna().all()
assert (new.target_value_percent.round(8)==(100*new.cooked_concentration/new.raw_concentration).round(8)).all()
assert not manifest['target_1000_reached'] and not manifest['stage_c_integration_authorized']
print('PASS: batch 004 preserves 488 parent rows and adds 36 traceable edible-seed HPLC-MS/MS/DW pairs from one new DOI family.')
