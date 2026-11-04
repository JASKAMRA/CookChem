from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from stageD.scripts.build_qualified_review_readiness_register import build_readiness_register  # noqa: E402


def synthetic_inputs():
    evidence = {
        "review_type": "evidence", "register_id": "SYN-E-1", "status": "PENDING_HUMAN_REVIEW",
        "source_reference": {"evidence_id": "E-SYN-1", "compound_id": "C-SYN-1", "study_id": "S-SYN-1",
                              "source_locator": "Table 1", "release_id": "Synthetic", "source_sha256": "a" * 64},
        "missing_evidence_fields": ["DOI"],
    }
    mechanism = {
        "review_type": "mechanism", "register_id": "SYN-M-1", "status": "PENDING_HUMAN_REVIEW",
        "source_reference": {"evidence_id": "E-SYN-2", "compound_id": "C-SYN-2", "study_id": "S-SYN-2",
                              "source_locator": "Figure 2", "access_level": "abstract", "release_id": "Synthetic",
                              "source_sha256": "b" * 64},
        "review_worksheet": [{"criterion": "identity", "reviewer_decision": None}],
    }
    queue = {"records": [{"review_id": "SYN-E-1", "source_record": {"Identity_Status": "synthetic pending"}}]}
    return {"reviews": [evidence, mechanism]}, queue


class QualifiedReviewReadinessRegisterTests(unittest.TestCase):
    def test_synthetic_records_remain_pending_with_blank_signoff(self):
        register, queue = synthetic_inputs()
        result = build_readiness_register(register, queue, review_register_sha256="c" * 64, queue_sha256="d" * 64)
        self.assertEqual(result["summary"]["evidence_records"], 1)
        self.assertEqual(result["summary"]["mechanism_candidates"], 1)
        self.assertEqual(result["summary"]["pending_reviews"], 2)
        self.assertEqual(result["summary"]["evidence_missing_metadata_fields"], {"DOI": 1})
        self.assertTrue(all(row["decision"] is None and row["approval_evidence"] is None for row in result["reviews"]))
        self.assertTrue(all(row["reviewer_identity"] is None for row in result["reviews"]))

    def test_missing_queue_link_fails_closed(self):
        register, queue = synthetic_inputs()
        queue["records"] = []
        with self.assertRaisesRegex(ValueError, "queue is missing review ID"):
            build_readiness_register(register, queue, review_register_sha256="c" * 64, queue_sha256="d" * 64)


if __name__ == "__main__":
    unittest.main()
