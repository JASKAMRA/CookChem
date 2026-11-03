"""Build a source-linked uncertainty gap registry from Phase 3 output JSON."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

STAGE_C = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STAGE_C / "src"))

from stage_c.exceptions import ValidationError  # noqa: E402
from stage_c.uncertainty import build_uncertainty_gap_registry  # noqa: E402


def _read_outputs(path: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"could not read Phase 3 JSON input: {exc}") from None
    outputs = payload.get("outputs") if isinstance(payload, dict) and "outputs" in payload else payload
    if isinstance(outputs, dict):
        outputs = [outputs]
    if not isinstance(outputs, list) or any(not isinstance(row, dict) for row in outputs):
        raise ValidationError("input must be a Phase 3 output object or a list of output objects")
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Phase 3 result JSON, list, or object containing an outputs list")
    parser.add_argument("--output", type=Path, help="write registry JSON here; default prints to stdout")
    args = parser.parse_args()
    try:
        registry = build_uncertainty_gap_registry(_read_outputs(args.input))
    except ValidationError as exc:
        parser.error(str(exc))
    text = json.dumps(registry, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
