---
id: provider_fallback_operations
version: 1.0.0
when_to_use: "Use when the task requires provider fallback operations."
---

# Provider fallback operations

## Approach

Map provider-specific capabilities, limits, credentials and data handling before implementing failover.

## Verification and handoff

Test timeouts, rate limits, schema differences and unavailable providers; do not fabricate output when all paths fail.

Report the inputs, decisions, evidence, assumptions and blockers to the next role. Use existing project constraints and explicit authorization; do not invent an execution or external result.
