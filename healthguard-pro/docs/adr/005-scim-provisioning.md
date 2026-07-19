# ADR-005: SCIM 2.0 for Hospital IT Provisioning

**Date:** 2026-07-17  
**Status:** Accepted  

## Context

Enterprise hospitals manage thousands of clinician accounts in Okta, Azure AD, or PingFederate. Manual account creation is not scalable and creates deprovisioning risk (ex-employees retaining access).

## Decision

Implement SCIM 2.0 (RFC 7644) as the provisioning protocol. Each tenant gets a bearer token for their IdP to use.

## Scope (Sprint 1)

| Endpoint | Method | Description |
|----------|--------|-------------|
| /scim/v2/Users | GET | List/filter users |
| /scim/v2/Users | POST | Create clinician account |
| /scim/v2/Users/{id} | GET | Get user |
| /scim/v2/Users/{id} | PUT | Replace user |
| /scim/v2/Users/{id} | PATCH | Partial update (activate/deactivate) |
| /scim/v2/Users/{id} | DELETE | Deprovision (immediate access revocation) |
| /scim/v2/ServiceProviderConfig | GET | SCIM capability discovery |
| /scim/v2/Schemas | GET | Schema definitions |

## Security

- Bearer token per tenant (stored as bcrypt hash in `scim_tokens` table)
- Token rotation: admin can issue new token + revoke old via dashboard
- Rate limiting: 100 req/min per token (Kong plugin on mobile-api-gateway)
- Deprovisioning: DELETE immediately sets `users.is_active = false` + revokes all JWTs via Redis blocklist

## HIPAA Role Mapping

| SCIM Group | HealthGuard Role |
|-----------|-----------------|
| HG-Nurses | NURSE |
| HG-Physicians | PHYSICIAN |
| HG-Admins | ADMIN |
| HG-IT | IT_ADMIN |

## Consequences

✅ Okta/Azure AD/PingFederate compatible out of the box  
✅ Automatic deprovisioning eliminates ex-employee access risk  
✅ HIPAA access management requirement satisfied  
⚠️ Hospital IT must configure SCIM connector in their IdP (30min one-time setup)  
⚠️ Group-to-role mapping must be documented per hospital
