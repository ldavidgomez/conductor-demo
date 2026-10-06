#!/usr/bin/env python3
"""Validate ReviewResult artifact and extract verdict for routing."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print(json.dumps({"valid": False, "verdict": "", "error": "pyyaml is not installed"}))
    sys.exit(1)

VALID_VERDICTS = {"Accepted", "ChangesRequested", "Rejected", "TicketInvalid"}
VALID_SEVERITIES = {"must_fix", "should_fix", "note"}
VALID_CATEGORIES = {"implementation_defect", "test_gap", "handoff_gap", "governance_defect"}


def parse_frontmatter(path: Path) -> tuple[dict[str, Any] | None, str]:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return None, ""

    if not content.startswith("---"):
        return {}, ""

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, ""

    try:
        loaded = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as error:
        return {}, str(error)

    return loaded if isinstance(loaded, dict) else {}, ""


def fail(message: str) -> None:
    print(json.dumps({"valid": False, "verdict": "", "error": message}))
    sys.exit(1)


def main() -> None:
    if len(sys.argv) != 2:
        fail("Usage: validate-review-result.py <review_result_path>")

    review_result_path = Path(sys.argv[1])
    if not review_result_path.exists():
        fail(f"ReviewResult not found at {review_result_path}")

    result, yaml_error = parse_frontmatter(review_result_path)
    if result is None:
        fail(f"Could not read {review_result_path}")
    if yaml_error:
        fail(f"invalid YAML frontmatter: {yaml_error}")

    if "checked" in result:
        fail("ReviewResult contains checked; use reviewScope instead")

    verdict = result.get("verdict")
    if verdict not in VALID_VERDICTS:
        fail(f"verdict is {verdict!r}, expected one of {sorted(VALID_VERDICTS)}")

    review_scope = result.get("reviewScope")
    if not review_scope:
        fail("reviewScope is missing or empty")

    if not result.get("workflowBranchId"):
        fail("workflowBranchId is missing or empty in ReviewResult")

    findings = result.get("findings", [])
    if findings is None:
        findings = []
    if not isinstance(findings, list):
        fail(f"findings must be a list when present, got {type(findings).__name__}")

    must_fix_findings: list[dict[str, Any]] = []
    advisory_findings: list[dict[str, Any]] = []
    governance_must_fix: list[dict[str, Any]] = []

    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            fail(f"findings[{index}] must be an object")

        severity = finding.get("severity")
        if severity not in VALID_SEVERITIES:
            fail(f"findings[{index}].severity is {severity!r}, expected one of {sorted(VALID_SEVERITIES)}")

        category = finding.get("category")
        if category not in VALID_CATEGORIES:
            fail(f"findings[{index}].category is {category!r}, expected one of {sorted(VALID_CATEGORIES)}")

        if severity == "must_fix":
            must_fix_findings.append(finding)
        if severity in {"must_fix", "should_fix"}:
            advisory_findings.append(finding)
        if severity == "must_fix" and category == "governance_defect":
            governance_must_fix.append(finding)

    if verdict == "Accepted" and must_fix_findings:
        fail("Accepted verdict requires no must_fix findings")

    if verdict == "ChangesRequested" and not advisory_findings:
        fail("ChangesRequested verdict requires at least one must_fix or should_fix finding")

    if verdict == "Rejected" and not must_fix_findings:
        fail("Rejected verdict requires at least one must_fix finding")

    if verdict == "TicketInvalid" and not governance_must_fix:
        fail("TicketInvalid verdict requires at least one must_fix governance_defect finding")

    print(json.dumps({"valid": True, "verdict": verdict, "error": ""}))


if __name__ == "__main__":
    main()
