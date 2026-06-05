---
inclusion: manual
---

# Skill Label Index (Fix 23C / Fix 24G)
# Split from skill-selection-matrix.md to reduce mandatory-load token cost.
# Load trigger: SM-PLAN activation (when story labels are being assigned).
# DO NOT load at STEP 4 — loaded on demand at SM-PLAN time only.
# See: kiro/steering/skill-selection-matrix.md for SKILL LOADING PROTOCOL and per-role rows.

---

## LABEL-INDEXED SKILL INDEX (Fix 23C)

**This section is the primary skill resolution mechanism. Replace ACTIVITY text matching with label lookups.**

### How dynamic resolution works (per story):
```
1. Read story labels  →  [be/api, be/resilience]
2. Look up EACH label in Section 1 (SKILL INDEX) below  →  base skill set per label
3. Look up role in Section 2 (ROLE OVERRIDES) below  →  add role-specific files
4. Union ALL files from steps 2+3, deduplicate
5. For EACH file: check LOAD-TYPE annotation at file top (Fix 28C):
   NARRATIVE (default) → compress to 5-line takeaway
   CHECKLIST (<!-- LOAD-TYPE: CHECKLIST -->) → FULL-LOAD always, no compression
   HYBRID (<!-- LOAD-TYPE: HYBRID -->) → compress for context; full-load for specific substep
   CHECKLIST files do NOT count toward the 2,000 token soft cap
6. Log (Fix 29B — separate CHECKLIST cost): [SKILLS: labels=[X,Y] | role=Z | narrative=A,B ~Ntok compressed | checklist=C,D ~Ntok full-load | Total: ~Ntok]

7. SPRINT-LEVEL CHECKLIST BUDGET CHECK (Fix 30B — runs once at SM-PLAN completion):
   After all story skill loads are estimated, sum CHECKLIST-only tokens across all sprint stories.
   IF sprint CHECKLIST total > 10,000 tokens:
     → Emit: [SPRINT CHECKLIST BUDGET: ~NKtok full-load across M stories.
              Stories driving cost: <list story IDs with CHECKLIST labels>.
              Recommend: (1) fresh session at story 4+ OR (2) scope-cut checklist-heavy stories to Sprint 2.]
   IF sprint CHECKLIST total ≤ 10,000 tokens:
     → Log: [SPRINT CHECKLIST BUDGET: ~Ntok — within budget. No action needed.]
```

---

### Section 1 — SKILL INDEX (label → files, role-agnostic)

**PATH FORMAT NOTE:** Files with `<role>/` prefix resolve to `kiro/skills/<role>/<file>`.
Files with `shared/` prefix resolve to `kiro/skills/shared/<file>`.
Files with no prefix resolve via ACTIVATING ROLE folder (see SKILL LOADING PROTOCOL below).

#### Backend lane

**be/api**
- backend_lead/api_versioning.md
- backend_lead/idempotency_patterns.md
- shared/api_versioning_strategy.md
- shared/error_handling_strategies.md
- backend_lead/scim_protocol.md  ← Fix 31G: SCIM 2.0 protocol coverage (LOAD-TYPE: CHECKLIST) — load when story title contains SCIM/provisioning/directory-sync/deprovision

**be/caching**
- backend_lead/caching_strategies.md
- shared/performance_optimization.md

**be/queue**
- backend_lead/async_job_queue_patterns.md
- backend_lead/outbox_pattern_event_publishing.md
- shared/distributed_systems_resilience.md

**be/database**
- backend_lead/database_schema_design.md
- database_architect/index_design_query_plans.md

**be/resilience**
- backend_lead/circuit_breaker_bulkhead.md
- backend_lead/saga_pattern_distributed_transactions.md
- shared/distributed_systems_resilience.md
- qa_engineer/property_based_testing.md  ← Fix 30E: CRDT/stateful protocol stories need property-based testing

**be/auth**
- security_engineer/auth_design.md
- security_engineer/saml_security.md  ← Fix 30D: SAML XXE/replay/signature (LOAD-TYPE: CHECKLIST)
- security_engineer/webauthn_fido2.md  ← Fix 31F: WebAuthn/FIDO2/passkey coverage (LOAD-TYPE: CHECKLIST)
- shared/privacy_engineering.md
- AUTH CHECKLIST RESOLUTION (Fix 32J): BEFORE loading saml_security or webauthn_fido2, read /docs/foundation/security-posture.md Section 2:
    PRIMARY_AUTH = SAML 2.0 OR SSO_PROTOCOL = SAML 2.0 → load saml_security.md ONLY
    PRIMARY_AUTH = WebAuthn OR MFA_REQUIRED = WebAuthn → load webauthn_fido2.md ONLY
    PRIMARY_AUTH = OAuth 2.0 → load auth_design.md ONLY (no CHECKLIST needed)
    Both SAML + WebAuthn declared → load both (budget ~2,200 tok each)
    security-posture.md missing → default: load auth_design.md + emit [AUTH-POSTURE-MISSING: load saml+webauthn manually when posture doc is created]
  Log: `[AUTH-POSTURE: primary=<mechanism> → CHECKLIST: <files loaded>]`

**be/pii**
- security_engineer/data_security_encryption_classification.md
- database_architect/retention_and_gdpr_deletion.md
- shared/privacy_engineering.md

**be/ml**
- ml_engineer/ai_ml_system_design.md
- ml_engineer/contextual_retrieval.md
- ml_engineer/ml_serving_and_embeddings.md
- database_architect/vector_database_design.md

#### Frontend lane

**fe/component**
- frontend_lead/component_decomposition.md
- frontend_lead/modern_react_nextjs_patterns.md
- shared/design_system_gate.md

**fe/form**
- frontend_lead/component_decomposition.md
- frontend_lead/modern_react_nextjs_patterns.md

**fe/state**
- frontend_lead/state_management_patterns.md
- frontend_lead/modern_react_nextjs_patterns.md

**fe/a11y**
- frontend_lead/wcag_accessibility.md  ← [FULL-LOAD-REQUIRED on a11y audit substep]
- qa_engineer/accessibility_testing.md
- shared/design_system_gate.md

**fe/perf**
- frontend_lead/core_web_vitals.md
- frontend_lead/frontend_build_optimization.md
- shared/performance_optimization.md

#### Mobile lane

**mobile/ios**
- mobile_engineer/ios_swiftui_architecture.md
- shared/mobile_offline_sync.md

**mobile/android**
- mobile_engineer/android_jetpack_compose.md
- shared/mobile_offline_sync.md

**mobile/rn**
- mobile_engineer/react_native_patterns.md
- shared/mobile_offline_sync.md

**mobile/offline**
- mobile_engineer/mobile_offline_sync.md
- shared/mobile_offline_sync.md

#### Data lane

**data/pipeline**
- data_engineer/batch_pipeline_spark.md
- data_engineer/airflow_dag_design.md
- data_engineer/dbt_transformation_patterns.md
- database_architect/analytical_datastore_patterns.md  ← Fix 31D: ClickHouse/Cassandra/DynamoDB patterns (LOAD-TYPE: HYBRID) — load when story uses one of these engines

**data/streaming**
- data_engineer/stream_processing_kafka.md
- data_engineer/cdc_change_data_capture.md

**data/modeling**
- database_architect/normalization_vs_denormalization.md
- database_architect/sharding_partitioning_strategies.md

**data/eda**
- data_scientist/exploratory_data_analysis.md  ← [FULL-LOAD preferred — rich analysis patterns]
- data_scientist/ab_test_statistical_analysis.md

#### Security lane

**security/auth**
- security_engineer/auth_design.md  ← [FULL-LOAD-REQUIRED on STRIDE substep or new trust boundary]
- security_engineer/cryptography_pki_key_management.md

**security/pii**
- security_engineer/data_security_encryption_classification.md
- database_architect/retention_and_gdpr_deletion.md
- shared/privacy_engineering.md

**security/review**
- security_engineer/api_security_owasp_top10.md  ← [FULL-LOAD-REQUIRED]
- security_engineer/application_security_testing_sast_dast.md
- security_engineer/strix_pentest_methodology.md  ← Fix 34: Strix-derived pentest CHECKLIST (LOAD-TYPE: CHECKLIST, ~4,800 tok) — load for all security review stories

**security/pentest**  ← Fix 34: active penetration testing stories
- security_engineer/strix_pentest_methodology.md  ← (LOAD-TYPE: CHECKLIST) — full Strix methodology: 8 vuln classes, toolchain, scan modes, validation protocol
- security_engineer/api_security_owasp_top10.md  ← [FULL-LOAD-REQUIRED]
  PENTEST SCAN MODE SELECTION (Fix 34): Read story context to select scan mode:
    story type=CI gate OR title contains (PR/pipeline/scan) → QUICK (5–10 min, Nuclei+Semgrep+Trivy)
    story type=security feature OR sprint=security → STANDARD (30–60 min, full vuln class probing)
    story type=audit OR sprint=hardening → DEEP (1–4 hr, full pentest + chaining)
  Log: `[PENTEST MODE: <QUICK|STANDARD|DEEP> | trigger=<story context>]`

**security/secrets**
- devops_engineer/secrets_management_cicd.md
- security_engineer/cryptography_pki_key_management.md

#### DevOps lane

**devops/k8s**
- devops_engineer/deployment_strategies.md
- devops_engineer/gitops_argocd_flux.md
- shared/infrastructure_as_code.md

**devops/ci**
- devops_engineer/ci_cd_pipeline_design.md
- devops_engineer/gitops_argocd_flux.md

**devops/infra**
- devops_engineer/iac_terraform_patterns.md
- shared/infrastructure_as_code.md

**devops/monitor**
- devops_engineer/monitoring_alerting_setup.md
- sre_engineer/observability_three_pillars.md
- sre_engineer/sli_slo_design.md

#### Testing

**testing/unit**
- shared/tdd_red_green_refactor.md
- qa_engineer/property_based_testing.md

**testing/integration**
- qa_engineer/test_data_management.md
- shared/tdd_red_green_refactor.md

**testing/e2e**
- qa_engineer/visual_regression_testing.md
- qa_engineer/exploratory_testing_charters.md

**testing/contract**
- qa_engineer/contract_testing.md

#### Cross-cutting

**impl-decision**
- shared/decision_record_template.md
- *(auto-creates docs/phase-N/impl-decisions.md entry — Fix 22E)*

**security-critical**
- security_engineer/api_security_owasp_top10.md  ← [FULL-LOAD-REQUIRED]
- architect/stride_threat_modeling.md  ← [FULL-LOAD-REQUIRED on new trust boundary] (Fix 25E: role=architect, not security_engineer)
- qa_engineer/property_based_testing.md  ← Fix 31H: ABAC/policy/crypto stories benefit from property-based test coverage
- *(triggers security_engineer DEVELOP pass — Fix 22D)*

**cross-domain** (Fix 25K + 31C sub-types)
Sub-type resolution (check story title BEFORE loading skills):
  cross-domain/docs (default — doc/runbook/guide/wiki/spec in title):
    - shared/decision_record_template.md
    - shared/error_handling_strategies.md
    - *(technical_writer activation for doc stories)*
  cross-domain/tooling (Fix 31C — SDK/codegen/generator/CLI/scaffold in title):
    - backend_lead/api_versioning.md  ← SDK breaking-change detection criteria
    - shared/error_handling_strategies.md  ← generated error format standards
    - *(senior_engineer_be as primary maker for tooling stories)*
    - NOTE: add be/api label to tooling stories so idempotency + contract criteria also load
  cross-domain/both: story needs docs AND tooling → load both sets
- *(coordination artifact — criteria derive from sub-type above)*

---

### Section 2 — ROLE OVERRIDES (additions beyond Section 1 base)

Only delta from Section 1. Omitted role+label combos → use Section 1 as-is.
All filenames here use explicit `<role>/filename` format to avoid path ambiguity (Fix 25E).

| Role | Label | Additional files |
|------|-------|-----------------|
| senior_engineer_be | be/api | senior_engineer_be/clean_architecture.md + senior_engineer_be/dependency_injection_patterns.md |
| senior_engineer_be | be/resilience | senior_engineer_be/observability_instrumentation.md |
| senior_engineer_be | be/database | backend_lead/database_schema_design.md (already in Section 1) |
| senior_engineer_fe | fe/a11y | frontend_lead/wcag_accessibility.md ← [FULL-LOAD-REQUIRED] (already in Section 1) |
| senior_engineer_fe | fe/perf | frontend_lead/frontend_build_optimization.md (already in Section 1) |
| security_engineer | be/api | security_engineer/api_security_owasp_top10.md ← [FULL-LOAD-REQUIRED] |
| security_engineer | be/auth | security_engineer/cryptography_pki_key_management.md (already in Section 1) |
| architect | security-critical | architect/stride_threat_modeling.md ← [FULL-LOAD-REQUIRED] (Fix 25E: architect owns this, not security_engineer) |
| qa_engineer | (any be/*) | qa_engineer/contract_testing.md |
| qa_engineer | (any fe/*) | qa_engineer/visual_regression_testing.md + qa_engineer/accessibility_testing.md |
| devops_engineer | devops/k8s | devops_engineer/iac_terraform_patterns.md |
| data_engineer | data/pipeline | data_engineer/dbt_transformation_patterns.md (already in Section 1) |
| ml_engineer | be/ml | ml_engineer/ml_serving_and_embeddings.md (already in Section 1) |
| technical_writer | cross-domain | technical_writer/documentation_standards.md + technical_writer/runbook_template.md (Fix 26C: cross-domain stories with doc/runbook titles load these) |

---

### LABEL-BASED FALLBACK (Fix 23E)

When a story has no labels (pre-23B project, Mode 3 trivial build, or missed SM-PLAN):

```
1. Read story title + acceptance criteria (already in context — no file read needed)
2. Match key nouns/verbs against label keyword map:
   'endpoint' | 'API' | 'POST/GET/PUT/PATCH' | 'route'  →  be/api
   'database' | 'migration' | 'schema' | 'ORM'           →  be/database
   'cache' | 'Redis' | 'TTL'                              →  be/caching
   'component' | 'render' | 'CSS' | 'UI' | 'React'       →  fe/component
   'form' | 'input' | 'validation' | 'submit'            →  fe/form
   'Kubernetes' | 'Helm' | 'deploy' | 'k8s'              →  devops/k8s
   'pipeline' | 'ETL' | 'dbt' | 'batch'                 →  data/pipeline
   'test' | 'spec' | 'coverage' | 'mock'                 →  testing/unit
   'secret' | 'JWT' | 'OAuth' | 'token' | 'auth'         →  security/auth
3. Pick top 2 label matches → use as if explicit labels
4. Log: [SKILLS: labels=INFERRED([X,Y]) | role=Z | files=... — no explicit labels on story]
5. SM: add inferred labels to story retroactively
```

---

## SKILL LOADING PROTOCOL (for orchestrator to follow)

```
BEFORE activating any role:
0. VERIFY SKILL FILES EXIST — for each file, resolve path using these rules (Fix 24D):

   PATH RESOLUTION (in order):
   a. Prefix "shared/"  → kiro/skills/shared/<filename after "shared/">
   a2. Prefix matches a known role name (e.g. "backend_lead/", "security_engineer/", "architect/")
       → kiro/skills/<role>/<filename> — explicit role path, ignores activating role
   b. No prefix — resolve by ACTIVATING ROLE:
      senior_engineer_be → kiro/skills/senior_engineer_be/<filename>
      senior_engineer_fe → kiro/skills/senior_engineer_fe/<filename>
      security_engineer  → kiro/skills/security_engineer/<filename>
      qa_engineer        → kiro/skills/qa_engineer/<filename>
      devops_engineer    → kiro/skills/devops_engineer/<filename>
      data_engineer      → kiro/skills/data_engineer/<filename>
      ml_engineer        → kiro/skills/ml_engineer/<filename>
      architect          → kiro/skills/architect/<filename>
      backend_lead       → kiro/skills/backend_lead/<filename>
      frontend_lead      → kiro/skills/frontend_lead/<filename>
      mobile_engineer    → kiro/skills/mobile_engineer/<filename>
      data_scientist     → kiro/skills/data_scientist/<filename>
      database_architect → kiro/skills/database_architect/<filename>
      sre_engineer       → kiro/skills/sre_engineer/<filename>
      scrum_master       → kiro/skills/scrum_master/<filename>
      cto                → kiro/skills/cto/<filename>
      (any unlisted role → kiro/skills/<role_name>/<filename>)
   c. If not found at role path → fall back to kiro/skills/shared/<filename>
   d. If still not found → trigger Fix 21A warning
   Confirm file exists at resolved path. If missing:
     log: "[SKILL MISSING: <resolved path> — file not found]"
     fall back to role's top-level SKILL.md for context
       (for shared/ files: fall back to kiro/skills/shared/SKILL.md)
     add to sprint backlog: "Create skill file: <resolved path>"
   Do NOT halt execution. Do NOT silently substitute an unrelated file.
1. Identify the ACTIVITY (not just the role)
2. Look up activity in this matrix
3. Load ALL listed skill files for the matched activity row
4. If story has labels → use LABEL-INDEXED SKILL INDEX (Section 1+2 above). No labels → use LABEL-BASED FALLBACK (Fix 23E). Filename guessing BANNED.
5. For EACH file: check LOAD-TYPE annotation at file top (Fix 28C):
   NARRATIVE (default, no annotation) → compress to 5-line takeaway → discard full content
   CHECKLIST (<!-- LOAD-TYPE: CHECKLIST -->) → FULL-LOAD always, no compression
     Reason: checklists (OWASP A1-A10, WCAG criteria, STRIDE, crypto) lose all value when compressed
   HYBRID (<!-- LOAD-TYPE: HYBRID -->) → compress for context; full-load for specific protocol substep
   Work from compressed summaries (NARRATIVE) or full content (CHECKLIST). Soft cap: Σ compressed ≤ 2,000 tokens
   CHECKLIST files do NOT count toward the 2,000 token soft cap (they are protocol-required, not optional)
6. On-demand full load: for a specific protocol-heavy substep (e.g., OWASP check, WCAG audit),
   re-load that ONE file → execute substep → discard full content immediately
   Log: [SKILLS: role=X | activity=Y | files=A,B,C | Σ~Ntok compressed]
```

This protocol replaces the old "read ALL .md files in that folder" rule.
