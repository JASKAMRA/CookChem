from pathlib import Path
import json,pandas as pd
R=Path(__file__).resolve().parent
parent=pd.read_csv(R.parent/"batch_015"/"updated_master_dataset.csv"); master=pd.read_csv(R/"updated_master_dataset.csv"); new=pd.read_csv(R/"verified_observations.csv"); manifest=json.loads((R/"manifest.json").read_text())
pd.testing.assert_frame_equal(parent.reset_index(drop=True),master.iloc[:len(parent)][parent.columns].reset_index(drop=True),check_dtype=False)
assert len(parent)==796 and len(master)==828 and len(new)==32 and master.doi.nunique()==28
assert set(new.doi)=={"10.1021/jf904306r"} and (new.measurement_basis=="dry weight (DW)").all() and new.compound.nunique()==2 and new.food_matrix.nunique()==4
assert not master.observation_id.duplicated().any() and (new.target_value_percent.round(8)==(100*new.cooked_concentration/new.raw_concentration).round(8)).all()
assert not manifest["target_1000_reached"] and not manifest["stage_c_integration_authorized"]
print("PASS: batch 016 preserves 796 parent rows and adds 32 primary-table individual Brassica carotenoid pairs from one DOI family.")
