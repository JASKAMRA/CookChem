from __future__ import annotations

import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

STAGE_D = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STAGE_D / "scripts"))
from build_reviewer_worklists import validate_registers, worklist_rows  # noqa: E402


def row(review_id, kind):
    return {"review_id": review_id, "review_type": kind,
            "identity_and_evidence": {"evidence_id": f"E-{review_id}", "compound_id": "MOL-SYN-1",
                                       "study_id": "STUDY-SYN-1", "source_locator": "Table 1",
                                       "release_id": "SYNTHETIC", "source_sha256": "a" * 64},
            "evidence_schema_reference": ("stageD/schemas/evidence_review_queue.schema.json" if kind == "evidence"
                                          else "stageD/schemas/mechanism_registry.schema.json"),
            "review_status": "PENDING_HUMAN_REVIEW", "reviewer_requirement": "qualified reviewer",
            "reviewer_identity": None, "reviewer_rationale": None, "decision": None, "approval_evidence": None,
            "unresolved_questions": ["synthetic check"], "missing_metadata_fields": []}


class ReviewerWorklistTests(unittest.TestCase):
    def test_pending_worklists_keep_reviewer_fields_blank(self):
        rows = [row("SYN-E-1", "evidence"), row("SYN-M-1", "mechanism")]
        evidence = worklist_rows({"reviews": rows}, "evidence")
        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0]["status"], "pending")
        self.assertEqual(evidence[0]["assigned_reviewer_subject_id"], "")
        self.assertEqual(evidence[0]["decision"], "")

    def test_register_mapping_checks_counts_references_and_pending_state(self):
        rows = [row(f"SYN-E-{i}", "evidence") for i in range(317)] + [row(f"SYN-M-{i}", "mechanism") for i in range(25)]
        v11 = {"register_version": "1.1.0", "reviews": rows}
        v12 = {"register_version": "1.2.0", "reviews": [dict(r) for r in rows],
               "supersedes": {"version": "1.1.0", "sha256": "b" * 64},
               "metadata_followup_summary": {"identifiers_added": 0, "scientific_or_review_status_changes": 0},
               "dummy": True}
        v12["reviews"][0]["unresolved_metadata"] = [{"field": "DOI", "status": "UNRESOLVED", "candidate_value": None}]
        for i in range(1, 5):
            v12["reviews"][i]["unresolved_metadata"] = [{"field": "DOI", "status": "UNRESOLVED", "candidate_value": None}]
        for i in range(5, 9):
            v12["reviews"][i]["unresolved_metadata"] = [{"field": "PMID", "status": "UNRESOLVED", "candidate_value": None}]
        v12["metadata_followup_summary"].update({"missing_doi_fields": 5, "missing_pmid_fields": 4})
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            predecessor = root / "stageD/reports/closure/qualified_review_readiness_register_v1.1.0.json"
            predecessor.parent.mkdir(parents=True)
            predecessor.write_text("synthetic predecessor bytes")
            schema = root / "stageD/schemas/evidence_review_queue.schema.json"
            schema.parent.mkdir(parents=True)
            schema.write_text("{}")
            (schema.parent / "mechanism_registry.schema.json").write_text("{}")
            # The hash chain is verified against the canonical project path in production.
            import build_reviewer_worklists as module
            old_stage_d = module.STAGE_D
            try:
                module.STAGE_D = root / "stageD"
                with mock.patch("build_reviewer_worklists.ROOT", root):
                    import hashlib
                    v12["supersedes"]["sha256"] = hashlib.sha256(predecessor.read_bytes()).hexdigest()
                    self.assertEqual(validate_registers(v11, v12, root / "stageD/schemas"), {"evidence": 317, "mechanism": 25})
            finally:
                module.STAGE_D = old_stage_d


if __name__ == "__main__":
    unittest.main()
