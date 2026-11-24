---
id: prompt_injection_tool_abuse
version: 1.0.0
when_to_use: "Use when the task requires prompt injection and tool abuse."
---

# Prompt injection and tool abuse

## Approach

Map trust boundaries between user requests, retrieved content, tool output and executable actions.

## Verification and handoff

Test malicious instructions in untrusted content and confirm authorization and tool boundaries independently of model compliance.

Report the inputs, decisions, evidence, assumptions and blockers to the next role. Use existing project constraints and explicit authorization; do not invent an execution or external result.
