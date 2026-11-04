"""Local-only CookRisk prototype API and static application.

The service reads pinned Stage C releases and the Stage B evidence source,
then delegates all exposure calculations and comparability gates to the
existing Stage C/Stage D modules. It is intentionally not a production server.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
import threading
import uuid
from collections import defaultdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

APP_DIR = Path(__file__).resolve().parent
STAGE_C = APP_DIR.parent
PROJECT_ROOT = STAGE_C.parent
sys.path.insert(0, str(STAGE_C / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "stageD" / "src"))

from stage_c.exceptions import SourceIntegrityError, ValidationError  # noqa: E402
from stage_c.provenance import deterministic_id, sha256_file  # noqa: E402
from stage_c.recipe_engine import calculate_meal_exposure, calculate_recipe_exposure  # noqa: E402
from stage_c.release_adapters import (  # noqa: E402
    PHASE4_RELEASE,
    load_phase1b_v131_inputs,
    load_phase2_v030_evidence,
    load_phase4_context_evidence,
)
from stage_c.uncertainty import (  # noqa: E402
    assess_phase3_estimate_uncertainty,
    assess_phase3_structured_input_uncertainty,
    assess_phase3_uncertainty_coverage,
    build_uncertainty_gap_registry,
    rank_additive_interval_sensitivity,
    rank_multi_compound_interval_sensitivity,
)
from stage_d.contracts import (  # noqa: E402
    ContractError,
    evaluate_comparability,
    normalize_stage_b_record,
)
from stage_d.evidence_queue import build_review_queue  # noqa: E402
from stage_d.evidence_review_workflow import (  # noqa: E402
    ReviewWorkflowError,
    append_review_action,
    build_assignment_export,
    build_coverage_dashboard,
    filter_review_queue,
    verify_review_action_log,
)

EVIDENCE_RELEASE = "StageB_V20_20261103"
EVIDENCE_SHA256 = "5c095c6ee22d8d998888d3d47bc4ae2fcabf17faf4df0bee8aad7d6bb9af1cec"
EVIDENCE_CSV = PROJECT_ROOT / "stageB" / "release" / EVIDENCE_RELEASE / "data" / "interaction_evidence.csv"
EVIDENCE_REGISTRY = PROJECT_ROOT / "stageD" / "data" / "mechanism_evidence_registry.json"
REVIEW_ACTION_LOG = PROJECT_ROOT / "stageD" / "data" / "evidence_review_actions.jsonl"
REVIEW_BACKUP_DIR = PROJECT_ROOT / "stageD" / "data" / "phase5" / "backups"
# This local prototype has no trusted reviewer identity provider configured.
# Keep review submissions disabled until a real, trusted provider is integrated.
TRUSTED_REVIEW_IDENTITY_PROVIDER_CONFIGURED = False
COMPARABILITY_FIELDS = (
    "compound_identity", "exposure_route", "dose_units_and_basis",
    "time_window", "population_or_model", "preparation_or_matrix",
)
MASS_FIELDS = (
    "raw_mass", "prepared_mass", "cooked_mass", "edible_portion_mass",
    "discarded_portion_mass", "cooking_liquid_retained_mass",
    "cooking_liquid_discarded_mass", "cooking_oil_retained_mass",
    "cooking_oil_discarded_mass",
)
RECIPE_MASS_FIELDS = (*MASS_FIELDS, "batch_yield", "serving_mass", "leftovers_mass")


class ReviewAuthenticationUnavailable(RuntimeError):
    """Raised when reviewer actions cannot be authenticated safely."""


def _empty_mass_balance(fields: tuple[str, ...]) -> dict[str, dict[str, str]]:
    return {name: {"status": "not_reported"} for name in fields}


def _required_text(value: Any, label: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValidationError(f"{label} is required")
    return text


def build_recipe_request(request: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Convert concise UI inputs into the existing validated recipe contract."""
    ingredients_in = request.get("ingredients")
    if not isinstance(ingredients_in, list) or not ingredients_in:
        raise ValidationError("ingredients must contain at least one item")
    cooking_method = str(request.get("cooking_method") or "").strip()
    operation = None
    if cooking_method:
        operation = {
            "operation_id": "OP-1", "method": cooking_method,
            "duration_min": str(request.get("duration_min") or ""),
            "temperature_c": str(request.get("temperature_c") or ""),
            "medium": str(request.get("cooking_medium") or ""),
        }
        operation = {key: value for key, value in operation.items() if value != ""}

    ingredients: list[dict[str, Any]] = []
    for index, row in enumerate(ingredients_in, start=1):
        if not isinstance(row, dict):
            raise ValidationError(f"ingredients[{index - 1}] must be an object")
        food_id = _required_text(row.get("food_record_id"), f"ingredients[{index - 1}].food_record_id")
        compound_id = _required_text(row.get("compound_id"), f"ingredients[{index - 1}].compound_id")
        quantity = _required_text(row.get("quantity"), f"ingredients[{index - 1}].quantity")
        unit = _required_text(row.get("unit"), f"ingredients[{index - 1}].unit")
        ingredient_ops = [operation] if operation and str(row.get("food_state", "raw")) == "cooked" else []
        balance = _empty_mass_balance(MASS_FIELDS)
        cooked_mass = str(row.get("cooked_mass") or "").strip()
        if cooked_mass:
            balance["cooked_mass"] = {
                "status": "measured", "value": cooked_mass,
                "unit": str(row.get("cooked_mass_unit") or "g"),
                "source_reference": "user-entered measurement in local prototype",
            }
        ingredients.append({
            "ingredient_id": f"ING-{index:03d}",
            "food_record_id": food_id,
            "compound_ids": [compound_id],
            "quantity": {"value": quantity, "unit": unit},
            "food_state": str(row.get("food_state") or "raw"),
            "preparation_description": str(row.get("preparation_description") or "User-described preparation"),
            "serving_fraction": str(row.get("serving_fraction") or "1"),
            "consumed_fraction": str(row.get("consumed_fraction") or "1"),
            "mass_balance": balance,
            "cooking_operations": ingredient_ops,
            "provenance": {"capture_method": "local_prototype_user_input",
                           "uncertainty_inputs": row.get("uncertainty_inputs", {})},
        })

    servings = str(request.get("servings_count") or "1")
    operation_list = [operation] if operation else []
    raw_recipe = {
        "recipe_id": deterministic_id("R-APP", request),
        "name": str(request.get("name") or "User recipe").strip() or "User recipe",
        "ingredients": ingredients,
        "cooking_operations": operation_list,
        "servings_count": {"status": "measured", "value": servings},
        "mass_balance": _empty_mass_balance(RECIPE_MASS_FIELDS),
        "provenance": {"capture_method": "local_prototype_user_input", "nonproduction": True,
                       "uncertainty_inputs": request.get("recipe_uncertainty_inputs", {})},
    }
    meal = {
        "meal_id": deterministic_id("M-APP", {"recipe_id": raw_recipe["recipe_id"], "request": request.get("meal", {})}),
        "provenance": {"capture_method": "local_prototype_user_input", "nonproduction": True,
                       "uncertainty_inputs": (request.get("meal") or {}).get("uncertainty_inputs", {})},
        "components": [{
            "component_id": "MEAL-RECIPE-001", "kind": "recipe", "recipe_id": raw_recipe["recipe_id"],
            "servings_consumed": str((request.get("meal") or {}).get("servings_consumed") or "1"),
            "consumed_fraction": str((request.get("meal") or {}).get("consumed_fraction") or "1"),
            "leftovers_servings_consumed": str((request.get("meal") or {}).get("leftovers_servings_consumed") or "0"),
        }],
    }
    return raw_recipe, meal


def _csv_safe(value: Any) -> str:
    text = "" if value is None else str(value)
    if text.startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + text
    return text


def render_csv(output: dict[str, Any]) -> str:
    """Flatten estimate rows without mixing units or discarding source IDs."""
    estimates = output.get("ingredient_results")
    if estimates is None:
        estimates = [row for component in output.get("component_results", [])
                     for row in component.get("ingredient_results", [])]
    columns = (
        "estimate_id", "ingredient_id", "food_record_id", "compound_id", "calculation_status",
        "estimate_type", "food_state", "raw_reference_amount_mg", "consumed_amount_low_mg",
        "consumed_amount_high_mg", "cooked_exposure_status", "retention_evidence_id",
        "input_source_ids", "source_title", "source_url", "stage_b_manifest_sha256",
    )
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for estimate in estimates or []:
        provenance = estimate.get("provenance") if isinstance(estimate.get("provenance"), dict) else {}
        row = {key: estimate.get(key, "") for key in columns}
        row.update({
            "input_source_ids": ";".join(estimate.get("input_source_ids", [])),
            "source_title": provenance.get("food_source_title", ""),
            "source_url": provenance.get("food_source_url", ""),
            "stage_b_manifest_sha256": estimate.get("stage_b_manifest_sha256", ""),
        })
        writer.writerow({key: _csv_safe(value) for key, value in row.items()})
    return stream.getvalue()


class CookRiskService:
    """Dependency container; injectable synthetic fixtures are test-only."""

    def __init__(self, *, foods=None, mappings=None, compounds=None, phase1b=None,
                 phase2_evidence=None, phase2=None, phase4_evidence=None,
                 phase4_status=None,
                 stage_b_rows=None, stage_b_release=EVIDENCE_RELEASE,
                 stage_b_sha256=EVIDENCE_SHA256, mechanisms=None,
                 review_action_path=REVIEW_ACTION_LOG, review_backup_dir=REVIEW_BACKUP_DIR):
        self.foods = foods
        self.mappings = mappings
        self.compounds = compounds
        self.phase1b = phase1b
        self.phase2_evidence = phase2_evidence
        self.phase2 = phase2
        self.phase4_evidence = phase4_evidence
        self.phase4_status = phase4_status
        self.stage_b_rows = stage_b_rows
        self.stage_b_release = stage_b_release
        self.stage_b_sha256 = stage_b_sha256
        self.mechanisms = mechanisms
        self.review_action_path = Path(review_action_path)
        self.review_backup_dir = Path(review_backup_dir)
        self.review_queue = None
        self.review_lock = threading.RLock()

    def load(self) -> "CookRiskService":
        if self.foods is None:
            self.foods, self.mappings, self.compounds, self.phase1b = load_phase1b_v131_inputs()
        if self.phase2_evidence is None:
            self.phase2_evidence, self.phase2 = load_phase2_v030_evidence()
        if self.phase4_evidence is None:
            try:
                self.phase4_evidence, self.phase4_status = load_phase4_context_evidence()
            except SourceIntegrityError as exc:
                # Phase 4 context is optional to the food/exposure workflow. Keep
                # its integrity gate fail-closed while allowing unrelated pinned
                # inputs to load with an explicit degraded-health warning.
                self.phase4_evidence = []
                self.phase4_status = {
                    "release_id": PHASE4_RELEASE,
                    "status": "BLOCKED_INTEGRITY",
                    "manifest_verified": False,
                    "selected_context_record_count": 0,
                    "error": str(exc),
                }
        elif self.phase4_status is None:
            self.phase4_status = {
                "release_id": PHASE4_RELEASE,
                "status": "PRELOADED_UNVERIFIED",
                "manifest_verified": False,
                "selected_context_record_count": len(self.phase4_evidence),
            }
        if self.stage_b_rows is None:
            if not EVIDENCE_CSV.is_file() or sha256_file(EVIDENCE_CSV) != self.stage_b_sha256:
                raise SourceIntegrityError("Pinned Stage B evidence source is missing or its SHA-256 changed")
            with EVIDENCE_CSV.open(encoding="utf-8-sig", newline="") as stream:
                self.stage_b_rows = list(csv.DictReader(stream))
            if len(self.stage_b_rows) != 317:
                raise SourceIntegrityError("Pinned Stage B evidence row count is not 317")
        if self.mechanisms is None:
            registry = json.loads(EVIDENCE_REGISTRY.read_text(encoding="utf-8"))
            self.mechanisms = registry.get("records", [])
        return self

    @property
    def ready(self) -> bool:
        return all(value is not None for value in (self.foods, self.mappings, self.compounds,
                                                   self.phase1b, self.phase2_evidence,
                                                   self.phase2, self.phase4_status,
                                                   self.stage_b_rows, self.mechanisms))

    def health(self) -> dict[str, Any]:
        self.load()
        phase4_status = dict(self.phase4_status or {})
        phase4_blocked = phase4_status.get("status") == "BLOCKED_INTEGRITY"
        return {
            "status": "DEGRADED_PHASE4_CONTEXT_UNAVAILABLE" if phase4_blocked else "NON_PRODUCTION_LOCAL_PROTOTYPE",
            "stage_a_inference": "not_run",
            "stage_b_source": {"release_id": self.stage_b_release, "sha256": self.stage_b_sha256,
                               "rows": len(self.stage_b_rows), "read_only": True},
            "phase1b": {key: self.phase1b.get(key) for key in ("release_id", "manifest_sha256", "food_records", "compounds")},
            "phase2": {key: self.phase2.get(key) for key in ("release_id", "manifest_sha256", "accepted_cooking_evidence", "blocked_records")},
            "phase4_context": {
                "release_id": phase4_status.get("release_id", PHASE4_RELEASE),
                "status": phase4_status.get("status", "NOT_REPORTED"),
                "manifest_verified": bool(phase4_status.get("manifest_verified", False)),
                "records_loaded": len(self.phase4_evidence),
                "error": phase4_status.get("error"),
            },
            "evidence_context_records": len(self.phase4_evidence),
            "mechanism_candidates": len(self.mechanisms),
            "clinical_interpretation": "not_performed",
            "warnings": (["Phase 4 contextual evidence was withheld because its pinned release failed integrity verification."]
                         if phase4_blocked else []),
        }

    def _review_snapshot(self):
        """Load a fresh, source-verified immutable queue and its separate action history."""
        with self.review_lock:
            if not EVIDENCE_CSV.is_file() or sha256_file(EVIDENCE_CSV) != EVIDENCE_SHA256:
                raise SourceIntegrityError("Pinned Stage B source is missing or its SHA-256 changed")
            if self.review_queue is None:
                self.review_queue = build_review_queue()
            events = verify_review_action_log(self.review_action_path, self.review_queue)
            return self.review_queue, events

    @staticmethod
    def _review_state(queue_record, events):
        review_id = queue_record["review_id"]
        history = [event for event in events if event["review_id"] == review_id]
        status = history[-1]["resulting_status"] if history else "NOT_REVIEWED"
        nonterminal = ["SOURCE_VERIFIED", "IDENTITY_PENDING", "CONTEXT_PENDING", "CONFLICT_REVIEW"]
        if status == "NOT_REVIEWED":
            allowed = ["SOURCE_VERIFIED", "IDENTITY_PENDING", "CONTEXT_PENDING", "CONFLICT_REVIEW"]
        elif status in {"EXPERT_ACCEPTED", "EXPERT_REJECTED"}:
            allowed = []
        elif status == "SOURCE_VERIFIED":
            allowed = [*nonterminal, "READY_FOR_EXPERT_REVIEW"]
        elif status == "READY_FOR_EXPERT_REVIEW":
            allowed = [*nonterminal, "EXPERT_ACCEPTED", "EXPERT_REJECTED"]
        else:
            allowed = list(nonterminal)
        source_verified = any(event["resulting_status"] in {
            "SOURCE_VERIFIED", "READY_FOR_EXPERT_REVIEW", "EXPERT_ACCEPTED", "EXPERT_REJECTED"
        } for event in history)
        return {
            "review_id": review_id,
            "evidence_id": queue_record["source_reference"]["evidence_id"],
            "human_review_status": status,
            "source_verification_status": "SOURCE_VERIFIED" if source_verified else "NOT_PERFORMED",
            "action_count": len(history),
            "latest_action": history[-1] if history else None,
            "review_history": history,
            "allowed_next_statuses": allowed,
        }

    def review_queue_search(self, filters: dict[str, str], *, limit: int = 80, offset: int = 0):
        queue, events = self._review_snapshot()
        selected = filter_review_queue(queue, events=events, **filters)
        page = selected[offset:offset + limit]
        records = []
        for row in page:
            view = dict(row)
            view["current_review_state"] = self._review_state(row, events)
            records.append(view)
        return {
            "source": {
                "release_id": queue["source"]["release_id"],
                "sha256": queue["source"]["sha256"],
                "record_count": len(queue["records"]),
            },
            "total_count": len(selected),
            "limit": limit,
            "offset": offset,
            "filters": filters,
            "records": records,
            "machine_triage_is_human_decision": False,
        }

    def review_coverage(self):
        queue, events = self._review_snapshot()
        return build_coverage_dashboard(queue, events)

    def review_assignment(self, filters: dict[str, str], *, assigned_to: str | None = None):
        queue, events = self._review_snapshot()
        return build_assignment_export(queue, events=events, filters=filters, assigned_to=assigned_to)

    def _backup_review_history(self, event):
        """Snapshot each committed history version; backups are confined to Stage D."""
        try:
            stage_d_root = (PROJECT_ROOT / "stageD").resolve(strict=True)
            backup_dir = self.review_backup_dir
            backup_dir.resolve(strict=False).relative_to(stage_d_root)
            for candidate in (backup_dir, *backup_dir.parents):
                if candidate.exists() and candidate.is_symlink():
                    raise OSError("Review backup path cannot traverse symbolic links")
            if not self.review_action_path.is_file():
                raise OSError("Committed action log is missing")
            content = self.review_action_path.read_bytes()
            if not content.endswith(b"\n"):
                raise OSError("Committed action log is missing its final newline")
            final_event = json.loads(content.decode("utf-8").splitlines()[-1])
            if final_event.get("event_sha256") != event.get("event_sha256"):
                raise OSError("Backup snapshot does not end at the committed action")
            digest = hashlib.sha256(content).hexdigest()
            filename = f"review_actions_{int(event['sequence']):06d}_{event['event_sha256'][:12]}.jsonl"
            destination = backup_dir / filename
            if destination.is_symlink():
                raise OSError("Review backup destination cannot be a symbolic link")
            backup_dir.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                if destination.read_bytes() != content:
                    raise OSError("Existing review backup does not match the committed history")
                status = "ALREADY_PRESENT"
            else:
                temporary = backup_dir / f".{filename}.{uuid.uuid4().hex}.tmp"
                try:
                    with temporary.open("xb") as stream:
                        stream.write(content)
                        stream.flush()
                        os.fsync(stream.fileno())
                    if destination.exists():
                        if destination.read_bytes() != content:
                            raise OSError("Review backup destination appeared with different content")
                        temporary.unlink()
                        status = "ALREADY_PRESENT"
                    else:
                        os.replace(temporary, destination)
                        status = "CREATED"
                finally:
                    if temporary.exists():
                        temporary.unlink()
            return {"status": status, "path": str(destination.relative_to(PROJECT_ROOT)), "sha256": digest}
        except (OSError, ValueError) as exc:
            return {"status": "FAILED", "reason": str(exc)}

    def submit_review_action(self, action: dict[str, Any]):
        if not TRUSTED_REVIEW_IDENTITY_PROVIDER_CONFIGURED:
            raise ReviewAuthenticationUnavailable(
                "Review submission is disabled because no trusted identity provider is configured"
            )
        with self.review_lock:
            if not EVIDENCE_CSV.is_file() or sha256_file(EVIDENCE_CSV) != EVIDENCE_SHA256:
                raise SourceIntegrityError("Pinned Stage B source is missing or its SHA-256 changed")
            queue = self.review_queue or build_review_queue()
            self.review_queue = queue
            event = append_review_action(self.review_action_path, queue, action)
            backup = self._backup_review_history(event)
            events = verify_review_action_log(self.review_action_path, queue)
            record = next(row for row in queue["records"] if row["review_id"] == event["review_id"])
            return {
                "event": event,
                "current_review_state": self._review_state(record, events),
                "coverage": build_coverage_dashboard(queue, events),
                "backup": backup,
                "clinical_interpretation": "not_performed",
            }

    def food_search(self, query: str = "", limit: int = 80) -> list[dict[str, Any]]:
        self.load()
        term = query.casefold().strip()
        results = []
        for food_id, row in self.foods.items():
            if term and term not in " ".join(str(row.get(key, "")) for key in ("food_record_id", "food_name", "food_category", "source_title")).casefold():
                continue
            maps = [mapping for mapping in self.mappings if mapping.get("food_record_id") == food_id]
            results.append({
                "food_record_id": food_id, "food_name": row.get("food_name", ""),
                "raw_or_processed_state": row.get("raw_or_processed_state", ""),
                "reported_concentration": row.get("reported_concentration", ""),
                "reported_unit": row.get("reported_unit", ""),
                "normalized_concentration": row.get("normalized_concentration", ""),
                "normalized_unit": row.get("normalized_unit", ""),
                "source_title": row.get("source_title", ""), "source_url": row.get("source_url", ""),
                "source_verification_status": row.get("source_verification_status", ""),
                "compound_ids": sorted({mapping.get("compound_id", "") for mapping in maps if mapping.get("compound_id")}),
            })
            if len(results) >= limit:
                break
        return results

    def evidence_search(self, query: str = "", category: str = "", limit: int = 80) -> list[dict[str, Any]]:
        self.load()
        term, wanted = query.casefold().strip(), category.casefold().strip()
        by_evidence = {str(row.get("stage_b_reference", {}).get("evidence_id", "")): row for row in self.mechanisms}
        results = []
        for raw in self.stage_b_rows:
            normalized = normalize_stage_b_record(raw, stage_b_release=self.stage_b_release,
                                                  stage_b_manifest_sha256=self.stage_b_sha256)
            values = " ".join(str(value) for value in raw.values()).casefold()
            cat = str(normalized.get("study_type", {}).get("normalized_category", ""))
            if term and term not in values:
                continue
            if wanted and wanted not in {str(raw.get("Evidence_Type", "")).casefold(), cat.casefold()}:
                continue
            results.append({"evidence_id": raw.get("Evidence_ID", ""), "compound_id": raw.get("Compound_ID", ""),
                            "compound": raw.get("Compound", ""), "drug": raw.get("Drug", ""),
                            "evidence_type": raw.get("Evidence_Type", ""), "study_category": cat,
                            "finding_polarity": normalized.get("finding", {}).get("polarity", "unclear"),
                            "raw_outcome": raw.get("Outcome", ""), "direction": raw.get("Direction", ""),
                            "quantitative_outcome": raw.get("Quantitative_Outcome", ""), "dose": raw.get("Dose", ""),
                            "population": raw.get("Population", ""), "study_design": raw.get("Study_Design", ""),
                            "source_title": raw.get("Source_Title", ""), "authors": raw.get("Authors", ""),
                            "year": raw.get("Year", ""), "doi": raw.get("DOI", ""), "pmid": raw.get("PMID", ""),
                            "source_url": raw.get("Source_URL", ""), "source_locator": raw.get("Source_Locator", ""),
                            "limitations": raw.get("Limitations", ""), "identity_status": raw.get("Identity_Status", ""),
                            "conflict_group": raw.get("Conflict_Group", ""),
                            "review_status": normalized.get("review_state", {}).get("evidence_review", "normalized_pending_review"),
                            "mechanism_candidate": by_evidence.get(raw.get("Evidence_ID", ""), {})})
            if len(results) >= limit:
                break
        return results

    def calculate_recipe(self, request: dict[str, Any]) -> dict[str, Any]:
        self.load()
        recipe, meal = build_recipe_request(request)
        recipe_result = calculate_recipe_exposure(
            recipe, self.foods, self.mappings, self.compounds, self.phase2_evidence,
            stage_b_manifest_sha256=self.phase1b["stage_b_manifest_sha256"],
            phase2_release_metadata=self.phase2,
        )
        meal_result = calculate_meal_exposure(
            meal, {recipe["recipe_id"]: recipe}, self.foods, self.mappings,
            self.compounds, self.phase2_evidence,
            stage_b_manifest_sha256=self.phase1b["stage_b_manifest_sha256"],
            phase2_release_metadata=self.phase2,
        )
        return {"recipe": recipe, "recipe_result": self._with_uncertainty(recipe_result),
                "meal": meal, "meal_result": self._with_uncertainty(meal_result),
                "release_context": {"phase1b": self.phase1b, "phase2": self.phase2,
                                    "stage_b_release": self.stage_b_release,
                                    "stage_b_manifest_sha256": self.stage_b_sha256},
                "clinical_interpretation": "not_performed"}

    def calculate_meal(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.load()
        meal, recipes = payload.get("meal"), payload.get("recipes")
        if not isinstance(meal, dict) or not isinstance(recipes, dict):
            raise ValidationError("meal and recipes objects are required")
        output = calculate_meal_exposure(
            meal, recipes, self.foods, self.mappings, self.compounds, self.phase2_evidence,
            stage_b_manifest_sha256=self.phase1b["stage_b_manifest_sha256"],
            phase2_release_metadata=self.phase2,
        )
        return {"meal": meal, "meal_result": self._with_uncertainty(output),
                "release_context": {"phase1b": self.phase1b, "phase2": self.phase2},
                "clinical_interpretation": "not_performed"}

    @staticmethod
    def _with_uncertainty(output: dict[str, Any]) -> dict[str, Any]:
        result = dict(output)
        coverage = assess_phase3_uncertainty_coverage(output)
        estimates = output.get("ingredient_results")
        if estimates is None:
            estimates = [row for component in output.get("component_results", [])
                         for row in component.get("ingredient_results", [])]
        assessments = [assess_phase3_estimate_uncertainty(row) for row in estimates]
        structured = [assess_phase3_structured_input_uncertainty(row) for row in estimates]
        estimate_compounds = {str(row.get("estimate_id", "")): str(row.get("compound_id", "")) for row in estimates}

        def grouped_sensitivity(items):
            groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for item in items:
                groups[estimate_compounds.get(str(item.get("estimate_id", "")), "")].append(item)
            return [{"compound_id": compound_id,
                     "analysis": rank_additive_interval_sensitivity(contributors, output_id=coverage.get("output_id", ""))}
                    for compound_id, contributors in sorted(groups.items())]

        result["uncertainty_coverage"] = coverage
        result["uncertainty_gap_registry"] = build_uncertainty_gap_registry([output])
        result["ingredient_uncertainty"] = assessments
        result["structured_input_uncertainty"] = structured
        result["interval_sensitivity_by_compound"] = grouped_sensitivity(assessments) if assessments else []
        result["structured_input_sensitivity_by_compound"] = grouped_sensitivity(structured) if structured else []
        result["multi_compound_interval_sensitivity"] = (
            rank_multi_compound_interval_sensitivity(assessments, output_id=coverage.get("output_id", ""))
            if assessments else {"compound_reports": []})
        result["multi_compound_structured_input_sensitivity"] = (
            rank_multi_compound_interval_sensitivity(structured, output_id=coverage.get("output_id", ""))
            if structured else {"compound_reports": []})
        return result

    def comparability(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.load()
        evidence_id = _required_text(payload.get("evidence_id"), "evidence_id")
        raw = next((row for row in self.stage_b_rows if row.get("Evidence_ID") == evidence_id), None)
        if raw is None:
            raise ContractError(f"Unknown Evidence_ID {evidence_id}")
        criteria = payload.get("criteria")
        if not isinstance(criteria, dict):
            raise ContractError("criteria object is required")
        normalized = normalize_stage_b_record(raw, stage_b_release=self.stage_b_release,
                                              stage_b_manifest_sha256=self.stage_b_sha256)
        gate = evaluate_comparability(criteria)
        return {"evidence_id": evidence_id, "normalized_evidence": normalized,
                "source_record": raw, "comparability": gate,
                "cross_stage_linkage": "not_performed_without_a_verified_published_phase3_estimate",
                "clinical_interpretation": "not_performed"}


_DEFAULT_SERVICE = CookRiskService()


class CookRiskHandler(BaseHTTPRequestHandler):
    service = _DEFAULT_SERVICE
    server_version = "CookRiskPrototype/0.1"

    def log_message(self, _format: str, *args: Any) -> None:
        # Local scientific inputs should not be copied to routine console logs.
        return

    def _send(self, body: bytes, content_type: str, status: int = 200, headers: dict[str, str] | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, payload: Any, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2, default=str).encode("utf-8")
        self._send(body, "application/json; charset=utf-8", status)

    def _body_json(self) -> dict[str, Any]:
        raw_length = self.headers.get("Content-Length", "0")
        try:
            length = int(raw_length)
        except ValueError:
            raise ValidationError("Content-Length must be an integer") from None
        if length < 0 or length > 1_000_000:
            raise ValidationError("Request body exceeds the 1 MB local prototype limit")
        try:
            value = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise ValidationError("Request body must be valid UTF-8 JSON") from None
        if not isinstance(value, dict):
            raise ValidationError("Request JSON must be an object")
        return value

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        try:
            if parsed.path == "/" or parsed.path == "/index.html":
                self._send((APP_DIR / "static" / "index.html").read_bytes(), "text/html; charset=utf-8")
                return
            if parsed.path in {"/app.js", "/style.css"}:
                name = parsed.path.lstrip("/")
                mime = "text/javascript; charset=utf-8" if name.endswith(".js") else "text/css; charset=utf-8"
                self._send((APP_DIR / "static" / name).read_bytes(), mime)
                return
            if parsed.path == "/api/health":
                self._json(self.service.health())
                return
            if parsed.path == "/api/catalog":
                self.service.load()
                self._json({"foods": self.service.food_search(limit=600),
                            "compounds": [{"compound_id": key, "name": value.get("Canonical_Name", ""),
                                           "identity_status": value.get("StageC_Identity_Verification_Status", "")}
                                          for key, value in sorted(self.service.compounds.items())],
                            "units": ["g", "kg", "mg", "ug", "mL", "L"]})
                return
            if parsed.path == "/api/foods":
                self._json({"results": self.service.food_search(query.get("q", [""])[0], _limit(query))})
                return
            if parsed.path == "/api/evidence":
                self._json({"results": self.service.evidence_search(
                    query.get("q", [""])[0], query.get("category", [""])[0], _limit(query))})
                return
            if parsed.path == "/api/review-queue":
                filters = _review_filters(query)
                self._json(self.service.review_queue_search(
                    filters, limit=_limit(query), offset=_offset(query)))
                return
            if parsed.path == "/api/review-coverage":
                self._json(self.service.review_coverage())
                return
            if parsed.path == "/api/review-assignment":
                filters = _review_filters(query)
                assignment = self.service.review_assignment(
                    filters, assigned_to=query.get("assigned_to", [None])[0])
                if query.get("format", ["json"])[0].casefold() == "csv":
                    columns = [
                        "assignment_id", "source_release_id", "source_sha256", "assigned_to",
                        "review_id", "evidence_id", "compound_id", "compound_source_label", "drug_source_label",
                        "study_id", "source_title", "evidence_category", "outcome_polarity_machine_triage",
                        "machine_triage_state", "identity_source_label", "source_verification_status",
                        "conflict_group", "source_url", "doi", "pmid", "source_locator", "review_status",
                    ]
                    stream = io.StringIO(newline="")
                    writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
                    writer.writeheader()
                    provenance = {
                        "assignment_id": assignment["assignment_id"],
                        "source_release_id": assignment["source_release_id"],
                        "source_sha256": assignment["source_sha256"],
                        "assigned_to": assignment.get("assigned_to") or "",
                    }
                    writer.writerows({**provenance, **row} for row in assignment["records"])
                    safe_name = assignment["assignment_id"]
                    self._send(stream.getvalue().encode("utf-8-sig"), "text/csv; charset=utf-8",
                               headers={"Content-Disposition": f'attachment; filename="{safe_name}.csv"'})
                else:
                    self._json({"assignment": assignment})
                return
            self._json({"error": "Not found"}, 404)
        except (ValidationError, ContractError, SourceIntegrityError, OSError, ValueError) as exc:
            self._json({"error": str(exc)}, 400)

    def do_POST(self) -> None:  # noqa: N802
        try:
            payload = self._body_json()
            if self.path == "/api/recipe/calculate":
                self._json(self.service.calculate_recipe(payload))
            elif self.path == "/api/meal/calculate":
                self._json(self.service.calculate_meal(payload))
            elif self.path == "/api/comparability":
                self._json(self.service.comparability(payload))
            elif self.path == "/api/review-action":
                self._json(self.service.submit_review_action(payload))
            elif self.path == "/api/export":
                result = payload.get("result")
                fmt = str(payload.get("format") or "json").casefold()
                if not isinstance(result, dict):
                    raise ValidationError("result object is required")
                filename = re.sub(r"[^A-Za-z0-9._-]", "_", str(payload.get("filename") or "cookrisk-export"))[:80]
                if fmt == "csv":
                    content = render_csv(result).encode("utf-8-sig")
                    self._send(content, "text/csv; charset=utf-8", headers={"Content-Disposition": f'attachment; filename="{filename}.csv"'})
                elif fmt == "json":
                    content = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2, default=str).encode("utf-8")
                    self._send(content, "application/json; charset=utf-8", headers={"Content-Disposition": f'attachment; filename="{filename}.json"'})
                else:
                    raise ValidationError("format must be json or csv")
            else:
                self._json({"error": "Not found"}, 404)
        except ReviewAuthenticationUnavailable as exc:
            self._json({
                "code": "review_authentication_unavailable",
                "error": str(exc),
                "review_submission_enabled": False,
            }, 503)
        except (ValidationError, ContractError) as exc:
            self._json({"error": str(exc)}, 400)
        except (SourceIntegrityError, OSError, ValueError) as exc:
            self._json({"error": str(exc)}, 400)


def _review_filters(query: dict[str, list[str]]) -> dict[str, str]:
    names = (
        "compound", "drug", "study", "evidence_category", "outcome_polarity",
        "conflict_status", "identity_status", "source_verification_status", "human_review_status",
    )
    return {name: str(query[name][0]) for name in names if name in query and query[name][0] is not None}


def _offset(query: dict[str, list[str]]) -> int:
    try:
        return max(0, min(100_000, int(query.get("offset", ["0"])[0])))
    except (ValueError, TypeError):
        return 0


def _limit(query: dict[str, list[str]]) -> int:
    try:
        return max(1, min(100, int(query.get("limit", ["80"])[0])))
    except ValueError:
        return 80


def make_server(host: str = "127.0.0.1", port: int = 8765,
                service: CookRiskService | None = None) -> ThreadingHTTPServer:
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("The prototype may bind only to the local machine")
    handler = type("ConfiguredCookRiskHandler", (CookRiskHandler,), {"service": service or _DEFAULT_SERVICE})
    return ThreadingHTTPServer((host, port), handler)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the non-production local CookRisk prototype")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = make_server(args.host, args.port)
    print(f"CookRisk local prototype: http://{args.host}:{server.server_address[1]}/")
    print("Not for clinical use. Stage A inference is disabled; no clinical interpretation is performed.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
