from __future__ import annotations

import csv
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "stageC/reports/phase2/source_pair_audit_2026-11-03.csv"
SCRIPT = ROOT / "stageC/scripts/audit_phase2_source_pairs.py"


class Phase2SourceAuditTests(unittest.TestCase):
    def test_all_117_pairs_match_primary_tables_and_recompute(self):
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True, capture_output=True, text=True)
        with AUDIT.open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 117)
        self.assertTrue(all(r["source_verification_status"] in {"VERIFIED_AGAINST_PRIMARY_TABLE", "VERIFIED_WITH_BASIS_LIMITATION"} for r in rows))
        self.assertEqual(sum(r["source_verification_status"] == "VERIFIED_WITH_BASIS_LIMITATION" for r in rows), 33)
        self.assertTrue(all(not r["audit_error_codes"] for r in rows))
        self.assertTrue(all(r["independently_recalculated_ratio"] for r in rows))
        self.assertEqual(len({r["compound_name"] for r in rows}), 24)
        self.assertTrue(all(r["source_url"].startswith("https://") for r in rows))


if __name__ == "__main__":
    unittest.main()
