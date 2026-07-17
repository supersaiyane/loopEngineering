# Dry Run 3-9 — All 7 Scenarios (Post-Fix-24 Gap Sweep)
**Date:** 2026-06-30
**Purpose:** Exhaust remaining unexercised agents/flows. Find all gaps before Fix 25 batch implementation.
**Key discovery:** skill-label-index.md has 26 filename mismatches vs actual files.

---

## LABEL INDEX MISMATCH MAP (26 wrong filenames — universal gap across all scenarios)

| Label | Index references (WRONG) | Actual file (CORRECT) | Role |
|-------|-------------------------|----------------------|------|
| be/api | api_design_restful.md | backend_lead/api_versioning.md + idempotency_patterns.md | backend_lead |
| be/caching | caching_strategies.md (be) | backend_lead/caching_strategies.md ✅ | backend_lead |
| be/queue | event_driven_architecture.md | backend_lead/async_job_queue_patterns.md + outbox_pattern_event_publishing.md | backend_lead |
| be/database | database_design_patterns.md | backend_lead/database_schema_design.md | backend_lead |
| be/resilience | circuit_breaker_patterns.md | backend_lead/circuit_breaker_bulkhead.md | backend_lead |
| be/auth | auth_patterns_jwt_oauth.md | security_engineer/auth_design.md | security_engineer |
| be/ml | ml_inference_serving.md | ml_engineer/ai_ml_system_design.md | ml_engineer |
| be/ml | embedding_strategies.md | ml_engineer/contextual_retrieval.md | ml_engineer |
| be/ml | vector_database_patterns.md | database_architect/vector_database_design.md | database_architect |
| data/streaming | streaming_architecture.md | data_engineer/stream_processing_kafka.md | data_engineer |
| data/pipeline | etl_batch_design.md | data_engineer/batch_pipeline_spark.md | data_engineer |
| security/auth | auth_patterns_jwt_oauth.md | security_engineer/auth_design.md | security_engineer |
| security/review | owasp_top10_checklist.md | security_engineer/api_security_owasp_top10.md | security_engineer |
| security-critical | stride_threat_model.md (security_engineer) | architect/stride_threat_modeling.md | architect |
| shared | security_baseline.md | DOES NOT EXIST — split across auth_design + api_security_owasp10 | — |
| shared | data_modeling_principles.md | DOES NOT EXIST — use database_architect/normalization_vs_denormalization.md | — |
| fe/component | component_architecture.md | frontend_lead/component_decomposition.md | frontend_lead |
| fe/state | state_management_patterns.md (fe) | frontend_lead/state_management_patterns.md ✅ | frontend_lead |
| fe/perf | web_performance_vitals.md | frontend_lead/core_web_vitals.md | frontend_lead |
| mobile/ios | ios_swift_patterns.md | mobile_engineer/ios_swiftui_architecture.md | mobile_engineer |
| mobile/android | android_kotlin_patterns.md | mobile_engineer/android_jetpack_compose.md | mobile_engineer |

---

## SCENARIO 8 — Loop Hard Stop
**Input:** "Build a distributed transaction saga with compensating transactions and eventual consistency guarantees"
**Mode:** 1 auto-inferred (distributed=signal, transaction=signal, consistency=signal ≥2) ✅

**Labels:** SAGA-1[be/resilience, impl-decision], SAGA-2[be/resilience, be/queue], SAGA-3[testing/integration]

**Skill resolution SAGA-2 (be/resilience, be/queue):**
  Index says: circuit_breaker_patterns.md, event_driven_architecture.md
  Reality: backend_lead/circuit_breaker_bulkhead.md ✅, backend_lead/async_job_queue_patterns.md ✅
  → Fix 23C filename mismatch fires (label index mismatch gap)

**Loop spec SAGA-2 criteria (be/resilience + be/queue):**
  C1: Compensating txn invoked on failure? C2: Idempotency on all saga steps?
  C3: Saga state persisted (not in-memory)? C4: At-least-once delivery? C5: DLQ on failed compensations?

**Iteration 1:** C1=6, C2=5, C3=4, C4=7, C5=3 → 5.0/10 → ACT
**DEGRADING fires** → max 1 ACT reload allowed (Fix 24F)
**Iteration 2 (post ACT):** C1=8, C2=8, C3=7, C4=8, C5=6 → 7.4/10 → below threshold, cannot ACT again
**Iterations 3-7:** marginal improvement only. C3→7, C5→6.5. Still <8.
**Iteration 8: HARD STOP**

**SM-UNBLOCK should activate:**
  GAP-S8A: SM-UNBLOCK receives loop-state HOW? No wiring from loop-engine.md to SM-UNBLOCK trigger.
           loop-state is in $TRACKER comment — SM-UNBLOCK must read it but trigger mechanism undefined.
  GAP-S8B: SM-UNBLOCK decision outcomes undefined:
           SCOPE-CUT: which parts cut? Does story split into done/not-done? Who updates $TRACKER?
           RE-SPEC: who rewrites loop spec? Does a fresh loop start (resetting iteration count)?
           ESCALATE: to whom? architect? user? What does escalation produce?
  GAP-S8C: Hard-stopped story impact on Sprint Discipline Card velocity: 0pts? partial credit? undefined.
  GAP-S8D: impl-decision entry for SAGA-1 (saga orchestrator choice) — created even if story never completes?
  GAP-S8E: DEGRADING + max 1 ACT = cannot converge when 2+ criteria fail. Fix 24F creates a trap:
           complex stories needing multiple ACT reloads are blocked by the 1-per-story rule at DEGRADING.

---

## SCENARIO 5 — Full Security Sprint
**Input:** "Refactor auth system to multi-tenant RBAC, rotate all secrets to Vault, and audit PII flows"
**Mode:** 1 auto-inferred (Vault=service, auth=system, PII=domain ≥2) ✅
**Memory:** domain=security lessons loaded → "JWT refresh rotation must be designed upfront" applies ✅

**Labels:** SEC-1[be/auth, security/auth, security-critical], SEC-2[security/secrets, devops/infra],
            SEC-3[be/pii, security/pii], SEC-4[testing/integration, security/review]

**Skill resolution SEC-1 (be/auth, security/auth, security-critical):**
  Index says: auth_patterns_jwt_oauth.md, shared/security_baseline.md, stride_threat_model.md(security_engineer)
  Reality: security_engineer/auth_design.md ✅, architect/stride_threat_modeling.md ✅, NO security_baseline.md
  GAP-S5A: shared/security_baseline.md doesn't exist — referenced in 8 label entries. Not a real file.

**Full STRIDE trigger for SEC-1:** New trust boundary (multi-tenant isolation) → FULL STRIDE fires ✅
  stride_threat_modeling.md is in architect/, not security_engineer/ → wrong role in Section 2 overrides.
  GAP-S5B: stride_threat_modeling.md owned by architect but label index puts it under security_engineer.
            security_engineer DEVELOP pass can't load a file it doesn't own via role-folder resolution.

**SEC-2 (security/secrets, devops/infra):**
  Index says: secrets_management.md(security_engineer), shared/infrastructure_as_code.md
  Reality: devops_engineer/secrets_management_cicd.md ✅, shared/infrastructure_as_code.md ✅

**SEC-3 (be/pii, security/pii):**
  Index says: pii_data_handling.md(senior_engineer_be), shared/privacy_engineering.md
  Reality: pii_data_handling.md DOES NOT EXIST. Closest: security_engineer/data_security_encryption_classification.md
           database_architect/retention_and_gdpr_deletion.md ✅, shared/privacy_engineering.md ✅
  GAP-S5C: pii_data_handling.md referenced in label index but doesn't exist in any role folder.

**GATE 4 — 4 ADR [PROMOTE] candidates in one sprint:**
  GAP-S5D: No limit or ordering rule on ADR promotions per sprint.
            4 promotions in one SM-RETRO = decisions.md grows unchecked. No dedup check against existing ADRs.

---

## SCENARIO 6 — DevOps/Infra Build
**Input:** "Set up Kubernetes cluster with Terraform, CI/CD pipeline, monitoring stack, and runbook documentation"
**Mode:** 1 auto-inferred (Kubernetes=infrastructure, Terraform=infrastructure, pipeline ≥2) ✅

**Labels:** INFRA-1[devops/k8s, devops/infra], INFRA-2[devops/infra, impl-decision],
            INFRA-3[devops/ci], INFRA-4[devops/monitor], INFRA-5[cross-domain] ← technical_writer

**Skill resolution — all devops labels:**
  Index says (wrong): kubernetes_deployment_patterns.md, observability_strategy.md, alerting_and_slo_design.md
  Reality: devops_engineer/deployment_strategies.md ✅, devops_engineer/gitops_argocd_flux.md ✅,
           devops_engineer/monitoring_alerting_setup.md ✅, sre_engineer/sli_slo_design.md ✅

**INFRA-5 (cross-domain) — technical_writer story:**
  GAP-S6A: cross-domain label = empty skill set in index. Story with ONLY cross-domain has no skills loaded.
  GAP-S6B: technical_writer trigger = "Sprint end" in hook trigger table.
            INFRA-5 is a mid-sprint documentation story. technical_writer never activates for it.
            No role picks up a pure documentation story mid-sprint.

**devops/monitor label resolution:**
  devops/monitor → monitoring_alerting_setup.md (devops_engineer) + sre_engineer files
  sre_engineer trigger = "Sprint end" — but monitoring stories need sre_engineer MID-SPRINT.
  GAP-S6C: sre_engineer fires only at sprint end. Monitoring, SLO, and chaos stories in DEVELOP never get sre_engineer expertise.

**GATE 5 question:**
  This sprint produces infrastructure artifacts (Helm charts, Terraform state, runbooks).
  Does GATE 5 (phase end) fire? What constitutes a "phase" vs a "sprint"?
  GAP-S6D: GATE 5 trigger condition undefined. No rule specifying when phase ends vs sprint ends.
            Infrastructure builds may need GATE 5 (phase review) but nothing routes to it.

---

## SCENARIO 3 — Mobile App
**Input:** "Build a cross-platform mobile app with offline-first sync, iOS and Android support, and contract tests"
**Mode:** 1 auto-inferred (app=platform, iOS=platform, Android=platform ≥2) ✅

**Labels:** MOB-1[mobile/rn, fe/component], MOB-2[mobile/ios], MOB-3[mobile/android],
            MOB-4[mobile/offline, be/database], MOB-5[testing/contract, be/api]

**Skill resolution MOB-2 (mobile/ios):**
  Index says: ios_swift_patterns.md → Reality: mobile_engineer/ios_swiftui_architecture.md ✅
**Skill resolution MOB-3 (mobile/android):**
  Index says: android_kotlin_patterns.md → Reality: mobile_engineer/android_jetpack_compose.md ✅
**Skill resolution MOB-5 (testing/contract):**
  Index says: contract_testing.md (qa_engineer) → Reality: qa_engineer/contract_testing.md ✅ CORRECT!

**DESIGN SYSTEM GATE fires:** mobile/* stories present → docs/design_system.md missing
  GAP-S3A: Design system gate doesn't distinguish web design system (component library)
            from mobile design system (iOS HIG, Material Design). Same gate, same requirement,
            but mobile apps need platform-specific design tokens, not a web component library.

**MOB-4 (mobile/offline):**
  mobile/offline → [shared/mobile_offline_sync.md ✅, conflict_resolution_patterns.md]
  GAP-S3B: conflict_resolution_patterns.md doesn't exist. mobile_offline_sync.md (shared) covers it partially
            but no dedicated conflict resolution skill file exists anywhere.

---

## SCENARIO 7 — Sprint 2 Continuation
**Input:** "Sprint 2: add payments integration, webhook system, and upgrade test coverage to 90%"
**Mode:** 1 auto-inferred (payments=service, integration=integration, webhook=service ≥2) ✅

**Sprint state detection (Fix 22F):** reads checkpoint.md LAST ROW ONLY
  Last row of current checkpoint.md = "Fix 25 added (PENDING)" — NOT a sprint entry.
  GAP-S7A: checkpoint.md mixes sprint state entries AND fix/implementation tracking entries in same table.
            Last row detection is unreliable — may read a fix entry instead of sprint entry.
            No separator, no type column, no sprint-only section. False "fresh build" detected.

**Memory load:** Prior lessons from Sprint 1 JWT/Dashboard projects:
  ADR: jsonwebtoken v9 is binding → PAY-1 uses Stripe HMAC-SHA256 for webhook sig — different mechanism.
  GAP-S7B: ADR binding constraints have no scope definition. JWT ADR may incorrectly constrain
            webhook signature validation (completely different auth mechanism, same "auth" domain tag).

**Lessons bleed:**
  "JWT refresh rotation must be designed upfront" (domain=security) loads for PAY-1.
  This lesson is from a different project entirely.
  GAP-S7C: lessons.md has no project namespace. Lessons from Project A load into Project B
            when same domain matches. No way to scope a lesson to a specific project.

---

## SCENARIO 4 — ML Recommendation Engine
**Input:** "Build a product recommendation engine with vector embeddings, model serving API, and A/B test framework"
**Mode:** 1 auto-inferred (API=service, model=system, embeddings=system ≥2) ✅

**Labels:** ML-1[be/ml, data/pipeline], ML-2[be/ml, be/api], ML-3[be/ml, be/database], ML-4[data/eda, testing/integration]

**Skill resolution be/ml:**
  Index says: ml_inference_serving.md, embedding_strategies.md, vector_database_patterns.md
  Reality: ml_engineer has NONE of these. Actual files are LLM-focused:
    agent_design_tool_use.md, agentic_memory_mem0.md, ai_ml_system_design.md, graph_rag.md etc.
  GAP-S4A: ml_engineer skill files are built for LLM/agent use cases, NOT traditional ML/embedding/model-serving.
            The be/ml label maps to the wrong conceptual space. vector_database_design.md is in database_architect.

**data/eda label — who activates?**
  Trigger table: data_engineer handles data/pipeline, data/streaming. data_scientist = LAUNCH only.
  ML-4 has data/eda label but no role in trigger table handles it mid-sprint.
  GAP-S4B: data/eda label has no DEVELOP-phase role assignment. data_scientist is LAUNCH-only.
            A/B test design, statistical analysis, and EDA stories have no owner in DEVELOP.

**data_scientist files exist (exploratory_data_analysis.md, ab_test_statistical_analysis.md ✅)**
  but data_scientist role cannot activate in DEVELOP — wasted files.
  GAP-S4C: data_scientist wired to LAUNCH phase only. ML builds need it in DEVELOP for experiment design,
            model evaluation, and statistical analysis of A/B tests.

---

## SCENARIO 9 — TRIVIAL
**Input A:** "Add a currency formatter utility function" (6 words, no BUILD keyword)
  STEP 0: ≤8 words AND no keyword → SKIP ALL STEPS → direct response
  GAP-S9A: "Add", "Fix", "Update", "Extend", "Insert", "Integrate", "Configure", "Deploy"
            are common build verbs missing from STEP 0 keyword list. These bypass all routing.
            "Add auth middleware" (3 words + "Add") → direct response, no Mode 3 routing, no tests.

**Input B:** "Create a currency formatter utility function" (6 words + CREATE)
  STEP 2: TRIVIAL ✅ → MODE 3 direct → senior_engineer executes
  Produces: utility function + unit tests
  Produces: Mode 3 Build Report
  GAP-S9B: Mode 3 Build Report format never defined anywhere in steering files.
            Hook says "Produce Mode 3 Build Report at end" but no template, no required sections,
            no file path, no role responsible. Each execution invents a different format.

---

## MASTER GAP SUMMARY

| ID | Category | Gap | Severity |
|----|----------|-----|----------|
| MASTER | Label index | 26 filename mismatches — index has invented names, not actual file names | 🔴 Critical |
| S5A | Missing shared | shared/security_baseline.md referenced in 8 labels — doesn't exist anywhere | 🔴 High |
| S8A | SM-UNBLOCK | No wiring from loop hard-stop to SM-UNBLOCK trigger — mechanism undefined | 🔴 High |
| S8B | SM-UNBLOCK | SCOPE-CUT/RE-SPEC/ESCALATE outcomes undefined | 🔴 High |
| S4B | Role gap | data/eda label has no DEVELOP-phase role — data_scientist LAUNCH-only | 🔴 High |
| S9A | Hook | "Add/Fix/Update/Extend/Integrate" missing from STEP 0 keyword list | 🔴 High |
| S8E | Loop | DEGRADING + max 1 ACT = cannot converge on multi-criteria failures | 🟡 Medium |
| S8C | Sprint card | Hard-stopped story velocity impact undefined | 🟡 Medium |
| S5B | Role conflict | stride_threat_modeling.md in architect/ but index assigns to security_engineer/ | 🟡 Medium |
| S5C | Missing file | pii_data_handling.md doesn't exist — be/pii and security/pii labels broken | 🟡 Medium |
| S5D | ADR flood | No limit/dedup rule on ADR promotions per sprint | 🟡 Medium |
| S6A | cross-domain | cross-domain label = empty skill set when story has no other labels | 🟡 Medium |
| S6B | Role trigger | technical_writer = Sprint end only — doc stories mid-sprint have no owner | 🟡 Medium |
| S6C | Role trigger | sre_engineer = Sprint end only — monitoring/SLO stories mid-sprint have no owner | 🟡 Medium |
| S6D | GATE 5 | GATE 5 trigger condition undefined — no rule for phase vs sprint end | 🟡 Medium |
| S7A | checkpoint | checkpoint.md mixes sprint state + fix tracking — last-row detection unreliable | 🟡 Medium |
| S7B | ADR scope | ADR binding has no domain scope — wrong-domain ADRs apply incorrectly | 🟡 Medium |
| S7C | Memory | lessons.md has no project namespace — lessons bleed across projects | 🟡 Medium |
| S4A | ml_engineer | ml_engineer files are LLM/agent focused — not traditional ML/embedding/serving | 🟡 Medium |
| S4C | data_scientist | data_scientist LAUNCH-only, needed in DEVELOP for ML/experiment stories | 🟡 Medium |
| S3A | Design gate | Design system gate doesn't distinguish web vs mobile design systems | 🟢 Minor |
| S3B | Missing file | conflict_resolution_patterns.md doesn't exist for mobile/offline | 🟢 Minor |
| S8D | Loop | impl-decision entry creation on hard-stopped story — undefined behavior | 🟢 Minor |
| S9B | Mode 3 | Mode 3 Build Report format/template never defined | 🟢 Minor |
