# Sprint 1 Git Log — HealthGuard Pro

**Branch:** `feature/sprint-1-auth-infra` → merged to `main`  
**Sprint:** 2026-07-17 → 2026-07-31  
**Convention:** [Conventional Commits](https://www.conventionalcommits.org/) + story ID in footer

---

## Commit History (reverse chronological)

```
commit a9f3c82  (HEAD → main, origin/main)
Merge: 8d4e1f2 7c2b390
Author: BACKEND_LEAD <eng@healthguard.internal>
Date:   2026-07-31 17:00:00 +0000

    chore: merge sprint-1-auth-infra → main [GATE 5 PASS]
    
    All stories: AUTH-001 AUTH-003 AUTH-004 PAT-001 INFRA-001 INFRA-002
    Coverage: auth-service 78% | GATE S2: 6/6 stories passed
    
    BREAKING CHANGE: none
    Reviewed-by: ARCHITECT, SECURITY_ENGINEER

──────────────────────────────────────────────────────────────

commit 7c2b390
Author: DEVOPS_ENGINEER <devops@healthguard.internal>
Date:   2026-07-30 14:22:00 +0000

    ci: add final all-checks-pass gate job

    Blocks merge to main if auth-service, terraform-validate,
    or security-scan fails. Conditionally skips patient-data-service
    and sepsis-scoring-service if not yet present.
    
    Story-ID: INFRA-002

commit 6e8d1c4
Author: DEVOPS_ENGINEER <devops@healthguard.internal>
Date:   2026-07-30 11:45:00 +0000

    ci: add semgrep SAST + gitleaks secrets scan

    Rules: p/golang, p/owasp-top-ten, p/cwe-top-25
    SEMGREP_APP_TOKEN via GitHub Actions secrets (not hardcoded)
    0 findings on current codebase.
    
    Story-ID: INFRA-002

commit 5d7a9f1
Author: DEVOPS_ENGINEER <devops@healthguard.internal>
Date:   2026-07-29 16:30:00 +0000

    ci: add go test -race + coverage gate (≥70%) for auth-service

    Services: postgres:16-alpine + redis:7-alpine
    Schema applied from docs/schema/postgres.sql before tests run.
    go vet passes. Coverage: 78%
    
    Story-ID: INFRA-002

commit 4b2e8d3
Author: DEVOPS_ENGINEER <devops@healthguard.internal>
Date:   2026-07-29 10:00:00 +0000

    feat(infra): add GitHub Actions CI workflow skeleton

    Workflow: push/PR to main + feature/**
    Jobs: auth-service, patient-data-service (conditional), 
          sepsis-scoring (conditional), terraform-validate, security
    Go: 1.22 pinned. Terraform: 1.8.x pinned.
    
    Story-ID: INFRA-002

commit 3a1f7c8
Author: DEVOPS_ENGINEER <devops@healthguard.internal>
Date:   2026-07-28 15:00:00 +0000

    feat(infra): eu-west-1 Terraform stack (GDPR)

    VPC 10.1.0.0/16, EKS 1.30, RDS Multi-AZ (db.t3.medium)
    State in S3 healthguard-tfstate-eu-west-1 (same region — data residency)
    HARD CONSTRAINT: no aws_s3_bucket_replication_configuration
    HARD CONSTRAINT: no VPC peering to us-east-1
    Tags: Compliance=GDPR
    
    Story-ID: INFRA-001

commit 2d9c0e5
Author: DEVOPS_ENGINEER <devops@healthguard.internal>
Date:   2026-07-28 11:30:00 +0000

    feat(infra): us-east-1 Terraform stack (HIPAA)

    VPC 10.0.0.0/16, EKS 1.30 (endpoint_public_access=false),
    KMS CMK for secrets, RDS Multi-AZ + CloudWatch + Performance Insights
    State in S3 healthguard-tfstate-us-east-1
    Tags: Compliance=HIPAA
    
    Story-ID: INFRA-001

commit 1e8b5d2
Author: DEVOPS_ENGINEER <devops@healthguard.internal>
Date:   2026-07-28 09:00:00 +0000

    feat(infra): reusable EKS Terraform module

    aws_eks_cluster: endpoint_public_access=false, KMS enc, CW logs
    aws_eks_node_group: t3.large, min2/desired3/max10
    Module inputs: cluster_name, vpc_id, subnet_ids, tags
    
    Story-ID: INFRA-001

commit 9f4a2b1
Author: BACKEND_LEAD <eng@healthguard.internal>
Date:   2026-07-25 17:45:00 +0000

    test(auth): add RequireRole tests for all 4 roles × protected routes

    TestRequireRole_AllowedRole, TestRequireRole_ForbiddenRole
    TestNurseOnAdminEndpoint → 403
    TestITAdminOnPatientEndpoint → 403
    Property-based: all 4 roles × all protected routes
    Coverage +4% → 82%
    
    Story-ID: AUTH-004

commit 8c3d7f9
Author: BACKEND_LEAD <eng@healthguard.internal>
Date:   2026-07-25 14:00:00 +0000

    feat(auth): RBAC RequireRole middleware + safe context extractors

    RequireRole(roles ...Role) — 403 if JWT role not in allowed set
    TenantID/UserID/Role extractors — panic (5xx) if JWT middleware skipped
    AssertSameTenant — IDOR prevention, 403 on mismatch
    Role embedded in JWT at login (zero DB calls per request)
    
    Co-Reviewed-by: SECURITY_ENGINEER
    Story-ID: AUTH-004

commit 7a1e9c3
Author: BACKEND_LEAD <eng@healthguard.internal>
Date:   2026-07-24 16:00:00 +0000

    test(patient): cross-tenant E2E denial test for patient CRUD

    GET /v1/patients/:id with Hospital B patient ID + Hospital A JWT → 403
    Covers AssertSameTenant path in all CRUD handlers
    e2e-required label: full E2E suite run (not unit only)
    Coverage: 74%
    
    Story-ID: PAT-001

commit 6b2d8e4
Author: BACKEND_LEAD <eng@healthguard.internal>
Date:   2026-07-24 10:30:00 +0000

    feat(patient): Patient CRUD API with tenant isolation + PII encryption

    POST/GET/PUT/DELETE /v1/patients
    tenant_id injected from JWT (never request body)
    PII fields encrypted with pgp_sym_encrypt (pgcrypto)
    MRN index: (tenant_id, mrn) — no MRN-only index
    audit_log write on all accesses
    Soft delete only (HIPAA — no hard delete)
    
    Story-ID: PAT-001

commit 5e7c1a8
Author: BACKEND_LEAD <eng@healthguard.internal>
Date:   2026-07-22 16:30:00 +0000

    test(scim): SCIM provisioning handler tests + cross-tenant denial

    ListUsers with Tenant A token → only Tenant A users returned
    SCIM token for Tenant A on /scim/v2/Users (Tenant B root) → 403
    DeleteUser E2E: SCIM DELETE → is_active=false within 1s
    Coverage: 71%
    
    Story-ID: AUTH-003

commit 4d9f0b7
Author: BACKEND_LEAD <eng@healthguard.internal>
Date:   2026-07-22 11:00:00 +0000

    feat(auth): SCIM 2.0 provisioning API (RFC 7644)

    GET ServiceProviderConfig, List/Get/Create/Replace/Patch/Delete Users
    SCIM group → HealthGuard role mapping (HG-Nurses→NURSE etc.)
    Bearer tokens stored as bcrypt hash (bcrypt.DefaultCost)
    Immediate deprovisioning: is_active=false on DELETE
    audit_log on every SCIM operation
    All operations scoped to token's tenant_id
    
    Story-ID: AUTH-003

commit 3c8a5f2
Author: BACKEND_LEAD <eng@healthguard.internal>
Date:   2026-07-21 15:00:00 +0000

    test(auth): WebAuthn handler tests + mandatory cross-tenant denial

    TestCrossTenantDenial: TenantA token → TenantB resource → 403
    TestSameTenantAllowed: happy path
    TestBeginRegistration_ExcludesExistingCredentials
    TestCompleteLogin_UpdatesSignCount (replay prevention)
    Fuzz: 1000 attestation objects (security-critical label)
    Coverage: 78%
    
    Fix-43C: cross-tenant test present ✅
    Story-ID: AUTH-001

commit 2b7e4d1
Author: BACKEND_LEAD <eng@healthguard.internal>
Date:   2026-07-21 10:00:00 +0000

    feat(auth): WebAuthn challenge cache (Redis + in-memory test double)

    RedisCache: go-redis/v9, TTL 5min, deleted on use (no replay)
    InMemoryCache: test double, no Redis dep in unit tests
    Key scheme: webauthn:reg:{tenantID}:{userID}
    
    Story-ID: AUTH-001

commit 1a9d3c6
Author: BACKEND_LEAD <eng@healthguard.internal>
Date:   2026-07-20 16:45:00 +0000

    feat(auth): WebAuthn registration + authentication handlers

    BeginRegistration: excludes existing credentials, residentKey=required,
      userVerification=required (HIPAA), challenge stored in Redis
    CompleteRegistration: verifies attestation, persists credential (tenant-scoped)
    BeginLogin: loads credentials by tenantID+userID, issues challenge
    CompleteLogin: verifies assertion, updates sign_count, issues JWT
    All events written to audit_log
    
    Dep: github.com/go-webauthn/webauthn v0.10.2 (Rung 2 ✅)
    Story-ID: AUTH-001

commit 0f2c8b9
Author: BACKEND_LEAD <eng@healthguard.internal>
Date:   2026-07-20 09:00:00 +0000

    feat(auth): PostgreSQL store layer (all queries tenant-scoped)

    GetUserByID/Email, CreateUser, UpdateUser, SoftDeleteUser, ListUsers
    GetCredentialsByUserID, SaveCredential, UpdateCredentialSignCount
    GetSCIMTokenByHash, TouchSCIMToken
    WriteAuditLog (append-only — no UPDATE/DELETE)
    ALL queries: WHERE ... AND tenant_id = $N
    
    Story-ID: AUTH-001

commit f1e7a3d
Author: BACKEND_LEAD <eng@healthguard.internal>
Date:   2026-07-19 15:30:00 +0000

    feat(auth): User model implements webauthn.User interface

    WebAuthnID/Name/DisplayName/Credentials methods
    Role type: NURSE/PHYSICIAN/ADMIN/IT_ADMIN
    JWTClaims: uid, tid, role, jti (Redis blocklist key)
    WebAuthnCredential.ToWebAuthnCredential() converter
    
    Story-ID: AUTH-001

commit e9b2d4f
Author: BACKEND_LEAD <eng@healthguard.internal>
Date:   2026-07-19 11:00:00 +0000

    feat(auth): config loader with validation

    All config from env vars (12-factor)
    JWT_SECRET: must be ≥ 32 chars — panic on startup if not
    WEBAUTHN_RP_ID, WEBAUTHN_RP_ORIGIN, DATABASE_URL, REDIS_URL required
    panic vs error: startup misconfig = panic (fail fast, don't serve)
    
    Story-ID: AUTH-001

commit d4a1c8e
Author: DEVOPS_ENGINEER <devops@healthguard.internal>
Date:   2026-07-19 09:00:00 +0000

    build(auth): multi-stage Dockerfile (distroless runtime)

    Builder: golang:1.22-alpine, CGO_ENABLED=0, trimpath, -ldflags="-s -w"
    Runtime: gcr.io/distroless/static-debian12 (non-root, no shell)
    Final image: ~8MB
    
    Story-ID: AUTH-001

commit c7f3b2a
Author: DEVOPS_ENGINEER <devops@healthguard.internal>
Date:   2026-07-18 17:00:00 +0000

    chore: add docker-compose.yml for local dev

    Services: postgres:16, clickhouse:24, redis:7, auth-service
    Sprint 2 services under profiles: [sprint2]
    Health checks on all services
    Schema auto-applied from docs/schema/postgres.sql
    
    Story-ID: INFRA-001

commit b5e2d9c
Author: ARCHITECT <arch@healthguard.internal>
Date:   2026-07-18 14:00:00 +0000

    docs: add ClickHouse schema (sepsis_scores, vitals, api_usage)

    MergeTree, PARTITION BY (toYYYYMM, tenant_id)
    vitals_hourly SummingMergeTree + materialized view
    api_usage_monthly_mv for Stripe billing reconciliation
    TTL: sepsis_scores 10yr, vitals 2yr
    
    Story-ID: INFRA-001

commit a3d1f7b
Author: ARCHITECT <arch@healthguard.internal>
Date:   2026-07-18 11:00:00 +0000

    docs: add PostgreSQL schema (partitioned audit_log, encrypted patients)

    Extensions: pgcrypto, uuid-ossp
    audit_log: partitioned by year, 6 partitions (6yr HIPAA retention)
    patients: pgp_sym_encrypt on PII fields, GDPR annotations
    vitals: partitioned by month
    ALL tables: tenant_id column + NOT NULL
    No MRN-only index (always query with tenant_id)
    
    Story-ID: INFRA-001

commit 9e8c4a2
Author: ARCHITECT <arch@healthguard.internal>
Date:   2026-07-17 16:00:00 +0000

    docs: add ADRs 001-005

    001: ClickHouse for analytics (vs TimescaleDB, Redshift, BigQuery)
    002: WebAuthn/FIDO2 passwordless (userVerification=required)
    003: SAML 2.0 deferred Sprint 2 (IAM budget 73%)
    004: Multi-region AWS, no VPC peering (GDPR)
    005: SCIM 2.0, immediate deprovisioning, HIPAA role mapping

commit 8d4e1f2
Author: ARCHITECT <arch@healthguard.internal>
Date:   2026-07-17 14:30:00 +0000

    docs: TRD v1 — architecture, STRIDE threat model, compliance

    ASCII architecture diagram, services table, trust boundaries
    STRIDE: Spoofing/Tampering/Repudiation/Info Disclosure/DoS/Elevation
    Auth flow diagrams (registration + authentication)
    Multi-region strategy (HIPAA + GDPR hard constraints)
    Compliance checklist

commit 7c1a9f3
Author: CTO <cto@healthguard.internal>
Date:   2026-07-17 12:00:00 +0000

    docs: Sprint 1 plan — IAM budget check, story sizing, GATE S1

    IAM budget: 73% → AUTH-002 (SAML) deferred (Fix 33A triggered)
    26pts selected: AUTH-001(8) AUTH-003(5) PAT-001(3) INFRA-001(5)
                    INFRA-002(3) AUTH-004(2)
    GATE S1: PASS (STRIDE + auth model + secrets mgmt reviewed)

commit 6b8d2e1
Author: CTO <cto@healthguard.internal>
Date:   2026-07-17 10:00:00 +0000

    docs: PRD v1 — goals, non-goals, personas, success metrics

    G1-G5 with metrics, 6 explicit non-goals (Fix 32A template)
    Personas: ICU Nurse, IT Admin, CFO, Physician
    Success metrics: sensitivity ≥85%, false-positive <12%, deprovisioning <60s
    Label map for SM-PLAN, OQ log (3 items)

commit 5a4c7b8  (initial)
Author: CTO <cto@healthguard.internal>
Date:   2026-07-17 09:00:00 +0000

    chore: initialize HealthGuard Pro repository

    Monorepo structure: services/, infra/, docs/, .github/
    README.md with stack overview and quick start
    Makefile with dev, test, lint, build, tf-plan targets
    .gitignore, go.work skeleton
```

---

## Sprint 1 Commit Stats

| Metric | Value |
|--------|-------|
| Total commits | 28 |
| Authors | BACKEND_LEAD, DEVOPS_ENGINEER, ARCHITECT, CTO |
| Files changed | 34 |
| Lines added | ~2,400 |
| Lines deleted | 0 (new project) |
| Test coverage (auth-service) | 78% |
| GATE S2 passes | 6/6 stories |
| Security findings (gitleaks/semgrep) | 0 HIGH/CRITICAL |
