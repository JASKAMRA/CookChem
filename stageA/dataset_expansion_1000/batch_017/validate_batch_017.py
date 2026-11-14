from pathlib import Path
import hashlib, json
import pandas as pd
R=Path(__file__).resolve().parent; ROOT=R.parent
parent=pd.read_csv(ROOT/"batch_016"/"updated_master_dataset.csv"); master=pd.read_csv(R/"updated_master_dataset.csv"); new=pd.read_csv(R/"verified_observations.csv")
assert len(parent)==828 and len(master)==837 and len(new)==9
assert master.iloc[:len(parent)].equals(parent)
assert master.doi.nunique()==29 and new.doi.nunique()==1 and new.doi.iloc[0]=="10.14456/apst.2022.5"
assert new["compound"].nunique()==9 and new["food_matrix"].nunique()==1
assert new["measurement_basis"].eq("dry weight (DW)").all()
assert new["cooking_method_normalized"].eq("boiling_then_drying").all()
assert new["evidence_status"].eq("VERIFIED_PRIMARY_TABLE").all()
assert new["canonical_molecular_id"].notna().all() and not master["observation_id"].duplicated().any()
assert (new.target_value_percent.round(8)==(100*new.cooked_concentration/new.raw_concentration).round(8)).all()
assert hashlib.sha256((ROOT/"batch_016"/"updated_master_dataset.csv").read_bytes()).hexdigest()==json.loads((R/"manifest.json").read_text())["parent_sha256"]
print("PASS: batch 017 preserves 828 parent rows and adds 9 primary-table individual raw/cooked Chaya pairs from one new DOI family.")
