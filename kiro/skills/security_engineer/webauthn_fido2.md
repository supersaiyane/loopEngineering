<!-- LOAD-TYPE: CHECKLIST -->
---
id: webauthn_fido2
version: 1.0.0
owners: [security_engineer, architect]
tags: [security, auth, webauthn, fido2, passkeys, mfa]
when_to_use: >
  Any story implementing WebAuthn registration or authentication, FIDO2 passkeys,
  platform authenticators (FaceID/TouchID), security keys (YubiKey), or any
  be/auth story where WebAuthn/FIDO2 is the credential mechanism.
---

# WebAuthn / FIDO2 Security Checklist

FULL-LOAD REQUIRED — compress-to-5-lines destroys security coverage.

---

## A1 — Relying Party (RP) Origin Validation

The RP ID and origin binding is the core security primitive in WebAuthn. Misconfiguration enables cross-origin credential use.

**Checklist:**
- [ ] `rpId` set to the effective domain (e.g., `example.com` not `auth.example.com`) — must match the origin the credential was registered on
- [ ] `rpId` validated server-side against the origin in the client data JSON — not accepted from client payload
- [ ] Cross-origin iframes cannot trigger WebAuthn without explicit `allow="publickey-credentials-get"` policy
- [ ] Test: attempt authentication from a different origin → must fail with `SecurityError`
- [ ] Log: `[WEBAUTHN-RP: rpId=<domain> | origin=<validated> | cross-origin: blocked]`

---

## A2 — Attestation Verification

Attestation proves the authenticator is genuine. Skipping verification accepts potentially spoofed or cloned credentials.

**Checklist:**
- [ ] Attestation format validated: `none`, `packed`, `tpm`, `android-key`, `fido-u2f`, `apple` — handle all
- [ ] For `packed` and `fido-u2f`: certificate chain validated against FIDO MDS3 metadata
- [ ] Attestation verification is configurable (none/indirect/direct) — default to `indirect` for consumer, `direct` for high-assurance
- [ ] `aaguid` extracted and logged for authenticator type tracking
- [ ] Test: send crafted attestation with invalid certificate → rejected

---

## A3 — Authenticator Data Flags

The `authenticatorData` byte array contains critical flags. Not checking them = skipping security assertions.

**Checklist:**
- [ ] `UP` flag (user presence) MUST be set — reject if not
- [ ] `UV` flag (user verification) checked if `userVerification=required` was specified
- [ ] `BE` flag (backup eligible) and `BS` flag (backed up) logged — affects risk assessment for passkeys
- [ ] `signCount` compared on every authentication — see A4
- [ ] Test: send response with `UP=0` → must reject

---

## A4 — Clone Detection via Signature Counter

FIDO2 authenticators maintain a signature counter that increments on each use. A replayed or cloned credential counter will not increment correctly.

**Checklist:**
- [ ] `signCount` stored per credential on registration (initial value 0)
- [ ] On authentication: received `signCount` MUST be > stored `signCount` (or both = 0 for software authenticators)
- [ ] If `signCount` ≤ stored value (and stored > 0): log `[WEBAUTHN-CLONE: credId=<id> | expected=>N | got=M]` and treat as possible clone
- [ ] Clone detection policy: configurable — warn (default) or hard reject
- [ ] Test: replay same authentication response twice → second use triggers clone detection

---

## A5 — Challenge Freshness and Single-Use

WebAuthn uses server-generated challenges to prevent replay attacks. Stale or reused challenges = replay vulnerability.

**Checklist:**
- [ ] Server generates cryptographically random challenge per ceremony (registration or authentication)
- [ ] Challenge stored server-side (not in client) with TTL (recommend ≤ 5 minutes)
- [ ] Challenge single-use — consumed on verification, cannot be reused
- [ ] `clientDataJSON.challenge` compared to stored challenge (base64url decoded)
- [ ] Test: replay same authentication response → challenge already consumed → rejected

---

## A6 — Credential Storage and Binding

**Checklist:**
- [ ] Credential ID stored per user — not globally unique across users (same authenticator can register with multiple services)
- [ ] Public key stored (not private key — never leaves authenticator)
- [ ] Credential bound to specific user — `userHandle` validated on authentication
- [ ] Multiple credentials per user supported (multiple devices/passkeys)
- [ ] Credential deregistration supported — removing a credential invalidates future assertions from it

---

## A7 — Resident Keys / Discoverable Credentials (Passkeys)

**Checklist:**
- [ ] If passkeys enabled: `residentKey=required` set in registration options
- [ ] `userHandle` (user ID) must NOT be a PII identifier (not email/username) — use opaque random ID
- [ ] `userHandle` max 64 bytes
- [ ] Server accepts discoverable credential flow — no username input required before authentication
- [ ] `allowCredentials` list empty for passkey flow (discoverable) — authenticator selects credential

---

## A8 — User Verification Requirements

**Checklist:**
- [ ] `userVerification` setting matches security level: `required` for high-assurance (banking, admin); `preferred` for consumer
- [ ] If `UV=required` and authenticator returns `UV=0`: authentication rejected
- [ ] Fallback when authenticator doesn't support UV: configurable (reject vs degrade to presence-only)
- [ ] Document UV policy in ADR — affects which authenticators are accepted

---

## VERIFIER COMMANDS

```bash
# RP origin validation test
npm run test:webauthn:origin

# Clone detection (replay signCount)
npm run test:webauthn:clone

# Challenge single-use
npm run test:webauthn:challenge-replay

# Attestation verification
npm run test:webauthn:attestation

# Flags validation (UP/UV)
npm run test:webauthn:flags
```

---

## CRITERIA TEMPLATES (for loop spec)

```
WEBAUTHN-RP: rpId validated server-side against clientDataJSON origin (score 1-10)
WEBAUTHN-CLONE: signCount checked on every auth, clone detection fires on replay (score 1-10)
WEBAUTHN-CHALLENGE: challenge single-use, TTL ≤ 5min, replay rejected (score 1-10)
WEBAUTHN-FLAGS: UP flag required, UV flag enforced when userVerification=required (score 1-10)
WEBAUTHN-PASSKEY: userHandle is opaque random ID (not PII), resident key stored correctly (score 1-10)
```

Use max 2 WebAuthn criteria per story (STRIDE-BRIDGE rule). Pick the two highest-risk for the story's scope.
