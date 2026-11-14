"""Fail-closed checks for generated Stage A/Stage C recovery artifacts."""
from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    ledger = read("source_to_target_ledger.csv")
    assert len(ledger) == 1124
    assert {row["record_id"] for row in ledger}.__len__() == 1124
    assert sum(row["evidence_status"] == "VERIFIED" for row in ledger) == 117
    assert sum(row["target_classification"] == "VERIFIED_APPARENT_RATIO" for row in ledger) == 117
    assert all(row["model_rebuild_disposition"] == "EXCLUDED_FROM_MODEL_REBUILD" for row in ledger)
    assert all(row["target_classification"] != "VERIFIED_TOTAL_MASS_RETENTION" for row in ledger)
    assert sum(row["evidence_status"] == "DOI_MISMATCH" for row in ledger) > 0
    print("PASS: recovery ledger retains 1,124 rows and authorizes neither retraining nor total-mass inference.")


if __name__ == "__main__":
    main()
