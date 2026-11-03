"""Print a reproducible synthetic Phase 2 readiness demonstration."""
from __future__ import annotations

import json
import argparse
import sys
from pathlib import Path

STAGE_C = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STAGE_C / "src"))

from stage_c.deployment_decisions import build_readiness_dashboard, render_readiness_markdown  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tracker", type=Path, default=STAGE_C / "data/phase2/owner_decision_tracker.json")
    parser.add_argument("--write-report", action="store_true", help="regenerate the checked-in Markdown dashboard from the tracker")
    args = parser.parse_args()
    tracker = json.loads(args.tracker.read_text(encoding="utf-8"))
    dashboard = build_readiness_dashboard(tracker)
    if args.write_report:
        report_path = STAGE_C / "reports/phase2/STAGE_A_DEPLOYMENT_READINESS_DASHBOARD.md"
        report_path.write_text(render_readiness_markdown(dashboard), encoding="utf-8")
        print(f"Updated {report_path}")
    else:
        print(json.dumps(dashboard, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
