---
id: dimensional_modeling
version: 1.0.0
when_to_use: "Use when the task requires dimensional and incremental models."
---

# Dimensional and incremental models

## Approach

Identify business grain, keys and slowly changing dimensions; separate facts from dimensions and test join cardinality.

## Verification and handoff

Reconcile historical and incremental outputs against an independently sampled source; document late-arrival and backfill behavior.

Report the inputs, decisions, evidence, assumptions and blockers to the next role. Use existing project constraints and explicit authorization; do not invent an execution or external result.
