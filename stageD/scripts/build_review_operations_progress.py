"""Create the initial consolidated progress snapshot without inventing reviewers."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
STAGE_D = ROOT / "stageD"
sys.path.insert(0, str(STAGE_D / "src"))
from stage_d.review_operations import review_progress



def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=STAGE_D / "reports/closure/review_operations_progress_v1.0.0.json")
    args = parser.parse_args()
    readiness_path = STAGE_D / "reports/closure/qualified_review_readiness_register_v1.1.0.json"
    audit_path = STAGE_D / "data/review_operations.jsonl"
    if audit_path.exists():
        raise SystemExit("A review operations ledger exists; configure the owner-approved verifier before reporting progress.")
    register = json.loads(readiness_path.read_text(encoding="utf-8"))
    snapshot = review_progress(register, [])
    snapshot["audit_ledger"] = "NOT_PROVISIONED"
    snapshot["reviewer_worklists_generated"] = 0
    snapshot["reviewer_roster"] = "NOT_PROVISIONED"
    snapshot["note"] = "No reviewer identities or decisions have been supplied; all records remain pending and unassigned."
    payload = json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(payload)
    print(json.dumps(snapshot, sort_keys=True))


if __name__ == "__main__":
    main()
