# HealthGuard Pro

Multi-tenant HealthTech SaaS for hospital networks.

## Stack
- **Backend services**: Go 1.22
- **ML/Inference**: Python 3.11 + FastAPI
- **Frontend**: React 18 + TypeScript
- **Mobile**: React Native 0.74
- **Database**: PostgreSQL 16 (OLTP) + ClickHouse 24 (analytics)
- **Infrastructure**: AWS EKS (us-east-1 + eu-west-1), Terraform 1.8
- **Auth**: WebAuthn/FIDO2 + SAML 2.0 + SCIM 2.0

## Compliance
- HIPAA BAA required before data ingestion
- GDPR: EU patient data stays in eu-west-1 (hard boundary)
- SOC 2 Type II (planned Q3)

## Services

| Service | Language | Status |
|---------|----------|--------|
| auth-service | Go | ✅ Sprint 1 |
| patient-data-service | Go | 🔜 Sprint 2 |
| sepsis-scoring-service | Python | 🔜 Sprint 2 |
| alerting-service | Go | 🔜 Sprint 2 |
| analytics-ingestion-service | Go | 🔜 Sprint 2 |
| billing-service | Go | 🔜 Sprint 3 |
| mobile-api-gateway | Kong | 🔜 Sprint 2 |
| clinician-dashboard | React | 🔜 Sprint 2 |
| patient-mobile | React Native | 🔜 Sprint 2 |

## Quick Start

```bash
# Start local dev stack
make dev

# Run auth service tests
make test-auth

# Run all tests
make test
```

## Architecture

See [docs/trd.md](docs/trd.md) for the full Technical Requirements Document.

ADRs:
- [ADR-001](docs/adr/001-clickhouse-analytics.md) — ClickHouse for analytics
- [ADR-002](docs/adr/002-webauthn-passwordless.md) — WebAuthn/FIDO2 passwordless
- [ADR-003](docs/adr/003-saml-deferred.md) — SAML deferred to Sprint 2
- [ADR-004](docs/adr/004-multi-region.md) — Multi-region AWS deployment
- [ADR-005](docs/adr/005-scim-provisioning.md) — SCIM 2.0 provisioning

## Security

Security posture: **CRITICAL**
- STRIDE threat model: [docs/trd.md#threat-model](docs/trd.md#threat-model)
- Cross-tenant isolation: ALL queries include `WHERE tenant_id = $current_tenant`
- HIPAA audit log: append-only, 6-year retention
- WebAuthn: user verification = `required`, resident keys enabled
