# AgentOps Conductor demo

This repository contains three short, reproducible demonstrations of a controlled Dev → Reviewer workflow.

## Scenarios

1. `01-ticket-invalid`: a deterministic precondition check stops an incomplete ticket before an agent is invoked.
2. `02-changes-requested`: Dev and Reviewer run as separate Copilot agents. A known, injected acceptance-criterion failure produces `ChangesRequested`.
3. `03-happy-path`: the ticket passes Dev, Reviewer and deterministic checks before a human closes it.

Each scenario begins from the `demo-baseline` tag and uses a real ticket under
`.agentops/tickets/ready-for-dev/`. Keep the injected fault in scenario 2
explicit during the presentation: it makes the routing demonstration reliable;
it is not evidence that a reviewer detects every defect.

## Run scenario 1

```powershell
conductor validate workflows/demo/01-ticket-invalid.yaml
conductor run workflows/demo/01-ticket-invalid.yaml
```

The workflow should route straight to the `TicketInvalid` human gate. No LLM call occurs.

## Validate the other scenarios

```powershell
conductor validate workflows/demo/02-changes-requested.yaml
conductor validate workflows/demo/03-happy-path.yaml
```

Run a scenario from a fresh worktree. This keeps agent changes and ticket
artifacts isolated and makes a replay safe:

```powershell
git worktree add ..\demo-changes-requested demo-baseline
cd ..\demo-changes-requested
conductor run workflows/demo/02-changes-requested.yaml
```

For scenario 2, Dev receives an explicit instruction to leave the empty-name
case unhandled. Reviewer must identify that deliberate defect and route the
ticket to `ChangesRequested`. Scenario 3 asks Dev to implement every acceptance
criterion and runs the Python test suite after Reviewer accepts. The tickets are
seeded in `ReadyForDev` solely to keep each live demo short and reproducible.

## Next preparation steps

- Verify Copilot models with `conductor doctor --models --provider copilot`.
- Choose the Dev and Reviewer model names and place them in the workflow YAML files.
- Rehearse each scenario from its own disposable worktree.
