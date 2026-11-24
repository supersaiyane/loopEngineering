---
id: ai_trace_instrumentation
version: 1.0.0
when_to_use: "Use when the task requires ai trace instrumentation."
---

# AI trace instrumentation

## Approach

Capture supported operation, model, duration, outcome and correlation identifiers across agent and tool calls.

## Verification and handoff

Validate trace completeness and redaction; avoid logging prompts, tool results or personal data by default.

Report the inputs, decisions, evidence, assumptions and blockers to the next role. Use existing project constraints and explicit authorization; do not invent an execution or external result.
