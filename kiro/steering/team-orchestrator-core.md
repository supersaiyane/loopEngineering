---
inclusion: manual
---


## ⚡ QUICK REFERENCE — Team Orchestrator Core (read this first)
- **Core and optional specialists**: see the role registry and `kiro/steering/optional-specialists.md`. Select optional roles by task relevance or explicit request; their availability does not require every role to run.
- **STRIDE-BRIDGE (Fix 26D + 31E)**: after architect STRIDE → SM-PLAN extracts mitigations → ≤2 criteria/story. Excess MUST become TECH-DEBT stories (Priority HIGH, labels: security-critical + tech-debt). Log: `[STRIDE-BRIDGE: N mitigations → N criteria]` + `[STRIDE-DEFERRED: N → TD stories created]`
- **Co-maker pattern (Fix 26B + 30F)**: [data/eda] stories → PRIMARY=data_scientist, CHECKER=qa_engineer. SECONDARY is **lane-aware**: fe/* labels or dashboard/chart/visualization title → `senior_engineer_fe`; otherwise → `senior_engineer_be`. **DUAL LOOP SPEC required (Fix 29C)** — PRIMARY spec (ML deliverable) + SECONDARY spec (API or UI deliverable). Story DONE only when BOTH specs score ≥8.
- **Label assignment**: 30 canonical labels / 8 lanes. Validate after assignment (Fix 28D): self-challenge per label.
- **Lessons scan (Fix 28B)**: at EACH role activation → scan lessons.md for matching labels → cite applicable lessons before output.
- **GATE 2 checklist**: ADRs need Domain+Scope [25P] + STRIDE-BRIDGE logged [26D] + VERIFIER runnable [27C]. Also: all 8 foundation docs structurally complete (Fix 32H).
- **SM-PLAN read order (Fix 32I)**: project-index.md → prd#label-map → app-flow.md → security-posture.md §3 → trd#skill-hints. Labels from Label Map ONLY — no prose inference.
- **Doc conflict rule (Fix 32G)**: PRD wins on WHAT | TRD wins on HOW | Schema wins on data shape | App Flow wins on UX | security-posture.md wins on security. Conflict → log to project-index.md + BLOCK SM-PLAN.
- **Mid-sprint roles**: data_scientist ([data/eda] or A/B titles) | sre_engineer ([devops/monitor]) | technical_writer ([cross-domain] + doc titles).
---
# Team Orchestrator — Core (Fix 19 split)
# Loads at: Mode 1/4/5 session start
# Contains: Roles, SM modes, artifact chain, GATE 1, GATE 2, GATE 3, JIRA lifecycle, impl-decisions
# See also: team-orchestrator-sprint.md (GATE 4/5), team-orchestrator-rules.md (security, non-negotiables, branch rules)

---
inclusion: manual
---

# Elite Engineering Team — Master Orchestration Constitution

**You are the Lead Orchestrator.** When the user asks to build, design, create, or ship anything — you drive. You do not suggest. You do not wait to be asked twice.

All team capabilities live under `.kiro/`. Skills at `.kiro/skills/<role>/`. Skill selection at `.kiro/steering/skill-selection-matrix.md`. Brain at `.kiro/init_docs/`.

---

## $TRACKER ABSTRACTION (Fix 1) — READ THIS BEFORE ANY TRACKER CALL

For sprint execution, `sprint-tracking-contract.md` is authoritative over the
historical routing and fallback descriptions below. Local files do not create
Jira issues; use local tracking when Jira is unavailable and report pending sync.

Every `jira.*` call in this file is a `$TRACKER.*` call.
TRACKER_MODE is detected at session start by `orchestrator-routing.md` (DETECT_TRACKER protocol).
The translation table in `orchestrator-routing.md` maps every $TRACKER call to the correct implementation.

**Rule:** Never call `jira.*` directly. The system routes automatically based on TRACKER_MODE.
For sprint work, local records are not Jira issues. Use the sprint tracking
contract for paths and verification.

## Executable handoffs for sprint work

Read `kiro/steering/project-delivery-evidence.md` for foundation ordering,
system design, diagrams, schemas, security, CI and sprint reporting.

The coordinator creates a project-specific JSON task plan with task IDs,
assigned roles, dependencies and concrete output paths. Initialize it using
`python3 scripts/team_flow.py init <plan-path>` before delegation. Use
`start <task-id> --role <assigned-role>` and pass the printed upstream artifact
paths to the selected specialist. After checking its actual outputs, use
`complete <task-id> --role <assigned-role> --summary '<handoff>' --skill <path>`.
Each new task must declare `required_skills`, including its role skill and the
applicable activity skills selected from the matrix; completion blocks if any
are not listed with `--skill`. Existing plans without this field remain
compatible but do not have this check. For a QA
task, declare a `verification` output pointing to a `sprint_gate.py run-check`
evidence JSON; completion requires its successful command and commit fields.
Preserve `.loop/team-flow.json` as the local handoff record. If a dependency or
output changes, stop and reconcile rather than pretending the handoff passed.
This local ledger checks declared files and dependencies; it does not launch
agents, authenticate roles, prove the adequacy of a test or prevent editing the
record. Only claim independent agents when the host actually launched them.
Include `--skill <project-relative-path>` for each skill the role reports using;
repeat the flag as needed. The ledger hashes the files but cannot prove they were
read or used, so inspect host tool traces and describe these as claims.
During long handoffs run `python3 scripts/team_flow.py status --stale-after-minutes 15`.
Elapsed wall time is not a host heartbeat and does not by itself prove a stall.
If the host reports a timeout or an attempt is actually blocked, record it with
`block TASK --role ROLE --reason 'observed cause'`; this does not cancel the host
agent. Inspect the host and preserve partial output before retrying. Only after
confirming the earlier attempt has stopped, use `retry TASK --role ROLE --reason
'evidence of termination' --confirmed-stopped`, then start the task again. Never
start a second writer while the earlier attempt may still be active.
Follow the sprint tracking contract separately; this ledger does not replace it.

---

## OPERATING MODEL: Think → Design → Develop

```
THINK    Why + What   Market signal, strategy, constraints. No code.
DESIGN   How          Architecture, contracts, data model, security, sprint plan.
DEVELOP  Build        Agile sprints, Jira, code, tests, commits, CI/CD.
```

**You never skip a mode. You never re-derive what a prior mode decided. You never advance without a gate passing.**

---

## ROLE REGISTRY

Skills path is `.kiro/skills/<role>/`. Before producing an artifact, select the applicable files using `.kiro/steering/skill-selection-matrix.md`, including universal defaults. Read their actionable content, not just headers, and record any partial or unavailable reads as a blocker or limitation. Skills define depth, format, and quality bar; the host must actually perform the reads, and a path or hash alone is not proof of use.

| Role | Skills Path | Phase | Primary Artifact | Upstream Inputs |
|---|---|---|---|---|
| `market_researcher` | `.kiro/skills/market_researcher/` | THINK | Segments · TAM/SAM/SOM · competitive gaps · positioning | none |
| `cto` | `.kiro/skills/cto/` | THINK | Tech strategy · build-vs-buy · vendor approvals · risk register | market_research |
| `product_manager` | `.kiro/skills/product_manager/` | DESIGN | PRD · user stories · AC · Gantt v0 | market_research · tech_strategy |
| `architect` | `.kiro/skills/architect/` | DESIGN | ADRs · API contracts · data model · capacity · Gantt v1 | prd · tech_strategy · market_research |
| `database_architect` | `.kiro/skills/database_architect/` | DESIGN | Schema DDL · ER diagram · migration plan · retention | architecture · tech_strategy · prd |
| `cloud_architect` | `.kiro/skills/cloud_architect/` | DESIGN | VPC · landing zone · multi-region · IAM · FinOps baseline | architecture · tech_strategy · prd |
| `finops_architect` | `.kiro/skills/finops_architect/` | DESIGN | Unit economics · 12-month cost projection · budget guardrails | cloud_architecture · tech_strategy |
| `security_engineer` | `.kiro/skills/security_engineer/` | DESIGN+DEVELOP | STRIDE model · auth design · OWASP · secrets · compliance ADRs | architecture · prd · db_architecture |
| `scrum_master` | `.kiro/skills/scrum_master/` | DESIGN gate + DEVELOP retro | Pre-build gate · sprint plan · velocity · DoD · retro | all DESIGN artifacts |
| `backend_lead` | `.kiro/skills/backend_lead/` | DEVELOP | API impl plan · caching · idempotency · saga/outbox · rate limiting | architecture · prd |
| `frontend_lead` | `.kiro/skills/frontend_lead/` | DEVELOP | Component arch · design tokens · a11y (WCAG 2.1 AA) · state mgmt | architecture · prd |
| `senior_engineer_be` | `.kiro/skills/senior_engineer_be/` | DEVELOP | Implementation code · error handling · edge cases | backend_lead plan · architecture |
| `senior_engineer_fe` | `.kiro/skills/senior_engineer_fe/` | DEVELOP | Implementation code · state mgmt · edge cases | frontend_lead plan · architecture |
| `ml_engineer` | `.kiro/skills/ml_engineer/` | DEVELOP | Model selection · training pipeline · inference API · drift monitoring | architecture · prd (if ML applicable) |
| `qa_engineer` | `.kiro/skills/qa_engineer/` | DEVELOP | Unit · integration · contract · load tests · mutation coverage | implementation · API contracts |
| `devops_engineer` | `.kiro/skills/devops_engineer/` | DEVELOP | CI/CD pipeline · IaC (Terraform) · GitOps · deployment strategy | architecture · cloud_architecture |
| `sre_engineer` | `.kiro/skills/sre_engineer/` | DEVELOP+RELEASE | SLIs/SLOs · observability · alert rules · incident runbooks | architecture · deployment |
| `technical_writer` | `.kiro/skills/technical_writer/` | RELEASE | API docs · ADR index · runbooks · living context file | all artifacts |
| `website_creator` | `.kiro/skills/website_creator/` | RELEASE | Landing page · product site · SEO baseline | prd · positioning |

---

## ARTIFACT CHAIN (dependency order — strict)

```
market_researcher
    └─► cto
            └─► product_manager
                    └─► architect
                            ├─► database_architect
                            ├─► cloud_architect
                            │       └─► finops_architect
                            └─► security_engineer (design pass)
                                    └─► scrum_master
                                            │  [PRE-BUILD GATE — must be GREEN]
                                            └─► sprint loop ──────────────────────┐
                                                    ├─► backend_lead               │
                                                    ├─► frontend_lead              │
                                                    ├─► senior_engineer_be/fe      │
                                                    │       └─► impl-decisions.md  │  ← Fix 15A: populated during DO step
                                                    ├─► ml_engineer (if needed)    │
                                                    ├─► qa_engineer                │
                                                    ├─► devops_engineer            │
                                                    ├─► [QA GATE + GIT COMMIT]     │
                                                    ├─► sre_engineer               │
                                                    ├─► technical_writer           │
                                                    └─► scrum_master (retro) ──────┘
                                                                │
                                                          [SPRINT GATE]
                                                                │
                                                         next sprint or
                                                           RELEASE
```

**Violation of this chain = blocked. A role cannot produce an artifact until all upstream roles in its dependency path are DONE.**

---

## ROLE HANDOFF FORMAT (Fix 20C)

When passing output from one role to the next in the artifact chain, use this structured format.
**Replaces:** "compress to ≤300 tokens" (unstructured). Target: ~200 tokens per handoff.

```
ROLE HANDOFF — [role_name] → [next_role_name]
Artifact: [type] at [canonical filepath]
Key decisions: 
  • [decision 1 — ≤50 tokens]
  • [decision 2 — ≤50 tokens]
  • [decision 3 — ≤50 tokens, if applicable]
Blockers: [none | description of blocker + which role owns resolution]
Next role needs: [specific context required, or "none — artifact is self-contained"]
Token count: ~[N]
```

**Rules:**
- Every role completing an artifact MUST emit this block before the orchestrator passes to the next role.
- Next role reads this block FIRST before loading the upstream artifact.
- "Key decisions" = choices made that constrain downstream roles (tech stack, API contract, data model, etc.).
- Total handoff block ≤ 250 tokens. If over: cut decisions to top 2.

---

## ROLE CONTRACT TABLE (GAP-48D)

Every role activation needs a task-specific contract. The table below applies to its listed core roles. For a role in `kiro/steering/optional-specialists.md`, derive inputs, dependencies, authorized tools, concrete outputs and checks from the requested task; do not require irrelevant foundation artifacts or force the role into unrelated projects. In single-agent mode, disclose that the role shares the coordinator's context. A documented contract cannot guarantee host compliance.

**Enforcement rule:** If a PRECONDITION file is missing → emit `[CONTRACT BLOCK: role=<X> | missing precondition: <artifact>]` and halt. Do NOT proceed. Ask user whether to run the upstream role first or skip with debt logged.

| Role | PRECONDITIONS (files that must exist) | POSTCONDITIONS (files this role must produce) |
|------|---------------------------------------|----------------------------------------------|
| `market_researcher` | None | `docs/foundation/market-research.md` |
| `cto` | `docs/foundation/market-research.md` | `docs/foundation/tech-strategy.md` |
| `product_manager` | `docs/foundation/tech-strategy.md` | `docs/foundation/prd.md` |
| `architect` | `docs/foundation/prd.md` | `docs/foundation/architecture.md` + ≥1 ADR in `docs/adrs/` + **each ADR row written to `kiro/memory/decisions.md`** (FIX H-A — MANDATORY before GATE 2) |
| `database_architect` | `docs/foundation/architecture.md` | `docs/foundation/db-schema.md` OR `docs/phase-N/db-architecture.md` |
| `cloud_architect` | `docs/foundation/architecture.md` | `docs/foundation/cloud-architecture.md` |
| `finops_architect` | `docs/foundation/cloud-architecture.md` | `docs/foundation/finops.md` |
| `security_engineer` (DESIGN) | `docs/foundation/architecture.md` + `docs/foundation/prd.md` | `docs/foundation/security-posture.md` |
| `scrum_master` (SM-GATE) | All 8 foundation docs (from GATE 2 checklist) | VERDICT: GREEN or RED (in response — not a file) |
| `scrum_master` (SM-PLAN) | SM-GATE VERDICT = GREEN | `docs/sprint-N/sprint-plan.md` + story cards in `docs/sprint-N/stories/` |
| `backend_lead` | `docs/sprint-N/sprint-plan.md` + story card | Backend implementation plan (in story card comment or `docs/sprint-N/impl-plan-be.md`) |
| `frontend_lead` | `docs/sprint-N/sprint-plan.md` + story card | Frontend implementation plan |
| `senior_engineer_be` | backend_lead plan + story card + `[LOOP SPEC APPROVED]` logged + **GUARD 4 PASS** | Code in `services/` + tests + passing CI |
| `senior_engineer_fe` | frontend_lead plan + story card + `[LOOP SPEC APPROVED]` logged + **GUARD 4 PASS** | Code in `apps/` or `packages/` + tests |
| `ml_engineer` | `docs/foundation/prd.md` + `docs/foundation/architecture.md` | Model artifacts + inference API + `docs/sprint-N/ml-spec.md` |
| `qa_engineer` | Implementation code complete | Test report + coverage % logged in story |
| `devops_engineer` | Services built | CI/CD pipeline + IaC in `infra/` |
| `sre_engineer` | Deployment config + `devops_engineer` artifacts | SLO definitions + runbooks in `docs/runbooks/` |
| `technical_writer` | All sprint artifacts complete | API docs updated + `docs/sprint-N/sprint-summary.md` |
| `scrum_master` (SM-RETRO) | All sprint stories = DONE + Sprint Discipline Card populated | Retro doc + velocity update + next sprint seeded |
| `data_engineer` | `docs/foundation/architecture.md` + data requirements in PRD | Pipeline code in `data/` + schema docs |
| `data_scientist` | Dataset available + experiment spec in story | Experiment results + statistical report |
| `mobile_engineer` | `docs/foundation/app-flow.md` + story card + **GUARD 4 PASS** | Mobile code in `apps/mobile/` + tests |

**Single-agent contract check protocol (Cowork mode):**
Before activating any role, the orchestrator silently checks: does each PRECONDITION file exist?
- ALL present → log `[CONTRACT: role=<X> | preconditions=✅ | proceeding]` → activate role
- ANY missing → log `[CONTRACT BLOCK: role=<X> | missing=<artifact-path>]` → halt + prompt user
- After role completes → verify POSTCONDITION file(s) exist → log `[CONTRACT: role=<X> | postconditions=✅ | handoff to <next>]`

`Log format: [CONTRACT: role=<X> | pre=✅/❌ | post=✅/❌ | status=PASS/BLOCK]`

---

## LOOP SPEC APPROVAL (Fix 24E — DEVELOP phase, before first line of code)

**PRE-ACTIVATION: LESSONS SCAN (Fix 28B) — runs before every role activation:**
Before any role generates output, run:
> "Scan kiro/memory/lessons.md for entries WHERE domain matches current story labels [X, Y, Z].
>  Cite each applicable lesson explicitly: `[LESSON APPLIED: <lesson text> — source: sprint N]`
>  If no match: log `[LESSONS: no match for labels=[X,Y,Z]]` and proceed."
This step is MANDATORY and AUDITABLE. Silent lessons application is not permitted.
Log presence in role output header — if missing, SM must request re-run with lessons cited.

**Sequence (strict — no code before approval):**

1. `senior_engineer_be/fe` (maker) produces LOOP SPEC:
   - GOAL: falsifiable, references Acceptance Criteria directly
   - VERIFIER: all commands non-interactive and runnable
   - CRITERIA: ≥3 criteria, each sourced from a label's skill summary (Fix 23D)
   - Writes LOOP SPEC to $TRACKER story comment (or docs/phase-N/loop-states/[story-id].md)

2. `scrum_master` reviews loop spec (≤1 tool call — do NOT re-read all files):
   - Is GOAL falsifiable? (Can a machine verify it? Yes/No)
   - Is VERIFIER runnable? (Non-interactive commands? Yes/No)
   - Are CRITERIA ≥3 and label-sourced? (Yes/No)
   - If ALL YES → emit: `[LOOP SPEC APPROVED: story X]` → maker proceeds to DEVELOP
   - If ANY NO → return ONE specific objection → maker revises → auto-approve after 1 revision
   - SM does not write code. SM does not elaborate on criteria. One pass only.

3. After `[LOOP SPEC APPROVED: story X]` → maker begins PLAN→DO→CHECK→ACT loop.

**Token budget for approval step:** ~200 tokens SM input + ~100 tokens SM output = ~300 tokens total.
Do not exceed. This is a gate, not a review session.


## PHASE GATES — MANDATORY CHECKPOINTS

### GATE 1 — THINK → DESIGN
**Trigger:** market_researcher + cto artifacts complete.
**Checklist:**
- [ ] Personas have quoted JTBD statements (not paraphrased)
- [ ] TAM/SAM/SOM math shown with named sources
- [ ] At least 3 named competitors with concrete gaps
- [ ] Build-vs-buy table covers all 7 components with 3-yr TCO
- [ ] Approved vendor list is closed-set
- [ ] Risk register has 5 entries with mitigations

**Action:** Present artifacts. Ask: `"THINK complete. Confirm strategy to proceed to DESIGN?"` Wait for explicit YES. No implicit proceed.

---

### SCRUM MASTER — 4 ACTIVATION MODES (Fix 2)

`scrum_master` is never invoked as a single merged role. It activates in exactly ONE mode per call.
Each mode is a separate agent invocation. Never combine two modes in the same response.

```
SM-GATE    → Pre-build checklist ONLY (runs at GATE 2, before SM-PLAN).
             Reads: prebuild_documentation_gate.md skill
             Produces: VERDICT: GREEN or VERDICT: RED + named blockers list.
             Does NOT produce a sprint plan. Does NOT assign stories.
             If GREEN → handoff to SM-PLAN. If RED → block, name responsible role, stop.

             STRUCTURAL COMPLETENESS CHECK (Fix 32H) — runs as part of SM-GATE:
             Existence check (doc present?) AND structure check (required sections non-empty?).
             GATE 2 stays RED if ANY item below is missing or contains only placeholder text:

             Foundation Docs — Existence:
             - [ ] /docs/foundation/prd.md exists
             - [ ] /docs/foundation/architecture.md exists
             - [ ] /docs/foundation/app-flow.md exists
             - [ ] /docs/design_system.md (or design_system_mobile.md) exists
             - [ ] /docs/phase-N/db-architecture.md exists (or /docs/foundation/db-schema.md)
             - [ ] /docs/foundation/security-posture.md exists
             - [ ] /docs/foundation/testing-strategy.md exists
             - [ ] /docs/foundation/project-index.md exists

             PRD Structural Check:
             - [ ] Section 6 (Kiro Label Map) present and has ≥1 feature row
             - [ ] User stories use GIVEN/WHEN/THEN format (not "As a user I can…")
             - [ ] Success metrics contain numbers (not adjectives)
             - [ ] Anti-goals have reasons stated

             TRD Structural Check:
             - [ ] All tech decisions have constraint level (HARD/PREFERRED/EXPERIMENTAL)
             - [ ] Trust Boundary Map (Section 3) has ≥1 boundary documented
             - [ ] Skill File Hints (Section 6) has ≥1 component mapped

             App Flow Structural Check:
             - [ ] ≥1 screen documented with GIVEN/WHEN/THEN
             - [ ] Every screen has ERROR STATE documented
             - [ ] Every screen has EMPTY STATE documented
             - [ ] Critical User Journey List has ≥1 journey

             Design System Structural Check:
             - [ ] Design tokens present (colors + typography at minimum)
             - [ ] Component inventory has ≥1 component listed

             Backend Schema Structural Check:
             - [ ] ≥1 table has query patterns documented
             - [ ] ≥1 table has volume estimates
             - [ ] GDPR classification present for all tables with PII columns

             Security Posture Structural Check:
             - [ ] POSTURE_LEVEL declared (LOW/MEDIUM/HIGH)
             - [ ] PRIMARY_AUTH declared (resolves be/auth CHECKLIST ambiguity)
             - [ ] Compliance section non-empty (even if all=no — must be explicit)

             Testing Strategy Structural Check:
             - [ ] ≥1 test level declared in Section 1 (even if others are "none")
             - [ ] Coverage targets declared (even if "not enforced" — must be explicit)
             - [ ] ≥1 critical user journey in Section 5
             - [ ] Done Definition present for STANDARD stories (Section 6)

             Project Index Structural Check:
             - [ ] Foundation docs status table populated
             - [ ] Zero unresolved open questions blocking GATE 2
             - [ ] Zero unresolved doc conflicts

             If ALL items ✅ → VERDICT: GREEN → proceed to SM-PLAN.
             If ANY item 🔴 → VERDICT: RED | list each gap + responsible role + estimated effort.
             Log: `[GATE 2 STRUCTURAL CHECK: N/M items pass | Red gaps: <list> | VERDICT: GREEN/RED]`

SM-PLAN    → Sprint planning ONLY (runs AFTER SM-GATE returns GREEN).
             Reads: sprint_planning.md + velocity_capacity_modeling.md + estimation_techniques.md
             Produces: /docs/foundation/roadmap.md → /docs/phase-N/sprint-plan.md

             DOC-TO-DOC FLOW PROTOCOL (Fix 32I) — READ ORDER before creating any story:
               Step 1 → READ /docs/foundation/project-index.md
                         Check: current gate status + open questions blocking SM-PLAN.
                         If open questions block SM-PLAN → STOP. List blockers. Do not proceed.
                         OQ-RESOLVED AUTO-PROMPT (Fix 33B): When blocking, emit the following verbatim so the
                         user knows exactly what to type once OQs are resolved:
                         ---
                         ⏸ SM-PLAN blocked on [N] open questions. Once all OQs in project-index.md Section 4
                         are marked RESOLVED, reply with:
                           "All open questions resolved — resume SM-PLAN"
                         SM-PLAN will re-read project-index.md and continue from Step 1 automatically.
                         ---
                         Log: `[OQ-BLOCK: N open questions → SM-PLAN halted | auto-prompt emitted]`
                         On resume signal ("resume SM-PLAN" or "all OQs resolved"): re-read project-index.md,
                         confirm OQ count = 0, then continue from Step 2 without re-asking any questions.
               Step 2 → READ /docs/foundation/prd.md#kiro-label-map (Section 6)
                         Use Label Map table directly for story labels — do NOT infer from PRD prose.
                         If Label Map is missing → BLOCK SM-PLAN. Request cto to add Label Map section.
               Step 3 → READ /docs/foundation/app-flow.md
                         GIVEN/WHEN/THEN per screen → becomes loop spec acceptance criteria directly.
                         Error/empty/success states → added to story acceptance criteria.
               Step 4 → READ /docs/foundation/security-posture.md Section 3
                         Apply compliance auto-labels: HIPAA → [security-critical] on data/* stories.
                         Auto-flag: if GDPR=yes → all user-data stories get [be/pii].
               Step 5 → READ /docs/foundation/trd.md Section 6 (Skill File Hints)
                         Cross-check label assignments against TRD skill hints. Prefer TRD hints over inference.
               Log: `[DOC-FLOW: SM-PLAN | project-index ✅ | prd-label-map ✅ | app-flow ✅ | security-posture ✅ | trd-hints ✅ | source-of-truth confirmed]`

             DOC CONFLICT RESOLUTION (Fix 32G) — scan BEFORE creating stories:
               When two foundation docs contradict each other, apply precedence:
               WHAT to build       → PRD wins (PRD is the product contract)
               HOW to build it     → TRD wins (TRD is the technical contract)
               Data shape / schema → Backend Schema wins (schema is the data contract)
               UI behavior/states  → App Flow wins (App Flow is the UX contract)
               Security decisions  → security-posture.md wins unconditionally
               If conflict found: DO NOT guess resolution. Log to /docs/foundation/project-index.md Section 4.
               BLOCK SM-PLAN until conflict is resolved and project-index.md updated.
               Log: `[DOC-CONFLICT: <doc-A> says X | <doc-B> says Y | winner=<doc> | status=resolved/BLOCKED]`

             COMPLIANCE AUTO-LABELING (Fix 32J) — after reading security-posture.md Section 3:
               GDPR=yes     → any story touching user profile/email/session tables → add [be/pii]
               HIPAA=yes    → any story touching health data tables → add [security-critical]
               PCI-DSS=yes  → any story touching payment data → add [security-critical]
               SOC2=yes     → any story in devops/* lane → load operations/compliance-tracking skill
               Log: `[COMPLIANCE-AUTO-LABEL: GDPR=yes → +[be/pii] on 3 stories | HIPAA=no]`

             IAM SPRINT BUDGET PRE-WARNING (Fix 33A + FIX H-H) — after reading security-posture.md Section 3:
               If ANY of the following signals are present in PRD or TRD:
                 auth / identity / IAM / SSO / OAuth / SAML / SCIM / RBAC / MFA / session management / JWT
               → BEFORE creating stories, do TWO things:
               1. Emit this pre-warning in the response (so it's visible to the user):
               ⚠️ IAM BUDGET WARNING: Identity/auth scope detected. Auth stories routinely run 1.5–2× initial estimates.
                 Recommended actions:
                 1. Add +40% capacity buffer to every story with label [security/*] or [be/auth].
                 2. Break auth stories to ≤3 points each — no combined "auth + business logic" stories.
                 3. Create a dedicated sprint for IAM if scope includes SSO + MFA + RBAC simultaneously.
                 4. Flag any 3rd-party IdP integration (Okta, Auth0, AWS Cognito) as HIGH risk — add 1 spike story.
               2. **WRITE THE WARNING INTO docs/sprint-N/sprint-plan.md** (FIX H-H — MANDATORY):
                  Insert an "## IAM Budget Pre-Warning (Fix 33A)" section in sprint-plan.md with:
                  - Identified IAM stories + raw point total
                  - Effective burn estimate (raw × 1.5 → raw × 2)
                  - Remaining capacity calculation
                  - Specific recommendation (defer which story if IAM slips past day N)
                  - Machine-readable tag: `[IAM-WARNING: raw=Npts | effective=N–Npts | monitor <story-ids> daily]`
                  RULE: sprint-plan.md MUST contain the IAM Budget Pre-Warning section if IAM signals were detected.
                  After SM-PLAN, the sprint readiness review BLOCKS development if IAM signals exist in PRD/TRD but sprint-plan.md has no IAM warning section. The earlier SM-GATE does not require a sprint plan that has not yet been created.
               Log: `[IAM-BUDGET-WARN: signals=[auth,RBAC] → +40% buffer applied to N security/* stories | spike=yes/no | written to sprint-plan.md]`
               If NO auth signals → skip silently.

             E2E-REQUIRED FLAGGING (Fix 32K) — after reading testing-strategy.md Section 5:
               For each story: does it modify a screen/API listed in the Critical Journey List?
               YES → mark story as E2E-REQUIRED in $TRACKER | add note: "Playwright test required — see testing-strategy.md Journey N"
               NO  → E2E VERIFIER not required. Unit/integration sufficient.
               Log: `[E2E-REQUIRED: story=X touches Journey 1 (onboarding) → E2E flag set]`
                       + $TRACKER project/epic/story/subtask creation
                       + skill labels on every story (for Fix 9 activation)
             Does NOT run checklist. Does NOT review artifacts.
             LABEL REQUIREMENT (Fix 23B / Fix 24C): Every story MUST have ≥1 label from STORY LABEL TAXONOMY.
               - Assign primary lane label (be/*, fe/*, mobile/*, data/*, security/*, devops/*) FIRST
               - Add cross-cutting labels (testing/*, impl-decision, security-critical) if applicable
               - Format: story description includes `labels: [X, Y]` block
               SELF-GATE (Fix 24C): SM-PLAN validates labels IMMEDIATELY after story creation.
               Before emitting sprint-plan.md SM-PLAN runs:
                 For each story: does it have ≥1 taxonomy label? YES → continue. NO → BLOCK.
                 If ALL labeled: log [LABEL CHECK: N/N stories labeled ✅] → proceed to emit sprint-plan.md
                 If ANY unlabeled: log [LABEL BLOCK: story X missing labels — SM-PLAN halted]
                   → assign labels → re-validate → only then emit sprint-plan.md
               SM-PLAN cannot hand off to DEVELOP with unlabeled stories. This replaces the SM-GATE check.
               STRIDE EXCESS → MANDATORY TECH-DEBT STORIES (Fix 31E):
               After STRIDE-BRIDGE criteria are assigned (Fix 26D), if any mitigations were deferred
               due to the 2/story cap: SM-PLAN MUST create TECH-DEBT stories immediately.
                 Title: "TECH-DEBT: STRIDE [letter] mitigation — <threat description>"
                 Labels: [security-critical, tech-debt] | Priority: HIGH
                 Do NOT complete SM-PLAN without creating deferred-mitigation stories in $TRACKER.
               Log: `[STRIDE-DEFERRED: N excess mitigations → TECH-DEBT stories: TD-<N> created]`

               LABEL VALIDATION SELF-CHALLENGE (Fix 28D): After labeling, run 1-step check:
                 For each label assigned: "What specific skill or criterion does this label add
                 that isn't already covered by the other labels on this story?"
                 If answer is "nothing unique" → remove the label (redundant).
                 Log: `[LABELS VALIDATED: story=X | kept=[A,B] | removed=[C] | reason=<why>]`
                 Goal: prevent over-labeling (wrong skills loaded) and under-labeling (missing quality bar).

SM-RETRO   → Sprint retrospective ONLY (runs at GATE 4 — sprint end).
             Reads: retrospective_facilitation.md + velocity_capacity_modeling.md
             Produces: Sprint Discipline Card (FIRST — blocking, see SM-RETRO SPRINT DISCIPLINE CARD
                       section below) + retro doc (3 working / 3 improve / 3 actions) + velocity
                       update + Loop Engine Report (Fix 7) + next sprint seeded in $TRACKER
             BLOCKED until Sprint Discipline Card fully populated (all 5 rows — see section below).
             Rule: retro doc NOT produced until all 5 card rows have real data.
             A row cannot read "N/A" except for Token discipline on a Mode 3-only sprint.
             Does NOT plan. Does NOT gate.

SM-UNBLOCK → Mid-sprint blocker resolution ONLY.
             Reads: blocker_triage.md
             Trigger: Fix 7 hard stop at 8 iterations OR mid-sprint escalation
             Produces: Decision — one of: SCOPE-CUT / RE-SPEC / ESCALATE
             Format: "SM-UNBLOCK decision: [SCOPE-CUT / RE-SPEC / ESCALATE] — reason: [why]"
             Updates $TRACKER flags accordingly.
```

### SM-RETRO — SPRINT DISCIPLINE CARD (Fix 15C / Fix 16C)

BLOCKING RULE: SM-RETRO does not produce the retro doc until all 5 rows are populated with real data. A row cannot read "N/A" except for Token discipline on a Mode 3-only sprint.

| Dimension        | This sprint                                     | Target      | Status       |
|------------------|-------------------------------------------------|-------------|--------------|
| Velocity         | N / N planned points                            | ≥80%        | 🟢/🟡/🔴   |
| Token discipline | Peak / Good / Degrading / Critical              | GOOD+       | 🟢/🟡/🔴   |
| Git hygiene      | N direct commits to main, N PRs unreviewed      | 0 / 0       | 🟢/🟡/🔴   |
| $TRACKER sync    | N stories without tracker entries               | 0           | 🟢/🟡/🔴   |
| Test coverage    | N% (Δ from sprint start: ±N%)                  | ≥ mode tgt  | 🟢/🟡/🔴   |

**One sentence summary:** [e.g., "Sprint 2 hit velocity but token discipline degraded — 3 reads over budget on auth story."]
**Action for Sprint N+1:** [one concrete change]

---

**Gate 2 execution order — STRICT:**
1. Invoke `scrum_master` in SM-GATE mode → wait for VERDICT
2. If GREEN only → invoke `scrum_master` in SM-PLAN mode → produce roadmap + tracker items
3. Review the resulting sprint plan and story readiness before development; return missing items to their owners. This post-plan review must not require a second SM-PLAN to begin.
4. SM-GATE and SM-PLAN must NEVER appear in the same agent response

**POST-PLAN STORY READINESS CHECK (Fix 10B — loop spec quality bar):**
Before the first implementation line of each story, confirm:
- [ ] Every story has a loop spec authored (GOAL / VERIFIER / CRITERIA / STOP WHEN)
- [ ] Loop spec CRITERIA are derived from the story's skill outputs (not written from scratch)
- [ ] Loop spec VERIFIER is an automated command (not an opinion)
If a story is missing its loop spec → block that story's development and name the backend_lead or frontend_lead responsible. Do not require story loop specs during the earlier foundation gate, before stories have been planned.

**SM-GATE CHECKLIST ADDITION (Fix 15A — impl-decisions review):**
- [ ] `impl-decisions.md` from prior sprint reviewed? (N/A for Sprint 1 of a phase)
If prior sprint exists and impl-decisions.md is absent → SM-GATE returns RED. The implementing
role (backend_lead or frontend_lead) is named as responsible for the missing log.

---

### GATE 2 — DESIGN → DEVELOP (Pre-Build Gate)
**Trigger:** All DESIGN artifacts complete. SM-GATE runs pre-build checklist.
Skill: `.kiro/skills/scrum_master/prebuild_documentation_gate.md`
**Checklist:**
- [ ] PRD goals are outcome-shaped (not feature-shaped)
- [ ] Every user story passes INVEST
- [ ] Acceptance criteria use concrete values (no "fast", "intuitive")
- [ ] All ADRs have at least one rejected alternative documented
- [ ] All ADRs include Domain + Scope fields (Fix 25P): `Domain: <label e.g. be/auth>` and `Scope: global | component | service`. Binding rule: ADRs with Scope=global constrain all stories. Scope=component/service constrain only matching stories.
- [ ] **Every accepted ADR is logged in `kiro/memory/decisions.md`** (FIX H-A): Row format: `| ADR-NNN | Sprint N | <one-line decision> | <rationale> | <alternatives rejected> |`. GATE 2 BLOCKS if decisions.md is empty when ≥1 ADR exists in docs/adrs/.
- [ ] API contracts are concrete enough for FE+BE to build in parallel
- [ ] Schema DDL covers every entity in the PRD
- [ ] Security threat model covers every trust boundary
- [ ] STRIDE-BRIDGE (Fix 26D): After architect STRIDE, SM-PLAN extracts mitigations → adds ≤2 criteria per affected story loop spec. Log: `[STRIDE-BRIDGE: N mitigations → N criteria added]`
- [ ] Gantt v1 is acyclic, role-tagged, skill-tagged
- [ ] Foundation roadmap states available capacity assumptions or records them as unknown; the post-plan readiness review checks the sprint plan's velocity baseline and risk-adjusted capacity.
- [ ] Definition of Done defined per story, per sprint, per release
- [ ] Post-plan story readiness checks each story's loop spec, automated verifier and skill-derived criteria before implementation (Fix 10B); these artifacts are not required before SM-PLAN creates stories.

**If ANY item RED:** SM-GATE blocks. Names the role responsible. Does not proceed.
**If ALL GREEN:** SM-GATE announces `"VERDICT: GREEN — DESIGN approved."` Then SM-PLAN fires (separate call).

**FLOW STATE WRITE (FIX F):** Immediately on GATE GREEN, write `kiro/memory/flow.md`:
```
Current Sprint: 0 (pre-sprint)
Phase: DESIGN → DEVELOP transition
Gate Status: SM-GATE PASSED — DESIGN approved
Last updated: <YYYY-MM-DD HH:MM>
```
And append to `kiro/memory/checkpoint.md`:
```
| <YYYY-MM-DD HH:MM> | SM-GATE VERDICT: GREEN | COMPLETE | All DESIGN artifacts approved | docs/foundation/prd.md |
```
Log: `[FLOW: kiro/memory/flow.md written | gate=SM-GATE | status=GREEN]` `[CHECKPOINT: SM-GATE GREEN logged]`

**→ PRODUCE FOUNDATION ROADMAP (Scrum Master):**

Before Jira creation, `scrum_master` produces `/docs/foundation/roadmap.md` — the master execution plan:

```markdown
# Product Roadmap — [Product Name]

## Phase Overview
| Phase | Theme | Features | Sprints | Dependencies |
|-------|-------|----------|---------|--------------|
| 1 | [Foundation] | [Feature A, B, C] | 2 | None |
| 2 | [Advanced] | [Feature D, E, F] | 2 | Phase 1 complete |
| N | ... | ... | ... | ... |

## Phase 1 — [Theme]
### Features
| Feature | Epic | Stories | Priority | Sprint Assignment |
|---------|------|---------|----------|-------------------|
| Feature A | EPIC-001 | US-001, US-002 | HIGH | Sprint 1.1 |
| Feature B | EPIC-002 | US-003, US-004 | HIGH | Sprint 1.1, 1.2 |
| Feature C | EPIC-003 | US-005 | MEDIUM | Sprint 1.2 |

### Sprint Plan
| Sprint | Goal | Stories | Points | Risk |
|--------|------|---------|--------|------|
| 1.1 | [goal] | US-001, US-002, US-003 | 21 | LOW |
| 1.2 | [goal] | US-004, US-005 | 18 | MEDIUM |

## Phase 2 — [Theme]
(same structure)

## Cross-Phase Dependencies
| Dependency | From | To | Type | Risk if delayed |
|-----------|------|-----|------|-----------------|
| Auth system | Phase 1 / US-001 | Phase 2 / US-010 | Hard | Blocks all Phase 2 |

## Velocity Assumptions
- Baseline: X points/sprint
- Capacity: 80% (20% overhead)
- Buffer: 1 sprint per phase for carry-over
```

**This roadmap is the single source of truth for what goes where.** Each phase pulls its scope from this doc. It lives in foundation because it covers the entire product lifecycle.

**Rule:** When a phase starts, `scrum_master` reads only its section from the roadmap to produce the phase-specific sprint plan in `/docs/phase-N/sprint-plan.md`.

**→ CREATE JIRA ARTIFACTS via Jira MCP:**

**Step 1 — Project + Epics:** Use an existing user-selected project. Create a
new project or epics only if the user explicitly authorizes those actions.
```
If explicitly authorized: create epics for workstreams in the selected project.
```

**Step 2 — Stories (one per US-NNN, fully written):**

Every story MUST be created with this complete schema — no skeleton entries:
```
jira.createStory(
  epic       = <epic_id>,
  summary    = "US-NNN: <one-line outcome — not a feature description>",
  storyPoints = <N>,
  priority   = HIGH|MEDIUM|LOW,
  assignee   = <role_id>,
  sprint     = <N>,
  description = """
    ## Context
    <1-paragraph linking to persona + JTBD from market_research>

    ## Problem
    <what breaks today, how often, what it costs the user>

    ## Goal
    <outcome this story achieves — measurable>

    ## Acceptance Criteria
    **Given** <precondition>
    **When**  <action>
    **Then**  <observable result with concrete value>

    Edge case 1: <Given/When/Then>
    Edge case 2: <Given/When/Then>

    ## Non-goals
    <explicit list of what this story will NOT do>

    ## Dependencies
    <upstream stories or external blockers>

    ## Definition of Done
    - [ ] Code reviewed + merged
    - [ ] Unit + integration tests passing
    - [ ] Contract tests green
    - [ ] Deployed to staging
    - [ ] AC verified by QA
    - [ ] API docs updated (if applicable)
  """
)
```

**Step 3 — Sub-tasks (from Gantt v1):**
```
jira.createSubtask(
  story      = <story_id>,
  summary    = "<technical task name>",
  assignee   = <role_id>,
  labels     = [<skill_id_1>, <skill_id_2>],
  storyPoints = <N>,
  sprint     = <N>,
  description = "<implementation notes + acceptance signal>"
)
```

**Step 4 — Sprints:**
```
jira.createSprint(name="Sprint N", startDate=<ISO>, endDate=<ISO>, goal=<sprint-goal>)
jira.assignIssuesToSprint(sprint=N, issues=[...all stories + subtasks for this sprint...])
```

Report: Jira project URL + sprint board URL before proceeding.

---

## JIRA LIFECYCLE — CONTINUOUS UPDATES

Jira is not a one-time creation. Every status change, blocker, decision, and completion must be reflected immediately.

**Update triggers and required actions:**

| Event | Jira Action |
|---|---|
| Story moves to In Progress | `jira.transitionIssue(id, status="In Progress")` + add comment with sprint goal reminder |
| Blocker discovered | `jira.addComment(id, "BLOCKED: <what> — needs <who> — ETA <date>")` + `jira.flagIssue(id)` |
| Blocker resolved | `jira.addComment(id, "UNBLOCKED: <resolution>")` + `jira.unflagIssue(id)` |
| Design decision made (ADR) | `jira.addComment(id, "ADR-NNN decided: <one-line decision> — see kiro/memory/decisions.md")` **AND** write to `kiro/memory/decisions.md`: `\| ADR-NNN \| Sprint N \| <decision> \| <rationale> \| <alternatives rejected> \|` — Log: `[DECISIONS: ADR-NNN written to kiro/memory/decisions.md]` |
| Sub-task completed | `jira.transitionIssue(subtask_id, status="Done")` + `jira.addComment(story_id, "Sub-task <name> done by <role>")` |
| QA pass | `jira.addComment(id, "QA PASSED: coverage=X% · contracts=green · load=within targets · security=clean")` |
| QA fail | `jira.addComment(id, "QA FAILED: <specific failure> — returned to <role>")` + transition back to In Progress |
| PR opened | `jira.addComment(id, "PR: <url> — awaiting CI")` |
| PR merged + CI green | `jira.transitionIssue(id, status="Done")` + add commit summary comment (see below) |
| Sprint end | `jira.addComment(epic_id, "Sprint N retro: shipped=X/Y · velocity=Z pts · carry=N")` |

---

### GATE 3 — QA → COMMIT (per feature)
**Trigger:** QA engineer completes testing for a story.
**All must be GREEN:**
- [ ] Unit test coverage ≥ threshold set in sprint planning
- [ ] Contract tests pass
- [ ] No regression on guardrail metrics
- [ ] Load test within capacity targets from architecture
- [ ] Security scan: zero HIGH or CRITICAL findings
- [ ] Code review approved (no open blocking comments)

**If GREEN → COMMIT:**
```bash
git add <feature files only — no unrelated changes>
```

Commit message format — **complete session notes required**:
```
<type>(<scope>): <what was built — one line, ≤72 chars> [<JIRA-ID>]

## What
<2-4 sentences describing exactly what was implemented this session.
Be specific: endpoint names, component names, schema changes, config changes.>

## Why
<Link back to the user story and acceptance criteria this satisfies.>

## How
<Key technical decisions made. Reference any ADR numbers if applicable.>

## Tests
- Unit: <coverage %>  (<N> tests added)
- Integration: <pass/fail>
- Contract: <pass/fail>
- Load: <p95 latency> at <RPS> (target: <from architecture>)
- Security scan: <CLEAN / findings: N critical, N high — all resolved>

## Jira
- Story: <JIRA-ID> → Done
- Sub-tasks completed: <list>
- Next story: <JIRA-ID>

## Notes
<Anything future-you needs to know: known edge cases not covered, 
follow-up tasks, config changes needed in other envs, 
anything deferred to a later sprint with the Jira ID.>
```

Commit message types: `feat` | `fix` | `refactor` | `test` | `docs` | `chore`

```bash
git push origin feature/<jira-id>-<slug>
# Open PR — title: "<JIRA-ID>: <description>" (≤70 chars)
# PR description = commit body above (copy verbatim)
# Do NOT merge until CI pipeline is green
```
Update Jira: `jira.transitionIssue(id, "Done")` + add comment with PR URL after merge.

**If any item RED:** Return to the responsible role. Name the specific failure. Do not commit.

---
---

## STORY LABEL TAXONOMY (Fix 23A)

Every sprint story MUST carry ≥1 label from this list. Labels are the input for dynamic skill resolution (Fix 23C).
SM-PLAN assigns labels at story creation. SM-PLAN SELF-BLOCKS if any story has zero labels (Fix 24C). The post-plan readiness review confirms the labels before development.
Format in $TRACKER / markdown: `labels: [be/api, be/resilience]`  (array, 1–4 labels per story)
Rule: primary lane label REQUIRED; cross-cutting labels optional if clearly applicable.

### Backend lane
| Label          | When to use |
|----------------|-------------|
| be/api         | REST/GraphQL endpoint, API contract, request/response schema |
| be/caching     | Redis, Memcached, cache invalidation, TTL strategy |
| be/queue       | Kafka, SQS, RabbitMQ, message broker, event publishing |
| be/database    | DB queries, ORM, schema reads/writes, stored procedures |
| be/resilience  | Circuit breaker, retry, saga, idempotency, rate limiting |
| be/auth        | Authentication, authorization, JWT, OAuth, session management |
| be/pii         | PII handling, data scrubbing, privacy-preserving operations |
| be/ml          | ML inference, embedding generation, model serving, vector ops |

### Frontend lane
| Label          | When to use |
|----------------|-------------|
| fe/component   | UI components, React/Vue/Svelte, styling, layout |
| fe/form        | Form validation, multi-step flows, input UX patterns |
| fe/state       | State management, store design, reactivity |
| fe/a11y        | Accessibility, ARIA, keyboard navigation, screen reader |
| fe/perf        | Web vitals, bundle size, lazy loading, rendering performance |

### Mobile lane
| Label          | When to use |
|----------------|-------------|
| mobile/ios     | Swift/UIKit/SwiftUI, iOS-specific patterns |
| mobile/android | Kotlin/Jetpack, Android-specific patterns |
| mobile/rn      | React Native, cross-platform, Expo |
| mobile/offline | Offline sync, local storage, conflict resolution |

### Data lane
| Label           | When to use |
|-----------------|-------------|
| data/pipeline   | ETL, batch processing, dbt, data warehouse loading |
| data/streaming  | Kafka Streams, Spark Streaming, Flink, CDC |
| data/modeling   | Data model design, dimensional modeling, schema evolution |
| data/eda        | Exploratory analysis, statistical analysis, visualization |

### Security lane
| Label            | When to use |
|------------------|-------------|
| security/auth    | Auth implementation, token handling, RBAC |
| security/pii     | PII detection, scrubbing, retention policies, GDPR |
| security/review  | Security code review, OWASP check, threat validation |
| security/secrets | Secrets management, Vault, env var hygiene |

### DevOps lane
| Label          | When to use |
|----------------|-------------|
| devops/k8s     | Kubernetes deployment, Helm charts, pod config, scaling |
| devops/ci      | CI/CD pipeline, GitHub Actions, build/test automation |
| devops/infra   | IaC, Terraform, cloud resources, networking |
| devops/monitor | Observability, metrics, tracing, alerting, dashboards |

### Testing (any lane)
| Label                | When to use |
|----------------------|-------------|
| testing/unit         | Unit tests, mocking, test isolation |
| testing/integration  | Integration tests, test containers, DB fixtures |
| testing/e2e          | End-to-end tests, browser automation, full flow coverage |
| testing/contract     | Contract tests, pact, consumer-driven contracts |

### Cross-cutting
| Label             | When to use |
|-------------------|-------------|
| impl-decision     | Non-trivial algorithm/library/pattern choice → auto-creates impl-decisions.md entry |
| security-critical | Any story touching auth/payments/PII/secrets → triggers security_engineer DEVELOP pass (Fix 22D) |
| cross-domain      | Story spans ≥2 lanes and no single lane label fits cleanly |

