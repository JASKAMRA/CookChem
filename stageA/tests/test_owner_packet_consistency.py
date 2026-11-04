"""Keep the Stage A RF owner packet, evidence matrix, and tracker aligned."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TRACKER = ROOT / "stageC" / "data" / "phase2" / "owner_decision_tracker.json"
TEMPLATE = ROOT / "stageC" / "reports" / "phase2" / "RETENTION_FINAL_OWNER_RESPONSE_TEMPLATE.md"
MATRIX = ROOT / "stageA" / "STAGE_A_RF01_RF15_EVIDENCE_MATRIX_2026-11-04.md"
HANDOFF = ROOT / "stageA" / "STAGE_A_RF01_RF15_HUMAN_DECISION_HANDOFF_2026-11-04.md"
EXPECTED_IDS = [f"RF-{number:02d}" for number in range(1, 16)]


class OwnerPacketConsistencyTests(unittest.TestCase):
    def test_tracker_and_all_three_handoffs_cover_exactly_fifteen_pending_decisions(self):
        tracker = json.loads(TRACKER.read_text(encoding="utf-8"))
        tracker_ids = [item["decision_id"] for item in tracker["decisions"]]
        self.assertEqual(tracker_ids, EXPECTED_IDS)
        self.assertEqual(tracker["overall_status"], "OPEN")
        self.assertTrue(all(item["approval_status"] == "PENDING" for item in tracker["decisions"]))

        template_ids = re.findall(r"^\|\s*(RF-\d{2})\s*\|", TEMPLATE.read_text(encoding="utf-8"), re.MULTILINE)
        matrix_ids = re.findall(r"^\|\s*(RF-\d{2})\s*\|", MATRIX.read_text(encoding="utf-8"), re.MULTILINE)
        handoff_ids = re.findall(r"^###\s+(RF-\d{2})\s+—", HANDOFF.read_text(encoding="utf-8"), re.MULTILINE)

        self.assertEqual(template_ids, EXPECTED_IDS)
        self.assertEqual(matrix_ids, EXPECTED_IDS)
        self.assertEqual(handoff_ids, EXPECTED_IDS)
        for decision_id in EXPECTED_IDS:
            with self.subTest(decision_id=decision_id):
                self.assertIn(f"owner response template row {decision_id}", HANDOFF.read_text(encoding="utf-8"))
                self.assertIn(f"evidence matrix row {decision_id}", HANDOFF.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
