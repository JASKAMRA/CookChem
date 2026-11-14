"""Read-only integrity checks for controlled expansion batch 002 outputs."""
from pathlib import Path
import json
import pandas as pd

R = Path(__file__).resolve().parent
parent = pd.read_csv(R.parent / "updated_master_dataset.csv")
master = pd.read_csv(R / "updated_master_dataset.csv")
new = pd.read_csv(R / "verified_observations.csv")
manifest = json.loads((R / "manifest.json").read_text(encoding="utf-8"))

parent_projection = master.iloc[: len(parent)][parent.columns]
pd.testing.assert_frame_equal(parent.reset_index(drop=True), parent_projection.reset_index(drop=True), check_dtype=False)
assert len(parent) == 451 and len(master) == 471 and len(new) == 20
assert master["doi"].nunique() == 12 and new["doi"].nunique() == 1
assert new["doi"].iloc[0] == "10.3390/foods13020230"
assert (new["measurement_basis"] == "dry weight (DW)").all()
assert (new["evidence_status"] == "VERIFIED_PRIMARY_TABLE").all()
assert new["canonical_molecular_id"].notna().all()
assert set(new["analytical_definition"]) == {"free phenolic-acid extract", "bound phenolic-acid extract"}
assert (new["target_value_percent"].round(8) == (100 * new["cooked_concentration"] / new["raw_concentration"]).round(8)).all()
assert not manifest["target_1000_reached"] and not manifest["stage_c_integration_authorized"]
print("PASS: batch 002 preserves all 451 parent rows and adds 20 traceable HPLC/DW same-fraction phenolic-acid condition means from one new DOI family.")
