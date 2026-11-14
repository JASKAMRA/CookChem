from pathlib import Path
import hashlib,json
import pandas as pd
R=Path(__file__).resolve().parent; ROOT=R.parent
p=pd.read_csv(ROOT/"batch_018"/"updated_master_dataset.csv"); m=pd.read_csv(R/"updated_master_dataset.csv"); n=pd.read_csv(R/"verified_observations.csv")
assert len(p)==858 and len(m)==914 and len(n)==56 and m.iloc[:858].equals(p)
assert m.doi.nunique()==30 and n.doi.nunique()==1 and n.doi.iloc[0]=="10.1021/jf072304b"
assert n.food_matrix.nunique()==3 and n.compound.nunique()==10 and n.cooking_method_normalized.nunique()==3
assert n.measurement_basis.eq("dry weight (DW)").all() and n.evidence_status.eq("VERIFIED_PRIMARY_TABLE").all()
assert n.canonical_molecular_id.notna().all() and not m.observation_id.duplicated().any()
assert (n.target_value_percent.round(8)==(100*n.cooked_concentration/n.raw_concentration).round(8)).all()
assert hashlib.sha256((ROOT/"batch_018"/"updated_master_dataset.csv").read_bytes()).hexdigest()==json.loads((R/"manifest.json").read_text())["parent_sha256"]
print("PASS: batch 019 preserves 858 parent rows and adds 56 primary-table multi-matrix raw/cooked pairs from one new DOI family.")
