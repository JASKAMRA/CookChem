from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
import unittest
from pathlib import Path

STAGE_D = Path(__file__).resolve().parents[1]
ROOT = STAGE_D.parent
sys.path.insert(0, str(STAGE_D / "src"))
PINNED_SCHEMA_DEPS = ROOT / "stageC" / ".test-deps"
if PINNED_SCHEMA_DEPS.is_dir():
    sys.path.insert(0, str(PINNED_SCHEMA_DEPS))

from stage_d.mechanisms import (  # noqa: E402
    CRITERION_STATES,
    REVIEW_CRITERIA,
    MechanismContractError,
    classify_source_outcome,
    validate_mechanism_record,
)


RELEASE = "StageB_V20_20261103"
SOURCE_RELATIVE = Path("stageB/release") / RELEASE / "data/interaction_evidence.csv"
REGISTRY_PATH = STAGE_D / "data" / "mechanism_evidence_registry.json"
SOURCED_IDS = {
    "SB-0003", "SB-0004", "SB-0005", "SB-0043", "SB-0044", "SB-0046", "SB-0047", "SB-0048",
    "SB-V14-008", "SB-V15-001", "SB-V15-002", "SB-V15-003", "SB-V15-004", "SB-V15-005",
    "SB-V15-006", "SB-V15-007", "SB-V15-008", "SB-V15-009", "SB-V15-010", "SB-V15-011",
    "SB-V17-001", "SB-V17-002", "SB-V17-003", "SB-V17-004", "SB-V17-007",
}


def synthetic_record() -> dict:
    raw = {
        "Evidence_ID": "SB-SYN-MECH-001",
        "Compound": "Synthetic food compound",
        "Compound_ID": "SYNTHETIC-ID-NOT-APPROVED",
        "Drug": "Synthetic probe",
        "Mechanism": "Synthetic source reports an enzyme probe effect",
        "Outcome": "synthetic observed effect",
        "Quantitative_Outcome": "synthetic value retained as text",
        "PMID": "00000000",
        "DOI": "10.0000/synthetic",
        "Source_URL": "https://example.invalid/primary",
        "Source_Locator": "Synthetic Table 1",
        "Evidence_Type": "In vitro",
        "Direction": "synthetic direction retained only as text",
        "Conflict_Group": "",
    }
    return {
        "schema_version": "1.0.0",
        "mechanism_record_id": "SBD-MECH-9999",
        "stage_b_reference": {
            "release_id": RELEASE,
            "source_file": SOURCE_RELATIVE.as_posix(),
            "source_file_sha256": "a" * 64,
            "row_count_at_build": 1,
            "evidence_id": raw["Evidence_ID"],
        },
        "raw_stage_b_record": raw,
        "mechanism_candidate": {
            "candidate_family": "drug_metabolizing_enzyme",
            "source_reported_target": "synthetic source target",
            "source_reported_relation": "unresolved_or_mixed",
            "classification_basis": "Synthetic fixture only.",
            "classification_status": "pending_manual_review",
            "canonical_target_id": None,
        },
        "source_verification": {
            "access_level": "primary_article_abstract_reviewed",
            "verified_source_url": "https://example.invalid/primary",
            "pmid": raw["PMID"],
            "doi": raw["DOI"],
            "pmcid": None,
            "source_locator": "Synthetic abstract",
            "verification_note": "Synthetic fixture; no source claim is made.",
        },
        "source_outcome_classification": {
            "raw_outcome": raw["Outcome"],
            "raw_direction": raw["Direction"],
            "raw_conflict_group": raw["Conflict_Group"],
            "state": "unclear",
            "reason_code": "source_text_requires_manual_interpretation",
            "review_status": "pending_manual_review",
            "interpretation_boundary": "Synthetic source-label grouping only.",
        },
        "review_criteria": {
            criterion: {"state": "not_assessed", "reason_codes": ["manual_review_required"]}
            for criterion in REVIEW_CRITERIA
        },
        "review_reasons": [
            {"criterion": criterion, "code": "manual_review_required", "status": "open"}
            for criterion in REVIEW_CRITERIA
        ],
        "source_discrepancies": [],
        "review_state": {
            "status": "pending_manual_review",
            "acceptance": "pending",
            "identity_adjudication": "not_performed",
            "reviewer": None,
            "reviewed_on": None,
        },
    }


def load_sourced_state():
    source_path = ROOT / SOURCE_RELATIVE
    source_bytes = source_path.read_bytes()
    source_rows = list(csv.DictReader(io.StringIO(source_bytes.decode("utf-8-sig"), newline="")))
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return source_path, source_bytes, source_rows, registry


class MechanismContractTests(unittest.TestCase):
    def test_synthetic_candidate_validates_and_cannot_be_auto_accepted(self):
        record = synthetic_record()
        validate_mechanism_record(record)
        self.assertEqual(record["review_state"]["acceptance"], "pending")
        self.assertEqual(record["review_state"]["identity_adjudication"], "not_performed")
        self.assertTrue(all(v["state"] in CRITERION_STATES for v in record["review_criteria"].values()))

    def test_numeric_criterion_score_is_rejected(self):
        record = synthetic_record()
        record["review_criteria"]["mechanistic_directness"] = 1
        with self.assertRaises(MechanismContractError):
            validate_mechanism_record(record)

    def test_automatic_acceptance_or_identity_assignment_is_rejected(self):
        for key, value in (("acceptance", "accepted"), ("identity_adjudication", "verified")):
            record = synthetic_record()
            record["review_state"][key] = value
            with self.subTest(key=key), self.assertRaises(MechanismContractError):
                validate_mechanism_record(record)

    def test_mismatched_source_identifiers_are_rejected(self):
        record = synthetic_record()
        record["source_verification"]["pmid"] = "12345678"
        with self.assertRaises(MechanismContractError):
            validate_mechanism_record(record)

    def test_null_negative_mixed_conflict_and_unclear_outcomes_stay_distinct(self):
        null = classify_source_outcome("null_finding", direction="increased exposure")
        negative = classify_source_outcome("no inhibition reported under tested microsomal conditions")
        mixed = classify_source_outcome("mixed: overall null and subgroup effect")
        conflict = classify_source_outcome("observed_effect", conflict_group="CONFLICT-17")
        labeled_conflict = classify_source_outcome("source_discrepancy_pending_adjudication")
        unclear = classify_source_outcome("effect direction requires full-text interpretation")
        self.assertEqual(null["state"], "null_or_non_significant")
        self.assertEqual(null["reason_code"], "explicit_null_or_non_significant_source_label")
        self.assertEqual(negative["state"], "negative_under_tested_conditions")
        self.assertEqual(mixed["state"], "mixed")
        self.assertEqual(conflict["state"], "conflicting")
        self.assertEqual(conflict["reason_code"], "explicit_conflict_group")
        self.assertEqual(labeled_conflict["state"], "conflicting")
        self.assertEqual(unclear["state"], "unclear")
        explicit_in_vitro = classify_source_outcome("observed_in_vitro_effect")
        self.assertEqual(explicit_in_vitro["state"], "reported_effect")
        self.assertEqual(explicit_in_vitro["reason_code"], "explicit_source_effect_label")
        self.assertTrue(all(x["review_status"] == "pending_manual_review" for x in (null, negative, mixed, conflict, labeled_conflict, unclear)))

    def test_registry_is_pinned_to_exact_stage_b_rows_and_file_digest(self):
        _, source_bytes, source_rows, registry = load_sourced_state()
        self.assertEqual(registry["release_id"], RELEASE)
        self.assertEqual(registry["source_row_count"], len(source_rows))
        self.assertEqual(registry["selected_record_count"], 25)
        digest = hashlib.sha256(source_bytes).hexdigest()
        self.assertEqual(registry["source_file_sha256"], digest)
        by_id = {row["Evidence_ID"]: row for row in source_rows}
        self.assertTrue(SOURCED_IDS.issubset(by_id))
        self.assertEqual({record["stage_b_reference"]["evidence_id"] for record in registry["records"]}, SOURCED_IDS)
        for record in registry["records"]:
            validate_mechanism_record(record)
            ref = record["stage_b_reference"]
            self.assertEqual(ref["source_file_sha256"], digest)
            self.assertEqual(ref["row_count_at_build"], len(source_rows))
            evidence_id = ref["evidence_id"]
            self.assertEqual(record["raw_stage_b_record"], by_id[evidence_id])
            self.assertEqual(record["raw_stage_b_record"]["Quantitative_Outcome"], by_id[evidence_id]["Quantitative_Outcome"])
            self.assertEqual(record["source_verification"]["pmid"], by_id[evidence_id]["PMID"])
            self.assertEqual(record["source_verification"]["doi"], by_id[evidence_id]["DOI"])
            self.assertEqual(record["review_state"]["status"], "pending_manual_review")
            self.assertEqual(record["review_state"]["acceptance"], "pending")
            self.assertTrue(all(item["state"] in CRITERION_STATES for item in record["review_criteria"].values()))
            self.assertTrue(all(item["reason_codes"] for item in record["review_criteria"].values()))

    def test_added_mechanism_classes_preserve_source_status_and_pending_review(self):
        _, _, _, registry = load_sourced_state()
        records = {r["stage_b_reference"]["evidence_id"]: r for r in registry["records"]}
        self.assertEqual(set(records), SOURCED_IDS)
        expected_relations = {
            "SB-0003": "inhibition_or_reduced_activity",
            "SB-0004": "inhibition_or_reduced_activity",
            "SB-0005": "inhibition_or_reduced_activity",
            "SB-0046": "inhibition_or_reduced_activity",
            "SB-0048": "inhibition_or_reduced_activity",
            "SB-V17-001": "inhibition_or_reduced_activity",
            "SB-V17-002": "inhibition_or_reduced_activity",
            "SB-V17-003": "inhibition_or_reduced_activity",
            "SB-V17-004": "inhibition_or_reduced_activity",
            "SB-V17-007": "inhibition_or_reduced_activity",
            "SB-V14-008": "inhibition_or_reduced_activity",
            "SB-V15-001": "inhibition_or_reduced_activity",
            "SB-V15-002": "inhibition_or_reduced_activity",
            "SB-V15-003": "inhibition_or_reduced_activity",
            "SB-V15-004": "unresolved_or_mixed",
            "SB-V15-005": "inhibition_or_reduced_activity",
            "SB-V15-006": "inhibition_or_reduced_activity",
            "SB-V15-007": "inhibition_or_reduced_activity",
            "SB-V15-008": "unresolved_or_mixed",
            "SB-V15-009": "unresolved_or_mixed",
            "SB-V15-010": "unresolved_or_mixed",
            "SB-V15-011": "unresolved_or_mixed",
            "SB-0043": "induction_or_increased_activity",
            "SB-0044": "induction_or_increased_activity",
            "SB-0047": "inhibition_or_reduced_activity",
        }
        for evidence_id, relation in expected_relations.items():
            record = records[evidence_id]
            self.assertEqual(record["mechanism_candidate"]["source_reported_relation"], relation)
            self.assertEqual(record["mechanism_candidate"]["classification_status"], "pending_manual_review")
            self.assertEqual(record["review_state"]["acceptance"], "pending")
            self.assertEqual(record["review_state"]["identity_adjudication"], "not_performed")
        self.assertEqual(records["SB-0043"]["source_verification"]["access_level"], "primary_article_abstract_reviewed")
        self.assertEqual(records["SB-0044"]["source_verification"]["access_level"], "primary_article_abstract_reviewed")
        self.assertTrue(all(
            records[evidence_id]["source_verification"]["access_level"] == "primary_article_full_text_reviewed"
            for evidence_id in {"SB-V17-001", "SB-V17-002", "SB-V17-003", "SB-V17-004", "SB-V17-007", "SB-V14-008", "SB-0047", *(f"SB-V15-{i:03d}" for i in range(1, 12))}
        ))
        self.assertIn("not a direct P-gp transport", records["SB-0044"]["mechanism_candidate"]["classification_basis"])
        self.assertIn("not attributed to an Allura Red dietary serving", records["SB-V14-008"]["source_verification"]["verification_note"])
        self.assertIn("animal absorption phenotype", records["SB-0047"]["source_verification"]["verification_note"])

    def test_cycle5_records_keep_transporter_assays_and_caco2_nulls_distinct(self):
        _, _, _, registry = load_sourced_state()
        records = {r["stage_b_reference"]["evidence_id"]: r for r in registry["records"]}
        direct_ids = {"SB-V15-001", "SB-V15-002", "SB-V15-003", "SB-V15-005", "SB-V15-006", "SB-V15-007"}
        null_ids = {"SB-V15-004", "SB-V15-008", "SB-V15-009", "SB-V15-010", "SB-V15-011"}
        for evidence_id in direct_ids | null_ids:
            record = records[evidence_id]
            self.assertEqual(record["source_verification"]["pmid"], "40773056")
            self.assertEqual(record["source_verification"]["doi"], "10.1021/acs.molpharmaceut.5c00705")
            self.assertEqual(record["source_verification"]["pmcid"], "PMC12406256")
            self.assertIn("Figure", record["source_verification"]["source_locator"])
            self.assertEqual(record["review_state"]["acceptance"], "pending")
            self.assertEqual(record["mechanism_candidate"]["classification_status"], "pending_manual_review")
        for evidence_id in direct_ids:
            self.assertEqual(records[evidence_id]["mechanism_candidate"]["candidate_family"], "membrane_transporter")
            self.assertIn("direct_transport_assay_still_requires_review", records[evidence_id]["review_criteria"]["mechanistic_directness"]["reason_codes"])
        for evidence_id in null_ids:
            self.assertEqual(records[evidence_id]["source_outcome_classification"]["state"], "null_or_non_significant")
            self.assertEqual(records[evidence_id]["mechanism_candidate"]["candidate_family"], "metabolism_or_transport_unresolved")
            self.assertTrue(any(token in records[evidence_id]["source_verification"]["verification_note"] for token in ("not a human or clinical null finding", "not a negative human interaction finding")))
        self.assertIn("fluorescence interference", records["SB-V15-001"]["source_verification"]["verification_note"])
        self.assertIn("quenching", records["SB-V15-006"]["source_verification"]["verification_note"])
        self.assertIn("65% OATP2B1 inhibition at 50 μM", records["SB-V15-007"]["source_verification"]["verification_note"])
        self.assertIn("no dose-response", records["SB-V15-007"]["source_verification"]["verification_note"])

    def test_berberine_losartan_target_disagreement_remains_open(self):
        _, _, source_rows, registry = load_sourced_state()
        source = next(row for row in source_rows if row["Evidence_ID"] == "SB-0005")
        record = next(r for r in registry["records"] if r["stage_b_reference"]["evidence_id"] == "SB-0005")
        self.assertEqual(record["raw_stage_b_record"], source)
        target = record["mechanism_candidate"]["source_reported_target"]
        self.assertIn("CYP2C9", target)
        self.assertIn("CYP2C19", target)
        self.assertIn("remains open", record["source_verification"]["verification_note"])
        self.assertEqual(record["source_discrepancies"], [])
        self.assertEqual(record["review_state"]["acceptance"], "pending")

    def test_reviewer_packets_are_prepared_but_unassigned(self):
        packet = STAGE_D / "reports" / "mechanism_reviewer_packets.md"
        content = packet.read_text(encoding="utf-8")
        self.assertIn("**Independent reviewer:** **not assigned**", content)
        self.assertIn("**Decision:** **pending**", content)
        for evidence_id in SOURCED_IDS:
            self.assertIn(f"`{evidence_id}`", content)

    def test_sourced_raw_outcomes_and_conflict_note_remain_unmodified(self):
        _, _, _, registry = load_sourced_state()
        by_id = {r["stage_b_reference"]["evidence_id"]: r for r in registry["records"]}
        self.assertIn("Table 1", by_id["SB-0003"]["raw_stage_b_record"]["Quantitative_Outcome"])
        self.assertIn("AUC0-24 increased", by_id["SB-0046"]["raw_stage_b_record"]["Quantitative_Outcome"])
        self.assertIn("full-text results prose assigns different values", by_id["SB-0046"]["raw_stage_b_record"]["Notes"])
        self.assertEqual(by_id["SB-0048"]["raw_stage_b_record"]["Quantitative_Outcome"], "Ki 0.70 +/- 0.41 micromolar.")
        discrepancy = by_id["SB-0046"]["source_discrepancies"][0]
        self.assertEqual(discrepancy["status"], "resolved_source_record_level")
        self.assertEqual(len(discrepancy["observations"]), 4)
        self.assertIn("2.0-fold at microdoses and 3.2-fold at therapeutic doses", discrepancy["observations"][0]["summary"])
        self.assertIn("3.2- and 1.8-fold larger in curcumin-treated groups at the microdose", discrepancy["observations"][1]["summary"])
        self.assertIn("43.5 ± 5.3; 79.4 ± 6.8", discrepancy["observations"][2]["summary"])
        self.assertIn("Therapeutic dose 5.89 ± 0.71; 19.0 ± 2.7", discrepancy["observations"][2]["summary"])
        self.assertIn("79.4/43.5 ≈ 1.83", discrepancy["resolution"]["selected_assignment"])
        self.assertEqual(discrepancy["resolution"]["manual_review_status"], "pending_manual_review")
        self.assertEqual(by_id["SB-0046"]["review_criteria"]["endpoint_reconciliation"]["state"], "meets")

    def test_source_text_adjudication_cannot_close_manual_review_or_change_raw_source(self):
        _, _, source_rows, registry = load_sourced_state()
        source = next(row for row in source_rows if row["Evidence_ID"] == "SB-0046")
        record = next(r for r in registry["records"] if r["stage_b_reference"]["evidence_id"] == "SB-0046")
        self.assertEqual(record["raw_stage_b_record"], source)
        self.assertEqual(record["review_state"]["acceptance"], "pending")
        self.assertEqual(record["review_state"]["status"], "pending_manual_review")
        self.assertEqual(record["source_discrepancies"][0]["status"], "resolved_source_record_level")
        self.assertEqual(record["source_discrepancies"][0]["resolution"]["manual_review_status"], "pending_manual_review")

    def test_formal_schemas_accept_registry_and_reject_unsafe_mutations(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("jsonschema is not installed")
        registry_schema = json.loads((STAGE_D / "schemas" / "mechanism_registry.schema.json").read_text(encoding="utf-8"))
        evidence_schema = json.loads((STAGE_D / "schemas" / "mechanism_evidence.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(registry_schema)
        Draft202012Validator.check_schema(evidence_schema)
        _, _, _, registry = load_sourced_state()
        Draft202012Validator(registry_schema).validate(registry)
        for record in registry["records"]:
            Draft202012Validator(evidence_schema).validate(record)
        invalid = json.loads(json.dumps(registry))
        invalid["records"][0]["review_state"]["acceptance"] = "accepted"
        self.assertTrue(list(Draft202012Validator(evidence_schema).iter_errors(invalid["records"][0])))
        invalid_criterion = json.loads(json.dumps(registry["records"][0]))
        invalid_criterion["review_criteria"]["human_exposure_relevance"] = 0.8
        self.assertTrue(list(Draft202012Validator(evidence_schema).iter_errors(invalid_criterion)))


if __name__ == "__main__":
    unittest.main()
