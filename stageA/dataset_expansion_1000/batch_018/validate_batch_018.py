from pathlib import Path
import hashlib,json
import pandas as pd
R=Path(__file__).resolve().parent; ROOT=R.parent
parent=pd.read_csv(ROOT/"batch_016"/"updated_master_dataset.csv"); master=pd.read_csv(R/"updated_master_dataset.csv"); new=pd.read_csv(R/"verified_observations.csv")
assert len(parent)==828 and len(master)==858 and len(new)==30 and master.iloc[:828].equals(parent)
assert master.doi.nunique()==29 and new.doi.nunique()==1 and new.doi.iloc[0]=="10.3390/foods13030472"
assert new.compound.nunique()==3 and new.food_matrix.nunique()==5 and new.cooking_method_normalized.nunique()==2
assert new.measurement_basis.eq("fresh weight (FW)").all() and new.evidence_status.eq("VERIFIED_PRIMARY_TABLE").all()
assert new.canonical_molecular_id.notna().all() and not master.observation_id.duplicated().any()
assert (new.target_value_percent.round(8)==(100*new.cooked_concentration/new.raw_concentration).round(8)).all()
assert hashlib.sha256((ROOT/"batch_016"/"updated_master_dataset.csv").read_bytes()).hexdigest()==json.loads((R/"manifest.json").read_text())["parent_sha256"]
print("PASS: batch 018 preserves 828 parent rows and adds 30 primary-table individual wild-leaf raw/cooked pairs from one new DOI family.")
