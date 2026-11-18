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
- backend_lead/scim_protocol.md  ← Fix 31G
- backend_lead/integration_contract_spec.md
- backend_lead/rate_limiting_algorithms.md: SCIM 2.0 protocol coverage (LOAD-TYPE: CHECKLIST) — load when story title contains SCIM/provisioning/directory-sync/deprovision

**be/caching**
- backend_lead/caching_strategies.md
- shared/performance_optimization.md
- ml_engineer/semantic_caching.md

**be/queue**
- backend_lead/async_job_queue_patterns.md
- backend_lead/outbox_pattern_event_publishing.md
- shared/distributed_systems_resilience.md
- architect/event_sourcing_cqrs.md
- shared/concurrency_safety.md

**be/database**
- backend_lead/database_schema_design.md
- database_architect/index_design_query_plans.md
- database_architect/database_performance_tuning.md
- database_architect/nosql_patterns.md
- database_architect/migration_strategies_online_offline.md
- database_architect/read_replica_topology.md
- shared/data_modeling_principles.md

**be/resilience**
- backend_lead/circuit_breaker_bulkhead.md
- backend_lead/saga_pattern_distributed_transactions.md
- shared/distributed_systems_resilience.md
- qa_engineer/property_based_testing.md  ← Fix 30E: CRDT/stateful protocol stories need property-based testing
- architect/consistency_models_cap.md
- shared/concurrency_safety.md

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
- ml_engineer/production_rag_at_scale.md
- ml_engineer/vector_search_rag_architecture.md
- security_engineer/ai_ml_security_prompt_injection.md

#### Frontend lane

**fe/component**
- frontend_lead/component_decomposition.md
- frontend_lead/modern_react_nextjs_patterns.md
- shared/design_system_gate.md
- frontend_lead/frontend_testing_strategy.md

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
- senior_engineer_fe/react_performance_patterns.md
- senior_engineer_fe/frontend_observability.md

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
- data_engineer/data_pipeline_testing.md

**data/streaming**
- data_engineer/stream_processing_kafka.md
- data_engineer/cdc_change_data_capture.md

**data/modeling**
- database_architect/normalization_vs_denormalization.md
- database_architect/sharding_partitioning_strategies.md
- database_architect/olap_oltp_boundaries.md
- shared/data_modeling_principles.md

**data/eda**
- data_scientist/exploratory_data_analysis.md  ← [FULL-LOAD preferred — rich analysis patterns]
- data_scientist/ab_test_statistical_analysis.md
- data_scientist/cohort_retention_analysis.md
- data_scientist/data_storytelling_visualization.md
- data_scientist/funnel_analysis.md
- shared/statistical_analysis_patterns.md

#### Security lane

**security/auth**
- security_engineer/auth_design.md  ← [FULL-LOAD-REQUIRED on STRIDE substep or new trust boundary]
- security_engineer/cryptography_pki_key_management.md
- security_engineer/identity_access_management_rbac_abac.md

**security/pii**
- security_engineer/data_security_encryption_classification.md
- database_architect/retention_and_gdpr_deletion.md
- shared/privacy_engineering.md
- security_engineer/privacy_engineering_gdpr_ccpa.md

**security/review**
- security_engineer/api_security_owasp_top10.md  ← [FULL-LOAD-REQUIRED]
- security_engineer/application_security_testing_sast_dast.md
- security_engineer/strix_pentest_methodology.md  ← Fix 34: Strix-derived pentest CHECKLIST (LOAD-TYPE: CHECKLIST, ~4,800 tok) — load for all security review stories
- security_engineer/owasp_top10_review.md
- security_engineer/threat_modeling_stride_pasta.md

**security/pentest**  ← Fix 34: active penetration testing stories
- security_engineer/strix_pentest_methodology.md  ← (LOAD-TYPE: CHECKLIST) — full Strix methodology: 8 vuln classes, toolchain, scan modes, validation protocol
- security_engineer/api_security_owasp_top10.md  ← [FULL-LOAD-REQUIRED]
  PENTEST SCAN MODE SELECTION (Fix 34): Read story context to select scan mode:
    story type=CI gate OR title contains (PR/pipeline/scan) → QUICK (5–10 min, Nuclei+Semgrep+Trivy)
    story type=security feature OR sprint=security → STANDARD (30–60 min, full vuln class probing)
    story type=audit OR sprint=hardening → DEEP (1–4 hr, full pentest + chaining)
  Log: `[PENTEST MODE: <QUICK|STANDARD|DEEP> | trigger=<story context>]`
- security_engineer/red_blue_purple_team_operations.md

**security/secrets**
- devops_engineer/secrets_management_cicd.md
- security_engineer/cryptography_pki_key_management.md

#### DevOps lane

**devops/k8s**
- devops_engineer/deployment_strategies.md
- devops_engineer/gitops_argocd_flux.md
- shared/infrastructure_as_code.md
- security_engineer/container_kubernetes_security.md

**devops/ci**
- devops_engineer/ci_cd_pipeline_design.md
- devops_engineer/gitops_argocd_flux.md
- devops_engineer/database_migrations_cicd.md
- security_engineer/secure_sdlc_devsecops.md

**devops/infra**
- devops_engineer/iac_terraform_patterns.md
- shared/infrastructure_as_code.md

**devops/monitor**
- devops_engineer/monitoring_alerting_setup.md
- sre_engineer/observability_three_pillars.md
- sre_engineer/sli_slo_design.md
- sre_engineer/error_budget_policy.md
- senior_engineer_fe/frontend_observability.md

#### Testing

**testing/unit**
- shared/tdd_red_green_refactor.md
- qa_engineer/property_based_testing.md
- qa_engineer/equivalence_partitioning.md
- qa_engineer/mutation_testing.md

**testing/integration**
- qa_engineer/test_data_management.md
- shared/tdd_red_green_refactor.md

**testing/e2e**
- qa_engineer/visual_regression_testing.md
- qa_engineer/exploratory_testing_charters.md
- frontend_lead/frontend_testing_strategy.md
- qa_engineer/web_app_testing.md  ← browser-based testing via claude-in-chrome (LOAD-TYPE: CHECKLIST)

**testing/web**
- qa_engineer/web_app_testing.md  ← (LOAD-TYPE: CHECKLIST) — console errors, network requests, functional happy path, screenshot evidence
- qa_engineer/visual_regression_testing.md
- qa_engineer/accessibility_testing.md

**testing/contract**
- qa_engineer/contract_testing.md

#### Cross-cutting

**impl-decision**
- shared/decision_record_template.md
- architect/adr_authoring.md
- architect/trd_template.md
- *(auto-creates docs/phase-N/impl-decisions.md entry — Fix 22E)*

**security-critical**
- security_engineer/api_security_owasp_top10.md  ← [FULL-LOAD-REQUIRED]
- architect/stride_threat_modeling.md  ← [FULL-LOAD-REQUIRED on new trust boundary] (Fix 25E: role=architect, not security_engineer)
- qa_engineer/property_based_testing.md  ← Fix 31H: ABAC/policy/crypto stories benefit from property-based test coverage
- security_engineer/threat_modeling_stride_pasta.md
- *(triggers security_engineer DEVELOP pass — Fix 22D)*

**cross-domain** (Fix 25K + 31C sub-types)
Sub-type resolution (check story title BEFORE loading skills):
  cross-domain/docs (default — doc/runbook/guide/wiki/spec in title):
    - shared/decision_record_template.md
    - shared/error_handling_strategies.md
    - technical_writer/audience_adaptation.md
    - technical_writer/changelog_release_notes.md
    - technical_writer/developer_handoff_kit.md
    - technical_writer/diataxis_framework.md
    - technical_writer/plain_language.md
    - *(technical_writer activation for doc stories)*
  cross-domain/tooling (Fix 31C — SDK/codegen/generator/CLI/scaffold in title):
    - backend_lead/api_versioning.md  ← SDK breaking-change detection criteria
    - shared/error_handling_strategies.md  ← generated error format standards
    - *(senior_engineer_be as primary maker for tooling stories)*
    - NOTE: add be/api label to tooling stories so idempotency + contract criteria also load
  cross-domain/both: story needs docs AND tooling → load both sets
- *(coordination artifact — criteria derive from sub-type above)*

#### Architecture lane

**arch/ddd**
- architect/domain_driven_design.md
- architect/hexagonal_architecture.md
- backend_lead/microservices_communication.md

**arch/microservices**
- architect/microservices_decomposition.md
- backend_lead/microservices_communication.md
- architect/service_mesh_architecture.md

**arch/monorepo**
- architect/monorepo_polyrepo_strategy.md
- architect/project_structure_layout.md

**arch/api-gateway**
- architect/api_gateway_patterns.md
- backend_lead/rate_limiting_algorithms.md

**arch/capacity**
- architect/capacity_planning.md
- cloud_architect/capacity_planning_quotas_limits.md

**arch/microfrontend**
- frontend_lead/micro_frontend_architecture.md
- frontend_lead/design_system_governance.md

**arch/zero-trust**
- security_engineer/zero_trust_architecture.md
- cloud_architect/iam_boundary_policies.md
- security_engineer/identity_access_management_rbac_abac.md

**arch/cqrs**
- architect/event_sourcing_cqrs.md
- backend_lead/outbox_pattern_event_publishing.md
- backend_lead/saga_pattern_distributed_transactions.md

**arch/refactor**
- architect/hexagonal_architecture.md
- devops_engineer/twelve_factor_app.md
- senior_engineer_be/clean_architecture.md
- shared/refactoring_safely.md

**arch/graph**  ← Fix 46A: product knowledge graph stories (new service, structural refactor, API addition)
- architect/product_graph_update.md  ← (LOAD-TYPE: CHECKLIST) — ARCHITECT GATE 5 merge protocol
- shared/graph_patch_emit.md  ← (LOAD-TYPE: CHECKLIST) — SE patch emission (load only when story adds structural nodes)

#### ML lane

**ml/agent**
- ml_engineer/agent_design_tool_use.md
- ml_engineer/agentic_memory_mem0.md
- ml_engineer/multi_agent_orchestration.md
- ml_engineer/long_term_memory_systems.md

**ml/rag**
- ml_engineer/production_rag_at_scale.md
- ml_engineer/graph_rag.md
- ml_engineer/vector_search_rag_architecture.md
- ml_engineer/semantic_caching.md
- ml_engineer/contextual_retrieval.md
- database_architect/vector_database_design.md

**ml/evals**
- ml_engineer/ai_ml_testing_evals.md
- ml_engineer/model_evaluation_benchmarking.md
- shared/statistical_analysis_patterns.md

**ml/fine-tuning**
- ml_engineer/fine_tuning_llms.md
- data_scientist/feature_engineering.md

**ml/mlops**
- ml_engineer/mlops_pipelines_deployment.md
- devops_engineer/ci_cd_pipeline_design.md

**ml/prompt**
- ml_engineer/prompt_engineering_production.md
- ml_engineer/prompt_optimization_dspy.md

**ml/cost**
- ml_engineer/llm_cost_optimization.md
- finops_architect/cost_modeling_unit_economics.md

#### Backend extras

**be/graphql**
- backend_lead/graphql_api_design.md
- backend_lead/api_versioning.md
- shared/api_versioning_strategy.md

**be/realtime**
- backend_lead/websocket_realtime_patterns.md
- shared/distributed_systems_resilience.md

**be/refactor**
- shared/refactoring_safely.md
- senior_engineer_be/clean_architecture.md
- senior_engineer_be/dependency_injection_patterns.md
- cto/technical_debt_strategy.md

**be/perf**
- shared/performance_optimization.md
- shared/performance_profiling.md
- senior_engineer_be/observability_instrumentation.md

#### Frontend extras

**fe/ssr**
- frontend_lead/server_side_rendering_strategies.md
- frontend_lead/modern_react_nextjs_patterns.md

**fe/pwa**
- senior_engineer_fe/progressive_web_app.md
- frontend_lead/mobile_development_strategy.md

**fe/design-system**
- frontend_lead/design_system_governance.md
- shared/design_system_gate.md

#### Database lane

**db/graph**
- database_architect/graph_database_design.md

**db/timeseries**
- database_architect/time_series_schema_design.md

**db/reliability**
- database_architect/backup_restore_rto_rpo.md
- database_architect/read_replica_topology.md
- database_architect/migration_strategies_online_offline.md
- sre_engineer/sli_slo_design.md

#### Cloud lane

**cloud/landing-zone**
- cloud_architect/landing_zone_design.md
- cloud_architect/well_architected_framework.md
- shared/infrastructure_as_code.md

**cloud/network**
- cloud_architect/vpc_network_topology.md
- shared/infrastructure_as_code.md

**cloud/multi-region**
- cloud_architect/multi_region_strategy.md
- database_architect/read_replica_topology.md

**cloud/review**
- cloud_architect/security_review_drives.md
- cloud_architect/well_architected_framework.md
- security_engineer/compliance_soc2_iso_hipaa_pci.md

**cloud/compliance**
- cloud_architect/regulated_industry_architectures.md
- security_engineer/compliance_soc2_iso_hipaa_pci.md
- security_engineer/vulnerability_management_cve_patching.md

**cloud/cost**
- cloud_architect/finops_baseline.md
- finops_architect/cost_modeling_unit_economics.md
- finops_architect/optimization_roadmap_quarterly.md

**cloud/capacity**
- cloud_architect/capacity_planning_quotas_limits.md
- architect/capacity_planning.md

**cloud/multi-cloud**
- cloud_architect/cross_cloud_multicloud_setup.md

#### FinOps lane

**finops/cost**
- finops_architect/cost_modeling_unit_economics.md
- cloud_architect/finops_baseline.md

**finops/alerts**
- finops_architect/anomaly_detection_budget_alerts.md

**finops/chargeback**
- finops_architect/chargeback_showback_models.md

**finops/savings**
- finops_architect/commitments_savings_plans_strategy.md

**finops/optimize**
- finops_architect/optimization_roadmap_quarterly.md

#### Security extras

**security/compliance**
- security_engineer/compliance_soc2_iso_hipaa_pci.md
- security_engineer/vulnerability_management_cve_patching.md
- cloud_architect/regulated_industry_architectures.md

**security/incident**
- security_engineer/incident_response_runbook.md
- security_engineer/forensics_log_analysis_dfir.md
- sre_engineer/blameless_postmortem.md
- sre_engineer/incident_command_system.md

**security/supply-chain**
- security_engineer/supply_chain_sbom_slsa.md

#### SRE lane

**sre/capacity**
- sre_engineer/capacity_planning_sre.md
- architect/capacity_planning.md
- cloud_architect/capacity_planning_quotas_limits.md

**sre/chaos**
- sre_engineer/chaos_engineering.md
- sre_engineer/error_budget_policy.md

**sre/incident**
- sre_engineer/incident_command_system.md
- sre_engineer/blameless_postmortem.md
- security_engineer/incident_response_runbook.md

**sre/oncall**
- sre_engineer/on_call_management.md
- sre_engineer/sli_slo_design.md
- sre_engineer/runbook_automation.md

**sre/runbook**
- sre_engineer/runbook_automation.md
- technical_writer/troubleshooting_guide_authoring.md

**sre/toil**
- sre_engineer/toil_reduction.md

#### DevOps extras

**devops/platform**
- devops_engineer/platform_engineering_idp.md
- cto/developer_experience_dx.md

**devops/feature-flags**
- shared/feature_flags_safely.md

#### Mobile extras

**mobile/release**
- mobile_engineer/app_store_deployment.md

**mobile/push**
- mobile_engineer/push_notifications_deep_links.md

#### Testing extras

**testing/load**
- qa_engineer/load_testing_methodology.md
- sre_engineer/capacity_planning_sre.md

#### Product lane

**product/prd**
- product_manager/prd_authoring.md
- cto/prd_template.md

**product/stories**
- product_manager/user_story_authoring.md

**product/mvp**
- product_manager/mvp_scope_definition.md
- cto/tech_stack_selection.md
- cto/build_vs_buy_evaluation.md

**product/prioritize**
- product_manager/rice_prioritization.md

**product/metrics**
- product_manager/north_star_metric.md
- data_scientist/cohort_retention_analysis.md
- data_scientist/funnel_analysis.md

**product/okrs**
- product_manager/okrs_framework.md

**product/experiment**
- product_manager/experiment_design_ab.md
- data_scientist/ab_test_statistical_analysis.md

**product/discovery**
- product_manager/continuous_discovery_habits.md
- market_researcher/jtbd_interviews.md
- cto/build_vs_buy_evaluation.md

#### Research lane

**research/competitive**
- market_researcher/competitive_teardown.md

**research/user**
- market_researcher/jtbd_interviews.md
- product_manager/continuous_discovery_habits.md

**research/market**
- market_researcher/market_sizing_tam_sam_som.md

**research/positioning**
- market_researcher/positioning_april_dunford.md

**research/pricing**
- market_researcher/pricing_van_westendorp.md

#### Web lane

**web/content**
- website_creator/content/content_marketing_strategy.md
- website_creator/content/landing_page_copy.md
- website_creator/content/case_study_customer_stories.md

**web/email**
- website_creator/content/email_marketing_automation.md

**web/conversion**
- website_creator/conversion/conversion_optimization.md
- website_creator/conversion/conversion_psychology_principles.md
- website_creator/conversion/landing_page_patterns.md
- website_creator/conversion/trust_signals_social_proof.md
- website_creator/conversion/forms_lead_capture_ux.md
- website_creator/conversion/pricing_page_design.md

**web/growth**
- website_creator/conversion/growth_loops_referral_plg.md
- website_creator/conversion/ab_testing_experimentation.md
- data_scientist/ab_test_statistical_analysis.md

**web/seo**
- website_creator/seo/seo_foundations.md
- website_creator/seo/technical_seo_structured_data.md
- website_creator/seo/internationalization_seo_hreflang.md
- website_creator/seo/analytics_event_tracking_setup.md

**web/technical**
- website_creator/technical/accessibility_wcag_2_2_aa.md
- website_creator/technical/responsive_design_mobile_first.md
- website_creator/technical/animation_choreography.md
- website_creator/technical/image_video_optimization.md
- website_creator/technical/web_typography_variable_fonts.md
- website_creator/technical/cms_headless_integration.md
- website_creator/technical/cookie_consent_privacy_ux.md

#### Docs lane

**docs/sdk**
- technical_writer/sdk_documentation.md
- technical_writer/api_reference_authoring.md

**docs/onboarding**
- technical_writer/onboarding_documentation.md

**docs/troubleshooting**
- technical_writer/troubleshooting_guide_authoring.md

**docs/leadership**
- technical_writer/leadership_deck_authoring.md
- scrum_master/stakeholder_communication.md
- scrum_master/sprint_artifacts.md  ← invoke pptx skill for stakeholder/review decks (LOAD-TYPE: HYBRID)

**docs/sprint**
- scrum_master/sprint_artifacts.md  ← (LOAD-TYPE: HYBRID) — pptx review deck, pdf retro report, xlsx velocity tracker
- scrum_master/velocity_capacity_modeling.md
- scrum_master/retrospective_facilitation.md

**docs/sales**
- technical_writer/sales_demo_deck.md

#### Data extras

**data/quality**
- data_engineer/data_quality_great_expectations.md

**data/analytics**
- data_scientist/cohort_retention_analysis.md
- data_scientist/funnel_analysis.md
- data_scientist/data_storytelling_visualization.md
- database_architect/olap_oltp_boundaries.md
- shared/statistical_analysis_patterns.md

**data/lake**
- database_architect/data_lake_lakehouse_design.md
- database_architect/cloud_data_pipelines_aws_azure_gcp.md


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
| technical_writer | cross-domain | technical_writer/plain_language.md + technical_writer/troubleshooting_guide_authoring.md (Fix 26C: cross-domain stories with doc/runbook titles load these) |
| scrum_master | docs/leadership | scrum_master/sprint_artifacts.md ← pptx/pdf/xlsx Anthropic document skills for sprint outputs |
| scrum_master | docs/sprint | scrum_master/sprint_artifacts.md + scrum_master/velocity_capacity_modeling.md |
| qa_engineer | testing/web | qa_engineer/web_app_testing.md (LOAD-TYPE: CHECKLIST) ← browser-based testing via claude-in-chrome |
| qa_engineer | testing/e2e | qa_engineer/web_app_testing.md (extend) — browser test checklist alongside exploratory charter |

---

### LABEL-BASED FALLBACK (Fix 23E)

When a story has no labels (pre-23B project, Mode 3 trivial build, or missed SM-PLAN):

```
1. Read story title + acceptance criteria (already in context — no file read needed)
2. Match key nouns/verbs against label keyword map:
   # ── Original 9 patterns ──────────────────────────────────────────
   'endpoint' | 'API' | 'POST/GET/PUT/PATCH' | 'route'        →  be/api
   'database' | 'migration' | 'schema' | 'ORM'                →  be/database
   'cache' | 'Redis' | 'TTL'                                   →  be/caching
   'component' | 'render' | 'CSS' | 'UI' | 'React'            →  fe/component
   'form' | 'input' | 'validation' | 'submit'                  →  fe/form
   'Kubernetes' | 'Helm' | 'deploy' | 'k8s'                   →  devops/k8s
   'pipeline' | 'ETL' | 'dbt' | 'batch'                       →  data/pipeline
   'test' | 'spec' | 'coverage' | 'mock'                       →  testing/unit
   'secret' | 'JWT' | 'OAuth' | 'token' | 'auth'              →  security/auth
   # ── Fix 47D: 82 new label patterns ───────────────────────────────
   # BE extras
   'GraphQL' | 'subscription' | 'resolver' | 'mutation'       →  be/graphql
   'WebSocket' | 'SSE' | 'real-time' | 'streaming'            →  be/realtime
   'queue' | 'Kafka' | 'SQS' | 'event' | 'message broker'     →  be/queue
   'refactor' | 'clean up' | 'tech debt' | 'decouple'         →  be/refactor
   'rate limit' | 'throttle' | 'quota'                         →  be/resilience
   'contract test' | 'OpenAPI' | 'integration spec'            →  be/api
   # Architecture
   'DDD' | 'domain' | 'bounded context' | 'aggregate'         →  arch/ddd
   'microservice' | 'service mesh' | 'decompose' | 'Istio'     →  arch/microservices
   'monorepo' | 'Nx' | 'Turborepo' | 'workspace'              →  arch/monorepo
   'event sourcing' | 'CQRS' | 'event store'                  →  arch/event-driven
   'ADR' | 'architecture decision' | 'architecture review'     →  arch/adr
   # ML / AI
   'RAG' | 'retrieval' | 'vector search' | 'embedding'        →  ml/rag
   'agent' | 'tool use' | 'orchestration' | 'LLM chain'       →  ml/agent
   'eval' | 'benchmark' | 'evaluation' | 'evals'              →  ml/evals
   'fine-tun' | 'LoRA' | 'PEFT' | 'SFT'                      →  ml/fine-tuning
   'prompt' | 'prompt engineer' | 'system prompt'              →  ml/prompt
   'model serv' | 'inference' | 'serving'                      →  ml/serving
   # Cloud / Infra
   'landing zone' | 'VPC' | 'cloud setup' | 'AWS org'         →  cloud/landing-zone
   'Terraform' | 'IaC' | 'Pulumi' | 'CloudFormation'          →  cloud/iac
   'multi-region' | 'DR' | 'disaster recovery' | 'failover'   →  cloud/multi-region
   'serverless' | 'Lambda' | 'Cloud Function' | 'FaaS'        →  cloud/serverless
   # FinOps
   'FinOps' | 'cost model' | 'chargeback' | 'showback'        →  finops/cost
   'reserved instance' | 'savings plan' | 'spot instance'      →  finops/cost
   # SRE
   'SLO' | 'SLI' | 'error budget' | 'reliability'             →  sre/oncall
   'chaos' | 'game day' | 'fault injection' | 'chaos eng'     →  sre/chaos
   'runbook' | 'on-call' | 'playbook' | 'incident'            →  sre/runbook
   'capacity plan' | 'traffic model' | 'load forecast'         →  sre/capacity
   # Product
   'PRD' | 'product requirements' | 'product spec'             →  product/prd
   'OKR' | 'north star' | 'key result' | 'objective'          →  product/okrs
   'roadmap' | 'feature prioritization' | 'backlog refinement' →  product/roadmap
   'user story' | 'story map' | 'story mapping'               →  product/stories
   # Market Research
   'market research' | 'competitive analysis' | 'JTBD'        →  research/market
   'user interview' | 'user research' | 'persona'              →  research/user
   # Web
   'SEO' | 'structured data' | 'hreflang' | 'sitemap'         →  web/seo
   'conversion' | 'CRO' | 'landing page' | 'A/B test'         →  web/conversion
   'accessibility' | 'WCAG' | 'a11y' | 'screen reader'        →  fe/a11y
   # Docs
   'SDK docs' | 'API reference' | 'developer docs'             →  docs/sdk
   'changelog' | 'release notes' | 'what\'s new'              →  docs/changelog
   'runbook doc' | 'operational guide' | 'ops doc'             →  docs/runbook
   # Data extras
   'OLAP' | 'data warehouse' | 'star schema' | 'dimensional'   →  data/modeling
   'EDA' | 'exploratory' | 'data analysis' | 'notebook'        →  data/eda
   'cohort' | 'retention' | 'funnel' | 'attribution'           →  data/eda
   # Security extras
   'RBAC' | 'ABAC' | 'IAM' | 'role' | 'permission'           →  security/auth
   'GDPR' | 'PII' | 'data privacy' | 'CCPA'                   →  security/pii
   'pentest' | 'penetration test' | 'red team'                 →  security/pentest
   'threat model' | 'STRIDE' | 'attack surface'               →  security/review
   # DevOps extras
   'CI/CD' | 'GitHub Actions' | 'pipeline' | 'build'          →  devops/ci
   'container' | 'Docker' | 'image' | 'registry'               →  devops/k8s
   'monitoring' | 'alerting' | 'Prometheus' | 'Grafana'        →  devops/monitor
   # Mobile
   'iOS' | 'Android' | 'React Native' | 'Flutter' | 'mobile'  →  mobile/crossplatform
   'App Store' | 'Play Store' | 'mobile release'              →  mobile/release
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
