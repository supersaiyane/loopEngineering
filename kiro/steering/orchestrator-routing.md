---
inclusion: manual
---

# Orchestrator Routing Rule — $TRACKER TABLE + Reference (Fix 35)
# inclusion changed from `always` → `manual` (Fix 35): hook is now sole router.
# Auto-loading this file caused dual routing conflict — "Is this a feature or bugfix?" Kiro fallback.
# This file is now loaded ON DEMAND by team-orchestrator-core.md for the $TRACKER translation table.
# DO NOT change back to `inclusion: always` — the hook (elite-team-orchestrator.kiro.hook) handles
# all ENV detection, mode selection, and discovery routing. Duplication = conflict.

# Orchestrator Routing Rule (Reference + $TRACKER Table Only)

Routing logic lives exclusively in `elite-team-orchestrator.kiro.hook`.
This file provides the $TRACKER translation table and MANDATORY LOADS reference for team-orchestrator-core.md.

---

## ENVIRONMENT DETECTION — RUNS ONCE AT SESSION START (Fix 1 + Fix 4)

Before mode selection. Before discovery. Before any role activates.
Run both detections in a single step and log one line.

### STEP 1 — DETECT_TRACKER (Fix 1)

```
Check in order:
1. Is Jira MCP connected and responding?   → TRACKER_MODE=jira
2. Is Linear MCP connected?                → TRACKER_MODE=linear
3. Is GitHub Projects MCP connected?       → TRACKER_MODE=github
4. Is Asana MCP connected?                 → TRACKER_MODE=asana
5. None of the above                       → TRACKER_MODE=markdown
   Create /docs/phase-N/sprint-plan.md and /docs/phase-N/loop-states/ as fallback
```

**$TRACKER TRANSLATION TABLE** (applies for the entire session regardless of mode):

| $TRACKER verb | TRACKER_MODE=jira | TRACKER_MODE=linear | TRACKER_MODE=github | TRACKER_MODE=asana | TRACKER_MODE=markdown |
|---|---|---|---|---|---|
| `createProject` | `jira.createProject()` | `linear.createProject()` | `gh.createRepo()` / Project | `asana.createProject()` | `/docs/phase-N/sprint-plan.md` |
| `createEpic` | `jira.createEpic()` | `linear.createProject()` | `gh.createMilestone()` | `asana.createProject()` | section in sprint-plan.md |
| `createSprint` | `jira.createSprint()` | `linear.createCycle()` | `gh.createIteration()` | `asana.createSection()` | `/docs/phase-N/sprint-plan.md` |
| `createStory` | `jira.createStory()` | `linear.createIssue()` | `gh.createIssue()` | `asana.createTask()` | story entry in sprint-plan.md |
| `createSubtask` | `jira.createSubtask()` | `linear.createIssue(parentId)` | `gh.createIssue(linked)` | `asana.createSubtask()` | subtask line under story |
| `transitionIssue` | `jira.transitionIssue()` | `linear.updateIssue(stateId)` | `gh.updateIssue(state)` | `asana.updateTask(completed)` | update status field in markdown |
| `addComment` | `jira.addComment()` | `linear.createComment()` | `gh.createComment()` | `asana.createStory()` | append to story's markdown entry |
| `flagIssue` | `jira.flagIssue()` | `linear.updateIssue(priority=urgent)` | `gh.addLabel("blocked")` | `asana.addTag("blocked")` | add `[BLOCKED]` tag in markdown |
| `unflagIssue` | `jira.unflagIssue()` | `linear.updateIssue(priority=normal)` | `gh.removeLabel("blocked")` | `asana.removeTag("blocked")` | remove `[BLOCKED]` tag |

Rule: every existing `jira.*` call in `team-orchestrator-core.md` is now a `$TRACKER.*` call.
The translation table above maps it to the right implementation for the detected TRACKER_MODE.
Never call `jira.*` directly — always route through $TRACKER semantics.

### STEP 2 — DETECT_REMOTE (Fix 10D)

```
Run: git remote -v
→ remote(s) listed         : GIT_MODE=REMOTE
→ no output                : GIT_MODE=LOCAL
→ push fails later         : downgrade to GIT_MODE=LOCAL, notify SM-UNBLOCK
```

### LOG LINE (required — first output of every session)

```
[ENV] TRACKER_MODE=<jira|linear|github|asana|markdown> | GIT_MODE=<REMOTE|LOCAL>
```

If this log line is absent, the session is NOT correctly initialized. Stop and re-run detection.

---

## MANDATORY LOADS (Fix 4) — FIRE IMMEDIATELY AFTER ENV DETECTION

```
IF mode is Mode 1 OR Mode 4 OR Mode 5:
  LOAD: kiro/steering/team-orchestrator-core.md   ← roles, SM modes, GATE 1-3
  LOAD: kiro/steering/team-orchestrator-rules.md  ← security gates, non-negotiables, branch rules
  VERIFY both are in context before invoking any role.
  If absent → STOP. "Constitution not loaded. Load team-orchestrator-core.md + team-orchestrator-rules.md before proceeding."

  LOAD: kiro/steering/skill-selection-matrix.md          ← required for Fix 9B Step 2
  VERIFY it is in context before any role's skill activation runs.
  If absent → STOP. "Skill matrix not loaded. Fix 9B cannot resolve skill paths without it."

IF DEVELOP phase starts (any mode except Mode 2 and Mode 3):
  LOAD: kiro/steering/loop-engine.md
  VERIFY it is in context before senior_engineer_be or senior_engineer_fe activates.
  If absent → STOP. "Loop engine not loaded. Load loop-engine.md before senior_engineer activates."

IF first request of a new build task (BUILD/CREATE/MAKE/DEVELOP/IMPLEMENT + APP/TOOL/SYSTEM/etc.)
  AND user did NOT use an explicit mode override ("mode N") or bypass ("just build it", "skip questions"):
  LOAD: kiro/steering/discovery-engine.md
  VERIFY it is in context before the 7 scoping questions run.
  If absent → STOP. "Discovery engine not loaded. Cannot score task complexity without it.
               Load kiro/steering/discovery-engine.md before mode selection."
  Exception: explicit "mode N" or bypass keywords → skip this load (discovery is bypassed by user intent).
```

Load order: discovery-engine.md (new builds only) → team-orchestrator-core.md + team-orchestrator-rules.md → skill-selection-matrix.md → loop-engine.md (at DEVELOP) → team-orchestrator-sprint.md (at sprint end).
All must be in context before their respective phases begin. No exceptions.

---

## MANDATORY: DISCOVERY-FIRST (before mode selection, before ANY work)

**CRITICAL RULE:** On the FIRST request of any new development task (BUILD/CREATE/MAKE/DEVELOP/IMPLEMENT + APP/TOOL/SYSTEM/etc.), the **Discovery Engine** (`discovery-engine.md`) runs FIRST.

**Execution order:**
1. Discovery Engine asks 7 scoping questions
2. Score answers → determine complexity tier
3. Recommend mode + agent subset
4. User confirms (or overrides)
5. THEN orchestrator-routing activates the confirmed mode

**Discovery Engine takes priority over this file's mode detection logic.** This file only fires AFTER discovery completes and mode is confirmed.

**Bypasses (skip discovery, go direct to mode):**
- User says "mode N" explicitly → skip discovery, use that mode with full agent set
- User says "just build it" / "skip questions" → Mode 3 (Direct Execution)
- Request is NOT a build (bug fix, refactor, question) → Mode 3 directly

---

## ROUTING: 4 Modes (reference for execution after selection)

### EXPLICIT MODE OVERRIDE
**Trigger:** Prompt contains "mode 1", "mode 2", "mode 3", or "mode 4" (case-insensitive).
**Action:** Skip mode selection prompt. Activate the specified mode directly.
**Priority:** Explicit override > mode selection prompt.
Examples: "mode 1: build a chess app" → Full Army. "mode 4: create a dashboard" → Hybrid.

### MODE 1: Full Army Pipeline
**Trigger:** Prompt contains BUILD/CREATE/MAKE/DEVELOP/IMPLEMENT combined with
APP/TOOL/SYSTEM/PRODUCT/SERVICE/FEATURE/UI/API/DASHBOARD/BOT/AGENT/WEBSITE/PIPELINE
**Confidence gate (Fix 27B):** Mode 1 auto-inference requires HIGH confidence (≥90%) OR user confirmation. See hook STEP 3 confidence scoring. Never commit to Mode 1 on MEDIUM/LOW confidence without user Y/n.

**Action:** Invoke `team-orchestrator-core.md` + `team-orchestrator-rules.md` constitution (Fix 19 split). 
**IMPORTANT:** Load `team-orchestrator-core.md` + `team-orchestrator-rules.md` into context FIRST (both are manual-inclusion — see MANDATORY LOADS above).
Run full Think → Design → Develop chain.
- ALL roles fire (per team-orchestrator-core.md role registry)
- Multi-phase: ≥2 phases, ≥2 sprints/phase, ≥3 tasks/sprint
- 8 docs per phase in docs/phase-N/
- Security/QA/DevOps tasks mandatory in sprint plan
- Git discipline per team-orchestrator-rules.md (FEATURE BRANCH LIFECYCLE section)
- Mapping + Discipline reports at phase end

**NEVER:**
- Write code before docs
- Skip any gate
- Collapse to single phase

---

### MODE 2: Single Agent Invocation
**Trigger:** Prompt targets ONE specific role without full pipeline intent.

| User Intent Pattern | Role Invoked | Output |
|-------------------|-------------|--------|
| "research / market analysis / competitor / opportunity" | Market Researcher | market-researcher doc |
| "tech strategy / tech stack / build vs buy / scalability" | CTO | cto-strategy doc |
| "user stories / PRD / requirements / feature spec / acceptance criteria" | Product Manager | PRD doc |
| "architecture / system design / data model / API design / sequence diagram" | Architect | architecture doc |
| "sprint plan / tasks / backlog / estimate / velocity" | Scrum Master | sprint-plan doc |
| "security review / threat model / vulnerability / audit / OWASP" | Security Engineer | security doc |
| "test plan / test cases / QA / testing / coverage" | QA Engineer | test-plan doc |
| "CI/CD / deployment / infrastructure / monitoring / DevOps / IaC" | DevOps Engineer | devops-plan doc |
| "database design / schema / ER diagram / migration" | Database Architect | schema doc |
| "cloud architecture / VPC / landing zone / multi-region" | Cloud Architect | cloud doc |
| "cost analysis / FinOps / budget / unit economics" | FinOps Architect | finops doc |
| "SLI / SLO / observability / incident / runbook" | SRE Engineer | sre doc |
| "documentation / API docs / runbooks / ADR index" | Technical Writer | docs |
| "pipeline / streaming / Kafka / Spark / dbt / batch / CDC / data engineering" | Data Engineer | pipeline-design doc |
| "mobile / iOS / Android / React Native / offline sync / push notifications" | Mobile Engineer | mobile-design doc |
| "funnel analysis / cohort / A/B test / EDA / retention / data storytelling" | Data Scientist | analysis doc |

**Action:** Invoke ONLY that role. Produce its document (≥300 words, full depth, same template as pipeline). No other roles, no phases/sprints, no git unless asked.

**market_researcher RE-INVOCATION (Fix 13E):** If a Mode 2 request targets market_researcher AND the session already has a cto-strategy doc or PRD doc in context → re-invoke market_researcher first to cross-check its findings against those docs. market_researcher must flag any market assumptions that contradict the existing strategy before the new artifact is produced. Log: `[market_researcher re-invocation: validating against existing strategy docs]`

**SKILL SELECTION IN MODE 2:** `skill-selection-matrix.md` still applies — Mode 2 is NOT exempt from Fix 9B. Before the role produces its artifact: (1) identify the activity from the user's request, (2) look up the matching row in `skill-selection-matrix.md` for that role, (3) load only the listed skill files (max 3). Skill activation summary (Fix 9B Step 4) is required before output is produced. If no $TRACKER labels exist (Mode 2 has no sprint stories), use matrix lookup as the primary skill-selection path.

---

### MODE 3: Direct Execution
**Trigger:** Neither Mode 1, Mode 2, Mode 4, nor Mode 5 matches.
- Bug fix, refactor, style change, conversational question, debugging
- **TRIVIAL BUILD (Fix 22G):** Single-file / single-function deliverable with no backend, no integrations, no database, no multi-role work. Prompt ≤ 12 words, no system/platform/service/infrastructure/integration/pipeline/agent. Examples: calculator, converter, formatter, script, utility, simple game.
  → One senior role executes directly. No Jira. No ADRs unless non-obvious decision. No sprint. Tests required. Mode 3 Build Report at end. ~8,000 tokens vs Mode 5's ~31,000.

**Action:** Proceed directly. No orchestrator invoked.

---

### MODE 4: Hybrid (Spec + Army)
**Trigger:** Prompt contains BUILD/CREATE/MAKE/DEVELOP/IMPLEMENT + APP/TOOL/SYSTEM/... AND user explicitly requests "mode 4" OR "hybrid".
Also activates when Kiro spec workflow is running AND Mode 1 would normally trigger.

**Mode 4 Lite vs Standard (Fix 12D):**
- **Mode 4 Lite** — project has ≤5 user stories OR single sprint planned → minimum coverage ≥60%
- **Mode 4 Standard** — project has >5 user stories OR multi-sprint plan → minimum coverage ≥70%
Log at project start: `[MODE 4: Lite/Standard — N stories, N sprints planned]`

**Action:** Two-phase hybrid approach:
1. **Planning phase** — Use Kiro spec workflow (.kiro/specs/) for requirements.md → design.md → tasks.md
2. **Execution phase** — Once tasks.md is generated, switch to Mode 1 army pipeline for implementation:
   - Load `#team-orchestrator` steering file
   - Use spec's requirements.md as PRD input (skip Market Researcher + CTO Think phase)
   - Use spec's design.md as architecture input (skip Architect design from scratch)
   - Run Develop chain: sprints, all engineering roles, gates, reports
   - Multi-phase: ≥2 phases, ≥2 sprints/phase, ≥3 tasks/sprint
   - All 6 reports per phase (QA, Security, Mapping, Discipline, Jira, Git)

**Key difference from Mode 1:** Think + Design phases are replaced by Kiro spec system. Develop phase uses full army pipeline.

**Artifacts produced:**
- `.kiro/specs/{name}/` — requirements.md, design.md, tasks.md (planning)
- `docs/phase-N/` — sprint plans, code, tests, reports (execution)

**NEVER:**
- Write code during planning phase
- Skip army roles during execution phase
- Collapse execution to single phase

---

### MODE 5: Lean (Fix 6 — small teams, MVPs, solo projects)
**Trigger:** User says "mode 5", "lean mode", "just 3 roles", "small team", or project has ≤2 engineers.
**Also activates:** When user explicitly requests speed over completeness.

**Role collapse — exactly 3 roles (no others):**
| Lean Role | Maps to | Covers |
|-----------|---------|--------|
| STRATEGIST | market_researcher + cto + product_manager | Discovery + strategy + PRD |
| BUILDER | backend_lead + senior_engineer_be/fe + devops_engineer | Design + implement + deploy |
| QUALITY | qa_engineer + security_engineer + sre_engineer | Test + security + reliability |

**LEAN LOOP (replaces standard Fix 7 loop spec — simpler format):**
```
LEAN LOOP SPEC
GOAL:       <one sentence — what done looks like>
VERIFIER:   <one automated command>
CRITERIA:   <max 2 criteria, scored 1-10>
STOP WHEN:  both criteria ≥ 8 OR 4 iterations reached (lean cap — lower than standard 8)
```
Checker in lean mode = QUALITY role (fresh context invocation — not the same call as BUILDER).
> **Cross-reference:** LEAN LOOP SPEC is a simplification of the full 4-section spec in `kiro/steering/loop-engine.md` (used by Modes 1/4; also loaded by Mode 5 DEVELOP phase per Step 4).

**Lean discipline profile (simplification of Fixes 1–9):**
- Fix 1: $TRACKER still applies — TRACKER_MODE=markdown is the default in lean mode
- Fix 2: SM modes collapse → STRATEGIST gates (no separate SM-GATE / SM-PLAN calls)
- Fix 4: loop-engine.md still loads before BUILDER activates
- Fix 7: use LEAN LOOP SPEC (above) — not full 4-section spec
- Fix 8: degradation tiers apply, 4-read cap per iteration (not 2 — lean roles cover more ground)
- Fix 9: skill activation still applies — ≤3 files per lean role per activation
- Fix 10: GIT_MODE detection still applies. Branch lifecycle still applies.

**Security gates S2 + S3 are NOT optional in lean mode.**
QUALITY role runs S2 (feature security review) and S3 (secrets scan) regardless of team size.

**NEVER in lean mode:**
- Merge without QUALITY checker approval
- Skip verifier
- Read all skill files

---

## PRIORITY: Mode Override > Mode 4 (with .kiro/specs/) > Mode 1 > Mode 2 > Mode 5 > Mode 3

If user says "mode N" explicitly → that mode wins, no detection needed.
Mode 4 wins over Mode 1 ONLY when `.kiro/specs/` directory already exists from a prior spec workflow run.
If `.kiro/specs/` is absent → Mode 1 wins.
Mode 5 is for explicitly small-team or lean requests only.
Mode 2 is for ISOLATED role requests only.

---

## EXCEPTIONS (bypass to Mode 3):
- "skip orchestrator" / "just code it" — explicit user override
- "Add X to existing Y" where Y is already built this session
- Bug fix on existing code
- Refactor / rename / style change

---

## MANDATORY: TESTING + REPORTS IN ALL MODES

**CRITICAL RULE:** Testing is NON-NEGOTIABLE in every mode. No code ships without tests.
Discipline report is NON-NEGOTIABLE in every mode. User must always see burn rate.

### Testing Requirements by Mode

| Mode | Testing Requirement | Test Framework | Gate | Min Coverage (new code) |
|------|-------------------|----------------|------|------------------------|
| Mode 3 (Direct) | Write + run relevant tests after every build | vitest/jest/pytest (match project) | Build fails if tests fail | Report only — no threshold |
| Mode 4 Lite | QA (lite) — unit tests for all new functions | Project's test framework | Must pass before "done" | ≥ 60% |
| Mode 4 Standard | QA (full) — unit + integration tests | Full test suite | Gate before each sprint end | ≥ 70% |
| Mode 1 (Full) | QA (full) — unit + integration + contract + load | Full suite + regression | Gate 3 + Gate 5 (phase-end) | ≥ 80% |
| Mode 5 (Lean) | Unit tests + manual smoke | Project's test framework | S2 + S3 gates | ≥ 60% |

### Testing Protocol (Mode 3 — Direct Execution)

After EVERY code build in Mode 3:
1. **Set up test framework** if not present (vitest for Vue/JS, pytest for Python, etc.)
2. **Write tests** for the code just built (minimum: happy path + 1 edge case per component)
3. **Run tests** — `npm test` / `vitest --run` / equivalent
4. **Report results** inline:

```
## Test Report
- Framework: [vitest/jest/pytest]
- Tests run: X
- Passed: X
- Failed: X
- Coverage: X% (report only — no threshold in Mode 3)
- Duration: Xs
```

**If tests fail:** Fix before declaring task complete. Never ship broken code.

### Discipline Report Requirements by Mode

| Mode | Report Trigger | Report Format |
|------|---------------|---------------|
| Mode 3 (Direct) | End of every build task | Inline mini-report (see below) |
| Mode 4 Lite | End of build | Lite discipline report |
| Mode 4 Standard | Phase/sprint end | Full discipline report |
| Mode 1 (Full) | Phase end | Full 6-report set (QA, Security, Mapping, Discipline, Jira, Git) |

### Mode 3 Build Report (MANDATORY after every Mode 3 build)

```
## Build Report (Mode 3)
| Metric | Value |
|--------|-------|
| Tests | X pass / Y fail |
| Coverage | X% (report only — no threshold) |
| Reads | X |
| Tool calls | X |
| Tier | PEAK/GOOD/DEGRADING |
| Tokens saved (est.) | X% |
| Build verified | YES/NO |
```

### Mode 4 Lite Build Report

```
## Build Report (Mode 4 Lite)
| Metric | Value |
|--------|-------|
| Tests written | X |
| Tests passed | X / Y |
| Coverage | X% (target: ≥ 60% new code) |
| Agents used | [list] |
| Reads | X |
| Tool calls | X |
| Tier | PEAK/GOOD |
| Tokens saved (est.) | X% |
| Planning docs produced | X |
```

**ENFORCEMENT:** If a build completes WITHOUT a test report → the build is INCOMPLETE.
The task is not done until tests pass and report is shown.


---

## SELF-CHECK + PHASE PARALLELISM RULES
See `kiro/steering/team-orchestrator-sprint.md` — "MODE 1 SELF-CHECK" and "PHASE PARALLELISM RULES" sections (Fix 19 split).

---

## PER-PHASE REPORT TEMPLATES
All 6 report templates (QA, Security, Mapping, Discipline, Jira, Git) are defined in `kiro/steering/team-orchestrator-sprint.md` (GATE 5 → PHASE-END REPORT TEMPLATES section — Fix 15B / Fix 19 split).
Canonical filenames: DISCIPLINE-REPORT.md (scrum_master), JIRA-REPORT.md (scrum_master), GIT-REPORT.md (devops_engineer), MAPPING-REPORT.md (architect), QA-REPORT.md (qa_engineer), SECURITY-REPORT.md (security_engineer).
File path: `docs/phase-N/<REPORT-NAME>.md`