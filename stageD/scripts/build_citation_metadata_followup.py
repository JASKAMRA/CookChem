"""Version the Stage D readiness index with source-checked citation gaps."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAGE_D = ROOT / "stageD"
PUBMED = "https://pubmed.ncbi.nlm.nih.gov/"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=STAGE_D / "reports/closure/qualified_review_readiness_register_v1.2.0.json")
    args = parser.parse_args()
    index_path = STAGE_D / "reports/closure/qualified_review_readiness_register_v1.1.0.json"
    queue_path = STAGE_D / "data/evidence_review_queue.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    queue_by_id = {row["review_id"]: row for row in queue["records"]}
    out = json.loads(json.dumps(index))
    out["register_version"] = "1.2.0"
    out["supersedes"] = {"version": index["register_version"], "sha256": hashlib.sha256(index_path.read_bytes()).hexdigest()}
    unresolved = 0
    for row in out["reviews"]:
        if row["review_type"] != "evidence" or not row.get("missing_metadata_fields"):
            continue
        source = queue_by_id[row["review_id"]]["source_record"]
        followups = []
        for field in row["missing_metadata_fields"]:
            if field == "DOI":
                pmid = str(source.get("PMID", "")).strip()
                sources = [f"{PUBMED}{pmid}/"] if pmid else []
                note = "PubMed primary citation inspected; no DOI was visible in the reviewed citation representation. This does not establish that no DOI exists; leave the field blank pending publisher/registry confirmation."
            elif field == "PMID":
                doi = str(source.get("DOI", "")).strip()
                sources = [f"{PUBMED}?term=%22{doi}%22"] if doi else []
                source_url = str(source.get("Source_URL", "")).strip()
                if source_url:
                    sources.append(source_url)
                note = "Exact DOI/title lookup did not establish a PubMed identifier in the reviewed authoritative records. This does not establish that no PMID exists; leave the field blank pending NCBI confirmation."
            else:
                sources, note = [], "Field is missing; no authoritative lookup procedure is defined."
            followups.append({"field": field, "status": "UNRESOLVED", "candidate_value": None,
                              "source_checks": sources, "note": note})
            unresolved += 1
        row["unresolved_metadata"] = followups
        row["unresolved_questions"].append("Confirm missing citation identifiers against the publisher and NCBI; do not infer an absent DOI/PMID.")
    out["metadata_followup_summary"] = {
        "unresolved_identifier_fields": unresolved,
        "missing_doi_fields": sum(item["field"] == "DOI" for row in out["reviews"] for item in row.get("unresolved_metadata", [])),
        "missing_pmid_fields": sum(item["field"] == "PMID" for row in out["reviews"] for item in row.get("unresolved_metadata", [])),
        "identifiers_added": 0,
        "scientific_or_review_status_changes": 0,
    }
    payload = json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(payload)
    print(json.dumps(out["metadata_followup_summary"], sort_keys=True))
    print("register_sha256=" + hashlib.sha256(payload.encode("utf-8")).hexdigest())


if __name__ == "__main__":
    main()
