# Lessons — HealthGuard Pro

**Framework:** Loop Engineering v9.5 — Fix 40A 5-Stage Progression  
**Rule:** New lessons enter at STAGE 1. Graduation requires evidence from subsequent sprints.

## Stages

| Stage | Meaning | Graduation Trigger |
|-------|---------|-------------------|
| 1 | Observed once — raw lesson | Appears again in next sprint |
| 2 | Pattern confirmed — applies broadly | Applied correctly in 2+ sprints |
| 3 | Team internalized | No reminders needed, self-applied |
| 4 | Embedded in process | Added to template/gate/checklist |
| 5 | Retired — embedded everywhere | Remove from lessons.md |

---

## STAGE 1 — Observed this sprint (Sprint 1)

### L-001 · IAM budget concentrations surface early when you measure them

**Observed:** IAM budget check (Fix 33A) triggered in sprint planning with 73% of capacity assigned to auth stories. Without this check, AUTH-001 + AUTH-002 + AUTH-003 would all have been committed, creating a fragile sprint where one auth story blocking would halt the entire sprint.

**Action taken:** AUTH-002 (SAML) deferred to Sprint 2. Sprint delivered 100% of committed stories.

**Lesson:** High IAM concentration isn't always avoidable (some sprints ARE auth sprints), but making it visible early changes the conversation from "why is Sprint 1 late?" to "we knowingly deferred SAML."

```yaml
stage: 1
graduation_trigger: "IAM budget check fires in Sprint 2 and the capacity decision (defer or buffer) is made correctly without being reminded"
confirmed_at: null
confirmed_in_sprint: null
```

---

### L-002 · Ponytail check saves you from SCIM library supply-chain risk

**Observed:** Evaluated `elimity-com/scim` for SCIM 2.0 implementation. Failed Rung 2 (<10k weekly downloads). Instead of accepting a Rung 3 library for RFC 7644 (a stable, simple spec), implemented directly in ~250 lines.

**Result:** No external SCIM dependency. Zero supply-chain risk for that surface. SCIM spec is stable — direct implementation is lower total cost than maintaining a Rung 3 lib.

**Lesson:** For stable, bounded specs (SCIM, JOSE, simple REST schemas), direct implementation beats a low-rung library. Ponytail check catches this decision point before code is written.

```yaml
stage: 1
graduation_trigger: "Sprint 2 contains a bounded-spec implementation decision and direct implementation is chosen over a Rung 3 library without being prompted"
confirmed_at: null
confirmed_in_sprint: null
```

---

### L-003 · Tenant_id on credentials (not just users) prevents cross-tenant credential replay

**Observed:** Initial schema draft had `tenant_id` on `users` but not on `webauthn_credentials`. A credential could theoretically be used to authenticate under a different tenant if only user-level isolation existed.

**Fix applied:** `tenant_id` added to `webauthn_credentials` + challenge cache key includes `tenantID` in the prefix (`webauthn:reg:{tenantID}:{userID}`).

**Lesson:** Tenant isolation must be applied at the credential level, not just the user level. The attack vector is: attacker creates account in their tenant, registers a hardware key, then attempts to use that key against a target user's account in another tenant. Tenant_id on the credential prevents this.

```yaml
stage: 1
graduation_trigger: "Next multi-tenant auth feature schema includes tenant_id on all credential/token tables without explicit reminder in story AC"
confirmed_at: null
confirmed_in_sprint: null
```

---

### L-004 · distroless containers eliminate shell-pivot attack surface at near-zero cost

**Observed:** Go binaries compile to static executables (CGO_ENABLED=0). The distroless/static image is appropriate and produces a ~8MB container with no shell, no package manager, and a non-root user by default.

**HIPAA implication:** In a HIPAA environment, a container shell is an attack escalation path. An attacker with code execution in an Alpine container has bash. An attacker with code execution in a distroless container has nothing to pivot from.

**Lesson:** For statically compiled Go services, distroless/static is always preferred over Alpine for production. The only cost is that debugging requires ephemeral debug containers (`kubectl debug`).

```yaml
stage: 1
graduation_trigger: "All new Go service Dockerfiles in Sprint 2 use distroless/static without being specified in story ACs"
confirmed_at: null
confirmed_in_sprint: null
```

---

### L-005 · GDPR Terraform state residency is easy to miss without an explicit checklist item

**Observed:** The eu-west-1 Terraform backend defaulted to the CLI's configured region (us-east-1) unless overridden explicitly. The fix is one line: `region = "eu-west-1"` in the backend block. But it's invisible unless you check.

**Lesson:** GDPR data residency applies to infrastructure metadata, not just application data. Terraform state contains resource ARNs, IP ranges, and config that represents EU infrastructure. Add "Terraform state bucket in correct region?" as a GATE S2 infra checklist item.

```yaml
stage: 1
graduation_trigger: "Next INFRA story with multi-region scope correctly sets Terraform state bucket region without explicit reminder"
confirmed_at: null
confirmed_in_sprint: null
```

---

### L-006 · Soft-delete-only enforcement needs to be at the store layer, not just the schema

**Observed:** The `patients` table has `deleted_at` for HIPAA compliance (no hard deletes). But if any handler calls `store.DeleteUser()` and that method issued a `DELETE FROM patients`, the schema annotation wouldn't catch it.

**Fix applied:** All `DeleteUser`/`DeletePatient` methods in the store layer do `UPDATE ... SET deleted_at = NOW()` — there is literally no `DELETE FROM` statement in the store for HIPAA-scoped tables.

**Lesson:** HIPAA "no hard delete" must be enforced in code, not just documented in the schema. Code review should grep for `DELETE FROM patients` / `DELETE FROM users` as a security gate.

```yaml
stage: 1
graduation_trigger: "Next HIPAA-scoped data story has no DELETE FROM on patient/user tables in store layer — soft-delete enforced without being called out in AC"
confirmed_at: null
confirmed_in_sprint: null
```

---

## STAGE 4 — Embedded in process (from framework, applies to all projects)

### L-F01 · IAM work >35% of sprint → alert + defer (Fix 33A)

Embedded in: `team-orchestrator-sprint.md` SM-PLAN section, `sprint-plan.md` template.

### L-F02 · Cross-tenant denial test mandatory on every multi-tenant endpoint (Fix 43C)

Embedded in: GATE S2 checklist, `skill-label-index.md` (`be/api` label row).

### L-F03 · Ponytail check before any new dependency (Rung 2 minimum)

Embedded in: GATE S2 checklist, `ponytail.md`, `team-orchestrator-sprint.md`.

### L-F04 · All SQL must include tenant_id filter — no exceptions

Embedded in: `database_schema_design.md`, `team-orchestrator-sprint.md` invariant list.
