# ADR-002: WebAuthn/FIDO2 Passwordless Authentication for Clinicians

**Date:** 2026-07-17  
**Status:** Accepted  
**Deciders:** CTO, Security Engineer  

## Context

Clinicians access HealthGuard Pro from hospital workstations, personal laptops, and mobile devices. Passwords are a known phishing vector and HIPAA guidance (§164.312(d)) requires robust authentication controls. Hospital IT teams want SSO integration but also need offline/failover auth.

## Decision

Implement WebAuthn/FIDO2 as the primary authentication mechanism for clinicians. Passwords are eliminated entirely (no password column in `users` table).

## Configuration

```
Relying Party ID:          healthguard.io (pinned to origin)
User Verification:         required  (not "preferred" — HIPAA compliance)
Resident Keys:             required  (enables usernameless login)
Attestation:               direct (enterprise), none (consumer)
Replay prevention:         challenge nonce cache in Redis (5min TTL)
Supported transports:      internal, hybrid, usb, nfc, ble
```

## Consequences

✅ Eliminates phishing vector entirely  
✅ Satisfies HIPAA §164.312(d) strong authentication  
✅ Hardware keys supported (Yubikey, Titan) for high-security roles  
✅ Biometric unlock on mobile (Face ID, fingerprint) for convenience  
⚠️ Requires user enrollment ceremony (one-time setup)  
⚠️ Recovery flow needed when authenticator is lost (admin-assisted re-enrollment)  

## Implementation

Library: `github.com/go-webauthn/webauthn` (Rung 2, MIT, 1.2M weekly downloads)  
Service: `auth-service` (Go)  
Endpoints: `POST /v1/auth/register/begin`, `POST /v1/auth/register/complete`, `POST /v1/auth/login/begin`, `POST /v1/auth/login/complete`
