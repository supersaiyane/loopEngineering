# AUTH-004 — RBAC Role Enforcement Middleware

**Epic:** HEALTHGUARD-001 — Auth Platform  
**Sprint:** 1  
**Points:** 2 (S)  
**Labels:** `be/auth` `security-critical`  
**Primary Agent:** BACKEND_LEAD  
**Co-Agent:** SECURITY_ENGINEER  
**Status:** ✅ DONE  

---

## User Story

> **As a** SECURITY_ENGINEER,  
> **I want to** enforce role-based access control on every API route via a reusable middleware,  
> **So that** a NURSE cannot call admin endpoints and an IT_ADMIN cannot access clinical data endpoints.

---

## Acceptance Criteria

- [ ] `RequireRole(roles ...Role)` Gin middleware rejects requests with 403 if JWT role not in allowed set
- [ ] `TenantID(c)`, `UserID(c)`, `Role(c)` safe extractors: panic (5xx) if `RequireJWT` middleware not applied upstream
- [ ] `AssertSameTenant(c, resourceTenantID)` returns false + writes 403 if resource tenant ≠ JWT tenant
- [ ] Role hierarchy respected:
  - NURSE: patient read/write, own profile
  - PHYSICIAN: all NURSE permissions + discharge patients + view sepsis alerts
  - ADMIN: all clinical + org-level reporting
  - IT_ADMIN: user management (SCIM) + system config, NO clinical data access
- [ ] Role is embedded in JWT at login — not looked up from DB on every request (performance)
- [ ] Role change takes effect on next login (no mid-session role update) — documented in TRD
- [ ] `TestRequireRole_AllowedRole` and `TestRequireRole_ForbiddenRole` cover all 4 roles
- [ ] SECURITY_ENGINEER co-review mandatory (be/auth + security-critical labels)

---

## Role Matrix

| Endpoint | NURSE | PHYSICIAN | ADMIN | IT_ADMIN |
|----------|-------|-----------|-------|---------|
| GET /v1/patients | ✅ | ✅ | ✅ | ❌ |
| POST /v1/patients | ✅ | ✅ | ✅ | ❌ |
| GET /v1/alerts | ✅ | ✅ | ✅ | ❌ |
| GET /v1/reports/org | ❌ | ❌ | ✅ | ❌ |
| SCIM /scim/v2/Users | ❌ | ❌ | ❌ | ✅ (token) |
| POST /v1/auth/register | ✅ | ✅ | ✅ | ✅ |

---

## Technical Notes

**Implementation:** `services/auth-service/middleware/tenant.go`  
**No new dependencies.**

The role is encoded in the JWT claims (`role` field) at login time. Middleware reads from context — zero DB calls per request for role checks.

Role-change attack surface: if a user's role is elevated, they must log out and back in. This is acceptable for a clinical environment where role changes are rare HR events.

---

## GATE S2 Checklist

```
✅  SAST                                    — 0 findings
✅  OWASP A01 Broken Access Control         — roles enforced before any business logic
✅  Role confusion test                     — NURSE JWT on admin endpoint → 403 ✅
✅  IT_ADMIN isolation test                 — IT_ADMIN JWT on /v1/patients → 403 ✅
✅  No secrets committed                    — PASS
✅  Property-based tests (security-critical) — all 4 roles × all protected routes ✅
✅  SECURITY_ENGINEER co-review             — PASS ✅
✅  Test output committed                   — coverage: 82%
```

**GATE S2: PASS → AUTH-004 MERGED**

---

## Linked Files

- `services/auth-service/middleware/tenant.go`
- `services/auth-service/middleware/tenant_test.go`
- `docs/trd.md#auth-model`
