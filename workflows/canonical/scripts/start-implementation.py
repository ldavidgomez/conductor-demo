#!/usr/bin/env python3
"""Deterministic implementation start step.

Promotes a ReadyForDev task to InProgress and creates the WorkflowBranch.

Used by implement-task-v0.yaml as the first deterministic step before Dev runs.
Replaces the PM WorkflowBranch-creation responsibility from the deprecated
pm-dev-reviewer-v0.yaml combined workflow.

WorkflowBranch ID convention: WFBR-YYYYMMDD-NNN-slug
Derived by replacing the "TASK-" prefix with "WFBR-" from the taskId field.
Example: taskId TASK-20260526-001-my-feature → WFBR-20260526-001-my-feature
"""

from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print(
        json.dumps({
            "valid": False,
            "new_ticket_dir": "",
            "workflow_branch_id": "",
            "error": "pyyaml is not installed",
        })
    )
    sys.exit(1)


def fail(message: str) -> None:
    print(
        json.dumps({
            "valid": False,
            "new_ticket_dir": "",
            "workflow_branch_id": "",
            "error": message,
        })
    )
    sys.exit(1)


def now_utc() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def read_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"Could not read {path}: {exc}")

    if not content.startswith("---"):
        fail(f"{path} is missing YAML frontmatter")

    parts = content.split("---", 2)
    if len(parts) < 3:
        fail(f"{path} has malformed YAML frontmatter")

    try:
        loaded = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as exc:
        fail(f"{path} has invalid YAML frontmatter: {exc}")

    if not isinstance(loaded, dict):
        fail(f"{path} YAML frontmatter must be an object")

    return loaded, parts[2]  # type: ignore[return-value]


def write_frontmatter(path: Path, data: dict[str, Any], body: str) -> None:
    yaml_text = yaml.safe_dump(data, sort_keys=False, allow_unicode=False)
    path.write_text(f"---\n{yaml_text}---{body}", encoding="utf-8")


def main() -> None:
    if len(sys.argv) != 2:
        fail("Usage: start-implementation.py <ticket_dir>")

    ticket_dir = Path(sys.argv[1])

    if ticket_dir.parent.name != "ready-for-dev":
        fail(
            f"ticket_dir must be inside 'ready-for-dev/', "
            f"got parent folder {ticket_dir.parent.name!r}"
        )

    ticket_path = ticket_dir / "ticket.md"

    if not ticket_path.exists():
        fail(f"ticket.md not found at {ticket_path}")

    ticket, ticket_body = read_frontmatter(ticket_path)

    # --- Precondition checks ---

    status = ticket.get("status")
    if status != "ReadyForDev":
        fail(f"task status is {status!r}, expected 'ReadyForDev'")

    task_id = ticket.get("taskId")
    if not task_id or not str(task_id).startswith("TASK-"):
        fail(f"taskId is missing or has unexpected format: {task_id!r}")

    existing_branch_id = ticket.get("activeWorkflowBranchId")
    if existing_branch_id:
        fail(
            f"activeWorkflowBranchId is already set to {existing_branch_id!r}; "
            f"task may already have an open WorkflowBranch"
        )

    # --- Derive WorkflowBranch ID (WFBR- convention) ---

    workflow_branch_id = "WFBR-" + str(task_id)[len("TASK-"):]

    branch_meta_path = ticket_dir / f"workflow-branch-{workflow_branch_id}.md"
    if branch_meta_path.exists():
        fail(f"WorkflowBranch metadata already exists at {branch_meta_path}")

    timestamp = now_utc()

    # --- Create WorkflowBranch metadata ---

    branch_meta: dict[str, Any] = {
        "artifactType": "workflow-branch",
        "workflowBranchId": workflow_branch_id,
        "taskId": str(task_id),
        "sequenceNumber": 1,
        "branchType": "Implementation",
        "status": "Active",
        "openedBy": "HumanOperator",
        "openedReason": "InitialImplementation",
        "createdAt": timestamp,
        "terminalReason": None,
    }
    write_frontmatter(branch_meta_path, branch_meta, "\n")

    # --- Update ticket.md ---

    ticket["status"] = "InProgress"
    ticket["activeWorkflowBranchId"] = workflow_branch_id
    ticket["lastTransitionBy"] = "HumanOperator"
    ticket["lastTransitionReason"] = "ImplementationWorkflowStarted"
    ticket["updatedAt"] = timestamp
    write_frontmatter(ticket_path, ticket, ticket_body)

    # --- Move folder: ready-for-dev/<slug> → in-progress/<slug> ---

    # ticket_dir.parent should be ready-for-dev/; parent.parent is tickets/
    destination = ticket_dir.parent.parent / "in-progress" / ticket_dir.name
    if destination.exists():
        fail(f"Destination ticket directory already exists at {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(ticket_dir), str(destination))

    print(
        json.dumps({
            "valid": True,
            "new_ticket_dir": str(destination),
            "workflow_branch_id": workflow_branch_id,
            "error": "",
        })
    )


if __name__ == "__main__":
    main()
