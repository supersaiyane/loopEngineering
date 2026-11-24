---
id: safe_api_session_implementation
version: 1.0.0
when_to_use: "Use when the task requires safe api and session implementation."
---

# Safe API and session implementation

## Approach

Implement stack-appropriate tenant-scoped data access and session controls from the approved design.

For NestJS with Prisma and PostgreSQL, apply authorization at both route and
object boundaries and bind tenant context to the same transaction and connection
used by the query. Verify the application role cannot bypass RLS and that a
pooled connection cannot retain another tenant's context. Use the actual
project's ORM and database equivalents when this stack is not in use.

## Verification and handoff

Test unauthorized access, session expiration, invalid inputs and framework-specific failures.
Exercise cross-tenant identifiers, revoked sessions, transaction failures and
concurrent requests with two tenants using a disposable database.

Report the inputs, decisions, evidence, assumptions and blockers to the next role. Use existing project constraints and explicit authorization; do not invent an execution or external result.
