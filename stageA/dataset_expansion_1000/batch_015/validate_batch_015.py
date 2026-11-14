from pathlib import Path
import json
import pandas as pd

R = Path(__file__).resolve().parent
parent = pd.read_csv(R.parent / "batch_013" / "updated_master_dataset.csv")
master = pd.read_csv(R / "updated_master_dataset.csv")
new = pd.read_csv(R / "verified_observations.csv")
manifest = json.loads((R / "manifest.json").read_text(encoding="utf-8"))

pd.testing.assert_frame_equal(parent.reset_index(drop=True), master.iloc[:len(parent)][parent.columns].reset_index(drop=True), check_dtype=False)
assert len(parent) == 757 and len(master) == 796 and len(new) == 39 and master.doi.nunique() == 27
assert set(new.doi) == {"10.1007/s13197-017-2547-2"}
assert (new.measurement_basis == "fresh weight (FW)").all() and new.canonical_molecular_id.notna().all()
assert new.compound.nunique() == 5 and new.food_matrix.nunique() == 8
assert not master.observation_id.duplicated().any()
assert (new.target_value_percent.round(8) == (100 * new.cooked_concentration / new.raw_concentration).round(8)).all()
assert not manifest["target_1000_reached"] and not manifest["stage_c_integration_authorized"]
print("PASS: batch 015 preserves 757 parent rows and adds 39 primary-table individual raw/cooked corn pairs from one new DOI family.")
