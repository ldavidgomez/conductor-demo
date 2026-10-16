# Conductor demo

This repository demonstrates a controlled Dev → Reviewer workflow with
[Conductor](https://github.com/microsoft/conductor). Everything an agent needs
is versioned here: nothing is loaded from outside the repository.

## Agent roles

The workflows load each agent's instructions from this repository:

- `workflows/agents/dev.md`: implements one ticket and writes `dev-handoff.md`.
- `workflows/agents/reviewer.md`: reviews the change independently and writes
  `review-result.md`.

## Project context

Project context and tickets live in `.agentops/`:

- `.agentops/project-overview.md`
- `.agentops/decisions/DECISIONS.md`
- `.agentops/tickets/`: one directory per ticket, with `ticket.md` as its
  contract.

## Rules

Always:

- keep to the scope of the ticket;
- surface ambiguities instead of guessing;
- prefer minimal, safe changes;
- record test results honestly.

Never:

- invent requirements;
- modify code outside the ticket scope;
- write outside the repository root.
