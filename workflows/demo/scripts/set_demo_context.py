#!/usr/bin/env python3
"""Persist the current ticket path so both demo entry routes share later steps."""

from __future__ import annotations

import json
import sys
from pathlib import Path


CONTEXT_PATH = Path(".agentops/demo-runtime/current-ticket.json")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: set_demo_context.py <ticket_dir>")

    ticket_dir = Path(sys.argv[1])
    if not (ticket_dir / "ticket.md").exists():
        raise SystemExit(f"ticket.md not found at {ticket_dir}")

    CONTEXT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONTEXT_PATH.write_text(json.dumps({"ticket_dir": str(ticket_dir)}), encoding="utf-8")
    print(json.dumps({"ticket_dir": str(ticket_dir)}))


if __name__ == "__main__":
    main()
