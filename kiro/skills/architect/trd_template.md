<!-- LOAD-TYPE: CHECKLIST -->
---
id: trd_template
version: 1.0.0
owners: [architect, security_engineer]
tags: [foundation, trd, architecture, planning]
when_to_use: >
  When creating or reviewing /docs/foundation/architecture.md. Mandatory at GATE 2.
  STRIDE consumes the Trust Boundary Map (Section 3) directly — no re-derivation.
  Tech constraint levels (Section 1) tell SM-PLAN which decisions are locked vs. flexible.
  GATE 2 stays RED until all 7 sections are present and non-empty.
---

# TRD Template — Technical Requirements Document

FULL-LOAD REQUIRED — creation checklist and structural template.
Output file: `/docs/foundation/architecture.md`
Owner: `architect` (drafts) + `security_engineer` (reviews Sections 3, 5, 6)

---

## QUICK REFERENCE

- Write TRD AFTER PRD is approved. PRD says "what" — TRD says "how."
- Every tech decision MUST have a constraint level: HARD / PREFERRED / EXPERIMENTAL.
- Trust Boundary Map (Section 3) is pre-populated here — architect STRIDE uses it directly.
- Skill file hints (Section 6) feed SM-PLAN label assignment — no re-inference needed.
- Conflicts with PRD: TRD wins on HOW to build; PRD wins on WHAT to build.
- Conflicts with security-posture.md: security-posture.md wins on all security-specific decisions.

---

## TRD STRUCTURE CHECKLIST

Before marking TRD complete, verify ALL sections exist and are non-empty:

- [ ] Section 1: Tech Stack with constraint levels
- [ ] Section 2: System Architecture Overview
- [ ] Section 3: Trust Boundary Map ← STRIDE reads this directly
- [ ] Section 4: ADR Index
- [ ] Section 5: Non-Functional Requirements
- [ ] Section 6: Skill File Hints ← SM-PLAN reads this
- [ ] Section 7: Open Questions

---

## SECTION 1 — Tech Stack

Every entry MUST have a constraint level. No unlabeled decisions.

```
| Layer | Technology | Constraint Level | Reason |
|-------|-----------|-----------------|--------|
| Frontend | Next.js 14 (App Router) | PREFERRED | Can switch to Remix if App Router causes issues |
| Frontend | TypeScript | HARD CONSTRAINT | Team mandate, existing codebase |
| Backend | Node.js + Fastify | PREFERRED | Performance benefit over Express; can revert |
| Database | PostgreSQL 15 | HARD CONSTRAINT | Existing prod DB, no migration budget this phase |
| Cache | Redis 7 | PREFERRED | Elasticache in AWS; can use Memcached as fallback |
| Auth | OAuth 2.0 (Google/GitHub) | HARD CONSTRAINT | Signed contract with identity provider |
| Queue | BullMQ (Redis-backed) | PREFERRED | Simpler than SQS for current scale; revisit at 1M jobs/day |
| Search | PostgreSQL full-text | PREFERRED | Avoid Elasticsearch until search volume justifies it |
| Hosting | AWS (ECS Fargate) | HARD CONSTRAINT | Existing AWS org, SOC2 audit in progress |
| CI/CD | GitHub Actions | PREFERRED | Can migrate to CircleCI |
```

Constraint level definitions:
- **HARD CONSTRAINT**: Cannot change without explicit architectural decision record. Agents must not suggest alternatives.
- **PREFERRED**: Strong default. Can be changed with a new ADR and justification.
- **EXPERIMENTAL**: Proof-of-concept only. MUST NOT be used for production data paths until promoted.

---

## SECTION 2 — System Architecture Overview

```
ARCHITECTURE STYLE:  [monolith | modular monolith | microservices | serverless | hybrid]
DEPLOYMENT MODEL:    [single region | multi-region | edge | on-prem]
DATA FLOW:           [describe: user → frontend → API → DB / queue → worker / cache]

Component diagram (text form):
  [Browser / Mobile App]
       ↓ HTTPS
  [CDN / Load Balancer]
       ↓
  [API Gateway / BFF]
       ↓            ↓
  [Auth Service]  [Core API]
                     ↓          ↓
               [PostgreSQL]  [Redis Cache]
                               ↓
                         [BullMQ Workers]
                               ↓
                      [Email / Notification / External APIs]
```

---

## SECTION 3 — Trust Boundary Map ← STRIDE READS THIS DIRECTLY

architect fills this table at TRD creation time.
STRIDE task: run threat analysis AGAINST this table — do NOT re-derive boundaries from architecture prose.

```
| Boundary ID | From | To | Protocol | Primary Threats | STRIDE Letters |
|-------------|------|----|----------|----------------|----------------|
| TB-1 | Public Internet | API Gateway | HTTPS/TLS 1.3 | token injection, enumeration, DDoS | S, R, D |
| TB-2 | API Gateway | Auth Service | internal mTLS | session hijack, privilege escalation | S, E |
| TB-3 | Core API | PostgreSQL | TCP (VPC-internal) | SQL injection, data exfiltration | T, I |
| TB-4 | Core API | Redis Cache | TCP (VPC-internal) | cache poisoning, data leakage | T, I |
| TB-5 | Admin Panel | Core API | HTTPS + separate auth | horizontal privilege escalation | E, I |
| TB-6 | Workers | External APIs (Email/Stripe) | HTTPS | credential leakage, response tampering | S, T |
```

Format per threat: `[STRIDE letter]: [specific threat description]`
STRIDE output format: `T/R/I/D/E/S: [threat] → [mitigation]`
Excess mitigations (>2 per story) → TECH-DEBT stories (Fix 31E rule applies).

---

## SECTION 4 — ADR Index

All architectural decisions recorded as ADRs in `/docs/phase-N/adrs/`.
This index is a pointer table — quick lookup without opening individual ADR files.

```
| ADR ID | Decision | Status | Date | Alternatives Rejected |
|--------|----------|--------|------|----------------------|
| ADR-001 | PostgreSQL over MongoDB | Accepted | YYYY-MM-DD | MongoDB (flexible schema not needed), DynamoDB (over-engineered for current scale) |
| ADR-002 | BullMQ over SQS | Accepted | YYYY-MM-DD | SQS (adds AWS coupling), Celery (Python-only) |
| ADR-003 | JWT with RS256 | Accepted | YYYY-MM-DD | HS256 (banned — shared secret across services), sessions (stateful) |
```

New ADRs added here when architectural decisions change. Stale ADRs marked SUPERSEDED.

---

## SECTION 5 — Non-Functional Requirements

```
PERFORMANCE:
  API p95 response time: < 200ms (authenticated endpoints)
  API p99 response time: < 500ms
  Dashboard LCP: < 2.0s
  Background job processing: < 30s for standard jobs, < 5min for batch

SCALABILITY:
  Concurrent users at launch: 1,000
  Target at 12 months: 10,000
  Peak burst capacity: 3x normal (handle marketing spikes)

AVAILABILITY:
  SLA target: 99.9% uptime (< 8.7h downtime/year)
  Planned maintenance window: Sundays 02:00-04:00 UTC
  RTO (recovery time objective): < 1 hour
  RPO (recovery point objective): < 15 minutes

SECURITY:
  → See /docs/foundation/security-posture.md (security-posture.md wins on security decisions)

DATA RESIDENCY:
  [EU only | US only | global | specify per data type]
```

---

## SECTION 6 — Skill File Hints ← SM-PLAN READS THIS

Maps system components to Kiro labels and skill files. SM-PLAN uses this to assign labels without re-inferring from architecture prose.

```
| Component | Labels | Skill Files to Load | Notes |
|-----------|--------|-------------------|-------|
| Auth module | [be/auth, security-critical] | auth_design.md + webauthn_fido2.md | WebAuthn declared in security-posture.md |
| User API (CRUD) | [be/api, be/database] | api_versioning.md + idempotency_patterns.md | versioned from day 1 |
| Payment flow | [be/api, security-critical] | idempotency_patterns.md + api_security_owasp_top10.md | Stripe integration |
| Dashboard UI | [fe/component, fe/state, fe/perf] | component_decomposition.md + state_management_patterns.md + core_web_vitals.md | LCP < 2s target |
| Analytics queries | [data/pipeline] | analytical_datastore_patterns.md | ClickHouse for usage metrics |
| CI/CD pipeline | [devops/ci, devops/infra] | ci_cd_pipeline_design.md + iac_terraform_patterns.md | GitHub Actions |
| Background workers | [be/queue, be/resilience] | async_job_queue_patterns.md + circuit_breaker_bulkhead.md | BullMQ |
```

---

## SECTION 7 — Open Questions

Unresolved architectural decisions. Each blocks a listed gate or story.

```
| Question | Blocks | Owner | Due |
|----------|--------|-------|-----|
| Multi-region from day 1 or post-MVP? | NFR finalization | architect + cto | before Sprint 2 |
| SCIM provisioning required for enterprise tier? | be/api stories | architect | before Sprint 3 |
| ClickHouse self-hosted or managed (Clickhouse Cloud)? | data/pipeline stories | database_architect | before Sprint 2 |
```

---

## VALIDATION LOG

When TRD is complete, emit:
```
[TRD-COMPLETE: stack=N decisions (HARD=X/PREFERRED=Y/EXPERIMENTAL=Z) | trust-boundaries=M | ADRs=K | skill-hints=P components mapped | open-questions=Q]
```
