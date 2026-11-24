---
id: agent_trace_evaluation
version: 1.0.0
when_to_use: "Use when the task requires agent trace evaluation."
---

# Agent trace evaluation

## Approach

Define the task, allowed actions, success criteria and source of host traces before judging an agent run.

## Verification and handoff

Compare invoked roles, tool calls, skill reads and outputs to evidence; label unobservable activity unknown.

A ledger entry, claimed skill path or file hash is a claim about activity, not
proof that the host invoked an agent or read a skill. Compare with host traces
when available. Missing traces mean the action is unverified; they do not by
themselves establish that it did not happen. Report the evidence source and any
limits on its completeness for each conclusion.

Report the inputs, decisions, evidence, assumptions and blockers to the next role. Use existing project constraints and explicit authorization; do not invent an execution or external result.
