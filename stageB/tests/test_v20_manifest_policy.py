"""Reproduce the V20 exact-vs-canonical policy disagreement without mutation."""
from __future__ import annotations

import hashlib
import json
import tempfile
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / "stageB" / "release" / "StageB_V20_20261103"
VERIFIER_PATH = RELEASE / "scripts" / "manifest_integrity.py"


def load_verifier():
    module = types.ModuleType("v20_manifest_integrity")
    module.__file__ = str(VERIFIER_PATH)
    module.__package__ = ""
    exec(compile(VERIFIER_PATH.read_bytes(), str(VERIFIER_PATH), "exec"), module.__dict__)
    return module


verifier = load_verifier()


class V20ManifestPolicyTests(unittest.TestCase):
    def test_release_exact_hashing_passes_and_canonical_disagreement_is_scoped(self):
        exact = verifier.verify_manifest(RELEASE, mode="exact")
        canonical = verifier.verify_manifest(RELEASE, mode="canonical")

        self.assertEqual(exact["status"], "PASS")
        self.assertEqual(exact["manifest_entries"], 839)
        self.assertEqual(exact["release_files"], 839)
        self.assertEqual(exact["missing"], [])
        self.assertEqual(exact["unexpected"], [])
        self.assertEqual(exact["mismatches"], [])
        self.assertEqual(canonical["status"], "FAIL")
        self.assertEqual(canonical["mismatches"], [{
            "path": "validation/final_validation_results.csv",
            "expected": "9494588fa341142fa98c34d0991c5b53321f0d28235a07ff9b45e4cd82e493b2",
            "actual": "d4172d01804bed6466d9868007b70733a752e67a8e3531edd63e21c9aa35b3c9",
        }])
        self.assertEqual(canonical["raw_byte_mismatch_count"], 0)

    def test_crlf_disagreement_reproduces_in_isolated_copy(self):
        relative = "validation/final_validation_results.csv"
        source_bytes = (RELEASE / relative).read_bytes()
        self.assertEqual(source_bytes.count(b"\r\n"), 17)
        expected_raw_hash = hashlib.sha256(source_bytes).hexdigest()

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            artifact = root / relative
            artifact.parent.mkdir(parents=True)
            artifact.write_bytes(source_bytes)
            manifest_path = root / verifier.MANIFEST_RELATIVE_PATH
            manifest_path.parent.mkdir(parents=True)
            manifest_path.write_text(json.dumps({relative: expected_raw_hash}), encoding="utf-8")

            self.assertEqual(verifier.verify_manifest(root, mode="exact")["status"], "PASS")
            canonical = verifier.verify_manifest(root, mode="canonical")
            self.assertEqual(canonical["status"], "FAIL")
            self.assertEqual(canonical["mismatches"][0]["path"], relative)
            self.assertEqual(canonical["raw_byte_mismatch_count"], 0)


if __name__ == "__main__":
    unittest.main()
