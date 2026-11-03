from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from stage_d.evidence_queue import (  # noqa: E402
    QueueValidationError,
    SOURCE_ROW_COUNT,
    SOURCE_SHA256,
    build_review_queue,
    stable_review_id,
    validate_review_queue,
)


class EvidenceQueueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.queue = build_review_queue()
        cls.records = cls.queue["records"]
        cls.by_id = {row["source_reference"]["evidence_id"]: row for row in cls.records}

    def test_all_pinned_source_rows_and_evidence_ids_are_preserved(self):
        self.assertEqual(len(self.records), SOURCE_ROW_COUNT)
        self.assertEqual(self.queue["source"]["sha256"], SOURCE_SHA256)
        self.assertEqual(self.queue["source"]["records_preserved"], SOURCE_ROW_COUNT)
        self.assertEqual(len(self.by_id), SOURCE_ROW_COUNT)
        self.assertEqual(self.queue["statistics"]["record_count"], SOURCE_ROW_COUNT)
        self.assertEqual(self.queue["statistics"]["human_review_state_counts"], {"NOT_REVIEWED": SOURCE_ROW_COUNT})

    def test_machine_triage_is_separate_from_human_review_and_does_not_verify_sources(self):
        self.assertTrue(all(row["machine_assessment"]["source_verification"] == "NOT_PERFORMED" for row in self.records))
        self.assertTrue(all(row["human_review"]["state"] == "NOT_REVIEWED" for row in self.records))
        self.assertFalse(self.queue["purpose_and_limits"]["machine_assessment_is_adjudication"])
        self.assertEqual(self.queue["statistics"]["source_verified_count"], 0)
        self.assertEqual(self.queue["statistics"]["expert_accepted_count"], 0)
        self.assertEqual(self.queue["statistics"]["expert_rejected_count"], 0)
        self.assertEqual(self.queue["statistics"]["finding_polarity_counts"].keys() & {"positive", "negative", "null", "conflicting", "unclear"},
                         set(self.queue["statistics"]["finding_polarity_counts"]))

    def test_review_ids_are_stable_opaque_and_source_scoped(self):
        first = self.records[0]
        evidence_id = first["source_reference"]["evidence_id"]
        expected = stable_review_id(evidence_id, SOURCE_SHA256)
        self.assertRegex(expected, r"^RV-[A-F0-9]{20}$")
        self.assertEqual(first["review_id"], expected)
        rebuilt = build_review_queue()
        self.assertEqual({row["review_id"] for row in rebuilt["records"]}, {row["review_id"] for row in self.records})
        self.assertNotEqual(stable_review_id(evidence_id, "0" * 64), expected)

    def test_explicit_source_conflicts_are_queued_without_inferred_conflicts(self):
        conflict_rows = [row for row in self.records if row["source_record"].get("Conflict_Group")]
        self.assertEqual(len(conflict_rows), self.queue["statistics"]["explicit_conflict_record_count"])
        self.assertTrue(all(row["machine_assessment"]["triage_state"] == "CONFLICT_REVIEW" for row in conflict_rows))
        self.assertTrue(all(row["machine_assessment"]["finding_polarity"] == "conflicting" for row in conflict_rows))
        self.assertEqual(len(self.queue["group_index"]["conflict_group"]),
                         self.queue["statistics"]["explicit_conflict_group_count"])
        for row in self.records:
            if not row["source_record"].get("Conflict_Group"):
                self.assertNotEqual(row["machine_assessment"]["triage_state"], "CONFLICT_REVIEW")

    def test_group_indexes_preserve_record_links_and_exact_duplicate_candidates_are_conservative(self):
        groups = self.queue["group_index"]
        self.assertEqual(set(groups), {
            "evidence_category", "compound", "drug_name", "source_and_study", "study",
            "source_reported_target_context", "conflict_group", "exact_duplicate_candidate",
        })
        for dimension, items in groups.items():
            for group in items:
                self.assertEqual(group["member_count"], len(group["member_evidence_ids"]))
                for evidence_id in group["member_evidence_ids"]:
                    self.assertEqual(self.by_id[evidence_id]["groups"][dimension], group["group_id"])
        duplicate_groups = groups["exact_duplicate_candidate"]
        self.assertTrue(all(group["member_count"] > 1 for group in duplicate_groups))
        self.assertTrue(all("candidate" in group["interpretation"].casefold() for group in duplicate_groups))

    def test_null_conflicting_unclear_and_unreviewed_records_cannot_be_mutated_to_negative(self):
        for target in ("null", "conflicting", "unclear", "positive"):
            source = next(row for row in self.records if row["machine_assessment"]["finding_polarity"] == target)
            mutated = copy.deepcopy(self.queue)
            record = next(row for row in mutated["records"] if row["source_reference"]["evidence_id"] == source["source_reference"]["evidence_id"])
            record["human_review"]["negative_evidence_assessment"] = "EXPLICIT_NEGATIVE_REVIEWED"
            with self.subTest(polarity=target), self.assertRaises(QueueValidationError):
                validate_review_queue(mutated)
        unreviewed_negative = next(row for row in self.records if row["machine_assessment"]["finding_polarity"] == "negative")
        mutated = copy.deepcopy(self.queue)
        record = next(row for row in mutated["records"] if row["source_reference"]["evidence_id"] == unreviewed_negative["source_reference"]["evidence_id"])
        record["human_review"]["negative_evidence_assessment"] = "EXPLICIT_NEGATIVE_REVIEWED"
        with self.assertRaisesRegex(QueueValidationError, "Unreviewed records"):
            validate_review_queue(mutated)

    def test_mutation_tests_reject_missing_duplicate_and_falsely_reviewed_rows(self):
        missing = copy.deepcopy(self.queue)
        missing["records"].pop()
        with self.assertRaisesRegex(QueueValidationError, "preserve every"):
            validate_review_queue(missing)

        duplicate = copy.deepcopy(self.queue)
        duplicate["records"][1]["source_reference"]["evidence_id"] = duplicate["records"][0]["source_reference"]["evidence_id"]
        with self.assertRaisesRegex(QueueValidationError, "unique"):
            validate_review_queue(duplicate)

        falsely_verified = copy.deepcopy(self.queue)
        falsely_verified["records"][0]["machine_assessment"]["source_verification"] = "SOURCE_VERIFIED"
        with self.assertRaisesRegex(QueueValidationError, "cannot claim source verification"):
            validate_review_queue(falsely_verified)

        unsupported_expert = copy.deepcopy(self.queue)
        unsupported_expert["records"][0]["human_review"].update({
            "state": "EXPERT_ACCEPTED",
            "reviewer_identity": "Synthetic Fixture Expert",
            "reviewed_at": "2026-11-04",
            "rationale": "Synthetic mutation test only",
            "cited_source_location": "Synthetic fixture locator",
        })
        # Complete fake fields cannot transform the immutable machine queue
        # into a reviewed source record; reviewer actions belong in the log.
        with self.assertRaisesRegex(QueueValidationError, "Generated queue records remain NOT_REVIEWED"):
            validate_review_queue(unsupported_expert)

        altered_review_id = copy.deepcopy(self.queue)
        altered_review_id["records"][0]["review_id"] = "RV-00000000000000000000"
        with self.assertRaisesRegex(QueueValidationError, "Stable review ID"):
            validate_review_queue(altered_review_id)

        wrong_group = copy.deepcopy(self.queue)
        wrong_group["group_index"]["compound"][0]["member_evidence_ids"].append("SB-DOES-NOT-EXIST")
        wrong_group["group_index"]["compound"][0]["member_count"] += 1
        with self.assertRaisesRegex(QueueValidationError, "invalid member references"):
            validate_review_queue(wrong_group)

    def test_generated_queue_artifact_matches_reproducible_builder(self):
        artifact = ROOT / "data" / "evidence_review_queue.json"
        if artifact.exists():
            parsed = json.loads(artifact.read_text(encoding="utf-8"))
            validate_review_queue(parsed)
            self.assertEqual(parsed, self.queue)

    def test_schema_is_valid_json_and_optional_draft_2020_12_check(self):
        schema_path = ROOT / "schemas" / "evidence_review_queue.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema is not installed")
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(self.queue, schema)
        broken = copy.deepcopy(self.queue)
        broken["purpose_and_limits"]["negative_evidence_inferred"] = True
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(broken, schema)


if __name__ == "__main__":
    unittest.main()
