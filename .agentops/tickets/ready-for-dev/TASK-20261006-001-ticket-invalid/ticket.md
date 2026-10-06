---
taskId: TASK-20261006-001-ticket-invalid
status: ReadyForDev
activeWorkflowBranchId: null
lastTransitionBy: HumanOperator
lastTransitionReason: "Demo seed: invalid precondition"
updatedAt: 2026-10-06T10:00:00Z
authorizedForDevBy: Demo presenter
authorizedForDevAt: 2026-10-06T10:00:00Z
---

# Demo: invalid ticket precondition

## Goal

Show that the deterministic workflow rejects an incompletely authorised ticket
before it invokes Dev or Reviewer.

## Scope

### Product/source scope

No product files may change.

### Not Included

No implementation, review or agent invocation occurs.

## Acceptance Criteria

- [ ] The workflow reports the missing authorisation precondition.
- [ ] The workflow routes to `TicketInvalid`.
- [ ] No LLM is invoked.

## Deliberate defect

`authorizationReason` is intentionally absent from the frontmatter.

## Links

- Implementation: implementation-prompt.md
- Review: review-prompt.md
