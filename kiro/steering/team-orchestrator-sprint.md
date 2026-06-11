---
inclusion: manual
---


## ⚡ QUICK REFERENCE — Sprint Orchestrator (read this first)
- **GATE 5 triggers (Fix 25L)**: user says "phase complete" OR EPIC all-done OR sprint mod 3 = 0.
- **ADR promotions (Fix 25M)**: max 2/sprint. Dedup before promoting. Excess → [ADR-QUEUED].
- **ADR scope filter (Fix 25P)**: load ADRs WHERE domain overlaps story labels AND scope=global OR matches component.
- **Lessons namespace (Fix 25Q)**: load WHERE project=global OR project=<current-sprint-project>.
- **Design system gate (Fix 25B)**: BLOCKS Sprint 1 start. web→design_system.md, mobile→design_system_mobile.md.
- **SM-RETRO**: velocity + DoD + lessons write (5-step protocol) + impl-decisions.md + ADR promotions.
- **CHECKPOINT write**: Type=SPRINT. Last SPRINT row = session resume point. [Fix 25O/26A]
---
# Team Orchestrator — Sprint & Phase Gates (Fix 19 split)
# Loads at: Sprint end (GATE 4 trigger) and Phase end (GATE 5 trigger)
# Contains: GATE 4 (memory write + SM-RETRO), GATE 5 (phase-end reports), MODE 1 SELF-CHECK, PHASE PARALLELISM RULES
# See also: team-orchestrator-core.md (session start), team-orchestrator-rules.md (security, non-negotiables)

### GATE 4 — SPRINT END (per sprint)
**Trigger:** All sprint stories reach Done or explicit carry-over decision made.
**Actions in order:**
1. `sre_engineer` — SLI/SLO review, alert rule updates, runbook additions for sprint's features
2. `technical_writer` — API docs update, ADR index update, new runbooks
2b. MEMORY WRITE (`scrum_master`, before SM-RETRO):
    1. Read docs/lessons.md — check last entry date and confidence levels
    2. If any sprint pattern not captured → append with `confidence: low` and domain tag (Fix 20D)
    3. If any low/medium entry confirmed this sprint → upgrade per objective criteria (Fix 20B):
       low→medium: this is the 2nd+ separate sprint confirming it, zero contradictions
       medium→high: 5+ sprint count + user confirmed at least once. Check checkpoint.md dates.
    4. Read docs/decisions.md — if any ADR made or superseded this sprint → update
       ADR SCOPE LOAD RULE (Fix 25P): When loading ADRs for a story, filter by:
         domain overlaps story labels AND (scope=global OR scope matches story component).
         Skip ADRs whose domain does not match ANY story label (prevents cross-domain constraint bleed).
         Log: `[ADRs: N loaded (N skipped: domain mismatch)]`
    4b. IMPL-DECISIONS REVIEW (Fix 22E): Read docs/phase-N/impl-decisions.md for this sprint.
        Scan each entry for [PROMOTE] marker OR entries that appear in 2+ stories (recurring pattern).
        If [PROMOTE] found → promote to ADR (consequential) OR lessons.md (pattern/learning, confidence: low).
        ADR PROMOTION RULES (Fix 25M):
          - Max 2 new ADR promotions per sprint. Queue excess with [ADR-QUEUED] tag for next sprint.
          - Before promoting: check docs/decisions.md for existing entry on same topic (keyword match on title).
            Duplicate found → skip, log [ADR-SKIP: duplicate of ADR-N].
        Log: `[IMPL-DECISIONS: N entries reviewed, N promoted to ADR/lessons, N queued, N skipped-dedup]`
        If nothing to promote: log `[IMPL-DECISIONS: N entries reviewed, 0 promoted]`
    5. Log: `[MEMORY WRITE: N entries updated/added, N ADRs updated]`
    6. MEMORY REFRESH — re-inject into active context the 3 most recently written/upgraded entries:
       Pull last 3 entries by date from docs/lessons.md after step 5 write completes.
       LESSON PROJECT SCOPE (Fix 25Q): Load lessons WHERE:
         (project=global OR project=<current-sprint-project-name>) AND domain matches.
         Current project name = TITLE field of sprint-plan.md (first line after "# Sprint N").
         Cross-project lessons (project=other-project) are EXCLUDED unless project=global.
       Log: `[MEMORY REFRESH: N new entries now active this session]`
       HIGH-confidence entries from this sprint apply immediately to Sprint N+1 stories.
3. `scrum_master` [SM-RETRO mode] — Sprint review (shipped vs committed) + retrospective (3 working / 3 improve / 3 actions) + velocity update + Loop Engine Report (Fix 7) + next sprint seeded in $TRACKER

   COMPREHENSION DEBT CHECK (Fix 40B) — SM-RETRO must include this human-facing block:
   ```
   ⚠️ COMPREHENSION DEBT CHECK — answer before Sprint N+1 starts:
   □ Did every team member READ the diffs shipped this sprint (not just approve)?
   □ Spot-check: pick 2 PRs the agents opened. Can you verify the gate that approved them
     actually catches the failure mode it was written for? (Gates rot silently.)
   □ Is any module now "owned by the loop, understood by no one"?
     If YES → flag it. Schedule a manual review session before Sprint N+1 touches that module.
   □ Cognitive surrender check: can each team member explain WHY the top 3 changes were made?
     If NO → comprehension debt is accumulating. Slow the loop. Read the code.
   ```
   DEBT SCORING RUBRIC (Fix 41B) — count YES answers to the 4 checklist items above:
   ```
   4/4 YES → debt=low      → proceed to Sprint N+1
   3/4 YES → debt=medium   → note in retro, monitor next sprint, proceed with warning
   2/4 YES → debt=high     → BLOCK Sprint N+1 (manual review sprint required first)
   1/4 YES → debt=critical → BLOCK + escalate to user immediately
   0/4 YES → debt=critical → BLOCK + escalate to user immediately
   Any module flagged "owned by loop, understood by no one" → debt=high MINIMUM regardless of score
   ```
   Log: `[COMPREHENSION-DEBT: score=N/4 | debt=low/medium/high/critical | modules-at-risk: <list> | action: <none/warning/review-sprint/escalate>]`
   If debt=high or critical → SM-RETRO BLOCKS Sprint N+1 start. Scrum Master must surface to user.

   LESSON AGE CHECK (Fix 42B) — runs AFTER comprehension debt check, BEFORE Sprint N+1:
   Scan `docs/lessons.md`. For each entry tagged [Stage 1-Fail]:
     - If the lesson's sprint stamp is OLDER than the current sprint → "stale blocker"
     - A stale blocker = a failure that was known but NOT investigated across at least 1 full sprint

   ```
   Stale blocker count:
   0 stale blockers → proceed
   1 stale blocker  → flag in retro, assign owning role, monitor (proceed with warning)
   2+ stale blockers → BLOCK Sprint N+1 (separate from comprehension debt block)
   Any stale blocker in: auth / payments / billing / database / security → BLOCK regardless of count
   ```
   Log: `[LESSON-AGE: N stale blockers | oldest=[lesson title] age=[N sprints] | action: BLOCK/FLAG/OK]`
   If blocked → scrum_master emits:
     ⚠️ LESSON AGE BLOCK: [N] Stage-1-Fail lessons are stale (>1 sprint old with no progression).
     Sprint N+1 is blocked. Required: for each stale lesson, move to Stage 2 (Investigate) or
     document why it's deprioritized. Reply "Lessons reviewed — resume sprint N+1" to continue.

**Announce:** `"Sprint N complete. Shipped: X/Y stories. Velocity: Z pts. Blockers carried: N. Proceed to Sprint N+1?"`
Wait for explicit YES.

---

### GATE 5 — PHASE-END GATE (after all sprints in a phase complete)

**Trigger (Fix 25L):** Any of the following:
  (a) User explicitly says "end of phase" or "phase complete"
  (b) sprint-plan.md has an EPIC label AND all stories in the EPIC are DONE across all sprints
  (c) Sprint number mod 3 === 0 (every 3rd sprint = automatic phase boundary)
  Before Phase N+1 can begin.

**Purpose:** Holistic quality check across the ENTIRE phase — not just individual features, but how they work together.

**Step 1 — Full Regression QA (qa_engineer):**
```
1. Run FULL test suite (not just last sprint's tests):
   - All unit tests across phase scope
   - All integration tests (cross-feature interactions)
   - Contract tests (API consumers still compatible)
   - Load test at expected phase-N traffic levels
   - E2E smoke tests covering all phase-N user journeys

2. Produce Phase QA Report → `/docs/phase-N/QA-REPORT.md`:
   | Metric | Target | Actual | Status |
   |--------|--------|--------|--------|
   | Unit coverage | ≥X% | Y% | GREEN/RED |
   | Integration pass rate | 100% | Y% | GREEN/RED |
   | Contract tests | all green | Y failures | GREEN/RED |
   | Load (p95 latency) | <Xms at Y RPS | Zms | GREEN/RED |
   | E2E journeys | all pass | Y/Z pass | GREEN/RED |
   | Regressions found | 0 | N | GREEN/RED |
```

**Step 2 — Phase Security Audit (security_engineer):**
```
1. Full SAST scan across ALL code added in this phase
2. Dependency audit (all packages added during phase)
3. OWASP Top 10 review of phase's combined attack surface
4. Secrets scan of entire repo (not just last commit)
5. Auth/access control review across all new endpoints

6. Produce Phase Security Report → `/docs/phase-N/SECURITY-REPORT.md`:
   | Check | Result | Findings |
   |-------|--------|----------|
   | SAST | CLEAN/FINDINGS | list |
   | Dependency CVEs | CLEAN/FINDINGS | list |
   | OWASP review | PASS/FAIL | list items failed |
   | Secrets scan | CLEAN/FOUND | details |
   | Auth review | PASS/FAIL | gaps found |
```

**Step 3 — Rejection Loop (if ANY item RED):**

```
IF QA or Security report has RED items:
  1. Identify specific stories/features that caused failures
  2. Reopen their Jira stories:
     jira.transitionIssue(story_id, status="In Progress")
     jira.addComment(story_id, 
       "PHASE-END GATE FAILED:\n" +
       "Finding: <specific failure>\n" +
       "Root cause: <what's wrong>\n" +
       "Required fix: <concrete action>\n" +
       "Assigned to: <backend_lead|frontend_lead>\n" +
       "Deadline: <before phase can close>"
     )
  3. Route to responsible engineer:
     - Backend issue → backend_lead + senior_engineer_be
     - Frontend issue → frontend_lead + senior_engineer_fe
     - Security issue → security_engineer provides fix guidance, engineer implements
     - Infrastructure issue → devops_engineer
  4. Engineer fixes → QA re-tests ONLY the failed items
  5. Re-run GATE 5 checks on fixed items
  6. Repeat until ALL GREEN

GATE 5 BLOCKS Phase N+1 until:
  - QA Report: ALL GREEN
  - Security Report: ALL GREEN (zero HIGH/CRITICAL)
  - All reopened stories re-closed in Jira
```

**Step 4 — Phase Closure:**

When GATE 5 passes:
1. Produce all 6 phase-end reports (QA, Security, Mapping, Discipline, Jira, Git)
2. `scrum_master` marks phase as DONE in roadmap
3. Announce: `"Phase N CLOSED. QA: GREEN. Security: GREEN. Ready to begin Phase N+1?"`
4. Wait for explicit YES before starting next phase

**Non-negotiable:** Code in Phase N+1 CANNOT begin while GATE 5 is RED. No "we'll fix it later" carries.

---

#### PHASE-END REPORT TEMPLATES (Fix 15B)

All 6 reports are produced at Step 4. QA-REPORT.md and SECURITY-REPORT.md templates are defined in GATE 5 Step 1-2 above. The remaining 4:

---

**DISCIPLINE-REPORT.md** → `/docs/phase-N/DISCIPLINE-REPORT.md` | Owner: scrum_master

```markdown
# Discipline Report — Phase N

## Token / Context Discipline
| Role | Tool calls this phase | Peak tier breaches | Reads > 2-read rule | Skill files loaded (avg per activation) |
|------|-----------------------|--------------------|---------------------|----------------------------------------|
| architect | N | N | N | N |
| [all active roles] | | | | |

**Overall tier:** PEAK / GOOD / DEGRADING / CRITICAL
**Worst breach:** [role + what happened]
**Action:** [none / add to lessons.md / change operating rule]

## Skill Activation Compliance
| Role | Activations | Matrix-compliant | Improvised (no matrix lookup) | Missing skill files logged |
|------|-------------|-----------------|-------------------------------|---------------------------|
| [role] | N | N | N | N |

## Context Rot Events
| Session | Rot detected at tool call # | Type (coherence/goal drift) | Resolution |
|---------|-----------------------------|-----------------------------|------------|

## Summary verdict: [GREEN / YELLOW / RED] — [one sentence reason]
```

---

**JIRA-REPORT.md** → `/docs/phase-N/JIRA-REPORT.md` | Owner: scrum_master

```markdown
# Tracker Activity Report — Phase N
Tracker: [TRACKER_MODE value] | Phase dates: [start] → [end]

## Velocity
| Sprint | Planned points | Completed points | Carry-over | Carry-over reason |
|--------|---------------|-----------------|------------|-------------------|
| S1 | N | N | N | [scope cut / blocked / re-spec] |
| S2 | | | | |
| **Phase total** | | | | |

## Story Status
| Status | Count | % of phase scope |
|--------|-------|-----------------|
| Done | N | N% |
| Carry-over to next phase | N | N% |
| Scope-cut (removed) | N | N% |
| Blocked (unresolved) | N | N% |

## Blocker Log
| Story ID | Blocker description | Raised by | Resolution | Days blocked |
|----------|--------------------|-----------|-----------:|:------------:|

## Summary verdict: [GREEN / YELLOW / RED]
GREEN = ≥80% planned points delivered. YELLOW = 60-79%. RED = <60%.
```

---

**GIT-REPORT.md** → `/docs/phase-N/GIT-REPORT.md` | Owner: devops_engineer

```markdown
# Git Activity Report — Phase N

## Commit Summary
| Type | Count | % of total |
|------|-------|-----------|
| feat | N | N% |
| fix | N | N% |
| refactor | N | N% |
| test | N | N% |
| docs | N | N% |
| chore | N | N% |
| **Total** | N | 100% |

## PR Health
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| PRs opened | N | — | — |
| PRs merged | N | — | — |
| PRs rejected / closed without merge | N | 0 ideally | [GREEN/RED] |
| Avg time PR open → merged | Xh | < 24h | [GREEN/RED] |
| PRs merged without review | N | 0 | [GREEN/RED] |

## Branch Hygiene
| Check | Result |
|-------|--------|
| Stale branches (>7 days, unmerged, no activity) | N found — [list] |
| Direct commits to main/master | N found — [list if any] |
| Feature branches following naming convention | N% compliant |

## Coverage Delta
| Metric | Phase start | Phase end | Delta |
|--------|------------|-----------|-------|
| Unit coverage | N% | N% | ±N% |
| Integration coverage | N% | N% | ±N% |

## Summary verdict: [GREEN / YELLOW / RED]
GREEN = coverage increased or held, 0 PRs merged without review, 0 direct commits to main.
```

---

**MAPPING-REPORT.md** → `/docs/phase-N/MAPPING-REPORT.md` | Owner: architect

```markdown
# Traceability Mapping Report — Phase N

## Story → Code Traceability
| Story ID | Story title | Commits referencing this story | Code files changed | Mapped? |
|----------|-------------|-------------------------------|-------------------|---------|
| PROJ-101 | User auth | abc1234, def5678 | auth/*, middleware/* | ✅ |
| PROJ-102 | Dashboard | [none found] | — | ❌ UNMAPPED |

**Unmapped stories** (code shipped with no traceable story): [list or "none"]
**Orphan commits** (commits with no story reference in message): [list or "none"]

## PRD Coverage
| PRD requirement | Implemented in phase N? | Story ID | Notes |
|----------------|------------------------|----------|-------|
| [req text] | YES / NO / PARTIAL | ID | |

**PRD gaps** (requirements with no implementation and no explicit deferral): [list or "none"]

## Summary verdict: [GREEN / YELLOW / RED]
GREEN = 100% stories mapped to commits, 0 PRD gaps without explicit deferral decision.
```

---

---

## MODE 1 SELF-CHECK (before proceeding to DEVELOP)

Run before any DEVELOP phase work begins in Mode 1. All must be checked before advancing.

- [ ] ≥2 phases decomposed?
- [ ] Each phase has ≥2 sprints?
- [ ] Each sprint has ≥3 tasks?
- [ ] 8+ docs per phase?
- [ ] All gates defined (Think→Design, Design→Develop)?
- [ ] Security/QA/DevOps tasks in sprint plan?
- [ ] Git: feature branches, task IDs, no secrets?
- [ ] **DESIGN SYSTEM GATE (Fix 22C / Fix 25B):**
  If sprint has frontend/* stories:
    → verify docs/design_system.md exists (web component library, ≥200 words with components section)
  If sprint has mobile/* stories:
    → verify docs/design_system_mobile.md exists (iOS HIG + Material Design tokens, ≥200 words with platform section)
  If sprint has BOTH frontend/* and mobile/*:
    → verify BOTH docs/design_system.md AND docs/design_system_mobile.md
  Missing doc behavior (Fix 25B): DO NOT inject into Sprint 1 backlog.
    Instead: BLOCK Sprint 1 start. Flag as prerequisite:
    "Sprint 1 blocked until design_system[_mobile].md exists. Create it before sprint planning."
    Rationale: injecting into Sprint 1 competes with real stories for token budget, triggering DEGRADING earlier.
- [ ] **LABEL GATE (Fix 23B / Fix 24C):** Confirm SM-PLAN emitted [LABEL CHECK: N/N stories labeled ✅] before this sprint was finalized. If that log line is absent → block. SM-PLAN is self-gating; this is the confirmation only.
- [ ] Mapping + Discipline reports planned?
- [ ] **QA report after EVERY phase** (covers all sprints — tests run, coverage, pass/fail per sprint)?
- [ ] **Security report after EVERY phase** (covers all sprints — audit, scan results, findings per sprint)?
- [ ] **Mapping report after EVERY phase** (covers all sprints — task status per sprint)?
- [ ] **Discipline report after EVERY phase** (covers all sprints — token metrics, tier, grade per sprint)?
- [ ] **Jira Task Tracking report after EVERY phase** (covers all sprints — epic/story/task status per sprint)?
- [ ] **Git Commit/Branch Tracking report after EVERY phase** (covers all sprints — commits, branches, merges per sprint)?

---

## PHASE PARALLELISM RULES (Fix 11D — Mode 1 and Mode 4 only)

Agents marked `[PARALLEL]` within the same phase can activate concurrently via Fix 10C lane model.
Agents without `[PARALLEL]` are sequential — must wait for the previous agent's artifact before starting.
SM-GATE still collects ALL outputs before the phase advances. Parallelism is within-phase only.

### THINK PHASE — sequential
```
market_researcher → cto   (cto reads market-researcher output)
```

### DESIGN PHASE — partial parallel
```
product_manager          SEQUENTIAL first — PRD is input to architect
architect                SEQUENTIAL second — service decomposition is input to db/cloud
database_architect       [PARALLEL with cloud_architect, finops_architect]
cloud_architect          [PARALLEL with database_architect, finops_architect]
finops_architect         [PARALLEL with database_architect, cloud_architect]
security_engineer        SEQUENTIAL last — threat model reads PRD + architecture + schema
scrum_master (SM-GATE)   SEQUENTIAL after all above — gates on complete DESIGN artifacts
```

### DEVELOP PHASE — parallel lanes (per Fix 10C)
```
devops_engineer          [PARALLEL with backend_lead + frontend_lead] — CI/CD setup is independent
backend_lead             [PARALLEL with frontend_lead] — independent domains
frontend_lead            [PARALLEL with backend_lead]
ml_engineer              [PARALLEL with frontend_lead if no API contract dependency yet]
senior_engineer_be/fe    [PARALLEL — up to 3 story lanes per Fix 10C]
qa_engineer              SEQUENTIAL per story — checker runs after maker FINAL
security_engineer (S1)   SEQUENTIAL — runs once before sprint coding starts
security_engineer (S2)   SEQUENTIAL per story — runs after checker approves
```

### LAUNCH PHASE — sequential
```
data_scientist → website_creator → scrum_master (SM-RETRO)
```

**Lane conflict rule:** If two parallel stories modify the same file → merge them into a single sequential lane before execution. Check at sprint planning, not at runtime.

---

