# Technical Requirements Document — HealthGuard Pro v1

**Status:** Sprint 1 baseline  
**Security Posture:** CRITICAL  
**Last updated:** 2026-07-17  

---

## 1. System Overview

HealthGuard Pro is a multi-tenant SaaS platform for hospital networks providing:
- Real-time AI-powered sepsis risk scoring
- HIPAA/GDPR-compliant patient data management
- Enterprise SSO + passwordless authentication
- Population health analytics

---

## 2. Architecture

**Pattern:** Event-driven microservices on Kubernetes (EKS)

```
                        ┌──────────────────────────────────┐
 Patients (mobile)  ──► │     mobile-api-gateway (Kong)    │
 Clinicians (web)   ──► │     clinician-web-dashboard      │
                        └──────────────┬───────────────────┘
                                       │
              ┌────────────────────────┼────────────────────────┐
              ▼                        ▼                        ▼
    ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
    │  auth-service    │   │ patient-data-svc │   │ alerting-service │
    │  (Go)            │   │ (Go)             │   │ (Go + WebSocket) │
    └──────────────────┘   └────────┬─────────┘   └──────────────────┘
              │                     │                        │
              ▼                     ▼                        ▼
    ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
    │  RDS PostgreSQL  │   │ sepsis-scoring   │   │ analytics-       │
    │  (per region)    │   │ (Python FastAPI) │   │ ingestion → CH   │
    └──────────────────┘   └──────────────────┘   └──────────────────┘
```

---

## 3. Services

| Service | Language | Port | Responsibility |
|---------|----------|------|----------------|
| auth-service | Go 1.22 | 8080 | WebAuthn, SCIM, SAML, JWT issuance |
| patient-data-service | Go 1.22 | 8080 | Patient CRUD, vitals ingestion, audit log |
| sepsis-scoring-service | Python 3.11 | 8000 | Feature pipeline, ONNX inference, score API |
| alerting-service | Go 1.22 | 8080 | WebSocket hub, alert rule engine |
| analytics-ingestion-service | Go 1.22 | 8080 | Kafka consumer → ClickHouse writer |
| billing-service | Go 1.22 | 8080 | Stripe metering, per-seat + per-API-call |
| mobile-api-gateway | Kong 3.x | 8000 | Rate limiting, auth, routing for mobile |
| clinician-dashboard | React 18 | 3000 | Web SPA for clinicians |
| patient-mobile | React Native 0.74 | — | iOS + Android patient app |

---

## 4. Constraints

### HARD (non-negotiable)
- EU patient data MUST NOT leave `eu-west-1` (GDPR Article 46)
- ALL patient data queries MUST include `WHERE tenant_id = $current_tenant_id`
- HIPAA BAA signed before any US hospital data is ingested
- WebAuthn user verification = `required` (not `preferred`)
- Cross-tenant isolation tests MANDATORY on every API endpoint that reads patient data

### SOFT (target, negotiable)
- Sepsis inference P99 latency < 500ms (can relax to 1s if model complexity requires)
- ClickHouse cluster: start small (3 nodes), scale as usage grows
- SAML 2.0: deferred to Sprint 2 (IAM budget constraint, see ADR-003)

---

## 5. Trust Boundary Map

```
PUBLIC ZONE
  └── mobile-api-gateway (Kong) — rate-limited, auth-validated
  └── clinician-dashboard (React) — served via CloudFront

INTERNAL ZONE (VPC-private, no public ingress)
  └── auth-service
  └── patient-data-service
  └── sepsis-scoring-service
  └── alerting-service
  └── analytics-ingestion-service
  └── billing-service

DATA ZONE (isolated per tenant_id)
  └── RDS PostgreSQL — row-level security + tenant_id on every table
  └── ClickHouse — tenant_id in PARTITION BY
  └── S3 — bucket policy per tenant prefix
```

---

## 6. Threat Model (STRIDE — CRITICAL depth)

| Threat | Component | Mitigation |
|--------|-----------|-----------|
| Spoofing | auth-service | WebAuthn + MFA required for clinicians |
| Tampering | patient-data-service | Signed append-only audit log |
| Repudiation | All services | Immutable CloudTrail + RDS audit log |
| Info Disclosure | patient-data-service | tenant_id row-level security in Postgres |
| Denial of Service | mobile-api-gateway | Rate limiting per tenant_id (Kong plugin) |
| Elevation of Privilege | auth-service | RBAC: NURSE / ADMIN / PHYSICIAN — no cross-role escalation |
| **Cross-tenant leak** | patient-data-service | ALL queries: `WHERE tenant_id = :current_tenant` — GATE S2 blocks merge without cross-tenant denial test |

---

## 7. Data Model (summary)

Full schema: [schema/postgres.sql](schema/postgres.sql)

Core entities:
- `tenants` — hospital networks (isolation root)
- `users` — clinicians + patients, scoped to tenant
- `webauthn_credentials` — FIDO2 resident keys per user
- `patients` — PII encrypted at rest, GDPR-annotated
- `vitals` — time-series, denormalized tenant_id for partition isolation
- `audit_log` — HIPAA append-only log
- `scim_tokens` — per-tenant SCIM bearer tokens

---

## 8. Authentication Flow

```
Clinician registration:
  1. POST /v1/auth/register/begin → server issues challenge
  2. Authenticator signs challenge with private key
  3. POST /v1/auth/register/complete → server verifies attestation, stores credential
  4. Server issues JWT (15m access + 7d refresh)

Clinician authentication:
  1. POST /v1/auth/login/begin → server issues challenge
  2. Authenticator signs with stored credential
  3. POST /v1/auth/login/complete → server verifies assertion → JWT issued

SCIM provisioning (hospital IT):
  1. Hospital IT generates SCIM token (admin UI)
  2. Okta/Azure AD calls POST /scim/v2/Users to create clinicians
  3. Deprovisioning: DELETE /scim/v2/Users/{id} → immediate access revocation
```

---

## 9. Multi-Region Strategy

| Region | Handles | Data |
|--------|---------|------|
| us-east-1 | US hospital networks | US patient data (HIPAA) |
| eu-west-1 | EU hospital networks | EU patient data (GDPR — stays here) |

- **No VPC peering between regions** (data residency hard boundary)
- Route 53 geolocation routing: EU → eu-west-1, all others → us-east-1
- Each region has its own: EKS cluster, RDS Multi-AZ, ClickHouse cluster
- `patients.region` field tracks which region stores the record

---

## 10. Compliance Checklist

| Requirement | Status | Owner |
|------------|--------|-------|
| HIPAA BAA template | ✅ Ready | Legal |
| GDPR DPA template | ✅ Ready | Legal |
| Data retention policy | ✅ US: 7yr, EU: 10yr | Eng + Legal |
| Right to erasure | 🔜 Sprint 3 | Backend Lead |
| SOC 2 Type II | 🔜 Q3 2026 | Security |
| Pen test | 🔜 Pre-GA | Security |
