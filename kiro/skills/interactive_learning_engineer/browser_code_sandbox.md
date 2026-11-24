---
id: browser_code_sandbox
version: 1.0.0
when_to_use: "Use when the task requires browser code sandbox."
---

# Browser code sandbox

## Approach

Define execution isolation, message boundaries, timeouts, resource limits and permitted APIs for untrusted code.

## Verification and handoff

Test runaway code and boundary escape attempts; a browser worker alone is not a complete security boundary.

Report the inputs, decisions, evidence, assumptions and blockers to the next role. Use existing project constraints and explicit authorization; do not invent an execution or external result.
