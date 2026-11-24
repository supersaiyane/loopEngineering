---
id: tenant_safe_integration_design
version: 1.0.0
when_to_use: "Use when the task requires tenant-safe integration design."
---

# Tenant-safe integration design

## Approach

Specify authorization at object and tenant boundaries, secure upload contracts and webhook signature/idempotency rules.

## Verification and handoff

Test cross-tenant requests, duplicate events and unavailable providers against declared contracts.

Report the inputs, decisions, evidence, assumptions and blockers to the next role. Use existing project constraints and explicit authorization; do not invent an execution or external result.
