---
id: simulation_project_storage
version: 1.0.0
when_to_use: "Use when the task requires simulation and project storage."
---

# Simulation and project storage

## Approach

Specify simulation correctness, persistence, sharing and access independently from where code executes.

Decide whether saving is local-only or uses authorized backend or object storage.
Define tenant ownership, access checks, deletion and sharing before choosing a
storage path. A requirement that code must not execute on the server does not
by itself prohibit saving or transmitting source; obtain the actual requirement.

## Verification and handoff

Test real outputs, saved-project integrity and authorized sharing without confusing storage with server-side execution.
Exercise save, reopen and cross-tenant denial, and verify that uploaded source
is never executed on the server when the design prohibits it.

Report the inputs, decisions, evidence, assumptions and blockers to the next role. Use existing project constraints and explicit authorization; do not invent an execution or external result.
