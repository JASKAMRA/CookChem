from pathlib import Path
import hashlib, json
import pandas as pd

R = Path(__file__).resolve().parent
ROOT = R.parent
p = pd.read_csv(ROOT / "batch_019" / "updated_master_dataset.csv")
m = pd.read_csv(R / "updated_master_dataset.csv")
n = pd.read_csv(R / "verified_observations.csv")
assert len(p) == 914 and len(m) == 938 and len(n) == 24 and m.iloc[:914].equals(p)
assert m.doi.nunique() == 31 and n.doi.nunique() == 1 and n.doi.iloc[0] == "10.1016/j.foodchem.2015.10.037"
assert n.food_matrix.nunique() == 2 and n.compound.nunique() == 4 and n.cooking_method_normalized.nunique() == 3
assert n.measurement_basis.eq("raw-sample reference basis (common raw mass)").all()
assert n.evidence_status.eq("VERIFIED_PRIMARY_TABLE").all() and n.canonical_molecular_id.notna().all()
assert not m.observation_id.duplicated().any()
assert (n.target_value_percent.round(8) == (100 * n.cooked_concentration / n.raw_concentration).round(8)).all()
assert hashlib.sha256((ROOT / "batch_019" / "updated_master_dataset.csv").read_bytes()).hexdigest() == json.loads((R / "manifest.json").read_text())["parent_sha256"]
print("PASS: batch 020 preserves 914 parent rows and adds 24 direct primary-table, common-raw-basis raw/cooked pairs from one new DOI family.")
