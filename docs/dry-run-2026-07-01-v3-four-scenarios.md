# Dry Run v3 — Four Scenarios
**Date:** 2026-07-01
**Fixes active:** Fix 1–29 (all implemented)
**Method:** Full-depth trace per scenario. Same methodology as dry-run-v2.
**Goal:** Surface gaps beyond Fix 29. Each scenario stresses a different part of the system.

---

## SCENARIOS

| # | Scenario | Primary stress |
|---|----------|---------------|
| 1 | Healthcare / HIPAA | Regulatory PII, FHIR API, HIPAA audit trail, consent flows |
| 2 | FinTech / PCI-DSS | Payment ledger, KYC/AML, SOX audit, security-critical STRIDE |
| 3 | B2B Enterprise SaaS | Multi-tenant, SSO/SAML, RBAC, deferred stories across sprints |
| 4 | IoT / Edge Platform | MQTT telemetry, edge compute, OTA updates, SLI/SLO co-maker |

---

---

# SCENARIO 1 — Healthcare / HIPAA

**Prompt:** "Build a healthcare platform — EHR patient records + FHIR R4 API + patient portal web app + iOS/Android mobile app + HIPAA audit trail + HL7 messaging + role-based access (physician/nurse/admin) + multi-facility support"

---

## STEP 0 — COMPLEXITY GATE

Prompt length: >8 words. Contains: BUILD, PLATFORM, API, APP, SYSTEM.
→ Proceed to STEP 2.

## STEP 1 — ENV DETECTION

`[ENV] TRACKER_MODE=Jira | GIT_MODE=REMOTE`

## STEP 2 — REQUEST CLASSIFICATION

Keywords: healthcare platform, EHR, FHIR API, patient portal, mobile app, HIPAA, HL7, multi-facility.
→ BUILD class. → STEP 3.

## STEP 3 — MODE SELECTION + CONFIDENCE GATE (Fix 27B)

System-scale signals: platform(1), API(2), app(3), HIPAA(4), multi-facility(5), HL7(6).
Signal count: 6. Single sentence with no role ambiguity.
→ confidence=HIGH (97%)
→ `[MODE: 1 auto-inferred | confidence=HIGH (97%) | signals=6]`

## STEP 4 — LOAD STEERING FILES

```
LOAD: team-orchestrator-core.md ✅
LOAD: team-orchestrator-rules.md ✅
LOAD: skill-selection-matrix.md ✅
NOTE: skill-label-index.md deferred to SM-PLAN
[TOKEN ESTIMATE: ~22,900 baseline | Tier: PEAK]
```

---

## THINK PHASE

### market_researcher
Segments: Physicians, Nurses, Admins, Patients. TAM: $25B US EHR market.
Regulatory: HIPAA Privacy Rule + Security Rule. HITECH. ONC Interoperability Rule.
Competitive: Epic, Cerner, athenahealth. Differentiator: FHIR-native + mobile-first.

### cto
Tech stack decision:
- Backend: Node.js / Python FastAPI (FHIR R4 server — HAPI FHIR or Firely)
- Database: PostgreSQL (PHI) + MongoDB (audit logs) + Redis (session)
- Mobile: React Native (shared codebase iOS/Android)
- Web portal: Next.js
- Messaging: HL7 MLLP → FHIR converter
- Infra: AWS HIPAA BAA eligible services (ECS Fargate, RDS, S3 with encryption)
- Auth: SMART on FHIR (OAuth2 + PKCE)

**ADR-001:** SMART on FHIR over custom auth — FHIR-native, patient app authorization standard.
**ADR-002:** PostgreSQL over DynamoDB for PHI — ACID guarantees + audit trail foreign keys.

### architect
STRIDE threat model on FHIR API trust boundary:

| Threat | Category | Mitigation |
|--------|----------|-----------|
| Unauthorized PHI access | Spoofing | SMART on FHIR + MFA required |
| PHI in transit interception | Tampering | TLS 1.3 mandatory, no HTTP |
| Audit log deletion | Repudiation | Immutable audit log (append-only, WORM S3) |
| PHI data exfiltration | Information Disclosure | Field-level encryption for SSN/DOB |
| FHIR API DDoS | Denial of Service | WAF + rate limiting per client_id |
| Role escalation (nurse→physician) | Elevation of Privilege | RBAC enforced at API layer, FHIR resource scopes |

`[STRIDE-BRIDGE: 6 mitigations → criteria will be added to affected stories (max 2/story)]`

### DESIGN SYSTEM GATE CHECK (Fix 29A)

Patient portal is a web app + mobile app.
Check: does `/docs/design_system.md` exist? → NO (new project).

**CREATION OWNERSHIP (Fix 29A):**
- Web: `technical_writer` → Section 1 (Typography) + Section 6 (Component Voice)
- Web: `frontend_lead` → Sections 2–5 (Color, Spacing, Layout, Animation)
- Mobile: `mobile_engineer` → `/docs/design_system_mobile.md` (all 6 sections)

`[DESIGN GATE: design_system.md NOT FOUND — assigning creation. Owner: technical_writer+frontend_lead (web), mobile_engineer (mobile). BLOCKS UI start.]`

**technical_writer + frontend_lead execute design_system.md:**
```
# Design System — HealthPortal
Generated: 2026-07-01 | Gate version: 1.0.0

Typography:
  Display: Neue Haas Grotesk — clinical precision, trusted, not sterile
  Body: Source Serif 4 — warm, readable for dense medical content
  Mono: JetBrains Mono — dosage/code fields

Color System:
  Primary:   #1B4F72 — deep medical blue, trust + authority
  Secondary: #27AE60 — health/status green, positive outcomes
  Surface:   #F8FAFB — near-white, clean clinical environment
  Text:      #1A1A2E — near-black, high contrast for readability
  Accent:    #E74C3C — alerts, critical values, warnings

Spacing: Base 8px. Tokens space-1(8) through space-9(96).
Layout: asymmetric editorial grid. Data-dense dashboard sections.
Animation: minimal. Confirm actions only (pill dispense, order sign).
Component Voice: "Precise and calm. Dense data without anxiety. The UI handles life-critical information — it must feel like a trusted tool, not a consumer app. No gradients, no decoration. Every element earns its place."
```

`[DESIGN GATE: design_system.md locked. Proceeding to DESIGN phase.]`

### GATE 1 — THINK → DESIGN
Artifacts: market_research.md ✅ | tech_strategy.md ✅ | design_system.md ✅ | STRIDE threat model ✅
→ `"THINK complete. Confirm strategy to proceed to DESIGN?"`

---

## DESIGN PHASE

### architect
Components:
1. FHIR R4 Resource Server (Patient, Observation, MedicationRequest, AllergyIntolerance)
2. HL7 MLLP Gateway (ADT, ORM, ORU message types → FHIR converter)
3. SMART on FHIR Authorization Server (OAuth2 + PKCE, scopes per FHIR resource type)
4. HIPAA Audit Service (every PHI access logged: who, what resource, when, from where)
5. Patient Portal (Next.js, SMART app launch)
6. Mobile App (React Native, biometric auth, offline PHI cache with encryption)
7. RBAC Service (physician/nurse/admin/patient roles, facility-scoped permissions)

### database_architect
- PHI tables: encrypted at rest (RDS + KMS). Row-level security by facility.
- Audit table: append-only. No UPDATE/DELETE on audit rows. WORM policy.
- FHIR Resource store: PostgreSQL JSONB for resource flexibility.
- Retention: HIPAA requires 6-year retention. S3 Glacier for archived records.

### GATE 2 — DESIGN → DEVELOP

Checklist:
- [ ] ADRs have Domain+Scope [Fix 25P]: ADR-001 (auth/FHIR), ADR-002 (db/PHI) ✅
- [ ] STRIDE-BRIDGE logged [Fix 26D] ✅ — 6 mitigations queued
- [ ] VERIFIER commands runnable [Fix 27C] ✅ — npm test, pytest, semgrep available
- [ ] design_system.md created [Fix 29A] ✅

→ GATE 2 PASS.

---

## SM-GATE → SM-PLAN

### SM-GATE
Sprint 1 scope review. HIPAA compliance stories in Sprint 1 (non-negotiable — no PHI before audit trail).

Story breakdown:

| Story | Description | Labels |
|-------|-------------|--------|
| HC-1 | FHIR Patient resource CRUD API | be/api, be/database, security-critical |
| HC-2 | HIPAA Audit Trail service | be/api, be/database, security-critical, be/pii |
| HC-3 | SMART on FHIR authorization server | be/auth, security-critical |
| HC-4 | RBAC service — physician/nurse/admin scopes | be/auth, be/api |
| HC-5 | Patient Portal — login + patient summary page | fe/component, fe/a11y |
| HC-6 | React Native mobile app — biometric auth + offline cache | mobile/ios, mobile/android, be/auth |
| HC-7 | HL7 MLLP → FHIR converter gateway | data/pipeline, be/api |

### LABEL VALIDATION SELF-CHALLENGE (Fix 28D)

HC-1: [be/api, be/database, security-critical]
- be/api: API contract, versioning, error format → unique ✅
- be/database: schema, migrations, indexes → unique ✅
- security-critical: STRIDE review, threat criteria → unique ✅
`[LABELS VALIDATED: HC-1 | kept=[be/api, be/database, security-critical] | removed=[] | reason: all three add distinct quality bars]`

HC-2: [be/api, be/database, security-critical, be/pii]
- be/api ✅ | be/database ✅ | security-critical ✅
- be/pii: PHI scrubbing, retention tagging → unique ✅
`[LABELS VALIDATED: HC-2 | kept=[be/api, be/database, security-critical, be/pii] | removed=[] | reason: be/pii adds PHI-specific criteria not covered by security-critical]`

HC-7: [data/pipeline, be/api]
- data/pipeline: HL7 transform, schema evolution → unique ✅
- be/api: FHIR output contract → unique ✅
`[LABELS VALIDATED: HC-7 | kept=[data/pipeline, be/api] | removed=[] | reason: both required]`

### SKILL LOADING — CHECKLIST SEPARATION (Fix 29B)

HC-1 skill load (labels: be/api, be/database, security-critical):
- Narrative: api_versioning.md, idempotency_patterns.md, error_handling_strategies.md → ~420 tok compressed
- CHECKLIST: api_security_owasp_top10.md (LOAD-TYPE: CHECKLIST) → ~890 tok full-load
- CHECKLIST: application_security_testing_sast_dast.md (LOAD-TYPE: CHECKLIST) → ~760 tok full-load
- CHECKLIST: stride_threat_modeling.md (LOAD-TYPE: CHECKLIST) → ~840 tok full-load
`[SKILLS: labels=[be/api,be/database,security-critical] | role=senior_engineer_be | narrative=api_versioning,idempotency,error_handling ~420tok | checklist=owasp_top10,sast_dast,stride ~2,490tok full | Total: ~2,910tok | Tier: PEAK]`

HC-2 skill load (labels: be/api, be/database, security-critical, be/pii):
- Narrative: ~480 tok compressed
- CHECKLIST: owasp_top10, sast_dast, stride, data_security_encryption → ~3,200 tok full
`[SKILLS: labels=[be/api,be/database,security-critical,be/pii] | narrative=~480tok | checklist=~3,200tok full | Total: ~3,680tok | Tier: PEAK]`

`[TOKEN ESTIMATE: ~34K accumulated | Tier: PEAK]`

---

## DEVELOP PHASE — STORY HC-1

### PRE-ACTIVATION LESSONS SCAN (Fix 28B)
`"Scan docs/lessons.md for entries WHERE domain matches labels [be/api, be/database, security-critical]"`
→ Assume Sprint 1, fresh project: `[LESSONS: no match — first sprint, lessons.md empty]`

### LOOP SPEC — HC-1: FHIR Patient Resource CRUD API

```
▸ LOOP SPEC — HC-1: FHIR Patient resource CRUD API

GOAL:
  FHIR R4 Patient resource endpoints (GET/POST/PUT/DELETE) pass HAPI FHIR
  validator with zero conformance errors. PHI stored encrypted. Audit entry
  written on every access.

VERIFIER (Fix 27C):
  - npm test -- --coverage --testPathPattern=fhir/patient
  - npx semgrep --config=p/owasp-top-ten src/fhir/
  - npx tsc --noEmit
  - python -m pytest tests/fhir_conformance/ -v   # HAPI FHIR validator

CRITERIA:
  STRIDE-BRIDGE:
    STRIDE-S: SMART on FHIR scope validated on every endpoint (score 1-10)
    STRIDE-I: PHI field-level encryption verified in DB row (score 1-10)
  be/api:
    API versioned at /fhir/r4/ prefix (score 1-10)
    Error responses follow FHIR OperationOutcome format (score 1-10)
  be/database:
    Migration reversible — down() implemented (score 1-10)
    No N+1 queries on patient-with-resources fetch (score 1-10)
  security-critical:
    OWASP A1 (injection) scan: zero findings (score 1-10)

STOP WHEN: all ≥ 8, OR 8 iterations reached.
```

`[VERIFIER OUTPUT: exit=0 | stdout=42 tests pass, coverage 87% | semgrep: 0 findings | tsc: clean | conformance: PASS | pass=Y]`

Iteration 1 scores:
- STRIDE-S: 9 (SMART scopes validated on all 4 endpoints)
- STRIDE-I: 7 (field encryption present, SSN encrypted, DOB not yet)
- API versioned: 10
- OperationOutcome format: 9
- Migration reversible: 10
- No N+1: 8
- OWASP A1: 10

→ 1 criterion below 8: STRIDE-I (DOB not encrypted)

Iteration 2: DOB encrypted. All scores ≥ 8.
`[LOOP CLOSED: HC-1 | iter=2 | all criteria ≥8]`

---

## DEVELOP PHASE — STORY HC-2

### PRE-ACTIVATION LESSONS SCAN (Fix 28B)
Domain: [be/api, be/database, security-critical, be/pii]
→ `[LESSONS: no match — first sprint]`

### LOOP SPEC — HC-2: HIPAA Audit Trail Service

```
▸ LOOP SPEC — HC-2: HIPAA Audit Trail service

GOAL:
  Every PHI access (read/write/delete) generates an immutable audit record with:
  user_id, resource_type, resource_id, action, timestamp, source_ip, facility_id.
  Audit records are append-only (no UPDATE/DELETE possible).

VERIFIER (Fix 27C):
  - npm test -- --testPathPattern=audit
  - npx semgrep --config=p/owasp-top-ten src/audit/
  - python -c "from audit.db import try_delete_audit; try_delete_audit()" && echo "FAIL: delete succeeded" || echo "PASS: delete blocked"

CRITERIA:
  STRIDE-BRIDGE:
    STRIDE-R: Audit log deletion attempt returns 403 (score 1-10)
    STRIDE-I: Audit records contain all 7 required HIPAA fields (score 1-10)
  be/pii:
    PHI fields scrubbed from application logs (no SSN/DOB in stdout) (score 1-10)
    Retention period tagged on audit records (HIPAA: 6 years) (score 1-10)
  security-critical:
    OWASP scan: zero findings on audit endpoints (score 1-10)

STOP WHEN: all ≥ 8, OR 8 iterations reached.
```

`[VERIFIER OUTPUT: exit=0 | audit tests: 28 pass | delete attempt: PASS (blocked) | semgrep: 0 findings | pass=Y]`

Iteration 1 scores:
- STRIDE-R (delete blocked): 10
- STRIDE-I (7 HIPAA fields): 8 — all fields present
- PHI scrubbed from logs: 6 — DOB still leaking in debug logs
- Retention tag: 10
- OWASP: 10

→ 1 below 8: PHI in debug logs

**⚠️ GAP CANDIDATE:** Debug log PHI leakage is a new failure mode not covered by existing labels. be/pii criterion "PHI scrubbed before logging" catches it — but the debug log path bypasses the scrubber middleware. This pattern (middleware bypass via debug path) is not in lessons.md.

Iteration 2: Debug log PHI scrubbed at logger layer. All ≥ 8.
`[LOOP CLOSED: HC-2 | iter=2 | all criteria ≥8]`

---

## CONTEXT CHECK
`[TOKEN ESTIMATE: ~68K accumulated | Tier: GOOD (was PEAK)]`
→ Transition to GOOD tier. Compress reads from here. Max 2 ACT reloads per story.

---

## DEVELOP PHASE — STORY HC-6 (mobile — React Native + biometric + offline cache)

### PRE-ACTIVATION LESSONS SCAN (Fix 28B)
Domain: [mobile/ios, mobile/android, be/auth]
→ `[LESSONS: no match — first sprint]`

### DESIGN SYSTEM MOBILE GATE CHECK
`mobile_engineer` checks: `/docs/design_system_mobile.md` — was assigned in THINK phase.
`[DESIGN GATE: design_system_mobile.md locked. Proceeding to mobile implementation.]`

### LOOP SPEC — HC-6: React Native biometric auth + offline PHI cache

```
▸ LOOP SPEC — HC-6: React Native biometric + offline cache

GOAL:
  RN app authenticates via SMART on FHIR + biometric (FaceID/TouchID fallback).
  Offline PHI cache encrypted at rest (device keychain). Cache expires after 24h.

VERIFIER (Fix 27C):
  - npx jest --testPathPattern=mobile/auth
  - npx tsc --noEmit
  - npx semgrep --config=p/owasp-mobile src/mobile/

CRITERIA:
  mobile/ios: FaceID entitlement configured, LAContext fallback to PIN (score 1-10)
  mobile/android: Biometric API uses BiometricPrompt (not deprecated FingerprintManager) (score 1-10)
  be/auth: SMART on FHIR token stored in keychain (not AsyncStorage) (score 1-10)
  be/pii: PHI cache encrypted with AES-256-GCM, key from device keychain (score 1-10)
  be/pii: Cache TTL enforced — stale PHI purged on app foreground (score 1-10)

STOP WHEN: all ≥ 8, OR 8 iterations reached.
```

**⚠️ GAP CANDIDATE — 30A:** mobile/ios and mobile/android criteria in the same loop spec force the senior_engineer to be both iOS and Android expert. The skill files for mobile/ios vs mobile/android are separate but the VERIFIER runs one test suite. If the RN codebase is unified, this works — but if there are platform-specific paths, one VERIFIER may not exercise both. No guidance in loop-engine.md for "platform-split verification within a single mobile story."

`[VERIFIER OUTPUT: exit=0 | 31 mobile tests pass | tsc: clean | semgrep: 1 LOW finding (info leak in debug mode) | pass=Y]`

Iteration 1 scores:
- FaceID: 9
- BiometricPrompt: 9
- SMART token in keychain: 10
- PHI cache encrypted: 8
- Cache TTL: 7 — TTL checked only on cold start, not on resume from background

Iteration 2: TTL checked on AppState change event. All ≥ 8.
`[LOOP CLOSED: HC-6 | iter=2 | all criteria ≥8]`

---

## SM-RETRO — SCENARIO 1

`[TOKEN ESTIMATE: ~125K accumulated | Tier: DEGRADING (just crossed 120K)]`
`[CRITICAL: SM-RETRO writes permitted — ~2K tok (Fix 29D). Writing lessons + checkpoint.]`

### Lessons generated:

**LESSON-HC-1:** Debug log middleware bypass — PHI can leak via framework debug paths that bypass application-layer scrubbers. Mitigation: scrub at logger layer (not middleware), so all output paths are covered. Domain: be/pii, security-critical.

**LESSON-HC-2:** Mobile biometric TTL — cache expiry must be checked on AppState "active" event, not just cold start. Background resume doesn't trigger constructor-level checks. Domain: mobile/ios, mobile/android.

### Sprint 1 gaps found:

| ID | Description | Severity |
|----|-------------|----------|
| **GAP-30A** | Mobile platform-split VERIFIER — single loop spec for mobile/ios + mobile/android doesn't guarantee platform-specific paths are both exercised | 🟡 Medium |

---
---

# SCENARIO 2 — FinTech / PCI-DSS

**Prompt:** "Build a payment processing platform — multi-currency ledger + card payment processing (Stripe/Braintree) + KYC/AML identity verification + SOX audit compliance + real-time fraud scoring + merchant dashboard + webhook delivery system"

---

## STEP 0–3 — MODE DETECTION

Signals: platform(1), payment processing(2), ledger(3), KYC/AML(4), SOX(5), fraud scoring(6), webhook(7).
Count: 7. → confidence=HIGH (98%)
`[MODE: 1 auto-inferred | confidence=HIGH (98%) | signals=7]`
`[TOKEN ESTIMATE: ~22,900 baseline | Tier: PEAK]`

---

## THINK PHASE

### cto
Stack: Node.js + TypeScript, PostgreSQL (ledger — double-entry), Redis (idempotency keys), Kafka (event streaming), Stripe Connect (card processing), Jumio/Onfido (KYC), AWS (PCI-DSS compliant regions).

**ADR-001:** Double-entry bookkeeping ledger over simple balance table — SOX requires auditability of every financial movement.
**ADR-002:** Idempotency keys on all payment endpoints — prevent double-charge on retry.
**ADR-003:** Webhook delivery via SQS + Lambda fanout — decoupled, retriable, observable.

### architect — STRIDE on Payment API trust boundary

| Threat | Mitigation |
|--------|-----------|
| Spoofing (fake merchant) | API key + webhook signature (HMAC-SHA256) mandatory |
| Tampering (amount modification in transit) | Request signing, TLS 1.3, idempotency key locks amount |
| Repudiation (deny transaction happened) | Immutable double-entry ledger + SOX audit log |
| Info Disclosure (card data) | PCI-DSS: no card storage, Stripe tokenization only |
| DoS (payment flood) | Rate limit per merchant_id, circuit breaker |
| Elevation (merchant → admin) | RBAC scoped to merchant_id, no cross-merchant reads |

`[STRIDE-BRIDGE: 6 mitigations → criteria queued for payment API stories]`

### DESIGN SYSTEM GATE (Fix 29A)
Merchant dashboard = web app. Check design_system.md → NO (new project).
**CREATION OWNERSHIP:** technical_writer + frontend_lead.

```
# Design System — PayLedger Dashboard
Typography: Roobert — financial data clarity, modern but not casual
Body: Inter (body only, non-standard heading justifies this)
Color: Primary #0A2540 (Stripe navy) → rejected. Use #1A3A5C (darker, proprietary).
      Accent: #00C896 — success green for completed transactions.
      Alert: #FF4D4F — failed/reversed transactions.
Layout: data-dense. Tables primary. No hero section.
Component Voice: "Transaction data first. Every pixel either carries a number or navigates to one. No marketing energy — this is an operations tool."
```

`[DESIGN GATE: design_system.md locked.]`

---

## SM-PLAN

| Story | Labels |
|-------|--------|
| FT-1 | Double-entry ledger service | be/database, be/api, security-critical |
| FT-2 | Stripe Connect payment processor integration | be/api, be/resilience, security-critical |
| FT-3 | Idempotency key service | be/api, be/resilience |
| FT-4 | KYC/AML identity verification webhook handler | be/api, data/pipeline, security-critical, be/pii |
| FT-5 | SOX audit trail service | be/database, be/api, security-critical, be/pii |
| FT-6 | Real-time fraud scoring (ML feature store + rules engine) | data/eda, data/ml, be/api |
| FT-7 | Webhook delivery system (SQS fanout + retry) | be/queue, be/resilience, devops/k8s |
| FT-8 | Merchant dashboard | fe/component, fe/performance |

### LABEL VALIDATION (Fix 28D)

FT-6: [data/eda, data/ml, be/api]
- data/eda: EDA on transaction features, fraud signal distribution → unique ✅
- data/ml: model scoring, threshold calibration → unique ✅
- be/api: REST endpoint for score serving → unique ✅
`[LABELS VALIDATED: FT-6 | kept=[data/eda,data/ml,be/api] | removed=[] | all unique]`

FT-6 has [data/eda] → CO-MAKER PATTERN (Fix 26B) triggers.
PRIMARY: data_scientist | SECONDARY: senior_engineer_be | CHECKER: qa_engineer
`[CO-MAKER: data_scientist+senior_engineer_be | story=FT-6]`
→ DUAL LOOP SPEC required (Fix 29C).

### CHECKLIST TOKEN COST (Fix 29B)

FT-1 skills:
- Narrative: ~350 tok
- CHECKLIST: owasp_top10 (~890), stride (~840) → ~1,730 tok full-load
`[SKILLS: narrative=~350tok | checklist=owasp_top10,stride ~1,730tok full | Total: ~2,080tok]`

FT-5 skills (SOX audit = be/pii + security-critical heavy):
- Narrative: ~380 tok
- CHECKLIST: owasp, sast_dast, stride, data_security → ~3,520 tok full-load
`[SKILLS: narrative=~380tok | checklist=~3,520tok full | Total: ~3,900tok]`

⚠️ **GAP CANDIDATE — 30B:** FT-5 alone costs ~3,900 tokens in CHECKLIST skills. With 8 stories in Sprint 1, cumulative CHECKLIST load could be ~15-20K tokens — enough to push the tier faster than the narrative estimate suggests. The system logs it correctly (Fix 29B) but there's no rule that says "if CHECKLIST cost per story exceeds threshold, flag to SM." SM has no early warning of a CHECKLIST-heavy sprint.

---

## DEVELOP PHASE — FT-6 (CO-MAKER DUAL LOOP SPEC)

### PRE-ACTIVATION LESSONS SCAN (Fix 28B)
Domain: [data/eda, data/ml, be/api]
→ `[LESSONS: no match — first sprint]`

### DUAL LOOP SPEC — FT-6 (Fix 29C)

```
▸ LOOP SPEC A — FT-6-PRIMARY: Fraud Scoring — data_scientist

GOAL:
  ML fraud scoring model achieves AUC ≥ 0.92 on holdout set.
  Feature pipeline reproducible. Threshold calibrated at <1% false positive rate.

VERIFIER:
  - python -m pytest tests/ml/fraud_model/ -v
  - python scripts/eval_fraud_model.py --threshold-fp 0.01

CRITERIA:
  data/ml: AUC ≥ 0.92 on holdout (score 1-10)
  data/eda: feature drift check implemented (score 1-10)
  data/ml: experiment reproducible (seed set, MLflow logged) (score 1-10)

STOP WHEN: all ≥ 8, OR 8 iterations reached.
```

```
▸ LOOP SPEC B — FT-6-SECONDARY: Fraud Score API — senior_engineer_be

GOAL:
  REST endpoint /v1/fraud/score accepts transaction payload, calls model,
  returns {score: 0-1, label: low|medium|high} in < 50ms p99.

VERIFIER:
  - npm test -- --testPathPattern=fraud-api
  - npx semgrep --config=p/owasp-top-ten src/api/fraud/
  - k6 run tests/load/fraud_score_k6.js  # p99 latency check

CRITERIA:
  be/api: response schema matches contract (score 1-10)
  be/resilience: model timeout → fallback to rules-engine (score 1-10)
  be/performance: p99 < 50ms under 1000 rps (score 1-10)
  STRIDE-S: API key + merchant_id scope enforced (score 1-10)

STOP WHEN: all ≥ 8, OR 8 iterations reached.
```

`[CO-MAKER RUNNING: FT-6-PRIMARY (data_scientist) + FT-6-SECONDARY (senior_engineer_be) | dual spec active]`

**PRIMARY loop — Iteration 1:**
`[VERIFIER OUTPUT: exit=0 | AUC=0.94 | FP rate=0.008 | MLflow: logged | pass=Y]`
- AUC: 9 | drift check: 7 (implemented but not alerting) | reproducible: 10
→ 1 below 8.

**PRIMARY loop — Iteration 2:**
Drift alerting wired to Kafka topic. All ≥ 8.
`[LOOP A CLOSED: FT-6-PRIMARY | iter=2 | all criteria ≥8]`

**SECONDARY loop — Iteration 1:**
`[VERIFIER OUTPUT: exit=0 | API tests: 18 pass | semgrep: 0 | k6: p99=62ms (FAIL) | pass=N]`
- API schema: 10 | fallback: 9 | p99 latency: 5 (62ms, >50ms) | STRIDE-S: 10
→ p99 failing.

**SECONDARY loop — Iteration 2:**
Model call async with local cache for recent merchant_id patterns. p99 → 41ms.
`[VERIFIER OUTPUT: exit=0 | k6: p99=41ms | pass=Y]`
All ≥ 8.
`[LOOP B CLOSED: FT-6-SECONDARY | iter=2 | all criteria ≥8]`

`[CO-MAKER DONE: story=FT-6 | PRIMARY SPEC: all ≥8 | SECONDARY SPEC: all ≥8 | CHECKER: PASS]`

---

## DEVELOP PHASE — FT-3 (Idempotency Key Service)

### LOOP SPEC — FT-3

```
▸ LOOP SPEC — FT-3: Idempotency Key Service

GOAL:
  Payment endpoint with same idempotency_key from same client returns
  identical response within 24h window. Concurrent requests with same key
  block until first completes (no double-charge).

VERIFIER:
  - npm test -- --testPathPattern=idempotency
  - npx tsc --noEmit

CRITERIA:
  be/resilience: concurrent duplicate blocked by Redis SETNX lock (score 1-10)
  be/api: 24h expiry enforced — expired key generates fresh charge (score 1-10)
  be/resilience: idempotency key scoped to client_id (no cross-client reuse) (score 1-10)
```

**⚠️ GAP CANDIDATE — 30C:** The idempotency key story has [be/api, be/resilience] labels. The skill files for be/resilience cover retry + circuit breaker + rate limit — but NOT idempotency key design specifically (that's in backend_lead/idempotency_patterns.md under be/api). The criteria written above came from the engineer's knowledge, not label-sourced criteria. The label→skill mapping silently misses idempotency as a dedicated criterion source. The be/api label resolves to `backend_lead/idempotency_patterns.md` but only if the label index has that explicit mapping — and skill-label-index.md maps be/api to idempotency_patterns.md ✅. So this works, but only because of a specific file name match. If the file were named differently, it would be missed.

`[VERIFIER OUTPUT: exit=0 | 22 tests pass | tsc: clean | pass=Y]`
Iteration 1: All ≥ 8.
`[LOOP CLOSED: FT-3 | iter=1 | all criteria ≥8]`

---

## SM-RETRO — SCENARIO 2

`[TOKEN ESTIMATE: ~135K | Tier: DEGRADING]`
`[CRITICAL exception: SM-RETRO writes permitted (Fix 29D)]`

**Lessons:**
- **LESSON-FT-1:** CHECKLIST-heavy sprints (SOX + PCI stories) can accumulate 15-20K extra tokens vs estimate. Log the total early (Fix 29B helps) but no preemptive SM warning exists.
- **LESSON-FT-2:** CO-MAKER dual loop with p99 latency criterion requires load test VERIFIER (k6/locust). If load test tool unavailable, SECONDARY loop is BLOCKED:VERIFIER-UNEXECUTABLE — need fallback criterion.

### Sprint 2 gaps found:

| ID | Description | Severity |
|----|-------------|----------|
| **GAP-30B** | CHECKLIST-heavy sprint early warning missing — no SM alert when CHECKLIST token cost per sprint exceeds ~10K tokens | 🟡 Medium |
| **GAP-30C** | Load test VERIFIER dependency — p99 latency criteria require k6/locust; if unavailable, SECONDARY co-maker loop blocks with no documented fallback | 🟡 Medium |

---
---

# SCENARIO 3 — B2B Enterprise SaaS

**Prompt:** "Build a B2B project management SaaS — multi-tenant workspace isolation + SSO/SAML 2.0 + granular RBAC + real-time collaboration (CRDTs) + Stripe billing + usage-based metering + REST + GraphQL API + audit logs + white-label support"

---

## STEP 0–3 — MODE DETECTION

Signals: SaaS(1), multi-tenant(2), SSO/SAML(3), RBAC(4), real-time collaboration(5), GraphQL(6), billing(7).
Count: 7. → confidence=HIGH (98%)
`[MODE: 1 auto-inferred | confidence=HIGH (98%)]`

---

## THINK PHASE

### cto
Stack: Next.js (web), Node.js/TypeScript (API), PostgreSQL (per-tenant schemas), Redis (CRDT sync), Yjs (CRDT library), SAML2 (Okta/Azure AD), Stripe (billing + metering), GraphQL Yoga.

**ADR-001:** Per-tenant PostgreSQL schema (not row-level) — strict isolation, no cross-tenant query leakage risk.
**ADR-002:** Yjs CRDT for real-time collaboration — conflict-free, offline-first, proven in production (Notion-style).
**ADR-003:** Usage metering via Stripe Metered Billing — avoids building billing infrastructure.

### architect — STRIDE on Multi-tenant API

| Threat | Mitigation |
|--------|-----------|
| Spoofing (tenant impersonation) | JWT must contain tenant_id claim, validated on every request |
| Tampering (cross-tenant write) | Schema-per-tenant enforces DB isolation at Postgres level |
| Repudiation (audit disputes) | Audit log with actor, tenant, resource, action, timestamp |
| Info Disclosure (tenant data leak) | ORM tenant context forced at middleware — no raw SQL without tenant_id |
| DoS (one tenant starves others) | Per-tenant rate limits + connection pool limits |
| Elevation (member → admin) | RBAC roles stored per-workspace, not per-user |

`[STRIDE-BRIDGE: 6 mitigations → criteria queued]`

---

## SM-PLAN

| Story | Labels |
|-------|--------|
| B2B-1 | Multi-tenant schema provisioning + migration runner | be/database, be/api, security-critical |
| B2B-2 | SSO/SAML 2.0 integration (Okta/Azure AD) | be/auth, security-critical |
| B2B-3 | RBAC service — workspace-scoped roles | be/auth, be/api |
| B2B-4 | CRDT real-time collaboration (Yjs + WebSocket) | be/api, be/resilience, fe/component |
| B2B-5 | Stripe billing + usage metering | be/api, be/resilience |
| B2B-6 | Audit log service | be/database, be/api, security-critical, be/pii |
| B2B-7 | GraphQL API layer | be/api |
| B2B-8 | White-label theme system | fe/component, fe/a11y |

**Co-maker check:** No [data/eda] labels → no co-maker stories in this sprint. Standard single-maker pattern.

### DEFERRED STORY TEST (Fix 29E)

Scenario: B2B-8 (white-label theme) deferred from Sprint 1 → Sprint 2 (deprioritized by PO).

**Sprint 2 resume simulation:**

```
SPRINT STATE: Sprint 1 complete. Sprint 2 starting.
Next story: B2B-8 (DEFERRED from Sprint 1)
```

`[DEFERRED-RESUME: story=B2B-8 | labels=[fe/component, fe/a11y] | lessons scan: running before DO phase]`

Lessons scan: domain=fe/component, fe/a11y
→ Assume Sprint 1 generated LESSON: "WCAG criteria for complex interactive components (CRDT editor) need explicit keyboard trap testing — standard a11y checklist misses focus management in collaborative surfaces."

`[LESSONS APPLIED: keyboard trap testing in collaborative surfaces — source: Sprint 1 B2B-4] [Fix 29E triggered ✅]`

→ Loop spec for B2B-8 now includes criterion: "Collaborative editor keyboard trap: Tab does not trap in CRDT canvas. Focus moves to next focusable element."

---

## DEVELOP PHASE — B2B-2 (SSO/SAML 2.0)

### LOOP SPEC — B2B-2

```
▸ LOOP SPEC — B2B-2: SSO/SAML 2.0 integration

GOAL:
  SAML 2.0 SP-initiated flow completes against Okta sandbox. IdP metadata
  auto-configures from URL. JIT provisioning creates user on first login.

VERIFIER:
  - npm test -- --testPathPattern=auth/saml
  - npx semgrep --config=p/owasp-top-ten src/auth/
  - node scripts/saml_e2e_test.js --idp=okta-sandbox

CRITERIA:
  STRIDE-S: SAML response signature validated before user creation (score 1-10)
  be/auth: JIT provisioning maps SAML attributes to workspace roles (score 1-10)
  be/auth: SP metadata endpoint at /auth/saml/metadata returns valid XML (score 1-10)
  security-critical: XML external entity (XXE) attack blocked (score 1-10)
```

**⚠️ GAP CANDIDATE — 30D:** XXE on SAML XML parsing is a critical SAML-specific attack vector. The existing OWASP CHECKLIST file (owasp_top10.md covers A3: Injection broadly) but SAML-specific XXE is not guaranteed to be explicit in the checklist. The label [be/auth] does NOT resolve to any SAML-specific skill file. The security_engineer/auth_design.md file is HYBRID — but auth_design covers JWT/OAuth, not SAML. There is no `be/auth/saml_security.md` or similar. The criterion was written from engineer knowledge, not skill-sourced. **Label coverage gap: SAML-specific attack vectors have no dedicated skill file.**

`[VERIFIER OUTPUT: exit=0 | 19 SAML tests pass | XXE test: PASS (lxml with resolve_entities=False) | semgrep: 0 findings | pass=Y]`

Iteration 1:
- STRIDE-S: 10 | JIT provisioning: 9 | SP metadata: 10 | XXE blocked: 10
All ≥ 8.
`[LOOP CLOSED: B2B-2 | iter=1 | all criteria ≥8]`

---

## DEVELOP PHASE — B2B-4 (CRDT Real-time Collaboration)

### LOOP SPEC — B2B-4

```
▸ LOOP SPEC — B2B-4: CRDT real-time collaboration

GOAL:
  Two concurrent users editing the same document converge to identical state
  within 500ms of last edit. WebSocket disconnection triggers graceful
  offline merge on reconnect.

VERIFIER:
  - npm test -- --testPathPattern=crdt
  - npx tsc --noEmit

CRITERIA:
  be/resilience: concurrent edit convergence test: 1000 random ops → same final doc (score 1-10)
  be/resilience: reconnection merges offline changes without data loss (score 1-10)
  be/api: WebSocket auth — JWT validated on upgrade request (score 1-10)
  STRIDE-T: Yjs update payloads validated server-side (malformed ops rejected) (score 1-10)
```

**⚠️ GAP CANDIDATE — 30E:** The CRDT convergence VERIFIER (1000 random ops → same final doc) is a property-based test. The skill file `qa_engineer/property_based_testing.md` exists and is HYBRID. But property-based testing is NOT triggered by any current label. Labels [be/api, be/resilience, fe/component] don't resolve to property_based_testing.md in the skill index. This skill file is invisible for CRDT stories. **Label → skill gap: property-based testing skill not reachable from resilience labels.**

`[VERIFIER OUTPUT: exit=0 | 1000 op convergence: PASS | reconnect merge: PASS | JWT upgrade: PASS | malformed ops: PASS | pass=Y]`

Iteration 1: All ≥ 8.
`[LOOP CLOSED: B2B-4 | iter=1 | all criteria ≥8]`

---

## SM-RETRO — SCENARIO 3

`[TOKEN ESTIMATE: ~122K | Tier: DEGRADING (just over 120K)]`

**Lessons:**
- **LESSON-B2B-1:** SAML XXE is not covered by existing be/auth skill files. Need saml_security.md or add XXE criterion to auth_design.md HYBRID file.
- **LESSON-B2B-2:** Property-based testing (Hypothesis, fast-check) needed for CRDT/stateful protocol stories. Current label index doesn't route to property_based_testing.md from resilience labels.

### Gaps found:

| ID | Description | Severity |
|----|-------------|----------|
| **GAP-30D** | No SAML-specific skill file — SAML XXE, assertion replay, ACS validation not covered by be/auth label skills | 🔴 High |
| **GAP-30E** | property_based_testing.md not reachable from [be/resilience] label — CRDT/protocol stories miss this skill | 🟡 Medium |

---
---

# SCENARIO 4 — IoT / Edge Platform

**Prompt:** "Build an IoT platform — device management + MQTT telemetry streaming (10M devices) + edge compute (Kubernetes at edge) + OTA firmware updates + time-series analytics dashboard + alerting + device twin state sync + AWS IoT Core integration"

---

## STEP 0–3 — MODE DETECTION

Signals: platform(1), device management(2), MQTT(3), 10M devices(4), Kubernetes(5), OTA(6), analytics(7), AWS IoT(8).
Count: 8. → confidence=HIGH (99%)
`[MODE: 1 auto-inferred | confidence=HIGH (99%)]`

---

## THINK PHASE

### cto
Stack: AWS IoT Core (MQTT broker), TimescaleDB (time-series), Kafka (telemetry ingestion), Python FastAPI (device management API), React (dashboard), K3s (edge Kubernetes), Mender.io (OTA), InfluxDB (edge metrics), Telegraf (edge agent).

**ADR-001:** TimescaleDB over InfluxDB for cloud — SQL compatible, PostgreSQL extension, easier joins with device metadata.
**ADR-002:** K3s at edge over full K8s — 50% memory reduction, ARM-compatible for constrained devices.
**ADR-003:** AWS IoT Core as MQTT broker — handles device cert management, 10M device scale, DLQ built in.

### architect — STRIDE on MQTT/OTA trust boundaries

| Threat | Mitigation |
|--------|-----------|
| Spoofing (rogue device) | mTLS client cert per device, cert pinned at device |
| Tampering (firmware injection) | OTA packages signed, signature verified before flash |
| Repudiation (deny telemetry sent) | IoT Core message audit trail |
| Info Disclosure (telemetry sniff) | TLS 1.3 on MQTT, no plaintext broker |
| DoS (device flood) | Per-device publish rate limit in IoT Core policy |
| Elevation (device → admin API) | Device cert cannot call management API — separate auth domain |

`[STRIDE-BRIDGE: 6 mitigations → criteria queued]`

### DESIGN SYSTEM GATE (Fix 29A)
Dashboard = web app. design_system.md → NO.
**CREATION OWNERSHIP:** technical_writer + frontend_lead.

```
# Design System — IoT Command Center
Typography: IBM Plex Mono (data/telemetry values) + IBM Plex Sans (labels/navigation)
Color: Primary #0F172A (near-black base), Accent #22D3EE (cyan — live data, real-time)
      Alert: #F97316 (amber for degraded), Critical: #EF4444 (device offline/fault)
Layout: data-dense, terminal aesthetic. Monospace for all metric values.
Component Voice: "This is a command center, not a consumer dashboard. Operators need to see 10,000 device states at once. Dense, scannable, zero decoration."
```

`[DESIGN GATE: design_system.md locked.]`

---

## SM-PLAN

| Story | Labels |
|-------|--------|
| IOT-1 | Device registration + cert provisioning (AWS IoT Core) | be/api, be/auth, security-critical |
| IOT-2 | MQTT telemetry ingestion → Kafka pipeline | data/streaming, data/pipeline, be/api |
| IOT-3 | TimescaleDB time-series data model + ingest API | be/database, data/pipeline |
| IOT-4 | Device twin state sync (shadow document) | be/api, be/resilience |
| IOT-5 | OTA firmware update service (Mender integration) | be/api, devops/k8s, security-critical |
| IOT-6 | SLI/SLO design — device connectivity + telemetry freshness | devops/monitor |
| IOT-7 | Edge K3s deployment manifests + Helm chart | devops/k8s |
| IOT-8 | Analytics dashboard — fleet health + time-series charts | fe/component, fe/performance, data/eda |

**Co-maker check:** IOT-8 has [data/eda] → CO-MAKER triggers.
PRIMARY: data_scientist (analytics queries, anomaly detection spec)
SECONDARY: senior_engineer_fe (dashboard implementation)
CHECKER: qa_engineer

**⚠️ GAP CANDIDATE — 30F:** CO-MAKER pattern (Fix 26B) is defined as:
`PRIMARY=data_scientist, SECONDARY=senior_engineer_be`
But IOT-8 is a FRONTEND story — the SECONDARY should be `senior_engineer_fe`, not `senior_engineer_be`. The co-maker pattern in the hook hardcodes `senior_engineer_be` as secondary. For data/eda stories that produce a frontend dashboard (not a backend API), the secondary role should be `senior_engineer_fe`. **The co-maker role assignment is hardcoded and doesn't adapt to the story's lane (BE vs FE).**

### SRE — IOT-6 (SLI/SLO)

sre_engineer triggers on [devops/monitor] label.

```
▸ LOOP SPEC — IOT-6: SLI/SLO design — device connectivity + telemetry freshness

GOAL:
  SLI/SLO document defines: (1) device connectivity SLI (% of registered devices
  with last heartbeat < 5min), (2) telemetry freshness SLI (% of expected
  messages received within tolerance window). Error budgets defined for both.

VERIFIER:
  - python scripts/validate_slo_doc.py docs/slo/device_platform.md
  - cat docs/slo/device_platform.md | grep -E "error_budget|SLI|SLO" | wc -l (expect > 10)

CRITERIA:
  devops/monitor: SLI is measurable from existing metrics (TimescaleDB query provided) (score 1-10)
  devops/monitor: Error budget burn rate alert defined (score 1-10)
  devops/monitor: SLO window stated (rolling 28-day) (score 1-10)
```

`[VERIFIER OUTPUT: exit=0 | validate_slo_doc: PASS | grep count: 14 | pass=Y]`
Iteration 1: All ≥ 8.
`[LOOP CLOSED: IOT-6 | iter=1]`

---

## DEVELOP PHASE — IOT-2 (MQTT Telemetry Ingestion)

### LOOP SPEC — IOT-2

```
▸ LOOP SPEC — IOT-2: MQTT telemetry ingestion → Kafka pipeline

GOAL:
  AWS IoT Core rule routes MQTT messages to Kafka topic. Consumer processes
  10K msg/sec sustained. Schema validated (JSON Schema). Malformed messages
  sent to DLQ (not dropped silently).

VERIFIER:
  - pytest tests/telemetry/ -v
  - python scripts/load_test_kafka.py --rate 10000 --duration 60s
  - pytest tests/telemetry/test_dlq.py -v

CRITERIA:
  data/streaming: 10K msg/sec sustained without consumer lag > 5s (score 1-10)
  data/pipeline: schema validation rejects malformed messages → DLQ (score 1-10)
  data/pipeline: Kafka topic partitioned by device_id (consistent routing) (score 1-10)
  STRIDE-T: message payload validated before Kafka publish (no injection via telemetry) (score 1-10)
```

`[VERIFIER OUTPUT: exit=0 | throughput: 11,200 msg/sec | DLQ test: PASS | partitioning: PASS | schema: PASS | pass=Y]`

Iteration 1: All ≥ 8.
`[LOOP CLOSED: IOT-2 | iter=1]`

---

## DEVELOP PHASE — IOT-5 (OTA Firmware Update)

### LOOP SPEC — IOT-5

```
▸ LOOP SPEC — IOT-5: OTA Firmware Update Service

GOAL:
  OTA job targets device group. Firmware package uploaded, signed (Ed25519).
  Device downloads, verifies signature before flash. Failed update rolls back.
  Update progress tracked per-device.

VERIFIER:
  - pytest tests/ota/ -v
  - python scripts/verify_fw_signature.py --fw tests/fixtures/firmware.bin

CRITERIA:
  STRIDE-T: firmware signature verified on device before flash (score 1-10)
  security-critical: OTA job requires admin JWT (not device cert) (score 1-10)
  devops/k8s: rollback triggered on 3 consecutive failed device updates (score 1-10)
  be/api: job status endpoint paginated (1M devices in job) (score 1-10)
```

`[VERIFIER OUTPUT: exit=0 | OTA tests: 31 pass | signature verify: PASS | pass=Y]`

Iteration 1:
- STRIDE-T: 10 | admin JWT: 10 | rollback: 8 | pagination: 7 (cursor not implemented)

Iteration 2: Cursor-based pagination implemented. All ≥ 8.
`[LOOP CLOSED: IOT-5 | iter=2]`

---

## CONTEXT CHECK
`[TOKEN ESTIMATE: ~130K | Tier: DEGRADING]`
Compound DEGRADING warning (Fix 26F): IOT-3, IOT-4, IOT-5 all used 2 iterations.
`[COMPOUND-DEGRADING: streak=3 | remaining=3 stories | projected_critical=~155K. Options: (1) Fresh session. (2) Scope-cut IOT-7/8. (3) Continue with suppressed reloads.]`

→ Proceeding with suppressed reloads for IOT-7 (Helm chart) and IOT-8 (dashboard co-maker).

---

## IOT-8 — CO-MAKER (DUAL LOOP SPEC — WITH GAP)

`[CO-MAKER: data_scientist+senior_engineer_FE | story=IOT-8]`
→ Note: hook says `senior_engineer_be` but correct is `senior_engineer_fe` for FE stories. **GAP-30F fires here.**

```
▸ LOOP SPEC A — IOT-8-PRIMARY: Fleet Analytics — data_scientist
  GOAL: Anomaly detection on device telemetry identifies outlier devices (Z-score >3σ).
  VERIFIER: pytest tests/analytics/ -v
  CRITERIA: data/eda: anomaly correctly identifies top 1% outlier devices (score 1-10)
            data/ml: Z-score baseline recalibrates daily (score 1-10)

▸ LOOP SPEC B — IOT-8-SECONDARY: Dashboard — senior_engineer_fe
  GOAL: Fleet health dashboard renders 10K device dots in <2s. Anomalies highlighted.
  VERIFIER: npx jest --testPathPattern=dashboard | npx lighthouse --only-categories=performance
  CRITERIA: fe/performance: 10K device map renders <2s (score 1-10)
            fe/component: anomaly devices highlighted in red with tooltip (score 1-10)
```

**⚠️ GAP CANDIDATE — 30G:** IOT-8-SECONDARY VERIFIER uses Lighthouse for performance testing. Lighthouse is a browser tool — it requires a running app URL, not just npm test. If Lighthouse is not available in CI, this VERIFIER is BLOCKED:VERIFIER-UNEXECUTABLE. No documented fallback for browser-based VERIFIER tools in loop-engine.md. The existing BLOCKED path only covers "Bash tool unavailable" — not "Bash available but tool requires browser runtime."

Both loops close in 2 iterations. `[CO-MAKER DONE: IOT-8]`

---

## SM-RETRO — SCENARIO 4

`[TOKEN ESTIMATE: ~158K | Tier: approaching CRITICAL]`
`[SM-RETRO writes permitted at DEGRADING — completing now. (Fix 29D)]`

**Lessons:**
- **LESSON-IOT-1:** data/eda co-maker secondary role should be lane-aware (FE vs BE). Hook hardcodes be as secondary.
- **LESSON-IOT-2:** Browser-based VERIFIER tools (Lighthouse, Cypress) require running app URL — standard Bash execution not sufficient. Need VERIFIER type annotation or fallback criterion.

### Gaps found:

| ID | Description | Severity |
|----|-------------|----------|
| **GAP-30F** | Co-maker SECONDARY role hardcoded as `senior_engineer_be` — FE-lane co-maker stories need `senior_engineer_fe` as secondary | 🔴 High |
| **GAP-30G** | Browser-based VERIFIER tools (Lighthouse, Cypress) require running app, not just Bash exec — no fallback documented in loop-engine.md | 🟡 Medium |

---
---

# MASTER GAP SUMMARY — DRY RUN v3

| Gap | Source | Description | Severity | Fix Target |
|-----|--------|-------------|----------|-----------|
| **30A** | Scenario 1 (Healthcare) | Mobile platform-split VERIFIER — single loop spec for mobile/ios + mobile/android doesn't guarantee both platforms tested | 🟡 Medium | loop-engine.md |
| **30B** | Scenario 2 (FinTech) | CHECKLIST-heavy sprint early warning missing — no SM alert when sprint CHECKLIST token budget exceeds ~10K | 🟡 Medium | skill-label-index.md + team-orchestrator-sprint.md |
| **30C** | Scenario 2 (FinTech) | Load test VERIFIER dependency (k6/locust) — no fallback criterion if load test tool unavailable | 🟡 Medium | loop-engine.md |
| **30D** | Scenario 3 (B2B SaaS) | No SAML-specific skill file — SAML XXE, assertion replay, ACS binding not covered by any label | 🔴 High | kiro/skills/security_engineer/ + skill-label-index.md |
| **30E** | Scenario 3 (B2B SaaS) | property_based_testing.md not reachable from [be/resilience] — CRDT/stateful protocol stories miss it | 🟡 Medium | skill-label-index.md (add be/resilience → property_based_testing.md) |
| **30F** | Scenario 4 (IoT) | Co-maker SECONDARY hardcoded as `senior_engineer_be` — FE-lane stories need `senior_engineer_fe` | 🔴 High | kiro/hooks/elite-team-orchestrator.kiro.hook |
| **30G** | Scenario 4 (IoT) | Browser VERIFIER tools (Lighthouse, Cypress) need running app — no fallback in loop-engine.md | 🟡 Medium | loop-engine.md |

**Total: 7 new gaps (2 🔴 High, 5 🟡 Medium, 0 🟢 Low)**

---

## CROSS-SCENARIO SYSTEM HEALTH

| Fix | Scenario 1 | Scenario 2 | Scenario 3 | Scenario 4 |
|-----|-----------|-----------|-----------|-----------|
| **27A** Token tiers | ✅ PEAK→GOOD→DEGRADING correct | ✅ PEAK→DEGRADING | ✅ DEGRADING correct | ✅ DEGRADING+compound warning |
| **27B** Confidence gate | ✅ HIGH all 4 | ✅ HIGH | ✅ HIGH | ✅ HIGH |
| **27C** VERIFIER enforcement | ✅ Bash executed every story | ✅ Bash executed | ✅ Bash executed | ⚠️ Lighthouse gap (30G) |
| **28A** QUICK REF | ✅ Visible | ✅ Visible | ✅ Visible | ✅ Visible |
| **28B** Lessons scan | ✅ Logged (empty Sprint 1) | ✅ Logged | ✅ Logged | ✅ Logged |
| **28C** LOAD-TYPE | ✅ CHECKLIST full-loaded | ✅ CHECKLIST logged (29B fix) | ✅ Correct | ✅ Correct |
| **28D** Label validation | ✅ Self-challenge ran | ✅ Ran | ✅ Ran | ✅ Ran |
| **29A** Design gate owners | ✅ Owners assigned | ✅ Owners assigned | ✅ Owners assigned | ✅ Owners assigned |
| **29B** CHECKLIST token log | ✅ Split shown | ✅ Split shown | ✅ Split shown | ✅ Split shown |
| **29C** Dual loop spec | N/A (no co-maker) | ✅ FT-6 dual spec | N/A | ⚠️ FE secondary wrong (30F) |
| **29D** SM-RETRO at CRITICAL | ✅ Permitted | ✅ Permitted | ✅ Permitted | ✅ Permitted |
| **29E** Deferred lessons reload | N/A | N/A | ✅ B2B-8 fired correctly | N/A |

---

## SYSTEM COMPLIANCE ESTIMATE (post-Fix 29)

| Category | v6 Score | post-Fix 27 | post-Fix 28 | post-Fix 29 | post-Dry-Run v3 gaps |
|----------|---------|------------|------------|------------|---------------------|
| Mode detection | 45% | 82% | 82% | 82% | 82% |
| Token discipline | 30% | 78% | 78% | 82% | 82% |
| VERIFIER execution | 25% | 70% | 70% | 70% | 68% (30G degrades) |
| Skill coverage | 40% | 40% | 55% | 55% | 45% (30D/30E/30F gap) |
| Co-maker pattern | 50% | 50% | 55% | 65% | 58% (30F regression) |
| Lessons memory | 20% | 20% | 65% | 72% | 72% |
| Design gate | 35% | 35% | 35% | 80% | 80% |
| **Overall** | **59%** | **68%** | **73%** | **76%** | **74% (new gaps found)** |

New gaps (30D + 30F = 🔴 High) pull overall down from 76% to ~74%.
Fixing Fix 30 should push to ~82%.
