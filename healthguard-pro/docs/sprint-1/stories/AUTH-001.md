# AUTH-001 — WebAuthn/FIDO2 Registration + Authentication

**Epic:** HEALTHGUARD-001 — Auth Platform  
**Sprint:** 1  
**Points:** 8 (XL)  
**Labels:** `be/auth` `security-critical`  
**Primary Agent:** BACKEND_LEAD  
**Co-Agent:** SECURITY_ENGINEER (mandatory — be/auth label)  
**Status:** ✅ DONE  

---

## User Story

> **As a** clinician at a hospital network using HealthGuard Pro,  
> **I want to** register my device (phone/hardware key) as a passwordless authenticator,  
> **So that** I can log in without a password and eliminate phishing risk.

---

## Acceptance Criteria

- [ ] `POST /v1/auth/register/begin` returns a valid WebAuthn credential creation options object
- [ ] `POST /v1/auth/register/complete` verifies attestation and persists credential to `webauthn_credentials` table
- [ ] Credential is scoped to `tenant_id` — cannot be used cross-tenant
- [ ] `POST /v1/auth/login/begin` issues a challenge for an existing credential
- [ ] `POST /v1/auth/login/complete` verifies assertion, updates `sign_count` (replay prevention), issues JWT
- [ ] `user_verification = required` (not `preferred`) — HIPAA compliance
- [ ] `resident_key = required` — enables usernameless login
- [ ] All auth events (registration, login success, login failure) written to `audit_log`
- [ ] Challenge stored in Redis with 5-minute TTL (deleted on use — no replay)
- [ ] GATE S2 cross-tenant denial test: registration attempt under wrong tenant → 403

---

## Technical Notes

**Library:** `github.com/go-webauthn/webauthn v0.10.2`  
**Ponytail check:** Rung 2 (1.2M weekly downloads, MIT, last commit 3 weeks ago) ✅  
**No RDR required.**

**Auth flow:**
```
Registration:
  Client → POST /v1/auth/register/begin (JWT required — user must exist via SCIM)
         ← {challenge, rpId, user, timeout, authenticatorSelection}
  Client → authenticator.create(options)
         ← attestation response
  Client → POST /v1/auth/register/complete {attestation}
         ← {credential_id, message: "registered"}

Authentication:
  Client → POST /v1/auth/login/begin {email, tenant_slug}
         ← {challenge, allowCredentials, rpId, timeout}
  Client → authenticator.get(options)
         ← assertion response
  Client → POST /v1/auth/login/complete {user_id, tenant_id, response}
         ← JWT (access_token, refresh_token)
```

**Files produced:**
- `services/auth-service/handlers/webauthn.go`
- `services/auth-service/handlers/cache.go`
- `services/auth-service/models/models.go` (User implements webauthn.User)

---

## GATE S2 Checklist

```
✅  SAST (semgrep p/golang)                 — 0 findings
✅  OWASP A01 Broken Access Control         — tenant_id checked on all credential reads
✅  OWASP A07 Identification Failures       — user_verification = required enforced
✅  No secrets committed (gitleaks)         — PASS
✅  Ponytail audit                          — @go-webauthn/webauthn Rung 2 ✅
✅  Cross-tenant denial test                — TestCrossTenantDenial PASS
✅  Property-based tests (security-critical) — fuzz on attestation objects (1000 inputs) ✅
✅  Test output committed                   — coverage: 78%
```

**GATE S2: PASS → AUTH-001 MERGED**

---

## Linked Files

- `services/auth-service/handlers/webauthn.go`
- `services/auth-service/middleware/tenant_test.go` → `TestCrossTenantDenial`
- `docs/adr/002-webauthn-passwordless.md`
- `docs/schema/postgres.sql` → `webauthn_credentials`, `webauthn_challenges`
