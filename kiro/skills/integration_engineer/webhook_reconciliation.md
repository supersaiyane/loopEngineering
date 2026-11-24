---
id: webhook_reconciliation
version: 1.0.0
when_to_use: "Use when the task requires webhook reconciliation."
---

# Webhook reconciliation

## Approach

Verify signatures and timestamps, enforce idempotency and handle retries, ordering and delivery failures.

## Verification and handoff

Reconcile accepted events to durable state; never report a simulated integration as a real provider transaction.

Report the inputs, decisions, evidence, assumptions and blockers to the next role. Use existing project constraints and explicit authorization; do not invent an execution or external result.
