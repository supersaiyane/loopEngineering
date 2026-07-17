# Agent Skill Audit — Fix 47 Discovery
**Date:** 2026-07-17 · **Auditor:** Claude (automated cross-reference)

---

## Summary

| Metric | Count |
|--------|-------|
| Total skill files | 254 |
| Wired (have label trigger) | 81 |
| **Dead (zero triggers)** | **173** |
| Dead percentage | **68%** |
| Agents fully unwired | **6** |

**6 entire agent directories have zero coverage:** `cto`, `scrum_master`, `technical_writer`, `cloud_architect`, `finops_architect`, `product_manager`

---

## Agent-by-Agent Coverage

| Agent | Total | Wired | Dead | Coverage |
|-------|-------|-------|------|----------|
| security_engineer | 23 | 8 | 15 | 35% |
| ml_engineer | 18 | 4 | 14 | 22% |
| database_architect | 18 | 7 | 11 | 39% |
| technical_writer | 13 | 0 | **13** | **0%** |
| architect | 14 | 2 | 12 | 14% |
| website_creator | 19 | 0 | **19** | **0%** |
| cto | 10 | 0 | **10** | **0%** |
| cloud_architect | 10 | 0 | **10** | **0%** |
| scrum_master | 9 | 0 | **9** | **0%** |
| product_manager | 8 | 0 | **8** | **0%** |
| sre_engineer | 10 | 2 | 8 | 20% |
| shared/ | 19 | 11 | 8 | 58% |
| frontend_lead | 11 | 6 | 5 | 55% |
| market_researcher | 5 | 0 | **5** | **0%** |
| finops_architect | 5 | 0 | **5** | **0%** |
| backend_lead | 13 | 8 | 5 | 62% |
| data_scientist | 6 | 2 | 4 | 33% |
| mobile_engineer | 7 | 4 | 3 | 57% |
| qa_engineer | 10 | 6 | 4 | 60% |
| devops_engineer | 9 | 6 | 3 | 67% |
| senior_engineer_fe | 3 | 0 | 3 | 0% |
| data_engineer | 7 | 5 | 2 | 71% |
| senior_engineer_be | 3 | 2 | 1 | 67% |

---

## Complete Dead Skills List

### architect (12 dead)
| Skill file | Proposed trigger |
|-----------|-----------------|
| architect/adr_authoring.md | label: `arch/decision` or extend `impl-decision` |
| architect/api_gateway_patterns.md | label: `arch/api-gateway` (new) |
| architect/capacity_planning.md | label: `arch/capacity` (new) |
| architect/consistency_models_cap.md | extend existing: `be/resilience` |
| architect/domain_driven_design.md | label: `arch/ddd` (new) |
| architect/event_sourcing_cqrs.md | extend existing: `be/queue` |
| architect/hexagonal_architecture.md | THINK phase default (architect always) |
| architect/microservices_decomposition.md | label: `arch/microservices` (new) |
| architect/monorepo_polyrepo_strategy.md | label: `arch/monorepo` (new) |
| architect/project_structure_layout.md | THINK phase default (architect always) |
| architect/service_mesh_architecture.md | extend existing: `devops/k8s` |
| architect/trd_template.md | THINK phase default (architect always) |

### backend_lead (5 dead)
| Skill file | Proposed trigger |
|-----------|-----------------|
| backend_lead/graphql_api_design.md | label: `be/graphql` (new) |
| backend_lead/integration_contract_spec.md | extend existing: `be/api` |
| backend_lead/microservices_communication.md | extend existing: `be/resilience` |
| backend_lead/rate_limiting_algorithms.md | extend existing: `be/api` |
| backend_lead/websocket_realtime_patterns.md | label: `be/realtime` (new) |

### cloud_architect (10 dead — entire agent unwired)
| Skill file | Proposed trigger |
|-----------|-----------------|
| cloud_architect/landing_zone_design.md | label: `cloud/landing-zone` (new) |
| cloud_architect/vpc_network_topology.md | label: `cloud/network` (new) |
| cloud_architect/multi_region_strategy.md | label: `cloud/multi-region` (new) |
| cloud_architect/iam_boundary_policies.md | extend existing: `security/auth` |
| cloud_architect/well_architected_framework.md | label: `cloud/review` (new) |
| cloud_architect/regulated_industry_architectures.md | label: `cloud/compliance` (new) |
| cloud_architect/security_review_drives.md | extend existing: `security/review` |
| cloud_architect/finops_baseline.md | label: `cloud/cost` (new) |
| cloud_architect/cross_cloud_multicloud_setup.md | label: `cloud/multi-cloud` (new) |
| cloud_architect/capacity_planning_quotas_limits.md | label: `cloud/capacity` (new) |

### cto (10 dead — entire agent unwired)
| Skill file | Proposed trigger |
|-----------|-----------------|
| cto/prd_template.md | THINK phase default (CTO always) |
| cto/tech_strategy_framework.md | THINK phase default (CTO always) |
| cto/build_vs_buy_evaluation.md | THINK phase default (CTO always) |
| cto/tech_stack_selection.md | THINK phase default (CTO always) |
| cto/technical_debt_strategy.md | THINK phase default (CTO always) |
| cto/api_platform_strategy.md | label: `arch/api-gateway` or THINK phase |
| cto/developer_experience_dx.md | THINK phase default |
| cto/engineering_org_design.md | THINK phase default |
| cto/open_source_strategy.md | THINK phase default |
| cto/technical_due_diligence.md | THINK phase default |

### data_engineer (2 dead)
| Skill file | Proposed trigger |
|-----------|-----------------|
| data_engineer/data_pipeline_testing.md | extend existing: `data/pipeline` + label: `testing/data` |
| data_engineer/data_quality_great_expectations.md | label: `data/quality` (new) |

### data_scientist (4 dead)
| Skill file | Proposed trigger |
|-----------|-----------------|
| data_scientist/cohort_retention_analysis.md | extend existing: `data/eda` |
| data_scientist/data_storytelling_visualization.md | extend existing: `data/eda` |
| data_scientist/feature_engineering.md | extend existing: `be/ml` + `data/ml` |
| data_scientist/funnel_analysis.md | label: `data/analytics` (new) |

### database_architect (11 dead)
| Skill file | Proposed trigger |
|-----------|-----------------|
| database_architect/backup_restore_rto_rpo.md | label: `db/reliability` (new) |
| database_architect/cloud_data_pipelines_aws_azure_gcp.md | extend existing: `data/pipeline` |
| database_architect/data_lake_lakehouse_design.md | label: `data/lake` (new) |
| database_architect/database_performance_tuning.md | extend existing: `be/database` |
| database_architect/graph_database_design.md | label: `db/graph` (new) |
| database_architect/migration_strategies_online_offline.md | extend existing: `be/database` |
| database_architect/multi_tenancy_patterns.md | extend existing: `be/auth` (multi-tenant) |
| database_architect/nosql_patterns.md | extend existing: `be/database` |
| database_architect/olap_oltp_boundaries.md | extend existing: `data/modeling` |
| database_architect/read_replica_topology.md | extend existing: `be/database` |
| database_architect/time_series_schema_design.md | label: `db/timeseries` (new) |

### devops_engineer (3 dead)
| Skill file | Proposed trigger |
|-----------|-----------------|
| devops_engineer/database_migrations_cicd.md | extend existing: `devops/ci` + `be/database` |
| devops_engineer/platform_engineering_idp.md | label: `devops/platform` (new) |
| devops_engineer/twelve_factor_app.md | role default (devops_engineer always) |

### finops_architect (5 dead — entire agent unwired)
| Skill file | Proposed trigger |
|-----------|-----------------|
| finops_architect/cost_modeling_unit_economics.md | label: `finops/cost` (new) |
| finops_architect/anomaly_detection_budget_alerts.md | label: `finops/alerts` (new) |
| finops_architect/chargeback_showback_models.md | label: `finops/chargeback` (new) |
| finops_architect/commitments_savings_plans_strategy.md | label: `finops/savings` (new) |
| finops_architect/optimization_roadmap_quarterly.md | label: `finops/optimize` (new) |

### frontend_lead (5 dead)
| Skill file | Proposed trigger |
|-----------|-----------------|
| frontend_lead/design_system_governance.md | label: `fe/design-system` (new) or role default |
| frontend_lead/frontend_testing_strategy.md | role override: qa_engineer on any `fe/*` |
| frontend_lead/micro_frontend_architecture.md | label: `arch/microfrontend` (new) |
| frontend_lead/mobile_development_strategy.md | extend existing: `mobile/*` labels |
| frontend_lead/server_side_rendering_strategies.md | label: `fe/ssr` (new) |

### market_researcher (5 dead — entire agent unwired)
| Skill file | Proposed trigger |
|-----------|-----------------|
| market_researcher/competitive_teardown.md | label: `research/competitive` (new) |
| market_researcher/jtbd_interviews.md | label: `research/user` (new) |
| market_researcher/market_sizing_tam_sam_som.md | label: `research/market` (new) |
| market_researcher/positioning_april_dunford.md | label: `research/positioning` (new) |
| market_researcher/pricing_van_westendorp.md | label: `research/pricing` (new) |

### ml_engineer (14 dead)
| Skill file | Proposed trigger |
|-----------|-----------------|
| ml_engineer/agent_design_tool_use.md | label: `ml/agent` (new) |
| ml_engineer/agentic_memory_mem0.md | extend: `ml/agent` |
| ml_engineer/ai_ml_testing_evals.md | label: `ml/evals` (new) |
| ml_engineer/fine_tuning_llms.md | label: `ml/fine-tuning` (new) |
| ml_engineer/graph_rag.md | label: `ml/rag` (new) |
| ml_engineer/llm_cost_optimization.md | label: `ml/cost` (new) |
| ml_engineer/long_term_memory_systems.md | extend: `ml/agent` |
| ml_engineer/mlops_pipelines_deployment.md | label: `ml/mlops` (new) |
| ml_engineer/model_evaluation_benchmarking.md | extend: `ml/evals` |
| ml_engineer/multi_agent_orchestration.md | extend: `ml/agent` |
| ml_engineer/production_rag_at_scale.md | extend existing: `be/ml` |
| ml_engineer/prompt_engineering_production.md | label: `ml/prompt` (new) |
| ml_engineer/prompt_optimization_dspy.md | extend: `ml/prompt` |
| ml_engineer/semantic_caching.md | extend existing: `be/caching` |

### mobile_engineer (3 dead)
| Skill file | Proposed trigger |
|-----------|-----------------|
| mobile_engineer/app_store_deployment.md | label: `mobile/release` (new) |
| mobile_engineer/mobile_performance_profiling.md | extend all: `mobile/*` labels |
| mobile_engineer/push_notifications_deep_links.md | label: `mobile/push` (new) |

### product_manager (8 dead — entire agent unwired)
| Skill file | Proposed trigger |
|-----------|-----------------|
| product_manager/prd_authoring.md | THINK phase or label: `product/prd` |
| product_manager/user_story_authoring.md | label: `product/stories` (new) |
| product_manager/mvp_scope_definition.md | label: `product/mvp` (new) |
| product_manager/rice_prioritization.md | label: `product/prioritize` (new) |
| product_manager/north_star_metric.md | label: `product/metrics` (new) |
| product_manager/okrs_framework.md | label: `product/okrs` (new) |
| product_manager/experiment_design_ab.md | label: `product/experiment` (new) |
| product_manager/continuous_discovery_habits.md | label: `product/discovery` (new) |

### qa_engineer (4 dead)
| Skill file | Proposed trigger |
|-----------|-----------------|
| qa_engineer/equivalence_partitioning.md | extend existing: `testing/unit` |
| qa_engineer/load_testing_methodology.md | label: `testing/load` (new) |
| qa_engineer/mutation_testing.md | extend existing: `security-critical` |
| qa_engineer/testing_strategy_template.md | GATE 2 trigger (always at sprint planning) |

### scrum_master (9 dead — entire agent unwired)
| Skill file | Proposed trigger |
|-----------|-----------------|
| scrum_master/sprint_planning.md | SM-PLAN phase (always) |
| scrum_master/estimation_techniques.md | SM-PLAN phase (always) |
| scrum_master/velocity_capacity_modeling.md | SM-PLAN phase (always) |
| scrum_master/dependency_management.md | SM-PLAN phase (always) |
| scrum_master/living_context_file.md | SM-PLAN phase (always) |
| scrum_master/retrospective_facilitation.md | SM-RETRO phase (always) |
| scrum_master/blocker_triage.md | SM-PLAN / mid-sprint trigger |
| scrum_master/prebuild_documentation_gate.md | GATE 2 (always) |
| scrum_master/stakeholder_communication.md | SM-PLAN phase (always) |

### security_engineer (15 dead)
| Skill file | Proposed trigger |
|-----------|-----------------|
| security_engineer/ai_ml_security_prompt_injection.md | extend existing: `be/ml` |
| security_engineer/compliance_soc2_iso_hipaa_pci.md | label: `security/compliance` (new) |
| security_engineer/container_kubernetes_security.md | extend existing: `devops/k8s` |
| security_engineer/forensics_log_analysis_dfir.md | label: `security/incident` (new) |
| security_engineer/identity_access_management_rbac_abac.md | extend existing: `be/auth` |
| security_engineer/incident_response_runbook.md | extend: `security/incident` |
| security_engineer/owasp_top10_review.md | extend existing: `security/review` |
| security_engineer/privacy_engineering_gdpr_ccpa.md | extend existing: `be/pii` |
| security_engineer/red_blue_purple_team_operations.md | extend existing: `security/pentest` |
| security_engineer/secrets_management.md | extend existing: `security/secrets` |
| security_engineer/secure_sdlc_devsecops.md | role default (security_engineer always) |
| security_engineer/security_posture_template.md | GATE 2 trigger (architect always) |
| security_engineer/supply_chain_sbom_slsa.md | label: `security/supply-chain` (new) |
| security_engineer/threat_modeling_stride_pasta.md | extend existing: `security-critical` |
| security_engineer/vulnerability_management_cve_patching.md | extend existing: `security/review` |
| security_engineer/zero_trust_architecture.md | label: `arch/zero-trust` (new) |

### senior_engineer_fe (3 dead)
| Skill file | Proposed trigger |
|-----------|-----------------|
| senior_engineer_fe/frontend_observability.md | extend existing: `fe/perf` |
| senior_engineer_fe/progressive_web_app.md | label: `fe/pwa` (new) |
| senior_engineer_fe/react_performance_patterns.md | extend existing: `fe/perf` |

### shared/ (8 dead)
| Skill file | Proposed trigger |
|-----------|-----------------|
| shared/code_review_excellence.md | role default (all agents, always) |
| shared/concurrency_safety.md | extend existing: `be/resilience` |
| shared/data_modeling_principles.md | extend existing: `be/database` |
| shared/debugging_methodology.md | Mode 3 default (bugfix/trivial) |
| shared/feature_flags_safely.md | label: `devops/feature-flags` (new) |
| shared/performance_profiling.md | extend existing: `fe/perf` + `be/perf` |
| shared/refactoring_safely.md | label: `be/refactor` (new) or Mode 3 |
| shared/statistical_analysis_patterns.md | extend existing: `data/eda` |

### sre_engineer (8 dead)
| Skill file | Proposed trigger |
|-----------|-----------------|
| sre_engineer/blameless_postmortem.md | SM-RETRO trigger (after incident sprint) |
| sre_engineer/capacity_planning_sre.md | label: `sre/capacity` (new) |
| sre_engineer/chaos_engineering.md | label: `sre/chaos` (new) |
| sre_engineer/error_budget_policy.md | extend existing: `devops/monitor` |
| sre_engineer/incident_command_system.md | label: `sre/incident` (new) |
| sre_engineer/on_call_management.md | label: `sre/oncall` (new) |
| sre_engineer/runbook_automation.md | label: `sre/runbook` (new) |
| sre_engineer/toil_reduction.md | label: `sre/toil` (new) |

### technical_writer (13 dead — entire agent unwired)
| Skill file | Proposed trigger |
|-----------|-----------------|
| technical_writer/diataxis_framework.md | GATE 5 / sprint close (always) |
| technical_writer/plain_language.md | GATE 5 / sprint close (always) |
| technical_writer/audience_adaptation.md | GATE 5 / sprint close (always) |
| technical_writer/changelog_release_notes.md | GATE 5 / sprint close (always) |
| technical_writer/app_flow_template.md | GATE 2 trigger (always) |
| technical_writer/project_index_template.md | GATE 2 trigger (always) |
| technical_writer/developer_handoff_kit.md | GATE 5 / sprint close (always) |
| technical_writer/api_reference_authoring.md | extend: sprint close if `be/api` in sprint |
| technical_writer/sdk_documentation.md | label: `docs/sdk` (new) |
| technical_writer/onboarding_documentation.md | label: `docs/onboarding` (new) |
| technical_writer/troubleshooting_guide_authoring.md | label: `docs/troubleshooting` (new) |
| technical_writer/leadership_deck_authoring.md | label: `docs/leadership` (new) |
| technical_writer/sales_demo_deck.md | label: `docs/sales` (new) |

### website_creator (19 dead — entire subdomain routing unwired)
| Skill file | Proposed trigger |
|-----------|-----------------|
| website_creator/content/landing_page_copy.md | label: `web/content` (new) |
| website_creator/content/content_marketing_strategy.md | label: `web/content` |
| website_creator/content/case_study_customer_stories.md | label: `web/content` |
| website_creator/content/email_marketing_automation.md | label: `web/email` (new) |
| website_creator/conversion/landing_page_patterns.md | label: `web/conversion` (new) |
| website_creator/conversion/conversion_optimization.md | label: `web/conversion` |
| website_creator/conversion/conversion_psychology_principles.md | label: `web/conversion` |
| website_creator/conversion/forms_lead_capture_ux.md | label: `web/conversion` |
| website_creator/conversion/growth_loops_referral_plg.md | label: `web/growth` (new) |
| website_creator/conversion/ab_testing_experimentation.md | label: `web/growth` |
| website_creator/conversion/pricing_page_design.md | label: `web/conversion` |
| website_creator/conversion/trust_signals_social_proof.md | label: `web/conversion` |
| website_creator/seo/seo_foundations.md | label: `web/seo` (new) |
| website_creator/seo/technical_seo_structured_data.md | label: `web/seo` |
| website_creator/seo/analytics_event_tracking_setup.md | label: `web/seo` |
| website_creator/seo/internationalization_seo_hreflang.md | label: `web/seo` |
| website_creator/technical/responsive_design_mobile_first.md | label: `web/technical` (new) |
| website_creator/technical/accessibility_wcag_2_2_aa.md | label: `web/technical` |
| website_creator/technical/animation_choreography.md | label: `web/technical` |
| website_creator/technical/cms_headless_integration.md | label: `web/technical` |
| website_creator/technical/cookie_consent_privacy_ux.md | label: `web/technical` |
| website_creator/technical/image_video_optimization.md | label: `web/technical` |
| website_creator/technical/web_typography_variable_fonts.md | label: `web/technical` |

---

## Implementation Plan — Fix 47

### Fix 47A — New labels + extend existing rows in `skill-label-index.md`
**Scope:** ~115 skills · ~25 new labels + extensions to existing rows
**New labels to add:**
```
be/graphql, be/realtime, be/refactor, be/perf
fe/ssr, fe/pwa, fe/design-system
arch/ddd, arch/microservices, arch/monorepo, arch/api-gateway, arch/capacity,
arch/microfrontend, arch/zero-trust
ml/agent, ml/rag, ml/evals, ml/fine-tuning, ml/mlops, ml/prompt, ml/cost
data/quality, data/analytics, data/lake
db/graph, db/timeseries, db/reliability
cloud/landing-zone, cloud/network, cloud/multi-region, cloud/review,
cloud/compliance, cloud/cost, cloud/capacity, cloud/multi-cloud
finops/cost, finops/alerts, finops/chargeback, finops/savings, finops/optimize
security/compliance, security/incident, security/supply-chain
sre/capacity, sre/chaos, sre/incident, sre/oncall, sre/runbook, sre/toil
devops/platform, devops/feature-flags
mobile/release, mobile/push
product/prd, product/stories, product/mvp, product/prioritize,
product/metrics, product/okrs, product/experiment, product/discovery
research/competitive, research/user, research/market, research/positioning, research/pricing
web/content, web/email, web/conversion, web/growth, web/seo, web/technical
docs/sdk, docs/onboarding, docs/troubleshooting, docs/leadership, docs/sales
testing/load
```

### Fix 47B — Phase/event triggers in `orchestrator-routing.md` + `team-orchestrator-core.md`
**Scope:** ~41 skills
- CTO THINK phase → load all `cto/` skills when CTO activates
- SM-PLAN → load all `scrum_master/` skills when SM-PLAN starts
- SM-RETRO → `retrospective_facilitation.md`, `blameless_postmortem.md`
- GATE 2 → `testing_strategy_template.md`, `security_posture_template.md`, `prebuild_documentation_gate.md`, `app_flow_template.md`, `project_index_template.md`
- GATE 5 / sprint close → all `technical_writer/` base skills, ARCHITECT loads `trd_template.md` + `hexagonal_architecture.md` + `project_structure_layout.md`

### Fix 47C — Role defaults in `skill-selection-matrix.md`
**Scope:** ~17 skills
- All agents → `shared/code_review_excellence.md`
- Mode 3 / bugfix → `shared/debugging_methodology.md`, `shared/refactoring_safely.md`
- `devops_engineer` → `devops_engineer/twelve_factor_app.md`
- `security_engineer` → `security_engineer/secure_sdlc_devsecops.md`

---

*Next action: implement Fix 47A → 47B → 47C in sequence. Start with 47A (biggest coverage gain).*
