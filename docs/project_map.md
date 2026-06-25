# Project Map — Loop Engineering System

Module-level map of the kiro/ directory. Read this before any source file to orient without a wide scan.
Last updated: 2026-06-30

---

## Top-Level Structure

```
loopEngineering/
├── kiro/                        ← Kiro AI system root
│   ├── hooks/                   ← Active hooks (1 active, dead hooks deleted via Fix 13A)
│   ├── steering/                ← Always-loaded + manual-inclusion steering files
│   └── skills/                  ← 22 role directories, 261 skill files
├── docs/                        ← Cross-session memory + project artifacts
│   ├── lessons.md               ← Self-improvement log (confidence-scored)
│   ├── decisions.md             ← ADR index with temporal validity windows
│   ├── project_map.md           ← This file — workspace orientation
│   └── checkpoint.md            ← Session resume vectors
└── (user projects live outside this directory)
```

---

## kiro/hooks/

| File | Status | Purpose |
|------|--------|---------|
| `elite-team-orchestrator.kiro.hook` | ✅ ACTIVE (v3) | Thin router. Detects ENV, classifies request, loads steering files, delegates to team-orchestrator.md. ≤60-line prompt. |

Dead hooks (01-05, context-rot-detection, enforce-orchestrator-pipeline) — deleted 2026-06-30 via Fix 13A.

---

## kiro/steering/

| File | Inclusion | Lines | Purpose |
|------|-----------|-------|---------|
| `orchestrator-routing.md` | always | ~300 | ENV detection, TRACKER translation, mode routing, MANDATORY LOADS |
| `context-memory-discipline.md` | always | ~100 | Degradation tiers, read budget, ROT CHECK, goal anchor — canonical discipline source |
| `team-orchestrator.md` | manual | ~1,028 | Full constitution: 22 roles, artifact chain, gates, commit format, 6 phase-end reports |
| `skill-selection-matrix.md` | manual | ~326 | Role × activity → max 3 skill files. Step 0 existence check. Fix 9B protocol. |
| `loop-engine.md` | manual | ~200 | PLAN→DO→VERIFY→DECIDE loop. Maker/checker split. Stop conditions. |
| `discovery-engine.md` | manual | ~150 | 7 scoping questions → complexity score → mode recommendation |
| `memory-management.md` | fileMatch: init_docs/ | ~80 | Session-start memory load protocol |
| `phase-reporting.md` | fileMatch: docs/phase-*/ | ~60 | Phase artifact formatting rules |

---

## kiro/skills/ — 22 Roles

| Role | Files | Key skills |
|------|-------|-----------|
| `architect/` | 14 | system_design, api_design, adr_writing, microservices |
| `backend_lead/` | 15 | graphql_api, rest_api, async_patterns, loop_spec_authorship |
| `cloud_architect/` | 12 | vpc_design, landing_zone, iam_policies, multi_region |
| `cto/` | 12 | tech_strategy, build_vs_buy, risk_register, vendor_evaluation |
| `data_engineer/` | 7 | stream_processing_kafka, batch_pipeline_spark, dbt_transformation, airflow_dag, cdc, great_expectations |
| `data_scientist/` | 6 | eda, ab_test_analysis, cohort_retention, funnel_analysis, feature_engineering, data_storytelling |
| `database_architect/` | 17 | schema_design, migration_patterns, query_optimization, multi_tenancy |
| `devops_engineer/` | 13 | ci_cd_pipelines, docker_containerization, kubernetes, terraform |
| `finops_architect/` | 8 | unit_economics, cost_optimization, budget_guardrails |
| `frontend_lead/` | 14 | component_architecture, state_management, performance, a11y |
| `market_researcher/` | 10 | jtbd_research, competitive_analysis, tam_sam_som, positioning |
| `ml_engineer/` | 10 | model_selection, training_pipeline, inference_api, drift_monitoring |
| `mobile_engineer/` | 7 | ios_swiftui, android_jetpack_compose, react_native, offline_sync, push_notifications |
| `product_manager/` | 12 | prd_writing, user_story_mapping, acceptance_criteria, metrics |
| `qa_engineer/` | 12 | test_strategy, contract_testing, load_testing, security_testing |
| `scrum_master/` | 10 | prebuild_gate, sprint_planning, retro_facilitation, blocker_triage |
| `security_engineer/` | 21 | stride_threat_model, auth_design, secrets_management, owasp |
| `senior_engineer_be/` | 11 | clean_architecture, observability, dependency_injection + 8 shared |
| `senior_engineer_fe/` | 9 | react_performance, pwa, frontend_observability + 8 shared |
| `shared/` | 9 | code_review, concurrency_safety, debugging, error_handling, feature_flags, performance_profiling, refactoring, tdd, **design_system_gate** (prerequisite gate for all UI roles) |
| `sre_engineer/` | 11 | slo_design, incident_response, on_call_runbooks, chaos_engineering |
| `technical_writer/` | 9 | api_documentation, adr_index, runbook_writing, changelog |
| `website_creator/` | 24 | Split into 4 subdirs: seo/ (4), conversion/ (8), content/ (4), technical/ (7). Root has SKILL.md only. |

---

## docs/ — Cross-Session Memory

| File | Written by | Read at |
|------|-----------|--------|
| `lessons.md` | LLM at session end (when corrected or pattern identified) | Session start — orient before work |
| `decisions.md` | LLM when ADR filed or superseded | Session start — load binding constraints |
| `project_map.md` | LLM when dirs/files change | Before any source file read |
| `checkpoint.md` | LLM after every completed task | Session start — get resume vector |

**Session-end write protocol:**
1. Write checkpoint entry
2. If user corrected LLM → append to lessons.md (confidence: low)
3. If new ADR filed → append to decisions.md (valid_from: today, valid_to: present)
4. If prior decision superseded → update its valid_to field
5. If new files/dirs created → update this file

---

## Pending Fixes (summary — full detail in CLAUDE.md)

| Fix | Status | Description |
|-----|--------|-------------|
| Fix 12 | ✅ Done | Hook thin router, routing fixes, memory files, discipline source, goal anchor, 85% offloading |
| Fix 13 | ✅ Done | Dead hooks deleted, shared/ dedup, single discipline source, website_creator split, market_researcher re-invocation, temporal decisions, threshold offloading |
| Fix 14 | ✅ Done | design_system_gate.md created in shared/ (6 gate sections, anti-pattern reject list, output template); prerequisite rows added to matrix for website_creator, mobile_engineer, frontend_lead |
| Fix 15 | ✅ Done | impl-decisions.md in DEVELOP artifact chain + SM-GATE checklist; 4 report templates (DISCIPLINE, JIRA, GIT, MAPPING) added to GATE 5; Sprint Discipline Card prepended to SM-RETRO with blocking rule |
