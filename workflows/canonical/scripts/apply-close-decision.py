#!/usr/bin/env python3
"""Apply the PM/HumanOperator closure decision after an Accepted review.

Used by implement-task-v0.yaml as pm_apply_close_decision after pm_close_gate.

Input: ticket_dir (task is in .agentops/tickets/accepted/ at this point,
       moved there by apply-review-verdict.py)

Decisions:
  close_done       → accepted/ → done/               (WorkflowBranch → Terminal)
  override_changes → accepted/ → changes-requested/  (WorkflowBranch remains Active)
  override_reject  → accepted/ → rejected/            (WorkflowBranch → Terminal)
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
    print(json.dumps({"valid": False, "status": "", "error": "pyyaml is not installed"}))
    sys.exit(1)

VALID_DECISIONS = {"close_done", "override_changes", "override_reject"}


def emit(valid: bool, status: str = "", error: str = "") -> None:
    print(json.dumps({"valid": valid, "status": status, "error": error}))


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    emit(False, "", message)
    sys.exit(1)


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def sibling_path(ticket_dir: Path, folder_name: str) -> Path:
    """Return path for the ticket directory moved to a sibling folder lane.

    ticket_dir is expected to be inside .agentops/tickets/<lane>/<task-slug>.
    Returns .agentops/tickets/<folder_name>/<task-slug>.
    """
    return ticket_dir.parent.parent / folder_name / ticket_dir.name


def validate_common(ticket: dict[str, Any], branch: dict[str, Any]) -> str:
    if ticket.get("status") != "Accepted":
        fail(f"task.status must be Accepted, got {ticket.get('status')!r}")
    if branch.get("status") != "Active":
        fail(f"WorkflowBranch.status must be Active, got {branch.get('status')!r}")

    branch_id = ticket.get("activeWorkflowBranchId")
    if not branch_id:
        fail("activeWorkflowBranchId is missing or empty")
    return str(branch_id)


def main() -> None:
    if len(sys.argv) != 3:
        fail("Usage: apply-close-decision.py <ticket_dir> <decision>")

    ticket_dir = Path(sys.argv[1])
    decision = sys.argv[2]

    if ticket_dir.parent.name != "accepted":
        fail(
            f"ticket_dir must be inside 'accepted/', "
            f"got parent folder {ticket_dir.parent.name!r}"
        )

    if decision not in VALID_DECISIONS:
        fail(f"Unknown decision: {decision}")

    ticket_path = ticket_dir / "ticket.md"
    if not ticket_path.exists():
        fail(f"ticket.md not found at {ticket_path}")

    ticket, ticket_body = read_frontmatter(ticket_path)
    active_branch_id = ticket.get("activeWorkflowBranchId")
    if not active_branch_id:
        fail("activeWorkflowBranchId is missing or empty")

    branch_path = ticket_dir / f"workflow-branch-{active_branch_id}.md"
    if not branch_path.exists():
        fail(f"WorkflowBranch metadata not found at {branch_path}")

    branch, branch_body = read_frontmatter(branch_path)
    validate_common(ticket, branch)

    timestamp = now_utc()

    if decision == "override_changes":
        # Move accepted/ → changes-requested/; WorkflowBranch remains Active
        destination = sibling_path(ticket_dir, "changes-requested")
        if destination.exists():
            fail(f"Destination ticket directory already exists at {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)

        ticket["status"] = "ChangesRequested"
        ticket["lastTransitionBy"] = "HumanOperator"
        ticket["lastTransitionReason"] = "HumanOverrideAfterAccepted"
        ticket["updatedAt"] = timestamp
        write_frontmatter(ticket_path, ticket, ticket_body)

        shutil.move(str(ticket_dir), str(destination))
        emit(True, "ChangesRequested", "")
        return

    # close_done or override_reject — both require WorkflowBranch termination
    if decision == "close_done":
        target_folder = "done"
        next_status = "Done"
        terminal_reason = "Accepted"
        transition_reason = "AcceptedClosedAsDone"
    else:  # override_reject
        target_folder = "rejected"
        next_status = "Rejected"
        terminal_reason = "Rejected"
        transition_reason = "HumanOverrideAfterAccepted"

    destination = sibling_path(ticket_dir, target_folder)
    if destination.exists():
        fail(f"Destination ticket directory already exists at {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)

    branch["status"] = "Terminal"
    branch["terminalReason"] = terminal_reason
    branch["terminatedAt"] = timestamp
    write_frontmatter(branch_path, branch, branch_body)

    ticket["status"] = next_status
    ticket["lastTransitionBy"] = "HumanOperator"
    ticket["lastTransitionReason"] = transition_reason
    ticket["activeWorkflowBranchId"] = None
    ticket["updatedAt"] = timestamp
    write_frontmatter(ticket_path, ticket, ticket_body)

    shutil.move(str(ticket_dir), str(destination))
    emit(True, next_status, "")


if __name__ == "__main__":
    main()
