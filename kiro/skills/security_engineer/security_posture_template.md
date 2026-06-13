<!-- LOAD-TYPE: CHECKLIST -->
---
id: security_posture_template
version: 1.0.0
owners: [security_engineer, architect, cto]
tags: [foundation, security, compliance, auth, posture]
when_to_use: >
  When creating /docs/foundation/security-posture.md. Mandatory GATE 2 artifact.
  security_engineer owns creation. architect reviews Sections 3, 5, 6. cto approves Section 1.
  skill-label-index.md be/auth reads Section 2 to resolve auth CHECKLIST selection.
  SM-PLAN reads Section 3 for compliance auto-labeling rules.
  GATE 2 stays RED until all 8 sections are present and non-empty.
---

# Security Posture Template — Project Security Foundation

FULL-LOAD REQUIRED — this drives auth CHECKLIST selection, compliance auto-labels, STRIDE depth, and VERIFIER security checks system-wide.
Output file: `/docs/foundation/security-posture.md`
Owner: `security_engineer` (drafts) + `architect` (reviews Sections 3,5,6) + `cto` (approves Section 1)

**CONFLICT RULE: security-posture.md wins over TRD on all security-specific decisions.**
If TRD says "JWT HS256" but this doc says "HS256 banned" → this doc is the contract. Log conflict to project-index.md.

---

## SECURITY POSTURE CHECKLIST

Before marking security-posture.md complete, verify ALL sections present and non-empty:

- [ ] Section 1: Security Posture Level declared
- [ ] Section 2: Auth Mechanism Declaration (resolves be/auth CHECKLIST ambiguity)
- [ ] Section 3: Compliance Requirements (drives auto-labeling in SM-PLAN)
- [ ] Section 4: Data Classification Schema
- [ ] Section 5: Encryption Standards
- [ ] Section 6: Secrets Management Standard
- [ ] Section 7: Security Testing Requirements
- [ ] Section 8: API Security Standards

---

## SECTION 1 — Security Posture Level

Declare ONE level. This changes agent behavior system-wide.

```
POSTURE_LEVEL: LOW | MEDIUM | HIGH

LOW   → Startup MVP, no regulated data, speed over controls.
        STRIDE: threat-identification only, mitigations as TECH-DEBT stories.
        security_engineer: review [security-critical] stories only.
        Pen test: not required for v1.

MEDIUM → B2B SaaS, business data, SOC2 target, no regulated health/payment data.
         STRIDE: full depth on all trust boundaries (Fix 26D).
         security_engineer: DEVELOP pass on all [security-critical] stories.
         Pen test: before launch or at 6-month mark.

HIGH   → Regulated: HIPAA / PCI-DSS / ISO27001 / FedRAMP / financial services.
         STRIDE: mandatory on ALL trust boundaries, not just major ones.
         security_engineer: reviews ALL be/* stories, not just security-critical.
         Pen test: before launch AND annually.
         SAST: required in CI on every PR.
```

Log: `[POSTURE-LEVEL: HIGH | STRIDE-depth: all boundaries | sec-eng coverage: all be/* stories]`

---

## SECTION 2 — Auth Mechanism Declaration

**This section resolves be/auth CHECKLIST ambiguity in skill-label-index.md.**
When a story has label [be/auth], load ONLY the CHECKLISTs matching PRIMARY_AUTH and MFA_REQUIRED.
Do NOT load both saml_security.md and webauthn_fido2.md unless both are declared here.

```
PRIMARY_AUTH:   OAuth 2.0 (Google/GitHub/Microsoft)
                | SAML 2.0 (enterprise SSO)
                | WebAuthn / FIDO2 Passkeys
                | Email + Password (bcrypt)
                | API Key (machine-to-machine)
                | Custom JWT

MFA_REQUIRED:   none | TOTP (Google Authenticator / Authy) | WebAuthn / Passkeys | SMS (discouraged)

SSO_PROTOCOL:   none | SAML 2.0 | OIDC (OpenID Connect)

MACHINE_AUTH:   none | API Key | mTLS | Service account JWT

SESSION_TYPE:   JWT (stateless) | Session cookie (stateful) | Hybrid
SESSION_TTL:    access=15min | refresh=7days (or specify)
```

**CHECKLIST load rules for be/auth stories (overrides skill-label-index.md note):**
```
PRIMARY_AUTH = SAML 2.0 → load saml_security.md (CHECKLIST)
PRIMARY_AUTH = WebAuthn → load webauthn_fido2.md (CHECKLIST)
PRIMARY_AUTH = OAuth 2.0 → load auth_design.md (NARRATIVE)
MFA_REQUIRED = WebAuthn → ALSO load webauthn_fido2.md
SSO_PROTOCOL = SAML 2.0 → ALSO load saml_security.md
SSO_PROTOCOL = OIDC → Note: oidc_protocol.md pending (Fix 30 known gap — load auth_design.md instead)
```

Log: `[AUTH-POSTURE: primary=WebAuthn | mfa=WebAuthn | sso=SAML | machine=API-Key → CHECKLISTs: webauthn_fido2.md + saml_security.md]`

---

## SECTION 3 — Compliance Requirements

**SM-PLAN reads this section for compliance auto-labeling rules.**
Declare which frameworks apply. Each has auto-label consequences.

```
GDPR:    yes | no
         Scope: EU users only | all users regardless of location
         Auto-label: ALL stories touching user data → [be/pii] if not already labeled

HIPAA:   yes | no
         Data type: PHI (Protected Health Information)
         Auto-label: ALL [data/*] stories → [security-critical] added automatically
         Auto-label: ALL [be/api] stories touching health data → [security-critical]
         Additional: test data MUST be synthetic — no production PHI in non-prod environments

PCI-DSS: yes | no
         Level: 1 | 2 | 3 | 4
         Auto-label: ALL stories touching payment data → [security-critical]
         Rule: card numbers NEVER stored — tokenize via Stripe/Adyen/Braintree only
         Auto-story: TECH-DEBT story if any payment data stored raw

SOC2:    yes | no
         Type: I | II | both
         Target date: YYYY-MM
         Auto-label: ALL [devops/*] stories → load operations/compliance-tracking skill

ISO27001: yes | no
FEDRAMP:  yes | no | in-progress

NONE:    [explicitly state "no regulatory requirements" — do not leave blank]
```

Log: `[COMPLIANCE: GDPR=yes(all-users) | HIPAA=no | SOC2=yes(Type-II,target:2026-12) | auto-labels: be/pii on all user-data stories]`

---

## SECTION 4 — Data Classification Schema

**database_architect reads this schema when classifying columns (feeds Fix 32E).**
One definition used everywhere — no per-table reinvention.

```
PII:HIGH     → Real name, email, phone number, SSN, DOB, biometric, government ID
               Controls: encrypted at rest (AES-256), excluded from all logs, masked in non-prod
               Retention: per GDPR/CCPA — deletion must be executable (not just flagged)

PII:MEDIUM   → Username, IP address, device fingerprint, location (city-level)
               Controls: pseudonymised, masked in non-prod, not in error logs

PII:NONE     → Timestamps, feature flags, aggregated analytics, system events
               Controls: standard access controls

PHI          → (HIPAA only) Diagnosis codes, medication, treatment records, lab results
               Controls: full PHI controls — encryption + audit log + BAA required with vendors

PCI          → (PCI-DSS only) Card number, CVV, expiry date, track data
               Controls: NEVER stored — tokenize immediately via payment processor
               Failure mode: automatic TECH-DEBT story created if PCI data detected in schema

INTERNAL     → Business data, configuration, non-personal metrics
               Controls: role-based access, standard encryption in transit
```

---

## SECTION 5 — Encryption Standards

```
AT_REST:
  Algorithm: AES-256-GCM (preferred) | ChaCha20-Poly1305
  Key management: AWS KMS | HashiCorp Vault | GCP KMS
  BANNED: application-level encryption with hardcoded keys | no encryption for PII:HIGH

IN_TRANSIT:
  Minimum: TLS 1.3 (TLS 1.2 only with approved cipher suites: ECDHE + AES-256-GCM)
  BANNED: TLS 1.0 | TLS 1.1 | SSLv3 | self-signed certs in production

PASSWORD_HASHING:
  Algorithm: bcrypt (cost ≥ 12) | argon2id (recommended) | scrypt
  BANNED: MD5 | SHA-1 | SHA-256 (unsalted) | bcrypt cost < 10

TOKEN_SIGNING:
  Algorithm: RS256 (RSA) | ES256 (ECDSA P-256)
  BANNED: HS256 for multi-service architectures (shared secret = single point of compromise)
  Key rotation: automatic (90-day) | manual with documented procedure

DATABASE_COLUMN_ENCRYPTION:
  Applies to: all PII:HIGH columns
  Method: application-level (before insert) | transparent encryption (pgcrypto / TDE)
```

---

## SECTION 6 — Secrets Management Standard

```
SECRET_STORE:  AWS Secrets Manager | HashiCorp Vault | GCP Secret Manager | Azure Key Vault
               BANNED: .env files committed to repo | hardcoded credentials | process.env raw in prod

ROTATION:
  API keys: automatic (30-day) | manual (quarterly) | none (flag as TECH-DEBT story)
  DB credentials: automatic (Vault dynamic secrets) | quarterly rotation
  JWT signing keys: automatic (90-day)

CI/CD SECRETS:
  Store in: GitHub Actions Secrets | AWS Parameter Store | Vault
  NEVER: commit to repo | log in CI output | pass as plain CLI args

AUTO-STORY RULE:
  If SECRET_STORE = none OR .env in prod detected:
  → SM-PLAN automatically creates TECH-DEBT story: "Migrate secrets to [declared store]"
  → Labels: [security-critical, tech-debt] | Priority: HIGH | BLOCKS Sprint 1 auth stories
```

---

## SECTION 7 — Security Testing Requirements

**Cross-references testing-strategy.md Section 8 (which owns CI tooling config).**
This section owns: schedule, scope, and compliance obligations.

```
SAST:
  Tool: semgrep | bandit (Python) | eslint-plugin-security | gosec (Go)
  Frequency: every PR (blocking) — required for MEDIUM and HIGH posture
  Ruleset: semgrep registry (p/owasp-top-ten + p/secrets)
  Failure: SAST findings of severity HIGH or CRITICAL block merge

DEPENDENCY_SCANNING:
  Tool: npm audit | snyk | dependabot | OWASP dependency-check
  Frequency: nightly (auto-PR for patches) | per PR (audit-level=high)
  Failure: HIGH severity CVE in direct dependency → blocks PR

SECRET_SCANNING:
  Tool: gitleaks | trufflehog | GitHub Advanced Security
  Trigger: pre-commit hook + CI check
  On detection: block commit, rotate detected credential immediately

DAST:
  Tool: OWASP ZAP | Burp Suite | none
  Frequency: quarterly | at launch only | none
  Scope: all authenticated endpoints + public API surface

PEN_TEST:
  Frequency: before launch | annually | none
  Scope: full application | API only | specify
  Provider: internal | external (named firm)

SECURITY_REGRESSION:
  After any security incident or pen test finding:
  → Write automated test that replays the attack vector
  → Add to [security-critical] VERIFIER suite permanently
```

---

## SECTION 8 — API Security Standards

**loop-engine.md adds these as mandatory be/api story criteria when this section is present.**

```
RATE_LIMITING:
  Per-IP: 100 requests/min (unauthenticated) | 1000 requests/min (authenticated)
  Per-user: 1000 requests/min | configurable per tier
  Response: 429 Too Many Requests + Retry-After header
  Storage: Redis sliding window

INPUT_VALIDATION:
  Strategy: strict schema validation on ALL endpoints (accept only known fields)
  Library: ajv (JSON Schema) | zod | pydantic | joi
  Rejection: 400 Bad Request + field-level error detail (no stack traces)
  BANNED: trusting client-provided types | string interpolation into SQL/shell

OUTPUT_ENCODING:
  HTML: encode all user-controlled output (no raw innerHTML)
  JSON: no JSONP | no XSS via JSON content-type sniffing
  Files: Content-Disposition: attachment for all user-uploaded file downloads

CORS_POLICY:
  Production: explicit allowlist only (no wildcard *)
  Dev/staging: localhost allowlist only
  BANNED: Access-Control-Allow-Origin: * in production

SECURITY_HEADERS:
  Content-Security-Policy: required (no unsafe-inline without hash/nonce)
  X-Frame-Options: DENY | SAMEORIGIN
  X-Content-Type-Options: nosniff
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  Referrer-Policy: strict-origin-when-cross-origin

AUTHENTICATION_HEADERS:
  API Key: X-API-Key header (not query param)
  JWT: Authorization: Bearer [token] (not cookie for API-first)
  BANNED: token in URL query string | token in logs
```

---

## VALIDATION LOG

When security-posture.md is complete, emit:
```
[SECURITY-POSTURE: level=<LOW|MEDIUM|HIGH> | auth=<mechanisms> | compliance=<frameworks> | checklist-load=<which auth CHECKLISTs> | GATE 2: ✅]
```
