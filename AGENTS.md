<!-- managed-by: agentops -->
<!-- agentops-artifact: provider-entrypoint -->
<!-- agentops-provider: codex -->
<!-- agentops-version: 0.1.0 -->
# AgentOps Project

This repository uses AgentOps Core.

## Canonical AgentOps Core

Canonical AgentOps behavior is located at:

- ~/.agentops/agents/
- ~/.agentops/rules/
- ~/.agentops/workflows/
- ~/.agentops/templates/

These files are the canonical behavioral source of truth.

Do not modify AgentOps Core files from this repository.

---

## Project Operational Context

Project-specific operational context is located at:

- .agentops/

This includes:
- architecture
- contracts
- decisions
- domain knowledge
- tickets
- tech debt

Always prefer .agentops/ as the project source of truth.

---

## Project Guidance

Before acting, read the project guidance and canonical context:

- .agentops/agent-guidance.md, if present
- .agentops/project-overview.md
- .agentops/decisions/DECISIONS.md

Do not treat provider-local memory as canonical. Durable project knowledge must be promoted into versioned repository files.

---

## Available AgentOps Modes

Available canonical operational modes:

- discuss
- grill-me
- pm
- dev
- reviewer

When the user explicitly invokes one of these modes:

```text
/pm /dev /reviewer /discuss /grill-me
```

load the corresponding canonical behavior from:

```text
~/.agentops/agents/<mode>.md
```

and apply its rules strictly.

---

## Mandatory Operational Rules

Always:
- preserve strict scope discipline
- surface ambiguities explicitly
- avoid silent assumptions
- prefer minimal safe changes
- follow canonical working agreement
- follow canonical testing guidelines

Never:
- redefine canonical agent behavior locally
- invent requirements
- silently change architecture
- modify unrelated code
- modify AgentOps Core files

---

## Ownership Boundary

AgentOps Core:
- behavioral rules
- workflows
- templates
- governance

Project Repository:
- business logic
- implementation
- project operational context
- tickets
- architecture
- domain knowledge
