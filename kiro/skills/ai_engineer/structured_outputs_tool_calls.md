---
id: structured_outputs_tool_calls
version: 1.0.0
when_to_use: "Use when the task requires structured output and tool calls."
---

# Structured output and tool calls

## Approach

Use validated schemas, explicit tool permissions and bounded execution; handle malformed outputs and unavailable tools.

## Verification and handoff

Test failure, retry, injection and human-approval paths with realistic cases; do not claim instructions enforce controls.

Report the inputs, decisions, evidence, assumptions and blockers to the next role. Use existing project constraints and explicit authorization; do not invent an execution or external result.
