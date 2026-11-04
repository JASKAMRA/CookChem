from __future__ import annotations

import sys
import unittest
from pathlib import Path

STAGE_D = Path(__file__).resolve().parents[1]
ROOT = STAGE_D.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(STAGE_D / "src"))

from stageD.scripts.build_human_review_register import build_register  # noqa: E402
from stage_d.evidence_queue import SOURCE_SHA256, SOURCE_RELEASE, build_queue_from_rows  # noqa: E402


def synthetic_review_queue():
    rows = []
    for index in range(1, 318):
        rows.append({
            "Evidence_ID": f"SB-SYN-{index:04d}", "Compound": f"Synthetic compound {index}",
            "Compound_ID": f"MOL-SYN-{index:04d}", "Drug": "Synthetic probe", "Evidence_Type": "In vitro",
            "Mechanism": "Synthetic assay", "Study_ID": f"STUDY-SYN-{index:04d}",
            "Study_Design": "Synthetic design", "Source_Title": f"Synthetic study {index}",
            "Outcome": "observed effect", "Direction": "synthetic", "Source_URL": "https://example.invalid/source",
            "Source_Locator": "Table 1", "PMID": "00000000", "DOI": f"10.0000/synthetic.{index}",
            "Identity_Status": "verified_exact", "Conflict_Group": "",
        })
    return build_queue_from_rows(rows, source_sha256=SOURCE_SHA256, source_release=SOURCE_RELEASE)


class HumanReviewRegisterTests(unittest.TestCase):
    def test_register_keeps_all_queue_rows_pending_and_decisions_empty(self):
        queue = synthetic_review_queue()
        registry = {
            "schema_version": "1.0.0",
            "release_id": "StageB_V20_20261103",
            "source_file_sha256": "a" * 64,
            "source_row_count": 317,
            "selected_record_count": 0,
            "records": [],
        }
        register = build_register(queue, registry, queue_digest="b" * 64, registry_digest="c" * 64)
        self.assertEqual(register["summary"]["evidence_records_pending"], 317)
        self.assertEqual(register["summary"]["mechanism_candidates_pending"], 0)
        self.assertTrue(all(row["status"] == "PENDING_HUMAN_REVIEW" for row in register["reviews"]))
        self.assertTrue(all(row["decision"] is None for row in register["reviews"]))
        self.assertTrue(all(row["authorization_evidence"] is None for row in register["reviews"]))


if __name__ == "__main__":
    unittest.main()
