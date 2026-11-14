from pathlib import Path
import json
import pandas as pd

R = Path(__file__).resolve().parent
parent = pd.read_csv(R.parent / "batch_012" / "updated_master_dataset.csv")
master = pd.read_csv(R / "updated_master_dataset.csv")
new = pd.read_csv(R / "verified_observations.csv")
manifest = json.loads((R / "manifest.json").read_text(encoding="utf-8"))
pd.testing.assert_frame_equal(parent.reset_index(drop=True), master.iloc[:len(parent)][parent.columns].reset_index(drop=True), check_dtype=False)
assert len(parent) == 749 and len(master) == 757 and len(new) == 8 and master.doi.nunique() == 26
assert set(new.doi) == {"10.1007/s11130-026-01551-8"}
assert (new.measurement_basis == "dry weight (DW)").all() and new.canonical_molecular_id.notna().all()
assert new.compound.nunique() == 8 and new.cooking_method_normalized.nunique() == 1 and new.Cooking_Time_min.eq(20).all()
assert not master.observation_id.duplicated().any()
assert (new.target_value_percent.round(8) == (100 * new.cooked_concentration / new.raw_concentration).round(8)).all()
assert not manifest["target_1000_reached"] and not manifest["stage_c_integration_authorized"]
print("PASS: batch 013 preserves 749 parent rows and adds 8 traceable individual raw/boiled Loche-squash pairs from one new DOI family.")
