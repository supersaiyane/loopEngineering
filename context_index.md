# Context Index — Loop Engineering

Function/component-level index. Pairs with `project_map.md` (module-level). Excludes
`healthguard-pro/` and `kiro/memory/` per user instruction.

---

## Entry Points (read these first when tracing runtime behavior)

- **Hook / trigger:** `kiro/hooks/elite-team-orchestrator.kiro.hook` — fires on every `promptSubmit`;
  the only thing Kiro loads automatically. Detects spec-phase vs develop-phase, runs GUARD 4
  (pre-code artifact gate), then loads steering files and delegates.
- **Main routing logic:** `kiro/steering/orchestrator-routing.md` — defines the 5 execution modes
  (Mode 1 Full Army, Mode 2 Single Agent, Mode 3 Direct, Mode 4 Hybrid/Spec+Army, Mode 5 Lean),
  the `$TRACKER` abstraction/translation table (Jira/Linear/GitHub/Asana/markdown), environment
  detection, and phase/event auto-triggers (Fix 47B).
- **Constitution (roles + gates 1-3):** `kiro/steering/team-orchestrator-core.md` — role registry,
  artifact dependency chain, role handoff format, ROLE CONTRACT TABLE (pre/postconditions per role),
  scrum_master's 4 activation modes (SM-GATE/SM-PLAN/SM-RETRO/SM-UNBLOCK), GATE 1/2/3, story label taxonomy.
- **Iteration protocol:** `kiro/steering/loop-engine.md` — the PLAN→DO→VERIFY→DECIDE loop every
  story goes through in DEVELOP phase (max 8 iterations, maker/checker split, SM-UNBLOCK on hard stop).

---

## `kiro/skills/` — 22 Roles + shared (one line each, from each SKILL.md)

| Role folder | Focus |
|---|---|
| `architect` | Architecture decisions, patterns, system design, threat modeling (ADRs, STRIDE, API contracts). |
| `backend_lead` | API design, caching, resilience, distributed transactions, async patterns. |
| `cloud_architect` | Cloud infrastructure: VPC, multi-region, IAM, cost optimization, DR planning. |
| `cto` | Tech strategy, org design, build-vs-buy, API platform strategy, developer experience. |
| `data_engineer` | Stream processing, batch pipelines, dbt transformations, Airflow DAGs, CDC, data quality. |
| `data_scientist` | EDA, A/B testing, cohort analysis, funnel analysis, feature engineering, data storytelling. |
| `database_architect` | Database design, query optimization, scaling, cloud data pipelines. |
| `devops_engineer` | CI/CD, IaC, deployment strategies, monitoring, secrets, GitOps. |
| `finops_architect` | Unit economics, cost projections, budget guardrails, pricing sensitivity. |
| `frontend_lead` | React/Next.js, component systems, SSR, performance, micro-frontends. |
| `market_researcher` | Market analysis, TAM/SAM/SOM, competitive intelligence, personas, positioning. |
| `ml_engineer` | RAG, LLM engineering, agents, fine-tuning, MLOps, cost optimization. |
| `mobile_engineer` | iOS/SwiftUI, Android/Jetpack Compose, React Native, offline sync, push notifications, app store deployment. |
| `product_manager` | PRD, user stories, acceptance criteria, roadmap, prioritization. |
| `qa_engineer` | Testing strategies, contract testing, accessibility, visual regression, test data. |
| `scrum_master` | Sprint planning, estimation, retrospectives, dependency management, stakeholder comms. |
| `security_engineer` | STRIDE threat modeling, OWASP review, auth design, encryption, compliance. |
| `senior_engineer_be` | Clean code, TDD, observability, refactoring, dependency injection. |
| `senior_engineer_fe` | React performance, PWA, frontend observability, TDD, feature flags. |
| `shared` | Cross-role utility skills (code review, concurrency safety, data modeling, design system gate, etc.) any role can load when the activity matches. |
| `sre_engineer` | SLOs, incident response, chaos engineering, capacity planning, on-call. |
| `technical_writer` | API docs, SDK guides, changelogs, Diátaxis framework, troubleshooting guides. |
| `website_creator` | Landing pages, product sites, SEO, marketing web presence (has nested content/conversion/seo/technical subfolders). |

Each role folder = `SKILL.md` (role description) + ~5-14 topic reference files. Loaded selectively
per activity via `skill-selection-matrix.md`, not in bulk (~173 skill files total across all roles).

---

## `kiro/steering/` — 14 files, one line each on what it governs

| File | Governs |
|---|---|
| `team-orchestrator-core.md` | Roles, artifact chain, SM's 4 modes, GATE 1/2/3, role contract table, story label taxonomy. Loads at Mode 1/4/5 session start. |
| `team-orchestrator-sprint.md` | GATE 4 (sprint end/retro) and GATE 5 (phase end) — split out of team-orchestrator.md (Fix 19) to reduce single-file size. |
| `team-orchestrator-rules.md` | Security discipline, non-negotiables, quality bars, conflict resolution, subagent isolation, branch lifecycle, document ownership. Loads at DEVELOP phase start. |
| `team-orchestrator.md` | Deprecated pointer file — explains the 3-way split (core/sprint/rules) and says "do not load directly." |
| `orchestrator-routing.md` | $TRACKER translation table, environment detection, mandatory load order, the 5 execution modes, phase/event auto-triggers. Loaded on demand (not auto — Fix 35 fixed a dual-routing conflict). |
| `loop-engine.md` | The per-story PLAN→DO→VERIFY→DECIDE loop, scoring rubric, maker/checker split, Ralph Wiggum guard (against premature "done" declarations), SM-UNBLOCK protocol. Loads at DEVELOP phase. |
| `discovery-engine.md` | The 7 scoping questions (platform/scale/complexity/deployment/revenue/design/security) that run before mode selection on ambiguous new-build prompts. |
| `skill-selection-matrix.md` | Maps role + activity → which 2-4 skill files to load (compress-all protocol), keeping context cost low. |
| `skill-label-index.md` | Maps story labels (be/api, security/auth, etc.) to skill file paths; loaded only at SM-PLAN time to save tokens. |
| `context-memory-discipline.md` | Token/context budget tiers (PEAK/GOOD/DEGRADING/CRITICAL), read-count discipline, degradation behavior. Always-loaded, canonical source for discipline tiers. |
| `session-guards.md` | Always-on guards: constraint drift (GUARD 1), bad-loop domain blocklist (GUARD 2), pxpipe context check (GUARD 3), pre-code artifact gate (GUARD 4). |
| `memory-management.md` | Rules for reading/writing `init_docs/`-style memory files (lessons, decisions) — loaded only when touching memory. |
| `phase-reporting.md` | Mandatory report templates used at phase boundaries (loaded only when working in phase docs). |
| `ponytail.md` | The "lazy senior dev" 7-rung ladder (use stdlib → dependency → config → tool → compose → fork → write-custom-last) plus rung-disqualification/escalation protocol. |

---

## `scripts/` — one line each

| Script | Purpose |
|---|---|
| `bootstrap-project.sh` | Scaffolds a new Kiro-ready project (copies framework, sets up symlinks, seeds docs/services/infra dirs). Usage: `./scripts/bootstrap-project.sh <ProjectName> [/path/to/parent]`. |
| `start-kiro-pxpipe.sh` | Launches the pxpipe token-compression proxy (image-rendered context, ~59-70% input token savings) with a local dashboard on port 47821. |

---

## Key Entry Points Summary

- **Orchestrator's main routing logic:** `kiro/steering/orchestrator-routing.md` (mode selection, $TRACKER table, phase triggers).
- **Hook that triggers it all:** `kiro/hooks/elite-team-orchestrator.kiro.hook` (`promptSubmit` event → `askAgent` action → loads team-orchestrator-core.md, team-orchestrator-rules.md, skill-selection-matrix.md, then loop-engine.md at DEVELOP phase, then team-orchestrator-sprint.md at sprint/phase end).
- **Constitution root:** `kiro/steering/team-orchestrator-core.md` (role registry + gates 1-3).
- **Iteration/quality engine:** `kiro/steering/loop-engine.md`.
- **Non-Kiro runtime adapters:** `kiro/adapters/claude-system-prompt.md`, `kiro/adapters/chatgpt-system-prompt.md`.
