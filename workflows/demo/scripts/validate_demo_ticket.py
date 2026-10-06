#!/usr/bin/env python3
"""Deterministically reject the intentionally incomplete ticket used in demo 1."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REQUIRED_FIELDS = ("taskId", "status", "authorizedForDevBy", "authorizedForDevAt", "authorizationReason")


def frontmatter(path: Path) -> dict[str, str]:
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}

    values: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: validate_demo_ticket.py <ticket.md>")

    ticket_path = Path(sys.argv[1])
    if not ticket_path.is_file():
        print(json.dumps({"verdict": "Error", "reason": f"ticket not found: {ticket_path}"}))
        raise SystemExit(1)

    ticket = frontmatter(ticket_path)
    missing = [field for field in REQUIRED_FIELDS if not ticket.get(field)]
    if ticket.get("status") != "ReadyForDev":
        missing.append("status must be ReadyForDev")

    if not missing:
        print(json.dumps({"verdict": "UnexpectedPass", "reason": "fixture satisfies every demo precondition"}))
        raise SystemExit(1)

    print(json.dumps({"verdict": "TicketInvalid", "reason": "Missing or invalid: " + ", ".join(missing)}))


if __name__ == "__main__":
    main()
