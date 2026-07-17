# Loop Engineering — Complete System Flow
> Every agent, gate, discipline, and tool from prompt to shipped product.
> Last updated: 2026-07-17

---

```
╔══════════════════════════════════════════════════════════════════════════════════╗
║              LOOP ENGINEERING — END-TO-END SYSTEM FLOW                         ║
║              prompt → hook → discovery → mode → think → sprint → done          ║
╚══════════════════════════════════════════════════════════════════════════════════╝
```

---

## 1. PROMPT ENTERS → HOOK

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  HOOK  ·  elite-team-orchestrator.kiro.hook                                      │
├──────────────────────────────────────────────────────────────────────────────────┤
│  STORY: The first thing that runs on every prompt, before any agent activates.   │
│  It is the immune system of the session — it catches drift before work starts.   │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  READS:                                                                          │
│    kiro/memory/checkpoint.md        → resume vector (which files + lines to open)       │
│    kiro/memory/lessons.md           → domain-scoped lessons only (not full file)        │
│    kiro/steering/session-guards.md  → GUARD 0–3 definitions                     │
│                                                                                  │
│  DOES:                                                                           │
│    ① ENV detection: Kiro native / Claude Projects / ChatGPT adapter             │
│    ② Open ONLY resume vector files from checkpoint (not full codebase)          │
│    ③ GUARD 0: constraint drift check                                            │
│       Compare today's constraints vs last session's checkpoint                   │
│       If drift detected → surface conflict, ask user to resolve before work      │
│    ④ Domain-scoped lessons: extract task domain label from prompt               │
│       auth task   → load F05, F06, F11 nodes only                               │
│       data task   → load F08, F09 nodes only                                    │
│       deploy task → load F06 node only                                           │
│       Prevents full-file haystack scan (anti-pattern from Rakesh Gohel research) │
│    ⑤ Degrade gracefully: PEAK(0-4 reads) → GOOD → DEGRADING → CRITICAL         │
│                                                                                  │
│  PRODUCES:                                                                       │
│    Oriented session context — constraints confirmed, lessons loaded, files open  │
│    Mode recommendation passed to DISCOVERY ENGINE                                │
│                                                                                  │
│  GIT:  no action     JIRA:  no action                                           │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. DISCOVERY ENGINE

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  DISCOVERY ENGINE  ·  discovery-engine.md                                        │
├──────────────────────────────────────────────────────────────────────────────────┤
│  STORY: Scores the incoming request before any agent spends a token on it.       │
│  Prevents over-engineering trivial tasks and under-resourcing complex ones.      │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  READS:   Prompt text + any attached PRD/spec                                    │
│                                                                                  │
│  SCORES (1–10 complexity):                                                       │
│    +2  Auth / RBAC / multi-tenant in scope                                       │
│    +2  DB migrations or schema changes                                           │
│    +1  External integrations (payment, email, OAuth)                             │
│    +1  Mobile platform in scope                                                  │
│    +1  Real-time / websocket / concurrency                                       │
│    +1  ML / embeddings / model serving                                           │
│    +1  No PRD exists yet                                                         │
│                                                                                  │
│  CONFIDENCE CALIBRATION:                                                         │
│    HIGH   → clear PRD, known stack, no ambiguous requirements                   │
│    MEDIUM → partial PRD, some unknowns, mixed signals                            │
│    LOW    → no PRD, first-time domain, conflicting signals                       │
│             LOW confidence → must ask before proceeding, not guess               │
│                                                                                  │
│  OUTPUTS:                                                                        │
│    Score + confidence + recommended Mode → passed to MODE ROUTING                │
│                                                                                  │
│  GIT:  no action     JIRA:  no action                                           │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. MODE ROUTING

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  MODE ROUTING  ·  orchestrator-routing.md                                        │
├──────────────────────────────────────────────────────────────────────────────────┤
│  STORY: Selects the right team size for the job. No overhead for trivial work.   │
│  No under-resourcing for complex or security-sensitive work.                     │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  MODE 1 — Full Army  (score 7–10, LOW confidence)                               │
│    All 22 agents active. Full gate sequence. Used for:                           │
│    greenfield products, auth-heavy features, enterprise SaaS, multi-tenant apps  │
│    Agents: CTO, ARCHITECT, DB_ARCHITECT, SECURITY_ENGINEER, BACKEND_LEAD,       │
│            FRONTEND_LEAD, SENIOR_BE, SENIOR_FE, ML_ENGINEER, DATA_ENGINEER,     │
│            MOBILE_ENGINEER, DATA_SCIENTIST, DEVOPS_ENGINEER, SRE_ENGINEER,      │
│            QA_ENGINEER, SCRUM_MASTER, TECHNICAL_WRITER, MARKET_RESEARCHER,      │
│            UX_RESEARCHER, WEBSITE_CREATOR, SECURITY_AUDITOR, COMPLIANCE_OFFICER │
│                                                                                  │
│  MODE 2 — Standard Team  (score 4–6, MEDIUM confidence)                         │
│    ~10 agents active. Core disciplines only. Used for:                           │
│    feature additions to existing product, moderate complexity                    │
│    Agents: ARCHITECT, BACKEND_LEAD, FRONTEND_LEAD, SENIOR_BE, SENIOR_FE,       │
│            QA_ENGINEER, SCRUM_MASTER, DEVOPS_ENGINEER, TECHNICAL_WRITER         │
│                                                                                  │
│  MODE 3 — Direct Fix  (score 1–3, HIGH confidence)                              │
│    Builder only. No orchestration overhead. Used for:                            │
│    bugfixes, trivial changes, single-file edits, known patterns                  │
│    Agents: SENIOR_BE or SENIOR_FE (whichever matches task)                       │
│                                                                                  │
│  MODE 4 — Research  (R&D tasks)                                                  │
│    Researcher only. No code output. Used for:                                    │
│    technology evaluation, competitor analysis, feasibility studies               │
│    Agents: MARKET_RESEARCHER, UX_RESEARCHER                                      │
│                                                                                  │
│  MODE 5 — Lean  (fast iteration, low complexity, HIGH confidence)                │
│    Single builder, minimal overhead. Used for:                                   │
│    solo developer, fast prototyping, well-understood tasks                       │
│    Agent: BUILDER (SENIOR_BE or SENIOR_FE)                                       │
│    ⚠️  FIX 44A: if story has label security/rbac/auth/multi-tenant →            │
│         ADVISORY EMITTED before builder activates:                               │
│         Option A: continue, cross-tenant test MUST be in VERIFIER                │
│         Option B: switch to Mode 1 or 2 — HOLD until user acknowledges          │
│                                                                                  │
│  GIT:  no action     JIRA:  no action                                           │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. THINK PHASE

### 4A. CTO

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  CTO  ·  kiro/skills/cto/  ·  Active: Mode 1, Mode 2                            │
├──────────────────────────────────────────────────────────────────────────────────┤
│  STORY: Sets the strategic ceiling before engineering begins. Prevents scope     │
│  creep (F03) by defining what the product IS and IS NOT from the start.         │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  READS:   Prompt, any existing product context                                   │
│                                                                                  │
│  DOES:                                                                           │
│    • Strategic alignment: does this fit OKRs / product vision?                  │
│    • Build vs Buy decision: should this be built or integrated?                  │
│    • Market positioning: who is this for, what's the differentiator?            │
│    • Non-goals explicitly declared (prevents F03 scope creep)                   │
│                                                                                  │
│  PRODUCES:                                                                       │
│    prd_template.md → PRD: goals, non-goals, user personas, success metrics      │
│                                                                                  │
│  JIRA:  Epic created from PRD    GIT:  no action                                │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### 4B. ARCHITECT

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  ARCHITECT  ·  kiro/skills/architect/  ·  Active: Mode 1, Mode 2                │
├──────────────────────────────────────────────────────────────────────────────────┤
│  STORY: Translates the PRD into a buildable system. Owns all structural          │
│  decisions. Also owns the product-graph.yaml update at every sprint close.      │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  READS:   PRD (from CTO), any existing TRD                                       │
│                                                                                  │
│  DOES:                                                                           │
│    • System design: services, modules, boundaries, APIs                          │
│    • Trust boundary map: what can call what, what is public vs internal          │
│    • Constraint levels:                                                          │
│        HARD = never change (e.g. HIPAA data residency)                          │
│        SOFT = change with approval (e.g. caching strategy)                      │
│    • ADRs (Architecture Decision Records) for every non-obvious choice          │
│    • App flow: user journey → system path → data flow                           │
│    • Security posture level: HIGH / MEDIUM / LOW → drives STRIDE depth          │
│    ── AT GATE 5 (every sprint close) ──                                          │
│    • Reads sprint diff: new files, new deps, new ADRs                           │
│    • Appends nodes + edges to docs/product-graph.yaml                           │
│    • Regenerates docs/product-graph.html (D3 interactive viz)                   │
│                                                                                  │
│  PRODUCES:                                                                       │
│    trd_template.md (TRD)   app_flow_template.md   security_posture_template.md  │
│    docs/product-graph.yaml + docs/product-graph.html  (at sprint close)         │
│                                                                                  │
│  GIT:  commits TRD + app flow    JIRA:  no action                               │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### 4C. DATABASE_ARCHITECT

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  DATABASE_ARCHITECT  ·  kiro/skills/database_architect/  ·  Active: Mode 1, 2   │
├──────────────────────────────────────────────────────────────────────────────────┤
│  STORY: Designs the data layer before any code is written. Query-first approach  │
│  prevents the common failure of designing schema before knowing access patterns. │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  READS:   TRD (from ARCHITECT), PRD user stories                                 │
│                                                                                  │
│  DOES:                                                                           │
│    • Query-first design: define the queries first, then schema                   │
│    • No premature indexing: only index what access patterns prove                │
│    • GDPR field annotations: PII fields marked, retention policy attached        │
│    • STRIDE annotations: threat model on sensitive tables                        │
│    • Transactional vs analytical split decision                                  │
│    • Migration strategy: how to get from current state to target schema          │
│                                                                                  │
│  PRODUCES:                                                                       │
│    database_schema_design.md   migration_plan.md                                 │
│                                                                                  │
│  GIT:  commits schema + migration files    JIRA:  DB stories created            │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. GATE 2 — Structural Completeness

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  GATE 2  ·  team-orchestrator-sprint.md  ·  BLOCKS sprint start if any fail     │
├──────────────────────────────────────────────────────────────────────────────────┤
│  STORY: Nothing gets built without the foundation docs. Gate 2 is the contract  │
│  that engineering cannot start until strategy and design are complete.           │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  CHECKLIST (all must pass):                                                      │
│    ✓  PRD exists and has non-goals declared                                      │
│    ✓  TRD exists with HARD/SOFT constraint levels                                │
│    ✓  App flow documented                                                        │
│    ✓  Design system declared (token source, component library)                   │
│    ✓  Database schema + migration plan present (if DB in scope)                  │
│    ✓  Security posture level declared                                            │
│    ✓  Testing strategy defined (coverage threshold, E2E scope)                  │
│    ✓  Doc conflicts resolved (if TRD contradicts PRD → explicit decision logged) │
│                                                                                  │
│  ON FAIL:  BLOCK — identify which doc is missing → route back to correct agent  │
│  ON PASS:  Sprint planning begins                                                │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. SPRINT LOOP — SM-PLAN

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  SM-PLAN  ·  SCRUM_MASTER  ·  kiro/steering/team-orchestrator-core.md           │
├──────────────────────────────────────────────────────────────────────────────────┤
│  STORY: Translates the TRD into sprint-sized stories with clear labels.          │
│  The label is the routing key — wrong label = wrong agent = wrong skills loaded. │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  READS:   TRD, PRD, app flow, project_index.md, impl-decisions.md               │
│                                                                                  │
│  DOES:                                                                           │
│    • Story breakdown: TRD sections → sprint stories                              │
│    • Story sizing: S (< 2h) / M (half day) / L (full day) / XL (multi-day)     │
│    • Label assignment (determines discipline routing):                           │
│        be/auth         → auth/RBAC/session work                                 │
│        be/api          → REST/GraphQL endpoint work                             │
│        be/data         → data processing, ETL                                   │
│        fe/component    → UI component work                                       │
│        fe/layout       → page layout, routing                                   │
│        data/pipeline   → data pipeline, streaming                               │
│        data/ml         → model training, feature engineering                    │
│        mobile/ios      → iOS-specific work                                       │
│        mobile/android  → Android-specific work                                  │
│        infra/deploy    → deployment, CI/CD                                       │
│        security-critical → triggers property-based testing                      │
│        e2e-required    → triggers E2E test suite                                │
│    • IAM budget pre-warning: if auth stories > 40% sprint capacity → flag early  │
│    • OQ-resolved auto-prompt: if open question from last sprint resolved → auto  │
│      trigger doc-to-doc update (TRD → schema or schema → app flow)              │
│                                                                                  │
│  PRODUCES:                                                                       │
│    Sprint backlog with labeled stories + acceptance criteria                     │
│                                                                                  │
│  JIRA:  Stories created, sprint board populated, sprint started                  │
│  GIT:   feature/sprint-N branch cut from main                                   │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. DEVELOP PHASE — Discipline Routing

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  SKILL ROUTING  ·  skill-label-index.md + skill-selection-matrix.md             │
├──────────────────────────────────────────────────────────────────────────────────┤
│  STORY: Story label → agent assignment + skill file load. Surgical activation.  │
│  Only the skills relevant to THIS story are loaded. No broad context reads.     │
└──────────────────────────────────────────────────────────────────────────────────┘

  Label: be/auth
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  Agents:  BACKEND_LEAD + SECURITY_ENGINEER                                  │
  │  Skills:  auth_patterns.md, webauthn_fido2.md, scim_protocol.md            │
  │           security_posture_template.md (referenced for STRIDE depth)        │
  │  Guards:  GUARD 2 (auth scope), GATE S2 cross-tenant test                  │
  │  Watches: F05 (auth scope violation), F11 (cross-tenant blindspot)          │
  └─────────────────────────────────────────────────────────────────────────────┘

  Label: be/api
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  Agents:  BACKEND_LEAD                                                      │
  │  Skills:  api_design.md, rate_limiting.md, idempotency.md                  │
  │  Watches: F03 (scope creep — API contract must match TRD)                  │
  └─────────────────────────────────────────────────────────────────────────────┘

  Label: fe/component
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  Agents:  FRONTEND_LEAD                                                     │
  │  Skills:  component_architecture.md                                         │
  │  Prereq:  design_system_gate.md MUST pass first (design system declared?)  │
  │  Watches: F10 (ponytail violation — new UI lib when design system exists)   │
  └─────────────────────────────────────────────────────────────────────────────┘

  Label: data/pipeline
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  Agents:  DATA_ENGINEER                                                     │
  │  Skills:  pipeline_patterns.md, analytical_datastore_patterns.md           │
  │           (ClickHouse/Cassandra/DynamoDB for analytical workloads)          │
  │  Watches: F08 (memory rot — pipeline configs not documented)                │
  └─────────────────────────────────────────────────────────────────────────────┘

  Label: data/ml
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  Agents:  ML_ENGINEER + DATA_SCIENTIST                                      │
  │  Skills:  ml_serving_and_embeddings.md, feature_engineering.md             │
  │  Watches: F07 (comprehension theater — model eval rubber-stamped)           │
  └─────────────────────────────────────────────────────────────────────────────┘

  Label: mobile/*
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  Agents:  MOBILE_ENGINEER  (force-activated even in Mode 5 — Fix 38B)      │
  │  Skills:  mobile_patterns.md, responsive_design.md                         │
  │  Watches: F03 (scope creep to non-mobile platform features)                 │
  └─────────────────────────────────────────────────────────────────────────────┘

  Label: infra/deploy
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  Agents:  DEVOPS_ENGINEER + SRE_ENGINEER                                   │
  │  Skills:  deployment_patterns.md, incident_runbook.md                      │
  │  Guards:  GATE S3 (no self-trigger — human must approve deploy)            │
  │  Watches: F06 (deployment self-trigger)                                     │
  └─────────────────────────────────────────────────────────────────────────────┘

  Label: security-critical
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  Agents:  SECURITY_ENGINEER added to whatever agent owns the story         │
  │  Skills:  property_based_testing.md (required), webauthn_fido2.md          │
  │  Watches: F05, F11 — both guards on high alert                             │
  └─────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. PONYTAIL CHECK

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  PONYTAIL CHECK  ·  ponytail.md + disqualification-guide.md  ·  Fix 43B         │
├──────────────────────────────────────────────────────────────────────────────────┤
│  STORY: Fires before any new dependency is added. The ladder must be exhausted  │
│  in order. Skipping a rung is a policy violation, not a judgment call.          │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  THE LADDER (top to bottom — must try each before descending):                   │
│    ① stdlib / language built-in available?           → USE IT, stop             │
│    ② existing project dependency covers this?        → USE IT, stop             │
│    ③ 5-line utility function does the job?           → WRITE IT, stop           │
│    ④ proven, widely-adopted library (npm top 1000)?  → ADD IT, document why    │
│    ✗ new/niche/unknown package                       → BLOCK + log F10          │
│                                                                                  │
│  DISQUALIFICATION TRIGGERS (auto-block regardless of rung):                     │
│    • Package < 1000 weekly downloads                                            │
│    • Last commit > 18 months ago                                                │
│    • No LICENSE file                                                            │
│    • Name-squatting / typosquatting pattern                                     │
│    • Does only one thing that stdlib already does                               │
│                                                                                  │
│  ON VIOLATION:  Log F10 (Ponytail Violation) → BLOCK → suggest alternative     │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. IMPLEMENTATION

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  SENIOR_ENGINEER_BE / SENIOR_ENGINEER_FE  ·  Active in all Modes                │
├──────────────────────────────────────────────────────────────────────────────────┤
│  STORY: The hands. Execute the story against TRD constraints. No autonomy       │
│  beyond what the story explicitly asks for. Deviation = impl-decisions.md entry.│
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  READS:   Story acceptance criteria, TRD, skill files for this label            │
│                                                                                  │
│  RULES:                                                                          │
│    • Change ONLY what the story requires — no drive-by improvements             │
│    • No adding comments, types, or docstrings to unchanged code                 │
│    • No new dependency without passing PONYTAIL CHECK first                     │
│    • Any deviation from TRD → log in impl-decisions.md with reason             │
│    • GUARD 3: if working with image-compressed context (pxpipe) →              │
│        re-verify exact strings (SHAs, identifiers, file:line) before use       │
│                                                                                  │
│  PRODUCES:                                                                       │
│    Working code committed to feature/sprint-N                                    │
│    impl-decisions.md updated for any TRD deviations                             │
│                                                                                  │
│  GIT:   commits to feature/sprint-N    JIRA:  story → In Progress              │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. VERIFIER

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  VERIFIER  ·  QA_ENGINEER  ·  Fix 27C: tests MUST run — no assume-green        │
├──────────────────────────────────────────────────────────────────────────────────┤
│  STORY: VERIFIER is the only agent that can declare a story done. No agent      │
│  that wrote the code can declare their own code correct. Separation enforced.   │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  READS:   testing_strategy_template.md, story acceptance criteria               │
│                                                                                  │
│  DOES:                                                                           │
│    • Run tests — not review them, RUN them. Output required as evidence.        │
│    • Coverage check vs testing_strategy.md declared threshold                   │
│    • If label = e2e-required → E2E suite must run                               │
│    • If label = security-critical → property-based test suite must run          │
│    • If label = fe/* with browser → Lighthouse --assert must run (Fix 31B)     │
│    • Concurrency test if label = real-time/* (race detector, Promise.all)       │
│                                                                                  │
│  PRODUCES:                                                                       │
│    Test output committed as evidence    Coverage report                          │
│    PASS: story moves to GATE S2                                                  │
│    FAIL: story back to SENIOR_ENGINEER with exact failure output                │
│                                                                                  │
│  GIT:   test results committed    JIRA:  story → In Review                     │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 11. GATE S2 — Security Gate

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  GATE S2  ·  NON-BYPASSABLE  ·  kiro/steering/session-guards.md                 │
├──────────────────────────────────────────────────────────────────────────────────┤
│  STORY: The security gate that cannot be switched off in any mode.              │
│  Even Mode 5 Lean must pass GATE S2. No exceptions, no "we'll do it later."    │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  CHECKLIST (all must pass — any single failure blocks):                          │
│    ① Auth scope contained?                                                      │
│         No privilege escalation. User can only access their own resources.       │
│         Fails → log F05 (Auth Scope Violation) → BLOCK                          │
│    ② Cross-tenant access-denial test present? (Fix 43C)                         │
│         If story touches multi-tenant data: test that tenant A cannot read B    │
│         Fails → log F11 (Cross-Tenant Blindspot) → BLOCK                        │
│    ③ Ponytail check passed?                                                     │
│         No unreviewed new dependencies in this story                            │
│         Fails → log F10 (Ponytail Violation) → BLOCK                            │
│    ④ STRIDE threats either mitigated or TECH-DEBT story created?               │
│         Unmitigated excess threats must have a Priority HIGH TECH-DEBT story    │
│         Fails → BLOCK                                                           │
│    ⑤ Mode 5 + security label: Fix 44A advisory acknowledged?                   │
│         Must be on record before gate passes                                    │
│         Not acknowledged → HOLD                                                  │
│                                                                                  │
│  ON PASS:  Story proceeds to GATE S3                                             │
│  ON FAIL:  Sprint cannot close — surface exact failure item to user             │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 12. GATE S3 — Deployment Gate

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  GATE S3  ·  NON-BYPASSABLE  ·  kiro/steering/session-guards.md                 │
├──────────────────────────────────────────────────────────────────────────────────┤
│  STORY: Agents cannot deploy themselves. Ever. Full stop. This gate exists      │
│  because deployment self-trigger (F06) is the most catastrophic failure mode.  │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  CHECKLIST:                                                                      │
│    ① No self-trigger: agent CANNOT call deploy/release/publish without          │
│       explicit human instruction in THIS session (not "you said it was OK       │
│       last session" — prior sessions do not count)                              │
│    ② Human approval token present before any production deployment              │
│       Token = explicit user message: "deploy this" / "ship it" / "go to prod"  │
│    ③ Rollback plan documented in impl-decisions.md                             │
│       What command reverts this? Who is paged if it fails?                     │
│                                                                                  │
│  ON PASS:  Deployment may proceed (human initiates)                             │
│  ON FAIL:  HARD BLOCK — log F06 (Deployment Self-Trigger) if agent attempted  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 13. SM-RETRO

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  SM-RETRO  ·  SCRUM_MASTER  ·  kiro/steering/team-orchestrator-core.md          │
├──────────────────────────────────────────────────────────────────────────────────┤
│  STORY: The retrospective that writes institutional memory. Every failure mode  │
│  caught this sprint gets a lesson node. Every lesson is timestamped + labeled. │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  DOES:                                                                           │
│    • Comprehension debt score (Fix 41B):                                        │
│        Did any agent approve an artifact it did not actually read?              │
│        Score 0–10. Score > 6 → mandatory remediation before next sprint        │
│        Catches F07 (Comprehension Theater)                                       │
│    • Ralph Wiggum trap check (Fix 40D):                                        │
│        Did any agent say "I don't know" when it should have?                   │
│        vs did any agent fake understanding and proceed anyway?                  │
│        Fake understanding → logged, forces explicit acknowledgment next sprint  │
│    • Failure mode log: which F01–F12 were triggered this sprint?               │
│    • Lessons written to lessons.md (5-stage progression — Fix 40A):            │
│        Stage 1: OBSERVED (raw note)                                             │
│        Stage 2: CONFIRMED (happened twice)                                      │
│        Stage 3: GUARDED (guard added to steering file)                          │
│        Stage 4: TESTED (dry run confirmed guard works)                          │
│        Stage 5: RETIRED (guard works, no longer needs active monitoring)        │
│    • Sprint velocity logged: stories completed vs planned                       │
│                                                                                  │
│  PRODUCES:                                                                       │
│    Lessons appended to lessons.md    Sprint velocity note in checkpoint         │
│                                                                                  │
│  JIRA:  Stories closed    GIT:  no direct action                                │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 14. GATE 5 — Sprint Close

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  GATE 5  ·  kiro/steering/team-orchestrator-sprint.md  ·  NON-BYPASSABLE        │
├──────────────────────────────────────────────────────────────────────────────────┤
│  STORY: The sprint does not close until the product graph is updated.            │
│  ARCHITECT writes the structural record. TECHNICAL_WRITER writes the narrative. │
│  Git is clean. Jira is closed. Checkpoint is updated. Then and only then: done. │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  CHECKLIST (all must pass):                                                      │
│    ✓  All stories verified by VERIFIER (not self-verified by implementer)        │
│    ✓  GATE S2 passed for all stories                                            │
│    ✓  GATE S3 respected (no self-triggered deploy)                              │
│    ✓  impl-decisions.md up to date (all TRD deviations logged)                 │
│    ✓  ARCHITECT: product-graph.yaml updated with sprint diff                    │
│         New nodes: components, services, modules created this sprint            │
│         New edges: depends_on, implements, decides relationships                │
│         New decisions: ADRs from this sprint appended                           │
│    ✓  ARCHITECT: docs/product-graph.html regenerated (D3 interactive viz)      │
│    ✓  TECHNICAL_WRITER: sprint summary written referencing product-graph.html   │
│    ✓  checkpoint.md updated with resume vector for next session                 │
│                                                                                  │
│  GIT:  PR opened → reviewed → merged to main → tag: sprint-N-complete          │
│  JIRA: Sprint closed, Epic progress updated, velocity logged                    │
│                                                                                  │
│  LOOP:  More stories in backlog? → back to SM-PLAN for next sprint             │
│         All done? → DONE state (see below)                                      │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 15. DONE STATE

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  DONE                                                                            │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  docs/product-graph.html    Living architecture map of everything built         │
│  kiro/memory/checkpoint.md         Resume vector — any new session picks up instantly  │
│  kiro/memory/lessons.md            All failure modes caught, guards applied, staged     │
│  kiro/specs/                All stories, acceptance criteria, impl decisions     │
│  Git: main branch           Production-ready, all sprints merged                │
│  Jira: Epic closed          All stories done, velocity logged                   │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 16. GUARDS — Always Active

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  GUARDS  ·  kiro/steering/session-guards.md  ·  Run in ALL modes, ALL sprints   │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  GUARD 0 — Constraint Drift                                                     │
│    When:  Every session start                                                    │
│    Does:  Compare today's active constraints vs checkpoint from last session    │
│    Catch: F02 (Constraint Drift) — decisions made session N gone by session N+1│
│    On trigger: surface conflict, ask user to resolve before any work starts     │
│                                                                                  │
│  GUARD 1 — Lessons Scan                                                         │
│    When:  Every session start, before any build work                            │
│    Does:  Load ONLY domain-scoped lesson nodes (not full lessons.md)           │
│    Catch: F08 (Memory Rot), F09 (Lesson Age Inflation)                         │
│    Why:   Full-file scan = probabilistic haystack. Context graph = surgical.    │
│                                                                                  │
│  GUARD 2 — Auth Scope                                                           │
│    When:  Any story touching auth / payments / user-data                        │
│    Does:  HARD BLOCK — human gate required before any auth change proceeds      │
│    Catch: F05 (Auth Scope Violation)                                            │
│    On trigger: HOLD — do not proceed until explicit human acknowledgement       │
│                                                                                  │
│  GUARD 3 — Image Exact-String  (pxpipe / image-compressed context)             │
│    When:  Any exact string extracted from image-compressed context              │
│    Does:  Flag → require re-verification before use in code or commands        │
│    Catch: F12 (Compression Confabulation) — 11–17% silent misread rate         │
│    Types: git SHAs, camelCase identifiers, file:line refs, semver strings      │
│    Post-guard accuracy: 99.3% (vs 84.7% without guard)                         │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 17. FAILURE MODES — F01–F12

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  FAILURE MODES  ·  What goes wrong in production — and what catches each one    │
├────┬───────────────────────┬─────────────────────────────────────────────────────┤
│ ID │ Name                  │ Caught By                                           │
├────┼───────────────────────┼─────────────────────────────────────────────────────┤
│F01 │ Context Amnesia       │ GUARD 0 + checkpoint resume vector                  │
│    │ Constraints forgotten │ Hook re-establishes context from checkpoint         │
│    │ within a session      │                                                     │
├────┼───────────────────────┼─────────────────────────────────────────────────────┤
│F02 │ Constraint Drift      │ GUARD 0 cross-session comparison                    │
│    │ Decisions lost        │ Diff today vs last checkpoint → surface conflict    │
│    │ between sessions      │                                                     │
├────┼───────────────────────┼─────────────────────────────────────────────────────┤
│F03 │ Scope Creep           │ SM-PLAN story boundaries + PRD non-goals            │
│    │ Task expands beyond   │ impl-decisions.md for any deviation from story      │
│    │ what was asked        │                                                     │
├────┼───────────────────────┼─────────────────────────────────────────────────────┤
│F04 │ Premature Completion  │ VERIFIER mandatory execution (Fix 27C)              │
│    │ Done declared before  │ VERIFIER is separate from implementer — no          │
│    │ verification          │ self-verification allowed                           │
├────┼───────────────────────┼─────────────────────────────────────────────────────┤
│F05 │ Auth Scope Violation  │ GUARD 2 hard block + GATE S2 check ①               │
│    │ Auth changes without  │ Human gate required, no bypass                     │
│    │ human gate            │                                                     │
├────┼───────────────────────┼─────────────────────────────────────────────────────┤
│F06 │ Deployment            │ GATE S3 human approval token                        │
│    │ Self-Trigger          │ Agent cannot deploy without explicit human msg      │
│    │                       │ this session                                        │
├────┼───────────────────────┼─────────────────────────────────────────────────────┤
│F07 │ Comprehension Theater │ SM-RETRO comprehension debt score (Fix 41B)         │
│    │ Artifacts approved    │ Score > 6 → mandatory remediation                  │
│    │ unread                │                                                     │
├────┼───────────────────────┼─────────────────────────────────────────────────────┤
│F08 │ Memory Rot            │ 5-stage lesson progression (Fix 40A)                │
│    │ Lessons written but   │ Lessons must be CONFIRMED → GUARDED → TESTED        │
│    │ never applied         │ before marked active                                │
├────┼───────────────────────┼─────────────────────────────────────────────────────┤
│F09 │ Lesson Age Inflation  │ Timestamp + sprint ID on every lesson node          │
│    │ Stale lessons appear  │ Lessons older than N sprints flagged for review     │
│    │ fresh                 │                                                     │
├────┼───────────────────────┼─────────────────────────────────────────────────────┤
│F10 │ Ponytail Violation    │ Ponytail check ladder + disqualification guide      │
│    │ Unnecessary dep added │ Must exhaust stdlib → existing → utility fn first  │
├────┼───────────────────────┼─────────────────────────────────────────────────────┤
│F11 │ Cross-Tenant          │ GATE S2 check ② (Fix 43C)                          │
│    │ Blindspot             │ Cross-tenant denial test required on all            │
│    │ Security test omitted │ multi-tenant stories                                │
├────┼───────────────────────┼─────────────────────────────────────────────────────┤
│F12 │ Compression           │ GUARD 3 image exact-string re-verification          │
│    │ Confabulation         │ 11–17% misread rate → zero post-guard               │
│    │ Silent string errors  │ (see docs/research/compression-fidelity-methodology.md)     │
└────┴───────────────────────┴─────────────────────────────────────────────────────┘
```

---

*Full system reference: kiro/steering/ · Loop Engineering White Paper v5 · docs/product-graph.html (updated each sprint)*
