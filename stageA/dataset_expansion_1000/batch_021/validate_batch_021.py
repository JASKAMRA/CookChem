"""Independent validation for controlled expansion batch 021."""
from pathlib import Path
import hashlib, json
import pandas as pd

R=Path(__file__).resolve().parent; ROOT=R.parent
parent=pd.read_csv(ROOT/"batch_020"/"updated_master_dataset.csv")
master=pd.read_csv(R/"updated_master_dataset.csv"); new=pd.read_csv(R/"verified_observations.csv")
assert len(parent)==938 and len(master)==1016 and len(new)==78
assert master.iloc[:len(parent)].equals(parent)
assert master.doi.nunique()==32 and new.doi.nunique()==1 and new.doi.iloc[0]=="10.3390/foods9050607"
assert new.evidence_status.eq("VERIFIED_PRIMARY_TABLE").all()
assert new.measurement_basis.eq("dry-weight basis (common stated basis)").all()
assert new.target_semantics.eq("apparent concentration ratio; not total-mass retention").all()
assert new.raw_concentration.gt(0).all() and new.cooked_concentration.gt(0).all()
assert (new.target_value_percent.round(8)==(100*new.cooked_concentration/new.raw_concentration).round(8)).all()
assert set(new.compound)=={"Alpha-Carotene","Beta-Carotene"}
assert set(new.food_matrix)=={"Carrot","Orange-fleshed Sweet Potato"}
assert not master.observation_id.duplicated().any()
assert new.reported_replicate_design.str.contains("no technical replicate is expanded",case=False,na=False).all()
print("PASS: batch 021 preserves 938 parent rows and adds 78 direct primary-table raw/cooked pairs from one new DOI family; 1,016 total verified observations / 32 DOI families.")
