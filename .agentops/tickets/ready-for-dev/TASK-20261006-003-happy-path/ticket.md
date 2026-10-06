---
taskId: TASK-20261006-003-happy-path
status: ReadyForDev
tddMode: simple
activeWorkflowBranchId: null
lastTransitionBy: HumanOperator
lastTransitionReason: "Demo seed: authorised for complete delivery"
updatedAt: 2026-10-06T10:00:00Z
authorizedForDevBy: Demo presenter
authorizedForDevAt: 2026-10-06T10:00:00Z
authorizationReason: Ticket has a bounded scope and deterministic test command.
---

# Demo: greeting function accepted end to end

## Goal

Implement and test a small greeting function, then demonstrate independent
review, deterministic verification and human closure.

## TDD Mode

simple

## Scope

### Product/source scope

- `demo-app/greeting.py`
- `demo-app/tests/test_greeting.py`
- `.agentops/tickets/ready-for-dev/TASK-20261006-003-happy-path/`

### Not Included

No files outside `demo-app/` and this ticket directory may change.

## Requirements

- `greeting(name)` returns `Hello, <name>!` for a non-empty name.
- Empty or whitespace-only names raise `ValueError`.
- Tests use only the Python standard library.

## Acceptance Criteria

- [ ] `greeting("Ada")` returns `Hello, Ada!`.
- [ ] Empty and whitespace-only names raise `ValueError`.
- [ ] `python -m unittest discover -s demo-app/tests` passes.
- [ ] The Reviewer records the evidence for every criterion.

## Links

- Implementation: implementation-prompt.md
- Review: review-prompt.md
