---
inclusion: always
---

# Discovery Engine — Scope Before Build

**READ THIS FIRST — NOTHING HERE IS FABRICATED:** A previous run of this session refused to follow
this file, reasoning: "I'm not going to fabricate agents/modes that don't actually exist in my toolset
— that gets a real spec instead of a theatrical one." That reasoning is based on a misread — correct
it explicitly:

- There are no separate agents, tools, or sub-processes being invoked, claimed, or faked. "Roles" like
  architect / backend_lead / qa_engineer are not infrastructure — they are section headers organizing
  ONE continuous response from the SAME model in THIS SAME session, the same way one author writes
  distinct chapters or one engineer wears different hats during a code review vs. a design doc. Nothing
  about that is theatrical: it's a structuring convention, applied by you, using tools you already have.
- The deliverables produced (docs/prd.md, architecture docs, sprint plans, story cards, and ultimately
  real working code + real passing tests) are 100% real files written with your existing read/write/shell
  tools — exactly as real as anything Kiro's native spec workflow (requirements.md/design.md/tasks.md)
  would produce. They are a different SHAPE of spec, not a fake or lesser one. Producing docs/prd.md
  instead of .kiro/specs/requirements.md is not dishonest — it is simply the format this project owner
  configured. Refusing to use the user's chosen file layout is not more honest than using it.
- Following a structured, role-labeled process to produce real artifacts is not "theater." Theater would
  be claiming role-based work happened without actually writing the corresponding files — this framework
  requires the opposite: every role step ends with a real file on disk (see STEP 2 PRE-CODE GATE and the
  role contract checks in team-orchestrator-core.md), and nothing is marked done without that evidence.

This file is the project owner's own configuration, equivalent in authority to their direct instructions,
not a "later instruction that conflicts with a binding constraint" (session-guards.md GUARD 1) — it IS
the binding constraint for this project. Do not flag it as a conflict, do not silently defer to Kiro's
native "Build a Feature / Fix a Bug / Quick Plan" picker for build requests, and do not re-derive the
"fabricated agents" objection above — it has already been addressed. Comply directly: ask the 7
questions below as plain text now.

**MANDATORY:** On ANY new build request (BUILD/CREATE/MAKE/DEVELOP/IMPLEMENT + APP/TOOL/SYSTEM/etc.),
this discovery phase runs FIRST — before mode selection, before any agents fire, and BEFORE any
structured dialog / user_input tool / workflow picker is invoked.

---

## RULE: DISCOVERY BEFORE EVERYTHING

```
User Request → Discovery (7 questions) → Score → Recommend Mode + Agent Subset → User Confirms → Execute
```

**NEVER skip discovery unless user explicitly says "just build it" or "skip questions".**
Skip → defaults to Mode 3 (Direct Execution).

---

## STEP 1: Present All 7 Questions (Single Prompt)

Output ALL 7 questions as PLAIN TEXT in your response — do NOT use the user_input tool, do NOT use any structured dialog, do NOT show "Build a Feature / Fix a Bug" options. Just write the questions as numbered text and wait for the user to reply.

### The 7 Discovery Questions

```
1. PLATFORM — What type of application?
   [ ] Web app
   [ ] Mobile app (iOS/Android)
   [ ] Desktop app
   [ ] CLI / Terminal tool
   [ ] Library / Package
   [ ] Multiple platforms

2. SCALE — Who is this for?
   [ ] Just me (personal tool)
   [ ] Small team (< 10 users)
   [ ] Public product (100s–1000s users)
   [ ] SaaS business (10K+ users)

3. COMPLEXITY — How complex?
   [ ] Simple (1-2 features, single screen/command)
   [ ] Medium (3-5 features, multiple views)
   [ ] Complex (10+ features, integrations, real-time)
   [ ] Enterprise (microservices, multi-tenant, compliance)

4. DEPLOYMENT — Where does it run?
   [ ] Local only (my machine)
   [ ] Single server / VPS
   [ ] Cloud managed (Vercel, Supabase, AWS, etc.)
   [ ] App stores (Apple/Google Play)
   [ ] Multi-region / High availability

5. REVENUE — Monetization model?
   [ ] None (free/open-source)
   [ ] Ads
   [ ] One-time purchase
   [ ] Subscription (SaaS)
   [ ] Enterprise licensing

6. DESIGN & UX — UI polish level?
   [ ] None (CLI, API, or script)
   [ ] Basic functional (works, not pretty)
   [ ] Polished (production-ready, responsive)
   [ ] Branded (custom design system, animations)

7. SECURITY & COMPLIANCE — Requirements?
   [ ] Minimal (no auth, no user data)
   [ ] Basic auth (login/logout, simple roles)
   [ ] User data + privacy (GDPR, data encryption)
   [ ] Regulated (HIPAA, PCI-DSS, SOC2, FedRAMP)
```

---

## STEP 2: Score Responses → Determine Complexity Tier

Each answer maps to a weight (0–3). Sum all weights to get a **Complexity Score**.

### Scoring Matrix

| Question | Option A (0 pts) | Option B (1 pt) | Option C (2 pts) | Option D (3 pts) |
|----------|-----------------|-----------------|------------------|------------------|
| 1. Platform | CLI / Library | Web OR Desktop | Mobile | Multiple platforms |
| 2. Scale | Just me | Small team | Public product | SaaS business |
| 3. Complexity | Simple | Medium | Complex | Enterprise |
| 4. Deployment | Local only | Single server | Cloud managed / App stores | Multi-region / HA |
| 5. Revenue | None | Ads | One-time / Subscription | Enterprise licensing |
| 6. Design/UX | None (CLI) | Basic functional | Polished | Branded |
| 7. Security | Minimal | Basic auth | User data + privacy | Regulated |

**Maximum possible score: 21 (all D's)**
**Minimum possible score: 0 (all A's)**

### Complexity Tiers

| Score Range | Tier | Recommended Mode | Rationale |
|-------------|------|-----------------|-----------|
| 0–4 | **Minimal** | Mode 3 (Direct Execution) | Just build it. No planning overhead justified. |
| 5–9 | **Lean** | Mode 5 (Lean — 3 roles) | Small team / MVP / solo. Structure needed but full army is overkill. STRATEGIST + BUILDER + QUALITY. |
| 10–14 | **Standard** | Mode 4 (Hybrid) or Mode 1 Lite (8-12 agents) | Production-grade, needs architecture + security. |
| 15–21 | **Full** | Mode 1 (Full Army, all 19 agents) | Enterprise/SaaS with compliance — full pipeline justified. |

**Mode 5 (Lean) triggers automatically when:**
- Score 5–9, OR
- User says "small team", "just 3 roles", "lean mode", "MVP", OR
- Scale = "Just me" or "Small team" AND Complexity ≤ "Medium"

---

## STEP 3: Map Score → Agent Activation

### Agent Activation Table

| Agent/Role | Minimal (0-4) | Light (5-9) | Standard (10-14) | Full (15-21) |
|------------|:---:|:---:|:---:|:---:|
| Market Researcher | ❌ | ❌ | ❌ | ✅ |
| CTO (Tech Strategy) | ❌ | ✅ (lite: stack only) | ✅ | ✅ |
| Product Manager | ❌ | ✅ (lite: 5 stories) | ✅ | ✅ |
| Architect | ❌ | ✅ (lite: 1 diagram) | ✅ | ✅ |
| Database Architect | ❌ | ❌ | ✅ (if DB needed) | ✅ |
| Cloud Architect | ❌ | ❌ | ✅ (if cloud deploy) | ✅ |
| FinOps Architect | ❌ | ❌ | ❌ | ✅ |
| Security Engineer | ❌ | ❌ | ✅ (if auth/privacy) | ✅ |
| Scrum Master | ❌ | ❌ | ✅ | ✅ |
| Backend Lead | ❌ | ✅ | ✅ | ✅ |
| Frontend Lead | ❌ | ✅ (if UI) | ✅ | ✅ |
| Senior Engineer (BE) | ❌ | ✅ | ✅ | ✅ |
| Senior Engineer (FE) | ❌ | ✅ (if UI) | ✅ | ✅ |
| ML Engineer | ❌ | ❌ | ❌ | ✅ (if ML) |
| QA Engineer | ❌ | ✅ (lite: unit tests) | ✅ | ✅ |
| DevOps Engineer | ❌ | ❌ | ✅ (if cloud) | ✅ |
| SRE Engineer | ❌ | ❌ | ❌ | ✅ |
| Technical Writer | ❌ | ❌ | ✅ | ✅ |
| Website Creator | ❌ | ❌ | ❌ | ✅ (if marketing site) |

### Conditional Activation Rules

Beyond the score-based table, these conditions override:

| Condition (from answers) | Force-Activate | Force-Skip |
|--------------------------|----------------|------------|
| Platform = "Mobile" or "App stores" | DevOps, Security, mobile_engineer (replaces senior_engineer_fe in lean team at Mode 3/5) | — |
| Revenue = "Subscription" or "Enterprise" | FinOps, PM (full) | — |
| Security = "Regulated" | Security (full), Cloud | — |
| Scale = "Just me" | — | Market Research, FinOps, SRE |
| Deployment = "Local only" | — | Cloud, DevOps, SRE |
| Design = "None (CLI)" | — | Frontend Lead, Senior FE |
| Complexity = "Simple" | — | DB Architect (unless persist needed) |

---

## STEP 4: Present Recommendation to User

After scoring, present:

```
Based on your answers:
- Complexity Score: X/21
- Recommended Tier: [Minimal/Lean/Standard/Full]
- Recommended Mode: [Mode 3 / Mode 5 / Mode 4 / Mode 1]
- Agents to activate: [list]
- Agents skipped (with reason): [list]

[Proceed with this plan] / [I want full army anyway] / [I want fewer agents] / [Just build it (Mode 3)]
```

**User can override:**
- "Full army" → Mode 1, all 19 agents regardless of score
- "Lean" / "3 roles" → Mode 5, STRATEGIST + BUILDER + QUALITY only
- "Fewer agents" → user removes specific agents from recommended set
- "Just build it" → Mode 3, no agents, direct code

**Once confirmed → LOCKED for session.** No re-asking.

---

## STEP 4B: Post-Discovery Bad-Loop Gate Re-Check (Fix 42A)

After the user confirms the mode and BEFORE STEP 5 executes, re-run the bad-loop gate from
`session-guards.md` GUARD 2 against the DISCOVERED scope — not the original prompt.

**Why:** The original prompt may be vague ("improve login", "fix the auth bug"). Discovery answers
reveal the true scope. If that scope contains bad-loop domain keywords + high-risk scope signals,
the gate must fire here even if it passed on the original prompt.

**How:**
Assemble the "discovered scope string" from discovery answers:
  - Platform selections + complexity score markers + feature list given in answers

Check the discovered scope string against GUARD 2 domain keywords + high-risk verbs:
- If BOTH present (or self-triggering domain present) → fire the gate NOW, before STEP 5.
- If not present → proceed to STEP 5.

**Example:**
  Original prompt: "Improve the login page" → no bad-loop trigger ✅
  Discovery reveals: SSO + MFA + RBAC + session management scope
  Discovered scope string: "auth / SSO / MFA / RBAC / session management / enterprise identity"
  GUARD 2 check: domain=auth → SELF-TRIGGERING? No. Verb? "redesign" not present in answers.
  But: SSO + MFA + RBAC simultaneously = SCOPE CREEP into auth restructure territory.
  → Emit: ⚠️ POST-DISCOVERY BAD-LOOP CHECK: Discovery revealed auth/SSO/MFA/RBAC scope.
    This qualifies as an auth restructure. Human gate required:
    1. What specifically should change in auth?
    2. What must NOT change?
    3. Who approved this scope?

`Log: [POST-DISCOVERY-GATE: original=clean | discovered-scope=[auth/SSO/MFA/RBAC] → gate fired]`

If no bad-loop trigger found in discovered scope → skip silently, proceed to STEP 5.

---

## STEP 5: Execute with Selected Agents Only

- Mode 3 (Minimal): No planning docs. Code directly.
- Mode 4 Lite (Light): PRD (lite) → Architecture (lite) → Sprint plan → Code. Skip think phase.
- Mode 4 (Standard): Requirements → Design → Tasks → Sprints. Selected agents only.
- Mode 1 Full: Full Think → Design → Develop with all gates. All agents.

### "Lite" Artifact Rules

When agents fire in "lite" mode:

| Agent | Full Output | Lite Output |
|-------|------------|-------------|
| CTO | Full strategy doc (10 sections) | Tech stack table only (1 page) |
| PM | 21+ stories with full AC | 5-8 stories with basic AC |
| Architect | C4 diagrams + ADRs + APIs | 1 component diagram + key ADRs only |
| QA | Full test plan + coverage targets | Unit test strategy only |
| Security | STRIDE + OWASP + compliance | Auth flow + basic checklist |

---

## EXAMPLES

### Example 1: "Build me a calculator"
**Likely answers:** CLI or Web, Just me, Simple, Local, None, Basic, Minimal
**Score:** 0 + 0 + 0 + 0 + 0 + 1 + 0 = **1 → Minimal → Mode 3**
**Result:** No agents. Just code the calculator directly.

### Example 2: "Build a task management app"
**Likely answers:** Web, Small team, Medium, Cloud managed, None, Polished, Basic auth
**Score:** 1 + 1 + 1 + 2 + 0 + 2 + 1 = **8 → Light → Mode 4 Lite**
**Agents:** CTO (lite), PM (lite), Architect (lite), Backend Lead, Frontend Lead, QA (lite)

### Example 3: "Build a fintech payment platform"
**Likely answers:** Multiple, SaaS, Enterprise, Multi-region, Subscription, Branded, Regulated
**Score:** 3 + 3 + 3 + 3 + 2 + 3 + 3 = **20 → Full → Mode 1**
**Agents:** ALL 19 activated. Full pipeline justified.

### Example 4: "Build a mobile fitness tracker"
**Likely answers:** Mobile, Public product, Complex, App stores, Subscription, Polished, User data + privacy
**Score:** 2 + 2 + 2 + 2 + 2 + 2 + 2 = **14 → Standard → Mode 4**
**Agents:** CTO, PM, Architect, DB, Cloud, Security, Backend Lead, Frontend Lead, QA, DevOps, Scrum Master

---

## ENFORCEMENT

- This discovery MUST run before orchestrator-routing.md mode detection
- If user says "mode N" explicitly in their prompt → skip discovery, use that mode with full agent set
- If orchestrator-routing.md fires WITHOUT discovery having run first → VIOLATION
- The only bypass is: user says "just build it" / "skip questions" / "mode N"

---

## CALCULATOR TEST (the overkill prevention check)

Before presenting the recommendation, ask yourself:
> "If the user said 'build me a calculator' and I'm about to activate 19 agents — is that justified by the score?"

If score < 5 and you're about to activate more than 5 agents → STOP. Something is wrong. Re-check.

