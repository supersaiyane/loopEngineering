---
inclusion: manual
---

# Optional specialists and skill routing

These profiles are available for relevant tasks or explicit user requests. Their presence does not require activation in any mode. The coordinator selects a role only when the task needs its capability, declares inputs, outputs, permissions and checks, and records why it was selected or deferred. Use existing agents where responsibilities overlap; avoid duplicate work. A profile, prompt, recorded hash or claimed handoff does not prove host invocation or skill use.

Choose the matching role and activity below. Read the listed role-qualified skills plus relevant shared defaults; report omitted or unavailable material. Handoffs include source paths, decisions, actual checks, unknowns and the next owner. If a host cannot delegate, disclose that roles share one session.

| Role | When to select | Activity skills |
|---|---|---|
| `loop-analytics-engineer` | Translate source data into governed analytical models and reusable metrics. | `analytics_engineer/dimensional_modeling.md`, `analytics_engineer/semantic_metric_contracts.md` |
| `loop-data-analyst` | Answer product and business questions using inspectable data and explicit uncertainty. | `data_analyst/evidence_backed_analysis.md`, `data_analyst/metric_diagnostics.md` |
| `loop-data-quality-engineer` | Design and investigate checks that make data fit for an identified use. | `data_quality_engineer/data_quality_contracts.md`, `data_quality_engineer/reconciliation_and_anomalies.md` |
| `loop-data-governance` | Manage ownership, lineage, classification and access for data assets. | `data_governance/catalog_lineage_ownership.md`, `data_governance/data_access_retention.md` |
| `loop-bi-developer` | Build decision-focused dashboards from defined and validated metrics. | `bi_developer/dashboard_design_validation.md`, `bi_developer/metric_layer_consistency.md` |
| `loop-streaming-engineer` | Design event streams with explicit delivery and recovery semantics. | `streaming_engineer/stream_delivery_semantics.md`, `streaming_engineer/stream_replay_recovery.md` |
| `loop-data-platform-engineer` | Provide secure, reproducible data infrastructure and shared execution services. | `data_platform_engineer/lakehouse_platform_design.md`, `data_platform_engineer/compute_cost_isolation.md` |
| `loop-ai-engineer` | Build AI-powered applications with measured behavior and controlled integrations. | `ai_engineer/model_provider_selection.md`, `ai_engineer/structured_outputs_tool_calls.md` |
| `loop-agent-evaluator` | Evaluate agent behavior and handoffs from observed, reproducible evidence. | `agent_evaluator/agent_trace_evaluation.md`, `agent_evaluator/agent_regression_benchmarks.md` |
| `loop-ai-safety-engineer` | Review AI and agent systems for misuse and control failures. | `ai_safety_engineer/prompt_injection_tool_abuse.md`, `ai_safety_engineer/ai_red_team_data_leakage.md` |
| `loop-ai-observability` | Design evidence-based AI and agent monitoring without oversharing sensitive data. | `ai_observability/ai_trace_instrumentation.md`, `ai_observability/ai_usage_cost_accounting.md` |
| `loop-rag-engineer` | Build and evaluate access-aware retrieval augmented generation systems. | `rag_engineer/retrieval_ingestion_provenance.md`, `rag_engineer/retrieval_quality_evaluation.md` |
| `loop-mlops-engineer` | Operate reproducible machine-learning experiments and deployments. | `mlops_engineer/experiment_registry_reproducibility.md`, `mlops_engineer/model_deployment_monitoring.md` |
| `loop-llmops-engineer` | Release and operate LLM applications with versioned evaluations and fallbacks. | `llmops_engineer/prompt_model_release.md`, `llmops_engineer/provider_fallback_operations.md` |
| `loop-ai-governance` | Coordinate AI system inventory, risk ownership and human oversight. | `ai_governance/ai_inventory_risk_review.md`, `ai_governance/ai_provenance_human_oversight.md` |
| `loop-knowledge-engineer` | Model and maintain traceable organizational knowledge and relationships. | `knowledge_engineer/knowledge_graph_modeling.md`, `knowledge_engineer/entity_resolution_provenance.md` |
| `loop-multimodal-ai-engineer` | Build and evaluate image, audio, video and document AI workflows. | `multimodal_ai_engineer/multimodal_pipeline_design.md`, `multimodal_ai_engineer/multimodal_evaluation.md` |
| `loop-fine-tuning-engineer` | Assess and execute model adaptation with reproducible data and evaluation. | `fine_tuning_engineer/fine_tuning_data_preparation.md`, `fine_tuning_engineer/fine_tuning_evaluation.md` |
| `loop-product-designer` | Design coherent product experiences grounded in user tasks and evidence. | `product_designer/user_journeys_interaction.md`, `product_designer/design_system_usability.md` |
| `loop-learning-designer` | Design instructional outcomes, learning activities and assessments. | `learning_designer/curriculum_learning_objectives.md`, `learning_designer/assessment_feedback_design.md` |
| `loop-privacy-engineer` | Translate privacy requirements into evidence-backed data controls. | `privacy_engineer/privacy_data_mapping_consent.md`, `privacy_engineer/privacy_retention_deletion.md` |
| `loop-accessibility-specialist` | Evaluate accessibility through automated and informed manual review. | `accessibility_specialist/manual_accessibility_review.md`, `accessibility_specialist/inclusive_acceptance_criteria.md` |
| `loop-interactive-learning-engineer` | Build safe interactive coding and simulation experiences. | `interactive_learning_engineer/browser_code_sandbox.md`, `interactive_learning_engineer/simulation_project_storage.md` |
| `loop-performance-engineer` | Measure and improve software performance and capacity. | `performance_engineer/performance_profiling_baselines.md`, `performance_engineer/capacity_load_testing.md` |
| `loop-integration-engineer` | Design resilient integrations between independently owned systems. | `integration_engineer/api_contract_compatibility.md`, `integration_engineer/webhook_reconciliation.md` |
| `loop-platform-engineer` | Improve developer platforms and self-service workflows without imposing a fixed stack. | `platform_engineer/developer_platform_templates.md`, `platform_engineer/platform_access_operations.md` |
| `loop-technical-researcher` | Research technical choices using traceable and current evidence. | `technical_researcher/primary_source_research.md`, `technical_researcher/technical_options_comparison.md` |
| `loop-business-analyst` | Translate business processes and decisions into testable requirements. | `business_analyst/business_process_mapping.md`, `business_analyst/requirements_traceability.md` |

## Additions to existing roles

| Existing role | When to use | Activity skill |
|---|---|---|
| `product_manager` | Requirements and acceptance traceability | `product_manager/requirements_scenario_traceability.md` |
| `architect` | System boundaries and traceability | `architect/system_boundary_traceability.md` |
| `backend_lead` | Tenant-safe integration design | `backend_lead/tenant_safe_integration_design.md` |
| `database_architect` | Tenant migration parity | `database_architect/tenant_migration_parity.md` |
| `security_engineer` | Agent and child-data threat review | `security_engineer/agent_and_child_data_threat_review.md` |
| `devops_engineer` | Delivery supply-chain evidence | `devops_engineer/delivery_supply_chain_evidence.md` |
| `qa_engineer` | Tenant and consent acceptance testing | `qa_engineer/tenant_consent_acceptance_testing.md` |
| `frontend_lead` | Inclusive low-resource UX | `frontend_lead/inclusive_low_resource_ux.md` |
| `senior_engineer_be` | Safe API and session implementation | `senior_engineer_be/safe_api_session_implementation.md` |
| `senior_engineer_fe` | Accessible stateful web flows | `senior_engineer_fe/accessible_stateful_web_flows.md` |
| `scrum_master` | Evidence-backed sprint closure | `scrum_master/evidence_backed_sprint_closure.md` |
| `technical_writer` | Living design traceability | `technical_writer/living_design_traceability.md` |
| `cto` | Decision assumptions and trade-offs | `cto/decision_assumptions_tradeoffs.md` |
| `cloud_architect` | Residency and tenant recovery | `cloud_architect/residency_tenant_recovery.md` |
| `sre_engineer` | Tenant and agent observability | `sre_engineer/tenant_and_agent_observability.md` |
| `finops_architect` | Tenant and AI cost attribution | `finops_architect/tenant_ai_cost_attribution.md` |
| `ml_engineer` | ML data and evaluation operations | `ml_engineer/ml_data_evaluation_operations.md` |
| `ml_engineer` | Age-appropriate AI tutor evaluation | `ml_engineer/age_appropriate_ai_tutor_evaluation.md` |
| `data_engineer` | Incremental pipeline recovery | `data_engineer/incremental_pipeline_recovery.md` |
| `data_scientist` | Causal and forecasting diagnostics | `data_scientist/causal_forecasting_diagnostics.md` |
| `market_researcher` | Source freshness and assumptions | `market_researcher/source_freshness_assumptions.md` |
| `website_creator` | Consent-aware accessible conversion | `website_creator/consent_aware_accessible_conversion.md` |
| `mobile_engineer` | Mobile activation and offline risk | `mobile_engineer/mobile_activation_scope.md` |
| `shared` | Agent handoff evidence | `shared/agent_handoff_evidence.md` |
| `shared` | Agent interruption, approval wait or conflicting handoff | `shared/agent_run_recovery.md` |
