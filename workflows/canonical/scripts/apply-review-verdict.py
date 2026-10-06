#!/usr/bin/env python3
"""Apply Reviewer verdict: move ticket to the correct folder lane.

Used by implement-task-v0.yaml after validate_review_result confirms a valid verdict.

Verdict → folder mapping:
  Accepted         → .agentops/tickets/accepted/
  ChangesRequested → .agentops/tickets/changes-requested/
  Rejected         → .agentops/tickets/rejected/         (WorkflowBranch → Terminal)
  TicketInvalid    → .agentops/tickets/ticket-invalid/   (WorkflowBranch → Terminal)

For Accepted: WorkflowBranch remains Active; termination is deferred to PM/HumanOperator
via pm_close_gate → pm_apply_close_decision.

For ChangesRequested: WorkflowBranch remains Active; repair is manual in V0.
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
            "applied_status": "",
            "error": "pyyaml is not installed",
        })
    )
    sys.exit(1)

VALID_VERDICTS = {"Accepted", "ChangesRequested", "Rejected", "TicketInvalid"}

VERDICT_TO_FOLDER = {
    "Accepted": "accepted",
    "ChangesRequested": "changes-requested",
    "Rejected": "rejected",
    "TicketInvalid": "ticket-invalid",
}

# Verdicts that require WorkflowBranch termination
TERMINAL_VERDICTS = {"Rejected", "TicketInvalid"}


def fail(message: str) -> None:
    print(
        json.dumps({
            "valid": False,
            "new_ticket_dir": "",
            "applied_status": "",
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
    if len(sys.argv) != 3:
        fail("Usage: apply-review-verdict.py <ticket_dir> <verdict>")

    ticket_dir = Path(sys.argv[1])
    verdict = sys.argv[2]

    if ticket_dir.parent.name != "in-progress":
        fail(
            f"ticket_dir must be inside 'in-progress/', "
            f"got parent folder {ticket_dir.parent.name!r}"
        )

    if verdict not in VALID_VERDICTS:
        fail(f"Unknown verdict: {verdict!r}. Expected one of {sorted(VALID_VERDICTS)}")

    ticket_path = ticket_dir / "ticket.md"
    if not ticket_path.exists():
        fail(f"ticket.md not found at {ticket_path}")

    ticket, ticket_body = read_frontmatter(ticket_path)

    # Reviewer should have already set the status; verify it matches the verdict.
    current_status = ticket.get("status")
    if current_status != verdict:
        # The Reviewer may not have updated status yet; apply it now.
        # This makes the script safe to run even if the Reviewer omitted the update.
        ticket["status"] = verdict

    branch_id = ticket.get("activeWorkflowBranchId")
    if not branch_id:
        fail("activeWorkflowBranchId is null or missing")

    timestamp = now_utc()

    # --- Terminalize WorkflowBranch if required ---

    if verdict in TERMINAL_VERDICTS:
        branch_meta_path = ticket_dir / f"workflow-branch-{branch_id}.md"
        if not branch_meta_path.exists():
            fail(f"WorkflowBranch metadata not found at {branch_meta_path}")

        branch, branch_body = read_frontmatter(branch_meta_path)

        if branch.get("status") == "Terminal":
            fail(
                f"WorkflowBranch {branch_id} is already Terminal; "
                f"task may have been processed previously"
            )

        branch["status"] = "Terminal"
        branch["terminalReason"] = verdict  # Rejected or TicketInvalid
        branch["terminatedAt"] = timestamp
        write_frontmatter(branch_meta_path, branch, branch_body)

        # Clear activeWorkflowBranchId since branch is now Terminal
        ticket["activeWorkflowBranchId"] = None

    # --- Update ticket.md ---

    ticket["status"] = verdict
    ticket["lastTransitionBy"] = "Reviewer"
    ticket["lastTransitionReason"] = f"ReviewVerdict{verdict}"
    ticket["updatedAt"] = timestamp
    write_frontmatter(ticket_path, ticket, ticket_body)

    # --- Move folder to target lane ---

    target_folder = VERDICT_TO_FOLDER[verdict]
    # ticket_dir.parent = in-progress/, ticket_dir.parent.parent = tickets/
    destination = ticket_dir.parent.parent / target_folder / ticket_dir.name
    if destination.exists():
        fail(f"Destination ticket directory already exists at {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(ticket_dir), str(destination))

    print(
        json.dumps({
            "valid": True,
            "new_ticket_dir": str(destination),
            "applied_status": verdict,
            "error": "",
        })
    )


if __name__ == "__main__":
    main()
