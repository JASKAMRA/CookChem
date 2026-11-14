"""Read-only integrity checks for controlled expansion batch 005 outputs."""
from pathlib import Path
import json
import pandas as pd

R = Path(__file__).resolve().parent
parent = pd.read_csv(R.parent / "batch_004" / "updated_master_dataset.csv")
master = pd.read_csv(R / "updated_master_dataset.csv")
new = pd.read_csv(R / "verified_observations.csv")
manifest = json.loads((R / "manifest.json").read_text(encoding="utf-8"))

pd.testing.assert_frame_equal(parent.reset_index(drop=True), master.iloc[:len(parent)][parent.columns].reset_index(drop=True), check_dtype=False)
assert len(parent) == 524 and len(master) == 539 and len(new) == 15 and master.doi.nunique() == 17
assert set(new.doi) == {"10.14456/apst.2022.5", "10.3389/fsufs.2021.761145"}
assert not master.observation_id.duplicated().any() and new.canonical_molecular_id.notna().all()
assert (new.target_value_percent.round(8) == (100 * new.cooked_concentration / new.raw_concentration).round(8)).all()
assert (new.loc[new.doi == "10.14456/apst.2022.5", "measurement_basis"] == "dry weight (DW)").all()
assert (new.loc[new.doi == "10.3389/fsufs.2021.761145", "measurement_basis"] == "as reported (basis unspecified)").all()
assert not manifest["target_1000_reached"] and not manifest["stage_c_integration_authorized"]
print("PASS: batch 005 preserves 524 parent rows and adds 15 traceable individual-analyte pairs from two new DOI families; reported basis labels are preserved.")
