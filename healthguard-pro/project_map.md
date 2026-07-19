# Project Map — HealthGuard Pro

**Generated:** 2026-07-31 (Sprint 1 close)  
**Framework:** Loop Engineering v9.5  
**Rule:** BEFORE reading any source file, check if this map already answers the question.

---

## Repository Layout

```
healthguard-pro/
├── services/
│   ├── auth-service/           ← ACTIVE Sprint 1 (Go 1.22 + Gin)
│   │   ├── config/             ← Env var loading, validation (panic on bad config)
│   │   ├── handlers/           ← WebAuthn, SCIM, (future: patient)
│   │   ├── middleware/         ← JWT validation, RBAC, tenant isolation
│   │   ├── models/             ← Domain structs, webauthn.User impl
│   │   ├── store/              ← PostgreSQL queries (ALL tenant-scoped)
│   │   ├── main.go             ← Gin router, graceful shutdown
│   │   ├── Dockerfile          ← Multi-stage, distroless runtime
│   │   └── go.mod              ← module healthguard.io/auth-service
│   ├── patient-data-service/   ← Sprint 2 (Go)
│   ├── sepsis-scoring-service/ ← Sprint 2 (Python + FastAPI)
│   └── websocket-gateway/      ← Sprint 2 (Go)
├── infra/
│   └── terraform/
│       ├── modules/eks/        ← Reusable EKS module
│       ├── us-east-1/          ← HIPAA region (10.0.0.0/16)
│       └── eu-west-1/          ← GDPR region (10.1.0.0/16), NO peering
├── docs/
│   ├── schema/
│   │   ├── postgres.sql        ← ALL tables with tenant_id + HIPAA/GDPR annotations
│   │   └── clickhouse.sql      ← Analytics (sepsis_scores, vitals, api_usage)
│   ├── adr/                    ← ADR 001–005 (ClickHouse, WebAuthn, SAML-defer, multi-region, SCIM)
│   ├── graph/
│   │   └── graph-patch-sprint1.yaml  ← Fix 46A knowledge graph
│   ├── sprint-1/
│   │   ├── sprint-plan.md      ← SM-PLAN output, IAM budget, story table
│   │   ├── git-log.md          ← 28 commits, sprint 1 full history
│   │   ├── impl-decisions.md   ← 9 decisions D-001 through D-009
│   │   ├── sprint-discipline-card.md ← Framework compliance audit
│   │   └── stories/            ← AUTH-001/003/004, PAT-001, INFRA-001/002
│   ├── prd.md                  ← Product requirements (Fix 32A template)
│   └── trd.md                  ← Technical requirements + STRIDE + arch diagram
├── .github/workflows/ci.yml    ← Go tests (-race), semgrep, gitleaks, tf validate
├── docker-compose.yml          ← postgres:16, clickhouse:24, redis:7, auth-service
├── Makefile                    ← dev, test, lint, build-auth, tf-plan-us/eu
└── README.md                   ← Stack overview, services status, quick start
```

---

## Service Responsibilities

| Service | Sprint | Language | Owns | Port |
|---------|--------|----------|------|------|
| auth-service | 1 (ACTIVE) | Go 1.22 | WebAuthn, SCIM, JWT, RBAC | 8080 |
| patient-data-service | 2 | Go 1.22 | Patient CRUD, Vitals ingestion | 8081 |
| sepsis-scoring-service | 2 | Python 3.11 | ML inference, ClickHouse writes | 8082 |
| websocket-gateway | 2 | Go 1.22 | Real-time alerts, SSE | 8083 |
| mobile-bff | 3 | Go 1.22 | Mobile API aggregator | 8084 |

---

## Key Files — Where to Look First

| Question | File | Line hint |
|----------|------|-----------|
| How is tenant isolation enforced? | `services/auth-service/middleware/tenant.go` | `RequireJWT`, `AssertSameTenant` |
| What tables exist? | `docs/schema/postgres.sql` | Full schema with annotations |
| WebAuthn registration flow? | `services/auth-service/handlers/webauthn.go` | `BeginRegistration` |
| SCIM user provisioning? | `services/auth-service/handlers/scim.go` | `CreateUser`, `DeleteUser` |
| Cross-tenant test? | `services/auth-service/middleware/tenant_test.go` | `TestCrossTenantDenial` |
| Config/env vars required? | `services/auth-service/config/config.go` | `mustGetEnv` calls |
| PostgreSQL queries? | `services/auth-service/store/postgres.go` | All queries have `-- TENANT SCOPE` comment |
| GDPR/HIPAA arch decisions? | `docs/trd.md` | §HARD CONSTRAINTS, §STRIDE |
| Which ADR covers X? | `docs/adr/001–005` | See ADR index below |
| Sprint 1 stories? | `docs/sprint-1/stories/` | AUTH-001/003/004, PAT-001, INFRA-001/002 |

---

## ADR Index

| ADR | Decision | Status |
|-----|----------|--------|
| 001 | ClickHouse for analytics (rejected: TimescaleDB, Redshift, BigQuery) | Active |
| 002 | WebAuthn/FIDO2 passwordless (userVerification=required, residentKey=required) | Active |
| 003 | SAML 2.0 deferred to Sprint 2 (IAM budget 73%) | Deferred |
| 004 | Multi-region AWS, no VPC peering (GDPR hard constraint) | Active |
| 005 | SCIM 2.0, immediate deprovisioning, HIPAA role mapping | Active |

---

## Dependencies (Ponytail Ladder Status)

| Package | Version | Rung | Status |
|---------|---------|------|--------|
| github.com/go-webauthn/webauthn | v0.10.2 | 2 | ✅ Approved |
| github.com/gin-gonic/gin | latest | 2 | ✅ Approved |
| github.com/golang-jwt/jwt/v5 | latest | 2 | ✅ Approved |
| github.com/redis/go-redis/v9 | latest | 2 | ✅ Approved |
| github.com/lib/pq | latest | 2 | ✅ Approved |
| golang.org/x/crypto (bcrypt) | latest | 1 | ✅ Approved |
| SCIM library | — | 3 | ❌ Rejected → RFC 7644 direct |

---

## Compliance Map

| Constraint | How Enforced | Where |
|-----------|--------------|-------|
| HIPAA: All data tenant-scoped | `WHERE tenant_id = $N` + `AssertSameTenant()` | All store + middleware |
| HIPAA: Audit log 6yr retention | Partitioned table, append-only | `docs/schema/postgres.sql#audit_log` |
| HIPAA: No hard deletes | `deleted_at` soft delete on all tables | Schema + store layer |
| GDPR: EU data stays in eu-west-1 | No VPC peering, no replication | Terraform + ADR-004 |
| GDPR: PII erasure | `pgp_sym_encrypt`, `deleted_at` on patients | `docs/schema/postgres.sql#patients` |
| HIPAA: Strong auth | `userVerification=required` WebAuthn | ADR-002, handlers/webauthn.go |

---

## Open Items → Sprint 2

- AUTH-002: SAML 2.0 SSO (Okta) — ADR-003
- PAT-002: Vitals ingestion pipeline
- ML-001/002/003: Sepsis AI scoring
- RT-001: WebSocket gateway
- MOB-001/002/003: Mobile apps
- Fix 46A: knowledge graph D3 viz (graph-patch-sprint1.yaml ready, viz deferred)
- Per-tenant pgcrypto key rotation
