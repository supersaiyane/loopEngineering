# ADR-003: SAML 2.0 SSO Deferred to Sprint 2

**Date:** 2026-07-17  
**Status:** Accepted  

## Context

Sprint 1 capacity: 26 story points. Auth stories (WebAuthn + SCIM + RBAC) consumed 42% of capacity, exceeding the 35% IAM budget threshold (Fix 33A enforcement).

SAML 2.0 adds ~8 story points of implementation + security review overhead.

## Decision

Defer SAML 2.0 to Sprint 2. WebAuthn covers all auth requirements for Sprint 1 beta hospitals.

## Impact

- Sprint 1 beta hospitals use WebAuthn + SCIM only
- Hospitals with Okta/Azure AD can still provision users via SCIM
- Hospitals requiring SAML-only auth cannot onboard until Sprint 2 (estimated 3 weeks)

## Sprint 2 Plan

Implementation file: `kiro/skills/security_engineer/saml_security.md`  
Stories: AUTH-002 (SAML IdP integration), AUTH-006 (SAML session management)  
Security requirements from [saml_security.md]:
- XXE injection prevention on XML parser
- Signature validation: both message AND assertion
- ACS URL validated against allowlist
- Replay prevention: assertion ID cache (24h TTL)
- IdP-initiated flow: disabled by default
