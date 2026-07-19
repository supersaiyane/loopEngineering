# Sprint 1 Implementation Decisions

**Project:** HealthGuard Pro  
**Sprint:** 1  
**Date:** 2026-07-17 → 2026-07-31  
**Scope:** Auth service, patient CRUD scaffold, EKS infra, CI/CD

> Decisions made *during* implementation. Design decisions pre-sprint are in the ADRs (`docs/adr/`).

---

## D-001 — JWT role embedded at login, not fetched per-request

**Decision:** Encode `role` into the JWT payload at login time. Don't look up the user's role from the DB on every API request.

**Context:** Two options: (A) encode role in JWT once at login, (B) hit the DB on every request to get current role.

**Rationale:** Clinical APIs are high-frequency read paths (monitoring dashboards poll every 5 seconds per patient). DB lookup per-request adds 5–15ms + connection pool pressure at scale. Option A is standard practice for JWTs.

**Trade-off accepted:** Role changes (e.g., nurse promoted to admin) don't take effect until the user logs out and back in. This is acceptable for healthcare — role changes are rare HR events, not real-time operations.

**Alternative rejected:** Redis role cache per user — adds complexity without enough benefit vs. re-login.

**Owner:** BACKEND_LEAD  
**Story:** AUTH-004

---

## D-002 — SCIM implemented directly (RFC 7644), no SCIM library

**Decision:** Implement the SCIM 2.0 API from scratch against RFC 7644, rather than importing a Go SCIM library.

**Context:** Ponytail check found no Go SCIM library at Rung 2 or above. Best candidate (`elimity-com/scim`) had <10k weekly downloads.

**Rationale:** SCIM is REST + simple JSON schemas. The full implementation is ~250 lines of Go. A thin library at Rung 3 or below introduces a supply-chain risk not worth taking for that code surface.

**Trade-off accepted:** More boilerplate (SCIM error formatting, pagination, ServiceProviderConfig). Mitigated by the small surface area.

**Owner:** BACKEND_LEAD  
**Story:** AUTH-003  
**Ref:** Ponytail Ladder §3 — "Rung 2 or above required for production dependencies"

---

## D-003 — WebAuthn challenge stored in Redis (not Postgres)

**Decision:** Store WebAuthn registration and login challenges in Redis with a 5-minute TTL. Delete the key immediately on use.

**Context:** Challenges need: (a) short TTL, (b) delete-on-use for replay prevention, (c) fast lookup by tenantID+userID.

**Rationale:** Postgres could work but adds a GC job to delete expired challenges. Redis TTL + DEL-on-use is the canonical pattern. Redis is already in the stack for Sprint 2 JWT revocation.

**Implementation detail:** Key scheme: `webauthn:reg:{tenantID}:{userID}` — not just `{userID}`, to prevent a challenge issued under one tenant being consumed under another.

**Owner:** BACKEND_LEAD  
**Story:** AUTH-001

---

## D-004 — Per-tenant MRN uniqueness, not global MRN index

**Decision:** `UNIQUE(tenant_id, mrn)` on the `patients` table. No index on `mrn` alone.

**Context:** MRNs are hospital-assigned identifiers. Two hospitals can assign the same MRN to different patients.

**Rationale:** Global MRN uniqueness would be incorrect (MRN namespace is per-hospital). An `mrn`-only index would also allow cross-tenant patient lookup by MRN, violating isolation.

**HIPAA implication:** All MRN lookups must supply `tenant_id` in the WHERE clause. Enforced by the store layer — no method accepts MRN without tenant_id parameter.

**Owner:** BACKEND_LEAD, ARCHITECT  
**Story:** PAT-001

---

## D-005 — GDPR region: Terraform state bucket in eu-west-1, not us-east-1

**Decision:** The eu-west-1 Terraform remote state S3 bucket is created in eu-west-1 (not the default us-east-1).

**Context:** Terraform S3 backend defaults to the CLI-configured region, which for this team is us-east-1. If not overridden, eu-west-1 state would be stored in us-east-1.

**Rationale:** Terraform state for eu-west-1 resources contains resource ARNs, IP addresses, and config that constitutes EU infrastructure metadata. Storing this in us-east-1 would be a GDPR data residency risk (not a hard legal violation, but a risk we want to avoid given our GDPR compliance posture).

**Implementation:** `infra/terraform/eu-west-1/main.tf` → backend `region = "eu-west-1"` explicitly set.

**Owner:** DEVOPS_ENGINEER  
**Story:** INFRA-001

---

## D-006 — Conditional CI jobs for Sprint 2 services (not skipped, not failing)

**Decision:** `patient-data-service` and `sepsis-scoring-service` CI jobs use `if: hashFiles('services/.../go.mod') != ''` to skip if the service doesn't exist yet.

**Context:** Sprint 1 doesn't ship a patient-data-service or sepsis-scoring-service Go module. The CI workflow is written for the full architecture.

**Rationale:** Hard-coding these jobs as non-conditional would fail CI on every Sprint 1 commit. Removing them from the workflow would require a PR in Sprint 2 to add them back. Conditional guards let the workflow file represent the full intended pipeline without breaking the current build.

**Owner:** DEVOPS_ENGINEER  
**Story:** INFRA-002

---

## D-007 — bcrypt token hash for SCIM bearer tokens (not HMAC)

**Decision:** SCIM bearer tokens are stored as bcrypt hashes (`bcrypt.DefaultCost = 10`), not HMAC-SHA256.

**Context:** SCIM tokens are long-lived secrets (provisioned per-tenant, rotated by IT admin). Two options: HMAC-SHA256 (fast verify) vs bcrypt (slow verify, but standard for secrets at rest).

**Rationale:** SCIM endpoints are called infrequently (provisioning/deprovisioning events, not per-API-call). The bcrypt cost (50–100ms) is negligible on this traffic pattern but adds significant resistance if the `scim_tokens` table is ever exfiltrated. HMAC would require protecting a signing key; bcrypt is self-contained.

**Owner:** BACKEND_LEAD  
**Story:** AUTH-003

---

## D-008 — Distroless runtime image, not alpine

**Decision:** `gcr.io/distroless/static-debian12` as the Docker runtime image, not `alpine:3`.

**Context:** Two lightweight runtime options: Alpine (~7MB, has shell + package manager) vs Distroless (~2MB, no shell, no package manager, non-root by default).

**Rationale:** For a HIPAA-compliant service, a shell in the container is an attack surface. If an attacker achieves code execution, they have no shell to pivot from in a distroless container. The Go binary is statically compiled (CGO_ENABLED=0), so no libc dependency — distroless/static is the right base.

**Owner:** DEVOPS_ENGINEER  
**Story:** AUTH-001 (Dockerfile)

---

## D-009 — IAM budget exceeded → AUTH-002 (SAML 2.0) deferred to Sprint 2

**Decision:** AUTH-002 removed from Sprint 1 backlog and deferred to Sprint 2.

**Context:** Fix 33A IAM budget check triggered: AUTH-001(8) + AUTH-002(6) + AUTH-003(5) = 19pts = 73% of sprint capacity. Threshold is 35%.

**Rationale:** No hospital in the Sprint 1 beta cohort uses Okta exclusively (all have SCIM capability). SAML is required for Okta-only hospitals but not for first cohort. WebAuthn + SCIM covers all Sprint 1 requirements.

**Owner:** CTO (decided in sprint planning)  
**ADR:** ADR-003  
**Story:** AUTH-002 (deferred)
