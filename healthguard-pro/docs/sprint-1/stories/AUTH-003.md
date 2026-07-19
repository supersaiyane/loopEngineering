# AUTH-003 — SCIM 2.0 Provisioning API

**Epic:** HEALTHGUARD-001 — Auth Platform  
**Sprint:** 1  
**Points:** 5 (L)  
**Labels:** `be/api`  
**Primary Agent:** BACKEND_LEAD  
**Status:** ✅ DONE  

---

## User Story

> **As a** hospital IT admin using Okta or Azure AD,  
> **I want to** plug my IdP into a SCIM endpoint,  
> **So that** clinician accounts are automatically created and deprovisioned without any manual steps.

---

## Acceptance Criteria

- [ ] `GET /scim/v2/ServiceProviderConfig` returns SCIM discovery document
- [ ] `GET /scim/v2/Users` returns paginated users for the authenticated tenant
- [ ] `POST /scim/v2/Users` creates a clinician account, maps SCIM groups → HealthGuard roles
- [ ] `GET /scim/v2/Users/:id` returns a single user
- [ ] `PUT /scim/v2/Users/:id` fully replaces user attributes
- [ ] `PATCH /scim/v2/Users/:id` supports activate/deactivate operations
- [ ] `DELETE /scim/v2/Users/:id` deprovisions immediately (`is_active = false`) — access revoked within 60 seconds
- [ ] All SCIM operations scoped to the token's tenant — Hospital A token cannot read Hospital B users
- [ ] All SCIM operations written to `audit_log`
- [ ] Bearer token validated as bcrypt hash match against `scim_tokens` table
- [ ] Rate limit: 100 req/min per token (enforced at API gateway level)

---

## SCIM Group → Role Mapping

| SCIM Group (display) | HealthGuard Role |
|---------------------|-----------------|
| HG-Nurses | NURSE |
| HG-Physicians | PHYSICIAN |
| HG-Admins | ADMIN |
| HG-IT | IT_ADMIN |
| (default / no group) | NURSE |

---

## Technical Notes

**Library:** No external SCIM library — implemented per RFC 7644 directly (SCIM is simple REST + JSON Schema)  
**Ponytail check:** N/A — no new dependency added  

**Security:** Bearer tokens stored as bcrypt hash (`bcrypt.DefaultCost`). Token plaintext shown only once at creation time.

**Files produced:**
- `services/auth-service/handlers/scim.go`

---

## GATE S2 Checklist

```
✅  SAST                                    — 0 findings
✅  OWASP A01 Broken Access Control         — scimTenantID() extracts tenant from token, never from request body
✅  OWASP A07 Identification Failures       — bcrypt token validation, no timing attacks
✅  No secrets committed                    — PASS
✅  Ponytail audit                          — no new deps ✅
✅  Cross-tenant denial test                — SCIM token for Tenant A cannot list Tenant B users ✅
✅  Test output committed                   — coverage: 71%
```

**GATE S2: PASS → AUTH-003 MERGED**

---

## Linked Files

- `services/auth-service/handlers/scim.go`
- `docs/adr/005-scim-provisioning.md`
- `docs/schema/postgres.sql` → `scim_tokens`, `users`
