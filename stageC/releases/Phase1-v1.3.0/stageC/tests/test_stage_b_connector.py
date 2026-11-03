import copy
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from stage_c.exceptions import SourceIntegrityError
from stage_c.compound_mapping import assess_mapping_compatibility, mapping_coverage
from stage_c.food_composition import load_food_data
from stage_c.compound_mapping import load_mappings
from stage_c.provenance import sha256_file
from stage_c.stage_b_connector import (
    EXPECTED_COMPOUND_COUNT,
    RELEASE_ID,
    create_snapshot,
    default_release_path,
    detect_source_changes,
    load_stage_b,
    validate_registry_tables,
    verify_release,
)


class StageBConnectorTests(unittest.TestCase):
    def setUp(self):
        self.stage = Path(__file__).resolve().parents[1]
        self.temp_root = self.stage / "reports" / "testing"
        self.temp_root.mkdir(parents=True, exist_ok=True)

    def test_authoritative_release_manifest_and_exact_ids(self):
        release = verify_release()
        self.assertEqual(release["release_id"], RELEASE_ID)
        self.assertEqual(release["manifest_entries"], 836)
        self.assertEqual(release["compound_count"], EXPECTED_COMPOUND_COUNT)
        data = load_stage_b()
        compounds = data["source_files"]["compound_registry.csv"]
        identity = data["source_files"]["identity_structure_audit.csv"]
        ids = [row["Compound_ID"] for row in compounds]
        self.assertEqual(len(ids), 143)
        self.assertEqual(len(set(ids)), 143)
        self.assertEqual(len(identity), 143)
        self.assertTrue(all(row["StageC_Identity_Verification_Status"] for row in compounds))
        self.assertTrue(any(row["StageC_Identity_Verification_Status"] != "Complete" for row in compounds))

    def test_legacy_mapping_coverage_respects_pending_stage_b_identity(self):
        compounds = load_stage_b()["source_files"]["compound_registry.csv"]
        foods = load_food_data(self.stage / "data" / "food_composition" / "food_composition.csv")
        mappings = load_mappings(self.stage / "data" / "compound_food_mapping" / "compound_food_mapping.csv")
        coverage = mapping_coverage(compounds, foods, mappings)
        review = assess_mapping_compatibility(compounds, mappings)
        self.assertEqual(coverage["total_stage_b_compounds"], 143)
        self.assertEqual(coverage["compounds_with_verified_quantitative_food_data"], 93)
        self.assertEqual(coverage["legacy_mapped_compounds_pending_identity_review"], 16)
        self.assertEqual(coverage["legacy_mapping_rows_pending_identity_review"], 46)
        self.assertEqual(len(review), 46)
        self.assertTrue(all(row["active_use_allowed"] == "false" for row in review))

    def test_source_identity_warning_remains_visible(self):
        data = load_stage_b()
        compound = next(
            row for row in data["source_files"]["compound_registry.csv"]
            if row["Canonical_Name"] == "Capsaicin"
        )
        self.assertIn("V3-W01", compound["StageC_Warning_Identifiers"])

    def test_registry_and_identity_mutations_are_rejected(self):
        records = load_stage_b()["source_files"]
        duplicate = copy.deepcopy(records)
        duplicate["compound_registry.csv"][-1] = duplicate["compound_registry.csv"][0].copy()
        with self.assertRaisesRegex(SourceIntegrityError, "Duplicate Stage B Compound_ID"):
            validate_registry_tables(duplicate)

        missing_identity = copy.deepcopy(records)
        missing_identity["identity_structure_audit.csv"].pop()
        with self.assertRaisesRegex(SourceIntegrityError, "IDs differ"):
            validate_registry_tables(missing_identity)

        inconsistent_identity = copy.deepcopy(records)
        inconsistent_identity["identity_structure_audit.csv"][0]["Canonical_Name"] = "synthetic mismatch"
        with self.assertRaisesRegex(SourceIntegrityError, "Canonical_Name disagree"):
            validate_registry_tables(inconsistent_identity)

        duplicate_key = copy.deepcopy(records)
        repeated_key = duplicate_key["compound_registry.csv"][0]["InChIKey"]
        duplicate_key["compound_registry.csv"][1]["InChIKey"] = repeated_key
        duplicate_key["identity_structure_audit.csv"][1]["Registry_InChIKey"] = repeated_key
        with self.assertRaisesRegex(SourceIntegrityError, "Duplicate Stage B InChIKey"):
            validate_registry_tables(duplicate_key)

    def test_only_authoritative_release_path_is_accepted(self):
        with tempfile.TemporaryDirectory(dir=self.temp_root) as td:
            with self.assertRaisesRegex(SourceIntegrityError, "Only the authoritative Stage B release"):
                verify_release(Path(td))

    def test_snapshot_checksums_and_record_counts(self):
        source_manifest = sha256_file(default_release_path() / "manifests" / "SHA256SUMS.json")
        with tempfile.TemporaryDirectory(dir=self.temp_root) as td:
            destination = Path(td) / "snapshot"
            manifest = create_snapshot(destination)
            self.assertEqual(manifest["source_release_id"], RELEASE_ID)
            self.assertEqual(manifest["compound_count"], EXPECTED_COMPOUND_COUNT)
            self.assertEqual(len(manifest["files"]), 9)
            self.assertTrue(all(row["sha256"] == row["snapshot_sha256"] for row in manifest["files"]))
            self.assertEqual(
                next(row["record_count"] for row in manifest["files"] if row["snapshot_file"] == "compound_registry.csv"),
                143,
            )
            self.assertEqual(detect_source_changes(destination), [])
        self.assertEqual(
            source_manifest,
            sha256_file(default_release_path() / "manifests" / "SHA256SUMS.json"),
        )

    def test_changed_snapshot_is_detected_and_not_overwritten(self):
        with tempfile.TemporaryDirectory(dir=self.temp_root) as td:
            destination = Path(td) / "snapshot"
            create_snapshot(destination)
            (destination / "compound_registry.csv").write_text("corrupted", encoding="utf-8")
            changes = detect_source_changes(destination)
            self.assertTrue(any(row["side"] == "snapshot" for row in changes))
            with self.assertRaises(SourceIntegrityError):
                create_snapshot(destination)

    def test_tampered_import_manifest_metadata_is_detected(self):
        with tempfile.TemporaryDirectory(dir=self.temp_root) as td:
            destination = Path(td) / "snapshot"
            create_snapshot(destination)
            manifest_path = destination / "import_manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["files"][0]["record_count"] = 119
            manifest["files"][0]["source_path"] = "stageB/release/StageB_Final/data/compound_registry.csv"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            changes = detect_source_changes(destination)
            self.assertTrue(any(row["side"] == "record_count" for row in changes))
            self.assertTrue(any(row["side"] == "source_path" for row in changes))
            with self.assertRaises(SourceIntegrityError):
                create_snapshot(destination)

    def test_existing_phase1b_data_is_byte_preserved_and_new_ids_stay_unmapped(self):
        expected_hashes = {
            "data/food_composition/food_composition.csv": "aa15fd49be4afd30d1f61fe06de9039d0a925c22a6c56e970ddc75033b04f127",
            "data/compound_food_mapping/compound_food_mapping.csv": "9dcaadf0821aee15f1666ca26c88c592bb1e98a781eb533e246ddd94dab9ca97",
        }
        for relative, expected in expected_hashes.items():
            self.assertEqual(sha256_file(self.stage / relative), expected)

        old_snapshot = self.stage / "data" / "stage_b_snapshot_20261102" / "compound_registry.csv"
        with old_snapshot.open(encoding="utf-8-sig", newline="") as stream:
            old_ids = {row["Compound_ID"] for row in csv.DictReader(stream)}
        current_ids = {row["Compound_ID"] for row in load_stage_b()["source_files"]["compound_registry.csv"]}
        added_ids = current_ids - old_ids
        self.assertEqual(len(old_ids), 119)
        self.assertEqual(len(added_ids), 24)
        self.assertFalse(old_ids - current_ids)

        food_path = self.stage / "data" / "food_composition" / "food_composition.csv"
        mapping_path = self.stage / "data" / "compound_food_mapping" / "compound_food_mapping.csv"
        with food_path.open(encoding="utf-8-sig", newline="") as stream:
            foods = list(csv.DictReader(stream))
        with mapping_path.open(encoding="utf-8-sig", newline="") as stream:
            mappings = list(csv.DictReader(stream))
        self.assertEqual(len(foods), 511)
        self.assertEqual(len(mappings), 511)
        food_refs = {
            row.get(field, "").strip()
            for row in foods
            for field in ("compound_id", "mapping_review_compound_id")
            if row.get(field, "").strip()
        }
        mapping_refs = {
            value.strip()
            for row in mappings
            for field in ("compound_id", "candidate_compound_ids")
            for value in row.get(field, "").split("|")
            if value.strip()
        }
        self.assertFalse(food_refs & added_ids)
        self.assertFalse(mapping_refs & added_ids)


if __name__ == "__main__":
    unittest.main()
