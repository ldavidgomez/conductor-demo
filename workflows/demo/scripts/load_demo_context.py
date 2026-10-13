#!/usr/bin/env python3
"""Load the ticket context shared by the demo workflow's converged route."""

from __future__ import annotations

import json
from pathlib import Path


CONTEXT_PATH = Path(".agentops/demo-runtime/current-ticket.json")


def main() -> None:
    context = json.loads(CONTEXT_PATH.read_text(encoding="utf-8"))
    ticket_dir = Path(context["ticket_dir"])
    if not (ticket_dir / "ticket.md").exists():
        raise SystemExit(f"ticket.md not found at {ticket_dir}")
    print(json.dumps({
        "ticket_dir": str(ticket_dir),
        "handoff_path": str(ticket_dir / "dev-handoff.md"),
        "review_result_path": str(ticket_dir / "review-result.md"),
    }))


if __name__ == "__main__":
    main()
