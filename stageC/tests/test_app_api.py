from __future__ import annotations

import json
import io
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))
sys.path.insert(0, str(ROOT / "tests"))

from server import CookRiskHandler, CookRiskService, make_server  # noqa: E402
from test_recipe_engine import COMPOUNDS, FOOD, MAPPINGS, retention_evidence  # noqa: E402


SYNTHETIC_EVIDENCE = {
    "Evidence_ID": "SB-SYN-APP-001", "Compound": "Synthetic compound", "Compound_ID": "C-1",
    "Drug": "Synthetic probe", "Interaction_Effect": "Test-only source record",
    "Mechanism": "Not assessed", "Evidence_Type": "In vitro", "Evidence_Level": "compound",
    "Direction": "", "Quantitative_Outcome": "", "Dose": "", "Population": "Synthetic assay",
    "Study_Design": "Synthetic fixture", "Source_Title": "SYNTHETIC TEST ONLY",
    "Authors": "", "Year": "", "DOI": "", "PMID": "", "Source_Type": "synthetic",
    "Limitations": "Synthetic test fixture; not scientific evidence", "Confidence": "",
    "Notes": "", "Study_ID": "SYNTHETIC", "Source_URL": "", "Source_Cache": "",
    "Source_Locator": "synthetic fixture", "Preparation": "", "Co_Compounds": "",
    "Affected_Entity": "drug", "Perpetrator": "compound", "Outcome": "no significant effect",
    "Conflict_Group": "", "Identity_Status": "synthetic_unverified", "Release_Origin": "test",
    "Clinical_Extrapolation": "not assessed", "CookRisk_Exposure_Link": "not assessed",
}


def synthetic_service(review_action_path=None, review_backup_dir=None) -> CookRiskService:
    options = {}
    if review_action_path is not None:
        options["review_action_path"] = review_action_path
    if review_backup_dir is not None:
        options["review_backup_dir"] = review_backup_dir
    return CookRiskService(
        foods=FOOD, mappings=MAPPINGS, compounds=COMPOUNDS,
        phase1b={"release_id": "SYNTHETIC-TEST", "manifest_sha256": "a" * 64,
                 "stage_b_manifest_sha256": "a" * 64, "food_records": len(FOOD), "compounds": len(COMPOUNDS)},
        phase2_evidence={}, phase2={"release_id": "SYNTHETIC-TEST", "manifest_sha256": "b" * 64,
                                   "accepted_cooking_evidence": 0, "blocked_records": 1},
        phase4_evidence=[], stage_b_rows=[SYNTHETIC_EVIDENCE], stage_b_release="SYNTHETIC-TEST",
        stage_b_sha256="c" * 64, mechanisms=[], **options,
    )


class AppApiTests(unittest.TestCase):
    class Harness:
        _body_json = CookRiskHandler._body_json
        _json = CookRiskHandler._json
        _send = CookRiskHandler._send

        def __init__(self, path, service, payload=None):
            self.path = path
            self.service = service
            raw = json.dumps(payload).encode() if payload is not None else b""
            self.headers = {"Content-Length": str(len(raw))}
            self.rfile = io.BytesIO(raw)
            self.wfile = io.BytesIO()
            self.status = None
            self.response_headers = {}

        def send_response(self, status):
            self.status = status

        def send_header(self, key, value):
            self.response_headers[key] = value

        def end_headers(self):
            pass

    def get(self, path: str, service=None):
        harness = self.Harness(path, service or synthetic_service())
        CookRiskHandler.do_GET(harness)
        return harness.status, harness.response_headers, harness.wfile.getvalue()

    def post(self, path: str, payload: dict, service=None):
        harness = self.Harness(path, service or synthetic_service(), payload)
        CookRiskHandler.do_POST(harness)
        return harness.status, harness.response_headers, harness.wfile.getvalue()

    def test_local_application_and_catalog_serve_synthetic_test_inputs(self):
        _, _, page_body = self.get("/")
        page = page_body.decode()
        self.assertIn("Local research prototype", page)
        self.assertIn("Research use only", page)
        _, _, catalog_body = self.get("/api/catalog")
        catalog = json.loads(catalog_body)
        self.assertEqual(len(catalog["foods"]), len(FOOD))
        self.assertEqual(catalog["compounds"][0]["compound_id"], "C-1")

    def test_raw_recipe_calculates_and_csv_keeps_amounts_and_source_fields_separate(self):
        request = {
            "name": "Synthetic test recipe",
            "ingredients": [{"food_record_id": "F-1", "compound_id": "C-1", "quantity": "200", "unit": "g",
                             "serving_fraction": "0.5", "consumed_fraction": "0.5", "food_state": "raw"}],
            "servings_count": "1", "meal": {"servings_consumed": "1"},
        }
        _, _, body = self.post("/api/recipe/calculate", request)
        result = json.loads(body)
        estimate = result["recipe_result"]["ingredient_results"][0]
        self.assertEqual(Decimal(estimate["raw_reference_amount_mg"]), Decimal("0.5"))
        self.assertEqual(Decimal(estimate["consumed_amount_low_mg"]), Decimal("0.25"))
        self.assertEqual(Decimal(result["meal_result"]["compound_totals"][0]["consumed_amount_low_mg"]), Decimal("0.25"))
        self.assertEqual(result["recipe_result"]["uncertainty_gap_registry"]["output_count"], 1)
        self.assertEqual(result["recipe_result"]["multi_compound_interval_sensitivity"]["compound_reports"][0]["compound_id"], "C-1")
        _, _, csv_body = self.post("/api/export", {"format": "csv", "result": result["recipe_result"]})
        exported = csv_body.decode("utf-8-sig")
        self.assertIn("raw_reference_amount_mg", exported)
        self.assertIn("consumed_amount_low_mg", exported)
        self.assertIn("food_record_id", exported)

    def test_cooked_recipe_without_compatible_evidence_displays_no_cooked_number(self):
        request = {
            "name": "Synthetic cooked recipe",
            "ingredients": [{"food_record_id": "F-1", "compound_id": "C-1", "quantity": "200", "unit": "g",
                             "serving_fraction": "1", "consumed_fraction": "1", "food_state": "cooked",
                             "cooked_mass": "200"}],
            "cooking_method": "boil", "duration_min": "10", "cooking_medium": "water",
            "servings_count": "1", "meal": {"servings_consumed": "1"},
        }
        _, _, body = self.post("/api/recipe/calculate", request)
        result = json.loads(body)["recipe_result"]["ingredient_results"][0]
        self.assertEqual(result["cooked_exposure_status"], "UNAVAILABLE_NO_COMPATIBLE_PHASE2_EVIDENCE")
        self.assertEqual(result["consumed_amount_low_mg"], "")
        self.assertNotEqual(result["raw_reference_amount_mg"], "")

    def test_evidence_search_and_comparability_do_not_make_clinical_claims(self):
        _, _, evidence_body = self.get("/api/evidence?q=Synthetic%20compound")
        record = json.loads(evidence_body)["results"][0]
        self.assertEqual(record["finding_polarity"], "null")
        self.assertEqual(record["review_status"], "normalized_pending_review")
        pending = {key: None for key in (
            "compound_identity", "exposure_route", "dose_units_and_basis", "time_window",
            "population_or_model", "preparation_or_matrix",
        )}
        _, _, body = self.post("/api/comparability", {"evidence_id": "SB-SYN-APP-001", "criteria": pending})
        result = json.loads(body)
        self.assertEqual(result["comparability"]["decision"], "PENDING")
        self.assertEqual(result["clinical_interpretation"], "not_performed")

    def test_invalid_comparability_criteria_are_rejected(self):
        status, _, body = self.post("/api/comparability", {"evidence_id": "SB-SYN-APP-001", "criteria": {"compound_identity": True}})
        self.assertEqual(status, 400)
        self.assertIn("criteria mismatch", json.loads(body)["error"])

    def test_server_refuses_nonlocal_bind(self):
        with self.assertRaisesRegex(ValueError, "local machine"):
            make_server("0.0.0.0", 0, synthetic_service())

    def test_review_queue_api_keeps_machine_triage_separate_from_human_state(self):
        stage_d_root = ROOT.parent / "stageD"
        with tempfile.TemporaryDirectory(dir=stage_d_root) as temp_dir:
            service = synthetic_service(Path(temp_dir) / "empty_actions.jsonl", Path(temp_dir) / "backups")
            _, _, coverage_body = self.get("/api/review-coverage", service)
            coverage = json.loads(coverage_body)
            self.assertEqual(coverage["record_count"], 317)
            self.assertEqual(coverage["not_reviewed_record_count"], 317)
            self.assertEqual(coverage["audit_action_count"], 0)
            self.assertEqual(coverage["automatic_approval_count"], 0)
            self.assertEqual(coverage["automatic_negative_inference_count"], 0)

            _, _, queue_body = self.get("/api/review-queue?human_review_status=NOT_REVIEWED&limit=1", service)
            queue = json.loads(queue_body)
            self.assertEqual(queue["total_count"], 317)
            self.assertEqual(len(queue["records"]), 1)
            record = queue["records"][0]
            self.assertRegex(record["review_id"], r"^RV-[A-F0-9]{20}$")
            self.assertEqual(record["current_review_state"]["human_review_status"], "NOT_REVIEWED")
            self.assertEqual(record["current_review_state"]["source_verification_status"], "NOT_PERFORMED")
            self.assertFalse(queue["machine_triage_is_human_decision"])

            _, _, assignment_body = self.get("/api/review-assignment?human_review_status=NOT_REVIEWED", service)
            assignment = json.loads(assignment_body)["assignment"]
            self.assertEqual(assignment["record_count"], 317)
            self.assertFalse(assignment["purpose_and_limits"]["decisions_created"])

    def test_review_action_api_uses_separate_log_and_snapshots_history(self):
        stage_d_root = ROOT.parent / "stageD"
        with tempfile.TemporaryDirectory(dir=stage_d_root) as temp_dir:
            action_path = Path(temp_dir) / "synthetic_actions.jsonl"
            backup_dir = Path(temp_dir) / "backups"
            service = synthetic_service(action_path, backup_dir)
            _, _, queue_body = self.get("/api/review-queue?limit=1", service)
            record = json.loads(queue_body)["records"][0]
            action = {
                "review_id": record["review_id"], "evidence_id": record["source_reference"]["evidence_id"],
                "resulting_status": "SOURCE_VERIFIED", "reviewer_name": "SYNTHETIC_TEST_ONLY",
                "reviewer_role": "synthetic_test", "review_date": "2026-11-04",
                "source_locator": "SYNTHETIC_TEST_ONLY: app API test",
                "rationale": "SYNTHETIC_TEST_ONLY: verify API append, hash chain, and backup behavior",
            }
            status, _, body = self.post("/api/review-action", action, service)
            self.assertEqual(status, 200)
            response = json.loads(body)
            self.assertEqual(response["event"]["resulting_status"], "SOURCE_VERIFIED")
            self.assertEqual(response["current_review_state"]["action_count"], 1)
            self.assertEqual(response["backup"]["status"], "CREATED")
            self.assertTrue((backup_dir / Path(response["backup"]["path"]).name).is_file())
            coverage = service.review_coverage()
            self.assertEqual(coverage["reviewed_record_count"], 1)
            self.assertEqual(coverage["expert_accepted_count"], 0)
            self.assertEqual(coverage["automatic_approval_count"], 0)

            action["resulting_status"] = "EXPERT_ACCEPTED"
            action["reviewer_role"] = "synthetic_test"
            action["rationale"] = "SYNTHETIC_TEST_ONLY: expert acceptance must be gated"
            status, _, body = self.post("/api/review-action", action, service)
            self.assertEqual(status, 400)
            self.assertIn("prior READY_FOR_EXPERT_REVIEW", json.loads(body)["error"])
            self.assertEqual(len(service._review_snapshot()[1]), 1)


if __name__ == "__main__":
    unittest.main()
