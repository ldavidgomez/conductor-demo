#!/usr/bin/env python3
"""Validate DevHandoff artifact before Reviewer."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print(json.dumps({"valid": False, "error": "pyyaml is not installed"}))
    sys.exit(1)

VALID_RESULT_VALUES = {"passed", "failed", "skipped"}


def parse_frontmatter(path: Path) -> dict[str, Any] | None:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return None

    if not content.startswith("---"):
        return {}

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}

    try:
        loaded = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}

    return loaded if isinstance(loaded, dict) else {}


def fail(message: str) -> None:
    print(json.dumps({"valid": False, "error": message}))
    sys.exit(1)


def main() -> None:
    if len(sys.argv) != 3:
        fail("Usage: validate-dev-handoff.py <handoff_path> <ticket_dir>")

    handoff_path = Path(sys.argv[1])
    ticket_dir = Path(sys.argv[2])

    if not handoff_path.exists():
        fail(f"DevHandoff not found at {handoff_path}")

    handoff = parse_frontmatter(handoff_path)
    if handoff is None:
        fail(f"Could not read {handoff_path}")

    branch_id = handoff.get("workflowBranchId")
    if not branch_id:
        fail("workflowBranchId is missing or empty in DevHandoff")

    validation = handoff.get("validation")
    if not isinstance(validation, list):
        fail(f"validation must be a list, got {type(validation).__name__}")

    for index, item in enumerate(validation):
        if not isinstance(item, dict):
            fail(f"validation[{index}] must be an object")
        result = item.get("result")
        if result not in VALID_RESULT_VALUES:
            fail(
                f"validation[{index}].result is {result!r}, "
                f"expected one of {sorted(VALID_RESULT_VALUES)}"
            )

    ready = handoff.get("readyForReview")
    if ready is not True:
        fail(f"readyForReview is {ready!r}, expected true")

    ticket_path = ticket_dir / "ticket.md"
    if not ticket_path.exists():
        fail(f"ticket.md not found at {ticket_path}")

    ticket = parse_frontmatter(ticket_path)
    if ticket is None:
        fail(f"Could not read {ticket_path}")

    status = ticket.get("status")
    if status != "DevComplete":
        fail(f"task status is {status!r}, expected 'DevComplete'")

    print(json.dumps({"valid": True, "error": ""}))


if __name__ == "__main__":
    main()
