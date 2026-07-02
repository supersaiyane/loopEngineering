---
inclusion: manual
---

# Skill Selection Matrix — Targeted Skill Loading

**Purpose:** Load ALL activity-relevant skill files, but compress each immediately to a 5-line takeaway. This gives full expertise coverage at lower context cost than loading a few full files.

**Rule:** When a role activates, the orchestrator selects skills based on the ACTIVITY being performed. Load every file in the matching matrix row. Compress each to a 5-line takeaway immediately after reading. Work from summaries. Re-load full content on-demand only for the one file needed during a specific protocol-heavy substep (e.g., OWASP checklist, WCAG audit).

---

## THINK PHASE — Skill Selection

### market_researcher
| Activity | Load These Skills (all matched) | On-demand (protocol-heavy substep) |
|----------|--------------------------------|--------------------------------------|
| Full market research | jtbd_interviews.md, competitive_teardown.md, market_sizing_tam_sam_som.md | positioning_april_dunford.md, pricing_van_westendorp.md |
| Competitive analysis only | competitive_teardown.md, positioning_april_dunford.md | others |
| Sizing only | market_sizing_tam_sam_som.md | others |
| Persona/JTBD focus | jtbd_interviews.md, positioning_april_dunford.md | others |
| Pricing strategy | pricing_van_westendorp.md, positioning_april_dunford.md | others |

### cto
| Activity | Load These Skills (all matched) | On-demand (protocol-heavy substep) |
|----------|--------------------------------|--------------------------------------|
| Full strategy | tech_strategy_framework.md, build_vs_buy_evaluation.md, tech_stack_selection.md | technical_debt_strategy.md, engineering_org_design.md, technical_due_diligence.md |
| Build-vs-buy decision | build_vs_buy_evaluation.md, tech_stack_selection.md | others |
| Tech debt discussion | technical_debt_strategy.md, tech_strategy_framework.md | others |
| Org design question | engineering_org_design.md | others |
| Due diligence | technical_due_diligence.md | others |
| API platform strategy | api_platform_strategy.md, developer_experience_dx.md | others |
| Developer experience | developer_experience_dx.md | others |
| Open source decision | open_source_strategy.md | others |

---

## DESIGN PHASE — Skill Selection

### product_manager
| Activity | Load These Skills | Skip |
|----------|------------------|------|
| Full PRD creation | prd_authoring.md, user_story_authoring.md, mvp_scope_definition.md | experiment, okrs, rice, north_star |
| Story writing only | user_story_authoring.md | others |
| Prioritization | rice_prioritization.md, north_star_metric.md | others |
| Scope definition | mvp_scope_definition.md, okrs_framework.md | others |

### architect
| Activity | Load These Skills | Skip |
|----------|------------------|------|
| Full system design | microservices_decomposition.md, domain_driven_design.md, project_structure_layout.md | others load on-demand |
| ADR writing | adr_authoring.md | others |
| Event-driven design | event_sourcing_cqrs.md, consistency_models_cap.md | others |
| Capacity planning | capacity_planning.md | others |
| Security architecture | stride_threat_modeling.md | others |
| Monolith design | domain_driven_design.md, project_structure_layout.md | microservices, event_sourcing |
| API gateway design | api_gateway_patterns.md | others |
| Service mesh decision | service_mesh_architecture.md | others |
| Clean architecture | hexagonal_architecture.md | others |
| Repo structure | monorepo_polyrepo_strategy.md | others |

### database_architect
| Activity | Load These Skills | Skip |
|----------|------------------|------|
| Initial schema design | normalization_vs_denormalization.md, index_design_query_plans.md, multi_tenancy_patterns.md | others |
| Migration planning | migration_strategies_online_offline.md | others |
| Scaling decisions | sharding_partitioning_strategies.md, read_replica_topology.md | others |
| Compliance/GDPR | retention_and_gdpr_deletion.md | others |
| Time-series data | time_series_schema_design.md | others |
| Data lake/warehouse | data_lake_lakehouse_design.md, olap_oltp_boundaries.md, cloud_data_pipelines_aws_azure_gcp.md | others |
| Vector/embedding store | vector_database_design.md | others |
| Graph data model | graph_database_design.md | others |
| NoSQL selection | nosql_patterns.md | others |
| Query performance | database_performance_tuning.md, index_design_query_plans.md | others |

### cloud_architect
| Activity | Load These Skills | Skip |
|----------|------------------|------|
| Initial cloud design | vpc_network_topology.md, landing_zone_design.md, iam_boundary_policies.md | others |
| Multi-region setup | multi_region_strategy.md, capacity_planning_quotas_limits.md | others |
| Cost optimization | finops_baseline.md | others |
| Security review | security_review_drives.md, iam_boundary_policies.md | others |
| Regulated industry | regulated_industry_architectures.md, well_architected_framework.md | others |

### finops_architect
| Activity | Load These Skills | Skip |
|----------|------------------|------|
| Initial cost model | cost_modeling_unit_economics.md, commitments_savings_plans_strategy.md | others |
| Budget alerts setup | anomaly_detection_budget_alerts.md | others |
| Chargeback model | chargeback_showback_models.md | others |
| Quarterly review | optimization_roadmap_quarterly.md | others |

### security_engineer (DESIGN pass)
| Activity | Load These Skills | Skip |
|----------|------------------|------|
| Threat modeling | threat_modeling_stride_pasta.md, zero_trust_architecture.md | others |
| Auth design | auth_design.md, identity_access_management_rbac_abac.md | others |
| Compliance mapping | compliance_soc2_iso_hipaa_pci.md, privacy_engineering_gdpr_ccpa.md | others |
| Data security | data_security_encryption_classification.md, cryptography_pki_key_management.md | others |


### security_engineer (DEVELOP pass — Fix 22D)

Scope for DEVELOP activations is NARROWER than DESIGN pass. Do NOT re-run full STRIDE.

| Activity | Load These Skills (all matched) | On-demand |
|----------|---------------------------------|-----------|
| Reviewing security-critical story implementation (executor, auth, PII handler, secrets) | shared/security_baseline.md, shared/code_review_checklist.md | secrets_management.md (if vault/env var check needed) |
| Checking if implementation matches DESIGN decision | [no skill file] — compare code to ADR directly. If deviation: flag + add new ADR. | — |
| New trust boundary discovered during DEVELOP | threat_modeling_stride_pasta.md (FULL LOAD — new boundary = mini-STRIDE required) | — |

**Rules for DEVELOP pass:**
1. Check: Does implementation match the ADR/design decision? If YES → done. If NO → flag deviation, add ADR.
2. Check S2: No NEW trust boundaries introduced without STRIDE. If new boundary found → run mini-STRIDE on that boundary only.
3. Check S3: Secrets in Vault, not env vars. PII scrubbed before storage/LLM.
4. Full re-STRIDE only if architecture changed materially (new service, new external integration).
5. Log: `[SECURITY REVIEW (DEVELOP): story=X | ADR match=YES/NO | new boundaries=N | S2=PASS/FLAG | S3=PASS/FLAG]`


### scrum_master
Note: SM activates in ONE mode per call (Fix 2). Mode determines which skills load.
| SM Mode (Fix 2) | Load These Skills (all matched) | On-demand (protocol-heavy substep) |
|-----------------|--------------------------|------|
| SM-GATE | prebuild_documentation_gate.md | all others |
| SM-PLAN | sprint_planning.md, velocity_capacity_modeling.md, estimation_techniques.md | all others |
| SM-RETRO | retrospective_facilitation.md, velocity_capacity_modeling.md | all others |
| SM-UNBLOCK | blocker_triage.md | all others |
| Cross-team dependencies | dependency_management.md | all others |
| Stakeholder update | stakeholder_communication.md | all others |

---

## DEVELOP PHASE — Skill Selection

### backend_lead
| Activity | Load These Skills | Skip |
|----------|------------------|------|
| API implementation plan | api_versioning.md, rate_limiting_algorithms.md, idempotency_patterns.md | others |
| Distributed systems | saga_pattern_distributed_transactions.md, outbox_pattern_event_publishing.md, circuit_breaker_bulkhead.md | others |
| Performance optimization | caching_strategies.md, rate_limiting_algorithms.md | others |
| Integration design | integration_contract_spec.md | others |
| Schema work | database_schema_design.md | others |
| Background jobs | async_job_queue_patterns.md | others |
| GraphQL API | graphql_api_design.md | others |
| Real-time / WebSocket | websocket_realtime_patterns.md | others |
| Service communication | microservices_communication.md | others |

### frontend_lead
| Activity | Load These Skills | Skip |
|----------|------------------|------|
| **[PREREQUISITE] DESIGN phase — any UI work** | **shared/design_system_gate.md FIRST** — /docs/design_system.md must exist before component code | — |
| Component architecture | component_decomposition.md, state_management_patterns.md | others |
| React/Next.js project | modern_react_nextjs_patterns.md, component_decomposition.md | others |
| Accessibility | wcag_accessibility.md | others |
| Performance | core_web_vitals.md, frontend_build_optimization.md | others |
| Design system | design_system_governance.md | others |
| Mobile strategy | mobile_development_strategy.md | others |
| Micro-frontends | micro_frontend_architecture.md | others |
| SSR/rendering strategy | server_side_rendering_strategies.md | others |
| Frontend testing plan | frontend_testing_strategy.md | others |
| Build optimization | frontend_build_optimization.md | others |

### senior_engineer_be
| Activity | Load These Skills | Skip |
|----------|------------------|------|
| Writing new feature code | shared/tdd_red_green_refactor.md, shared/error_handling_strategies.md | others |
| Fixing bugs | shared/debugging_methodology.md, shared/error_handling_strategies.md | others |
| Code review | shared/code_review_excellence.md | others |
| Concurrency work | shared/concurrency_safety.md | others |
| Refactoring | shared/refactoring_safely.md | others |
| Feature flags | shared/feature_flags_safely.md | others |
| Performance issue | shared/performance_profiling.md | others |
| Architecture for a service | clean_architecture.md, dependency_injection_patterns.md | others |
| Adding observability | observability_instrumentation.md | others |
| Implementing non-trivial story (algorithm choice, library selection, pattern decision) | [no skill file] — write entry in docs/phase-N/impl-decisions.md during DO step. Template in team-orchestrator-core.md Fix 15A (Fix 19 split). Mark entry [PROMOTE] if decision is reusable across projects OR deviates from a standard pattern. SM-RETRO GATE 4 will promote [PROMOTE] entries to ADR or lessons.md (Fix 22E). | all |

### senior_engineer_fe
| Activity | Load These Skills | Skip |
|----------|------------------|------|
| Writing new feature code | shared/tdd_red_green_refactor.md, shared/error_handling_strategies.md | others |
| Fixing bugs | shared/debugging_methodology.md, shared/error_handling_strategies.md | others |
| Code review | shared/code_review_excellence.md | others |
| Performance issue | shared/performance_profiling.md, react_performance_patterns.md | others |
| Refactoring | shared/refactoring_safely.md | others |
| Feature flags | shared/feature_flags_safely.md | others |
| React performance | react_performance_patterns.md | others |
| PWA implementation | progressive_web_app.md | others |
| Frontend monitoring | frontend_observability.md | others |

### ml_engineer
| Activity | Load These Skills | Skip |
|----------|------------------|------|
| RAG system | vector_search_rag_architecture.md, production_rag_at_scale.md, contextual_retrieval.md | others |
| Agent design | agent_design_tool_use.md, prompt_engineering_production.md | others |
| Memory system | agentic_memory_mem0.md, long_term_memory_systems.md, semantic_caching.md | others |
| MLOps/deployment | mlops_pipelines_deployment.md, ai_ml_testing_evals.md | others |
| Full ML system design | ai_ml_system_design.md, mlops_pipelines_deployment.md | others |
| Prompt optimization | prompt_optimization_dspy.md, prompt_engineering_production.md | others |
| Graph-based retrieval | graph_rag.md, vector_search_rag_architecture.md | others |
| Fine-tuning decision | fine_tuning_llms.md | others |
| Cost optimization | llm_cost_optimization.md | others |
| Multi-agent system | multi_agent_orchestration.md, agent_design_tool_use.md | others |
| Model evaluation | model_evaluation_benchmarking.md, ai_ml_testing_evals.md | others |

### qa_engineer
| Activity | Load These Skills | Skip |
|----------|------------------|------|
| Test strategy creation | property_based_testing.md, contract_testing.md, load_testing_methodology.md | others |
| Unit test focus | equivalence_partitioning.md, mutation_testing.md | others |
| API testing | contract_testing.md | others |
| Load/perf testing | load_testing_methodology.md | others |
| Exploratory testing | exploratory_testing_charters.md | others |
| Visual regression | visual_regression_testing.md | others |
| Test data setup | test_data_management.md | others |
| Accessibility audit | accessibility_testing.md | others |
| Implementing non-trivial story (algorithm choice, library selection, pattern decision) | [no skill file] — write entry in docs/phase-N/impl-decisions.md during DO step. Template in team-orchestrator-core.md Fix 15A (Fix 19 split). Mark entry [PROMOTE] if decision is reusable across projects OR deviates from a standard pattern. SM-RETRO GATE 4 will promote [PROMOTE] entries to ADR or lessons.md (Fix 22E). | all |

### security_engineer (DEVELOP pass — Gates S1, S2)
| Activity | Load These Skills | Skip |
|----------|------------------|------|
| GATE S1 (package approval) | supply_chain_sbom_slsa.md, vulnerability_management_cve_patching.md | others |
| GATE S1 — CVE flags a dep (Fix 43B) | vulnerability_management_cve_patching.md → write RDR, check same-rung alternatives, sign off on replacement rung before DEVELOP. Full protocol: docs/ponytail-rung-disqualification-guide.md | others |
| GATE S2 (feature review) | application_security_testing_sast_dast.md, api_security_owasp_top10.md, owasp_top10_review.md | others |
| GATE S2 — rung escalation review (Fix 43B) | Verify RDR exists + same-rung alternatives documented + ADR written + security sign-off present. Any missing → GATE S2 FAIL. Ref: docs/ponytail-rung-disqualification-guide.md | others |
| Secrets management | secrets_management.md | others |
| Container security | container_kubernetes_security.md | others |
| AI/ML security | ai_ml_security_prompt_injection.md | others |
| Incident response | incident_response_runbook.md, forensics_log_analysis_dfir.md | others |
| DevSecOps pipeline | secure_sdlc_devsecops.md | others |

### devops_engineer
| Activity | Load These Skills | Skip |
|----------|------------------|------|
| CI/CD pipeline setup | ci_cd_pipeline_design.md, twelve_factor_app.md | others |
| Deployment strategy | deployment_strategies.md | others |
| IaC/Terraform | iac_terraform_patterns.md | others |
| GitOps setup | gitops_argocd_flux.md | others |
| Platform engineering | platform_engineering_idp.md | others |
| Monitoring/alerting setup | monitoring_alerting_setup.md | others |
| DB migration in CI | database_migrations_cicd.md | others |
| Secrets management | secrets_management_cicd.md | others |

### sre_engineer
| Activity | Load These Skills | Skip |
|----------|------------------|------|
| SLI/SLO definition | sli_slo_design.md, error_budget_policy.md | others |
| Observability setup | observability_three_pillars.md | others |
| Incident handling | incident_command_system.md, blameless_postmortem.md | others |
| Chaos testing | chaos_engineering.md | others |
| Toil reduction | toil_reduction.md | others |
| On-call setup | on_call_management.md | others |
| Runbook creation | runbook_automation.md | others |
| Capacity planning | capacity_planning_sre.md | others |

### technical_writer
| Activity | Load These Skills | Skip |
|----------|------------------|------|
| API documentation | api_reference_authoring.md, diataxis_framework.md | others |
| Changelog/release notes | changelog_release_notes.md | others |
| Onboarding docs | onboarding_documentation.md, plain_language.md | others |
| Developer handoff | developer_handoff_kit.md | others |
| Leadership deck | leadership_deck_authoring.md, audience_adaptation.md | others |
| Sales deck | sales_demo_deck.md, audience_adaptation.md | others |
| SDK documentation | sdk_documentation.md | others |
| Troubleshooting guide | troubleshooting_guide_authoring.md | others |

### data_engineer
| Activity | Load These Skills | Skip |
|----------|------------------|------|
| Streaming pipeline | stream_processing_kafka.md | others |
| Batch ETL pipeline | batch_pipeline_spark.md | others |
| dbt/transformation | dbt_transformation_patterns.md | others |
| Airflow DAG design | airflow_dag_design.md | others |
| Pipeline testing | data_pipeline_testing.md | others |
| CDC setup | cdc_change_data_capture.md | others |
| Data quality | data_quality_great_expectations.md | others |
| Full pipeline design | stream_processing_kafka.md, airflow_dag_design.md, dbt_transformation_patterns.md | others |

### mobile_engineer
| Activity | Load These Skills | Skip |
|----------|------------------|------|
| **[PREREQUISITE] UI story — any screen/component** | **shared/design_system_gate.md FIRST** — /docs/design_system.md must exist before ios_swiftui_architecture.md or android_jetpack_compose.md activates | — |
| iOS feature | ios_swiftui_architecture.md | others |
| Android feature | android_jetpack_compose.md | others |
| React Native feature | react_native_patterns.md | others |
| Offline/sync design | mobile_offline_sync.md | others |
| Push notifications | push_notifications_deep_links.md | others |
| Performance issue | mobile_performance_profiling.md | others |
| App store release | app_store_deployment.md | others |

### data_scientist
<!-- Phase: LAUNCH (always) + DEVELOP (when story has [data/eda] label OR title contains A/B/experiment/statistical/EDA) — Fix 25N -->
| Activity | Load These Skills | Skip |
|----------|------------------|------|
| Initial data exploration | exploratory_data_analysis.md | others |
| A/B test analysis | ab_test_statistical_analysis.md | others |
| A/B model routing / experiment design (DEVELOP) | ab_test_statistical_analysis.md, exploratory_data_analysis.md | others |
| Retention analysis | cohort_retention_analysis.md | others |
| Funnel analysis | funnel_analysis.md | others |
| Feature engineering | feature_engineering.md | others |
| Stakeholder report | data_storytelling_visualization.md | others |
| Full analysis | exploratory_data_analysis.md, funnel_analysis.md, data_storytelling_visualization.md | others |

### website_creator
| Activity | Load These Skills | Skip |
|----------|------------------|------|
| **[PREREQUISITE] ALL UI activities** | **shared/design_system_gate.md FIRST** — /docs/design_system.md must exist before any other skill in this role loads | — |
| Landing page (structure + conversion) | conversion/landing_page_patterns.md, conversion/conversion_optimization.md, conversion/trust_signals_social_proof.md | others |
| Landing page (copy + messaging) | content/landing_page_copy.md, conversion/conversion_optimization.md, conversion/trust_signals_social_proof.md | others |
| SEO setup | seo/seo_foundations.md, seo/technical_seo_structured_data.md | others |
| Pricing page | conversion/pricing_page_design.md, conversion/conversion_psychology_principles.md | others |
| Analytics setup | seo/analytics_event_tracking_setup.md, conversion/ab_testing_experimentation.md | others |
| Forms/lead capture | conversion/forms_lead_capture_ux.md, conversion/conversion_optimization.md | others |
| Content strategy | content/content_marketing_strategy.md, content/case_study_customer_stories.md | others |
| Responsive/mobile | technical/responsive_design_mobile_first.md, technical/image_video_optimization.md | others |
| i18n/multi-language | seo/internationalization_seo_hreflang.md | others |
| Privacy/consent | technical/cookie_consent_privacy_ux.md | others |
| Growth/referral | conversion/growth_loops_referral_plg.md, content/email_marketing_automation.md | others |

---

## USAGE RULES

1. **First activation of a role in a project:** Load the "Full" set (typically 3-5 core skills)
2. **Subsequent activations:** Load ONLY skills relevant to the specific task. Second-pass (on-demand) files trigger when: (a) loop verifier scores the first-pass artifact < 7/10 on any skill-linked criterion, (b) user explicitly requests deeper analysis, (c) orchestrator identifies a named gap that maps to a specific second-pass file, or (d) SM-GATE returns RED on a criterion a second-pass file would address. Second-pass files count toward the per-activation budget. Max after second pass: ≤ 5 files total.
3. **Gate activities:** Load ONLY gate-specific skills (e.g., S1 = supply_chain + vulnerability)
4. **If unsure which skills apply:** Load the role's top 4 by filename relevance to the task description
4b. **Ambiguous activity match (2+ rows match the same task description):** Load the union of matched rows' skill files, deduplicated. No cap — compress all. If union exceeds 10 files, rank by keyword overlap and take top 10. Log: `[ACTIVITY MATCH: ambiguous — matched [row-A, row-B], loaded [file1, file2, ...], Σ~Ntok compressed]`.
5. **Never load all 20 files** for security_engineer — pick the 2-3 that match the activity
6. **Token budget (compressed):** Soft cap: total compressed skill context ≤ 2,000 tokens per role activation (~8-12 summaries). NO hard cap on file count. Log: `[SKILLS: role=X | activity=Y | files=A,B,C,D | Σ~Ntok compressed]`

---

---

## SKILL LABEL INDEX (Fix 24G — split out)

The label-indexed skill index and fallback rules have been moved to:
  **kiro/steering/skill-label-index.md**

Load trigger: SM-PLAN activation only (NOT at STEP 4).
This keeps mandatory-load cost at ~1,800 tok instead of ~6,500 tok.
