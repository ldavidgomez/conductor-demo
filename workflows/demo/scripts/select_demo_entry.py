#!/usr/bin/env python3
"""Select the resumable entry point for the single demo workflow."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml


def frontmatter(path: Path) -> dict:
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    return yaml.safe_load(parts[1]) or {}


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: select_demo_entry.py <ticket_dir>")

    ticket_dir = Path(sys.argv[1])
    ticket_path = ticket_dir / "ticket.md"
    if not ticket_path.exists():
        print(json.dumps({"phase": "unsupported", "error": f"ticket.md not found at {ticket_path}"}))
        return

    try:
        ticket = frontmatter(ticket_path)
    except (OSError, yaml.YAMLError) as error:
        print(json.dumps({"phase": "unsupported", "error": f"could not parse ticket frontmatter: {error}"}))
        return

    status = ticket.get("status")
    if status == "ReadyForDev" and ticket_dir.parent.name == "ready-for-dev":
        print(json.dumps({"phase": "ready", "error": ""}))
        return

    if status == "DevComplete" and ticket_dir.parent.name == "in-progress":
        handoff = ticket_dir / "dev-handoff.md"
        if handoff.exists():
            print(json.dumps({"phase": "review", "error": ""}))
        else:
            print(json.dumps({"phase": "unsupported", "error": "DevComplete ticket has no dev-handoff.md"}))
        return

    print(json.dumps({
        "phase": "unsupported",
        "error": (
            "Demo tickets must be ReadyForDev under ready-for-dev/ or "
            "DevComplete under in-progress/; "
            f"got status {status!r} in {ticket_dir.parent.name!r}"
        ),
    }))


if __name__ == "__main__":
    main()
