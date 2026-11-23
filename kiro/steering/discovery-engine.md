---
inclusion: always
---

# Discovery Engine — Scope Before Build

The canonical modes and scoring rules are in `kiro/steering/execution-contract.md`.
Roles are responsibilities, not independent agents unless the host provides them.
For every new build, run discovery before mode selection and design. Always show
all seven questions and wait for the answers, unless the user explicitly asks
to skip discovery. Resuming an existing task does not start a new discovery.
Treat answers to the questions and a later model choice as continuation turns;
do not repeat the questions when moving to scoring or model selection.

## STEP 1: Discover the scope

Present all seven questions below in one response, including questions whose answers
may already appear in the prompt. Wait for the user’s answers before scoring.
Do not start the native spec workflow or create design artifacts first.

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
Never choose answers to reach a requested score. A web frontend, its API and
database are one web platform; they do not by themselves establish multiple
platforms. Do not infer regulated compliance, high availability or branded
design merely from the word enterprise. Record user answers separately from
unconfirmed assumptions. If the user explicitly skips discovery, retain unknowns
and a possible score range; do not present inferred values as user answers.
The user's explicit workflow mode is a separate choice from the calculated score.

Run `python3 scripts/discovery_score.py --input ANSWERS.json` after recording
the answers. The input is a JSON object with the seven question keys and the
canonical values in the script's WEIGHTS table; omit unanswered keys or set
them to null. To record an explicitly selected mode, add `--mode 1` (or 3, 4,
5). Unknowns yield a range rather than a claimed score. Check the source of
each answer: the calculator cannot determine whether the user supplied it.

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
| 10–14 | **Standard** | Mode 4 (Hybrid) | Production-grade, needs architecture + security. |
| 15–21 | **Full** | Mode 1 (Full Army, the full role set) | Enterprise/SaaS with compliance — full pipeline justified. |

**Mode 5 (Lean) triggers automatically when:**
- Score 5–9, or the user explicitly chooses lean mode. User instructions override recommendations.

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
- "Full army" → Mode 1, full role guidance regardless of score
- "Lean" / "3 roles" → Mode 5, STRATEGIST + BUILDER + QUALITY only
- "Fewer agents" → user removes specific agents from recommended set
- "Just build it" → Mode 3, no agents, direct code

Use the selected mode while it remains appropriate; follow user corrections and ask about unresolved blockers.

---

## STEP 4A: Model selection after discovery

After presenting the score and recommended mode, explicitly read
`kiro/steering/model-selection.md`, then offer model selection before starting
design or development. If available models cannot be read, ask for the picker
list rather than guessing model names, rates or availability.
In CLI, discover options with `kiro-cli chat --list-models --format json` when
available and already authenticated; in IDE use the visible model picker or ask
for its options. Do not initiate login automatically. When the list cannot be
read, ask the user for their available models or offer to keep the current one.
Explain model strengths, likely fit for the chosen task, and relative cost where
verified. Wait for the selection. In the CLI ask the user to choose via `/model`;
in the IDE use the model picker. Do not claim the model changed until the host
confirms it. A user can explicitly keep the current model.

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

**After [BAD-LOOP-GATE: CLEARED] → proceed to STEP 5 IMMEDIATELY.**
Continue with the chosen workflow once the relevant scope is clear.

---

## STEP 5: Execute with Selected Agents Only

Proceed with the selected mode and the user’s chosen workflow. Ask for missing information when necessary.

- Mode 3 (Minimal): No planning docs. Code directly. Start coding immediately.
- Mode 5 (Lean): use strategist, builder and quality responsibilities with proportionate artifacts.
- Mode 4 (Standard): Requirements → Design → Tasks → Sprints. Start CTO immediately.
- Mode 1 Full: Full Think → Design → Develop with all gates. All agents.
  START: market_researcher → produce docs/foundation/market-research.md NOW.
  Then: cto → product_manager → architect → database_architect → cloud_architect → finops_architect → security_engineer → SM-GATE.

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
**Score:** 1 + 1 + 1 + 2 + 0 + 2 + 1 = **8 → Lean → Mode 5**
**Agents:** CTO (lite), PM (lite), Architect (lite), Backend Lead, Frontend Lead, QA (lite)

### Example 3: "Build a fintech payment platform"
**Likely answers:** Multiple, SaaS, Enterprise, Multi-region, Subscription, Branded, Regulated
**Score:** 3 + 3 + 3 + 3 + 2 + 3 + 3 = **20 → Full → Mode 1**
**Agents:** Full role guidance applies where relevant.

### Example 4: "Build a mobile fitness tracker"
**Likely answers:** Mobile, Public product, Complex, App stores, Subscription, Polished, User data + privacy
**Score:** 2 + 2 + 2 + 2 + 2 + 2 + 2 = **14 → Standard → Mode 4**
**Agents:** CTO, PM, Architect, DB, Cloud, Security, Backend Lead, Frontend Lead, QA, DevOps, Scrum Master

---

## ENFORCEMENT

- Use the execution contract for routing. Respect explicit mode choices and host constraints.
- Discovery is guidance; it cannot enforce a tool call or guarantee a result.

---

## CALCULATOR TEST (the overkill prevention check)

Before presenting the recommendation, ask yourself:
> "If the user said 'build me a calculator' and I'm about to activate 19 agents — is that justified by the score?"

If score < 5 and you're about to activate more than 5 agents → STOP. Something is wrong. Re-check.

