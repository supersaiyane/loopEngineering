# Sprint 1 Plan — HealthGuard Pro

**Sprint:** 1 of N  
**Dates:** 2026-07-17 → 2026-07-31 (2 weeks)  
**Scrum Master:** SCRUM_MASTER  
**Sprint Goal:** Clinician can register a WebAuthn credential, authenticate passwordlessly, and hospital IT can provision users via SCIM. Infrastructure deployed to us-east-1.  
**Capacity:** 26 story points  

---

## Pre-Planning: IAM Budget Check (Fix 33A)

> ⚠️ **IAM BUDGET WARNING — Fix 33A triggered**
>
> Auth stories in backlog: AUTH-001 (8pts) + AUTH-002 (6pts) + AUTH-003 (5pts) = **19 pts = 73% of sprint capacity**
>
> Threshold: 35% max for auth/IAM work in a single sprint.
>
> **Resolution options:**
> - Option A: Defer AUTH-002 (SAML) to Sprint 2 → brings auth to 50% (still high)
> - Option B: Defer AUTH-002 + AUTH-004 → brings auth to 31% ✅
> - Option C: Expand sprint capacity to 40pts (not recommended — velocity unknown)
>
> **Decision: Defer AUTH-002 (SAML 2.0) to Sprint 2.**
> Rationale: WebAuthn + SCIM covers all Sprint 1 beta hospital requirements. SAML is needed for Okta-only hospitals — none in first cohort. Logged in ADR-003.

---

## OQ-Resolved Check (Fix 33B)

No prior sprints — no open questions to resolve. Skip.

---

## Sprint 1 Backlog

### Story Sizing Reference

| Size | Points | Rough effort |
|------|--------|-------------|
| XS | 1 | < 2 hours |
| S | 2 | half day |
| M | 3 | 1 day |
| L | 5 | 2–3 days |
| XL | 8 | full week |

---

### Stories Selected for Sprint 1 (26 pts total)

| Story ID | Title | Size | Points | Labels | Primary Agent | Co-Agent |
|----------|-------|------|--------|--------|--------------|---------|
| AUTH-001 | WebAuthn registration + authentication | XL | 8 | `be/auth` `security-critical` | BACKEND_LEAD | SECURITY_ENGINEER |
| AUTH-003 | SCIM 2.0 provisioning API | L | 5 | `be/api` | BACKEND_LEAD | — |
| PAT-001 | Patient CRUD + tenant isolation | M | 3 | `be/api` `e2e-required` | BACKEND_LEAD | — |
| INFRA-001 | EKS cluster + VPC (Terraform) | L | 5 | `infra/deploy` | DEVOPS_ENGINEER | SRE_ENGINEER |
| INFRA-002 | CI/CD pipeline (GitHub Actions) | M | 3 | `infra/deploy` | DEVOPS_ENGINEER | — |
| AUTH-004 | RBAC role enforcement middleware | M | 2 | `be/auth` `security-critical` | BACKEND_LEAD | SECURITY_ENGINEER |
| **TOTAL** | | | **26** | | | |

### Deferred to Sprint 2

| Story ID | Title | Points | Reason |
|----------|-------|--------|--------|
| AUTH-002 | SAML 2.0 SSO | 6 | IAM budget exceeded 35% threshold |
| PAT-002 | Vitals ingestion pipeline | 5 | Auth foundation required first |
| PAT-003 | HIPAA audit log | 3 | Included in auth-service (Sprint 1 partial) |
| ML-001–003 | Sepsis AI scoring | 13 | Patient data API required first |
| RT-001 | WebSocket gateway | 5 | Alerting after core data |
| MOB-001–003 | Mobile apps | 8 | API layer required first |

---

## Label Validation (Fix 28D — SM self-challenge)

Each label checked against skill-label-index.md before finalizing routing:

```
be/auth         → BACKEND_LEAD + SECURITY_ENGINEER (mandatory co-review)    ✅
be/api          → BACKEND_LEAD                                                ✅
security-critical → adds property_based_testing.md to VERIFIER suite          ✅
e2e-required    → VERIFIER must run full E2E suite (not just unit)            ✅
infra/deploy    → DEVOPS_ENGINEER + SRE_ENGINEER                              ✅
```

---

## Sprint 1 Execution Order

```
Week 1 (Days 1–5):
  Day 1–2:  AUTH-001 (WebAuthn) — BACKEND_LEAD + SECURITY_ENGINEER
  Day 2–3:  INFRA-001 (EKS + VPC) — DEVOPS_ENGINEER (parallel track)
  Day 3–4:  AUTH-003 (SCIM) — BACKEND_LEAD
  Day 4–5:  AUTH-004 (RBAC) — BACKEND_LEAD + SECURITY_ENGINEER

Week 2 (Days 6–10):
  Day 6–7:  PAT-001 (Patient CRUD) — BACKEND_LEAD
  Day 7–8:  INFRA-002 (CI/CD) — DEVOPS_ENGINEER
  Day 8–9:  GATE S2 reviews — SECURITY_ENGINEER + VERIFIER
  Day 9–10: Buffer / GATE 5 prep / sprint retro
```

---

## Definition of Done (per story)

- [ ] Code written and reviewed by co-agent (if applicable)
- [ ] VERIFIER ran tests — output committed (not self-reviewed)
- [ ] Cross-tenant denial test present if story touches multi-tenant data
- [ ] GATE S2 checklist signed off (SAST, OWASP, secrets scan, ponytail check)
- [ ] `impl-decisions.md` updated with any decisions made
- [ ] Story moved to DONE in tracker

---

## GATE S1 Sign-off (pre-code security gate)

```
✅  STRIDE threat model complete (docs/trd.md#threat-model)
✅  Auth + authz model reviewed (ADR-002 WebAuthn, RBAC in PRD)
✅  Secrets management: AWS Secrets Manager for DB creds + JWT secret
✅  OWASP Top-10 reviewed: A01 broken access, A07 auth failures
✅  Compliance scope: HIPAA BAA template ready, GDPR DPA template ready
✅  No code to be written until this gate passed
```

**GATE S1: PASS — DEVELOP phase unlocked · 2026-07-17**

---

*Sprint plan approved · SM-PLAN complete · Fix 47B auto-trigger fired*
