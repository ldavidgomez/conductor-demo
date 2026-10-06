---
taskId: TASK-20261006-002-reviewer-changes
status: ReadyForDev
activeWorkflowBranchId: null
lastTransitionBy: HumanOperator
lastTransitionReason: "Demo seed: authorised for review scenario"
updatedAt: 2026-10-06T10:00:00Z
authorizedForDevBy: Demo presenter
authorizedForDevAt: 2026-10-06T10:00:00Z
authorizationReason: Ticket has clear, testable acceptance criteria for the review-route demo.
---

# Demo: greeting function rejected by Reviewer

## Goal

Implement a small function whose intentionally incomplete first delivery gives
Reviewer a concrete, evidence-based reason to request changes.

## Scope

### Product/source scope

- `demo-app/greeting.py`
- `.agentops/tickets/ready-for-dev/TASK-20261006-002-reviewer-changes/`

### Not Included

No files outside `demo-app/` and this ticket directory may change.

## Requirements

- Expose `greeting(name)`.
- Return `Hello, <name>!` for a non-empty name.
- Reject empty or whitespace-only names with `ValueError`.

## Acceptance Criteria

- [ ] `greeting("Ada")` returns `Hello, Ada!`.
- [ ] `greeting("")` raises `ValueError`.
- [ ] The Reviewer records a concrete finding if either criterion is missing.

## Demo note

The first Dev attempt deliberately omits the empty-name check. This transparent
fault injection exists only to make the `ChangesRequested` route reproducible.

## Links

- Implementation: implementation-prompt.md
- Review: review-prompt.md
