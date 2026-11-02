import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"src"))
from stage_c.exceptions import SourceIntegrityError
from stage_c.provenance import sha256_file
from stage_c.stage_b_connector import create_snapshot, default_release_path, detect_source_changes, load_stage_b, verify_release

class StageBConnectorTests(unittest.TestCase):
    def setUp(self):
        self.temp_root=Path(__file__).resolve().parents[1]/"reports"/"testing";self.temp_root.mkdir(parents=True,exist_ok=True)

    def test_authoritative_release_manifest_and_exact_ids(self):
        release=verify_release();self.assertEqual(release["release_id"],"StageB_Final")
        data=load_stage_b();ids=[r["Compound_ID"] for r in data["source_files"]["compound_registry.csv"]]
        self.assertEqual(len(ids),119);self.assertEqual(len(set(ids)),119)
        self.assertEqual(len(data["source_files"]["identity_structure_audit.csv"]),119)

    def test_compound_specific_warning_ids_are_exposed(self):
        data=load_stage_b(); compound=next(r for r in data["source_files"]["compound_registry.csv"] if r["Canonical_Name"]=="Capsaicin")
        self.assertIn("V3-W01",compound["StageC_Warning_Identifiers"])

    def test_snapshot_checksums_and_record_counts(self):
        before=sha256_file(default_release_path()/"manifests"/"SHA256SUMS.json")
        with tempfile.TemporaryDirectory(dir=self.temp_root) as td:
            dest=Path(td)/"snapshot";m=create_snapshot(dest)
            self.assertEqual(len(m["files"]),9);self.assertTrue(all(x["sha256"]==x["snapshot_sha256"] for x in m["files"]))
            self.assertEqual(detect_source_changes(dest),[])
        after=sha256_file(default_release_path()/"manifests"/"SHA256SUMS.json")
        self.assertEqual(before,after)

    def test_changed_snapshot_is_detected(self):
        with tempfile.TemporaryDirectory(dir=self.temp_root) as td:
            dest=Path(td)/"snapshot";create_snapshot(dest)
            (dest/"compound_registry.csv").write_text("corrupted",encoding="utf-8")
            changes=detect_source_changes(dest)
            self.assertTrue(any(x["side"]=="snapshot" for x in changes))
            with self.assertRaises(SourceIntegrityError):create_snapshot(dest)

if __name__=="__main__":unittest.main()
