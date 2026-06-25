---
date: 2026-07-01
scenario: Real-time Fraud Detection Platform
fixes-active: 1–28D
purpose: Validate Fix 27 + 28 behaviors under maximum system stress
---

# Dry Run v2 — Fraud Detection Platform (Post Fix 27 + 28)
**Scenario:** ML model serving + 50M tx/day Kafka streaming + React dashboard +
iOS/Android native + GDPR/PII compliance + Kubernetes GitOps + A/B testing framework

---

## PHASE 0 — SESSION START

Read docs/checkpoint.md → last row: `Fix 27+28 implemented | Type=FIX`
No SPRINT row found → fresh build (no proactive announcement — Fix 26E not triggered)

---

## PHASE 1 — MODE DETECTION (STEP 0 + STEP 3)

**Fix 27B: CONFIDENCE SCORING fires**

Signals scanned from prompt:
```
platform(1), ml-model-serving(2), kafka-streaming(3), kubernetes(4),
ab-testing(5), gdpr-pii(6), react-dashboard(7), ios-android-native(8)
```

Signal count = 8. Single sentence. Clear scope.
→ confidence = HIGH (95%)
→ No confirmation needed. Commit immediately.

`[MODE: 1 auto-inferred | confidence=HIGH (95%) | signals=8 | no user confirmation required]`

*Previous behavior (pre-Fix 27B):* would have committed at 2 signals with no confidence check.
*New behavior:* explicitly scores 95% → HIGH → proceeds. If this were "Build a real-time
notification feature" (2 signals, ambiguous scope) → MEDIUM (75%) → would PAUSE for confirmation.

**Fix 27A: Initial token estimate**
Mandatory files loaded: ~22,900 tokens
`[TOKEN ESTIMATE: ~23KB accumulated | Tier: PEAK (<60K)]`
Full ops mode — all reads, reloads allowed.

---

## PHASE 2 — MULTI-LANE DETECTION  [Fix 25C]

```
Detected ALL build lanes in prompt:
  be       → Kafka streaming, ML serving, fraud decision engine
  fe       → React dashboard
  mobile   → iOS/Android native
  data     → Kafka streaming (data/streaming), A/B testing (data/eda)
  security → GDPR/PII compliance
  devops   → Kubernetes GitOps

[LANES: be, fe, mobile, data, security, devops — all 6 lanes active]
Load lessons for ALL matched domains (Fix 25Q — project=fraud-detection-platform OR global)
```

---

## PHASE 3 — THINK

### CTO
- 50M tx/day = 578 tx/sec avg | peak ~1,500 tx/sec (2.6x avg)
- Infrastructure projection:
  - Kafka (3 brokers, 12 partitions): ~$3K/month
  - Kubernetes (EKS, 6 nodes): ~$5K/month
  - ML serving (GPU inference): ~$6K/month
  - 12-month infra total: ~$168K
- Risk flag: ML inference must be <100ms p99 for real-time decisioning
- Mobile: iOS + Android = 2 separate codebases → velocity impact flagged

### Architect → System Design + ADRs + STRIDE

**System topology:**
```
Payment Processor → [TB1] → Kafka (transactions.raw)
                                    ↓
                          Feature Extraction (Spark Streaming)
                                    ↓
                          ML Inference Service (gRPC) ← Feature Store
                                    ↓
                          Decision Engine (be/api)
                            ↙           ↘
              React Dashboard      iOS/Android App
              (WebSocket)          (Push notifications)
                    ↓
              GDPR Erasure Pipeline ← PII Store
```

**Trust Boundaries identified:**
- TB1: Payment processor → Kafka ingest (public → internal)
- TB2: Kafka → ML inference (internal stream)
- TB3: ML inference → Decision engine (microservice)
- TB4: Decision engine → Dashboard (API)
- TB5: PII Store → GDPR erasure pipeline (compliance)
- TB6: A/B testing service → ML models (experiment)

**STRIDE on TB1 (highest risk):**
```
T (Spoofing):     Unauthorized producers injecting fraudulent transactions
R (Repudiation):  No audit trail → transactions can't be traced to source
I (Info Disc):    Unencrypted messages expose PII in transit
D (DoS):          Producer flooding denies legitimate transaction processing
E (Elevation):    Misconfigured ACLs allow unauthorized topic creation
S (Stride):       mTLS + SASL required for all producer connections

Mitigations:
M1: TLS 1.3 + mTLS on all Kafka connections
M2: SASL/SCRAM authentication + per-topic ACLs
M3: Transaction ID uniqueness check in consumer (dedup)
M4: Producer rate limiting + circuit breaker at ingest
M5: Cryptographic message signing (Ed25519)
M6: Append-only ACL audit log (separate from broker logs)
```

**ADR-1:** Event sourcing via Kafka (Domain: be/queue, Scope: global)
→ Rejected: RabbitMQ (throughput limits at 50M/day), AWS SQS (p99 latency too high)

**ADR-2:** ML serving via gRPC + feature store (Domain: be/ml, Scope: service=ml-inference)
→ Rejected: REST (13ms avg overhead per call unacceptable at 578 rps), embedded model (CI/CD complexity)

`[ADR-PROMOTED: 2/2 this sprint — ADR flood limit reached. Any additional ADRs → [ADR-QUEUED]]`

### STRIDE-BRIDGE  [Fix 26D fires]

```
[STRIDE-BRIDGE: TB1 has 6 mitigations → distributing to affected stories]

FRAUD-1 (Kafka ingest):     +STRIDE-M1 criterion | +STRIDE-M2 criterion  (max 2/story)
FRAUD-3 (Security/GDPR):   +STRIDE-M5 criterion | +STRIDE-M6 criterion
FRAUD-5 (Decision engine):  +STRIDE-M3 criterion | +STRIDE-M4 criterion

[STRIDE-BRIDGE: 6 mitigations → 6 story criteria added to FRAUD-1, FRAUD-3, FRAUD-5]
```

*Previous behavior (pre-Fix 26D):* STRIDE output lived in architect artifact only — never reached story criteria.
*New behavior:* 6 criteria injected directly into loop specs of affected stories.

---

## PHASE 4 — GATE 1 + GATE 2

**GATE 2 Checklist:**
- [✅] ADR-1 + ADR-2 have Domain + Scope fields [Fix 25P]
- [✅] STRIDE-BRIDGE logged: 6 mitigations → 6 story criteria [Fix 26D]
- [✅] API contracts defined (gRPC proto for ML service, REST for decision engine)
- [✅] Schema DDL: transactions table, features table, decisions table, pii_subjects table

**DESIGN SYSTEM GATE  [Fix 25B fires]**
```
Project has web (React) AND mobile (iOS + Android):
  → Check: kiro/skills/shared/design_system.md → REQUIRED before Sprint 1 web stories
  → Check: kiro/skills/shared/design_system_mobile.md → REQUIRED before Sprint 1 mobile stories

VERDICT: BLOCKED — both design system files must exist before sprint start.
SM action: create design tokens + component library spec for web and mobile before FRAUD-8/9/10.
[GATE 2: DESIGN SYSTEM BLOCK — Sprint cannot start web/mobile stories until resolved]
```

Gap found → design_system.md + design_system_mobile.md created (pre-sprint). Gate passes.

---

## PHASE 5 — SM-PLAN: SPRINT 1 STORY LABELING

Stories planned:
```
FRAUD-1: Kafka transaction ingestion service
FRAUD-2: ML feature extraction pipeline
FRAUD-3: Security baseline + GDPR PII classification
FRAUD-4: Fraud decision engine (core BE)
FRAUD-5: Kubernetes GitOps foundation
```

**Label assignment + Fix 28D VALIDATION SELF-CHALLENGE fires on each story:**

```
FRAUD-1 assigned: [be/queue, security-critical]
  Self-challenge:
  → be/queue: adds async queue patterns + outbox skills. Unique? YES (not in security-critical)
  → security-critical: adds OWASP + STRIDE skills. Unique? YES (different from be/queue)
  [LABELS VALIDATED: FRAUD-1 | kept=[be/queue, security-critical] | removed=[] | reason=each adds distinct skill set]

FRAUD-2 assigned: [be/ml, data/pipeline, be/api]
  Self-challenge:
  → be/ml: adds ML serving + embedding skills. Unique? YES
  → data/pipeline: adds Spark + Airflow skills. Unique? YES
  → be/api: "What does be/api add that be/ml doesn't already cover?" → API design patterns
             But FRAUD-2 is ML pipeline, not an API story. Criterion overlap with be/ml high.
  → REMOVE be/api — redundant here.
  [LABELS VALIDATED: FRAUD-2 | kept=[be/ml, data/pipeline] | removed=[be/api] | reason=be/api adds no unique criterion for pipeline story]

FRAUD-3 assigned: [be/pii, security/pii, security-critical]
  Self-challenge:
  → be/pii: data encryption + retention. Unique? YES
  → security/pii: GDPR deletion + privacy engineering. Unique? YES (adds retention_and_gdpr_deletion.md)
  → security-critical: OWASP + STRIDE. Unique? YES
  [LABELS VALIDATED: FRAUD-3 | kept=[be/pii, security/pii, security-critical] | removed=[]]
```

*Previous behavior (pre-Fix 28D):* be/api on FRAUD-2 would have loaded wrong skills silently.
*New behavior:* self-challenge removes the redundant label before skill loading.

**Token estimate at DEVELOP start:**
`[TOKEN ESTIMATE: ~34KB accumulated | Tier: PEAK]`

---

## PHASE 6 — DEVELOP SPRINT 1

### FRAUD-1: Kafka Transaction Ingestion  [be/queue, security-critical]

**Fix 28B: LESSONS SCAN fires**
```
Scanning lessons.md for labels=[be/queue, security-critical]...
Project = fraud-detection-platform (first sprint)
[LESSONS: no match for labels=[be/queue, security-critical] — first sprint, no prior lessons]
Proceeding without lesson citations.
```

**Skill loading  [Fix 28C: LOAD-TYPE respected]:**
```
be/queue:
  backend_lead/async_job_queue_patterns.md        [NARRATIVE] → 5-line compress
  backend_lead/outbox_pattern_event_publishing.md  [NARRATIVE] → 5-line compress
  shared/distributed_systems_resilience.md         [NARRATIVE] → 5-line compress
security-critical:
  security_engineer/api_security_owasp_top10.md   [CHECKLIST] → FULL-LOAD (not compressed)
  architect/stride_threat_modeling.md              [CHECKLIST] → FULL-LOAD (not compressed)

[SKILLS: labels=[be/queue, security-critical] | role=senior_engineer_be | files=5
         CHECKLIST=2 FULL-LOAD | Σ~480tok compressed + 2 full-load (CHECKLIST exempt from cap)]
```

*Previous behavior (pre-Fix 28C):* OWASP checklist compressed to 5 lines → lost 90% of A1-A10 items.
*New behavior:* CHECKLIST annotation → full load → all 10 OWASP items available for CHECK scoring.

**Loop Spec — FRAUD-1  [STRIDE criteria injected via Fix 26D]:**
```
GOAL: Kafka consumer group reading transactions.raw topic.
      Throughput: 578 tx/sec avg, 1,500 tx/sec peak (50M/day).
      Exactly-once semantics. Dead-letter queue for poison messages.

VERIFIER (Fix 27C — MUST execute via Bash before CHECK):
  docker-compose up kafka zookeeper -d --wait
  npm test -- --coverage --testPathPattern=kafka
  npx jest kafka.integration.spec.ts --forceExit
  [VERIFIER OUTPUT required before any criterion score is written]

CRITERIA:
  1. [be/queue]         Exactly-once: idempotent producer + transactional consumer
  2. [be/queue]         DLQ: poison messages retried 3x then routed to .dlq topic
  3. [STRIDE-M1]        TLS 1.3 enforced on all Kafka connections (no plaintext fallback)
  4. [STRIDE-M2]        SASL/SCRAM + per-topic ACL (transactions.raw: producer-only)
  5. [STRIDE-M6]        ACL audit log: append-only, separate from broker logs
STOP WHEN: all ≥ 8
```

**Iteration 1:**
```
DO:  senior_engineer_be generates KafkaConsumerService with consumer group config
CHECK:
  [VERIFIER OUTPUT: exit=1 | stdout=7/9 tests passing | pass=N]
  Failing: exactly-once-semantics.spec.ts (idempotent producer missing)
           acl-audit-log.spec.ts (not implemented)
Scores: [1]=4 [2]=9 [3]=9 [4]=8 [5]=3
Two criteria <8 → ACT

[TOKEN ESTIMATE: ~42KB | Tier: PEAK — still full ops, Fix 27A means no suppression]
```

*Previous behavior (pre-Fix 27A):* would have hit DEGRADING at ~28KB and suppressed ACT reload.
*New behavior:* PEAK at 42KB → full reload allowed for lowest-scoring criterion.

```
ACT (1/2): reload backend_lead/async_job_queue_patterns.md → focus idempotent producer config
```

**Iteration 2:**
```
DO:  Add enable.idempotence=true + transactional.id + isolation.level=read_committed
CHECK:
  [VERIFIER OUTPUT: exit=1 | stdout=8/9 tests passing | pass=N]
  Still failing: acl-audit-log.spec.ts
Scores: [1]=9✅ [2]=9✅ [3]=9✅ [4]=8✅ [5]=3
One criterion <8 → ACT

ACT (2/2): reload security_engineer/api_security_owasp_top10.md [CHECKLIST: already full-loaded]
            → target A9:Security Logging section for audit log pattern
```

**Iteration 3:**
```
DO:  Implement AclAuditAppender (separate file, append-only, JSON structured logs)
CHECK:
  [VERIFIER OUTPUT: exit=0 | stdout=9/9 tests passing | pass=Y]
Scores: [1]=9✅ [2]=9✅ [3]=9✅ [4]=9✅ [5]=9✅
All ≥ 8 → STORY DONE ✅

[LOOP: FRAUD-1 | iters=3 | ACTs=2/2 (PEAK tier: reloads allowed) | all criteria ≥8]
[TOKEN ESTIMATE: ~52KB | Tier: PEAK]
```

---

### FRAUD-2: ML Feature Extraction Pipeline  [be/ml, data/pipeline]

**Fix 28B: LESSONS SCAN**
```
[LESSONS: no match for labels=[be/ml, data/pipeline] — no prior lessons this project]
```

**Skill loading  [Fix 28C]:**
```
7 NARRATIVE files → all compress to 5-line summaries
[SKILLS: labels=[be/ml, data/pipeline] | role=ml_engineer | files=7 | Σ~420tok compressed]
[TOKEN ESTIMATE: ~58KB | Tier: PEAK → approaching GOOD boundary at 60K]
```

Loop runs 2 iterations. Story completes.
`[TOKEN ESTIMATE: ~65KB | Tier: GOOD (crossed 60K)]`

---

### FRAUD-3: Security Baseline + GDPR PII  [be/pii, security/pii, security-critical]

**Fix 28B: LESSONS SCAN**
```
[LESSONS: no match for labels=[be/pii, security/pii, security-critical]]
```

**Skill loading  [Fix 28C]:**
```
security_engineer/data_security_encryption_classification.md  [CHECKLIST] → FULL-LOAD
database_architect/retention_and_gdpr_deletion.md             [NARRATIVE] → compress
shared/privacy_engineering.md                                 [NARRATIVE] → compress
security_engineer/api_security_owasp_top10.md                 [CHECKLIST] → FULL-LOAD (already in context)
[SKILLS: CHECKLIST=2 | Σ~180tok compressed + 2 full-load]
```

GDPR-BRIDGE: STRIDE-M5 (message signing) + STRIDE-M6 (audit trail) already injected as criteria.
Story completes in 2 iterations. `[TOKEN ESTIMATE: ~82KB | Tier: GOOD]`

---

### FRAUD-4: Fraud Decision Engine  [be/api, be/resilience]

**Fix 28B: LESSONS SCAN**
```
[LESSONS: no match for labels=[be/api, be/resilience]]
```

All NARRATIVE skills → compress. Story completes 2 iterations.
`[TOKEN ESTIMATE: ~97KB | Tier: GOOD]`

---

### FRAUD-5: Kubernetes GitOps Foundation  [devops/k8s, devops/ci]

`[TOKEN ESTIMATE: ~99KB | Tier: GOOD]`

**Fix 28B: LESSONS SCAN**
```
[LESSONS: no match for labels=[devops/k8s, devops/ci]]
```

**Fix 27A: Still GOOD (99KB < 120K) → full ops**

*Previous behavior (pre-Fix 27A):* would have hit DEGRADING at read-count 8+ and suppressed reloads.
*New behavior:* GOOD tier at 99KB → targeted reads OK, no suppression yet.

Skill loading: all NARRATIVE. HYBRID deployment_strategies.md → compress (GOOD tier).
Story completes 2 iterations.

`[TOKEN ESTIMATE: ~115KB | Tier: GOOD — approaching DEGRADING at 120K]`

**Sprint 1 complete. 5/5 stories done.**

---

## GATE 4 — SM-RETRO SPRINT 1

- Velocity: 5/5 ✅
- DoD: all stories with verified VERIFIER output (Fix 27C compliance ✅)

**Lessons write  [Fix 28B/25Q]:**
```
[LESSONS WRITE: project=fraud-detection-platform]

Domain: be/queue
  "Kafka exactly-once requires BOTH enable.idempotence=true on producer AND
   isolation.level=read_committed on consumer. Configuring one side only fails silently
   and is not caught by basic consumer tests — requires integration test with duplicated messages."
  Confidence: HIGH (discovered via red test → fix → green)

Domain: security-critical
  "ACL audit logs must use a separate append-only appender (not broker logs). Broker logs
   rotate and are not tamper-evident. Use structured JSON to support SIEM ingestion."
  Confidence: HIGH (STRIDE-M6 criterion required this explicitly)

Domain: devops/k8s
  "ArgoCD: set syncPolicy.automated.selfHeal=false for production namespaces by default.
   Self-healing in prod can override manual hotfixes during incidents."
  Confidence: MEDIUM
```

**ADR promotions  [Fix 25M]:**
- ADR-1 (Kafka) + ADR-2 (ML serving) → promoted (2/2 sprint limit reached ✅)
- No excess ADRs

**GATE 5 check  [Fix 25L]:**
Sprint 1 mod 3 = 1 ≠ 0 → no Gate 5
Proceed to Sprint 2.

**CHECKPOINT:**
`| 2026-07-01 | Sprint 1 complete — FRAUD-1..5 | ✅ | ... | docs/phase-1/sprint-plan.md | SPRINT |`

---

## SPRINT 2 SETUP

Stories:
```
FRAUD-6:  ML model serving (gRPC + feature store)        [be/ml, security-critical]
FRAUD-7:  A/B testing framework                          [data/eda, be/api]
FRAUD-8:  React dashboard (WebSocket + real-time alerts) [fe/component, fe/state, fe/perf]
FRAUD-9:  iOS native app                                 [mobile/ios]
FRAUD-10: Android native app                             [mobile/android]
```

`[TOKEN ESTIMATE: ~122KB | Tier: DEGRADING (crossed 120K after retro)]`

**Fix 27A fires — DEGRADING tier activated:**
```
[DEGRADING: entering Sprint 2 | token estimate ~122KB | 60% of 200K window used]
DEVELOP rules: skill reloads suppressed (max 2 ACTs/story, security-critical: max 3)
Log per story: [DEGRADING: story X — full skill reload suppressed | exception: security-critical]
```

*Previous behavior (pre-Fix 27A):* DEGRADING would have fired after story 2 of Sprint 1 (~28K).
*New behavior:* DEGRADING fires after ALL of Sprint 1 + SM-RETRO, at 60% window usage.
**Effective gain: 5 additional stories before suppression kicks in.**

---

### FRAUD-6: ML Model Serving  [be/ml, security-critical]

**Fix 28B: LESSONS SCAN fires — first lesson citation this session**
```
Scanning lessons.md for labels=[be/ml, security-critical]...
Project = fraud-detection-platform

[LESSON APPLIED: "ACL audit logs must use separate append-only appender"
  — source: Sprint 1, domain=security-critical]
Applying: ML serving endpoints need separate audit log for model version + inference decisions.

[LESSON APPLIED: none found for be/ml — no prior lessons]
```

*Previous behavior (pre-Fix 28B):* lessons.md loaded but never cited. Silent (possibly zero) application.
*New behavior:* explicit scan → explicit citation → auditable. ML serving endpoints get audit log requirement from Sprint 1 lesson.

Skill loading at DEGRADING:
```
be/ml: all NARRATIVE → compress (suppressed: no full-load at DEGRADING)
security-critical: api_security_owasp_top10.md [CHECKLIST] → FULL-LOAD (exception: security-critical)
[DEGRADING: FRAUD-6 | suppressed: be/ml full-loads | exception: security-critical CHECKLIST preserved]
```

Story completes. `[TOKEN ESTIMATE: ~135KB | Tier: DEGRADING]`

---

### FRAUD-7: A/B Testing Framework  [data/eda, be/api]

**Fix 26B: CO-MAKER PATTERN fires**
```
Labels: [data/eda, be/api]
Title contains: "A/B testing framework"
→ CO-MAKER PATTERN (Fix 26B) triggered:
  PRIMARY:   data_scientist    (experiment design, MDE calc, stat analysis, metrics spec)
  SECONDARY: senior_engineer_be (assignment service, variant logging, holdout implementation)
  CHECKER:   qa_engineer       (randomization validation, SUTVA check, holdout integrity)
[CO-MAKER: data_scientist+senior_engineer_be | story=FRAUD-7 | checker=qa_engineer]
```

**Fix 28B: LESSONS SCAN**
```
Scanning for labels=[data/eda, be/api]...
No prior lessons for data/eda. No additional lessons for be/api.
[LESSONS: no match for labels=[data/eda, be/api]]
```

Skill loading (PRIMARY — data_scientist):
```
data_scientist/exploratory_data_analysis.md    [FULL-LOAD preferred] → full load
data_scientist/ab_test_statistical_analysis.md [NARRATIVE] → compress
shared/statistical_analysis_patterns.md        [NARRATIVE] → compress
[SKILLS: data_scientist PRIMARY | 3 files | 1 full-load preferred]
```

Loop spec: data_scientist writes experiment design spec (MDE, power analysis, randomization unit).
SECONDARY senior_engineer_be implements assignment service + event logging.
CHECKER qa_engineer verifies K-S test on assignment distribution.

Story completes 3 iterations. `[TOKEN ESTIMATE: ~148KB | Tier: DEGRADING]`

---

### FRAUD-8: React Dashboard  [fe/component, fe/state, fe/perf]

`[TOKEN ESTIMATE: ~150KB | Tier: DEGRADING]`

**Fix 28B: LESSONS SCAN**
```
Scanning for labels=[fe/component, fe/state, fe/perf]...
No prior fe/* lessons this project.
[LESSONS: no match for labels=[fe/component, fe/state, fe/perf]]
```

Design system gate: design_system.md confirmed in context ✅

Iteration 1: score [fe/state]=5 (WebSocket reconnect logic missing). ACT 1/2 used.
Iteration 2: score [fe/perf]=6 (bundle size). ACT 2/2 used.
Iteration 3: all ≥8 → DONE.

`[TOKEN ESTIMATE: ~162KB | Tier: DEGRADING (approaching CRITICAL at 160K... just crossed)]`

**Fix 26F: COMPOUND DEGRADING WARNING fires**
```
FRAUD-6: used 2/2 ACTs at DEGRADING
FRAUD-8: used 2/2 ACTs at DEGRADING
Consecutive stories at max ACTs: 2

Pre-compute remaining: FRAUD-9 + FRAUD-10 = 2 stories
Projected tokens per story at DEGRADING: ~12K avg
Current: ~162KB | Remaining budget: ~38KB | 2 stories × 12K = 24K → fits but tight

[COMPOUND-DEGRADING: streak=2 | remaining=2 stories | projected_critical_in=~1 story]
Options surfaced to SM:
  (1) Fresh session before FRAUD-9 (safest)
  (2) Continue with SUPPRESSED reloads (risky for mobile-specific skills)
  (3) Scope-cut FRAUD-10 to Sprint 3 (deferred)
SM decision: Continue — mobile stories are lower complexity (native UI, no backend changes)
```

---

### FRAUD-9: iOS Native App  [mobile/ios]

**Fix 27A: Check tier**
`[TOKEN ESTIMATE: ~165KB | Tier: CRITICAL (crossed 160K)]`

**CRITICAL tier fires  [Fix 25D]:**
```
[CRITICAL TOKEN TIER — completing story FRAUD-9 only]
Stories remaining after FRAUD-9: 1 (FRAUD-10)
→ Fix 25D: stories remain → complete FRAUD-9 → STOP. Do not start FRAUD-10.
Emit: [CRITICAL: FRAUD-9 completing. FRAUD-10 deferred to fresh session.]
Recommend: fresh session before FRAUD-10.
```

FRAUD-9 completes (mobile stories are simpler, 1 iteration).
`[TOKEN ESTIMATE: ~172KB | Tier: CRITICAL]`

Write loop state to docs/phase-1/loop-states/FRAUD-9.md before stopping.
Write FRAUD-10 as PENDING in $TRACKER.

→ **STOP. Do not start FRAUD-10.**

---

## GATE 4 — SM-RETRO SPRINT 2 (partial — FRAUD-10 deferred)

**Note: SM-RETRO runs at CRITICAL  [Fix 25D — last completed story was FRAUD-9]**
RETRO is ~2K tokens (much cheaper than DEVELOP). Proceeds despite CRITICAL.

```
Velocity: 4/5 (FRAUD-10 deferred — not a BLOCK, a deferral due to token budget)
Discipline: FRAUD-7 A/B co-maker pattern executed correctly ✅
            FRAUD-8 design system gate confirmed ✅
```

**Lessons write at CRITICAL:**
```
[LESSONS WRITE at CRITICAL — writes proceed (SM-RETRO exception)]

Domain: data/eda
  "A/B test randomization unit must be the merchant_id NOT the transaction_id for fraud
   models — transaction-level randomization breaks SUTVA (stable unit treatment value assumption)
   when the same merchant appears in both control and treatment groups."
  Confidence: HIGH

Domain: mobile/ios
  "SwiftUI real-time data updates via WebSocket: use .task modifier + AsyncStream.
   Do NOT store URLSessionWebSocketTask in @StateObject — causes lifecycle issues on background/foreground."
  Confidence: HIGH
```

ADR promotions: ADR-3 (A/B framework statistical design) — 1 promotion (1/2 limit) ✅

**GATE 5 check  [Fix 25L]:**
Sprint 2 mod 3 = 2 ≠ 0 → no Gate 5.

**CHECKPOINT:**
`| 2026-07-01 | Sprint 2 partial — FRAUD-6..9 done, FRAUD-10 deferred | ... | SPRINT |`

---

## SESSION END + FIX 26E PROACTIVE ANNOUNCEMENT

Next session opens checkpoint.md → last SPRINT row = "Sprint 2 partial, FRAUD-10 PENDING"

**Fix 26E fires immediately:**
```
[RESUMING: Sprint 2 in-progress. Next story: FRAUD-10 (Android native app). 
 Token budget: fresh session (200K available).
 Type 'continue' to proceed or 'status' for full sprint state.]
```

*Previous behavior (pre-Fix 26E):* user would discover the state themselves.
*New behavior:* proactively surfaced before user types anything.

---

## FIX 27-28 BEHAVIOR SUMMARY

| Fix | Scenario where it fired | Behavior observed |
|-----|------------------------|-------------------|
| 27A (thresholds) | DEGRADING triggered at 122KB (Sprint 2 start) | Previously would fire at 28KB (Sprint 1 story 2). 5 extra stories before suppression. |
| 27A (PEAK zone) | FRAUD-1 iteration 2 at ~42KB | ACT reload allowed (old system: DEGRADING = suppressed). Quality improved. |
| 27B (confidence) | Mode 1 detection at session start | 8 signals → HIGH (95%) → no confirmation needed. Correct. |
| 27C (VERIFIER) | Every story CHECK phase | `[VERIFIER OUTPUT: exit=N | stdout=... | pass=Y/N]` required before scores. No imagined output. |
| 28A (QUICK REF) | Steering file loads | STRIDE-BRIDGE, co-maker, compound DEGRADING all cited from QUICK REF position. |
| 28B (lessons scan) | FRAUD-6 at Sprint 2 start | First lesson citation: Sprint 1 audit log lesson applied to ML serving endpoints. |
| 28C (LOAD-TYPE) | FRAUD-1, FRAUD-3, FRAUD-6 skill loading | OWASP, STRIDE, encryption classification: FULL-LOAD. All checklist items preserved. |
| 28D (label validation) | FRAUD-2 label assignment | be/api removed from pipeline story (redundant). Correct skills loaded for ML pipeline. |
| 26B (co-maker) | FRAUD-7 A/B testing | data_scientist PRIMARY / senior_engineer_be SECONDARY / qa_engineer CHECKER |
| 26F (compound warn) | After FRAUD-8 | 2-story streak warning surfaced. SM made informed decision to continue. |
| 25D (CRITICAL last) | After FRAUD-9 | CRITICAL fires → FRAUD-9 not last → STOP. FRAUD-10 deferred correctly. |
| 26E (proactive) | Fresh session resume | "[RESUMING: Sprint 2 in-progress. Next story: FRAUD-10]" emitted immediately. |

---

## GAPS FOUND — CANDIDATES FOR FIX 29

### Gap 29A — Design System Owner Not Specified (🔴 High)
**Observed:** GATE 2 blocked on design_system.md + design_system_mobile.md not existing.
The gate correctly blocks. But NO role is assigned to CREATE these files.
The system says "must exist before sprint start" but doesn't say which role creates them,
what the creation process is, or what constitutes a valid design system file.
In practice: gate fires → SM and user stare at each other.
**Fix:** Add design system creation step to THINK phase: technical_writer + frontend_lead (web)
or mobile_engineer (mobile) own design system bootstrapping. Add creation protocol to
design_system_gate.md skill file.

### Gap 29B — CHECKLIST Token Cost Not Estimated (🟡 Medium)
**Observed:** skill-label-index.md says "CHECKLIST files exempt from 2,000 token soft cap."
But OWASP full file = ~800 tokens. STRIDE full file = ~600 tokens. Two CHECKLIST files
= ~1,400 tokens ON TOP OF the compressed budget. At DEGRADING, this makes the actual
token consumption higher than estimated but the estimate ignores it.
**Fix:** Track CHECKLIST file token cost separately. Log:
`[SKILLS: Σ~480 compressed + ~1,400 CHECKLIST full-load | Total session add: ~1,880tok]`
This makes CHECKLIST cost visible in token estimates.

### Gap 29C — Co-maker Loop Spec Ownership Ambiguous (🟡 Medium)
**Observed:** FRAUD-7 A/B testing activated co-maker pattern. But loop spec has one VERIFIER
and one set of CRITERIA. The PRIMARY (data_scientist) writes the experiment design.
The SECONDARY (senior_engineer_be) implements the assignment service.
These are two different implementations with two different VERIFIER commands:
  - data_scientist VERIFIER: Python notebook output / stat test
  - senior_engineer_be VERIFIER: npm test for assignment service
But the loop spec only has ONE VERIFIER block. Conflict not resolved.
**Fix:** Co-maker stories get DUAL LOOP SPEC: one per role. PRIMARY loop spec (experiment
design criteria) and SECONDARY loop spec (implementation criteria). Both must pass for story DONE.

### Gap 29D — SM-RETRO Lessons Write at CRITICAL Not Explicitly Permitted (🟡 Medium)
**Observed:** Sprint 2 retro ran at CRITICAL tier. Lessons were written.
But context-memory-discipline.md says "At CRITICAL: PAUSE DEVELOP. Do not start next story."
It doesn't explicitly say "SM-RETRO writes are exempt from CRITICAL pause."
The Fix 25D last-story rule says "proceed to SM-RETRO" but the context discipline rules
could be read as blocking ALL writes at CRITICAL, including lessons.md writes.
**Fix:** Add explicit exception in CRITICAL tier rules: "SM-RETRO writes (lessons, checkpoint,
impl-decisions) are permitted at CRITICAL — they are low-token operations (~2K) and required
for session continuity."

### Gap 29E — FRAUD-10 Deferred But Not Re-Labeled for Next Session (🟢 Low)
**Observed:** FRAUD-10 deferred to fresh session. Written as PENDING in $TRACKER.
But in the fresh session, the new context won't have Sprint 2's lessons in context until
the session start reads checkpoint.md. The lessons from Sprint 2 (mobile/ios lesson) are
critical for FRAUD-10 (Android). The sprint-state detection (Fix 26E) announces "continue"
but doesn't trigger lessons reload for the deferred story's labels.
**Fix:** When resuming a deferred story, SM-PLAN re-runs lessons scan for that story's labels
before the first role activation. Proactive announcement includes:
"[RESUMING: Sprint 2 FRAUD-10. Labels=[mobile/android]. Applicable lessons will be loaded.]"

---

## DRY RUN VERDICT

**All Fix 27-28 behaviors fired correctly.**
**5 new gaps found → Fix 29 candidates (29A-29E).**

Key improvement over previous dry run (pre-Fix 27-28):
- DEGRADING fired at 122KB instead of 28KB → 5 more stories in PEAK tier
- CHECKLIST skills preserved at full fidelity (OWASP, STRIDE, encryption) 
- Label validation caught a spurious be/api label before wrong skills loaded
- Lessons from Sprint 1 were cited (not just loaded) in Sprint 2 role activations
- VERIFIER output explicitly required before scoring (no self-grading)
- Co-maker pattern fired for A/B testing story
- Compound DEGRADING warning gave SM visibility before hitting CRITICAL
