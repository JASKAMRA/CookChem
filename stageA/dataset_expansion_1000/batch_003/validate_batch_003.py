"""Read-only integrity checks for controlled expansion batch 003 outputs."""
from pathlib import Path
import json
import pandas as pd

R = Path(__file__).resolve().parent
parent = pd.read_csv(R.parent / "batch_002" / "updated_master_dataset.csv")
master = pd.read_csv(R / "updated_master_dataset.csv")
new = pd.read_csv(R / "verified_observations.csv")
manifest = json.loads((R / "manifest.json").read_text(encoding="utf-8"))
pd.testing.assert_frame_equal(parent.reset_index(drop=True), master.iloc[:len(parent)][parent.columns].reset_index(drop=True), check_dtype=False)
assert len(parent) == 471 and len(master) == 488 and len(new) == 17
assert master.doi.nunique() == 14 and set(new.doi) == {"10.3390/molecules28073066", "10.3390/antiox13070755"}
assert new.canonical_molecular_id.notna().all()
assert set(new.loc[new.doi.eq("10.3390/molecules28073066"), "measurement_basis"]) == {"as-reported product basis (mg/100 g); not re-labelled FW or DW"}
assert set(new.loc[new.doi.eq("10.3390/antiox13070755"), "measurement_basis"]) == {"dry weight (DW)"}
assert (new.target_value_percent.round(8) == (100 * new.cooked_concentration / new.raw_concentration).round(8)).all()
assert not manifest["target_1000_reached"] and not manifest["stage_c_integration_authorized"]
print("PASS: batch 003 preserves 471 parent rows and adds 17 traceable primary-table pairs from two new DOI families.")
