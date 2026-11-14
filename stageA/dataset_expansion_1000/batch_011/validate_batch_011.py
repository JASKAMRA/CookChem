from pathlib import Path
import json,pandas as pd
R=Path(__file__).resolve().parent; parent=pd.read_csv(R.parent/'batch_010'/'updated_master_dataset.csv'); master=pd.read_csv(R/'updated_master_dataset.csv');new=pd.read_csv(R/'verified_observations.csv');m=json.loads((R/'manifest.json').read_text())
pd.testing.assert_frame_equal(parent.reset_index(drop=True),master.iloc[:len(parent)][parent.columns].reset_index(drop=True),check_dtype=False)
assert len(parent)==707 and len(master)==719 and len(new)==12 and master.doi.nunique()==24 and set(new.doi)=={'10.3390/foods13213459'}
assert (new.measurement_basis=='dry basis (as reported)').all() and new.canonical_molecular_id.notna().all() and not master.observation_id.duplicated().any()
assert set(new.compound)=={'Vitamin C','Beta-Carotene'} and new.cooking_method_normalized.nunique()==3 and (new.target_value_percent.round(8)==(100*new.cooked_concentration/new.raw_concentration).round(8)).all()
assert not m['target_1000_reached'] and not m['stage_c_integration_authorized'];print('PASS: batch 011 preserves 707 parent rows and adds 12 traceable individual raw/cooked dry-basis pairs from one new DOI family.')
