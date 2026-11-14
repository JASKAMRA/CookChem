from pathlib import Path
import json,pandas as pd
R=Path(__file__).resolve().parent;parent=pd.read_csv(R.parent/'batch_006'/'updated_master_dataset.csv');master=pd.read_csv(R/'updated_master_dataset.csv');new=pd.read_csv(R/'verified_observations.csv');m=json.loads((R/'manifest.json').read_text())
pd.testing.assert_frame_equal(parent.reset_index(drop=True),master.iloc[:len(parent)][parent.columns].reset_index(drop=True),check_dtype=False)
assert len(parent)==573 and len(master)==600 and len(new)==27 and master.doi.nunique()==20
assert set(new.doi)=={'10.3136/fstr.23.193','10.1371/journal.pone.0299037'} and (new.measurement_basis=='dry weight (DW)').all()
assert new.canonical_molecular_id.notna().all() and not master.observation_id.duplicated().any();assert (new.target_value_percent.round(8)==(100*new.cooked_concentration/new.raw_concentration).round(8)).all();assert not m['target_1000_reached'] and not m['stage_c_integration_authorized']
print('PASS: batch 007 preserves 573 parent rows and adds 27 traceable individual HPLC/DW pairs from two new DOI families.')
