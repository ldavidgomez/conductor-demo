#!/usr/bin/env python3
"""Validate that a task is ready for the implementation workflow to begin.

This script replaces the former validate-ready-for-dev.py used by
pm-dev-reviewer-v0.yaml (now deprecated). The deprecated workflow used this
script to validate InProgress state after PM created the WorkflowBranch.

The new script validates ReadyForDev preconditions BEFORE start-implementation.py
creates the WorkflowBranch. It is used by implement-task-v0.yaml as the first
step to confirm the task is properly authorized for implementation.

Checks:
  - ticket.md exists and is readable
  - status == ReadyForDev
  - activeWorkflowBranchId is null or absent (WorkflowBranch not yet created)
  - authorizedForDevBy field is present and non-empty
  - authorizedForDevAt field is present and non-empty
  - authorizationReason field is present and non-empty
"""

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
    if len(sys.argv) != 2:
        fail("Usage: validate-ready-for-dev.py <ticket_dir>")

    ticket_dir = Path(sys.argv[1])

    if ticket_dir.parent.name != "ready-for-dev":
        fail(
            f"ticket_dir must be inside 'ready-for-dev/', "
            f"got parent folder {ticket_dir.parent.name!r}"
        )

    ticket_path = ticket_dir / "ticket.md"

    if not ticket_path.exists():
        fail(f"ticket.md not found at {ticket_path}")

    ticket = parse_frontmatter(ticket_path)
    if ticket is None:
        fail(f"Could not read {ticket_path}")

    status = ticket.get("status")
    if status != "ReadyForDev":
        fail(f"task status is {status!r}, expected 'ReadyForDev'")

    branch_id = ticket.get("activeWorkflowBranchId")
    if branch_id:
        fail(
            f"activeWorkflowBranchId is {branch_id!r}; expected null for a ReadyForDev "
            f"task — WorkflowBranch should not exist before start-implementation.py runs"
        )

    # Authorization fields (required for ReadyForDev)
    authorized_by = ticket.get("authorizedForDevBy")
    if not authorized_by:
        fail("authorizedForDevBy is missing or empty — task has not been explicitly authorized for implementation")

    authorized_at = ticket.get("authorizedForDevAt")
    if not authorized_at:
        fail("authorizedForDevAt is missing or empty")

    authorization_reason = ticket.get("authorizationReason")
    if not authorization_reason:
        fail("authorizationReason is missing or empty")

    print(json.dumps({"valid": True, "error": ""}))


if __name__ == "__main__":
    main()
