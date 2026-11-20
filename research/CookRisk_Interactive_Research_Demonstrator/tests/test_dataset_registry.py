from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from research_data import (
    BATCH021_DATASET_ID,
    LIVE_EXPLORATION_DATASET_ID,
    annotate_saved_metric_provenance,
    load_acr_dataset,
    load_batch021_evaluation_provenance,
    load_registered_dataset,
    get_dataset_entry,
)


FIXTURE_COLUMNS = [
    "observation_id",
    "target_value_percent",
    "target_name",
    "target_equation",
    "target_semantics",
]
FIXTURE_TARGET = {
    "field": "target_value_percent",
    "name_field": "target_name",
    "name": "apparent_concentration_ratio_percent",
    "equation_field": "target_equation",
    "equation": "100 * C_cooked / C_raw",
    "semantics_field": "target_semantics",
    "semantics": "apparent concentration ratio; not total-mass retention",
    "unit": "%",
    "scientific_meaning": "Apparent ratio only; not total-mass retention.",
}


class DatasetRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent)
        self.root = Path(self.temp.name)
        self.dataset_path = self.root / "data.csv"
        self.rows = [
            {
                "observation_id": "obs-1",
                "target_value_percent": "55.0",
                "target_name": FIXTURE_TARGET["name"],
                "target_equation": FIXTURE_TARGET["equation"],
                "target_semantics": FIXTURE_TARGET["semantics"],
            },
            {
                "observation_id": "obs-2",
                "target_value_percent": "101.0",
                "target_name": FIXTURE_TARGET["name"],
                "target_equation": FIXTURE_TARGET["equation"],
                "target_semantics": FIXTURE_TARGET["semantics"],
            },
        ]
        self.write_dataset()
        self.registry_path = self.root / "registry.json"
        self.write_registry()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_dataset(self, rows: list[dict[str, str]] | None = None) -> None:
        with self.dataset_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=FIXTURE_COLUMNS)
            writer.writeheader()
            writer.writerows(self.rows if rows is None else rows)

    def entry(self) -> dict:
        return {
            "dataset_id": "fixture-approved",
            "repository_relative_path": "data.csv",
            "expected_sha256": hashlib.sha256(self.dataset_path.read_bytes()).hexdigest(),
            "row_count": 2,
            "column_count": len(FIXTURE_COLUMNS),
            "schema_columns": FIXTURE_COLUMNS,
            "id_field": "observation_id",
            "unique_id_count": 2,
            "target_definition": dict(FIXTURE_TARGET),
            "designation_status": "OWNER_APPROVED_DEMONSTRATOR_EXPLORATION_ONLY",
            "allowed_application_uses": ["live_record_level_exploration"],
        }

    def write_registry(self, entry: dict | None = None, extra: dict | None = None) -> None:
        datasets = {"fixture-approved": self.entry() if entry is None else entry}
        if extra:
            datasets.update(extra)
        self.registry_path.write_text(
            json.dumps({"schema_version": 1, "datasets": datasets}),
            encoding="utf-8",
        )

    def load_fixture(self):
        return load_registered_dataset(
            "fixture-approved", repo_root=self.root, registry_path=self.registry_path
        )

    def test_owner_approved_reconstruction_loads_exact_snapshot(self) -> None:
        rows, digest, entry = load_acr_dataset()
        self.assertEqual(len(rows), 1016)
        self.assertEqual(digest, "f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0")
        self.assertEqual(entry["dataset_id"], LIVE_EXPLORATION_DATASET_ID)
        self.assertFalse(entry["canonical_scientific_dataset"])
        self.assertFalse(entry["independently_scientifically_validated"])

    def test_approved_synthetic_snapshot_loads_without_transformation(self) -> None:
        rows, digest, entry = self.load_fixture()
        self.assertEqual(rows, self.rows)
        self.assertEqual(len(digest), 64)
        self.assertEqual(entry["target_definition"]["equation"], FIXTURE_TARGET["equation"])

    def test_hash_mismatch_is_rejected(self) -> None:
        entry = self.entry()
        entry["expected_sha256"] = "0" * 64
        self.write_registry(entry)
        with self.assertRaisesRegex(ValueError, "Dataset hash mismatch"):
            self.load_fixture()

    def test_unknown_dataset_id_is_rejected(self) -> None:
        with self.assertRaisesRegex(KeyError, "Unknown dataset ID"):
            load_registered_dataset(
                "not-registered", repo_root=self.root, registry_path=self.registry_path
            )

    def test_historical_batch021_id_cannot_be_used_for_live_loading(self) -> None:
        historical = self.entry()
        historical.update(
            dataset_id=BATCH021_DATASET_ID,
            designation_status="OWNER_APPROVED_SEPARATE_HISTORICAL_REFERENCE",
            allowed_application_uses=["historical_saved_ml_results"],
        )
        self.write_registry(
            entry={"dataset_id": "fixture-approved", **self.entry()},
            extra={BATCH021_DATASET_ID: historical},
        )
        with self.assertRaisesRegex(ValueError, "not approved for live exploration"):
            load_registered_dataset(
                BATCH021_DATASET_ID, repo_root=self.root, registry_path=self.registry_path
            )

    def test_missing_file_fails_without_fallback(self) -> None:
        entry = self.entry()
        entry["repository_relative_path"] = "missing.csv"
        self.write_registry(entry)
        (self.root / "batch021.csv").write_text("historical data", encoding="utf-8")
        with self.assertRaisesRegex(FileNotFoundError, "Selected dataset file is missing"):
            self.load_fixture()

    def test_missing_target_definition_is_rejected(self) -> None:
        entry = self.entry()
        del entry["target_definition"]["equation"]
        self.write_registry(entry)
        with self.assertRaisesRegex(ValueError, "target definition is missing"):
            self.load_fixture()

    def test_row_level_target_mismatch_is_rejected(self) -> None:
        altered = [dict(row) for row in self.rows]
        altered[1]["target_equation"] = ""
        self.write_dataset(altered)
        entry = self.entry()
        self.write_registry(entry)
        with self.assertRaisesRegex(ValueError, "row target definition is missing or inconsistent"):
            self.load_fixture()

    def test_schema_and_row_count_mismatch_are_rejected(self) -> None:
        entry = self.entry()
        entry["schema_columns"] = FIXTURE_COLUMNS[:-1]
        entry["column_count"] = len(FIXTURE_COLUMNS) - 1
        self.write_registry(entry)
        with self.assertRaisesRegex(ValueError, "Dataset schema mismatch"):
            self.load_fixture()

        entry = self.entry()
        entry["row_count"] = 3
        self.write_registry(entry)
        with self.assertRaisesRegex(ValueError, "Dataset row-count mismatch"):
            self.load_fixture()

    def test_duplicate_or_missing_ids_are_rejected(self) -> None:
        altered = [dict(row) for row in self.rows]
        altered[1]["observation_id"] = altered[0]["observation_id"]
        self.write_dataset(altered)
        self.write_registry(self.entry())
        with self.assertRaisesRegex(ValueError, "ID integrity check failed"):
            self.load_fixture()

    def test_acr_definition_explicitly_excludes_total_mass_retention(self) -> None:
        self.assertEqual(FIXTURE_TARGET["equation"], "100 * C_cooked / C_raw")
        self.assertIn("not total-mass retention", FIXTURE_TARGET["semantics"])
        self.assertIn("paired food masses", load_acr_dataset()[2]["target_definition"]["scientific_meaning"])

    def test_batch021_saved_input_hash_matches_current_historical_reference(self) -> None:
        provenance = load_batch021_evaluation_provenance()
        self.assertTrue(provenance["identity_matches"])
        self.assertEqual(
            provenance["actual_sha256"],
            "111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8",
        )
        self.assertEqual(provenance["saved_input_sha256"], provenance["actual_sha256"])

    def test_historical_retention_target_stays_separate_and_unresolved(self) -> None:
        entry = get_dataset_entry("stagea-historical-retention-final-1124")
        self.assertEqual(entry["target_definition"]["field"], "Retention_Final")
        self.assertIsNone(entry["target_definition"]["equation"])
        self.assertIsNone(entry["target_definition"]["unit"])
        self.assertNotIn("live_record_level_exploration", entry["allowed_application_uses"])

    def test_batch021_metric_annotation_does_not_change_saved_values(self) -> None:
        metric = {
            "result_family": "Batch021 fixed audit",
            "r2": "-0.067833",
            "mae": "102.391241",
            "rmse": "432.812778",
            "status": "old status",
            "limitation": "stale hash claim",
        }
        provenance = {
            "entry": {"expected_sha256": "abc"},
            "actual_sha256": "abc",
            "saved_input_sha256": "abc",
            "identity_matches": True,
        }
        shown = annotate_saved_metric_provenance([metric], provenance)[0]
        for field in ("r2", "mae", "rmse"):
            self.assertEqual(shown[field], metric[field])
        self.assertIn("not freshly reproduced", shown["status"])
        self.assertEqual(metric["status"], "old status")


if __name__ == "__main__":
    unittest.main()
