"""Conservative, auditable chemical identity and food-record mapping."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from .exceptions import ValidationError

MAPPING_FIELDS = ["mapping_id", "food_record_id", "compound_id", "candidate_compound_ids", "compound_name", "mapping_status", "identity_basis", "rationale", "mapping_source", "food_name", "source_verification_status", "quantitative_data_available", "warning"]
VERIFIED_STATUSES = {"Exact identity match", "Verified synonym match", "Structure-supported match"}


def _key(value: str) -> str:
    return " ".join(value.casefold().strip().split())


def _quantitative_data_available(record: dict[str, Any]) -> bool:
    return (
        bool(record.get("reported_concentration"))
        and bool(record.get("raw_or_processed_state"))
        and bool(record.get("moisture_basis"))
        and record.get("food_use_classification", "").casefold() in {"ordinary food", "food ingredient", "prepared beverage"}
        and record.get("source_verification_status", "").casefold() in {"verified", "full-text verified", "database verified", "user verified"}
        and record.get("source_classification", "") in {"Primary analytical measurement", "Peer-reviewed secondary source", "Authoritative food-composition database", "Verified laboratory measurement", "User-supplied measurement"}
    )


def build_mappings(compounds: list[dict[str, str]], food_records: list[dict[str, Any]]) -> list[dict[str, str]]:
    by_cid: dict[str, list[dict[str, str]]] = {}
    by_key: dict[str, list[dict[str, str]]] = {}
    by_name: dict[str, list[dict[str, str]]] = {}
    aliases: dict[str, list[dict[str, str]]] = {}
    for compound in compounds:
        if compound.get("PubChem_CID", "").strip(): by_cid.setdefault(compound["PubChem_CID"].strip(), []).append(compound)
        if compound.get("InChIKey", "").strip(): by_key.setdefault(compound["InChIKey"].strip().upper(), []).append(compound)
        if compound.get("Canonical_Name", "").strip(): by_name.setdefault(_key(compound["Canonical_Name"]), []).append(compound)
        for alias in compound.get("Aliases", "").split("|"):
            if alias.strip(): aliases.setdefault(_key(alias), []).append(compound)

    mappings = []
    for record in food_records:
        candidates: dict[str, str] = {}
        signals: list[tuple[str, set[str]]] = []
        explicit = record.get("compound_id", "").strip()
        if explicit:
            match = next((c for c in compounds if c["Compound_ID"] == explicit), None)
            found = {explicit} if match else set()
            signals.append(("Stage B Compound_ID exact match", found))
            if match: candidates[explicit] = "Stage B Compound_ID exact match"
        cid = record.get("pubchem_cid", "").strip()
        if cid:
            found = {c["Compound_ID"] for c in by_cid.get(cid, [])}
            signals.append(("identical PubChem CID", found))
            for c in by_cid.get(cid, []): candidates[c["Compound_ID"]] = "identical PubChem CID"
        inchikey = record.get("inchikey", "").strip().upper()
        if inchikey:
            found = {c["Compound_ID"] for c in by_key.get(inchikey, [])}
            signals.append(("identical InChIKey", found))
            for c in by_key.get(inchikey, []): candidates[c["Compound_ID"]] = "identical InChIKey"
        name = _key(record.get("compound_name", ""))
        exact_names = by_name.get(name, [])
        alias_matches = aliases.get(name, [])
        if name and (exact_names or not alias_matches):
            signals.append(("exact canonical compound name", {c["Compound_ID"] for c in exact_names}))
        for c in exact_names: candidates[c["Compound_ID"]] = "exact canonical compound name"
        if alias_matches:
            signals.append(("Stage B alias", {c["Compound_ID"] for c in alias_matches}))
        verified_alias = record.get("synonym_verification_status", "").strip().casefold() == "verified" and bool(record.get("synonym_source", "").strip())
        if verified_alias:
            for c in alias_matches: candidates[c["Compound_ID"]] = "explicitly source-verified synonym"
        # Name-only aliases are deliberately surfaced as candidates, never accepted as identity.
        review_status = record.get("mapping_review_status", "").strip()
        review_id = record.get("mapping_review_compound_id", "").strip()
        review_rationale = record.get("mapping_review_rationale", "").strip()
        review_source = record.get("mapping_review_source", "").strip()
        if review_status:
            valid_ids = {c.get("Compound_ID", "") for c in compounds}
            if not review_rationale or not review_source:
                raise ValidationError(f"Manual mapping decision for {record.get('food_record_id','')} requires rationale and source")
            if review_status == "Rejected match":
                candidates[review_id] = "manually rejected candidate" if review_id else "manually rejected"
                cid_match, basis, status, rationale = "", "manual review", "Rejected match", review_rationale
            elif review_status in {"Exact identity match", "Verified synonym match", "Structure-supported match"} and review_id in valid_ids:
                candidates[review_id] = "manual review"
                cid_match, basis, status, rationale = review_id, "manual review", review_status, review_rationale
            else:
                raise ValidationError(f"Invalid or unresolved manual mapping decision for {record.get('food_record_id','')}")
            quantitative = _quantitative_data_available(record)
            possible_ids = set().union(*(found for _, found in signals)) if signals else set()
            if review_id: possible_ids.add(review_id)
            mappings.append({"mapping_id":"", "food_record_id":str(record.get("food_record_id","")), "compound_id":cid_match, "candidate_compound_ids":"|".join(sorted(possible_ids)), "compound_name":str(record.get("compound_name","")), "mapping_status":status, "identity_basis":basis, "rationale":rationale, "mapping_source":review_source, "food_name":str(record.get("food_name","")), "source_verification_status":str(record.get("source_verification_status","")), "quantitative_data_available":"true" if quantitative else "false", "warning":"" if status in VERIFIED_STATUSES else "Identity requires review; no exposure estimate will be produced."})
            continue
        consensus = set.intersection(*(found for _, found in signals)) if signals and all(found for _, found in signals) else set()
        alias_only_unverified = bool(alias_matches) and not verified_alias and not exact_names and not cid and not inchikey and not explicit
        if len(consensus) == 1 and not alias_only_unverified:
            cid_match = next(iter(consensus))
            # The most identity-specific agreeing evidence determines the label.
            identity_id = cid_match
            if any(label == "identical InChIKey" and identity_id in found for label, found in signals): basis = "identical InChIKey"
            elif any(label == "identical PubChem CID" and identity_id in found for label, found in signals): basis = "identical PubChem CID"
            elif verified_alias and any(identity_id in found for label, found in signals if label == "Stage B alias"): basis = "explicitly source-verified synonym"
            elif any(label == "Stage B Compound_ID exact match" and identity_id in found for label, found in signals): basis = "Stage B Compound_ID exact match"
            else: basis = "exact canonical compound name"
            if basis == "identical InChIKey": status, rationale = "Structure-supported match", "Full InChIKey equality supports the match; isomer-sensitive key retained."
            elif basis == "identical PubChem CID": status, rationale = "Exact identity match", "PubChem CID is identical to the Stage B reference."
            elif basis == "explicitly source-verified synonym": status, rationale = "Verified synonym match", "Alias has an explicit verification source on the food record."
            else: status, rationale = "Exact identity match", "Exact Compound_ID or canonical-name match; no fuzzy matching used."
            matched_compound = next(c for c in compounds if c.get("Compound_ID") == cid_match)
            identity_status = matched_compound.get("StageC_Identity_Verification_Status", "Complete")
            if identity_status != "Complete":
                status = "Pending identity review"
                rationale = f"Stage B identity status is pending review ({identity_status}); candidate retained without verified mapping."
        elif candidates or signals:
            cid_match, basis, status = "", "; ".join(sorted(set(candidates.values()))), "Ambiguous match"
            rationale = "Chemical identifiers or names point to multiple Stage B compounds; manual adjudication required."
        else:
            cid_match, basis, status = "", "no exact chemical identifier", "Unmatched"
            rationale = "No exact Stage B ID, canonical name, CID, InChIKey, or verified synonym match."
        quantitative = _quantitative_data_available(record)
        possible_ids = set().union(*(found for _, found in signals)) if signals else set()
        mappings.append({"mapping_id": "", "food_record_id": str(record.get("food_record_id", "")), "compound_id": cid_match, "candidate_compound_ids": "|".join(sorted(possible_ids)), "compound_name": str(record.get("compound_name", "")), "mapping_status": status, "identity_basis": basis, "rationale": rationale, "mapping_source": str(record.get("synonym_source", "") or record.get("source_url", "") or record.get("database_reference", "")), "food_name": str(record.get("food_name", "")), "source_verification_status": str(record.get("source_verification_status", "")), "quantitative_data_available": "true" if quantitative else "false", "warning": "" if status in VERIFIED_STATUSES else "Identity requires review; no exposure estimate will be produced."})
    # Deterministic mapping identifiers, independent of record ordering.
    import hashlib
    for row in mappings:
        token = "|".join((row["food_record_id"], row["compound_id"], row["mapping_status"], row["identity_basis"]))
        row["mapping_id"] = "MAP-" + hashlib.sha256(token.encode()).hexdigest()[:20].upper()
    return mappings


def mapping_coverage(compounds: list[dict[str, str]], food_records: list[dict[str, Any]], mappings: list[dict[str, str]]) -> dict[str, Any]:
    compound_by_id = {row.get("Compound_ID", ""): row for row in compounds}
    eligible_ids = {
        compound_id for compound_id, row in compound_by_id.items()
        if row.get("StageC_Identity_Verification_Status", "Complete") == "Complete"
    }
    quantitatively_mapped = {
        row["compound_id"] for row in mappings
        if row["compound_id"] in eligible_ids
        and row["mapping_status"] in VERIFIED_STATUSES
        and row["quantitative_data_available"] == "true"
    }
    pending_identity_rows = [
        row for row in mappings
        if row.get("compound_id") in compound_by_id
        and compound_by_id[row["compound_id"]].get("StageC_Identity_Verification_Status", "Complete") != "Complete"
        and row.get("mapping_status") in VERIFIED_STATUSES
    ]
    candidate_ids = {cid for r in mappings for cid in (r.get("candidate_compound_ids", "").split("|") if r.get("candidate_compound_ids") else ([r["compound_id"]] if r.get("compound_id") else []))}
    pending_ids = {row["compound_id"] for row in pending_identity_rows}
    unverified_coverage = len(compounds) - len(quantitatively_mapped)
    return {
        "total_stage_b_compounds": len(compounds),
        "compounds_with_verified_quantitative_food_data": len(quantitatively_mapped),
        "compounds_with_candidate_records": len(candidate_ids),
        "compounds_with_no_verified_quantitative_data": unverified_coverage,
        "compounds_with_no_quantitative_data": unverified_coverage,
        "compounds_pending_identity_review": sum(
            row.get("StageC_Identity_Verification_Status", "Complete") != "Complete"
            for row in compounds
        ),
        "legacy_mapped_compounds_pending_identity_review": len(pending_ids),
        "legacy_mapping_rows_pending_identity_review": len(pending_identity_rows),
        "ambiguous_mappings": sum(row["mapping_status"] == "Ambiguous match" for row in mappings),
        "unmatched_records": sum(row["mapping_status"] == "Unmatched" for row in mappings),
        "rejected_mappings": sum(row["mapping_status"] == "Rejected match" for row in mappings),
        "food_composition_records": len(food_records),
        "mapping_records": len(mappings),
    }


def assess_mapping_compatibility(compounds: list[dict[str, str]], mappings: list[dict[str, str]]) -> list[dict[str, str]]:
    """Describe legacy verified mappings that current Stage B identity review blocks."""
    compound_by_id = {row.get("Compound_ID", ""): row for row in compounds}
    return [
        {
            "mapping_id": row.get("mapping_id", ""),
            "compound_id": row.get("compound_id", ""),
            "stored_mapping_status": row.get("mapping_status", ""),
            "effective_mapping_status": "Pending identity review",
            "current_identity_status": compound_by_id[row["compound_id"]].get("StageC_Identity_Verification_Status", ""),
            "active_use_allowed": "false",
        }
        for row in mappings
        if row.get("compound_id") in compound_by_id
        and compound_by_id[row["compound_id"]].get("StageC_Identity_Verification_Status", "Complete") != "Complete"
        and row.get("mapping_status") in VERIFIED_STATUSES
    ]


def write_mappings(path: Path, mappings: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=MAPPING_FIELDS); writer.writeheader(); writer.writerows(mappings)


def load_mappings(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream: return list(csv.DictReader(stream))
