#!/usr/bin/env python3
"""Validate the first-line verdict contract used by the Copilot demo workflows."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: validate_demo_verdict.py <review-result.md> <expected-verdict>")

    result_path = Path(sys.argv[1])
    expected = sys.argv[2]
    if not result_path.is_file():
        print(json.dumps({"verdict": "Missing", "reason": f"review artifact not found: {result_path}"}))
        raise SystemExit(1)

    first_line = result_path.read_text(encoding="utf-8").splitlines()[0].strip()
    actual = first_line.removeprefix("verdict:").strip() if first_line.startswith("verdict:") else "Malformed"

    if actual != expected:
        print(json.dumps({"verdict": actual, "reason": f"expected {expected}, got {actual}"}))
        raise SystemExit(1)

    print(json.dumps({"verdict": actual, "reason": "review artifact matches the expected route"}))


if __name__ == "__main__":
    main()
