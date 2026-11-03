from __future__ import annotations
import csv
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RELEASE = Path(__file__).resolve().parents[1]

class ReleaseAuditTests(unittest.TestCase):
    def test_source_audit_rebuilds_byte_identically_and_release_manifest_matches(self):
        with tempfile.TemporaryDirectory(dir=RELEASE) as temp:
            out = Path(temp) / "source_audit.csv"
            subprocess.run([sys.executable, str(RELEASE / "scripts/audit_phase2_source_pairs.py"), "--input", str(RELEASE / "data/source_observed_cooking_pairs.csv"), "--output", str(out)], check=True, capture_output=True, text=True)
            self.assertEqual(out.read_bytes(), (RELEASE / "data/source_pair_audit_2026-11-03.csv").read_bytes())
        manifest = json.loads((RELEASE / "RELEASE_MANIFEST.json").read_text())
        for rel, expected in manifest["file_hashes"].items():
            self.assertEqual(hashlib.sha256((RELEASE / rel).read_bytes()).hexdigest(), expected, rel)
        with (RELEASE / "data/cooked_concentration_estimates.csv").open(newline="") as f:
            self.assertEqual(list(csv.DictReader(f)), [])

if __name__ == "__main__":
    unittest.main()
