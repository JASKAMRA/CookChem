from __future__ import annotations

import sys
import unittest
from pathlib import Path

STAGE_D = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STAGE_D / "src"))

from stage_d.mechanisms import (  # noqa: E402
    REVIEW_CRITERIA,
    MechanismContractError,
    build_mechanism_review_packet,
    build_mechanism_review_packets,
)


def minimal_candidate():
    raw = {
        "Evidence_ID": "SB-SYN-001",
        "Compound": "Synthetic compound",
        "Compound_ID": "SYNTHETIC-ID-NOT-APPROVED",
        "Drug": "Synthetic probe",
        "Mechanism": "Source-reported assay outcome",
        "Outcome": "Outcome kept verbatim",
        "Direction": "Direction kept verbatim",
        "Quantitative_Outcome": "3.2 +/- 0.2",
        "PMID": "00000000",
        "DOI": "10.0000/synthetic",
        "Source_URL": "https://example.invalid/primary",
        "Source_Locator": "Table 2",
        "Conflict_Group": "SYNTHETIC-CONFLICT",
        "Source_Title": "Synthetic primary study",
        "Authors": "Synthetic Author",
        "Year": "2026",
        "Study_Design": "In vitro assay",
        "Population": "Cell model",
        "Dose": "Source dose text",
        "Limitations": "Single-source limitation",
    }
    return {
        "schema_version": "1.0.0",
        "mechanism_record_id": "SBD-MECH-9999",
        "stage_b_reference": {
            "evidence_id": "SB-SYN-001",
            "release_id": "StageB_V20_20261103",
            "source_file_sha256": "a" * 64,
            "row_count_at_build": 1,
        },
        "raw_stage_b_record": raw,
        "mechanism_candidate": {
            "candidate_family": "membrane_transporter",
            "source_reported_target": "Synthetic target",
            "source_reported_relation": "unresolved_or_mixed",
            "classification_basis": "Candidate label remains pending review.",
            "classification_status": "pending_manual_review",
            "canonical_target_id": None,
        },
        "source_verification": {
            "doi": raw["DOI"],
            "pmid": raw["PMID"],
            "verified_source_url": "https://example.invalid/primary",
            "access_level": "primary_article_full_text_reviewed",
            "source_locator": "Results, Table 2",
            "verification_note": "Synthetic test fixture only.",
        },
        "source_outcome_classification": {
            "raw_outcome": raw["Outcome"],
            "raw_direction": raw["Direction"],
            "raw_conflict_group": raw["Conflict_Group"],
            "state": "conflicting",
            "reason_code": "explicit_conflict_group",
            "review_status": "pending_manual_review",
            "interpretation_boundary": "Synthetic label only; not a scientific conclusion.",
        },
        "review_criteria": {
            criterion: {"state": "not_assessed", "reason_codes": ["manual_review_required"]}
            for criterion in REVIEW_CRITERIA
        },
        "source_discrepancies": [{
            "code": "primary_source_endpoint_text_conflict",
            "status": "resolved_source_record_level",
            "observations": [{"locator": "Table 1", "summary": "Conflict A"}, {"locator": "Results", "summary": "Conflict B"}],
            "resolution": {
                "decision": "source_record_level_assignment",
                "selected_assignment": "Synthetic selected transcription",
                "conflicting_assignment": "Synthetic alternative transcription",
                "rationale": "Synthetic fixture; no real evidence is asserted.",
                "manual_review_status": "pending_manual_review",
                "scope": "Fixture only",
            },
        }],
        "review_reasons": [
            {"criterion": criterion, "code": "manual_review_required", "status": "open"}
            for criterion in REVIEW_CRITERIA
        ],
        "review_state": {
            "status": "pending_manual_review",
            "acceptance": "pending",
            "identity_adjudication": "not_performed",
        },
    }


class MechanismReviewPacketTests(unittest.TestCase):
    def test_packet_preserves_source_links_conflict_and_empty_reviewer_rationale(self):
        record = minimal_candidate()
        packet = build_mechanism_review_packet(record)
        self.assertEqual(packet["candidate_reference"]["evidence_id"], "SB-SYN-001")
        self.assertEqual(packet["candidate_reference"]["compound_id"], "SYNTHETIC-ID-NOT-APPROVED")
        self.assertEqual(packet["primary_source"]["doi"], "10.0000/synthetic")
        self.assertEqual(packet["primary_source"]["source_locator"], "Results, Table 2")
        self.assertEqual(packet["source_record"]["quantitative_outcome_text"], "3.2 +/- 0.2")
        self.assertEqual(packet["source_record"]["limitations_text"], "Single-source limitation")
        self.assertEqual(len(packet["source_discrepancies"]), 1)
        self.assertEqual(packet["review_state"], "PENDING_HUMAN_REVIEW")
        self.assertTrue(all(item["reviewer_rationale"] is None for item in packet["review_worksheet"]))
        packet["source_discrepancies"].append({"synthetic": True})
        self.assertEqual(len(record["source_discrepancies"]), 1)
        self.assertEqual(packet["candidate_reference"]["study_id"], "")
        self.assertEqual(packet["reviewer_evidence_assessment"]["supporting_findings"], [])
        self.assertEqual(packet["review_state"], "PENDING_HUMAN_REVIEW")

    def test_registry_pipeline_validates_source_linkage_and_all_records(self):
        record = minimal_candidate()
        registry = {
            "schema_version": "1.0.0",
            "release_id": "StageB_V20_20261103",
            "source_file": "synthetic-only.csv",
            "source_file_sha256": "a" * 64,
            "source_row_count": 1,
            "selected_record_count": 1,
            "records": [record],
        }
        packets = build_mechanism_review_packets(registry)
        self.assertEqual(len(packets), 1)
        self.assertEqual(packets[0]["candidate_reference"]["evidence_id"], "SB-SYN-001")
        registry["records"].append(record)
        registry["selected_record_count"] = 2
        with self.assertRaisesRegex(MechanismContractError, "must be unique"):
            build_mechanism_review_packets(registry)

    def test_registry_pipeline_rejects_registry_record_hash_mismatch(self):
        record = minimal_candidate()
        registry = {
            "schema_version": "1.0.0",
            "release_id": "StageB_V20_20261103",
            "source_file": "synthetic-only.csv",
            "source_file_sha256": "b" * 64,
            "source_row_count": 1,
            "selected_record_count": 1,
            "records": [record],
        }
        with self.assertRaisesRegex(MechanismContractError, "pinned source"):
            build_mechanism_review_packets(registry)


if __name__ == "__main__":
    unittest.main()
