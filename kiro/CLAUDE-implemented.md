# KIRO SYSTEM — PATCH INSTRUCTIONS
# Fixes for identified structural lows. These rules OVERRIDE conflicting behavior in existing steering/hooks.

---

## APPLICATION SEQUENCE — APPLY IN THIS ORDER

Each fix creates the foundation the next fix depends on.
Applying out of order leaves a fix without its required support layer.

```
SEQUENCE   FIX    WHAT IT ESTABLISHES               WHAT IT ENABLES DOWNSTREAM
─────────────────────────────────────────────────────────────────────────────────
  1st    Fix 1   $TRACKER abstraction               Fixes 2,5,7,9,10 — all
                 All tracker calls routed through    tracker interactions are
                 one interface with markdown         now portable
                 fallback

  2nd    Fix 4   Steering files load correctly      Fixes 2,7,9 — agents cannot
                 team-orchestrator.md and            activate with the right
                 loop-engine.md load before          constitution until this is
                 any agent activates                 applied

  3rd    Fix 2   SM split into 4 modes              Fix 7 — SM-RETRO holds Loop
                 SM-GATE / SM-PLAN / SM-RETRO /      Report; SM-UNBLOCK handles
                 SM-UNBLOCK are separate             hard stops
                 agent calls                         Fix 10B — loop spec is a
                                                     SM-GATE checklist item

  4th    Fix 3   Shared base + role-specific        Fix 9 — shared skill
                 skill overlay for senior            ownership uses owners field
                 engineers                           Fix 8D — per-role budget
                                                     is accurate only when skill
                                                     file counts are known

  5th    Fix 5   Conflict arbitration chain         Fix 10B — if loop spec
                 CTO/Architect/Security              conflicts with PRD, chain
                 own their domains                   resolves it before loop starts

  6th    Fix 7   Loop engine core mechanics         Fix 8 — iteration pruning
                 PLAN→DO→VERIFY→DECIDE loop,         exists to wrap
                 maker/checker split,                Fix 9 — loop criteria need
                 Ralph Wiggum guard,                 skill outputs to populate
                 stop conditions                     Fix 10A — DO step needs
                                                     code-to-disk rule

  7th    Fix 8   Token/memory/context               Fix 9 — per-role budget
                 discipline                          governs skill file reads
                 Hook gate, iteration               Fix 6 — lean discipline
                 pruning, canonicalization,          profile is a simplification
                 per-role budget, mid-session        of Fix 8 rules
                 rot, subagent enforcement,          Fix 10C — parallel
                 skill matrix inlining               subagents each get
                                                     independent counters

  8th    Fix 9   Skill activation pipeline          Fix 10B — loop spec
                 Job label → skill files →           criteria come from skill
                 loop criteria auto-                 outputs so lead roles know
                 populated from skill                exactly what to write
                 outputs → checker                   Fix 10C — parallel
                 skill-aware                         subagents each activate
                                                     skills independently

  9th    Fix 6   Lean Mode (Mode 5)                 Terminal — no downstream
                 Simplification of Fixes             dependencies. Only applied
                 1-9 for small teams.                after all prior fixes so
                 Lean Loop, lean                     it correctly references
                 discipline, lean                    each one.
                 skill activation

  10th   Fix 10  Remaining execution gaps           Closes the loop entirely.
                 Code persistence,                   Without this, the pipeline
                 loop spec authorship,               has four silent failure
                 sprint parallelism,                 modes that break sprints
                 feature branch lifecycle            in production.
```

**Enforcement rule:** When a kiro session starts fresh, apply fixes in this sequence.
Do not activate any agent that depends on a later fix before the earlier fix is applied.
If a fix cannot be applied (e.g. no $TRACKER found), announce the degraded state and
apply the fallback defined in that fix before continuing.

---

---

## FIX 1 — PROJECT TRACKER ABSTRACTION (replaces hard-coded Jira calls)

**Problem:** Gate 2 and all DEVELOP phase instructions hard-code `jira.*` calls. No Jira = broken pipeline.

**Rule:** At GATE 2 (before any tracker calls), detect the available tracker once and lock it for the session:

```
DETECT TRACKER (run once at GATE 2, store result as $TRACKER):
  1. Check connected MCPs for: Jira, Linear, GitHub Projects, Asana, ClickUp, Notion, Monday
  2. If multiple found → present to user: "Which tracker should I use? [list]" → wait for answer
  3. If none found → use MARKDOWN FALLBACK (see below)
  4. Lock $TRACKER for entire session — never re-detect mid-session

MARKDOWN FALLBACK (when no tracker MCP is available):
  - Create /docs/backlog/stories.md with the same schema as Jira stories
  - Create /docs/backlog/sprints.md for sprint assignments
  - All "jira.*" calls in team-orchestrator.md translate to writes to these files
  - At Gate 3 (QA → commit), checklist items are written as GitHub PR descriptions instead
  - Announce: "No tracker MCP found. Using markdown backlog at /docs/backlog/."
```

**Tracker call translation table:**

| team-orchestrator.md says | What to actually do |
|---------------------------|---------------------|
| `jira.createProject(...)` | Create project in $TRACKER using its native API |
| `jira.createEpic(...)` | Create epic/milestone in $TRACKER |
| `jira.createStory(...)` | Create issue/card/story in $TRACKER with same fields |
| `jira.transitionIssue(...)` | Update status in $TRACKER |
| `jira.addComment(...)` | Add comment in $TRACKER |
| `jira.flagIssue(...)` | Add blocker label/flag in $TRACKER |
| `jira.createSprint(...)` | Create sprint/iteration in $TRACKER (if supported) |

---

## FIX 2 — SCRUM MASTER ROLE SPLIT (reduces concentration of responsibility)

**Problem:** Scrum Master gates the pre-build gate AND is the entity gated by it (self-review). Also holds planning, velocity, roadmap, and retro simultaneously.

**Rule:** Split Scrum Master into three distinct activation modes. Never run more than one mode in the same agent call.

```
SM-GATE    → runs pre-build checklist ONLY. Produces: GREEN/RED verdict + named blockers.
             Activated at: GATE 2 entry.
             Does NOT write sprint plans. Does NOT touch roadmap.

SM-PLAN    → runs sprint planning ONLY. Reads roadmap section for current phase.
             Produces: /docs/phase-N/sprint-plan.md
             Activated at: after GATE 2 passes (SM-GATE is GREEN).
             Does NOT run gates. Does NOT run retros.

SM-RETRO   → runs sprint retro + velocity update ONLY.
             Produces: retro summary + next sprint seeded in tracker.
             Activated at: GATE 4 (sprint end).
             Does NOT run gates. Does NOT write sprint plans.

SM-UNBLOCK → handles mid-sprint blockers and Fix 7 hard-stop escalations ONLY.
             Triggered by: loop hard stop (8 iterations hit), story blocked mid-sprint,
             dependency not resolved by implementing role.
             Produces: one of three decisions →
               SCOPE-CUT:  remove the failing story from sprint, carry to next
               RE-SPEC:    story's loop spec is wrong — rewrite criteria/verifier, reset loop
               ESCALATE:   problem is architectural — route to architect or security_engineer
             Does NOT run gates. Does NOT write sprint plans. Does NOT run retros.
             Hard stop escalation format:
               "[Story ID] hit 8-iteration cap. Unresolved: [criteria list].
                SM-UNBLOCK decision: [SCOPE-CUT / RE-SPEC / ESCALATE] — reason: [why]"
             Logs decision in $TRACKER and in sprint retro as a carry item.
```

**Gate 2 execution order (replaces current merged flow):**
1. SM-GATE reviews all DESIGN artifacts → produces verdict
2. If GREEN → SM-PLAN writes roadmap + sprint plan → tracker creation begins
3. SM-GATE and SM-PLAN must be separate agent calls (no merging)

---

## FIX 3 — FE/BE ENGINEER SKILL DIFFERENTIATION

**Problem:** `senior_engineer_fe` and `senior_engineer_be` have identical skill file names. Structural duplication with no genuine role separation.

**Rule:** When activating either role, load the SHARED base first, then the ROLE-SPECIFIC overlay. If the overlay file doesn't exist yet, treat the shared file as sufficient and note the gap.

```
SHARED BASE (both roles load these):
  - code_review_excellence.md
  - debugging_methodology.md
  - error_handling_strategies.md
  - feature_flags_safely.md
  - tdd_red_green_refactor.md

BACKEND-SPECIFIC (senior_engineer_be loads in addition):
  - concurrency_safety.md         ← thread safety, race conditions, async patterns
  - performance_profiling.md      ← query optimization, memory profiling, CPU flamegraphs
  - refactoring_safely.md         ← backend-specific: DB migrations, API versioning safety

FRONTEND-SPECIFIC (senior_engineer_fe loads in addition):
  - concurrency_safety.md         ← event loop, Promise chains, React concurrent mode
  - performance_profiling.md      ← bundle analysis, render profiling, CWV optimization
  - refactoring_safely.md         ← FE-specific: component extraction, state migration safety

AUDIT ACTION REQUIRED:
  Open kiro/skills/senior_engineer_fe/ and kiro/skills/senior_engineer_be/ and verify
  whether the .md files are byte-for-byte identical. If yes → differentiate file contents
  before next use. If already differentiated → remove this fix note.
```

---

## FIX 4 — STEERING FILE INCLUSION ASYMMETRY

**Problem:** `orchestrator-routing.md` has `inclusion: always` but references `team-orchestrator.md` which is `inclusion: manual`. Router fires without the constitution it needs.

**Rule:** At the start of any Mode 1 or Mode 4 session, load team-orchestrator.md explicitly before any routing decision executes.

```
SESSION START PROTOCOL (add to orchestrator-routing.md preamble):

IF mode detected is Mode 1 OR Mode 4:
  IMMEDIATELY load: kiro/steering/team-orchestrator.md
  VERIFY: team-orchestrator.md is in context before any role is invoked
  IF not in context: STOP. Announce "Constitution not loaded. Run [BOOT] or manually
    include kiro/steering/team-orchestrator.md." Do not proceed.

IF mode is Mode 2 OR Mode 3:
  team-orchestrator.md is NOT needed — skip load (token savings)

DEVELOP PHASE LOAD (in addition to above — fires when DEVELOP starts):
  IMMEDIATELY load: kiro/steering/loop-engine.md
  VERIFY: loop-engine.md is in context before senior_engineer activates
  IF not in context: STOP. Announce "Loop engine not loaded. Load kiro/steering/loop-engine.md
    before proceeding to DEVELOP." Do not invoke senior_engineer without it.
  Applies to: Mode 1, Mode 4, and Mode 5 (lean — uses simplified loop rules from Fix 6).
  Does NOT apply to: Mode 2 (single agent), Mode 3 (direct execution).

ENVIRONMENT DETECTION (runs once at session start, before any phase begins):
  STEP 1 — DETECT_TRACKER (Fix 1): detect $TRACKER type → set TRACKER_MODE
  STEP 2 — DETECT_REMOTE (Fix 10D): run `git remote -v`
    → remote listed   : set GIT_MODE=REMOTE
    → no output       : set GIT_MODE=LOCAL
    → push fails later: downgrade to GIT_MODE=LOCAL (SM-UNBLOCK notified)
  Log both detections in one line:
    "[ENV] TRACKER_MODE=<jira|linear|github|markdown> | GIT_MODE=<REMOTE|LOCAL>"
  These two values govern all tracker and git actions for the entire session.
  Never re-detect mid-sprint unless SM-UNBLOCK explicitly calls a re-detect.

HOOK SAFETY CHECK:
  When elite-team-orchestrator.kiro.hook fires:
  - First action: confirm team-orchestrator.md is in steering context
  - If absent: fetch it before invoking any role
  - Never invoke a role without the constitution loaded in Mode 1/4
```

---

## FIX 5 — CONFLICT RESOLUTION PROTOCOL

**Problem:** No rule for when two peer-level roles make contradictory decisions. "ADR required" is insufficient without an arbitration chain.

**Rule:** Add an explicit escalation chain for role conflicts.

```
CONFLICT DETECTION:
  A conflict exists when Role A's artifact explicitly contradicts Role B's artifact
  on a BINDING decision (tech stack choice, data model, auth approach, cost ceiling).

  Contradictions on implementation preferences (code style, naming) → NOT a conflict.
  Contradictions on architectural constraints → IS a conflict. Block immediately.

ARBITRATION CHAIN (in order):
  Tier 1 — CTO is final authority on: tech stack, build-vs-buy, vendor choices, risk tolerance
  Tier 2 — Architect is final authority on: service boundaries, API contracts, data model shape
  Tier 3 — Security Engineer is final authority on: auth design, compliance constraints, secrets
  Tier 4 — User escalation: if Tier 1-3 roles themselves conflict → surface to user with:
    "CONFLICT: [Role A] says [X]. [Role B] says [Y]. These are mutually exclusive.
     Which do you want to lock? Once locked, it becomes a binding ADR."

CONFLICT RESOLUTION STEPS:
  1. Identify the two conflicting artifacts and the specific contradicting statements
  2. Determine which tier owns the decision domain
  3. The owning-tier role produces a superseding ADR (ADR-NNN-CONFLICT)
  4. Downstream roles update their artifacts to reflect the resolved decision
  5. Log in /docs/decisions/index.md with label: [CONFLICT-RESOLVED]
  6. No phase advances until conflict is closed

NON-NEGOTIABLE: A role never silently adopts a conflicting decision without an ADR.
"I'll just use what the architect said" without a logged ADR = compliance violation.
```

---

## FIX 6 — LEAN TEAM MODE (small team / solo developer)

**Problem:** No guidance for 1-3 person teams. 19 roles across full pipeline is overkill for most projects. Mode 3 ("just build it") exists but skips all planning value.

**Add Mode 5 to orchestrator-routing.md:**

```
### MODE 5: Lean Team (3-Role Collapse)

Trigger: User says "lean mode", "small team", "startup mode", "mode 5", or team size ≤ 3.

Role collapse map:
  STRATEGIST  = market_researcher + cto + product_manager (combined)
  BUILDER     = architect + backend_lead + frontend_lead + senior_engineer_be/fe (combined)
  QUALITY     = security_engineer + qa_engineer + devops_engineer + sre_engineer (combined)

Phase structure:
  THINK  (STRATEGIST)  → Single doc: /docs/lean/strategy.md
                         Covers: personas, tech choices, PRD, key risks
                         Gate: user confirms strategy (1 question, not full Gate 1 checklist)

  BUILD  (BUILDER)     → Sprint loop: 1-week sprints, no Jira required (markdown backlog)
                         Architecture decisions inline in code comments or /docs/lean/decisions.md
                         No formal ADR ceremony — decision log entries are sufficient

  SHIP   (QUALITY)     → Security: OWASP Top 10 checklist + secrets scan (S2 + S3 gates intact)
                         QA: unit tests + manual smoke (no load testing requirement)
                         Deploy: CI/CD minimal (GitHub Actions or equivalent)

What Lean Mode KEEPS from full pipeline:
  - Security gates S2 (OWASP/SAST) and S3 (secrets hook) — non-negotiable even lean
  - Git commit format (abbreviated: type/scope/what/why — no full template required)
  - Explicit user confirmation before SHIP phase

What Lean Mode DROPS:
  - Formal Jira creation
  - Full ADR ceremony (decision log replaces)
  - Phase-end QA/Security reports (inline comments replace)
  - FinOps baseline (revisit at $1K+/month cloud spend)
  - Technical Writer trigger (team writes their own docs)
  - Full pre-build gate checklist (INVEST/acceptance criteria still required;
    loop spec required in simplified form — see LEAN LOOP below)

LEAN LOOP — Fix 7 applied to Mode 5 (resolves conflict with full Fix 7):

  Pre-build: loop spec IS required, but simplified:
    GOAL: [one sentence, falsifiable]
    VERIFIER: [one command that auto-rejects bad work]
    CRITERIA: [2 items max, scored 1-10]
    STOP WHEN: both criteria ≥ 8, OR 4 iterations reached (half the full cap)

  Maker/checker split (adapted for single BUILDER role):
    BUILDER acts as maker first: runs the loop, scores criteria each iteration.
    When BUILDER writes FINAL → start a NEW context turn with ONLY:
      story AC + code diff + verifier output (no loop-state narrative, no self-scores)
    BUILDER in checker mode scores independently in that fresh turn.
    If checker scores differ from maker scores by ≥ 2 on any criterion → rejection,
      return to maker mode, iteration counter continues (does NOT reset).
    This preserves the maker/checker isolation without requiring a separate agent.

  Loop-state: inline in the markdown backlog story entry (no separate file required).

  Ralph Wiggum Guard still applies: BUILDER cannot write FINAL with any criterion < 7.

  No Loop Engine Report at sprint retro (verbal summary: "N stories, avg Y iterations" is enough).

  Security gates S2 and S3 remain inside the verifier step — non-negotiable even in lean.

Upgrade path: At any point user can say "upgrade to full pipeline" →
  Orchestrator reads existing lean docs → maps to foundation doc structure →
  creates Jira project from markdown backlog → transitions to Mode 1 from current phase.
```

---

## FIX 7 — LOOP ENGINEERING INTEGRATION (replaces linear story execution)

**Problem:** The current pipeline moves linearly: engineer writes code → QA reviews → pass/fail.
There is no iteration inside a feature. The engineer self-declares done, and the model that wrote
the code is too generous grading its own homework.

**Rule:** Load `kiro/steering/loop-engine.md` at the start of every DEVELOP phase.
Every story now runs as a loop before it reaches QA.

### What changes in the pipeline

**At GATE 2 (pre-build):**
Every story must have a LOOP SPEC written before sprint starts. The loop spec is a gate item.
A story without a loop spec = blocked. Add to the pre-build checklist:
- [ ] Every story has a LOOP SPEC with: GOAL, VERIFIER commands, CRITERIA (3-5 items), STOP WHEN

**In DEVELOP (story execution):**
Replace: "senior_engineer writes code, QA reviews"
With:
```
1. senior_engineer (MAKER) runs self-checking loop:
   PLAN → DO → VERIFY (score 1-10) → DECIDE (ITERATING or FINAL)
   Repeats until all criteria ≥ 8 OR 8 iterations hit.

2. qa_engineer (CHECKER) receives ONLY: story AC + code diff + verifier output.
   Runs independent verifier. Scores criteria independently.
   Only the checker can transition story to Done.
```

**At sprint end (GATE 4):**
scrum_master adds Loop Engine Report to retro:
total iterations / hard stops / checker approve rate / cost-per-accepted-change.
If approve rate < 50% → loop specs reviewed before next sprint starts.

### Key rules (abbreviated — full detail in loop-engine.md)
- Maker CANNOT self-declare done. Only checker can approve.
- Checker NEVER reads maker's self-scores or loop-state narrative.
- Hard stop at 8 iterations — no exceptions, escalate to scrum_master.
- Ralph Wiggum Guard: if maker scores differ from checker by ≥ 2 → rejection, iteration continues.
- Loop state logged per story at `/docs/phase-N/loop-states/[story-id].md`
- Cost-per-accepted-change tracked: ≥ 1 approval per 3 iterations average is the target.

### Loop build order (for recurring kiro tasks)
Manual run → harden as skill → wrap in loop spec → then and only then schedule.
Never schedule something you have not proven reliable by hand.

**Reference:** `kiro/steering/loop-engine.md` — load this file whenever DEVELOP phase activates.

---

## FIX 8 — TOKEN / MEMORY / CONTEXT DISCIPLINE OVERHAUL

**Problem:** The existing discipline system (hooks 01-03, context-rot hook, context-memory-discipline
steering) has three structural failures that compound across the full pipeline:

1. Hooks fire on every prompt/tool-use regardless of complexity — for a 10-token question,
   500+ tokens of discipline instructions are prepended. The cure costs more than the disease.
2. No rule for loop iteration context growth — Fix 7 loops accumulate raw PLAN/DO/VERIFY content
   across iterations unbounded. By iteration 6 the context is carrying 6 full code attempts.
3. The same discipline rules exist in 3+ places (CLAUDE.md, Hook 01, context-memory-discipline.md)
   with different thresholds — they drift and conflict, and the agent has to guess which wins.

**Additional gaps:** No per-role context budget (one verbose role can drain the entire session),
context rot detected only at session end (too late to act), subagent isolation is an honor system
with no enforcement, skill-selection-matrix.md adds a meta-lookup cost on every role activation.

---

### 8A — HOOK COMPLEXITY GATE (stop hooks firing on simple tasks)

**Rule:** Hooks 01 (token discipline) and 02 (context discipline) MUST NOT fire when the session
is below GOOD tier. They are expensive overhead for cheap tasks.

```
HOOK FIRING CONDITION (add to hooks 01 and 02 `when` block):

FIRE if ANY of:
  - Session read count ≥ 5
  - Session tool call count ≥ 10
  - Active role count > 1 (orchestrator has dispatched a subagent)
  - Mode is 1 or 4 (full pipeline — always fire)
  - DEVELOP phase is active

DO NOT FIRE if ALL of:
  - Session read count < 5
  - Tool call count < 10
  - Single-role or direct-execution context (Mode 2, Mode 3, Mode 5)
  - No active subagents

Hook 03 (memory discipline) and context-rot-detection ALWAYS fire — they are cheap
write-guards, not expensive prompt-prepend operations.
```

---

### 8B — LOOP ITERATION PRUNING (fixes Fix 7's context growth blind spot)

**Problem:** Each loop iteration produces PLAN + DO + VERIFY content. By iteration 6 of 8,
the context holds 6 full code diffs, 6 verifier outputs, and 6 self-assessments. This is
the exact compounding cost the article warns about and Fix 7 does not address.

**Rule:** After every completed iteration, apply this discard protocol BEFORE starting the next:

```
ITERATION CONTEXT PRUNE (runs between iterations, before PLAN of next pass):

KEEP in context:
  - Loop spec (GOAL + VERIFIER + CRITERIA + STOP WHEN) — never discard
  - Latest VERIFY block: criterion scores + weakest criterion only
  - Loop-state summary: "Tried X, failed because Y" — max 2 lines per past iteration
  - Current code state (the actual file being edited) — keep latest version only

DISCARD from context:
  - All previous iterations' raw DO output (the full code attempt)
  - All previous iterations' full VERIFY text (replaced by the 2-line summary)
  - All previous iterations' PLAN text
  - Intermediate verifier command output beyond first 10 lines

PRUNE FORMAT (what stays in context after iteration N):
  [LOOP STATE — iterations 1 to N]
  | Iter | Tried                    | Scores           | Weakest    |
  |------|--------------------------|------------------|------------|
  |  1   | [one-line summary]       | c1=X c2=X c3=X   | [crit]     |
  |  2   | [one-line summary]       | c1=X c2=X c3=X   | [crit]     |
  ...
  [Current code: only the final file state — not a diff, the actual content]
```

This caps loop context at: loop spec + N×1-line summaries + current code.
Context size stays roughly constant regardless of iteration count.

---

### 8C — RULE CANONICALIZATION (one source, no drift)

**Problem:** Discipline rules exist in: global CLAUDE.md, Hook 01, Hook 02,
`kiro/steering/context-memory-discipline.md`. When thresholds differ, the agent guesses.

**Canonical source of truth:** This file (`kiro/CLAUDE.md`) for all kiro-specific rules.
Global `~/.claude/CLAUDE.md` for session-wide defaults that apply outside kiro projects.

```
CANONICALIZATION RULES:

1. DEGRADATION TIERS — canonical definition (overrides all hooks and steering):
   PEAK       reads 0-4,  tool calls 0-9    → normal behavior
   GOOD       reads 5-7,  tool calls 10-14  → targeted reads (offset+limit), prefer map
   DEGRADING  reads 8-11, tool calls 15-19  → map-only, no new reads unless editing
   CRITICAL   reads 12+,  tool calls 20+    → FULL STOP, tell user, recommend new session

2. 2-READ RULE — canonical definition:
   Max 2 source file reads per task. Steering files (loaded at session start) do NOT count.
   Loop iteration pruning reads do NOT count (they are context management, not task reads).

3. CONFLICT RESOLUTION between this file and hooks/steering:
   kiro/CLAUDE.md wins on: kiro pipeline rules, role behavior, gate logic, discipline thresholds
   Global CLAUDE.md wins on: session startup, mode detection, memory kernel behavior
   Hooks win on: nothing — hooks implement these rules, they do not define them
   If a hook threshold differs from this file → update the hook to match. This file is the spec.
```

---

### 8D — PER-ROLE CONTEXT BUDGET

**Problem:** Degradation tiers are session-wide. One verbose role can push the session from
PEAK to CRITICAL before others even activate, leaving nothing for the sprint loop.

**Rule:** Allocate a read budget per role category. The session total is still the ceiling,
but roles are accountable to their own slice first.

```
PER-ROLE READ BUDGET (reads allocated per activation, not per session):

THINK phase roles (market_researcher, cto):          3 reads each
DESIGN phase roles (architect, db_architect,
  cloud_architect, finops_architect, security_engineer): 3 reads each
DESIGN gate (SM-GATE, SM-PLAN):                      2 reads each
DEVELOP roles (backend_lead, frontend_lead,
  senior_engineer_be/fe, ml_engineer):               2 reads each per loop iteration
  Note: loop iteration pruning (Fix 8B) is exempt from this count
QA / DevOps / SRE:                                   2 reads each
Technical Writer:                                    1 read (formats, does not research)
Orchestrator (routing + dispatch):                   1 read per phase (map only)

OVERAGE RULE: if a role needs to exceed its budget:
  → It MUST spawn a subagent for the extra reads (keeps main context clean)
  → It MUST report the overage: "[ROLE] used N reads (budget: M). Spawned subagent for delta."
  → It CANNOT silently consume session budget without disclosure

SESSION CEILING still applies. Per-role budgets are a floor, not a guarantee.
If session is DEGRADING, role budgets are halved. If CRITICAL, roles read nothing.
```

---

### 8E — MID-SESSION ROT DETECTION

**Problem:** Context-rot hook fires only at `agentStop`. Damage is discovered after the session
ends. A mid-session check is needed to catch rot while recovery is still possible.

**Rule:** Add a lightweight rot check every 10 tool calls during the session.

```
MID-SESSION ROT TRIGGER (add to Hook 02 or as a new Hook 06):

FIRES when: session tool call count is a multiple of 10 (10, 20, 30...).
LIGHTWEIGHT CHECK (not the full agentStop scan — just 3 questions):

  1. Has any init_doc file been written to more than 5 times this session?
     YES → check its line count. If > GREEN threshold → archive now, don't wait for session end.

  2. Is session at DEGRADING or CRITICAL tier?
     YES → announce tier. Remind user: remaining reads = [N]. Recommend subagents for research.

  3. Has the loop iteration count exceeded 5 for any active story?
     YES → apply Fix 8B prune immediately if not already done this iteration.

REPORT FORMAT (inline, one line per trigger):
  [ROT-CHECK @ tool-call N]: tier=DEGRADING | checkpoint=18 entries (archive at 20) | loop=iter 6
```

---

### 8F — SUBAGENT ISOLATION ENFORCEMENT

**Problem:** team-orchestrator.md declares "orchestrator holds summaries only" but there is no
mechanism preventing a role from writing its full artifact into the main context.
It is an honor system that breaks as soon as one role produces a large output.

**Rule:** Add a mandatory summarization step before any role artifact enters the orchestrator context.

```
ARTIFACT HANDOFF PROTOCOL (runs after every role completes its artifact):

ROLE produces artifact → BEFORE orchestrator receives it:

  1. ARTIFACT SUMMARY (role writes this, max 300 tokens):
     - What was decided (3-5 bullet points, specific not vague)
     - What was rejected and why (1-2 lines)
     - Upstream constraints passed to next role (concrete — version numbers, RPS targets, etc.)
     - Blockers or open questions (named, not "TBD")

  2. ORCHESTRATOR receives ONLY the summary, not the full artifact.
     Full artifact goes to: /docs/<appropriate path> (written to disk, not held in context).

  3. NEXT ROLE receives ONLY the relevant summary from upstream roles + its own skill files.
     Never receives: full artifacts from roles outside its dependency path.

ENFORCEMENT: if a role hands off more than 300 tokens of context to the orchestrator,
  orchestrator MUST compress it before routing. Do not pass it through uncompressed.
  Log: "[HANDOFF COMPRESSED: role=X, original=~N tokens, compressed=~300 tokens]"

EXCEPTION: senior_engineer receiving backend_lead's plan — this is direct upstream,
  full plan is permitted (it IS the task spec). Orchestrator does not intermediate here.
```

---

### 8G — SKILL MATRIX INLINING (eliminate per-activation lookup cost)

**Problem:** Every role activation requires reading `skill-selection-matrix.md` to decide which
2-4 files to load. Across a full pipeline run, this adds 50+ matrix reads consuming context
before any role does real work.

**Rule:** Inline the skill selection logic into each role's `SKILL.md` directly.

```
SKILL.md REQUIRED SECTION (add to every role's SKILL.md file):

## Quick-Load Matrix
| Activity | Load These Files | Skip |
|----------|-----------------|------|
| [most common activity] | [file1.md, file2.md] | all others |
| [second activity]      | [file3.md]           | all others |
| [full activation]      | ALL                  | none |

When this section exists in SKILL.md:
  → Orchestrator reads SKILL.md once → gets both skill inventory AND load decision
  → skill-selection-matrix.md is NOT read (redundant)
  → Saves one read per role activation

MIGRATION: Until all SKILL.md files have this section, skill-selection-matrix.md
  is still the fallback. Prioritize adding Quick-Load Matrix to the 5 most-used roles first:
  senior_engineer_be, senior_engineer_fe, security_engineer, architect, qa_engineer.
```

---

### FIX 8 — ADJUSTMENTS TO FIXES 1–7

After adding Fix 8, the following targeted amendments apply to prior fixes:

**Fix 3 amendment:**
Skill file loading for senior_engineer counts toward the per-role budget (Fix 8D).
Shared base = 2 reads. Role-specific overlay = up to 3 more reads. Total = 5 reads per
senior_engineer activation. This puts them at GOOD tier immediately — meaning all reads
must use offset+limit (targeted ranges), not full file reads. Add to Fix 3:
"Load shared base first (2 reads). Load role-specific overlay second (max 2 reads, targeted).
Total senior_engineer read budget per loop iteration = 2 reads (Fix 8D). Use map/imports
for anything beyond that."

**Fix 4 amendment:**
team-orchestrator.md and loop-engine.md are large files loaded at session start.
They count as reads (2 reads used immediately at Mode 1/4/5 session start).
Add to Fix 4: "These files are loaded ONCE and cached as session references.
They do NOT count toward the 2-read rule for individual tasks — they are session-init reads.
However they DO count toward the session degradation tier total. A Mode 1 session starts
at GOOD tier (2 of 12 critical reads used before any work begins). Plan accordingly."

**Fix 6 amendment:**
Lean Mode (Mode 5) gets a simplified discipline profile per Fix 8A (hooks don't fire
below GOOD tier, and lean sessions rarely hit it). Add to Fix 6 LEAN LOOP section:
"Hook 01 and Hook 02 DO NOT fire in Lean Mode unless session crosses GOOD tier (5+ reads,
10+ tool calls). Below that, lean runs clean with no discipline overhead.
Iteration pruning (Fix 8B) still applies at the same cadence — discard raw DO content
after each of the 4 lean iterations."

**Fix 7 amendment:**
The self-checking loop prompt in loop-engine.md must include the iteration prune rule.
Add to every senior_engineer loop activation (after the RULES block):
"After each iteration, prune context per Fix 8B before starting PLAN of next iteration.
Keep: loop spec + scored VERIFY table + current file state.
Discard: all prior iterations' PLAN/DO/full VERIFY text.
This is mandatory — do not skip even if iteration count is low."

---

## FIX 9 — SKILL ACTIVATION PIPELINE (job → agent → correct skill → loop criteria)

**Problem:** The current flow is broken in two ways:

1. `elite-team-orchestrator.kiro.hook` says **"Read ALL `.md` files in `.kiro/skills/<role>/`"**
   on every role activation. This reads 8-20 files per role regardless of the task.
   It burns the per-role read budget (Fix 8D) before any work starts and contradicts the
   entire purpose of the skill-selection-matrix.

2. Skill files already have rich metadata (`id`, `owners`, `tags`, `when_to_use`, `inputs`,
   `outputs`) and `team-orchestrator.md` already tags subtasks with `labels: [skill_id_1, skill_id_2]`
   — but nothing connects these two pieces. The skill outputs are never used to auto-populate
   loop spec CRITERIA. The metadata is written but never read automatically.

**What this fix does:** Wires job assignment → skill tag extraction → targeted skill load →
loop spec criteria derived from skill outputs. The loop engine (Fix 7) becomes significantly
more effective because each agent starts with exactly the right knowledge loaded and the
loop criteria are grounded in the skill's own quality standards.

---

### 9A — FIX THE HOOK (replace read-all with read-targeted)

**Override for `elite-team-orchestrator.kiro.hook` Prime Directive 1:**

```
CURRENT (broken):
  "Read ALL .md files in .kiro/skills/<role>/"

REPLACE WITH:
  "Read ONLY the skill files identified by the Skill Activation Protocol (Fix 9B).
   Never read the full role skill folder. Max 3 skill files per role activation.
   If skill tags are absent, read the role's SKILL.md only (inventory + quick-load matrix).
   Never read more than SKILL.md without explicit skill tags to justify it."
```

This single change brings the hook into alignment with skill-selection-matrix intent and
respects Fix 8D per-role budgets.

---

### 9B — SKILL ACTIVATION PROTOCOL (job assignment → correct skill loaded)

Runs every time the orchestrator assigns a story/subtask to a role. Four steps, always in order.

```
STEP 1 — EXTRACT SKILL TAGS FROM JOB
  Source: the story/subtask in $TRACKER
  Read the `labels` field of the assigned subtask.
  Labels were set at GATE 2 by SM-PLAN using team-orchestrator.md subtask schema:
    labels: [<skill_id_1>, <skill_id_2>]  ← these are the skill file names without .md
  If labels are missing → SM-PLAN is incomplete. Block and request SM-PLAN to re-tag.

  Example: story US-042 subtask "Implement Redis cache layer"
    labels: [caching_strategies, circuit_breaker_bulkhead]
    role: senior_engineer_be

STEP 2 — RESOLVE SKILL FILE PATHS
  For each label: path = kiro/skills/<role>/<label>.md
  Verify the file exists. If not → try kiro/skills/<shared_base>/<label>.md
  If still not found → log "[SKILL NOT FOUND: label=X, role=Y]" and use generic role SKILL.md.

  For the example above:
    kiro/skills/backend_lead/caching_strategies.md       ✓
    kiro/skills/backend_lead/circuit_breaker_bulkhead.md ✓
  (senior_engineer_be inherits from backend_lead's skill folder — see Fix 3)

STEP 3 — LOAD AND EXTRACT (one read per skill file, targeted)
  Read each resolved skill file. Extract ONLY these frontmatter fields:
    - when_to_use  → confirms this skill is appropriate for the task
    - inputs       → what the agent must receive before starting
    - outputs      → what the agent must produce (becomes loop CRITERIA)
    - tags         → used for checker confirmation in Step 4

  Full skill file body is kept in context for the agent to use during the loop.
  Count: each skill file read = 1 read toward Fix 8D per-role budget.
  Max 3 skill files = 3 reads. With SKILL.md = 4 total. This is the role budget ceiling.

STEP 4 — CONFIRM ACTIVATION (agent announces before loop starts)
  Before the first loop iteration, agent writes:
  
  [SKILL ACTIVATION — story US-042, role: senior_engineer_be]
  Loaded:
    ✓ caching_strategies (v1.0.0) — owners: [backend_lead, senior_engineer_be]
      inputs:  hot_endpoint (RPS, payload size, freshness tolerance)
      outputs: cache_design (tier, TTL, invalidation strategy, stampede protection)
    ✓ circuit_breaker_bulkhead (vX.X.X) — loaded
  Inputs received from upstream: [list what was passed from orchestrator]
  Inputs missing: [any gaps — block if critical input is absent]
  Proceeding to loop spec derivation.
```

---

### 9C — LOOP SPEC AUTO-POPULATION FROM SKILL OUTPUTS

**Problem:** Loop spec CRITERIA are currently written generically ("tests pass", "lint clean").
The skill files already define exactly what quality outputs look like. Use them.

**Rule:** After skill activation (9B Step 4), the loop spec CRITERIA block is auto-populated
from the loaded skill files' `outputs` fields — not written from scratch.

```
LOOP SPEC CRITERIA DERIVATION:

For each loaded skill file's `outputs` field:
  → Each output becomes one criterion in the loop spec
  → The criterion is scored 1-10 (per loop engine Fix 7 scoring rubric)
  → The verifier for that criterion is derived from the output's expected form

EXAMPLE — from caching_strategies.md outputs:
  outputs:
    - cache_design: tier, TTL, invalidation strategy, stampede protection

  Becomes loop spec CRITERIA:
    - criterion-1: Cache tier selected and justified (L1/L2/L3/L4)
                   score: 1=not chosen, 8=tier chosen with measured justification
    - criterion-2: TTL defined per data freshness tolerance of hot_endpoint
                   score: 1=no TTL, 8=TTL matches stated freshness tolerance
    - criterion-3: Invalidation strategy documented (cache-aside / write-through / write-behind)
                   score: 1=missing, 8=strategy chosen with race condition analysis
    - criterion-4: Stampede protection in place (jitter / probabilistic expiry / lock)
                   score: 1=missing, 8=protection implemented and tested

VERIFIER for skill-derived criteria (in addition to test suite):
  Code review checklist generated from skill outputs — checker runs this independently.
  Each output field = one checklist item the checker confirms or denies.

BASELINE CRITERIA always present regardless of skill (from Fix 7):
  - All unit tests pass (from test suite)
  - Zero lint warnings
  - Type check clean
  - OWASP scan: zero HIGH/CRITICAL (from Security Gate S2)

FINAL LOOP SPEC = baseline criteria + skill-derived criteria (capped at 6 total).
If skill outputs would generate > 4 criteria, pick the 4 highest-impact ones.
```

---

### 9D — CHECKER SKILL VERIFICATION (closes the maker/checker loop on skills)

**Problem:** The checker (qa_engineer) receives code diff + verifier output but has no context
about which skill standards the maker was supposed to apply. Checker grades generically.

**Rule:** Checker receives the skill activation summary (9B Step 4) alongside the diff.

```
CHECKER HANDOFF PACKAGE (what qa_engineer receives — per Fix 7 maker/checker split):

  1. Story AC (acceptance criteria from PRD)
  2. Code diff (final file state, not intermediate iterations)
  3. Verifier output (test/lint/type results)
  4. Skill activation summary:
       - Which skills were loaded (name + version)
       - Skill-derived criteria and their expected outputs
       - Any inputs that were flagged as missing at Step 4
  5. Maker's final VERIFY scores (the table row — not the narrative)

CHECKER TASK: verify the code satisfies the skill's OUTPUTS, not just that tests pass.
  For each skill-derived criterion: confirm or deny with specific evidence from the diff.
  If checker cannot confirm a skill output is met → rejection with the specific gap named.

This makes checker reviews skill-aware rather than generic test-gate checks.
```

---

### 9E — SHARED SKILL OWNERSHIP (roles that share skill files)

The skill frontmatter has `owners: [backend_lead, senior_engineer_be]` already.
This means multiple roles can legitimately use the same skill file.

**Rule:** When resolving skill paths (9B Step 2), check the `owners` field of matching skills.
A skill file is valid for a role if that role appears in its `owners` list.

```
SHARED SKILL RESOLUTION ORDER:
  1. kiro/skills/<assigned_role>/<skill_id>.md          ← role-specific copy (preferred)
  2. kiro/skills/<any_owner_in_owners_field>/<skill_id>.md  ← any owning role's copy
  3. Log which path was used in the skill activation summary

This means:
  - senior_engineer_be can use backend_lead skills (both are in owners)
  - security_engineer skills can be shared with architect where both are owners
  - qa_engineer skills can be used by senior_engineer for TDD-related tasks
```

---

### 9F — SKILL GAP DETECTION (what to do when no skill covers the task)

**Rule:** If a story's subtask has no skill labels, or labels don't resolve to files,
do not fall back to "read all files." Instead:

```
SKILL GAP PROTOCOL:
  1. Log: "[SKILL GAP: story=X, task=Y, labels=[Z] — no matching skill file found]"
  2. Check if skill-selection-matrix.md has an entry for the current activity + role
     If yes → use those files as the skill load (one-time fallback to matrix)
  3. If matrix has no entry → role activates with SKILL.md inventory only (no deep files)
  4. Loop spec CRITERIA fall back to baseline only (test pass + lint + type + OWASP)
  5. Flag in sprint retro: "Story X had no skill coverage — create skill file for [topic]"

SKILL GAP IS NOT A BLOCKER. It slows quality but does not halt the sprint.
The gap is tracked and becomes a backlog item for new skill file creation.
```

---

### FIX 9 — ADJUSTMENTS TO PRIOR FIXES

**Fix 7 amendment (Loop Engine):**
Loop spec CRITERIA section is no longer written from scratch. It is derived from skill outputs
per Fix 9C. Add to the loop spec format: "CRITERIA: auto-populated from skill activation (Fix 9C).
Do not write criteria manually unless skill gap protocol (Fix 9F) is active."

**Fix 8B amendment (Iteration Pruning):**
Skill activation summary (9B Step 4) is NEVER pruned between iterations — it is session-persistent
context. It is small (< 50 tokens) and is the anchor for both maker and checker. Add to Fix 8B
KEEP list: "Skill activation summary from Fix 9B Step 4."

**Fix 8D amendment (Per-Role Budget):**
Skill file reads (max 3 per role activation per Fix 9B Step 3) are now the primary use of the
per-role read budget. After skill load, the remaining budget is:
  senior_engineer_be/fe: 2 reads (budget 2 — skill load uses all of it; use map/imports for rest)
  backend_lead / frontend_lead: 3 reads (1 remaining after skills)
  architect / security_engineer: 3 reads (0 remaining after skills if 3 files loaded)
  → If architect or security_engineer needs > 3 skill files, spawn a subagent per Fix 8F.

**Fix 8G amendment (Skill Matrix Inlining):**
Fix 8G said "inline the matrix into each SKILL.md." Fix 9B supersedes this partially:
skill selection is now driven by $TRACKER labels, not matrix lookups. The Quick-Load Matrix
in SKILL.md (Fix 8G) is still useful as a fallback (Fix 9F) and for Mode 2 single-agent
invocations where no tracker exists. Keep the Fix 8G migration plan but lower its priority —
Fix 9's label-driven approach is the primary path.

---

## FIX 10 — REMAINING EXECUTION GAPS (closes the loop completely)

**Depends on:** All prior fixes (1–9) must be applied first per APPLICATION SEQUENCE.
**Problem:** Four silent failure modes remain that break the sprint loop in production:
  10A — Code written during a loop iteration has nowhere to persist between iterations
  10B — Nobody is assigned to write loop specs before GATE 2
  10C — Parallel story execution in a sprint is unaddressed (sequential is too slow)
  10D — Feature branch lifecycle is implicit — branch creation, CI monitoring, PR timing undefined

---

### 10A — CODE PERSISTENCE BETWEEN LOOP ITERATIONS

**Problem:** Fix 7's DO step produces code. Fix 8B's iteration prune discards raw DO output.
If code only lives in context, the prune destroys it. The next iteration starts from nothing.
This is the most critical gap — it silently breaks every loop in practice.

**Rule:** Every DO step MUST write changed files to disk before the Fix 8B prune runs.
Disk = the story's feature branch working tree (established by Fix 10D).

```
DO STEP — MANDATORY SEQUENCE (replaces current implicit "produce code"):

  1. WRITE TO DISK
     For every file changed in this iteration:
       Write the complete current file state to the feature branch working tree.
       Use the Edit/Write tool (not just in-context changes).
       Confirm write succeeded before proceeding.
     
  2. STAGE CHANGES (do NOT commit yet — commit only after GATE 3)
     git add <changed files only>
     Verify: git diff --staged shows ONLY the intended changes.
     If unintended files appear in diff → unstage them. Do not proceed until clean.

  3. RUN VERIFIER
     Run the loop spec VERIFIER commands against the staged working tree.
     Score each criterion. Build the VERIFY block.

  4. PRUNE CONTEXT (Fix 8B)
     Now discard raw DO output from context.
     KEEP: the VERIFY scores table row + "current file state" = last git-staged version.
     The staged working tree is the source of truth — not what's in context.

  5. DECIDE
     ITERATING → go to next PLAN, which reads from the staged working tree.
     FINAL → hand off to checker. Checker reads the staged diff, not the context.

CRITICAL: "current file state" in Fix 8B KEEP list means the git-staged working tree,
not an in-context copy. After the prune, the agent must re-read from disk at the
start of the next DO step if it needs the file content. This counts as a read
toward Fix 8D per-role budget (1 read per iteration for the file being edited).
```

---

### 10B — LOOP SPEC AUTHORSHIP

**Problem:** Fix 7 requires a loop spec per story at GATE 2. Fix 9C says criteria come from
skill outputs. But no role is assigned to write the spec. It defaults to the orchestrator
producing generic specs, defeating Fix 9C's skill-grounded criteria.

**Rule:** Loop spec authorship is assigned by domain. It is a DESIGN phase artifact, not a
DEVELOP phase artifact. The lead role writes the spec for their domain stories.

```
LOOP SPEC AUTHORSHIP ASSIGNMENT:

  backend_lead     → writes loop specs for all backend stories
  frontend_lead    → writes loop specs for all frontend stories
  ml_engineer      → writes loop specs for all ML/model stories
  devops_engineer  → writes loop specs for all CI/CD/infrastructure stories
  security_engineer → writes loop specs for auth, compliance, and secrets stories

WHEN: written during DESIGN phase, after the story is fully written by product_manager,
      before SM-GATE runs the pre-build checklist.

HOW (using Fix 9C skill-output derivation):
  1. Lead role reads the story's acceptance criteria (from product_manager artifact)
  2. Lead role reads its domain skill files (via Fix 9's Quick-Load Matrix or labels)
  3. Derives CRITERIA from skill outputs (Fix 9C protocol)
  4. Writes VERIFIER commands it knows will work for its domain (lead knows the test suite)
  5. Attaches loop spec to the story in $TRACKER as a comment:
       $TRACKER.addComment(story_id, "LOOP SPEC:\n" + <formatted loop spec>)

SM-GATE CHECKLIST ADDITION (Fix 2 SM-GATE mode — add this item):
  - [ ] Every story has a loop spec attached (authored by the appropriate lead role)
  - [ ] Loop spec VERIFIER commands are runnable non-interactively
  - [ ] Loop spec CRITERIA reference skill outputs (not generic "tests pass")
  If any story is missing its loop spec → SM-GATE returns RED. Named role is responsible.

LOOP SPEC QUALITY BAR (SM-GATE enforces):
  REJECT if: GOAL is feature-shaped ("implement caching") not outcome-shaped ("p95 < 50ms for cached reads")
  REJECT if: VERIFIER is "manually check" or "review the code"
  REJECT if: CRITERIA are identical to another story's criteria (copy-paste = not domain-specific)
```

---

### 10C — SPRINT PARALLELISM PROTOCOL

**Problem:** A sprint with 10 stories running sequentially with up to 8 iterations each =
80 loop passes. Impractical. But parallel subagents break Fix 8D's per-role budget counter
(each subagent thinks it's at PEAK independently).

**Rule:** Stories run in parallel lanes, max 3 per lane, with isolated budget counters
and an explicit orchestrator merge step.

```
PARALLELISM MODEL:

LANE LIMIT: max 3 stories execute in parallel per sprint batch.
  - Orchestrator assigns stories to lanes based on domain isolation (no lane touches same files)
  - If stories share a file → they go into the SAME lane (sequential within that lane)
  - Lane assignment logged in sprint plan: "Lane 1: US-001, US-005 | Lane 2: US-002 | Lane 3: US-003, US-007"

PER-LANE ISOLATION:
  Each lane = one subagent with its own degradation counter (Fix 8D).
  Lane subagent starts at PEAK regardless of other lanes' state.
  Lane subagent reports its final tier to the orchestrator at lane completion.
  Orchestrator session tier = MAX(all lane tiers). If any lane hits CRITICAL → announce to user.

ORCHESTRATOR DURING PARALLEL EXECUTION:
  Orchestrator holds: lane assignments + story summaries (300-token cap per story, Fix 8F).
  Orchestrator does NOT load lane subagent contexts. Summaries only.
  Orchestrator applies Fix 8E mid-session rot check every 10 orchestrator tool calls
  (lane subagent tool calls do NOT count toward orchestrator's counter).

FILE CONFLICT DETECTION (before lane assignment):
  Before launching parallel lanes, orchestrator checks:
  "Do any two stories in this batch modify the same file?"
  Method: read the story's subtask descriptions for file paths.
  If conflict found → merge those stories into one lane (sequential within lane).
  If conflict unknown → default to sequential for safety.

MERGE STEP (after all lanes in a batch complete):
  1. Orchestrator receives summary from each lane (pass/fail, files changed, checker verdict)
  2. git merge --no-ff each lane's branch into the sprint integration branch
     If merge conflict → route to backend_lead or frontend_lead (whichever owns the file)
     Conflict resolution = a new single-iteration loop on the conflicting file only
  3. Run full test suite on integration branch (qa_engineer checker — one pass, not a loop)
  4. If integration tests pass → proceed to next batch of 3 stories
  5. If fail → identify which lane caused the regression, re-open that story (SM-UNBLOCK)

BATCH SIZE TUNING:
  Sprint start: begin with 2 parallel stories (conservative). 
  If first batch completes with no merge conflicts → increase to 3.
  If merge conflicts occur in > 30% of batches → reduce to 1 (sequential sprint).
  SM-RETRO reports: "Parallelism: N lanes, M merge conflicts, recommendation: [increase/hold/reduce]"
```

---

### 10D — FEATURE BRANCH LIFECYCLE

**Problem:** team-orchestrator.md mentions feature branches for commits but never specifies
when branches are created, when PRs are opened, who monitors CI, or how the checker accesses
the diff. These are implicit assumptions that break silently.
Additionally: git push and PR steps assume a remote exists — no local-only fallback was defined.

**Rule:** Explicit four-stage lifecycle from story assignment to merge, with DETECT_REMOTE
selecting REMOTE_MODE or LOCAL_MODE at session start.

```
─────────────────────────────────────────────────
DETECT_REMOTE PROTOCOL (runs once at session start, same agent call as DETECT_TRACKER)
─────────────────────────────────────────────────
Run: git remote -v

CASE A — remote(s) listed → set GIT_MODE=REMOTE
  Record: REMOTE_URL=<origin fetch url>
  Proceed with REMOTE_MODE lifecycle below.

CASE B — no remotes listed → set GIT_MODE=LOCAL
  Log: "[GIT_MODE=LOCAL] No remote configured. All git operations are local.
        PR creation skipped. CI substituted with local test run. Merge to main is local --no-ff."
  Proceed with LOCAL_MODE lifecycle below.

CASE C — remote listed but push fails (detected on first push attempt) → downgrade to LOCAL
  Log: "[GIT_MODE=LOCAL] Remote unreachable. Downgrading to local-only mode."
  Continue as LOCAL_MODE for the rest of the session. SM-UNBLOCK notified.

Rule: GIT_MODE is set ONCE per session. Never re-detect mid-sprint.
─────────────────────────────────────────────────

STAGE 1 — BRANCH CREATION (at story assignment, before loop starts)
  Trigger: orchestrator assigns story to senior_engineer via $TRACKER

  REMOTE_MODE:
    git checkout main && git pull origin main
    git checkout -b feature/<tracker-id>-<slug>
    git push --set-upstream origin feature/<tracker-id>-<slug>

  LOCAL_MODE:
    git checkout main
    git checkout -b feature/<tracker-id>-<slug>
    (no push — branch exists locally only)

  Both modes: Log in $TRACKER: "Branch created: feature/<tracker-id>-<slug> [GIT_MODE=<mode>]"
  This branch is the DO step destination (Fix 10A). All loop iterations write here.

STAGE 2 — LOOP EXECUTION (Fix 7 + Fix 10A run on this branch)
  Each DO step: write files → git add → run verifier → score → prune context (Fix 8B)
  Intermediate DO steps do NOT commit. Staged changes accumulate on the branch.
  Branch state after N iterations = best working state, staged but uncommitted.
  $TRACKER loop-state comments reference the branch name so checker can locate the diff.
  GIT_MODE has no effect on Stage 2 — loop runs identically in both modes.

STAGE 3 — CHECKER REVIEW + COMMIT (after maker writes FINAL — Fix 7)
  Maker writes FINAL → triggers handoff to qa_engineer (checker)
  
  CHECKER RECEIVES (Fix 9D handoff package):
    - git diff main..feature/<tracker-id>-<slug>   ← the full staged diff (both modes)
    - Story AC + loop spec + skill activation summary
    - Maker's final VERIFY scores table
  
  CHECKER RUNS:
    - Independent verifier (same commands, fresh context)
    - Skill output confirmation (Fix 9D)
    - Security gate S2 (Fix 8, Part 8C of security discipline)
  
  IF CHECKER APPROVES → COMMIT:
    git commit -m "<type>(<scope>): <what> [<tracker-id>]
    
    ## What / Why / How / Tests / Jira
    <full commit format from team-orchestrator.md>"

    REMOTE_MODE only: git push origin feature/<tracker-id>-<slug>
    LOCAL_MODE: commit is local — no push. SHA recorded in $TRACKER comment.

    $TRACKER.transitionIssue(story_id, "Done")
    $TRACKER.addComment(story_id, "Committed: <commit SHA> | Branch: feature/<tracker-id>-<slug> | GIT_MODE=<mode>")
  
  IF CHECKER REJECTS → return to maker, iteration counter continues (does NOT reset)

STAGE 4 — PR + CI + MERGE

  ── REMOTE_MODE ──────────────────────────────
  PR CREATION (devops_engineer or automated hook):
    Open PR: title = "<tracker-id>: <story summary>" (≤ 70 chars)
    PR description = commit body (verbatim copy)
    Assign reviewers: backend_lead or frontend_lead (domain owner)
    Link to $TRACKER story
  
  CI MONITORING:
    devops_engineer monitors CI pipeline on the PR branch.
    CI must run: unit tests + integration tests + lint + type check + security scan
    If CI fails → devops_engineer logs failure, routes back to senior_engineer (NOT a full loop
    reset — max 2 iterations, then SM-UNBLOCK if still failing)
  
  MERGE:
    Only after: CI green + lead role review approved + no open blocking comments
    git checkout main && git merge --no-ff feature/<tracker-id>-<slug>
    git push origin main
    git push origin --delete feature/<tracker-id>-<slug>   ← remote branch cleanup
    git branch -d feature/<tracker-id>-<slug>              ← local branch cleanup
    Log in $TRACKER: "Merged: PR #N | SHA: <merge-commit>"

  ── LOCAL_MODE ───────────────────────────────
  PR CREATION: SKIPPED (no remote). Substitute: lead role reviews git diff locally.
    devops_engineer runs: git diff main..feature/<tracker-id>-<slug> > /docs/reviews/<tracker-id>-diff.txt
    backend_lead or frontend_lead reads diff file and logs approval in $TRACKER comment.

  CI SUBSTITUTION (devops_engineer):
    Run locally: unit tests + integration tests + lint + type check
    Security scan: run available local tools (e.g., bandit, eslint-plugin-security)
    Log results in $TRACKER: "LOCAL CI: tests=pass | lint=pass | security=<result>"
    If any fail → same routing as remote CI fail (back to senior_engineer, max 2 iter)

  MERGE (local --no-ff, no remote push):
    Only after: local CI pass + lead role diff review logged in $TRACKER
    git checkout main
    git merge --no-ff feature/<tracker-id>-<slug>
    git branch -d feature/<tracker-id>-<slug>   ← local branch cleanup
    Log in $TRACKER: "Merged locally: SHA: <merge-commit> | GIT_MODE=LOCAL"

  NEVER merge (either mode) without: verifier pass + checker approval + lead review.
  These are hard blocks in both GIT_MODE=REMOTE and GIT_MODE=LOCAL.

GIT ↔ $TRACKER PARALLEL TABLE (applies in both modes):
  Every git action fires a $TRACKER action in the same agent step:
  ─────────────────────────────────────────────────────────────────
  git checkout -b <branch>          → $TRACKER.addComment("Branch created: <branch>")
  git add + verifier pass           → $TRACKER loop-state comment (Fix 10A)
  git commit                        → $TRACKER.addComment("Committed: <SHA>")
  git push (REMOTE only)            → $TRACKER.addComment("Pushed: <branch>")
  PR opened (REMOTE only)           → $TRACKER.addComment("PR: <url>")
  CI result (remote or local)       → $TRACKER.addComment("CI: <pass/fail details>")
  git merge --no-ff                 → $TRACKER.transitionIssue("Done") + merge SHA comment
  branch deleted                    → $TRACKER.addComment("Branch cleaned up")
  ─────────────────────────────────────────────────────────────────
  If $TRACKER is also LOCAL (markdown fallback from Fix 1), both systems are fully local.

MID-SPRINT ADR FILING (gap from Fix 5 — closes Fix 6's TW trigger point gap):
  If an ADR is created mid-sprint (from Fix 5 conflict resolution):
    1. File the ADR at /docs/decisions/ADR-NNN.md immediately
    2. Log in $TRACKER: "ADR-NNN filed — see /docs/decisions/ADR-NNN.md"
    3. DO NOT wait for sprint-end TW trigger to update the index
    4. Senior engineer or lead role updates /docs/decisions/index.md inline
    5. TW sprint-end trigger (Fix 7 / team-orchestrator) then only needs to verify the index,
       not write it from scratch
```

---

### FIX 10 — VERIFICATION CHECKLIST

After applying all 10 fixes, verify the complete pipeline is wired by checking:

```
[ ] Fix 1:  $TRACKER detected and locked at GATE 2. All tracker calls use $TRACKER.* not jira.*
[ ] Fix 4:  team-orchestrator.md loads before Mode 1/4 agents fire.
            loop-engine.md loads before DEVELOP phase starts.
[ ] Fix 2:  SM activates in the correct mode (SM-GATE / SM-PLAN / SM-RETRO / SM-UNBLOCK).
            Never more than one mode per agent call.
[ ] Fix 3:  senior_engineer_be loads shared base (5 files) then role overlay (max 2).
            senior_engineer_fe loads shared base (5 files) then role overlay (max 2).
[ ] Fix 5:  Any conflict detected → arbitration tier identified → ADR filed before phase advances.
[ ] Fix 7:  Every story has a loop spec. Maker runs PLAN→DO→VERIFY→DECIDE.
            Checker has fresh context. Only checker transitions story to Done.
[ ] Fix 8:  Hooks fire only at GOOD tier or above (except Hook 03 + context-rot: always).
            Iteration prune runs after every DO step. Per-role budget tracked.
            Mid-session rot check fires every 10 orchestrator tool calls.
[ ] Fix 9:  Skill labels present on every subtask. Skill files resolved and loaded (max 3).
            Skill activation announced before first loop iteration.
            Loop spec CRITERIA derived from skill outputs, not written generically.
[ ] Fix 6:  Mode 5 (lean) activates only when triggered. Lean loop uses 4-iteration cap.
            Builder uses fresh context turn for checker pass. Security gates S2+S3 intact.
[ ] Fix 10: Feature branch created at story assignment (not first commit).
            DO step writes to disk before context prune. Staged, not committed, between iterations.
            Max 3 stories in parallel. File conflict check before lane assignment.
            PR opened after checker approves. CI green before merge. Never --no-verify.
```

---

## FIX HEALTH CHECKS — Confidence Signals Per Fix

After each fix is applied, verify it using the observable signals below.
Every check is binary: PASS or FAIL. No partial credit.
Run the full table after your first sprint completes. Run individual rows when a fix is patched.

---

### HOW TO RUN

For each fix, look at the actual agent output or files produced.
If the signal is present → PASS. If absent or wrong → fix is not active, investigate.

A fix that cannot produce its signal has not been applied — it is just text in a file.

---

### FIX 1 — Tracker Abstraction

| # | Signal to check | Where to look | Pass condition |
|---|----------------|---------------|----------------|
| 1.1 | DETECT_TRACKER ran | Session start log | `[ENV] TRACKER_MODE=<jira|linear|github|markdown>` line present |
| 1.2 | No raw jira.* calls | Any agent output | Zero occurrences of `jira.createProject`, `jira.transitionIssue` etc. — only `$TRACKER.*` |
| 1.3 | Markdown fallback works | `/docs/phase-N/` | If TRACKER_MODE=markdown, sprint-plan.md and loop-state files exist here |

---

### FIX 2 — SM Split

| # | Signal to check | Where to look | Pass condition |
|---|----------------|---------------|----------------|
| 2.1 | SM-GATE produces verdict only | SM-GATE output | Output contains `VERDICT: GREEN` or `VERDICT: RED` + named blockers. No sprint plan in same output. |
| 2.2 | SM-PLAN fires after GREEN only | Session log | SM-PLAN agent call does not appear if SM-GATE returned RED |
| 2.3 | SM-GATE and SM-PLAN are separate calls | Agent call log | Two distinct invocations — not one merged response |
| 2.4 | SM-RETRO contains Loop Engine Report | Sprint-end output | Loop Engine Report section present in retro (Fix 7 metric) |

---

### FIX 3 — Steering Overlays

| # | Signal to check | Where to look | Pass condition |
|---|----------------|---------------|----------------|
| 3.1 | Roles load ≤ 5 base + 1 overlay | Role activation log | No role announces loading more than 6 steering files |
| 3.2 | No role loads team-orchestrator.md | Role context | team-orchestrator.md appears only in orchestrator context, not in role context |
| 3.3 | BE/FE overlays are distinct | Skill activation logs | backend_lead and frontend_lead load different overlay files |

---

### FIX 4 — Session Start Protocol

| # | Signal to check | Where to look | Pass condition |
|---|----------------|---------------|----------------|
| 4.1 | ENV detection log appears | Session start | `[ENV] TRACKER_MODE=X | GIT_MODE=Y` line is first logged output |
| 4.2 | Constitution loaded before first role | Session log | team-orchestrator.md load confirmation appears before any role invocation in Mode 1/4 |
| 4.3 | Loop engine loaded before senior_engineer | DEVELOP phase log | loop-engine.md load confirmation appears before senior_engineer_be or senior_engineer_fe activates |

---

### FIX 5 — Conflict Resolution

| # | Signal to check | Where to look | Pass condition |
|---|----------------|---------------|----------------|
| 5.1 | Conflicts produce ADRs | `/docs/decisions/` | Any mid-sprint architectural conflict produces an ADR-NNN-CONFLICT file immediately |
| 5.2 | Escalation chain is respected | ADR content | ADR shows CTO→Architect→Security→User escalation order; no step skipped |
| 5.3 | No silent resolutions | $TRACKER comments | Every conflict decision has a $TRACKER comment linking to the ADR |

---

### FIX 6 — Lean Mode

| # | Signal to check | Where to look | Pass condition |
|---|----------------|---------------|----------------|
| 6.1 | Mode 5 uses exactly 3 roles | Mode 5 output | Only STRATEGIST, BUILDER, QUALITY appear — no other roles |
| 6.2 | LEAN LOOP clause present | Lean loop spec | Loop spec header reads `LEAN LOOP` not standard loop spec |
| 6.3 | S2 + S3 gates still run | Mode 5 sprint output | Security gates S2 and S3 appear even in lean mode |
| 6.4 | Lean checker is fresh context | Mode 5 agent log | Checker call is a separate invocation, not continuation of BUILDER's context |

---

### FIX 7 — Loop Engineering

| # | Signal to check | Where to look | Pass condition |
|---|----------------|---------------|----------------|
| 7.1 | Every story has a loop spec before DEVELOP | SM-GATE checklist | SM-GATE returns RED if any story missing a loop spec |
| 7.2 | Loop spec has all 4 sections | Any loop spec file | GOAL + VERIFIER + CRITERIA + STOP WHEN all present |
| 7.3 | Maker and checker are separate calls | Agent log | qa_engineer invocation is a fresh call, not a continuation |
| 7.4 | Verifier is automated | Loop iteration log | Verifier = test suite / linter / build / contract test output — not agent opinion |
| 7.5 | Loop Engine Report at sprint end | SM-RETRO output | Report contains: stories looped, avg iterations, cost-per-accepted-change metric |
| 7.6 | Hard stop at 8 iterations | Any loop that stalls | Iteration counter hits 8 → SM-UNBLOCK is called, loop does NOT continue |

---

### FIX 8 — Token / Memory / Context Discipline

| # | Signal to check | Where to look | Pass condition |
|---|----------------|---------------|----------------|
| 8.1 | Degradation tier announced on crossing | Agent output | `[DEGRADING]` or `[CRITICAL]` log line appears when read count crosses threshold |
| 8.2 | PRUNE FORMAT appears after each iteration | Loop iteration log | After each DO step: kept items listed (loop spec + VERIFY row + staged paths), rest discarded |
| 8.3 | Per-role read budget respected | Role output | THINK roles ≤3 reads, DEVELOP roles ≤2 reads per iteration — no silent over-reads |
| 8.4 | Mid-session rot check fires | Every 10 tool calls | `[ROT CHECK]` log line appears at tool call 10, 20, 30 etc. |
| 8.5 | Handoff summaries ≤ 300 tokens | Orchestrator handoff | `[HANDOFF COMPRESSED: role=X, original=~N tokens, compressed=~300 tokens]` log line present |
| 8.6 | Hook complexity gate active | Hook firing log | Hooks with >3 file reads blocked; `[HOOK BLOCKED: complexity]` log if violated |

---

### FIX 9 — Skill Activation Pipeline

| # | Signal to check | Where to look | Pass condition |
|---|----------------|---------------|----------------|
| 9.1 | Skill activation summary logged | Pre-loop output | `[SKILLS ACTIVATED: role=X, skills=[...], outputs=[...]]` appears before loop spec is authored |
| 9.2 | No role reads all skill files | Role activation log | No role loads more than 3 skill files; no `read all .md in skills/` pattern |
| 9.3 | Loop spec CRITERIA derived from skill outputs | Loop spec content | CRITERIA section references specific skill output fields (e.g., `caching_strategies.md → outputs.cache_miss_rate`) |
| 9.4 | Checker receives skill activation summary | Checker handoff | Checker's context package includes `[SKILL ACTIVATION SUMMARY]` section |
| 9.5 | Skill gap protocol fires when no skill matches | Agent log | `[SKILL GAP: role=X, label=Y — no matching skill]` appears; no silent fallback to read-all |

---

### FIX 10 — Execution Gaps

| # | Signal to check | Where to look | Pass condition |
|---|----------------|---------------|----------------|
| 10.1 | GIT_MODE set at session start | ENV log line | `[ENV] ... GIT_MODE=<REMOTE|LOCAL>` present |
| 10.2 | 7-step DO sequence followed | Loop iteration log | Every DO step shows: READ→IDENTIFY→WRITE FIX→WRITE TO DISK→GIT ADD→RUN VERIFIER→SCORE→PRUNE |
| 10.3 | git diff --staged runs before verifier | DO step log | `git diff --staged` output appears before verifier commands in every iteration |
| 10.4 | Branch created at story assignment | $TRACKER comments | Branch creation comment appears at ASSIGN step — not at commit step |
| 10.5 | LOCAL_MODE skips push and substitutes PR | GIT_MODE=LOCAL log | No `git push` in output; `/docs/reviews/<id>-diff.txt` exists; lead review logged in $TRACKER |
| 10.6 | Parallel lanes have isolated counters | Sprint parallelism log | Each lane logs its own read count independently; one lane's CRITICAL does not block others |
| 10.7 | Merge only after all hard blocks cleared | Merge log | Merge step shows: verifier pass + checker approval + lead review + CI pass (or local CI pass) all confirmed before `git merge` |

---

### OVERALL CONFIDENCE SCORE

Run this after completing one full sprint:

```
Fix Health Score = (PASS checks) / (total checks) × 100

Target before first production sprint: ≥ 80%
Target before reassessment (PENDING CLEANUP section): ≥ 90%
Below 70%: stop. Identify failing fixes. Re-apply before continuing.
```

Fixes with any FAIL in a hard-block check (7.6, 8.5, 10.7) must be resolved regardless of overall score.

---

These fixes take precedence over conflicting instructions in:
- `kiro/steering/team-orchestrator.md`
- `kiro/steering/orchestrator-routing.md`
- `kiro/hooks/elite-team-orchestrator.kiro.hook`

When a conflict exists between this file and those files, apply this file's rule and note the override in your response.

Last updated: 2026-06-28

---

## PENDING CLEANUP — DO NOT DELETE YET

These files are superseded by fixes in this CLAUDE.md but are kept until a full system
reassessment is done. At reassessment time: verify no unique content remains, then delete.

### Files to DELETE after reassessment (fully covered by CLAUDE.md):

| File | Superseded by | Reason |
|------|--------------|--------|
| `hooks/01-token-discipline.kiro.hook` | Fix 8D + degradation tiers | Duplicate token budget rules |
| `hooks/02-context-discipline.kiro.hook` | Fix 8B | Duplicate iteration pruning rules |
| `hooks/03-memory-discipline.kiro.hook` | Fix 8 | Duplicate memory/context rules |
| `hooks/04-auto-memory-retrieval.kiro.hook` | Fix 8G + Fix 9B | Covered by Quick-Load Matrix + Skill Activation Protocol |
| `hooks/05-compression-feedback.kiro.hook` | Fix 8F | Covered by 300-token handoff enforcement |
| `hooks/context-rot-detection.kiro.hook` | Fix 8E | Covered by mid-session rot every 10 tool calls |
| `steering/context-memory-discipline.md` | Fix 8 | CLAUDE.md is now canonical for context discipline |
| `steering/memory-management.md` | Fix 8 + Fix 4 | Covered by session start protocol + Fix 8 |

### Files to KEEP but review for stale content at reassessment:

| File | Kept for | What to check |
|------|---------|--------------|
| `hooks/elite-team-orchestrator.kiro.hook` | Pipeline trigger mechanism | Confirm Fix 9A override (no read-all) is respected |
| `hooks/enforce-orchestrator-pipeline.kiro.hook` | Pipeline sequencing | Check for any conflict with CLAUDE.md fixes |
| `steering/orchestrator-routing.md` | Mode detection routing | Confirm Fix 4 env detection preamble is present |
| `steering/team-orchestrator.md` | Constitutional reference, Jira lifecycle, roles | Verify Fix 1/2/3/5/10D patches are not contradicted |
| `steering/skill-selection-matrix.md` | Fix 9B skill path resolution | No changes expected; verify activity→skill mapping is current |
| `steering/phase-reporting.md` | Discipline Report (reads/tier/tokens) | Verify metrics align with Fix 8D budgets |
| `steering/discovery-engine.md` | Mode selection (always-loaded) | No changes expected; verify 7 questions still valid |

### Reassessment trigger:
Run reassessment when ALL of the following are true:
1. At least one full sprint has completed using this CLAUDE.md
2. Loop Engine Reports exist for ≥ 2 stories
3. GIT_MODE and TRACKER_MODE have been exercised at least once each
4. No open SM-UNBLOCK escalations remain

Reassessment owner: CTO + Architect (Fix 5 conflict chain applies if they disagree).

---

## FIX 11 — ROUTING + MATRIX PRECISION FIXES

**Source:** Deep research analysis of `orchestrator-routing.md` and `skill-selection-matrix.md` (2026-06-29).
**Priority:** Apply low-complexity fixes (11A, 11B, 11C, 11D, 11E, 11H) first. Medium-complexity (11F, 11G) after.

---

### 11A — DISCOVERY ENGINE MISSING STOP GUARD (orchestrator-routing.md)

**Problem:** `orchestrator-routing.md` MANDATORY LOADS section (lines 66–84) has STOP guards for `team-orchestrator.md`, `skill-selection-matrix.md`, and `loop-engine.md`. But lines 89–101 reference `discovery-engine.md` as a prerequisite to mode selection without a corresponding STOP guard. If `discovery-engine.md` is absent, the overkill-prevention gate silently disappears and mode selection proceeds ungated.

**Fix:** Add to MANDATORY LOADS block in `orchestrator-routing.md`, immediately after the `loop-engine.md` guard:

```
IF first request of a new build task (BUILD/CREATE/MAKE/DEVELOP/IMPLEMENT + APP/TOOL/SYSTEM/etc.):
  LOAD: kiro/steering/discovery-engine.md
  VERIFY it is in context before the 7 scoping questions run.
  If absent → STOP. "Discovery engine not loaded. Cannot score task complexity without it.
               Load kiro/steering/discovery-engine.md before mode selection."

  Exception: explicit user mode override ("mode N") or bypass keywords ("just build it", "skip questions")
  → In those cases, discovery-engine.md is NOT required (discovery is skipped by user intent).
```

---

### 11B — MODE 2 SKILL SELECTION UNDEFINED (orchestrator-routing.md)

**Problem:** Mode 2 routes to a single role and specifies output format but says nothing about skill selection. A CTO invoked via Mode 2 for "tech strategy" could load 0 skills or 12, depending on LLM interpretation. The matrix applies in all other modes (via Fix 9B) but Mode 2 is silent.

**Fix:** Add to the Mode 2 spec block in `orchestrator-routing.md`, after "No other roles, no phases/sprints, no git unless asked":

```
SKILL SELECTION IN MODE 2:
  skill-selection-matrix.md still applies — Mode 2 is NOT exempt from Fix 9B.
  When the Mode 2 role activates:
    1. Identify the activity from the user's request (e.g., "tech strategy" → "Full strategy" row)
    2. Look up the activity in skill-selection-matrix.md for that role
    3. Load ONLY the listed skill files (max 3)
  If no tracker labels exist (Mode 2 has no $TRACKER stories), use matrix lookup as the primary path.
  Skill activation summary (Fix 9B Step 4) is still required before the role produces its artifact.
```

---

### 11C — NO COVERAGE THRESHOLDS IN TESTING REQUIREMENTS (orchestrator-routing.md)

**Problem:** The testing requirements table specifies frameworks and gate conditions but not minimum coverage numbers. "Unit + integration tests" means different things to different engineers. The discipline report cannot evaluate coverage adequacy.

**Fix:** Add a `Min Coverage` column to the testing requirements table in `orchestrator-routing.md`:

```
| Mode                | Testing Requirement                              | Min Coverage (new code) |
|---------------------|--------------------------------------------------|------------------------|
| Mode 3 (Direct)     | Write + run relevant tests after every build     | No threshold — run and report |
| Mode 4 Lite         | Unit tests for all new functions                 | ≥ 60%                  |
| Mode 4 Standard     | Unit + integration tests                         | ≥ 70%                  |
| Mode 1 (Full)       | Unit + integration + contract + load             | ≥ 80%                  |
| Mode 5 (Lean)       | Unit tests + manual smoke                        | ≥ 60%                  |
```

Add to the Mode 3 Build Report template: `| Coverage | X% (target: report only — no threshold in Mode 3) |`
Add to the Mode 4 Lite Build Report template: `| Coverage target | ≥ 60% for new code |`

---

### 11D — NO PARALLELISM SPEC WITHIN PHASES (orchestrator-routing.md)

**Problem:** The DESIGN phase activates `database_architect`, `cloud_architect`, `finops_architect`, and `security_engineer` sequentially. Their outputs are largely independent — schema design does not depend on VPC topology. Running them sequentially adds latency with no benefit. But the file has no annotation for concurrent activation.

**Fix:** Add a `[PARALLEL]` annotation system to `orchestrator-routing.md`. Add this block under the SELF-CHECK section or as a new PHASE PARALLELISM section:

```
## PHASE PARALLELISM RULES (Mode 1 and Mode 4 only)

Agents annotated [PARALLEL] within the same phase can activate concurrently.
Agents without [PARALLEL] must wait for the previous agent to complete and hand off.
SM-GATE still collects ALL outputs before the phase advances — parallelism is within-phase only.

DESIGN PHASE parallelism:
  database_architect    [PARALLEL with cloud_architect, finops_architect]
  cloud_architect       [PARALLEL with database_architect, finops_architect]
  finops_architect      [PARALLEL with database_architect, cloud_architect]
  security_engineer     SEQUENTIAL — runs after architect, product_manager, and db_architect complete
                        (needs their artifacts to run STRIDE threat model)
  architect             SEQUENTIAL — must complete before database_architect activates
                        (schema depends on service decomposition decisions)
  product_manager       SEQUENTIAL — must complete before architect activates (PRD is input)

DEVELOP PHASE parallelism:
  backend_lead + frontend_lead   [PARALLEL — independent domains, no shared output]
  senior_engineer_be/fe stories  [PARALLEL — per Fix 10C lane model]
  devops_engineer                [PARALLEL with senior engineers — CI/CD setup is independent]
  ml_engineer                    [PARALLEL with frontend_lead if no API dependency yet]

THINK PHASE: sequential (market_researcher → cto — each feeds the next).
LAUNCH PHASE: sequential (data_scientist → website_creator → scrum_master SM-RETRO).
```

---

### 11E — WEBSITE_CREATOR LANDING PAGE VIOLATES MAX-3-FILES RULE (skill-selection-matrix.md)

**Problem:** The `website_creator` landing page row in `skill-selection-matrix.md` lists 4 skill files: `landing_page_patterns.md, landing_page_copy.md, conversion_optimization.md, trust_signals_social_proof.md`. Fix 9 sets a hard cap of 3 per activation. This is the only row in the matrix that violates its own constraint.

**Fix:** Split the landing page row into two activity rows in `skill-selection-matrix.md`:

```
# REPLACE this row:
| Landing page | landing_page_patterns.md, landing_page_copy.md, conversion_optimization.md, trust_signals_social_proof.md | others |

# WITH these two rows:
| Landing page (structure + conversion) | landing_page_patterns.md, conversion_optimization.md, trust_signals_social_proof.md | others |
| Landing page (copy + messaging)       | landing_page_copy.md, conversion_optimization.md, trust_signals_social_proof.md      | others |
```

Rule: if both copy and structure are needed in the same activation, load `landing_page_patterns.md, landing_page_copy.md, conversion_optimization.md` (drop `trust_signals_social_proof.md` — it's a second-pass file).

---

### 11F — SKILL FILE EXISTENCE CHECK MISSING (skill-selection-matrix.md)

**Problem:** The SKILL LOADING PROTOCOL says "load these skill files" but does not verify they exist first. Three agents added to the matrix (data_engineer, mobile_engineer, data_scientist) reference skill files that were never created (e.g., `ios_swiftui_architecture.md`, `stream_processing_kafka.md`, `cohort_retention_analysis.md`). The matrix rows exist but the files don't — this fails silently.

**Fix:** Add Step 0 to the SKILL LOADING PROTOCOL in `skill-selection-matrix.md`, before Step 1:

```
BEFORE activating any role:
0. VERIFY SKILL FILES EXIST
   For each skill file listed in the matrix row for this activity:
     Check that the file exists at kiro/skills/<role>/<filename>.md
     If the file exists → proceed to load it (Steps 1–6 as normal)
     If the file is MISSING:
       Log: "[SKILL MISSING: kiro/skills/<role>/<filename>.md — file not found]"
       Fall back to the role's top-level SKILL.md description for context
       Add to sprint backlog: "Create skill file: kiro/skills/<role>/<filename>.md"
     Do NOT halt execution — continue with available files.
     Do NOT silently substitute an unrelated skill file.
```

**Known missing skill files (as of 2026-06-29) — backlog items:**

data_engineer: `stream_processing_kafka.md`, `batch_pipeline_spark.md`, `dbt_transformation_patterns.md`, `airflow_dag_design.md`, `data_pipeline_testing.md`, `cdc_change_data_capture.md`, `data_quality_great_expectations.md`

mobile_engineer: `ios_swiftui_architecture.md`, `android_jetpack_compose.md`, `react_native_patterns.md`, `mobile_offline_sync.md`, `push_notifications_deep_links.md`, `mobile_performance_profiling.md`, `app_store_deployment.md`

data_scientist: `exploratory_data_analysis.md`, `ab_test_statistical_analysis.md`, `cohort_retention_analysis.md`, `funnel_analysis.md`, `feature_engineering.md`, `data_storytelling_visualization.md`

---

### 11G — SECOND-PASS TRIGGER CONDITION UNDEFINED (skill-selection-matrix.md)

**Problem:** Usage Rule 2 in `skill-selection-matrix.md` states "Second-pass files loaded on-demand only." But "on-demand" is not defined. Does the user trigger it? The verifier score? The orchestrator? If a first-pass artifact scores 5/10 by the loop verifier, should the market_researcher automatically load `pricing_van_westendorp.md` and try again?

**Fix:** Add to USAGE RULES in `skill-selection-matrix.md`, replacing the current Rule 2:

```
2. **Second-pass files trigger when ANY of these conditions are met:**
   a) Loop verifier scores the first-pass artifact < 7/10 on any criterion linked to that skill
   b) User explicitly requests deeper analysis ("can you go deeper on X", "what about Y angle")
   c) The orchestrator identifies a named gap in the artifact that maps to a specific second-pass file
      (e.g., "pricing strategy is missing" → load pricing_van_westendorp.md)
   d) SM-GATE returns RED on a specific criterion that a second-pass file would address

   Second-pass files are NOT loaded pre-emptively "just in case."
   Loading a second-pass file counts toward the role's per-activation budget (Fix 8D).
   Max files after second pass: still ≤ 5 (first-pass 3 + second-pass 2 maximum).
```

---

### 11H — AMBIGUOUS ACTIVITY MATCHING NO TIE-BREAKING RULE (skill-selection-matrix.md)

**Problem:** The SKILL LOADING PROTOCOL requires identifying the ACTIVITY from the task description to look up a matrix row. But a task like "Build a GraphQL subscription system" could match `backend_lead > GraphQL API` (loads `graphql_api_design.md`) OR `backend_lead > Real-time / WebSocket` (loads `websocket_realtime_patterns.md`) — both are plausible. There is no tie-breaking rule.

**Fix:** Add to USAGE RULES in `skill-selection-matrix.md`, after Rule 4:

```
4b. **Ambiguous activity tie-breaking:**
    If a task description matches 2+ activity rows for the same role:
      Step 1: Load the union of all matched rows' skill files
      Step 2: Deduplicate (same file listed in two rows = load once)
      Step 3: If union exceeds 3 files, rank by keyword overlap density:
              count matching keywords between the task description and each file's `when_to_use` field
              load the top 3 by count
      Step 4: Log: "[ACTIVITY MATCH: ambiguous — matched rows [X, Y], loaded [file1, file2, file3]]"

    Example: "Build a GraphQL subscription system"
      Matches: "GraphQL API" (graphql_api_design.md) + "Real-time / WebSocket" (websocket_realtime_patterns.md)
      Union: graphql_api_design.md + websocket_realtime_patterns.md = 2 files (under limit)
      Load both. No tie-breaking needed (union ≤ 3).

    Example where tie-breaking is needed:
      "Implement async GraphQL mutations with Redis queue fallback"
      Matches: "GraphQL API" + "Real-time / WebSocket" + "Background jobs"
      Union: graphql_api_design.md, websocket_realtime_patterns.md, async_job_queue_patterns.md = 3 files
      Load all 3 (exactly at limit — no ranking needed).
```

---

### FIX 11 — HEALTH CHECKS

| # | Signal to check | Where to look | Pass condition |
|---|----------------|---------------|----------------|
| 11A | Discovery engine STOP guard fires | Session log | If `discovery-engine.md` absent on a new build task, `[STOP: Discovery engine not loaded]` appears |
| 11B | Mode 2 roles load skills via matrix | Mode 2 output | `[SKILL ACTIVATION]` log line appears before Mode 2 role produces its artifact |
| 11C | Coverage thresholds in build reports | Build report | Coverage row shows threshold comparison (e.g., "78% / target ≥ 70% ✓") |
| 11D | PARALLEL annotation respected | DESIGN phase log | database_architect and cloud_architect activation timestamps overlap (not sequential) |
| 11E | website_creator landing page ≤ 3 files | Skill activation log | Landing page activation loads ≤ 3 files — never 4 |
| 11F | Missing skill file logged not silently swapped | Role activation log | `[SKILL MISSING: ...]` log line appears for any missing file; no substitution without logging |
| 11G | Second-pass trigger condition explicit | Skill activation log | Second-pass files load only after defined trigger (verifier < 7, user request, named gap, RED gate) |
| 11H | Ambiguous activity match logged | Skill activation log | `[ACTIVITY MATCH: ambiguous — matched rows [...]]` appears when 2+ rows match |

Last updated: 2026-06-30

---
## FIX 12 — STRUCTURAL + CORRECTNESS FIXES

**Source:** Deep review analysis (docs/system-review-2026-06-30.md), 2026-06-30.
**Priority:** High — correctness bugs + token waste on every prompt.

---

### 12A — ADD NEW ROLES TO HOOK DEVELOP + LAUNCH SECTIONS (elite-team-orchestrator.kiro.hook)

**Problem:** data_engineer, mobile_engineer, data_scientist have skill files and matrix rows but are unreachable — the active hook's DEVELOP and LAUNCH sections never activate them.

**Fix:**
- DEVELOP section: add activation trigger for data_engineer (story labels: `data/pipeline`, `data/streaming`, `data/batch`, `data/cdc`) and mobile_engineer (story labels: `mobile/ios`, `mobile/android`, `mobile/rn`)
- LAUNCH section: add data_scientist activation BEFORE website_creator (per Phase Parallelism rules in orchestrator-routing.md: `data_scientist → website_creator → scrum_master SM-RETRO`)
- Follow Fix 9B Skill Activation Protocol for each new role (extract story labels → matrix lookup → max 3 files → log [SKILLS ACTIVATED])

---

### 12B — RESOLVE DISCOVERY vs MODE-SELECTION CONTRADICTION (orchestrator-routing.md lines 97–133)

**Problem:** Lines 97–114 say "Discovery Engine runs FIRST, this file only fires AFTER discovery." Lines 117–133 say "you MUST present mode options to the user BEFORE doing anything else." These are mutually exclusive.

**Fix:** Remove lines 117–133 ("MANDATORY: MODE SELECTION FIRST" section). Replace with a single note:

```
Mode presentation is handled by discovery-engine.md. After discovery scores the task,
it recommends a mode and presents the full mode table as part of its output.
The user confirms or overrides. Only then does orchestrator-routing activate the selected mode.
```

Canonical order (document this explicitly):
1. ENV detection (DETECT_TRACKER + DETECT_REMOTE)
2. Classify: build task vs bug fix vs question
3. Build task + no "mode N" bypass → load discovery-engine.md → 7 questions → score → recommend mode + show table → user confirms
4. Explicit "mode N" → skip discovery, activate directly
5. Bug fix / question / refactor → Mode 3

---

### 12C — INVERT THE HOOK ARCHITECTURE (elite-team-orchestrator.kiro.hook)

**Problem:** The active hook is ~900 lines of constitution that fires on every promptSubmit. It duplicates team-orchestrator.md. Every Mode 3 bug fix, every question, every conversational turn pays the token cost of loading and evaluating this hook before the HOOK COMPLEXITY GATE returns.

**Fix:** Replace the hook prompt with a thin loader (≤60 lines):

```
ORCHESTRATOR ROUTER — run on every prompt:

1. Check for explicit "mode N" → set MODE=N, skip discovery.
2. Classify: if BUILD/CREATE/MAKE/DEVELOP/IMPLEMENT + APP/TOOL/SYSTEM/etc. AND no bypass
   → load discovery-engine.md (STOP if absent), run 7 questions, await user mode confirmation.
3. If bug fix / refactor / question / "skip questions" → MODE=3, return.

After mode confirmed:
- Mode 1, 4, or 5 → LOAD team-orchestrator.md (STOP if absent), LOAD skill-selection-matrix.md (STOP if absent)
- DEVELOP phase start → LOAD loop-engine.md (STOP if absent)
- Delegate ALL role activation, artifact chain, gates, sprint logic to team-orchestrator.md.
  DO NOT replicate constitution content here.

Log [ENV] line. Log [MODE: N selected] line. Then defer to loaded steering files.
```

All role definitions, artifact chains, gates, commit formats, and sprint logic stay in team-orchestrator.md. Hook becomes a router only.

---

### 12D — DEFINE MODE 4 LITE vs STANDARD TRIGGER (orchestrator-routing.md)

**Problem:** Testing table distinguishes Mode 4 Lite (≥60%) from Mode 4 Standard (≥70%) with no definition of what makes a run Lite vs Standard.

**Fix:** Add this trigger definition to the Mode 4 section in orchestrator-routing.md:

```
Mode 4 Lite:     project ≤ 5 user stories OR single sprint planned
Mode 4 Standard: project > 5 user stories OR multi-sprint plan
```

---

### 12E — EXPAND $TRACKER TRANSLATION FOR NON-JIRA MODES (orchestrator-routing.md)

**Problem:** $TRACKER translation table maps only to Jira or markdown. TRACKER_MODE=linear/github/asana will fail at runtime because the mapped API calls don't exist in those tools.

**Fix:** Add per-tracker columns to the translation table:

| $TRACKER verb | jira | linear | github | asana |
|---|---|---|---|---|
| createProject | jira.createProject() | linear.createProject() | gh.createRepo() / Project | asana.createProject() |
| createEpic | jira.createEpic() | linear.createProject() | gh.createMilestone() | asana.createProject() |
| createSprint | jira.createSprint() | linear.createCycle() | gh.createIteration() | asana.createSection() |
| createStory | jira.createStory() | linear.createIssue() | gh.createIssue() | asana.createTask() |
| createSubtask | jira.createSubtask() | linear.createIssue(parentId) | gh.createIssue(linked) | asana.createSubtask() |
| transitionIssue | jira.transitionIssue() | linear.updateIssue(stateId) | gh.updateIssue(state) | asana.updateTask(completed) |
| addComment | jira.addComment() | linear.createComment() | gh.createComment() | asana.createStory() |
| flagIssue | jira.flagIssue() | linear.updateIssue(priority=urgent) | gh.addLabel("blocked") | asana.addTag("blocked") |

---

### 12F — INITIALIZE THE MEMORY SYSTEM

**Problem:** lessons.md, decisions.md, project_map.md don't exist. Memory hooks (03/04/05) are disabled. Zero cross-session context is preserved.

**Fix:** Create the three files and add session-end write instructions:

Files to create:
- `loopEngineering/docs/lessons.md` — use confidence-scored format defined in OPERATING RULES above
- `loopEngineering/docs/decisions.md` — ADR index with temporal validity:
  `| ADR-NNN | title | date | Accepted/Superseded | valid_from → valid_to | one-line decision |`
- `loopEngineering/docs/project_map.md` — module-level map of kiro/ system (dirs, responsibilities, key files)

Session-end write protocol (replaces disabled hooks 03/05):
1. Write checkpoint entry (checkpoint.md)
2. If user corrected LLM this session → append lesson to lessons.md with confidence: low
3. If new ADRs filed → append to decisions.md with valid_from: today, valid_to: present
4. If a prior decision is superseded → update its valid_to field (never delete the row)
5. If new files created or dirs changed → update project_map.md

Implementation options (choose one before executing):
- **Option A (zero infra):** Anthropic Memory Tool (public beta April 2026) — native semantic retrieval, no daemon
- **Option B (full control):** claude-mem (SQLite + ChromaDB + Node.js worker) — offline, team-shareable

---

### 12G — SPLIT CLAUDE.md INTO TWO FILES ✅ DONE

**Status:** DONE — split into CLAUDE.md (this file, ongoing) + CLAUDE-implemented.md (Fixes 1–11 history).
CLAUDE-implemented.md = manual-inclusion only. CLAUDE.md (this file) = always-loaded.

---

### 12H — IMPLEMENT PROMPT CACHING ON STATIC STEERING FILE PREFIXES

**Problem:** The always-loaded steering files (orchestrator-routing.md at 488 lines, context-memory-discipline.md at 97 lines) appear in every prompt but have no `cache_control` markers. Every session pays full input price for these tokens.

**Fix:** When invoking Claude via API, add `cache_control: {"type": "ephemeral"}` breakpoint at the end of the last static content block (after orchestrator-routing.md content loads). Cache reads cost $0.50/M vs $5.00/M = 90% reduction on those tokens.

For the Kiro hook: add a comment marker at the end of the always-loaded section so the API layer knows where the cache breakpoint is. Document in elite-team-orchestrator.kiro.hook that static steering file content should be the first message block (not the user's prompt), enabling prefix caching.

---

### 12I — ADD HARD TOKEN BUDGET VIA SPEND LIMIT ⚠️ MANUAL USER ACTION

**Problem:** Degradation tiers (PEAK/GOOD/DEGRADING/CRITICAL) are instruction-based soft limits. A model in a long reasoning chain will violate soft limits. A production agent that runs uncapped can generate large bills in hours.

**Fix (cannot be implemented in files — requires Anthropic console access):**
1. Go to console.anthropic.com → API keys → select your key → set daily spend limit
   - Development: $10/day
   - Production: $50/day
2. If using LiteLLM proxy: add `max_budget` per key with `budget_reset: daily`
3. Instruction-based tiers remain as behavioral guidance; the console cap is the backstop

**Status:** ⚠️ Awaiting manual action by Gurpreet. Cannot be done programmatically.

---

### 12J — ADD GOAL ANCHOR INJECTION (replaces ROT CHECK)

**Problem:** Current ROT CHECK fires every 10 tool calls and checks for context coherence. Research shows context rot is better detected as **goal drift** — the agent starts re-narrating earlier reasoning instead of advancing toward the original objective.

**Fix:** Replace or augment ROT CHECK in context-memory-discipline.md with:

```
GOAL ANCHOR (inject every 10 tool calls):
  "[GOAL ANCHOR — tool call N]: Original objective: '<exact text of user's first request this session>'.
  All current work must advance this objective directly.
  If the last 3 tool calls did not advance this objective → STOP. Re-read the objective. Re-route."
```

The original objective must be captured at session start (first user message) and stored as `$ORIGINAL_OBJECTIVE`. It is injected verbatim at each anchor point — not paraphrased.

---

### FIX 12 — HEALTH CHECKS

| # | Signal | Pass condition |
|---|--------|---------------|
| 12A | data_scientist activates in LAUNCH | `[SKILLS ACTIVATED: role=data_scientist]` appears before website_creator |
| 12A | mobile_engineer activates when story has mobile label | `[SKILLS ACTIVATED: role=mobile_engineer]` logged |
| 12B | No duplicate mode-selection prompt | Only one mode presentation per session (from discovery output) |
| 12C | Hook prompt length | Hook file < 100 lines; team-orchestrator.md unchanged |
| 12D | Mode 4 Lite/Standard determined at project start | Log line: `[MODE 4: Lite/Standard — N stories]` |
| 12E | Linear/GitHub/Asana tracker calls use correct API | TRACKER_MODE=linear → `linear.createCycle()` not `jira.createSprint()` |
| 12F | Memory files exist | `docs/lessons.md`, `docs/decisions.md`, `docs/project_map.md` present |
| 12G | Split complete | CLAUDE-implemented.md has Fixes 1–11; this file has Fix 12+ only |
| 12H | Prompt caching active | API logs show cache_read_input_tokens > 0 on second+ turns |
| 12I | Hard spend limit set | Anthropic console shows daily cap configured |
| 12J | Goal anchor appearing | `[GOAL ANCHOR — tool call N]` log line every 10 calls |

---

## FIX 13 — CLEANUP + DEDUPLICATION ✅ IMPLEMENTED 2026-06-30

**Source:** Deep review analysis (docs/system-review-2026-06-30.md), 2026-06-30.
**Priority:** Medium — maintainability and cognitive clarity.
**Status:** All 13A–13G complete. See CLAUDE-implemented.md for detail if needed.

---

### 13A — DELETE 7 DEAD HOOKS + 2 .DS_STORE FILES

**Problem:** 7 disabled hooks marked SUPERSEDED remain on disk, adding cognitive load and false confidence that they're doing something.

**Files to delete:**
```
kiro/hooks/01-token-discipline.kiro.hook
kiro/hooks/02-context-discipline.kiro.hook
kiro/hooks/03-memory-discipline.kiro.hook
kiro/hooks/04-auto-memory-retrieval.kiro.hook
kiro/hooks/05-compression-feedback.kiro.hook
kiro/hooks/context-rot-detection.kiro.hook
kiro/hooks/enforce-orchestrator-pipeline.kiro.hook
kiro/.DS_Store
kiro/skills/.DS_Store
```

If any content needs preservation for reference: copy the relevant prompt text to `CLAUDE-implemented.md` before deleting.

---

### 13B — DEDUPLICATE senior_engineer_be / senior_engineer_fe SHARED SKILLS

**Problem:** 8 identical files exist in both `senior_engineer_be/` and `senior_engineer_fe/`. Maintenance drift is inevitable.

**Shared files (currently duplicated):**
- code_review_excellence.md
- concurrency_safety.md
- debugging_methodology.md
- error_handling_strategies.md
- feature_flags_safely.md
- performance_profiling.md
- refactoring_safely.md
- tdd_red_green_refactor.md

**Fix:**
1. Create `kiro/skills/shared/` directory
2. Move the 8 files there
3. Update both `senior_engineer_be/SKILL.md` and `senior_engineer_fe/SKILL.md` to reference `shared/`
4. Update skill-selection-matrix.md rows for both roles to use `shared/<filename>.md` paths
5. Keep role-specific overlays in their own directories:
   - senior_engineer_be keeps: `clean_architecture.md`, `dependency_injection_patterns.md`, `observability_instrumentation.md`
   - senior_engineer_fe keeps: `frontend_observability.md`, `progressive_web_app.md`, `react_performance_patterns.md`

---

### 13C — MAKE context-memory-discipline.md THE SINGLE DISCIPLINE TIER SOURCE

**Problem:** Degradation tier definitions (PEAK/GOOD/DEGRADING/CRITICAL) exist in both `context-memory-discipline.md` (always-loaded) and CLAUDE.md Fix 8 (now in CLAUDE-implemented.md). Two authoritative sources for the same rules.

**Fix:** `context-memory-discipline.md` is canonical. Add a single reference line here:
> Discipline tiers (PEAK/GOOD/DEGRADING/CRITICAL) are defined in `kiro/steering/context-memory-discipline.md`. Do not redefine them elsewhere.

---

### 13D — SPLIT website_creator SKILL DIRECTORY INTO SUBDOMAINS

**Problem:** website_creator has 24 skill files — largest role in the system. Flat directory is hard to navigate.

**Proposed split:**
```
website_creator/
  seo/         ← seo_foundations.md, technical_seo_structured_data.md, internationalization_seo_hreflang.md
  conversion/  ← conversion_optimization.md, conversion_psychology_principles.md, landing_page_patterns.md,
                  landing_page_copy.md, pricing_page_design.md, trust_signals_social_proof.md, forms_lead_capture_ux.md
  content/     ← content_marketing_strategy.md, case_study_customer_stories.md, email_marketing_automation.md,
                  growth_loops_referral_plg.md
  technical/   ← responsive_design_mobile_first.md, image_video_optimization.md, animation_choreography.md,
                  cookie_consent_privacy_ux.md, web_typography_variable_fonts.md, cms_headless_integration.md,
                  analytics_event_tracking_setup.md, ab_testing_experimentation.md, accessibility_wcag_2_2_aa.md
  SKILL.md     ← stays at root
```

Update skill-selection-matrix.md paths accordingly.

---

### 13E — ADD market_researcher RE-INVOCATION PATH

**Problem:** market_researcher only appears in THINK phase. No path exists to re-invoke it mid-build.

**Fix:** Add a Mode 2 trigger in orchestrator-routing.md Mode 2 section:

```
| "market update / competitor update / re-validate assumptions" | Market Researcher (re-invocation) | market-researcher-update doc |
```

Re-invocation market_researcher reads the previous market-researcher artifact and produces a delta, not a full rewrite.

---

### 13F — EVOLVE decisions.md TO TEMPORAL FORMAT (Zep-inspired)

**Problem:** A flat ADR list loses the temporal dimension — when a decision was active, when it was superseded, and what replaced it. This information is critical for understanding why current architecture looks the way it does.

**Fix:** Every row in decisions.md includes validity window:

```
| ADR-NNN | title | date_created | status | valid_from | valid_to | decision |
| ADR-001 | Use PostgreSQL | 2026-01-15 | Accepted | 2026-01-15 | present | Primary store is PostgreSQL |
| ADR-002 | Use Jira | 2026-02-01 | Superseded | 2026-02-01 | 2026-04-10 | Jira for $TRACKER |
| ADR-003 | Use Linear | 2026-04-10 | Accepted | 2026-04-10 | present | Linear replaced Jira |
```

Rules:
- When a decision is superseded: update valid_to on the old row, add a new row — never delete
- Query "what's the current decision on X?" → filter rows where valid_to = "present"
- Query "what was the decision in March?" → filter rows where valid_from ≤ 2026-03-01 ≤ valid_to

---

### 13G — ADD 85% CONTEXT THRESHOLD OFFLOADING

**Problem:** No explicit trigger exists for offloading context when approaching the window limit. Sessions that run long silently degrade because old tool call results stay in context consuming tokens with diminishing value.

**Fix:** Add to context-memory-discipline.md:

```
THRESHOLD TRIGGER: At 85% context window usage:
  1. For each tool call result older than 5 turns:
     Compress to: "[tool_name result: <5-word summary>. Full output: checkpoint.md §N]"
  2. Write the compressed content to checkpoint.md under a new section
  3. Log: [85% THRESHOLD — context offloaded, estimated N tokens recovered]
  4. Continue session with compressed context
```

Signal: if Claude Code reports context usage in session metadata, watch for 85% mark. If no native signal, use tool call count as proxy: at 40+ tool calls, apply offloading.

---

### FIX 13 — HEALTH CHECKS

| # | Signal | Pass condition |
|---|--------|---------------|
| 13A | Dead hooks gone | `kiro/hooks/` contains only `elite-team-orchestrator.kiro.hook` |
| 13B | Shared skills deduped | `kiro/skills/shared/` exists with 8 files; both senior role dirs have 3 role-specific files each |
| 13C | Single tier source | Searching `DEGRADING` returns hits only in `context-memory-discipline.md`, not this file |
| 13D | website_creator organized | 4 subdirs under website_creator/; flat file count at root = 0 (except SKILL.md) |
| 13E | market_researcher re-invocation listed | Mode 2 table has "market update" row |
| 13F | Temporal decisions format | decisions.md has valid_from / valid_to columns; no rows deleted on supersession |
| 13G | Threshold offloading documented | context-memory-discipline.md has 85% THRESHOLD TRIGGER section |

---

## FIX 14 — DESIGN DIRECTION ENFORCEMENT ✅ IMPLEMENTED 2026-06-30

**Source:** UI UX Pro Max repo analysis (obra/ui-ux-pro-max-skill, 97K stars), 2026-06-30.
**Priority:** Medium — quality gap in UI output across website_creator, mobile_engineer, frontend_lead roles.
**Status:** 14A complete — design_system_gate.md created in shared/; prerequisite rows added to matrix for all 3 roles.

---

### 14A — CREATE DESIGN SYSTEM GATE SKILL (kiro/skills/shared/design_system_gate.md)

**Problem:** website_creator, mobile_engineer, and frontend_lead roles produce technically correct UI code with no design direction enforcement. Output defaults to AI-generic aesthetics (Inter/Roboto fonts, purple gradients, symmetric center-aligned layouts, generic card grids). No gate forces design decisions before UI code is written.

**Fix:** Create `kiro/skills/shared/design_system_gate.md` with this content structure:

```yaml
---
id: design_system_gate
version: 1.0.0
owners: [website_creator, mobile_engineer, frontend_lead]
tags: [design, ui, ux, prerequisite]
when_to_use: >
  Before writing ANY UI code. This skill must activate before component creation,
  landing page code, mobile screen code, or any visual implementation begins.
  It is a prerequisite gate, not a reference file.
inputs:
  - project brief or PRD
  - target audience description
  - brand references (if any)
outputs:
  - design_system.md in /docs/ — complete design token decisions before first line of UI code
---
```

**Gate content (what the design_system.md must define before UI code proceeds):**

1. **Typography** — Select a specific font pairing with justification. Banned defaults: Inter, Roboto, Arial, Space Grotesk (overused by AI-generated UIs). Required: at least one non-standard choice with a stated reason.

2. **Color system** — Define 5 roles: primary, secondary, surface, text, accent. No generic purple gradients (#7c3aed or similar). Colors must have a stated rationale tied to the audience or brand.

3. **Spacing scale** — Define the base unit (4px or 8px) and the scale steps (4, 8, 12, 16, 24, 32, 48, 64). All spacing in UI code must reference scale tokens, not hardcoded values.

4. **Layout direction** — State the layout philosophy: asymmetric vs symmetric, grid columns, hero treatment. Asymmetric layouts are strongly preferred for distinctiveness. Avoid: centered text blocks with illustration to the right (AI-generic pattern #1).

5. **Animation intent** — Define whether animations are used and what they communicate (purpose: guide attention / confirm action / indicate loading). No decorative animations without purpose.

6. **Component voice** — One paragraph describing the visual personality. Example: "Confident and technical — sharp corners, high contrast, data-dense. Not friendly-rounded-card-grid energy."

**Anti-patterns to explicitly reject in design_system.md:**
- Generic hero: large headline center, subtitle below, two CTA buttons, stock illustration right
- Purple/blue gradient backgrounds with white text
- Card grids with icons + short descriptions as primary content pattern
- Rounded corners everywhere (border-radius > 12px as default)
- Inter or Roboto as the primary typeface

**Skill activation in matrix:** Add to skill-selection-matrix.md as a prerequisite row for:
- `website_creator` — ALL UI activities: load design_system_gate.md FIRST, before any other skill
- `mobile_engineer` — UI story activities: load before ios_swiftui_architecture.md or android_jetpack_compose.md
- `frontend_lead` — DESIGN phase: load before any component design begins

---

### FIX 14 — HEALTH CHECKS

| # | Signal | Pass condition |
|---|--------|---------------|
| 14A | design_system.md created before UI code | /docs/design_system.md exists before first component file in any UI sprint |
| 14A | No banned fonts in output | grep for "Inter\|Roboto\|Arial\|Space Grotesk" in CSS output returns 0 hits |
| 14A | Design system gate logged | `[SKILLS ACTIVATED: design_system_gate.md]` appears before any UI role produces code |

---

## FIX 15 — DOCUMENTATION + REPORTING GAPS ✅ IMPLEMENTED 2026-06-30

**Source:** Audit of team-orchestrator.md artifact chain vs actual report templates defined, 2026-06-30.
**Problem:** The system references 6 phase-end reports (QA, Security, Mapping, Discipline, Jira, Git) but only defines templates for 2 of them (QA and Security). The other 4 have zero format definition — the LLM improvises a different format every time. Additionally, the DEVELOP phase has no per-sprint implementation decision record, so non-obvious engineering choices are permanently lost.
**Status:** 15A — impl-decisions.md added to DEVELOP artifact chain + SM-GATE checklist item. 15B — 4 missing report templates (DISCIPLINE, JIRA, GIT, MAPPING) added to team-orchestrator.md GATE 5. 15C — Sprint Discipline Card added to SM-RETRO with blocking rule.

---

### 15A — IMPLEMENTATION DECISION LOG (per sprint, owned by implementing role)

**Problem:** Loop spec captures WHAT to build. Retro captures HOW the sprint went. Nothing captures WHY the code is written the way it is. Non-obvious implementation decisions (algorithm choice, library picked, pattern selected over an alternative) disappear into git history with no rationale.

**Fix:** Add `/docs/phase-N/impl-decisions.md` to the DEVELOP artifact chain in `team-orchestrator.md`. The implementing role populates it during the DO step — not at the end of the sprint. Technical writer formats it at RELEASE.

**Template:**

```markdown
# Implementation Decisions — Phase N, Sprint S

## [Story ID] — [Story title]

| Decision | What was chosen | Alternatives rejected | Reason |
|----------|----------------|----------------------|--------|
| State management | Zustand | Redux, Context API | Redux overkill for 3 stores; Context causes re-render cascade |
| Caching layer | Redis | In-memory, Memcached | Redis already in infra; Memcached has no pub/sub for invalidation |

**Non-obvious constraints:** [anything future devs must know to not break this]
```

**Rules:**
- Only decisions that aren't obvious from the code itself go here
- Minimum 1 entry per story where a meaningful architectural choice was made
- Empty table = acceptable only for trivial CRUD stories with no design choices
- SM-GATE pre-build checklist gains a new item: "impl-decisions.md from prior sprint reviewed?"

---

### 15B — DEFINE THE 4 MISSING PHASE-END REPORT TEMPLATES

**Problem:** `team-orchestrator.md` line 479 says "Produce all 6 phase-end reports (QA, Security, Mapping, Discipline, Jira, Git)." QA-REPORT.md and SECURITY-REPORT.md have templates. The other 4 do not. They must be defined here so every run produces a consistent, comparable report.

Add these 4 report definitions to `team-orchestrator.md` in the GATE 5 section, after the existing QA and Security report templates.

---

#### DISCIPLINE-REPORT.md (owned by scrum_master, produced at GATE 5)

```markdown
# Discipline Report — Phase N

## Token / Context Discipline
| Role | Tool calls this phase | Peak tier breaches | Reads > 2-read rule | Skill files loaded (avg per activation) |
|------|-----------------------|--------------------|---------------------|----------------------------------------|
| architect | N | N | N | N |
| [all roles] | | | | |

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

#### JIRA-REPORT.md (owned by scrum_master, produced at GATE 5)

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

#### GIT-REPORT.md (owned by devops_engineer, produced at GATE 5)

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

#### MAPPING-REPORT.md (owned by architect, produced at GATE 5)

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

### 15C — SPRINT-LEVEL DISCIPLINE MINI-REPORT (owned by scrum_master SM-RETRO, every sprint)

**Problem:** Phase-end reports are produced weeks after the sprint they cover. By then, discipline drift has compounded. A sprint-level signal catches problems when they can still be corrected in the next sprint.

**Fix:** SM-RETRO produces a **Sprint Discipline Card** as the first section of every retro doc. It is a 5-row table, not a full report — takes 2 minutes to generate.

**Template (prepend to every SM-RETRO output):**

```markdown
## Sprint N Discipline Card

| Dimension | This sprint | Target | Status |
|-----------|------------|--------|--------|
| Velocity | N / N planned points | ≥80% | 🟢/🟡/🔴 |
| Token discipline | Peak / Good / Degrading / Critical | GOOD+ | 🟢/🟡/🔴 |
| Git hygiene | N direct commits to main, N PRs unreviewed | 0 / 0 | 🟢/🟡/🔴 |
| $TRACKER sync | N stories without tracker entries | 0 | 🟢/🟡/🔴 |
| Test coverage | N% (Δ from sprint start: ±N%) | ≥ mode target | 🟢/🟡/🔴 |

**One sentence summary:** [e.g., "Sprint 2 hit velocity target but token discipline degraded mid-sprint — 3 reads over budget on the auth story."]
**Action for Sprint 3:** [one concrete change]
```

**Rule:** SM-RETRO is blocked from producing the retro doc until the Sprint Discipline Card is filled. It is not optional. The card is the first thing the user sees at sprint end.

---

### FIX 15 — HEALTH CHECKS

| # | Signal | Pass condition |
|---|--------|---------------|
| 15A | impl-decisions.md exists per sprint | `/docs/phase-N/impl-decisions.md` present before GATE 5 runs |
| 15A | SM-GATE checks prior impl-decisions | Pre-build checklist has "impl-decisions.md from prior sprint reviewed?" item |
| 15B | All 4 missing reports have templates | `team-orchestrator.md` has DISCIPLINE, JIRA, GIT, MAPPING report templates in GATE 5 section |
| 15B | Reports use consistent format | Phase N and Phase N+1 reports have identical column structure (no ad-hoc improvisation) |
| 15C | Sprint Discipline Card appears in every retro | First section of every SM-RETRO output is the 5-row discipline card |
| 15C | Card is blocking | SM-RETRO doc is not produced until all 5 card rows are populated |


---

## FIXES 16–19 (appended 2026-06-30)

## FIX 16 — CRITICAL BUGS ✅ IMPLEMENTED 2026-06-30

**Source:** Deep review analysis (docs/system-review-2026-06-30-v2.md), 2026-06-30.
**Priority:** 🔴 Critical — these break report consistency, mode routing, and skill loading before any real project run.

---

### 16A — DELETE DUPLICATE REPORT SECTIONS FROM orchestrator-routing.md

**Problem:** `orchestrator-routing.md` sections E and F define `JIRA-TASK-REPORT.md` and `GIT-TRACKING-REPORT.md` with their own schemas. Fix 15B added `JIRA-REPORT.md` and `GIT-REPORT.md` to `team-orchestrator.md` with different schemas. Two report names, two formats, for the same data. The model will produce inconsistent reports every run.

**Fix:** Delete sections E and F from `orchestrator-routing.md` (lines ~413–476: "PER-PHASE REPORTS: Jira Task Tracking + Git Tracking" section and both sub-templates). Keep only the reference: "Produce all 6 phase-end reports — templates in team-orchestrator.md GATE 5 section." `team-orchestrator.md` Fix 15B templates are canonical.

**Health check:** `orchestrator-routing.md` contains no `JIRA-TASK-REPORT` or `GIT-TRACKING-REPORT` filenames. All 6 report templates live only in `team-orchestrator.md`.

---

### 16B — FIX MODE PRIORITY CONTRADICTION

**Problem:** `orchestrator-routing.md` line 253 states `Mode 1 > Mode 4` in priority. Line 256 states "Mode 4 wins when both match." These are opposite claims. Every "build an app" prompt where a `.kiro/specs/` dir exists is ambiguous.

**Fix:** Replace the contradiction with:
```
Priority: Mode Override > Mode 4 (when .kiro/specs/ dir exists from prior run) > Mode 1 > Mode 2 > Mode 5 > Mode 3

Mode 4 wins over Mode 1 ONLY when .kiro/specs/ directory already exists from a prior spec workflow run.
If .kiro/specs/ is absent: Mode 1 wins.
If user says "mode N" explicitly: that mode wins regardless.
```

**Health check:** Priority table and Mode 4 win-condition rule are consistent. No contradictory statements.

---

### 16C — FIX NESTED CODE BLOCK IN SM-RETRO DEFINITION

**Problem:** Fix 15C added a triple-backtick block inside the SM modes triple-backtick block (lines ~121–147 of `team-orchestrator.md`). Nested triple-backtick blocks break all Markdown parsers — the inner fence closes the outer block prematurely, mangling the SM-PLAN and SM-UNBLOCK definitions that follow.

**Fix:** Move the Sprint Discipline Card template OUT of the SM modes code block. Place it as a standalone section immediately after the SM modes block:

```
### SM-RETRO — SPRINT DISCIPLINE CARD (Fix 15C)

BLOCKING: SM-RETRO does not produce the retro doc until all 5 rows are populated.

| Dimension        | This sprint                            | Target     | Status     |
|------------------|----------------------------------------|------------|------------|
| Velocity         | N / N planned points                   | ≥80%       | 🟢/🟡/🔴 |
| Token discipline | Peak / Good / Degrading / Critical     | GOOD+      | 🟢/🟡/🔴 |
| Git hygiene      | N direct commits to main, N unreviewed | 0 / 0      | 🟢/🟡/🔴 |
| $TRACKER sync    | N stories without tracker entries      | 0          | 🟢/🟡/🔴 |
| Test coverage    | N% (Δ from sprint start: ±N%)          | ≥ mode tgt | 🟢/🟡/🔴 |

One sentence summary: [what happened this sprint in one line]
Action for Sprint N+1: [one concrete change]
```

Then in the SM-RETRO line of the SM modes code block, simply reference: `Produces: Sprint Discipline Card (see section below — blocking) + retro doc + ...`

**Health check:** SM modes code block contains no nested triple-backtick fences. Sprint Discipline Card renders as a visible Markdown table outside the code block.

---

### 16D — FIX STEP 0 PATH RESOLUTION FOR shared/ FILES

**Problem:** `skill-selection-matrix.md` Step 0 says: `"confirm it exists at kiro/skills/<role>/<filename>.md"`. But shared/ skills are referenced as `shared/design_system_gate.md` in the matrix. For role=website_creator, this expands to `kiro/skills/website_creator/shared/design_system_gate.md` — which does not exist. Actual path: `kiro/skills/shared/design_system_gate.md`. Existence check silently fails for all shared/ prerequisite loads.

**Fix:** Update SKILL LOADING PROTOCOL Step 0:
```
0. VERIFY SKILL FILES EXIST:
   - If filename starts with "shared/" → resolve as: kiro/skills/shared/<filename after "shared/">
   - Otherwise → resolve as: kiro/skills/<role>/<filename>
   Confirm file exists at resolved path. If missing:
     log: "[SKILL MISSING: <resolved path> — file not found]"
     fall back to role's top-level SKILL.md for context
     add to sprint backlog: "Create skill file: <resolved path>"
   Do NOT halt execution. Do NOT silently substitute an unrelated file.
```

**Health check:** `[SKILLS ACTIVATED: shared/design_system_gate.md]` log line appears with resolved path `kiro/skills/shared/design_system_gate.md`. No 404 on shared/ file lookups.

---

### 16E — MOVE SELF-CHECK + PHASE PARALLELISM RULES OUT OF orchestrator-routing.md

**Problem:** `orchestrator-routing.md` (always-loaded, 477 lines) contains two sections that are pipeline constitution content, not routing logic:
- `SELF-CHECK` (Mode 1 checklist, ~15 lines) — belongs in team-orchestrator.md
- `PHASE PARALLELISM RULES` (~40 lines) — belongs in team-orchestrator.md

These inflate the always-loaded file and are never needed unless a Mode 1/4 build is running — which is when team-orchestrator.md is already loaded.

**Fix:** Cut both sections from `orchestrator-routing.md`. Paste into `team-orchestrator.md` after the PHASE GATES section. Add a pointer in orchestrator-routing.md: `"Mode 1 SELF-CHECK and PHASE PARALLELISM RULES — see team-orchestrator.md."`

**Health check:** `orchestrator-routing.md` is ≤ 380 lines (GREEN ROT threshold). SELF-CHECK and PHASE PARALLELISM searchable in `team-orchestrator.md`.

---

#

## FIX 16 — HEALTH CHECKS

| # | Signal | Pass condition |
|---|--------|----------------|
| 16A | No duplicate report schemas | `orchestrator-routing.md` has no JIRA-TASK-REPORT or GIT-TRACKING-REPORT template |
| 16B | Priority table consistent | No contradictory "wins" statements for Mode 1 vs Mode 4 |
| 16C | SM-RETRO code block clean | No nested triple-backtick in SM modes block; Discipline Card renders as Markdown table |
| 16D | shared/ path resolution works | `[SKILLS ACTIVATED: shared/design_system_gate.md]` resolves to correct kiro/skills/shared/ path |
| 16E | orchestrator-routing.md ≤ 380 lines | ROT check returns GREEN |

---

## FIX 17 — MEDIUM IMPROVEMENTS ✅ IMPLEMENTED 2026-06-30

**Source:** Deep review analysis (docs/system-review-2026-06-30-v2.md), 2026-06-30.
**Priority:** 🟠 High-medium — system works without these but discipline gaps compound over time.

---

### 17A — ADD HOOK COMPLEXITY GATE (Step 0) BACK TO HOOK

**Problem:** The hook fires on every promptSubmit including "thanks", "what time is it?", and pure conversational turns. For Mode 3 (bug fix / question), the hook adds ~110 lines of routing overhead before passing through. Fix 8 added a HOOK COMPLEXITY GATE but it was removed during the v3 thin-router rewrite.

**Fix:** Add Step 0 to `elite-team-orchestrator.kiro.hook` before the ENV detection:
```
STEP 0 — COMPLEXITY GATE
IF prompt is ≤ 8 words AND contains none of:
  BUILD / CREATE / MAKE / DEVELOP / IMPLEMENT / DEPLOY / DESIGN / PLAN / ARCHITECT / SPRINT / PHASE
→ Skip all steps. Respond directly. No routing overhead.

IF an [ENV] log line already exists in this session AND [MODE: N selected] already logged:
→ Skip Steps 1–3. Active mode is known. Jump to Step 4 for current mode continuation.
```

**Health check:** Conversational replies ("thanks", "what does X mean?") show no `[ENV]` or `[MODE]` log lines. Mode continuation skips discovery re-run.

---

### 17B — ADD THREE MISSING ROLES TO MODE 2 TRIGGER TABLE

**Problem:** Mode 2 table in `orchestrator-routing.md` has 13 role rows. data_engineer, mobile_engineer, data_scientist are absent. "Design me a Kafka pipeline" has no Mode 2 match and will trigger the wrong role.

**Fix:** Add to the Mode 2 trigger table in `orchestrator-routing.md`:
```
| "pipeline / streaming / Kafka / Spark / dbt / batch / CDC / data engineering" | Data Engineer | pipeline-design doc |
| "mobile / iOS / Android / React Native / offline sync / push notifications" | Mobile Engineer | mobile-design doc |
| "funnel analysis / cohort / A/B test / EDA / retention / data storytelling" | Data Scientist | analysis doc |
```

**Health check:** "Design a Kafka streaming pipeline" in Mode 2 triggers `[SKILLS ACTIVATED: role=data_engineer]`.

---

### 17C — ADD SKILL FILE SUMMARIZATION RULE TO context-memory-discipline.md

**Problem:** `skill-selection-matrix.md` Step 6 says "summarize skill file to 5-line takeaway after extraction — do not keep full content in context." This rule only appears in the matrix (manual-inclusion). In Mode 3 or early Mode 2 sessions where the matrix hasn't loaded yet, the rule is invisible. A 200-line skill file left in context costs ~500 tokens every subsequent turn.

**Fix:** Add to `context-memory-discipline.md` Section 4 (SELF-ADAPTIVE CONTEXT PRUNING):
```
SKILL FILES: After extracting principles from a skill file, compress to 5-line takeaway.
             Do NOT hold the full file while producing the artifact.
             Pattern: Extract → Produce artifact → Discard full content, keep summary only.
             Full skill file content in context after artifact production = context rot.
```

**Health check:** After a role produces its artifact, context does not contain the full text of the skill files loaded for that activation.

---

### 17D — CREATE kiro/skills/shared/SKILL.md INDEX

**Problem:** Every role directory has a SKILL.md. shared/ has none. Step 0's fallback ("fall back to role's top-level SKILL.md") silently fails for shared/ files because there's no SKILL.md to fall back to.

**Fix:** Create `kiro/skills/shared/SKILL.md`:
```markdown
---
name: Shared Skills
description: Cross-role skill files used by senior_engineer_be, senior_engineer_fe, website_creator, mobile_engineer, and frontend_lead.
path_convention: Load as kiro/skills/shared/<filename>.md (NOT relative to role directory)
---

# Shared Skills

## Files
- code_review_excellence.md — code review standards, review checklist, feedback patterns
- concurrency_safety.md — thread safety, race conditions, lock patterns
- debugging_methodology.md — systematic debugging, root cause analysis
- error_handling_strategies.md — error propagation, retry logic, graceful degradation
- feature_flags_safely.md — flag lifecycle, kill switches, gradual rollout
- performance_profiling.md — profiling tools, bottleneck identification, optimization
- refactoring_safely.md — safe refactoring patterns, test coverage before refactor
- tdd_red_green_refactor.md — TDD discipline, test-first, red/green/refactor cycle
- design_system_gate.md — prerequisite gate for all UI roles before any UI code

## Usage
These files are referenced in skill-selection-matrix.md as `shared/<filename>.md`.
Step 0 path resolution: `kiro/skills/shared/<filename>` (not role-relative).
```

**Health check:** `kiro/skills/shared/SKILL.md` exists. Step 0 fallback for shared/ files resolves to it.

---

### 17E — ADD impl-decisions.md TRIGGER TO SKILL MATRIX

**Problem:** Fix 15A added `impl-decisions.md` to the DEVELOP artifact chain in team-orchestrator.md. But skill-selection-matrix.md has no row telling senior_engineer_be/fe when and how to write an entry. The implementing role sees the chain diagram but has no matrix trigger to remember the log.

**Fix:** Add to both `senior_engineer_be` and `senior_engineer_fe` sections in `skill-selection-matrix.md`:
```
| Implementing any non-trivial story (algorithm choice, library selection, pattern decision) | [no skill file] — write impl-decisions.md entry during DO step. Template in team-orchestrator.md Fix 15A | others |
```

**Health check:** `/docs/phase-N/impl-decisions.md` exists with ≥1 entry before GATE 5 runs for any sprint with non-trivial stories.

---

### 17F — ADD MEMORY FILE LOAD TRIGGER TO HOOK STEP 4

**Problem:** `kiro/steering/memory-management.md` uses `fileMatch: init_docs/` — it only loads when init_docs/ files match. For sessions without init_docs/ files present, memory-management.md never loads and the session-start memory retrieval protocol (read lessons.md, decisions.md at session start) never fires.

**Fix:** Add to hook Step 4 (ALL MODES block):
```
ALL MODES — session start:
  IF docs/lessons.md OR docs/decisions.md exist in the workspace:
    LOAD: kiro/steering/memory-management.md
    Execute memory retrieval protocol BEFORE first role activates.
    Log: [MEMORY: lessons.md loaded (N entries), decisions.md loaded (N ADRs)]
```

**Health check:** `[MEMORY: lessons.md loaded]` log line appears at session start when memory files exist. Lessons are consulted before first role action.

---

### 17G — ADD 85% CONTEXT CHECK TO GOAL ANCHOR INJECTION

**Problem:** `context-memory-discipline.md` Section 5 defines 85% threshold offloading, but there's no periodic signal prompting the model to check its context level. The Goal Anchor injection (every 10 tool calls) is the natural periodic checkpoint — but it only checks objective drift, not context size.

**Fix:** Update Goal Anchor injection in `context-memory-discipline.md` Section 5:
```
Every 10 tool calls, inject:
[GOAL ANCHOR — tool call N]: Original objective: "<$ORIGINAL_OBJECTIVE>".
All current work must advance this objective directly.
If the last 3 tool calls did not advance this → STOP. Re-read objective. Re-route.

ALSO at this checkpoint: Check context level.
  If context > 85% → run 85% THRESHOLD OFFLOADING (see below) before continuing.
  Log: [CONTEXT CHECK — tool call N: X% used. Offloading: YES/NO]
```

**Health check:** `[CONTEXT CHECK — tool call N]` log line appears every 10 calls alongside Goal Anchor. Offloading fires before 90% (hard stop).

---

### 17H — ADD MEMORY WRITE STEP TO SM-RETRO

**Problem:** The session-end write protocol (write to lessons.md when a pattern is identified) is defined in project_map.md but no role is explicitly tasked with executing it. SM-RETRO runs at every sprint end — the natural session boundary — but its current definition doesn't include the memory write step. Result: lessons.md stays at 3 seed entries indefinitely.

**Fix:** Add to SM-RETRO definition in `team-orchestrator.md`:
```
SM-RETRO — MEMORY WRITE STEP (run before producing retro doc):
1. Read docs/lessons.md — note the last entry date and confidence levels.
2. If any pattern from THIS sprint isn't captured → append entry with confidence: low.
3. If any low/medium entry from a prior sprint was confirmed this sprint → upgrade confidence.
4. Read docs/decisions.md — if any architectural decision was made or superseded this sprint → update ADR.
5. Log: [MEMORY WRITE: N entries updated/added to lessons.md, N ADRs updated]
This step is not optional. It runs before the retro 3-working/3-improve/3-actions sections.
```

**Health check:** lessons.md gains ≥1 new entry per sprint. Confidence levels evolve across sprints. `[MEMORY WRITE]` log line appears in every SM-RETRO output.

---

#

## FIX 17 — HEALTH CHECKS

| # | Signal | Pass condition |
|---|--------|----------------|
| 17A | Complexity gate fires | Conversational prompts show no [ENV] / [MODE] log output |
| 17B | data_engineer/mobile_engineer/data_scientist triggerable in Mode 2 | Kafka pipeline request → `[SKILLS ACTIVATED: role=data_engineer]` |
| 17C | Skill file summarization enforced | No full skill file text in context after artifact production |
| 17D | shared/SKILL.md exists | `kiro/skills/shared/SKILL.md` present with 9 file entries |
| 17E | impl-decisions.md populated | Entry exists before GATE 5 for any non-trivial sprint |
| 17F | Memory load at session start | `[MEMORY: lessons.md loaded]` at start of sessions where files exist |
| 17G | Context level checked every 10 calls | `[CONTEXT CHECK — tool call N]` in every 10-call cycle |
| 17H | lessons.md grows over time | lessons.md has more entries after each sprint than before |

---

## FIX 18 — LOW PRIORITY ✅ IMPLEMENTED 2026-06-30 (polish + completeness)

**Source:** Deep review analysis (docs/system-review-2026-06-30-v2.md), 2026-06-30.
**Priority:** 🟢 Low — system works without these. Fix when convenient.

---

### 18A — ADD ADR-009 TO ADR-012 TO decisions.md

Fixes 14 and 15 introduced architectural decisions not yet recorded as ADRs.

Add to `docs/decisions.md`:
- ADR-009: UI prerequisite gate approach — design_system_gate.md as blocking prerequisite vs inline linting rules
- ADR-010: Sprint Discipline Card as SM-RETRO blocker vs optional appendix
- ADR-011: impl-decisions.md as per-sprint ephemeral doc vs permanent ADR index entry
- ADR-012: shared/ skill directory vs per-role copies for cross-role skills

---

### 18B — FIX MODE 3 TRIGGER WORDING

`orchestrator-routing.md` line 173: "Neither Mode 1, Mode 2, nor Mode 4 matches."
Should read: "Neither Mode 1, Mode 2, Mode 4, nor Mode 5 matches."
One-line edit. Mode 5 is explicit-trigger only, so the logic is already correct — just the description is incomplete.

---

### 18C — ADD CROSS-REFERENCE BETWEEN loop-engine.md AND LEAN LOOP SPEC

`orchestrator-routing.md` line 224 defines `LEAN LOOP SPEC` for Mode 5. `loop-engine.md` defines the standard loop spec for Modes 1/4. The QUALITY role in lean mode may load loop-engine.md and be confused by the full 4-section format.

**Fix:** Add a note to loop-engine.md: `"In Mode 5 (Lean), use LEAN LOOP SPEC defined in orchestrator-routing.md Mode 5 section — max 2 CRITERIA, STOP WHEN at 4 iterations (not 8)."`
And to orchestrator-routing.md Mode 5: `"LEAN LOOP SPEC replaces loop-engine.md format for all lean-mode stories."`

---

### 18D — UPDATE HOOK PROMPT CACHING NOTE FOR KIRO DESKTOP

`elite-team-orchestrator.kiro.hook` prompt caching note says: "API callers: place `cache_control`..."
In Kiro desktop, prompt caching of static steering files is automatic — no explicit configuration needed. The note is confusing for desktop users.

**Fix:** Replace with: `"Prompt caching: In Kiro desktop, static steering files are cached automatically. Via API: add cache_control: {\"type\": \"ephemeral\"} at end of the last static content block."`

---

#

## FIX 18 — HEALTH CHECKS

| # | Signal | Pass condition |
|---|--------|----------------|
| 18A | decisions.md has ADR-009–012 | Four new ADRs present with valid_from / valid_to |
| 18B | Mode 3 trigger wording | "nor Mode 5" present in Mode 3 trigger description |
| 18C | Lean loop spec cross-reference | Both loop-engine.md and orchestrator-routing.md Mode 5 reference each other |
| 18D | Hook caching note | No "API callers" only language; covers both desktop and API |

## FIX 19 — TEAM-ORCHESTRATOR SPLIT + P0 FIXES ✅ IMPLEMENTED 2026-06-30

**Motivation:** AI professional review (v3) identified lost-in-middle attention risk on 1,264-line
team-orchestrator.md and discovery-engine.md always-loading wastefully on Mode 3 sessions.

**Note:** Review v3 incorrectly flagged CLAUDE-implemented.md as always-loading (grep matched content text,
not frontmatter). CLAUDE-implemented.md has no YAML frontmatter — it is NOT auto-loaded. Correction noted here.

### 19A — Fix discovery-engine.md always-load (P0)
- `kiro/steering/discovery-engine.md`: `inclusion: always` → `inclusion: manual`
- Hook Step 3: added explicit note that manual load is now required
- Saves ~2,319 tokens on every Mode 2/3 session

### 19B — Split team-orchestrator.md into 3 phase files (P1-A)
- `team-orchestrator-core.md` (425 lines) — roles, SM modes, GATE 1-3, JIRA lifecycle, impl-decisions
- `team-orchestrator-sprint.md` (316 lines) — GATE 4 (memory write + SM-RETRO), GATE 5 (report templates), MODE 1 SELF-CHECK, PHASE PARALLELISM RULES
- `team-orchestrator-rules.md` (554 lines) — SECURITY DISCIPLINE first (highest attention), NON-NEGOTIABLES, CONFLICT RESOLUTION, AGILE ENGINE, BRANCH LIFECYCLE, WORKSPACE LAYOUT, DOCUMENT OWNERSHIP
- Original `team-orchestrator.md` replaced with redirect stub
- Hook Step 4 updated: core + rules at session start, sprint at sprint end
- orchestrator-routing.md: all 9 references updated
- skill-selection-matrix.md: 2 impl-decisions references updated
- adapters: claude-setup-guide.md + chatgpt-setup-guide.md updated

**Token impact:**
- Mode 3 sessions: save ~2,319 tokens (discovery no longer always-loads)
- Mode 1 GATE 4/5 content now in top-attention zone of team-orchestrator-sprint.md
- SECURITY DISCIPLINE now in top-attention zone of team-orchestrator-rules.md

---

## FIX 20 — PERFORMANCE + INTELLIGENCE (from v3 AI Pro Review)

Priority: Medium. Items from system-review-2026-06-30-v3-ai-pro.md.

### 20A — Step 0 Keyword Expansion
**Problem:** Step 0 complexity gate keyword list missing WRITE, REVIEW, ANALYZE, AUDIT, RUN.
"Write the architecture doc" (5 words, no trigger) wrongly skips all steps → falls to Mode 3.
**Fix:** Add to Step 0 trigger bypass list in hook:
  BUILD / CREATE / MAKE / DEVELOP / IMPLEMENT / DESIGN / PLAN / ARCHITECT / SPRINT / PHASE
  + WRITE / REVIEW / ANALYZE / AUDIT / RUN / GENERATE / REFACTOR / TEST / DOCUMENT
**File:** kiro/hooks/elite-team-orchestrator.kiro.hook (Step 0)

### 20B — Measurable Memory Confidence Criteria
**Problem:** confidence: low/medium/high assigned by model impressionistically. Subjective = noise.
**Fix:** Replace with objective sprint-count criteria in memory-management.md and MEMORY WRITE protocol:
  confidence: low    → Observed in 1 sprint. Not yet validated in a separate sprint.
  confidence: medium → Observed in 2+ separate sprints. No contradictions recorded.
  confidence: high   → Observed in 5+ sprints. Zero contradictions. User-confirmed at least once.
  Rules: Model checks checkpoint.md dates to verify sprint count. Cannot self-assign high.
**Files:** kiro/steering/memory-management.md; team-orchestrator-sprint.md (MEMORY WRITE step 2b)

### 20C — Role Handoff Structured Format
**Problem:** "Compress to ≤300 tokens" has no format spec → inconsistent outputs, next role can't parse.
**Fix:** Define ROLE HANDOFF template in team-orchestrator-core.md after ARTIFACT CHAIN section:
  ```
  ROLE HANDOFF — [role_name]
  Artifact: [type + canonical filename]
  Key decisions: [2-3 bullets, ≤50 tokens each]
  Blockers: [none | description]
  Next role needs: [specific context required, or none]
  Token count: ~[N]
  ```
  Total: ~200 tokens. Replace "compress to ≤300 tokens" with "use ROLE HANDOFF format."
**File:** kiro/steering/team-orchestrator-core.md (after ARTIFACT CHAIN)

### 20D — Domain Tags in lessons.md for Filtered Loading
**Problem:** MEMORY load at session start loads ALL lessons regardless of domain relevance.
25 backend lessons load in a mobile sprint — irrelevant noise in context.
**Fix:** Add domain tag to each lesson entry:
  `## [date] [confidence] [domain: backend | frontend | mobile | data | security | all]`
  MEMORY WRITE (GATE 4) must tag each new entry with the sprint's primary lane.
  MEMORY LOAD (session start) filters: load entries where domain matches current build + all domain:all entries.
**Files:** docs/lessons.md (schema); kiro/steering/memory-management.md (load + write rules)

### 20E — Goal Anchor → Tie to 85% Threshold Instead of Count
**Problem:** "Every 10 tool calls" requires self-counting — unreliable in long sessions.
Count-based triggers drift; condition-based triggers are mechanical.
**Fix:** In context-memory-discipline.md Section 5, replace:
  "Every 10 tool calls, inject [GOAL ANCHOR]"
  with:
  "At every 85% THRESHOLD CHECK (already triggered mechanically): inject [GOAL ANCHOR] first, THEN run eviction."
  This ties anti-drift to a reliable trigger rather than self-counting.
**File:** kiro/steering/context-memory-discipline.md (Section 5)

### 20F — Byte-Based Context Pressure Metric
**Problem:** Degradation tiers count "reads" (operations) not context pressure (bytes).
4 large file reads (PEAK tier) can be more pressured than 12 bash commands (CRITICAL tier).
**Fix:** Add secondary threshold in context-memory-discipline.md Section 4:
  If tool output content accumulated > 50KB since session start → treat as DEGRADING regardless of read count.
  Log: [PRESSURE: ~NKB accumulated. Tier override: DEGRADING]
  Formula: estimate 1 tool output ≈ 2-4KB average. Track running total.
**File:** kiro/steering/context-memory-discipline.md (Section 4, after DEGRADATION TIERS table)

### 20G — Skill Loading Redesign: Compress-All Replaces Max-3 Cap
**Problem:** "Max 3 skill files per role" (Fix 9) is a blunt instrument. A senior_engineer_be doing
distributed systems work needs circuit_breaker, saga, outbox, caching, idempotency — 5 files.
The cap forces incomplete expertise.
**Root cause fix:** The right lever is COMPRESSION, not COUNT.
**New protocol:**
  OLD: Load max 3 skill files → hold full content during role work
  NEW:
    1. Load ALL activity-relevant files from matrix row (no hard count cap)
    2. For EACH file: Extract key principles → compress to 5-line takeaway → discard full content
    3. Work from compressed summaries (total context: N files × ~60 tokens = much less than 3 full files)
    4. Soft token cap: total compressed skill context ≤ 2,000 tokens (≈ 8-10 summaries)
    5. On-demand full load: when executing a specific substep requiring a detailed checklist
       (e.g., OWASP Top 10 check, WCAG audit) → re-load that ONE file → execute substep → discard
    6. Log: [SKILLS: role=X | activity=Y | files=A,B,C,D | compressed to N summaries | Σ~Ntok]
  Token math example: 6 files × 60 tokens = 360 tokens (vs 3 files × 500 tokens = 1,500 tokens full)
  Result: 2× more skill coverage at 76% less context cost.
**Files:**
  - kiro/steering/skill-selection-matrix.md (SKILL LOADING PROTOCOL — remove max 3, add compress-all)
  - kiro/steering/context-memory-discipline.md (Section 4 SKILL FILES rule — extend to match)
  - kiro/hooks/elite-team-orchestrator.kiro.hook (Step 5 log format update)

---

## FIX 21 — STRUCTURAL INTEGRITY (from v4 AI Pro Review)

Priority: Medium-Low. Items from system-review-2026-06-30-v4-ai-pro.md.

### 21A — Session-Start Skill File Verification
**Problem:** Missing shared/ skill files fail silently. Model falls back to SKILL.md index without
logging a visible warning. Entire sprints can run without a skill file the architect assumed was present.
**Fix:** Add to hook Step 5 (after matrix load):
  Scan skill-selection-matrix.md for all shared/* path references.
  For each: verify file exists at kiro/skills/shared/<filename>.
  If missing: log [INIT WARNING: skill file absent — kiro/skills/shared/<filename>]
              add to sprint backlog: "Create missing skill: kiro/skills/shared/<filename>"
  Do NOT block the session — warn and continue.
**File:** kiro/hooks/elite-team-orchestrator.kiro.hook (after Step 5 table)

### 21B — Memory Resync Within Session
**Problem:** MEMORY LOAD happens at session start. MEMORY WRITE happens at sprint end (GATE 4).
Lessons written at sprint end don't apply to the next sprint in the same session — they sit in
the file but not in context. Sprint N+1 within the same session runs without Sprint N's lessons.
**Fix:** Add to MEMORY WRITE step 2b in team-orchestrator-sprint.md, after the 5 write steps:
  "6. Re-inject into active context the 3 most recently written/upgraded entries:
       Log: [MEMORY REFRESH: N new entries now active this session]
       HIGH-confidence entries from this sprint apply immediately to the next story/sprint."
**File:** kiro/steering/team-orchestrator-sprint.md (GATE 4 step 2b, item 6)

### 21C — shared/SKILL.md: inclusion always → manual
**Problem:** shared/SKILL.md (created Fix 17D) has inclusion: always. Wastes ~783 tokens on
Mode 3 sessions where no shared skill files are ever loaded.
**Fix:** Change frontmatter to inclusion: manual.
  Add load trigger note to hook Step 5: "If any activated role has shared/* skills, shared/SKILL.md
  is the path resolution guide — load it before resolving paths."
**Files:** kiro/skills/shared/SKILL.md (frontmatter); hook Step 5

### 21D — NON-NEGOTIABLES Second Position in team-orchestrator-rules.md
**Problem:** NON-NEGOTIABLES (violations that block the entire pipeline) is currently mid-file in
rules.md. It should be immediately after SECURITY DISCIPLINE — the two together form the
"absolute hard blocks" group that must be in the highest-attention zone.
**Fix:** In team-orchestrator-rules.md: move NON-NEGOTIABLES section to immediately after
SECURITY DISCIPLINE (before CONFLICT RESOLUTION).
**File:** kiro/steering/team-orchestrator-rules.md (section reorder)

### 21E — Hook JSON Description Field (Metadata)
**Problem:** hook JSON description field says "delegates ALL role execution to team-orchestrator.md"
— stale after Fix 19 split. Not runtime-critical (not injected into model context) but misleading.
**Fix:** Update description to reference the 3 split files.
**File:** kiro/hooks/elite-team-orchestrator.kiro.hook (description field only)

---

## FIX 22 — DRY-RUN GAPS (from system dry run 2026-06-30)

Priority: High (A, F, G are correctness issues; B-E are friction). Source: docs/dry-run-2026-06-30.md.

### 22A — Hook STEP 6 Stale Handoff Instruction
**Problem:** Hook STEP 6 DISCIPLINE says "compress to ≤300 tokens before passing to orchestrator."
Fix 20C added the structured ROLE HANDOFF template (~200 tokens) to team-orchestrator-core.md.
Two conflicting instructions — model reads both, undefined which wins.
**Fix:** Replace in hook STEP 6:
  OLD: "Handoff compression: role output → compress to ≤300 tokens before passing to orchestrator."
  NEW: "Handoff: use ROLE HANDOFF format (~200 tokens) defined in team-orchestrator-core.md (Fix 20C).
        Fields: Artifact path | Key decisions (3×≤50 tok) | Blockers | Next role needs | Token count."
**File:** kiro/hooks/elite-team-orchestrator.kiro.hook (STEP 6)

### 22B — Domain Tag Schema: One Tag Only
**Problem:** memory-management.md §9 defines domain as a single value (backend|frontend|mobile|data|security|devops|all).
Dry run wrote "domain: backend+devops+security" (compound) — breaks MEMORY LOAD filter logic.
The filter does string-match, not set-intersection. Compound tags = never matched = lesson always skipped.
**Fix:** Clarify in memory-management.md §9:
  - ONE domain tag per entry. Choose PRIMARY lane.
  - If lesson applies to 2+ lanes equally → use `domain: all`
  - Examples: "FastAPI idempotency" → domain: backend. "PII scrubber" → domain: security. "Sprint buffer rule" → domain: all
  - MEMORY WRITE rule: model chooses the single most specific domain, defaults to `all` when ambiguous.
**File:** kiro/steering/memory-management.md (§9)

### 22C — design_system_gate: Move to GATE 2 (SM-GATE)
**Problem:** design_system_gate currently fires on FIRST FE story execution (during DEVELOP).
This adds unplanned work mid-sprint, breaking sprint point estimates.
Dry run: CALC-1 hit the gate; 0.5 pts of unplanned work not in sprint plan.
**Fix:** Add to SM-GATE checklist (prebuild_documentation_gate.md check in GATE 2):
  "[ ] If any sprint stories are labeled frontend/* or mobile/* → check docs/design_system.md exists.
       If missing: add story 'Create minimal design system' to Sprint 1 backlog BEFORE finalizing sprint."
  This surfaces the gate at SM-GATE (GATE 2) so SM-PLAN accounts for it.
**Files:** kiro/steering/team-orchestrator-sprint.md (GATE 2 SM-GATE checklist); kiro/steering/prebuild_documentation_gate.md (if exists)

### 22D — Security Engineer DEVELOP Pass: Define Scope
**Problem:** security_engineer has a full STRIDE+OWASP pass in DESIGN.
In DEVELOP (e.g., Sprint 4 Executor), security_engineer activates again — but scope is undefined.
Does it re-run full STRIDE? Just implementation-specific checks? Just S2+S3 gates?
Model has no guidance → inconsistent behavior across sprints.
**Fix:** Add to skill-selection-matrix.md security_engineer section, row for DEVELOP pass:
  | Reviewing implementation of security-critical story (executor, auth, PII handler) | [no full STRIDE re-run] — check: (1) implementation matches DESIGN decision, (2) S2: no new trust boundaries introduced, (3) S3: secrets handling correct. If new trust boundary found → flag, add ADR. Full STRIDE only if architecture changed. | security, devops |
**File:** kiro/steering/skill-selection-matrix.md (security_engineer section)

### 22E — impl-decisions.md: Close the Write-Only Sink
**Problem:** senior_engineer_be/fe writes impl-decisions.md during DO steps (Fix 15A, 17E).
Nothing reads it back. SM-RETRO doesn't reference it. GATE 4 doesn't check it.
Architectural decisions documented in impl-decisions.md effectively disappear — they don't flow to lessons.md or ADRs.
**Fix:** Add to GATE 4 step 2b (MEMORY WRITE), after step 4 (ADR update), new step 4b:
  "4b. Read docs/phase-N/impl-decisions.md — scan for entries marked [PROMOTE]:
        If any: promote to ADR (consequential architectural decision) OR to lessons.md (pattern/learning).
        If none marked [PROMOTE]: scan for any entry appearing in 2+ stories (recurring pattern) → promote to lessons.md confidence: low.
        Log: [IMPL-DECISIONS: N entries reviewed, N promoted]"
  Add to senior_engineer_be/fe matrix: "Mark entry [PROMOTE] if decision is reusable across projects or deviates from a default pattern."
**Files:** kiro/steering/team-orchestrator-sprint.md (GATE 4 step 2b); kiro/steering/skill-selection-matrix.md (senior_engineer_be + fe rows)

### 22F — Cross-Session Sprint Continuity
**Problem:** Hook STEP 4 memory load reads lessons.md + decisions.md but NOT checkpoint.md.
In a multi-sprint build, if the user starts a NEW session for Sprint 2, the model loads memory
but doesn't know: which sprint is active, what was shipped in Sprint 1, what stories are in progress.
Sprint 2 starts blind — no velocity baseline, no sprint context, wrong assumptions about project state.
**Fix:** Add to hook STEP 4 memory check block:
  "IF docs/checkpoint.md exists:
     Read LAST ROW only (latest state — not full file).
     If last row contains 'Sprint N complete' → Sprint N+1 is next. Load sprint N+1 context.
     If last row contains 'Sprint N in progress' → resume Sprint N. Load active stories from $TRACKER.
     Log: [SPRINT STATE: Sprint N+1 next | Sprint N resuming | fresh build]"
**File:** kiro/hooks/elite-team-orchestrator.kiro.hook (STEP 4, after memory check)

### 22G — TRIVIAL BUILD Tier: Route Micro-Builds to Mode 3
**Problem:** "build me a calculator" triggered Mode 5 — 10 agent activations, 3 ADRs, Jira epic,
sprint planning, SM-GATE, SM-RETRO. All for a single-file web app.
Mode 5 is "Lean Single Sprint" — still a sprint process with gates and Jira.
A calculator is a 30-minute task for one developer. The overhead is 5× the actual work.
Root cause: Step 2 correctly classifies BUILD, discovery engine has no TRIVIAL tier below Mode 5.
**Fix — two changes:**
  1. Add TRIVIAL class to Step 2 classification BEFORE BUILD check:
     | TRIVIAL | Single file or single function. No backend, no integrations, no multi-role work, no database. Examples: calculator, todo list, converter, formatter, script. Prompt ≤ 12 words AND no system/platform/service/infrastructure/integration mentioned. | → MODE 3 direct (Fix 22G) |
     TRIVIAL is checked BEFORE BUILD. If TRIVIAL matches → skip Steps 3-5. No discovery, no mode selection.
  2. In MODE 3 execution block (STEP 4): add TRIVIAL BUILD note:
     "If request was classified TRIVIAL BUILD: single senior role executes directly.
      No Jira stories. No ADRs unless a non-obvious decision is made. No sprint.
      Write tests. Produce Mode 3 Build Report. Done."
**Token savings:** TRIVIAL BUILD = ~8,000 tokens vs Mode 5 = ~31,000 tokens. 74% reduction.
**Files:** kiro/hooks/elite-team-orchestrator.kiro.hook (Step 2 + Step 4 Mode 3 block)

## FIX 23 — DYNAMIC SKILL × AGENT SELECTION (from dry-run analysis + architecture review)

Priority: High. Replaces static keyword-match matrix with label-indexed dynamic skill resolution.
Root problem: current skill selection is text-matching on "Activity" column — fragile, undefined multi-row behavior, fallback is filename guessing (~30% wrong). Source: docs/dry-run-2026-06-30.md + design session 2026-06-30.

### 23A — Story Label Taxonomy (the vocabulary)
**Problem:** No shared vocabulary between SM-PLAN (who labels stories) and skill-selection-matrix.md (who maps labels to files). Stories use free-text descriptions → skill lookup is approximate.
**Fix:** Define 30 canonical story labels in team-orchestrator-core.md under a new "STORY LABEL TAXONOMY" section:

Backend lane:
  be/api          — REST/GraphQL endpoint, API contract, request/response schema
  be/caching      — Redis, Memcached, cache invalidation, TTL strategy
  be/queue        — Kafka, SQS, RabbitMQ, message broker, event publishing
  be/database     — DB queries, ORM, schema reads/writes, stored procs
  be/resilience   — Circuit breaker, retry, saga, idempotency, rate limiting
  be/auth         — Authentication, authorization, JWT, OAuth, session
  be/pii          — PII handling, data scrubbing, privacy-preserving ops
  be/ml           — ML inference, embedding generation, model serving, vector ops

Frontend lane:
  fe/component    — UI components, React/Vue/Svelte, styling, layout
  fe/form         — Form validation, multi-step flows, UX patterns
  fe/state        — State management, store design, reactivity
  fe/a11y         — Accessibility, ARIA, keyboard nav, screen reader
  fe/perf         — Web vitals, bundle size, lazy loading, rendering perf

Mobile lane:
  mobile/ios      — Swift/UIKit/SwiftUI, iOS-specific patterns
  mobile/android  — Kotlin/Jetpack, Android-specific patterns
  mobile/rn       — React Native, cross-platform, Expo
  mobile/offline  — Offline sync, local storage, conflict resolution

Data lane:
  data/pipeline   — ETL, batch processing, dbt, data warehouse loading
  data/streaming  — Kafka Streams, Spark Streaming, Flink, CDC
  data/modeling   — Data model design, dimensional modeling, schema evolution
  data/eda        — Exploratory analysis, statistical analysis, visualization

Security lane:
  security/auth   — Auth implementation, token handling, RBAC
  security/pii    — PII detection, scrubbing, retention, GDPR
  security/review — Security code review, OWASP check, threat validation
  security/secrets — Secrets management, Vault, env var hygiene

DevOps lane:
  devops/k8s      — Kubernetes deployment, Helm, pod config, scaling
  devops/ci       — CI/CD pipeline, GitHub Actions, build, test automation
  devops/infra    — IaC, Terraform, cloud resources, networking
  devops/monitor  — Observability, metrics, tracing, alerting, dashboards

Cross-cutting (any lane):
  testing/unit        — Unit tests, mocking, test isolation
  testing/integration — Integration tests, test containers, DB fixtures
  testing/e2e         — End-to-end tests, browser automation, flow coverage
  testing/contract    — Contract tests, pact, consumer-driven contracts
  impl-decision       — Non-trivial algorithm/library/pattern choice (triggers impl-decisions.md entry)
  security-critical   — Triggers security_engineer DEVELOP pass (Fix 22D)

**File:** kiro/steering/team-orchestrator-core.md (new section: STORY LABEL TAXONOMY)

### 23B — SM-PLAN: Labels Required Per Story (gate enforcement)
**Problem:** SM-PLAN currently assigns points and acceptance criteria but story labels are informal/optional. Without labels, dynamic skill selection has no input → falls back to guessing.
**Fix:** Add to SM-PLAN mode in team-orchestrator-core.md:
  "Every story MUST have ≥1 label from the STORY LABEL TAXONOMY before it enters the sprint.
   No story enters IN PROGRESS without labels.
   SM-PLAN assigns labels at story creation. SM-GATE (GATE 2) blocks sprint if any story has zero labels.
   Format in Jira/markdown: story labels = [be/api, be/resilience] (array, 1-4 labels max per story)
   SM assigns: primary lane label (required) + cross-cutting labels (optional, add if clearly applicable)"
Add to SM-GATE prebuild checklist (team-orchestrator-sprint.md):
  "[ ] All sprint stories have ≥1 taxonomy label from STORY LABEL TAXONOMY"
**Files:** kiro/steering/team-orchestrator-core.md (SM-PLAN section); team-orchestrator-sprint.md (SM-GATE checklist)

### 23C — Skill Index: Rewrite Matrix as Label-Keyed Index
**Problem:** skill-selection-matrix.md is a per-role table with free-text "Activity" column. Lookup is O(n) text scan. Multi-row matches create undefined union behavior. Hard to maintain (255 skill files × 22 roles = complex).
**Fix:** Restructure skill-selection-matrix.md into two sections:
  Section 1 — SKILL INDEX (label → files, role-agnostic shared resolution):
    For each taxonomy label, list the skill files that apply regardless of role.
    Example:
      be/api:
        - api_design_restful.md
        - shared/api_versioning_strategy.md
        - shared/error_handling_strategies.md
      be/resilience:
        - distributed_systems_resilience.md
        - circuit_breaker_patterns.md
        - shared/error_handling_strategies.md
      security-critical:
        - shared/security_baseline.md
        [+ triggers security_engineer DEVELOP pass per Fix 22D]

  Section 2 — ROLE OVERRIDES (role-specific additions/exclusions per label):
    Only list what differs per role. Most roles use Section 1 as-is.
    Example:
      senior_engineer_be + be/api: add [idempotency_patterns.md] (BE-specific depth)
      security_engineer + be/api:  add [owasp_top_10.md] (security lens on API work)
      qa_engineer + be/api:        add [shared/testing_pyramid.md, contract_testing.md]

  Dynamic resolution at story activation:
    story labels → Section 1 lookup → base skill set
    + role → Section 2 lookup → role-specific additions
    → union, deduplicate → compress all → Σ ≤ 2,000 tokens
    Log: [SKILLS: labels=[X,Y] | role=Z | files=A,B,C,D | Σ~Ntok compressed]

**File:** kiro/steering/skill-selection-matrix.md (full restructure — keep existing per-role tables as reference during transition, mark deprecated)

### 23D — Loop Verifier CHECK: Label-Specific Scoring Criteria
**Problem:** loop-engine.md CHECK scores artifact 0-10 but criteria are generic. No connection to which skills were loaded for this story. A be/api story and a fe/component story get evaluated on the same generic criteria → misses domain-specific quality bars.
**Fix:** In loop-engine.md CHECK section, add label-sourced criteria resolution:
  "Before scoring, read the activated skill files' compressed summaries (already in context).
   Extract quality criteria FROM those summaries — not from a generic checklist.
   be/api summary likely contains: idempotency, versioning, error format → those become CHECK criteria.
   be/resilience summary likely contains: retry logic, rate limiting, circuit breaker → CHECK criteria.
   Score each criterion: present (1) / partial (0.5) / missing (0)
   Total = Σ scores / n_criteria × 10
   If score < 7: ACT — identify which criterion failed → reload that specific skill file FULL CONTENT → revise → re-CHECK
   Log: [CHECK: story=X | labels=[Y,Z] | criteria=N | score=S/10 | ACT=YES/NO]"
**File:** kiro/steering/loop-engine.md (CHECK section)

### 23E — Fallback: Label Inference When Story Has No Labels
**Problem:** Even with 23B enforcement, edge cases exist: Mode 3 TRIVIAL builds, Mode 2 single-role tasks, stories created outside SM-PLAN (user-added mid-sprint). These have no taxonomy labels.
**Fix:** Define label inference fallback (NOT filename guessing — Fix 22 eliminated that):
  "IF story has no taxonomy labels:
   1. Read story title + acceptance criteria (already in context — no file read needed)
   2. Match key nouns/verbs against label taxonomy keyword map:
      'endpoint' / 'API' / 'POST/GET/PUT' → guess: be/api
      'database' / 'migration' / 'schema' → guess: be/database
      'component' / 'render' / 'CSS' → guess: fe/component
      'Kubernetes' / 'Helm' / 'deploy' → guess: devops/k8s
      'test' / 'spec' / 'coverage' → guess: testing/unit + testing/integration
      'secret' / 'auth' / 'JWT' → guess: security/auth
   3. Pick top 2 label guesses → use as if they were explicit labels
   4. Log: [SKILLS: labels=INFERRED([X,Y]) | role=Z | files=... — story had no explicit labels]
   5. SM note: add inferred labels to story retroactively
  This is cleaner than filename guessing: model picks LABELS (30 options), then label → files (deterministic)."
**File:** kiro/steering/skill-selection-matrix.md (FALLBACK section at bottom)

---

## FIX 23 IMPLEMENTATION ORDER

1. 23A — taxonomy spec in core.md (spec work, no code — defines the vocabulary)
2. 23B — SM-PLAN + SM-GATE enforcement (ensures 23C has input to work with)
3. 23C — skill index restructure (biggest change — matrix becomes label-keyed)
4. 23E — fallback inference (safety net before 23C goes live)
5. 23D — loop verifier CHECK integration (ties loop engine to skill content — the "thunder")

## DRY RUN GAP — loop-engine.md not traced
The DEVELOP phase dry run described story execution without tracing PLAN→DO→CHECK→ACT.
Loop engine is loaded at DEVELOP start (hook Step 4) but not validated in dry run.
Fix 23D resolves this by making CHECK criteria traceable — a future dry run should trace
one full PLAN→DO→CHECK→ACT cycle on a scored story (e.g., ASRE-3 score < 7 → ACT fires).

## FIX 24 — DRY RUN GAP CLOSURE (from docs/dry-run-2026-06-30-jwt-auth.md)

Source: End-to-end dry run on "Build a rate-limited JWT authentication API with Redis caching, retry logic, and integration tests". 4 red gaps, 3 yellow. Ref doc: docs/dry-run-2026-06-30-jwt-auth.md.

### 24A — Mode Auto-Inference (Gap A — 🔴)
**Problem:** STEP 3 runs discovery-engine.md → 7 scoping questions → waits for user. Single-shot build prompts stall here indefinitely.
**Fix:** Add auto-inference rule to STEP 3 in hook:
  "If prompt is a single sentence AND contains ≥2 of: API/service/system/integration/pipeline/agent/platform → infer Mode 1.
   If prompt contains ≥1 of those AND is clearly scoped to one role → infer Mode 2.
   Log: [MODE: N auto-inferred from prompt analysis — no user confirmation needed]
   Run discovery-engine.md 7 questions ONLY if prompt is ambiguous (multi-sentence, conflicting signals, or user types 'help me figure out the mode').
   Auto-inference covers ~80% of real prompts. Reserve scoping questions for the 20% that are genuinely ambiguous."
**File:** kiro/hooks/elite-team-orchestrator.kiro.hook (STEP 3)

### 24B — Skill Index File Existence (Gap B — 🔴)
**Problem:** Fix 23C label index references ~30 skill filenames that don't exist. Fix 21A correctly warns, but a new sprint starts with 30 backlog warnings every session — noise that buries real blockers.
**Fix:** Two-part:
  Part 1 — Create the 8 highest-priority shared skill files (ones referenced most in Section 1):
    kiro/skills/shared/api_versioning_strategy.md
    kiro/skills/shared/error_handling_strategies.md
    kiro/skills/shared/distributed_systems_resilience.md
    kiro/skills/shared/performance_optimization.md
    kiro/skills/shared/privacy_engineering.md
    kiro/skills/shared/infrastructure_as_code.md
    kiro/skills/shared/mobile_offline_sync.md
    kiro/skills/shared/decision_record_template.md
  Part 2 — Change Fix 21A INIT WARNING behavior:
    "If missing skill file count > 5: suppress individual warnings, emit one summary:
     [INIT WARNING: N skill files absent — run /kiro skill-audit for full list]
     Only warn individually for STOP-level missing files (team-orchestrator-*.md, skill-selection-matrix.md).
     Add to sprint backlog as ONE consolidated story: 'Create missing skills (N files)' rather than N separate stories."
**Files:** kiro/skills/shared/ (8 new files); kiro/hooks/elite-team-orchestrator.kiro.hook (Fix 21A warning behavior)

### 24C — LABEL GATE Timing (Gap C — 🔴)
**Problem:** LABEL GATE (Fix 23B) placed in SM-GATE prebuild checklist. SM-GATE runs before SM-PLAN. On Sprint 1, no stories exist yet — gate is a no-op.
**Fix:** Move LABEL GATE out of SM-GATE and into SM-PLAN post-creation check:
  "SM-PLAN creates stories → immediately validates: every story has ≥1 taxonomy label.
   If any story has zero labels: SM-PLAN BLOCKS its own output. Cannot emit sprint-plan.md until all stories labeled.
   SM-PLAN is self-gating on labels — it cannot hand off to DEVELOP with unlabeled stories.
   Log: [LABEL CHECK: N/N stories labeled ✅] or [LABEL BLOCK: story X has no labels — SM-PLAN halted]"
  SM-GATE checklist item becomes: "[ ] SM-PLAN completed label check — all stories confirmed labeled"
  (This is a post-hoc confirmation, not a live check.)
**Files:** kiro/steering/team-orchestrator-core.md (SM-PLAN section); kiro/steering/team-orchestrator-sprint.md (SM-GATE item reworded)

### 24D — Non-Shared Skill File Path Resolution (Gap D — 🔴)
**Problem:** Fix 23C skill index lists filenames like `auth_patterns_jwt_oauth.md` with no folder prefix. The system cannot locate non-shared files — only `shared/` prefix is resolved by Fix 21A.
**Fix:** Add path resolution rule to skill-selection-matrix.md SKILL LOADING PROTOCOL:
  "Non-shared skill files (no 'shared/' prefix) — resolve by ROLE at activation time:
   senior_engineer_be → kiro/skills/senior_engineer_be/<filename>
   senior_engineer_fe → kiro/skills/senior_engineer_fe/<filename>
   security_engineer  → kiro/skills/security_engineer/<filename>
   qa_engineer        → kiro/skills/qa_engineer/<filename>
   devops_engineer    → kiro/skills/devops_engineer/<filename>
   data_engineer      → kiro/skills/data_engineer/<filename>
   ml_engineer        → kiro/skills/ml_engineer/<filename>
   architect          → kiro/skills/architect/<filename>
   (and so on for all 22 roles)
   If file not found at role path: check kiro/skills/shared/<filename> as fallback.
   If still not found: trigger Fix 21A warning."
  Also: update Section 1 of label index to add role-hint comments where the file owner is unambiguous.
  Example: be/auth → [auth_patterns_jwt_oauth.md (senior_engineer_be), shared/security_baseline.md]
**Files:** kiro/steering/skill-selection-matrix.md (SKILL LOADING PROTOCOL + Section 1 role hints)

### 24E — SM Loop Spec Approval Wiring (Gap E — 🟡)
**Problem:** loop-engine.md says "SM approves the loop spec" but no hook step, gate, or agent trigger fires this approval before DEVELOP starts.
**Fix:** Add explicit loop spec approval step to team-orchestrator-core.md DEVELOP phase:
  "Before maker writes first line of code:
   1. maker (senior_engineer_be/fe) produces LOOP SPEC → writes to $TRACKER story comment
   2. scrum_master reviews loop spec: is GOAL falsifiable? Is VERIFIER runnable? Are CRITERIA ≥3 and label-sourced?
      If YES → SM emits [LOOP SPEC APPROVED: story X] → maker proceeds
      If NO  → SM returns specific objection → maker revises (max 1 revision before auto-approve)
   Time budget: SM loop spec review ≤ 1 tool call. Do not re-read all files for this step."
**File:** kiro/steering/team-orchestrator-core.md (DEVELOP phase artifact chain)

### 24F — Mid-Sprint Degradation Handling (Gap F — 🟡)
**Problem:** Mode 1 hits DEGRADING token tier by story 3 of 4. No rule specifies how DEVELOP continues at DEGRADING — roles still need to load skill files but compressed reads only.
**Fix:** Add DEGRADING-tier DEVELOP rule to context-memory-discipline.md:
  "IF token tier = DEGRADING during DEVELOP:
   - Skill loading: labels → index lookup → load compressed summaries ONLY (no on-demand full loads)
   - Exception: security-critical stories — FULL LOAD still allowed for OWASP/STRIDE substep (non-negotiable)
   - Loop engine: max 1 ACT full-reload per story (not per criterion) to conserve budget
   - Log: [DEGRADING: story X — full skill reload suppressed except security-critical substeps]
   IF token tier = CRITICAL during DEVELOP:
   - Pause DEVELOP. Emit: '[CRITICAL TOKEN TIER — recommend fresh session for remaining N stories]'
   - Complete current story only. Do not start next story.
   - Write loop-state to $TRACKER before stopping."
**File:** kiro/steering/context-memory-discipline.md (new DEVELOP-specific degradation section)

### 24G — skill-selection-matrix.md Size (Gap G — 🟡)
**Problem:** After Fix 23C, skill-selection-matrix.md is ~600 lines (~6,500 tokens). Loaded at STEP 4 for every Mode 1 session — burns 6,500 tokens before any role activates.
**Fix:** Split skill-selection-matrix.md into two files:
  skill-selection-matrix.md   → Keep: SKILL LOADING PROTOCOL + ROLE TRIGGER TABLE + legacy per-role rows
                                 (~150 lines, ~1,800 tok) — loaded at STEP 4 as before
  skill-label-index.md        → New: LABEL-INDEXED SKILL INDEX (Section 1 + Section 2 + FALLBACK)
                                 (~450 lines, ~4,700 tok) — loaded ONLY at SM-PLAN time (when labels are assigned)
  Hook STEP 4: load skill-selection-matrix.md only.
  SM-PLAN trigger: load skill-label-index.md when assigning labels to stories.
  This saves ~4,700 tokens from the mandatory-load baseline for all Mode 1 sessions.
**Files:** kiro/steering/skill-selection-matrix.md (trimmed); kiro/steering/skill-label-index.md (new); hook STEP 4 (load reference update)

---

## FIX 24 IMPLEMENTATION ORDER
1. 24C — Label gate timing (highest logic correctness impact, simple move)
2. 24D — Path resolution rule (unblocks skill loading entirely)
3. 24A — Mode auto-inference (unblocks single-shot entry)
4. 24G — Matrix split (token savings, straightforward file split)
5. 24B — Create 8 shared skill files + consolidate warnings (content work)
6. 24E — Loop spec approval wiring (adds one step to DEVELOP)
7. 24F — Degradation handling for DEVELOP (edge case, important for long sprints)

## FIX 25 — DRY RUN 2 GAP CLOSURE (PENDING — accumulating from dry runs)

Source: docs/dry-run-2026-06-30-dashboard.md + docs/dry-run-2026-06-30-all-scenarios.md.
Status: IMPLEMENTED 2026-06-30 — all 19 items (25A-25S) complete.

### 25A — Data Lane Shared Skill Files (Gap A — 🟡)
**Problem:** Fix 24B created 7 shared files focused on backend/devops/mobile. Data lane shared files referenced in skill-label-index.md still missing:
  kiro/skills/shared/data_modeling_principles.md
  kiro/skills/shared/statistical_analysis_patterns.md
**Fix:** Create these 2 files with same format as 24B files.
**Files:** kiro/skills/shared/ (2 new files)

### 25B — Design System Story Token Budget (Gap B — 🟡)
**Problem:** SM-GATE (Fix 22C) injects design_system story into Sprint 1 when docs/design_system.md is missing. This story (fe/component) competes with real stories for the token budget, pushing sprint to CRITICAL earlier.
**Fix:** Change SM-GATE injection behavior:
  IF Sprint 1 AND design_system.md missing → create design_system story as Sprint 0 prerequisite (not Sprint 1 story).
  If no Sprint 0 concept exists → flag as blocker: "Sprint 1 blocked until design_system.md exists. Run design_system story first."
  Sprint 1 only starts when design_system.md is present.
**Files:** kiro/steering/team-orchestrator-sprint.md (SM-GATE Design System Gate item)

### 25C — Multi-Lane Domain Detection (Gap C — 🟡)
**Problem:** STEP 4 domain detection picks ONE lane from the prompt. Multi-lane builds (data + frontend + backend in same prompt) only load lessons for the first detected lane. Other lanes' lessons are skipped.
**Fix:** Update STEP 4 memory load rule:
  Detect ALL lanes present in prompt (not just first match).
  Load lessons where domain IN (all detected lanes) OR domain=all.
  Example: "Kafka + React + Redis" → detected=[data, frontend, backend] → load domain=data OR domain=frontend OR domain=backend OR domain=all.
  Log: [MEMORY: N lessons loaded (domains: data+frontend+backend+all)]
**Files:** kiro/hooks/elite-team-orchestrator.kiro.hook (STEP 4 memory load block)

### 25D — CRITICAL + Sprint Complete Declaration (Gap D — 🟢 Minor)
**Problem:** Fix 24F says "complete current story at CRITICAL, stop." But when CRITICAL fires on the LAST story, SM-RETRO still needs to run. No explicit rule covers "CRITICAL on last story → sprint still completes."
**Fix:** Add to Fix 24F CRITICAL rule:
  "IF CRITICAL fires AND no stories remain after current one:
   → complete current story → proceed to GATE 4 / SM-RETRO (retro is cheaper than DEVELOP, ~2K tok)
   → emit: [CRITICAL: last story — proceeding to SM-RETRO]
   IF CRITICAL fires AND stories remain:
   → complete current story → STOP. Do not start next story."
**Files:** kiro/steering/context-memory-discipline.md (Fix 24F CRITICAL block)

---

**NOTE:** Items 25A-D are PENDING. Will accumulate additional gaps from dry runs 3+ before implementing all at once.
Additional gaps discovered in future dry runs will be appended here as 25E, 25F, etc.

---

### 25E — Label Index Full Rewrite — 26 Filename Mismatches (🔴 Critical — Universal)
**Source:** Dry run mismatch analysis script. Affects ALL scenarios.
**Problem:** skill-label-index.md (Fix 23C) was written top-down with INVENTED filenames. 26 references
  point to files that don't exist. Every skill resolution attempt in DEVELOP fires a warning.
  Also: stride_threat_modeling.md lives in architect/ but index assigns it to security_engineer/ (wrong role).
  Also: shared/security_baseline.md and shared/data_modeling_principles.md don't exist anywhere.
**Fix:** Full rewrite of skill-label-index.md Section 1 (SKILL INDEX) using actual verified filenames:

  be/api           → backend_lead/api_versioning.md + backend_lead/idempotency_patterns.md + shared/error_handling_strategies.md
  be/caching       → backend_lead/caching_strategies.md + shared/performance_optimization.md
  be/queue         → backend_lead/async_job_queue_patterns.md + backend_lead/outbox_pattern_event_publishing.md
  be/database      → backend_lead/database_schema_design.md + database_architect/index_design_query_plans.md
  be/resilience    → backend_lead/circuit_breaker_bulkhead.md + backend_lead/saga_pattern_distributed_transactions.md + shared/distributed_systems_resilience.md
  be/auth          → security_engineer/auth_design.md + shared/privacy_engineering.md
  be/ml            → ml_engineer/ai_ml_system_design.md + ml_engineer/contextual_retrieval.md + database_architect/vector_database_design.md
  data/streaming   → data_engineer/stream_processing_kafka.md + data_engineer/cdc_change_data_capture.md
  data/pipeline    → data_engineer/batch_pipeline_spark.md + data_engineer/airflow_dag_design.md + data_engineer/dbt_transformation_patterns.md
  data/eda         → data_scientist/exploratory_data_analysis.md + data_scientist/ab_test_statistical_analysis.md
  security/auth    → security_engineer/auth_design.md + security_engineer/cryptography_pki_key_management.md
  security/review  → security_engineer/api_security_owasp_top10.md + security_engineer/application_security_testing_sast_dast.md
  security-critical → security_engineer/api_security_owasp_top10.md + architect/stride_threat_modeling.md
  security/pii     → security_engineer/data_security_encryption_classification.md + database_architect/retention_and_gdpr_deletion.md + shared/privacy_engineering.md
  fe/component     → frontend_lead/component_decomposition.md + frontend_lead/modern_react_nextjs_patterns.md
  fe/state         → frontend_lead/state_management_patterns.md ✅
  fe/perf          → frontend_lead/core_web_vitals.md + frontend_lead/frontend_build_optimization.md + shared/performance_optimization.md
  fe/a11y          → frontend_lead/wcag_accessibility.md + qa_engineer/accessibility_testing.md
  mobile/ios       → mobile_engineer/ios_swiftui_architecture.md + shared/mobile_offline_sync.md
  mobile/android   → mobile_engineer/android_jetpack_compose.md + shared/mobile_offline_sync.md
  mobile/rn        → mobile_engineer/react_native_patterns.md ✅ + shared/mobile_offline_sync.md ✅
  mobile/offline   → mobile_engineer/mobile_offline_sync.md + shared/mobile_offline_sync.md
  devops/k8s       → devops_engineer/deployment_strategies.md + devops_engineer/gitops_argocd_flux.md
  devops/ci        → devops_engineer/ci_cd_pipeline_design.md
  devops/infra     → devops_engineer/iac_terraform_patterns.md + shared/infrastructure_as_code.md
  devops/monitor   → devops_engineer/monitoring_alerting_setup.md + sre_engineer/observability_three_pillars.md + sre_engineer/sli_slo_design.md
  security/secrets → devops_engineer/secrets_management_cicd.md + security_engineer/cryptography_pki_key_management.md
  testing/contract → qa_engineer/contract_testing.md ✅
  testing/unit     → shared/tdd_red_green_refactor.md + qa_engineer/property_based_testing.md
  testing/integration → qa_engineer/test_data_management.md + shared/tdd_red_green_refactor.md
  testing/e2e      → qa_engineer/visual_regression_testing.md + qa_engineer/exploratory_testing_charters.md
  impl-decision    → shared/decision_record_template.md ✅

  Remove shared/security_baseline.md and shared/data_modeling_principles.md from all label entries (don't exist).
  Fix Section 2 ROLE OVERRIDES: stride_threat_modeling.md → role: architect, not security_engineer.
**Files:** kiro/steering/skill-label-index.md (full Section 1 + Section 2 corrections)

---

### 25F — SM-UNBLOCK Wiring + Outcome Protocol (🔴 High — Scenario 8)
**Source:** Dry run Scenario 8 (Loop Hard Stop)
**Problem A:** SM-UNBLOCK has no wiring mechanism. loop-engine.md says "SM-UNBLOCK fires at iteration 8"
  but nothing routes the loop-state to SM-UNBLOCK. The $TRACKER comment holds loop-state — SM-UNBLOCK
  must read it, but there is no trigger rule that connects them.
**Problem B:** SCOPE-CUT/RE-SPEC/ESCALATE outcomes are undefined:
  - SCOPE-CUT: which criteria get cut? who updates $TRACKER? does story get partial credit?
  - RE-SPEC: who rewrites loop spec? does iteration count reset to 0 or continue from 8?
  - ESCALATE: to whom? what artifact does escalation produce? who unblocks the sprint?
**Problem C:** Hard-stopped story velocity: 0 pts? partial (criteria met count / total)? undefined.
**Fix:** Add SM-UNBLOCK PROTOCOL to loop-engine.md:
  Trigger: iteration=8 AND score<8 → write loop-state summary (story, failing criteria, last score)
           to $TRACKER as [LOOP-STUCK] block → SM-PLAN picks it up at next SM-RETRO read.
  SM-UNBLOCK decision table:
    SCOPE-CUT: remove failing criterion from loop spec. Story marked DONE. SM logs which criterion cut.
               Velocity: full story points (scope was reduced, not quality dropped).
    RE-SPEC: SM-PLAN rewrites loop spec criteria only. Iteration counter RESETS to 0. Max 1 RE-SPEC per story.
    ESCALATE: Write BLOCKED card to sprint-plan.md. User notified. Sprint pauses on that story.
              Other stories in sprint may continue. SM-RETRO includes BLOCKED card in velocity calc as 0pts.
**Files:** kiro/steering/loop-engine.md (SM-UNBLOCK PROTOCOL section)
           kiro/steering/team-orchestrator-sprint.md (BLOCKED card handling in SM-RETRO)

---

### 25G — DEGRADING Loop Convergence Trap (🟡 Medium — Scenario 8)
**Source:** Dry run Scenario 8 (complex multi-criteria story at DEGRADING tier)
**Problem:** Fix 24F (DEGRADING) limits ACT reloads to 1 per story. A story with 3+ failing criteria at
  score 5.0/10 cannot converge in 1 reload — it physically needs 2+ targeted reloads to address each
  failing criterion domain. The 1-ACT limit and 8-iteration limit create a guaranteed hard-stop for
  any complex story that enters DEVELOP at DEGRADING tier.
**Fix:** Amend Fix 24F DEGRADING rule:
  "ACT reload limit at DEGRADING: max 2 per story (not 1). Security-critical stories: max 3.
   Rationale: complex stories (3+ labels, score <6) need multi-criterion coverage.
   If 2 ACTs exhaust and score still <8 at iteration 8: SM-UNBLOCK fires (as Fix 25F)."
**Files:** kiro/steering/context-memory-discipline.md (Fix 24F DEGRADING block)

---

### 25H — Missing Build Verbs in STEP 0 Keyword List (🔴 High — Scenario 9)
**Source:** Dry run Scenario 9 (TRIVIAL)
**Problem:** STEP 0 routes ≤8-word inputs with BUILD keywords to TRIVIAL/MODE 3. Current keyword list
  misses the most common development action verbs: Add, Fix, Update, Extend, Insert, Integrate,
  Configure, Deploy, Refactor, Remove, Delete, Migrate, Enable, Disable, Expose, Wire, Hook.
  "Add auth middleware" (3 words) → falls through as TRIVIAL ✅ (word count triggers it).
  "Add a background job for email sending and retries" (10 words) → direct response, no routing, no tests.
  The problem is asymmetric: long sentences with action verbs bypass all routing if they exceed 8 words
  and don't contain CREATE/BUILD/IMPLEMENT/WRITE.
**Fix:** Expand STEP 0 keyword list to include:
  CREATE, BUILD, IMPLEMENT, WRITE, ADD, FIX, UPDATE, EXTEND, INTEGRATE, CONFIGURE,
  DEPLOY, REFACTOR, REMOVE, MIGRATE, ENABLE, EXPOSE, WIRE, SET UP
  Keep word-count rule (≤8 words = TRIVIAL regardless). Keyword match = STEP 1 routing for any length.
**Files:** kiro/hooks/elite-team-orchestrator.kiro.hook (STEP 0 keyword detection block)

---

### 25I — Mode 3 Build Report Format Undefined (🟢 Minor — Scenario 9)
**Source:** Dry run Scenario 9 (TRIVIAL / Mode 3)
**Problem:** Hook says "Produce Mode 3 Build Report at end" but no template, required sections,
  file path, or owning role is defined anywhere. Each execution invents a different format.
**Fix:** Add MODE 3 BUILD REPORT FORMAT to team-orchestrator-core.md:
  Format (inline, no file created — output in response):
  ```
  ## Mode 3 Build Report
  Story: <1-line description>
  Output: <file(s) or change produced>
  Tests: <test count + pass/fail>
  Labels: [<labels>]
  Time: TRIVIAL (no sprint overhead)
  ```
**Files:** kiro/steering/team-orchestrator-core.md (Mode 3 section)

---

### 25J — Role Trigger Gaps: technical_writer + sre_engineer (🟡 Medium — Scenario 6)
**Source:** Dry run Scenario 6 (DevOps/Infra)
**Problem A:** technical_writer trigger = "Sprint end" only. Mid-sprint documentation stories (runbooks,
  API docs, architecture docs) have no role assigned — they fall through to senior_engineer with no
  writing-specific skill files loaded.
**Problem B:** sre_engineer trigger = "Sprint end" only. Monitoring setup stories, SLO definition stories,
  chaos engineering stories occur during DEVELOP but sre_engineer never activates for them.
**Fix:** Add mid-sprint triggers:
  technical_writer: ALSO triggers on any story with label [cross-domain] AND title contains
    (doc|runbook|readme|guide|spec|wiki)
  sre_engineer: ALSO triggers on any story with labels [devops/monitor] OR [cross-domain] AND
    title contains (SLO|SLI|monitoring|observability|alerting|chaos)
  These are additive — Sprint end triggers remain.
**Files:** kiro/hooks/elite-team-orchestrator.kiro.hook (STEP 4 role trigger table)
           kiro/steering/skill-selection-matrix.md (role trigger column for technical_writer, sre_engineer)

---

### 25K — cross-domain Label Empty Skill Set (🟡 Medium — Scenario 6)
**Source:** Dry run Scenario 6 (DevOps/Infra)
**Problem:** A story labeled [cross-domain] ONLY has no skill files loaded — cross-domain is not in
  the skill index. Stories that span teams (docs, ADR, architectural spikes, discovery) get zero
  skill file context in their loop spec, producing empty CRITERIA blocks.
**Fix:** Add cross-domain to skill-label-index.md:
  cross-domain → shared/decision_record_template.md + shared/error_handling_strategies.md
  Add note: "cross-domain = coordination artifact. Criteria derive from story title keywords:
    doc/runbook → technical_writer skills. ADR → decision_record_template.md. spike → architect skills."
**Files:** kiro/steering/skill-label-index.md (add cross-domain entry)

---

### 25L — GATE 5 Trigger Condition Undefined (🟡 Medium — Scenario 6)
**Source:** Dry run Scenario 6 (DevOps/Infra)
**Problem:** GATE 5 (phase end review) exists in the hook but its trigger condition is never defined.
  No rule specifies what constitutes a "phase" end vs a "sprint" end. Infrastructure builds that span
  multiple sprints (Terraform setup → CI/CD → monitoring → production hardening) never reach GATE 5
  because the trigger is missing.
**Fix:** Add GATE 5 trigger rule to team-orchestrator-sprint.md:
  "GATE 5 fires when: (a) user explicitly says 'end of phase' or 'phase complete', OR
   (b) sprint-plan.md has an EPIC label and all stories in the EPIC are DONE, OR
   (c) sprint number mod 3 === 0 (every 3rd sprint = phase boundary).
   GATE 5 = architectural review: ADR ledger audit, design system audit, tech debt backlog."
**Files:** kiro/steering/team-orchestrator-sprint.md (GATE 5 trigger section)

---

### 25M — ADR Flood: No Promotion Limit or Dedup (🟡 Medium — Scenario 5)
**Source:** Dry run Scenario 5 (Full Security Sprint)
**Problem:** No rule limits how many [PROMOTE] ADRs can be emitted per sprint, and no dedup check
  prevents re-promoting a decision already in decisions.md. A security sprint can generate 4-6
  ADRs in one SM-RETRO, making decisions.md grow unbounded.
**Fix:** Add to SM-RETRO ADR section in team-orchestrator-sprint.md:
  "Max 2 new ADR promotions per sprint. If more candidates exist, queue remainder for next sprint
   with [ADR-QUEUED] tag. Before promoting, check decisions.md for existing entry on same topic
   (keyword match on title). Duplicate = skip, add [ADR-SKIP: duplicate of #N] note."
**Files:** kiro/steering/team-orchestrator-sprint.md (SM-RETRO ADR PROMOTION block)

---

### 25N — data/eda No DEVELOP Role + data_scientist Phase Fix (🔴 High — Scenario 4)
**Source:** Dry run Scenario 4 (ML Recommendation Engine)
**Problem A:** data/eda label has no DEVELOP-phase role assignment in the trigger table. data_scientist
  is wired to LAUNCH phase only. A/B test design, EDA, statistical model evaluation during DEVELOP
  has no owner role — stories fall through to senior_engineer_be with no data science skill context.
**Problem B:** data_scientist skill files (exploratory_data_analysis.md, ab_test_statistical_analysis.md)
  exist and are correct but are unreachable during DEVELOP due to phase restriction.
**Fix A:** Add data_scientist to DEVELOP trigger table:
  Trigger condition: story has label [data/eda] OR [testing/integration] AND title contains
    (A/B|experiment|statistical|model eval|EDA|analysis|hypothesis)
  data_scientist loads: exploratory_data_analysis.md + ab_test_statistical_analysis.md
**Fix B:** Update phase table — data_scientist: DEVELOP (for ml/* stories) + LAUNCH (always).
**Files:** kiro/hooks/elite-team-orchestrator.kiro.hook (STEP 4 trigger table)
           kiro/steering/skill-selection-matrix.md (data_scientist row)

---

### 25O — checkpoint.md Sprint State vs Fix Tracking Collision (🟡 Medium — Scenario 7)
**Source:** Dry run Scenario 7 (Sprint 2 Continuation)
**Problem:** checkpoint.md is used for BOTH sprint state (which sprint is active, last sprint entry)
  AND fix/implementation tracking (fix 23 added, fix 24A-G done). They share the same table.
  "Last row detection" for sprint state may read a fix-tracking row instead of a sprint row,
  causing false "fresh build" detection on session start.
**Fix:** Add a TYPE column to checkpoint.md (SPRINT | FIX | SESSION):
  Example row: | 2026-06-30 | Sprint 1 complete | DONE | sprint-plan-v1 | kiro/sprint-plan.md:END | SPRINT |
  Session start detection: scan last row WHERE TYPE=SPRINT only.
  Alternative (simpler): Add horizontal separator "---" between sprint entries and non-sprint entries.
  Recommended: TYPE column approach (more reliable for programmatic parsing).
**Files:** docs/checkpoint.md (add TYPE column header + backfill existing entries)
           kiro/steering/team-orchestrator-core.md (checkpoint read instruction: filter TYPE=SPRINT)

---

### 25P — ADR Scope Bleed Across Domains (🟡 Medium — Scenario 7)
**Source:** Dry run Scenario 7 (Sprint 2 — payments + webhooks)
**Problem:** ADR binding constraints have no domain scope. "Use jsonwebtoken v9" ADR (domain=auth)
  loads when processing a webhook signature story, constraining HMAC-SHA256 selection — a different
  auth mechanism entirely. ADRs with broad keywords (auth, security, performance) apply across
  unrelated stories in the same sprint.
**Fix:** Add DOMAIN SCOPE field to ADR format in decisions.md template:
  ```
  ### ADR-N: <title>
  Date: YYYY-MM-DD | Status: ACTIVE | Domain: <be/auth|be/api|security/pii|...> | Scope: <component|service|global>
  Decision: ...
  Binding: YES (Scope=global) | NO (Scope=component)
  ```
  ADR loading rule: load ADRs WHERE domain overlaps story labels AND scope=global. Skip domain-mismatch ADRs.
**Files:** kiro/steering/team-orchestrator-sprint.md (ADR FORMAT + loading rule)
           kiro/steering/team-orchestrator-core.md (ADR binding section)

---

### 25Q — lessons.md No Project Namespace (🟡 Medium — Scenario 7)
**Source:** Dry run Scenario 7 (Sprint 2 — lessons bleeding from Sprint 1)
**Problem:** lessons.md has no project namespace. A lesson tagged domain=security from Project A (JWT)
  loads into Project B (payments) whenever the same domain matches. Cross-project lesson bleed
  reduces lesson signal quality and may impose wrong constraints.
**Fix:** Add PROJECT field to lesson format:
  ```
  - [domain=security] [project=jwt-auth-api] JWT refresh rotation must be designed upfront.
  - [domain=payments] [project=global] Always validate webhook HMAC before processing payload.
  ```
  Lesson loading rule: load WHERE (project=global OR project=<current-project-name>) AND domain matches.
  SM-PLAN writes current project name to sprint context on sprint start (from sprint-plan.md TITLE field).
**Files:** kiro/steering/team-orchestrator-sprint.md (LESSON FORMAT + loading rule)

---

### 25R — Design System Gate: Web vs Mobile Distinction (🟢 Minor — Scenario 3)
**Source:** Dry run Scenario 3 (Mobile App)
**Problem:** Design system gate (Fix 22C) requires docs/design_system.md without distinguishing
  web component library from mobile design system (iOS HIG compliance, Material Design tokens).
  Mobile builds get blocked waiting for a web-format design system doc.
**Fix:** Amend design system gate check:
  IF sprint has mobile/* labels ONLY: gate checks docs/design_system_mobile.md (iOS HIG + Material tokens).
  IF sprint has fe/* labels ONLY: gate checks docs/design_system.md (component library).
  IF sprint has both fe/* + mobile/*: require BOTH docs.
  Either doc may be a stub (≥200 words, platform section present) to pass the gate.
**Files:** kiro/steering/team-orchestrator-sprint.md (DESIGN SYSTEM GATE block)

---

### 25S — ml_engineer Skill Coverage Gap (Traditional ML vs LLM) (🟡 Medium — Scenario 4)
**Source:** Dry run Scenario 4 (ML Recommendation Engine)
**Problem:** All ml_engineer skill files are LLM/agent-focused (agent_design_tool_use.md, graph_rag.md,
  agentic_memory_mem0.md, etc.). Traditional ML use cases (embedding models, model serving APIs,
  vector similarity, recommendation engines) have no dedicated skill file in ml_engineer.
  The be/ml label maps to files that don't cover inference serving or embedding pipeline patterns.
**Fix:** Create kiro/skills/ml_engineer/ml_serving_and_embeddings.md:
  Covers: embedding pipeline design, vector similarity scoring, model serving patterns (REST/gRPC),
  feature store design, online vs batch inference, A/B model routing, model versioning.
  Add to skill-label-index.md be/ml: + ml_engineer/ml_serving_and_embeddings.md
**Files:** kiro/skills/ml_engineer/ml_serving_and_embeddings.md (new file)
           kiro/steering/skill-label-index.md (be/ml entry + new file)

---

**SCENARIO DRY RUN STATUS (all 7 complete):**
| Scenario | Name | Status | Gaps Found |
|----------|------|--------|------------|
| 8 | Loop Hard Stop | ✅ Complete | 25F, 25G |
| 5 | Full Security | ✅ Complete | 25E(partial), 25M |
| 6 | DevOps/Infra | ✅ Complete | 25J, 25K, 25L |
| 3 | Mobile App | ✅ Complete | 25R, minor |
| 7 | Sprint 2 | ✅ Complete | 25O, 25P, 25Q |
| 4 | ML Engine | ✅ Complete | 25N, 25S |
| 9 | TRIVIAL | ✅ Complete | 25H, 25I |

**MASTER GAP (all scenarios):** 25E — Label Index 26 Filename Mismatches

**Implementation order for Fix 25 (when ready):**
1. 25E — label index rewrite (blocks everything else, critical)
2. 25F — SM-UNBLOCK protocol (loop hard stop recovery)
3. 25H — hook keyword expansion (routing correctness)
4. 25N — data_scientist DEVELOP trigger (ml/eda stories need owner)
5. 25G — DEGRADING ACT limit fix (loop convergence)
6. 25J — technical_writer + sre_engineer mid-sprint triggers
7. 25K — cross-domain skill entry
8. 25L — GATE 5 trigger condition
9. 25M — ADR flood limit + dedup
10. 25O — checkpoint TYPE column
11. 25P — ADR domain scope field
12. 25Q — lessons project namespace
13. 25S — ml_serving_and_embeddings.md (new skill file)
14. 25I — Mode 3 Build Report format
15. 25R — design system gate mobile/web split (minor)

---

## FIX 26 — FRAUD PLATFORM DRY RUN GAP CLOSURE (PENDING)

Source: docs/dry-run-2026-07-01-fraud-platform.md
Status: PENDING IMPLEMENTATION

### 26A — checkpoint.md TYPE Column Migration (🟡 Medium)
**Problem:** Fix 25O added TYPE column to checkpoint.md header but existing rows have no TYPE field. Session-start sprint-detection scanner (last row WHERE Type=SPRINT) returns nothing on pre-25O checkpoints.
**Fix:** Add migration rule to session-start logic:
  "If last row has no TYPE column → inspect Resume Vector field:
   - If Resume Vector points to sprint-plan.md or story ID → treat as TYPE=SPRINT
   - If Resume Vector points to CLAUDE.md or a fix entry → treat as TYPE=FIX
   - If ambiguous → treat as TYPE=SESSION, log warning, ask user to confirm sprint state."
  Backfill existing checkpoint.md rows by adding TYPE column value based on Task column content.
**Files:** kiro/hooks/elite-team-orchestrator.kiro.hook (STEP 4 sprint state detection block)
           docs/checkpoint.md (manual backfill of TYPE values)

### 26B — data/eda Maker Role Ambiguity (🟡 Medium)
**Problem:** data/eda stories need BOTH data_scientist (experiment design + statistical analysis) AND senior_engineer_be (assignment service implementation). Current trigger: data_scientist = maker. But A/B framework requires backend implementation that data_scientist may not own.
**Fix:** Add role-split rule for data/eda + testing/integration co-labeled stories:
  "If story has [data/eda] + [testing/integration] or [be/api] labels:
   → data_scientist = PRIMARY maker (experiment design, criteria, analysis plan)
   → senior_engineer_be = SECONDARY maker (assignment service, bucketing API, logging)
   → qa_engineer = checker (as always)
   Both roles produce loop specs for their respective domains. Criteria merged into single loop spec."
**Files:** kiro/hooks/elite-team-orchestrator.kiro.hook (STEP 5 role trigger table — co-maker note)
           kiro/steering/team-orchestrator-core.md (ROLE REGISTRY — data_scientist row)

### 26C — cross-domain Skill Gap: technical_writer Files Not Loaded (🟢 Minor)
**Problem:** cross-domain label maps to shared/decision_record_template.md + shared/error_handling_strategies.md (Fix 25K). When technical_writer is the activating role on a cross-domain story, these shared files are generic. technical_writer's own skill files (runbook templates, API doc patterns) are not loaded because they're not in the cross-domain label entry.
**Fix:** Add technical_writer role override in skill-label-index.md Section 2:
  | technical_writer | cross-domain | technical_writer/api_documentation.md (or role folder SKILL.md for template list) |
  Update cross-domain entry: "Criteria derive from story title. For doc/runbook titles → also load technical_writer role SKILL.md to discover available templates."
**Files:** kiro/steering/skill-label-index.md (Section 2 ROLE OVERRIDES — add technical_writer row)

### 26D — STRIDE Findings → Story Criteria Not Bridged (🟡 Medium)
**Problem:** STRIDE threat model produces security mitigations (e.g., "4-eyes approval rule for TB-3") but these constraints are not automatically woven into the loop spec criteria of affected stories. Developer may miss implementing a mitigation because it's in the threat model doc but not in the story's C1-C5 criteria.
**Fix:** Add STRIDE → Loop Spec bridge rule in loop-engine.md:
  "After STRIDE runs for a trust boundary, SM-PLAN must extract the mitigations for each affected story.
   For each mitigation: if a story touches that trust boundary → add corresponding criterion to its loop spec.
   Example: TB-3 mitigation '4-eyes approval rule' → FRAUD-5 loop spec gets C7: 4-eyes approval enforced.
   SM-PLAN logs: [STRIDE-BRIDGE: N mitigations → N story criteria added]"
**Files:** kiro/steering/loop-engine.md (LOOP SPEC FORMAT section — STRIDE-bridge note)
           kiro/steering/team-orchestrator-core.md (DESIGN PHASE — architect post-STRIDE step)

### 26E — Fresh Session Continuation: No Auto-Detection of Mid-Sprint CRITICAL State (🟡 Medium)
**Problem:** When CRITICAL fires mid-sprint and user starts a fresh session, the system must detect "Sprint 1 resuming at FRAUD-4" from checkpoint.md. But if user types anything other than "continue" (e.g., asks a question), the system may not recognize it's in a resuming sprint and might start fresh.
**Fix:** Add to STEP 4 session start logic:
  "If checkpoint last SPRINT row shows Status=in-progress AND stories remain in $TRACKER as PENDING:
   → AUTOMATICALLY announce: '[RESUMING: Sprint N in-progress. Next story: <ID>. Type 'continue' to proceed or 'status' for sprint state.]'
   DO NOT wait for user to discover this. Surface it proactively."
**Files:** kiro/hooks/elite-team-orchestrator.kiro.hook (STEP 4 sprint state block — add in-progress announcement)

### 26F — DEGRADING ACT Budget Doesn't Account for Cross-Story Pressure (🟢 Minor)
**Problem:** DEGRADING ACT limit is per-story (2 reloads). But if 3 consecutive stories each use 2 ACTs under DEGRADING, the cumulative token load from all those reloads accelerates toward CRITICAL. The system tracks each story's ACT budget independently but doesn't model the compound effect.
**Fix:** Add DEGRADING compound rule:
  "If 2+ consecutive stories each used max ACTs at DEGRADING tier:
   → Pre-compute remaining story count. If remaining stories * avg-tok-per-story would hit CRITICAL before sprint end:
   → Emit: [DEGRADING WARNING: N remaining stories may hit CRITICAL. Consider splitting sprint.]
   → SM can choose to proceed or scope-cut lowest-priority remaining stories."
**Files:** kiro/steering/context-memory-discipline.md (DEVELOP-PHASE DEGRADATION RULES — compound warning)

---

**Status: IMPLEMENTED 2026-07-01**

26A: hook SPRINT STATE — TYPE migration rule added; checkpoint.md backfilled.
26B: data_scientist co-maker pattern (PRIMARY=data_scientist, SECONDARY=senior_engineer_be, CHECKER=qa_engineer) in hook trigger row.
26C: technical_writer cross-domain row added to skill-label-index.md Section 2.
26D: STRIDE-BRIDGE rule in loop-engine.md LOOP SPEC FORMAT; GATE 2 checklist item in team-orchestrator-core.md.
26E: Proactive mid-sprint announcement added to hook SPRINT STATE block.
26F: Compound DEGRADING warning added to context-memory-discipline.md.

---

## Fix 27 — P0 Calibration + Runtime Enforcement (v6 Analysis)
**Source:** system-review-2026-07-01-v6-ai-pro.md | Status: PENDING

### 27A — Degradation Threshold Recalibration (🔴 Critical)
**Problem:** DEGRADING fires at ~28K tokens (14% of 200K window). Thresholds calibrated for 30K-era models. System triggers compression, ACT suppression, and fresh-session recommendations with 170K tokens still available.
**Fix:** Retarget tiers to actual 200K window:
  PEAK: < 60K tokens | GOOD: 60K-120K | DEGRADING: 120K-160K | CRITICAL: 160K+
  Drop read-count as primary trigger. Use token-estimate (tool output size as proxy) as primary.
  Log: `[TOKEN ESTIMATE: ~NKB accumulated | Tier: X]` at each DEVELOP story start.
**Files:** kiro/steering/context-memory-discipline.md (DEVELOP-PHASE DEGRADATION RULES + token math table)
           kiro/CLAUDE.md §4 (DEGRADATION TIERS table)

### 27B — Mode Detection Confidence Gate (🔴 Critical)
**Problem:** Mode 1 auto-inference commits immediately on "single sentence + ≥2 system-scale signals." False positives turn a 5-minute Mode 3 task into a 22-role enterprise sprint — most expensive failure mode in the system.
**Fix:** After mode inference, emit confidence score. If <85%, pause and confirm before committing:
  `[MODE DETECTION: Mode 1 — confidence 72%. Signals: real-time(1), platform(2). Confirm? Y/n]`
  Only commit to Mode 1 on explicit user confirmation OR confidence ≥85%.
**Files:** kiro/hooks/elite-team-orchestrator.kiro.hook (STEP 0 mode detection block)
           kiro/steering/orchestrator-routing.md (Mode 1 auto-inference rule)

### 27C — VERIFIER Execution Enforcement (🔴 Critical)
**Problem:** Loop spec VERIFIER commands (npm test, tsc, semgrep) cannot be run by the LLM in generation mode. LLMs imagine VERIFIER output → self-graded quality theater. Scores inflate regardless of actual quality.
**Fix (Claude Code runtime):** VERIFIER MUST be executed via bash tool. Loop iteration invalid without actual command output. Add: "No bash output = story NOT READY. Do not proceed to scoring."
**Fix (generation-only runtime):** Replace VERIFIER with CHECKER ROLE PASS — spawn fresh-context checker with only the story spec + generated output. Checker verifies mechanically against spec. No access to maker's reasoning.
**Files:** kiro/steering/loop-engine.md (LOOP SPEC FORMAT — VERIFIER section)

---

## Fix 28 — P1 Attention + Memory Improvements (v6 Analysis)
**Source:** system-review-2026-07-01-v6-ai-pro.md | Status: PENDING

### 28A — QUICK REFERENCE Cards at Top of Steering Files (🟡 High)
**Problem:** Fix 25-26 behaviors (co-maker split, STRIDE-bridge, compound DEGRADING, ADR scope filter, lessons namespace) are mid-to-late file content. Attention degradation means ~65-80% of these rules are silently skipped. Compliance rate: 20-35%.
**Fix:** Add 5-7 bullet QUICK REFERENCE summary at the TOP of each steering file — before all other content. Key rules in attention-strong position.
  Target files: loop-engine.md, team-orchestrator-core.md, team-orchestrator-sprint.md, context-memory-discipline.md
**Files:** All 4 steering files above (add ## QUICK REFERENCE section as first content after frontmatter)

### 28B — Explicit Lessons Scan at Role Activation (🟡 High)
**Problem:** lessons.md is loaded as background context. LLMs treat it as ambient noise, not active instruction. Lessons are present in the window but rarely consulted at decision points. Memory system is decorative.
**Fix:** At each role activation in DEVELOP, add mandatory step:
  "Before generating output: scan lessons.md for entries with domain matching current story labels. Cite any applicable lessons explicitly. If none match, log: [LESSONS: no match for labels=X,Y]"
  Makes lesson application explicit and auditable.
**Files:** kiro/steering/team-orchestrator-core.md (DEVELOP phase — role activation step)

### 28C — Skill File LOAD-TYPE Annotations (🟡 Medium)
**Problem:** 5-line compression destroys checklist-style skill files (OWASP A1-A10, WCAG criteria, STRIDE categories, crypto algorithms). Currently only 3 files have [FULL-LOAD-REQUIRED]. At least 8-10 checklist files need it.
**Fix:** Annotate each skill file header with LOAD-TYPE:
  `<!-- LOAD-TYPE: NARRATIVE -->` — 5-line compress always sufficient
  `<!-- LOAD-TYPE: CHECKLIST -->` — FULL-LOAD required for any checklist substep (auto-full-load in skill index)
  `<!-- LOAD-TYPE: HYBRID -->` — compress for context, full-load for specific protocol
  Update skill-label-index.md: auto-full-load any file annotated CHECKLIST.
**Files:** ~10 skill files + kiro/steering/skill-label-index.md (SKILL LOADING PROTOCOL)

### 28D — Label Assignment Validation Step (🟡 Medium)
**Problem:** SM-PLAN assigns labels with no validation. Wrong label → wrong skills → wrong quality bar. Ambiguous stories (JWT auth = be/auth? security/auth? security-critical?) get inconsistent labels across sessions.
**Fix:** After label assignment, SM runs 1-step self-challenge:
  "For each label assigned: what specific criterion or skill does this label add that isn't covered by the other labels? If the answer is 'nothing' → remove the label."
  Log: `[LABELS VALIDATED: [be/auth, security-critical] | removed: [] | reason: both required for JWT + STRIDE]`
**Files:** kiro/steering/team-orchestrator-core.md (SM-PLAN step — after label assignment)
           kiro/steering/loop-engine.md (LOOP SPEC FORMAT — labels section)

---

## Fix 29 — Dry Run v2 Gaps (2026-07-01)
**Source:** docs/dry-run-2026-07-01-v2-fraud-platform-fix27-28.md | Status: IMPLEMENTED 2026-07-01

### 29A — Design System Owner Not Specified (🔴 High)
**Problem:** GATE 1 THINK phase blocks on design_system.md but no role is assigned to CREATE it. design_system_gate.md says "check if it exists" — if it doesn't, it never says who makes it.
**Fix:** Add explicit creation step to THINK phase in team-orchestrator-core.md:
  - Web projects: `technical_writer` owns design_system.md (brand voice + typography), `frontend_lead` owns color/spacing/layout sections.
  - Mobile projects: `mobile_engineer` owns design_system_mobile.md.
  - Update design_system_gate.md GATE PROTOCOL: if NO → assign creation ownership explicitly.
**Files:** kiro/steering/team-orchestrator-core.md (THINK phase — role table)
           kiro/skills/shared/design_system_gate.md (GATE PROTOCOL — creation ownership section)

### 29B — CHECKLIST Token Cost Not Estimated (🟡 Medium)
**Problem:** CHECKLIST files are full-loaded (not compressed) but the skills log format only shows compressed token sum. Net: token estimates undercount context consumption when CHECKLIST files are present.
**Fix:** Update SKILL LOADING PROTOCOL log format to split out CHECKLIST cost:
  `[SKILLS: labels=[X,Y] | role=Z | files=A,B | Σ~Ntok compressed + C,D CHECKLIST ~Ntok full | Total: ~Ntok]`
  Update context-memory-discipline.md SKILL LOADING section to explicitly note CHECKLIST cost is additive.
**Files:** kiro/steering/skill-label-index.md (SKILL LOADING PROTOCOL — step 6 log format)
           kiro/steering/context-memory-discipline.md (token math reference — CHECKLIST note)

### 29C — Co-maker Loop Spec Ownership Ambiguous (🟡 Medium)
**Problem:** Co-maker stories (PRIMARY + SECONDARY) have one shared VERIFIER in the loop spec. If PRIMARY produces ML model code and SECONDARY produces API wrapper, one VERIFIER cannot validate both. Story can close with one role's work untested.
**Fix:** Co-maker stories get DUAL LOOP SPEC:
  - PRIMARY LOOP SPEC: loop criteria for PRIMARY role's deliverable (experiment design, model eval criteria)
  - SECONDARY LOOP SPEC: loop criteria for SECONDARY role's deliverable (API contract, perf criteria)
  Both specs must independently reach score ≥8. Story is DONE only when BOTH closed.
**Files:** kiro/steering/loop-engine.md (add DUAL LOOP SPEC section for co-maker stories)
           kiro/steering/team-orchestrator-core.md (co-maker pattern — add dual spec requirement)

### 29D — SM-RETRO Writes at CRITICAL Not Explicitly Permitted (🟡 Medium)
**Problem:** CRITICAL tier says "FULL STOP after current story" but lessons.md writes, checkpoint updates, and impl-decisions entries happen at SM-RETRO time. These writes are not explicitly excepted from CRITICAL's stop rule — an LLM following the rule literally would skip SM-RETRO entirely.
**Fix:** Add explicit CRITICAL-tier exception:
  "SM-RETRO writes (lessons.md, checkpoint.md, impl-decisions.md) are PERMITTED at CRITICAL — estimated ~2K tokens. These are required for session continuity and are the ONLY permitted writes after CRITICAL fires."
**Files:** kiro/steering/context-memory-discipline.md (CRITICAL tier section — add SM-RETRO exception)

### 29E — Deferred Story Resumes Without Lessons Reload (🟢 Low)
**Problem:** When a deferred story is resumed in a new session, the proactive announcement emits the story ID but does NOT re-trigger the lessons scan for that story's labels.
**Fix:** Proactive RESUMING announcement for deferred stories must include lessons scan for story labels.
**Files:** kiro/hooks/elite-team-orchestrator.kiro.hook (SPRINT STATE block)

---

## Fix 30 — Dry Run v3 Gaps (2026-07-01)
**Source:** docs/dry-run-2026-07-01-v3-four-scenarios.md | Status: IMPLEMENTED 2026-07-01

### 30A — Mobile Platform-Split VERIFIER (🟡 Medium)
**Problem:** A story with BOTH mobile/ios AND mobile/android labels gets a single VERIFIER. If the RN codebase has platform-specific branches, one test suite may not exercise both. No loop-engine guidance for split-platform verification.
**Fix:** In loop-engine.md, add rule: if story labels include BOTH mobile/ios AND mobile/android, VERIFIER must include at least one iOS-specific command (xcodebuild test or detox ios) AND one Android-specific command (gradlew test or detox android), OR the loop spec must explicitly note "unified RN codebase — single VERIFIER covers both."
**Files:** kiro/steering/loop-engine.md (FEATURE LOOP SPEC FORMAT — mobile label note)

### 30B — CHECKLIST-Heavy Sprint Early Warning (🟡 Medium)
**Problem:** CHECKLIST files are full-loaded and can add 10-20K tokens to a sprint with many security/compliance stories. No SM alert fires when cumulative CHECKLIST cost is projected to be high at sprint planning time.
**Fix:** At SM-PLAN completion, after all story skill loads are estimated, sum CHECKLIST tokens across all sprint stories. If total > 10K: emit sprint-level warning: `[SPRINT CHECKLIST BUDGET: ~NKtok full-load across M stories. Recommend: fresh session at story 4+ OR scope-cut checklist-heavy stories to Sprint 2.]`
**Files:** kiro/steering/skill-label-index.md (SKILL LOADING PROTOCOL — add sprint-level CHECKLIST sum step)
           kiro/steering/team-orchestrator-sprint.md (SM-PLAN completion — add CHECKLIST budget check)

### 30C — Load Test VERIFIER Fallback (🟡 Medium)
**Problem:** Performance criteria (p99 latency) require load test tools (k6, locust, Artillery). If unavailable in Bash runtime, the VERIFIER is BLOCKED:VERIFIER-UNEXECUTABLE with no documented fallback — story cannot close.
**Fix:** Add VERIFIER tool-type classification to loop-engine.md:
  STANDARD: unit/integration tests (npm test, pytest) — always available
  LOAD-TEST: k6/locust/Artillery — may not be available. Fallback: replace with manual benchmark criterion: "API responds in <Xms under N concurrent simulated requests via autocannon (npm i -g autocannon)"
  BROWSER: Lighthouse/Cypress — requires running app. See Fix 30G.
**Files:** kiro/steering/loop-engine.md (VERIFIER section — add tool-type classification)

### 30D — No SAML-Specific Skill File (🔴 High)
**Problem:** be/auth label resolves to security_engineer/auth_design.md (JWT/OAuth focus). SAML 2.0 specific attack vectors (XXE on SAML XML, assertion replay, ACS binding validation, IdP-initiated flow risks) have zero skill coverage. Any SSO/SAML story gets generic auth criteria.
**Fix:** Create kiro/skills/security_engineer/saml_security.md covering: XXE prevention, assertion signature validation, replay prevention (InResponseTo), ACS URL binding, IdP metadata pinning, PKCE for SAML-to-OAuth bridge.
  Update skill-label-index.md: be/auth → add saml_security.md (LOAD-TYPE: CHECKLIST).
**Files:** kiro/skills/security_engineer/saml_security.md (NEW)
           kiro/steering/skill-label-index.md (be/auth label row)

### 30E — property_based_testing.md Not Reachable from be/resilience (🟡 Medium)
**Problem:** qa_engineer/property_based_testing.md exists but is not mapped from any label in skill-label-index.md Section 1. CRDT, state machine, and protocol stories with [be/resilience] never load this skill.
**Fix:** Add be/resilience → qa_engineer/property_based_testing.md mapping in skill-label-index.md Section 1.
**Files:** kiro/steering/skill-label-index.md (be/resilience label row)

### 30F — Co-maker SECONDARY Role Not Lane-Aware (🔴 High)
**Problem:** CO-MAKER pattern in hook hardcodes SECONDARY=senior_engineer_be. When [data/eda] story is in the FE lane (analytics dashboard, data visualization), SECONDARY should be senior_engineer_fe. BE secondary on a FE story writes the wrong half of the implementation.
**Fix:** Make co-maker SECONDARY lane-aware:
  IF story labels include fe/* OR title contains (dashboard/chart/visualization/UI/component) → SECONDARY=senior_engineer_fe
  ELSE → SECONDARY=senior_engineer_be (default)
  Log: `[CO-MAKER: data_scientist+senior_engineer_fe | story=<ID> | lane=FE]`
**Files:** kiro/hooks/elite-team-orchestrator.kiro.hook (ROLE TRIGGER TABLE — data_scientist row)
           kiro/steering/team-orchestrator-core.md (QUICK REF — co-maker pattern line)

### 30G — Browser VERIFIER Tools Have No Fallback (🟡 Medium)
**Problem:** Lighthouse/Cypress require running app. No fallback documented.
**Fix:** BROWSER-REQUIRED type + start-server-and-test + RTL fallback in loop-engine.md.
**Files:** kiro/steering/loop-engine.md

---

## Fix 31 — Dry Run v4 Gaps (2026-07-01)
**Source:** docs/dry-run-2026-07-01-v4-four-scenarios.md | Status: IMPLEMENTED 2026-07-01

### 31A — Race-condition Criteria Need Concurrency-Explicit VERIFIER (🟡 Medium)
**Problem:** Sequential Jest tests don't exercise race conditions. A criterion like "concurrent add-to-cart is race-safe" passes with a sequential test that never triggers the race. The criterion exists but the VERIFIER doesn't prove it.
**Fix:** Add guidance in loop-engine.md VERIFIER section: any criterion referencing concurrency, race conditions, or concurrent access MUST use one of: (1) Promise.all with N parallel requests, (2) property-based test generating random concurrent op sequences, or (3) explicit concurrency testing library (artillery, autocannon with concurrent connections).
**Files:** kiro/steering/loop-engine.md (VERIFIER tool-type classification — add CONCURRENCY type)

### 31B — Lighthouse VERIFIER Exits 0 Without --assert Flags (🔴 High)
**Problem:** Lighthouse CLI exits 0 regardless of performance score unless --assert or --budget-path flags are used. A score of 60 produces `exit=0 | pass=Y` in the loop log — a false PASS. Every BROWSER-REQUIRED VERIFIER using Lighthouse is silently untrustworthy.
**Fix:** Mandate --assert flag in BROWSER-REQUIRED Lighthouse VERIFIER pattern:
  `npx start-server-and-test 'npm run dev' PORT 'npx lighthouse URL --output json --assert perf=N --assert a11y=N'`
  Add to loop-engine.md: "Lighthouse without --assert is BANNED. Exit code 0 is meaningless without score assertion."
**Files:** kiro/steering/loop-engine.md (BROWSER-REQUIRED VERIFIER section)

### 31C — cross-domain Label Routes to Docs Skills for Engineering Stories (🟡 Medium)
**Problem:** cross-domain label resolves to technical_writer/documentation_standards.md + runbook_template.md. SDK auto-generation, API tooling, and codegen stories use cross-domain but need engineering criteria (type safety, breaking change detection, idempotency). Docs skills are irrelevant.
**Fix:** Add sub-type note to cross-domain in skill-label-index.md:
  cross-domain/docs (default): documentation_standards + runbook_template
  cross-domain/tooling (new): add backend_lead/api_versioning.md + shared/error_handling_strategies.md
  Stories with "SDK", "codegen", "generator", "CLI tool" in title → apply cross-domain/tooling sub-type.
**Files:** kiro/steering/skill-label-index.md (cross-domain label row — add tooling sub-type)

### 31D — No Skill Files for Analytical Data Store Patterns (🟡 Medium)
**Problem:** ClickHouse, Cassandra, DynamoDB each have distinct access patterns (ClickHouse: avoid offset pagination, use materialized views; Cassandra: partition key design; DynamoDB: single-table design, GSI fan-out). Criteria for these come from engineer memory, not label-sourced skills.
**Fix:** Create kiro/skills/database_architect/analytical_datastore_patterns.md covering ClickHouse, Cassandra, DynamoDB key patterns. Add to data/pipeline label row in skill-label-index.md.
**Files:** kiro/skills/database_architect/analytical_datastore_patterns.md (NEW, LOAD-TYPE: HYBRID)
           kiro/steering/skill-label-index.md (data/pipeline label row)

### 31E — STRIDE Excess Mitigations Silently Lost (🔴 High)
**Problem:** STRIDE-BRIDGE caps at 2 criteria per story. Excess mitigations are noted as "queue excess as TECH-DEBT stories" — but no rule forces actual story creation. High-value security work (ClamAV scan, request signing, certificate rotation) disappears with no trace.
**Fix:** When STRIDE-BRIDGE defers excess mitigations, SM-PLAN MUST create explicit TECH-DEBT stories immediately. Format: story title "TECH-DEBT: [mitigation description] (deferred from STRIDE [story-ID])". Log: [STRIDE-DEFERRED: N mitigations → TECH-DEBT stories: TD-N, TD-N+1 created in backlog].
**Files:** kiro/steering/loop-engine.md (STRIDE-BRIDGE RULE — excess mitigation tracking)
           kiro/steering/team-orchestrator-core.md (SM-PLAN — add STRIDE-DEFERRED story creation step)

### 31F — No WebAuthn/FIDO2 Skill File (🔴 High)
**Problem:** WebAuthn (FIDO2) is a complex W3C authentication standard. RP ID validation, attestation verification, credential binding, and authenticator clone detection are not covered by any skill file. saml_security.md was created for SAML (Fix 30D) but the same gap exists for WebAuthn.
**Fix:** Create kiro/skills/security_engineer/webauthn_fido2.md covering: RP origin validation, attestation types, credential ID binding, authenticator data flags, clone detection (counter), resident keys, user verification requirements.
  Update skill-label-index.md: be/auth → add webauthn_fido2.md (LOAD-TYPE: CHECKLIST).
**Files:** kiro/skills/security_engineer/webauthn_fido2.md (NEW)
           kiro/steering/skill-label-index.md (be/auth label row)

### 31G — No SCIM 2.0 Skill File (🟡 Medium)
**Problem:** SCIM 2.0 (RFC 7643/7644) is the standard for directory provisioning. Protocol-specific issues (filter syntax, bulk operations, ETag concurrency, error schema) have no coverage. Systemic pattern: SAML (fixed 30D), WebAuthn (fixed 31F), SCIM still missing.
**Fix:** Create kiro/skills/backend_lead/scim_protocol.md covering: SCIM resource schema, filter query syntax, PATCH semantics (RFC 7644 §3.5.2), bulk operations, ETag concurrency control, provisioning/deprovisioning event ordering, error response schema.
  Update skill-label-index.md: be/api (when story title contains SCIM/provisioning/directory) OR add data/pipeline → scim_protocol.md mapping.
**Files:** kiro/skills/backend_lead/scim_protocol.md (NEW, LOAD-TYPE: CHECKLIST)
           kiro/steering/skill-label-index.md (be/api label row — SCIM note)

### 31H — property_based_testing.md Not Reachable from security-critical (🟡 Medium)
**Problem:** Fix 30E added property_based_testing.md to be/resilience only. ABAC policy engines, cryptographic implementations, and permission systems use [security-critical] not [be/resilience]. Property-based testing is the ideal verification approach for these (random policy sets, random input fuzzing) but is unreachable from the security-critical label.
**Fix:** Add security-critical → qa_engineer/property_based_testing.md in skill-label-index.md Section 1.
**Files:** kiro/steering/skill-label-index.md (security-critical label row)
**Problem:** Lighthouse and Cypress require a running app at a URL. Bash can execute the CLI but only if the app is already running. In CI without a running dev server, these VERIFIERs fail silently or hang. No guidance in loop-engine.md.
**Fix:** Extend VERIFIER tool-type classification (Fix 30C) with BROWSER type:
  BROWSER: Lighthouse/Cypress/Playwright — requires running app at URL.
  Before writing a BROWSER VERIFIER: note the dev server start command in the loop spec.
  Fallback: replace with component-level tests (React Testing Library) + manual Lighthouse run noted in loop spec.
  Format: `VERIFIER (BROWSER-REQUIRED): npx start-server-and-test 'npm run dev' 3000 'npx lighthouse http://localhost:3000'`
**Files:** kiro/steering/loop-engine.md (VERIFIER tool-type classification section)
**Problem:** When a deferred story is resumed in a new session, the proactive announcement emits the story ID but does NOT re-trigger the lessons scan for that story's labels. Lessons from prior sprints that are relevant to the deferred story's domain are silently skipped.
**Fix:** Proactive RESUMING announcement for deferred stories must include:
  "Run LESSONS SCAN for story labels [X, Y, Z] from docs/lessons.md before resuming DO phase."
  Log: `[DEFERRED-RESUME: story=<ID> | labels=[X,Y,Z] | lessons scan: required before DO phase]`
**Files:** kiro/hooks/elite-team-orchestrator.kiro.hook (SPRINT STATE block — deferred story resume path)

---

## Fix 38 — Dry Run v6 Gaps (2026-07-09)
**Source:** Dry Run v6 — 4-scenario audit across Scenarios A/B/C/D
**Status:** CANDIDATE (not yet implemented)

**38A — Expand confidence signal list (P0 — breaks Mode detection for enterprise prompts)**
Gap: Hook STEP 3 signal list is too narrow. "Build a multi-tenant SaaS payment platform with subscription billing, fraud detection, PCI compliance" matches only `platform` (1 signal) → confidence=LOW → unnecessary discovery. Words like `saas`, `multi-tenant`, `compliance`, `billing`, `fraud`, `dashboard`, `microservice`, `real-time`, `analytics` are obvious enterprise signals but not in the list.
Fix: In hook STEP 3 CONFIDENCE SCORING — add to system-scale signal list:
  `saas / multi-tenant / multitenant / compliance / billing / dashboard / microservice / real-time / realtime / analytics / fraud / marketplace / fintech / healthtech / edtech / legaltech`
File: kiro/hooks/elite-team-orchestrator.kiro.hook (STEP 3 signal list)

**38B — mobile_engineer not force-activated at Mode 5 for mobile platform (P1)**
Gap: discovery-engine.md conditional rule `Platform = "Mobile"` force-activates DevOps + Security but NOT mobile_engineer. A Kundli app at Mode 5 Lean gets frontend_lead (web generalist) instead of mobile_engineer (React Native / SwiftUI / Jetpack Compose specialist). Risk: web-first patterns applied to mobile.
Fix: Add to discovery-engine.md STEP 3 conditional activation rules:
  `Platform = "Mobile" or "App stores" → Force-Activate: mobile_engineer (replaces senior_engineer_fe in lean team at Mode 3/5)`
File: kiro/steering/discovery-engine.md (STEP 3 conditional activation table)

**38C — No ponytail compliance check at GATE S2 (P1)**
Gap: ponytail is wired as inclusion:always (passive) and NON-NEGOTIABLE #9 (declared), but GATE S2 pre-commit checklist has no explicit ponytail check. Over-engineered code (unnecessary abstractions, new deps for stdlib tasks) can pass GATE S2 without being flagged.
Fix: Add item 5 to GATE S2 checklist in team-orchestrator-rules.md:
  ```
  5. PONYTAIL CHECK — before commit:
     □ Walk the 7-rung ladder for each new function/class/file added this story
     □ Rung 1: Does it need to exist? Rung 2: Stdlib? Rung 3: Native platform? Rung 4: Installed dep? Rung 5: One line?
     □ Flag any rung-7 code (new custom implementation) where rung 1-6 applies → revert and rewrite
     □ Mark intentional simplifications with ponytail: comment (ceiling + upgrade path)
  ```
File: kiro/steering/team-orchestrator-rules.md (GATE S2 checklist, after item 4)

---

## Fix 37 — Ponytail Lazy Senior Dev Integration (2026-07-09)
**Source:** User request — ponytail (github.com/DietrichGebert/ponytail) prevents AI over-engineering
**Status:** IMPLEMENTED 2026-07-09

**37A — ponytail.md steering file**
Created `kiro/steering/ponytail.md` with `inclusion: always`. Contains the 7-rung lazy ladder + rules + "not lazy about" list. Auto-loads every session — all agents see it before writing code.

**37B — NON-NEGOTIABLE #9 in team-orchestrator-rules.md**
Added ponytail as NON-NEGOTIABLE #9: enforced at orchestrator level as a pipeline constraint. Violation = over-engineered output → reject, rewrite at correct rung.

**37C — discovery-engine.md plain text fix**
Changed `Present using the user_input tool` → `Output ALL 7 questions as PLAIN TEXT`. Kiro was intercepting user_input tool calls and rendering them as the native "Build a Feature / Fix a Bug" dialog. Plain text output bypasses this.

**Files:**
  - kiro/steering/ponytail.md (NEW — inclusion: always)
  - kiro/steering/team-orchestrator-rules.md (NON-NEGOTIABLE #9)
  - kiro/steering/discovery-engine.md (plain text questions fix)

---

## Fix 36 — Hook SYSTEM AUTHORITY Declaration (2026-07-03)
**Source:** Kiro native "Build a Feature / Fix a Bug / Quick Plan" dialog overriding our orchestration
**Status:** IMPLEMENTED 2026-07-03

Prepended SYSTEM AUTHORITY block to hook prompt before STEP 0. Explicitly disables:
- DO NOT create .kiro/specs/ folders — Kiro spec-driven workflow OFF
- DO NOT ask "Is this a new feature or a bugfix?" — native classification SUPPRESSED
- DO NOT use Kiro built-in requirements.md / design.md / tasks.md
- ALL artifacts go under docs/
- FILE PATHS: steering files at .kiro/steering/ and kiro/steering/ (symlink required: `ln -s .kiro kiro`)
- FORCE OVERRIDE: [LOOP] prefix bypasses STEP 0 gate

**File:** kiro/hooks/elite-team-orchestrator.kiro.hook

---

## Fix 35 — orchestrator-routing.md Dual-Routing Conflict (2026-07-03)
**Source:** Kiro loading orchestrator-routing.md as inclusion:always caused two competing routing systems
**Status:** IMPLEMENTED 2026-07-03

Changed orchestrator-routing.md from `inclusion: always` → `inclusion: manual`. The hook is now the sole router. Auto-loading orchestrator-routing.md alongside the hook created dual routing — both tried to classify the request, causing the native Kiro "feature/bugfix?" dialog to win.

Also changed discovery-engine.md from `inclusion: manual` → `inclusion: always` so discovery questions are pre-loaded. (Files with inclusion:manual cannot be loaded from hook runtime instructions in Kiro.)

**File:** kiro/steering/orchestrator-routing.md

---

## Fix 34 — Strix Security Testing Integration (2026-07-03)
**Source:** User request — extract Strix AI pentesting framework skills into security_engineer role
**Status:** IMPLEMENTED 2026-07-03

**34A — strix_pentest_methodology.md** (LOAD-TYPE: CHECKLIST, ~4,800 tok)
New skill file synthesizing Strix's complete penetration testing methodology for the security_engineer role.
Covers 8 vulnerability classes: SQL injection, IDOR, JWT/auth attacks, XSS, SSRF, race conditions, business logic flaws, BFLA.
Includes: toolchain inventory (Nuclei/sqlmap/jwt_tool/Semgrep/TruffleHog/Caido/interactsh/ZAP/ffuf/Arjun/Trivy), scan mode selection (QUICK/STANDARD/DEEP), attack patterns per vuln class, bypass techniques, OAST callback protocol, exploit chain combinations, mandatory validation protocol, CI quick scan checklist, log format.

**34B — skill-label-index.md wiring**
- Added `strix_pentest_methodology.md` to `security/review` label (loads alongside api_security_owasp_top10.md)
- Added new `security/pentest` label → strix_pentest_methodology.md + api_security_owasp_top10.md
- Added PENTEST SCAN MODE SELECTION inline rule: story context drives QUICK/STANDARD/DEEP

**Files:**
  - kiro/skills/security_engineer/strix_pentest_methodology.md (NEW — LOAD-TYPE: CHECKLIST)
  - kiro/steering/skill-label-index.md (security/review + new security/pentest label)

---

## OPERATING RULES (before touching any fix below)

> **Discipline tiers (PEAK/GOOD/DEGRADING/CRITICAL) are defined in `kiro/steering/context-memory-discipline.md`. Do not redefine them elsewhere.**

### SKILL EVALUATION DISCIPLINE (from Superpowers methodology)
Before modifying ANY skill file in `kiro/skills/`:
1. Run at least 3 adversarial sessions against the current version — document what breaks
2. Make the change
3. Run 3 adversarial sessions against the modified version — document the delta
4. Only merge if the delta is positive. No intuition-based edits. Evidence required.

### LESSONS.MD CONFIDENCE SCORING
Every entry in `docs/lessons.md`:
```
## [YYYY-MM-DD] — [pattern title]
**Type:** Mistake | Correction | Rule | Anti-pattern
**Confidence:** low | medium | high
**Trigger:** [situation that activates this lesson]
**Body:** [what happened and what to do instead]
**Review:** [date of last confirmation / upgrade]
```
- `low` → new entry, not yet confirmed
- `medium` → confirmed in 3+ sessions
- `high` → promote to permanent CLAUDE.md operating rule

---

## Fix 33 — IAM Sprint Budget Pre-Warning + project-index OQ-Resolved Prompt (2026-07-03)
**Source:** Dry Run v5 — 2 minor gaps found
**Status:** CANDIDATE (not yet implemented)

**33A — IAM/Security-Heavy Sprint CHECKLIST Budget Pre-Warning**
Gap: IAM platforms with WebAuthn + SAML + SCIM can consume ~8,300 tok in just 3 stories, leaving only 1,700 tok headroom before Fix 30B split warning fires. The warning fires REACTIVELY (after SM-PLAN), causing disruption.
Fix: In SM-PLAN, after loading PRD label-map — if feature list contains ≥3 features labeled [be/auth] or [security-critical], emit PROACTIVELY:
  `[SECURITY-HEAVY PRD: ≥3 auth/security-critical features detected. CHECKLIST budget risk. Recommend: max 3 security-critical stories/sprint OR scope-split auth sprint from feature sprint.]`
File: kiro/steering/team-orchestrator-core.md SM-PLAN section

**33B — project-index.md Auto-Update Prompt on OQ Resolution**
Gap: When user resolves open questions mid-session (e.g., answers OQ-1 and OQ-2 in conversation), the SM does not proactively prompt to update project-index.md. Gate status becomes stale — project-index still shows BLOCKED even though questions are answered.
Fix: In SM-PLAN, when doc-to-doc flow reads project-index.md and detects open questions that are ALREADY ANSWERED in the current session context:
  emit: `[OQ-RESOLVED: OQ-1, OQ-2 resolved in this session — update /docs/foundation/project-index.md §2 (gate status) + §3 (question status) BEFORE DEVELOP starts. Assign: technical_writer or SM.]`
File: kiro/steering/team-orchestrator-core.md DOC-TO-DOC FLOW PROTOCOL section

---

## Fix 32 — Doc Knowledge Architecture: Source of Truth Framework (2026-07-03)
**Source:** Gap analysis against 6-doc framework (PRD/TRD/App Flow/UI-UX Brief/Backend Schema/Impl Plan)
**Status:** IMPLEMENTED 2026-07-03

**Root problem:** The system produces all 6 foundation docs but treats them as black boxes. Agents write them with no structural template → sections are missing, vague, or agent-interpreted. Docs don't flow into each other — SM-PLAN re-derives labels from PRD prose, architect re-derives trust boundaries from architecture prose, database_architect designs schema without query patterns. The result: every sprint has invisible decisions made by the agent instead of the docs.

**Fix philosophy:** Every doc must be (1) structured enough for an agent to write without guessing, (2) precise enough to feed the next doc directly, (3) validated at the gate it belongs to — not just existence-checked.

---

### 32A — PRD Has No Structural Template — Agent Writes Freeform (🔴 Critical)
**Problem:** The `cto` role produces `/docs/foundation/prd.md` but no skill enforces what sections it must contain. SM-PLAN infers labels from prose (~30% error rate on ambiguous features). Success metrics are vague. Anti-goals have no rationale. Open questions are buried or missing entirely.
**Fix:** Create `kiro/skills/cto/prd_template.md` — mandatory sections:
  1. App Overview (name, one-liner, target users, problem statement)
  2. Feature List with confidence levels: MUST / SHOULD / NICE-TO-HAVE
  3. User Stories in GIVEN/WHEN/THEN format (not "As a user I can…")
  4. Success Metrics — testable form: "p95 load time < 2s", "7-day retention ≥ 40%", NOT "users find it useful"
  5. Anti-Goals with reasons: "NOT in v1: real-time notifications — WebSocket adds 3 sprints, deferred to v2"
  6. **Kiro Label Map** — explicit table: Feature → Labels → Owning Role(s)
  7. Open Questions — unresolved decisions that block design (feeds 32F gate)
  8. Version + changelog header
  SM-PLAN reads the Label Map section FIRST. If Label Map section is missing → SM-PLAN BLOCKS and requests cto to add it before sprint planning begins.
  Log: `[PRD-LABEL-MAP: N features → M labels resolved. Open questions: K — review before SM-PLAN.]`
**Files:** kiro/skills/cto/prd_template.md (NEW — LOAD-TYPE: CHECKLIST), kiro/steering/team-orchestrator-core.md (SM-PLAN step: reads PRD Label Map first)

---

### 32B — TRD Has No Constraint Levels or Trust Boundary Map (🟡 Medium)
**Problem:** The architect produces architecture.md but tech decisions don't distinguish HARD CONSTRAINTS (existing infra, contracts) from PREFERRED choices (can be changed). STRIDE fires correctly but trust boundaries must be re-derived from architecture prose every time — architect has to re-read the full doc to find them.
**Fix:** Create `kiro/skills/architect/trd_template.md` — mandatory sections:
  1. Tech Stack — each entry tagged: HARD CONSTRAINT | PREFERRED | EXPERIMENTAL
     Format: `PostgreSQL — HARD CONSTRAINT (existing prod DB, no migration budget this phase)`
  2. **Trust Boundary Map** — explicit table pre-populated before STRIDE runs:
     `| Boundary | From | To | Primary Threats | STRIDE letter |`
     architect fills this at TRD creation. STRIDE consumes it directly — no re-derivation.
  3. Skill File Hints per component (feeds SM-PLAN label assignment):
     `Auth module → be/auth + security-critical | saml_security.md if SSO required`
  4. ADR Index — list of ADR IDs and one-line decisions (links to /docs/phase-N/adrs/)
  5. Non-functional requirements: performance budget, scalability targets, security posture level
  6. Open Questions — unresolved architectural decisions (feeds 32F gate)
  7. Version + changelog header
  GATE 2 checklist adds: Trust Boundary Map populated? Constraint levels on all tech decisions?
  Log: `[TRD-VALIDATED: N tech decisions (X HARD / Y PREFERRED) | Trust boundaries: M | ADRs: K]`
**Files:** kiro/skills/architect/trd_template.md (NEW — LOAD-TYPE: CHECKLIST), kiro/steering/team-orchestrator-sprint.md (GATE 2 checklist additions)

---

### 32C — App Flow Is Not a First-Class Artifact (🔴 Critical)
**Problem:** App Flow is distributed across stories with fe/* labels. Error states, empty states, and edge cases are routinely missed because no single doc forces them to be declared upfront. GATE 2 does not check for an App Flow document. Agents derive screen behavior from PRD user stories — which were written in vague narrative form.
**Fix:** Create `kiro/skills/technical_writer/app_flow_template.md` — mandatory output: `/docs/foundation/app-flow.md`
  Structure per screen:
  ```
  ## Screen: [Name] — Route: [/path]
  Owner: [role]
  GIVEN: [precondition]
  WHEN: [user action / trigger]
  THEN: [expected result, including URL change / API call / state update]

  ERROR STATE: [what happens when X fails — message, recovery path]
  EMPTY STATE: [what shows when no data exists — illustration, CTA]
  SUCCESS STATE: [confirmation, next screen, animation]
  VERIFIER ANCHOR: [bash command or test that proves this state works]
  ```
  Add `/docs/foundation/app-flow.md` to GATE 2 checklist — GATE stays RED until it exists with all screens documented.
  `technical_writer` owns creation. `frontend_lead` reviews for feasibility.
  SM-PLAN reads App Flow GIVEN/WHEN/THEN per screen → converts to story acceptance criteria directly (no re-derivation).
  Log: `[APP-FLOW: N screens | M error states | K empty states | GATE 2: ✅]`
**Files:** kiro/skills/technical_writer/app_flow_template.md (NEW — LOAD-TYPE: CHECKLIST), kiro/steering/team-orchestrator-sprint.md (GATE 2: app-flow.md required)

---

### 32D — Design System Gate Checks Existence Not Structure (🟡 Medium)
**Problem:** Fix 14A/29A created design_system_gate.md and enforced creation ownership. But the gate only checks that the file exists — not that it contains usable structured content. Agents still interpret "modern blue accent" differently each session. No component inventory forces frontend_lead to list reusable components upfront.
**Fix:** Update `kiro/skills/shared/design_system_gate.md` — add mandatory structure validation:
  Required sections checklist (GATE 2 validation):
  - [ ] Design Tokens as YAML: colors (all variants), typography (size/weight/line-height), spacing scale, border-radius, shadow scale
  - [ ] Component Inventory: every reusable component listed with variants + states (loading/disabled/error)
  - [ ] Core Web Vitals targets per page: LCP / CLS / FID targets — feeds fe/perf loop criteria directly
  - [ ] WCAG compliance level per component type: inputs (AA minimum), alerts (AA), data tables (AAA target)
  - [ ] Responsive breakpoints: exact px values + behavior at each breakpoint
  GATE 2 does not pass until ALL 5 sections are present and non-empty.
  Log: `[DESIGN-GATE: tokens ✅ | components ✅ | CWV targets ✅ | a11y levels ✅ | breakpoints ✅ — GATE 2 CLEARED]`
**Files:** kiro/skills/shared/design_system_gate.md (update — add structure validation checklist)

---

### 32E — Backend Schema Lacks Query-First Design and Proactive GDPR Classification (🔴 Critical)
**Problem:** `database_architect` creates schema tables with columns and types but no query patterns. Index design decisions are made later — often incorrectly — when senior_engineer_be can't find indexed columns. Volume estimates are absent, so the agent defaults to Postgres for everything regardless of scale. GDPR column classification is reactive (only fires on be/pii label) not proactive at schema creation.
**Fix:** Update `kiro/skills/database_architect/database_schema_design.md` — add mandatory sections:
  Per table:
  1. **Query Patterns** (top 3 for each table) — format:
     `Lookup by email: SELECT * FROM users WHERE email = $1 → INDEX: users(email) UNIQUE`
     `Admin range filter: WHERE status = $1 AND created_at BETWEEN $2 AND $3 → COMPOSITE INDEX: (status, created_at)`
  2. **Volume Estimate** — rows at launch / 6 months / 12 months
     Triggers: >1M rows → evaluate ClickHouse or partitioning. >10K writes/sec → evaluate Redis or DynamoDB.
     Log: `[SCHEMA-VOLUME: table=X | 12mo estimate=Y rows | recommendation: <Postgres/ClickHouse/Redis>]`
  3. **GDPR Column Classification** — per column at creation time (not deferred to be/pii story):
     PII:HIGH (encrypted at rest, excluded from logs) | PII:MEDIUM (masked in non-prod) | PII:NONE
     If ANY column is PII:HIGH → automatically add [be/pii] label to all stories touching that table.
  4. **STRIDE Annotations** per table:
     `users table — T: account enumeration via timing | I: PII exposure in logs`
     Pre-populates architect STRIDE surface. No re-derivation needed.
  Log: `[SCHEMA-COMPLETE: N tables | query patterns: ✅ | volumes: ✅ | GDPR: ✅ | STRIDE annotations: ✅]`
**Files:** kiro/skills/database_architect/database_schema_design.md (update — add 4 mandatory sections)

---

### 32F — No Project Index File — Hook Starts Blind (🟡 Medium)
**Problem:** On session start, the hook reads checkpoint.md to resume. There is no master index that tells the agent which foundation docs exist, which open questions are unresolved, and which gates are currently blocked. Agents start sessions by scanning checkpoint.md and must re-derive project state from it.
**Fix:** Create `kiro/skills/technical_writer/project_index_template.md` — mandatory output: `/docs/foundation/project-index.md`
  Structure:
  ```
  ## Foundation Docs Status
  | Doc | Path | Status | Gate | Owner | Last Updated |
  | PRD | /docs/foundation/prd.md | ✅ Complete | GATE 1 | cto | 2026-07-01 |
  | TRD | /docs/foundation/architecture.md | ✅ Complete | GATE 2 | architect | 2026-07-01 |
  | App Flow | /docs/foundation/app-flow.md | 🔴 Missing | GATE 2 | technical_writer | — |
  ...

  ## Open Questions (unresolved — blocks listed gate)
  - [ ] SAML SSO or OAuth-only? → blocks GATE 2 (architect needs for TRD trust boundary)
  - [ ] ClickHouse or Postgres for analytics? → blocks Sprint 1 schema story
  - [ ] Mobile v1 or web-only? → blocks PRD label map (mobile/* labels TBD)

  ## Current Gate
  GATE: 2 | Status: 🔴 BLOCKED | Blocker: app-flow.md missing + 2 open questions unresolved

  ## Doc Conflict Log
  (filled when docs disagree — see 32G)
  ```
  Hook reads `/docs/foundation/project-index.md` on session start BEFORE checkpoint.md.
  If open questions exist for current gate → emit: `[GATE BLOCKED: N open questions unresolved. List: <questions>. Resolve before proceeding.]`
  `technical_writer` owns creation and maintenance of project-index.md.
  Log: `[PROJECT-INDEX: gate=N | docs=X/6 complete | open questions=K | blockers=M]`
**Files:** kiro/skills/technical_writer/project_index_template.md (NEW), kiro/hooks/elite-team-orchestrator.kiro.hook (session start: read project-index.md before checkpoint.md)

---

### 32G — No Doc Conflict Resolution Protocol (🟡 Medium)
**Problem:** PRD says "use OAuth." TRD says "SAML for enterprise SSO." Schema has a `saml_assertions` table. Stories label is [be/auth]. Agent has 4 conflicting signals and no rule for which wins. Currently resolves by guessing (usually picks the most recent doc it read).
**Fix:** Add Doc Precedence Protocol to team-orchestrator-core.md:
  ```
  DOC CONFLICT RESOLUTION (Fix 32G):
  When two foundation docs contradict each other:
  1. WHAT to build → PRD wins (PRD is the product contract)
  2. HOW to build it → TRD wins (TRD is the technical contract)
  3. Data shape / schema → Backend Schema wins (schema is the data contract)
  4. UI behavior / states → App Flow wins (App Flow is the UX contract)
  When conflict is found: DO NOT guess. Log conflict to project-index.md Doc Conflict Log:
    `[DOC-CONFLICT: PRD says OAuth | TRD says SAML | Resolution needed by: architect + cto | Blocker: SM-PLAN]`
  SM-PLAN is BLOCKED until conflict is resolved and logged.
  ```
  Conflicts surface at SM-PLAN time (when all docs are in context). Never silently resolved by agent.
  Log: `[DOC-CONFLICT-SCAN: N docs reviewed | conflicts found: K | all resolved: ✅/🔴]`
**Files:** kiro/steering/team-orchestrator-core.md (SM-PLAN step: add conflict scan before sprint creation)

---

### 32H — GATE 2 Checks Artifact Existence Only — Not Structural Completeness (🔴 Critical)
**Problem:** GATE 2 (pre-build gate / SM-GATE) checks that architecture.md and design_system.md exist. It does NOT check that they have the required sections from 32A-32F. An empty design_system.md or a PRD without a Label Map passes GATE 2. This means structural gaps in foundation docs are invisible until mid-sprint when they cause agent confusion.
**Fix:** Update `prebuild_documentation_gate.md` skill (SM-GATE) — add structural completeness checks:
  GATE 2 checklist additions:
  - [ ] PRD: Label Map section present and non-empty?
  - [ ] PRD: All user stories in GIVEN/WHEN/THEN format?
  - [ ] PRD: Success metrics are testable (numbers, not adjectives)?
  - [ ] TRD: All tech decisions have constraint level (HARD/PREFERRED)?
  - [ ] TRD: Trust Boundary Map populated (≥1 boundary)?
  - [ ] App Flow: /docs/foundation/app-flow.md exists with all screens?
  - [ ] App Flow: Every screen has ERROR STATE + EMPTY STATE documented?
  - [ ] Design System: All 5 sections present (tokens/components/CWV/a11y/breakpoints)?
  - [ ] Backend Schema: Query patterns present on all tables?
  - [ ] Backend Schema: Volume estimates on all tables?
  - [ ] Backend Schema: GDPR column classification complete?
  - [ ] Project Index: /docs/foundation/project-index.md exists?
  - [ ] Project Index: Zero unresolved open questions for current gate?
  ANY red item → GATE 2 stays RED. Named role assigned to fix each gap.
  Log: `[GATE 2 STRUCTURAL CHECK: N/M items pass | Red: <list of gaps + owning roles>]`
**Files:** kiro/skills/scrum_master/prebuild_documentation_gate.md (update — add structural completeness checklist), or kiro/steering/team-orchestrator-sprint.md (GATE 2 section)

---

### 32I — Docs Don't Flow Into Each Other — Agents Re-Derive Everything (🟡 Medium)
**Problem:** PRD Label Map exists (after 32A) but SM-PLAN doesn't know to read it first. TRD Trust Boundary Map exists (after 32B) but architect starts STRIDE from scratch. Schema query patterns exist (after 32E) but database_architect ignores them when designing indexes. App Flow GIVEN/WHEN/THEN exists (after 32C) but loop specs are written from PRD user stories. Each agent re-reads and re-derives from the wrong source.
**Fix:** Add Doc-to-Doc Flow Rules to team-orchestrator-core.md (explicit read-order per role activation):
  ```
  DOC-TO-DOC FLOW PROTOCOL (Fix 32I):
  SM-PLAN:
    Step 1 → READ /docs/foundation/prd.md#label-map FIRST (not PRD prose)
    Step 2 → READ /docs/foundation/app-flow.md (loop spec acceptance criteria come from here)
    Step 3 → READ /docs/foundation/project-index.md (check open questions, current gate)
    Do NOT infer labels from PRD prose if Label Map section exists.

  architect (STRIDE):
    Step 1 → READ /docs/foundation/architecture.md#trust-boundary-map (pre-populated in TRD)
    STRIDE runs against this map — does NOT re-derive boundaries from architecture prose.

  database_architect (index design):
    Step 1 → READ schema query patterns section (already written in 32E)
    Index design is derived FROM query patterns — not from column names or guessing.

  loop-engine (loop spec creation):
    Step 1 → READ /docs/foundation/app-flow.md for the story's screen(s)
    GIVEN/WHEN/THEN from App Flow → become criteria directly (scored 1-10 each iteration)
    Do NOT rewrite acceptance criteria from scratch if App Flow has them.
  ```
  Log: `[DOC-FLOW: role=<X> | read-order=<prd-label-map→app-flow→project-index> | source-of-truth confirmed]`
**Files:** kiro/steering/team-orchestrator-core.md (add DOC-TO-DOC FLOW PROTOCOL section)

---

### 32J — No Security Foundation Document — Security Is Reactive Not Declared (🔴 Critical)
**Problem:** The system has excellent per-story security: STRIDE per trust boundary, saml_security.md and webauthn_fido2.md CHECKLISTs, OWASP for be/auth stories. But there is no `/docs/foundation/security-posture.md` — a project-level security declaration. This causes three critical failures:
  1. Auth mechanism is never declared upfront. skill-label-index.md be/auth says "load saml_security.md OR webauthn_fido2.md — load only the matching one." But nothing tells the agent WHICH mechanism THIS project uses. Every be/auth story either loads both (wasteful) or guesses wrong.
  2. Compliance requirements (GDPR/HIPAA/SOC2/PCI-DSS) surface mid-sprint when the first PII story appears. By then the schema is already wrong, the encryption choices are already made, and rework is expensive.
  3. STRIDE has no baseline security posture context. architect runs STRIDE with no knowledge of whether this is a startup MVP (risk appetite: medium) or a healthcare platform (risk appetite: zero). Threat model depth is inconsistent.

**Fix:** Create `kiro/skills/security_engineer/security_posture_template.md` — mandatory output: `/docs/foundation/security-posture.md`

  Mandatory sections:

  **Section 1 — Security Posture Level**
  ```
  POSTURE: LOW (startup MVP, no regulated data) |
           MEDIUM (B2B SaaS, business data, SOC2 target) |
           HIGH (regulated: HIPAA / PCI-DSS / ISO27001 / FedRAMP)
  ```
  This single field changes agent behavior system-wide:
  - LOW → STRIDE runs at threat-identification depth only, mitigations deferred to TECH-DEBT
  - MEDIUM → STRIDE full depth, security_engineer DEVELOP pass on [security-critical] stories
  - HIGH → STRIDE mandatory on ALL trust boundaries, security_engineer reviews ALL be/* stories, pen test schedule required

  **Section 2 — Auth Mechanism Declaration** (resolves be/auth CHECKLIST ambiguity)
  ```
  PRIMARY_AUTH: OAuth 2.0 (Google/GitHub) | SAML 2.0 | WebAuthn/Passkeys | API Key | JWT (custom)
  MFA_REQUIRED: none | TOTP | WebAuthn
  SSO_PROTOCOL: none | SAML 2.0 | OIDC
  MACHINE_AUTH: none | API Key | mTLS | service account JWT
  ```
  skill-label-index.md be/auth rule: read security-posture.md Section 2 → load ONLY the declared mechanism's CHECKLIST.
  Log: `[AUTH-POSTURE: primary=OAuth2 | mfa=WebAuthn | sso=none → loading: auth_design.md + webauthn_fido2.md ONLY]`

  **Section 3 — Compliance Requirements**
  ```
  GDPR: yes/no | scope: EU users / all users
  HIPAA: yes/no | data type: PHI (protected health info)
  PCI-DSS: yes/no | level: 1/2/3/4
  SOC2: yes/no | type: I / II | target date: YYYY-MM
  ISO27001: yes/no
  ```
  Auto-label rules when compliance is declared:
  - HIPAA=yes → ALL [data/*] stories get [security-critical] auto-added
  - PCI-DSS=yes → ALL [be/api] stories touching payment data get [security-critical] + saml_security.md or equivalent
  - SOC2=yes → ALL [devops/*] stories get [operations/compliance-tracking] skill load
  Log: `[COMPLIANCE-AUTO-LABEL: HIPAA=yes → +[security-critical] on 4 data/* stories]`

  **Section 4 — Data Classification Schema** (feeds 32E GDPR column tagging)
  ```
  PII:HIGH     → real name, email, phone, SSN, DOB, biometric — encrypted at rest, excluded from logs
  PII:MEDIUM   → username, IP address, device ID — masked in non-prod, pseudonymised
  PII:NONE     → timestamps, feature flags, analytics events (non-identifying)
  PHI          → (HIPAA only) diagnosis, medication, treatment records — full PHI controls
  PCI          → (PCI-DSS only) card number, CVV, expiry — NEVER stored, tokenized via Stripe/etc
  INTERNAL     → business data, not personal — standard access controls
  ```
  database_architect reads this schema when classifying columns (32E). One definition, used everywhere.

  **Section 5 — Encryption Standards**
  ```
  AT_REST:      AES-256-GCM | ChaCha20-Poly1305
  IN_TRANSIT:   TLS 1.3 minimum (TLS 1.2 with approved ciphers only)
  KEY_MGMT:     AWS KMS | HashiCorp Vault | GCP KMS | (none = flag as TECH-DEBT)
  PASSWORD_HASH: bcrypt (cost≥12) | argon2id | scrypt
  TOKEN_SIGNING: RS256 | ES256 (HS256 = banned for multi-service)
  ```

  **Section 6 — Secrets Management Standard**
  ```
  SECRET_STORE:  AWS Secrets Manager | HashiCorp Vault | GCP Secret Manager
  BANNED:        .env files in repo | hardcoded credentials | process.env in prod without rotation
  ROTATION:      automatic (30-day) | manual (quarterly) | none (flag as TECH-DEBT)
  ```
  If SECRET_STORE=none or .env in prod: automatically create a [security-critical, tech-debt] story before SM-PLAN proceeds.

  **Section 7 — Security Testing Requirements**
  ```
  SAST:         semgrep in CI (required for MEDIUM/HIGH) | bandit (Python) | eslint-security
  DAST:         OWASP ZAP quarterly | none
  PEN_TEST:     annually | at launch | never
  DEPENDENCY_SCAN: npm audit / snyk / dependabot — in CI
  SECRET_SCAN:  gitleaks / trufflehog — pre-commit hook
  ```
  loop-engine.md VERIFIER for [security-critical] stories: if SAST is declared, semgrep run is a STANDARD VERIFIER item on ALL security-critical stories — not optional.

  **Section 8 — API Security Standards**
  ```
  RATE_LIMITING:    per-IP (default 100/min) + per-user (default 1000/min)
  INPUT_VALIDATION: strict schema validation on all endpoints (ajv / zod / pydantic)
  OUTPUT_ENCODING:  HTML encode all user-controlled output
  CORS_POLICY:      allowlist only (no wildcard in prod)
  CONTENT_SECURITY: CSP headers required on all HTML responses
  ```
  be/api stories: loop-engine.md automatically adds rate-limit and input-validation criteria if security-posture.md Section 8 is present.

  **GATE 2 additions:**
  - `/docs/foundation/security-posture.md` required before GATE 2 passes
  - `security_engineer` owns creation. `architect` reviews Section 5+6. `cto` approves posture level.
  - GATE 2 STRUCTURAL CHECK (32H) includes: ALL 8 security-posture.md sections non-empty?

  **Flow into other docs:**
  - Section 2 (auth) → resolves be/auth skill-label-index.md ambiguity — no more "load the matching one" guessing
  - Section 3 (compliance) → auto-labels stories at SM-PLAN time
  - Section 4 (data classification) → feeds 32E schema GDPR column tagging
  - Section 7 (SAST) → adds semgrep to VERIFIER on all [security-critical] stories
  - Section 1 (posture level) → tells architect STRIDE depth + tells STRIDE-DEFERRED (32E Fix 31E) priority level

  **Doc conflict rule (feeds 32G):** security-posture.md wins over TRD on all security-specific decisions. If TRD says "JWT with HS256" but security-posture.md says "HS256 banned" → security-posture.md is the contract. Log conflict and block SM-PLAN.

  Log: `[SECURITY-POSTURE: level=HIGH | auth=SAML+WebAuthn | compliance=HIPAA+SOC2 | GATE 2: ✅]`
**Files:**
  - kiro/skills/security_engineer/security_posture_template.md (NEW — LOAD-TYPE: CHECKLIST)
  - kiro/steering/skill-label-index.md (be/auth: read security-posture.md Section 2 before loading CHECKLISTs)
  - kiro/steering/team-orchestrator-core.md (SM-PLAN: read security-posture.md Section 3 for auto-label rules)
  - kiro/steering/loop-engine.md (be/api criteria: add rate-limit + input-validation from Section 8 if posture doc present)
  - kiro/steering/team-orchestrator-sprint.md (GATE 2: security-posture.md structural check)

---

### 32K — No Testing Foundation Document — Test Strategy Re-Invented Per Story (🔴 Critical)
**Problem:** `qa_engineer` has 6 skill files and loop-engine.md has VERIFIER type classification (Fix 30C). But there is no `/docs/foundation/testing-strategy.md`. This causes 4 compounding failures:
  1. VERIFIER tool choice is guessed per story. Fix 30C says "if k6 unavailable → autocannon fallback." But nothing declares whether THIS project uses k6, autocannon, or Artillery. Fallback fires when it shouldn't.
  2. Coverage targets don't exist. `npm test` exits 0 with 12% coverage. VERIFIER passes. Story closes. Ship.
  3. E2E scope creeps. No list of critical user journeys = Playwright runs on every screen = slow CI, brittle tests, nobody maintains them.
  4. Test data strategy is reinvented per sprint. One sprint uses factories, next uses fixtures, next hardcodes values. `qa_engineer/test_data_management.md` has no baseline to anchor against.
**Fix:** Create `kiro/skills/qa_engineer/testing_strategy_template.md` — mandatory output: `/docs/foundation/testing-strategy.md`

  **Section 1 — Test Pyramid Declaration**
  ```
  UNIT:        jest | pytest | go test | vitest — target coverage: ≥N%
  INTEGRATION: supertest | testcontainers — target: all API contracts covered
  E2E:         Playwright | Cypress — scope: critical journeys ONLY (listed in Section 5)
  CONTRACT:    Pact | none — required if: microservices or 3rd-party APIs
  VISUAL:      Percy | Chromatic | none — required if: component library exists
  PROPERTY:    fast-check | hypothesis | none — required if: be/resilience or security-critical
  LOAD:        k6 | autocannon | Artillery — required if: be/perf stories in roadmap
  MOBILE:      Detox | XCTest/Espresso | none — required if: mobile/* labels in roadmap
  ```
  loop-engine.md VERIFIER type selection reads this — no guessing. If LOAD=k6, never falls to autocannon unless k6 unavailable.

  **Section 2 — Coverage Targets**
  ```
  MINIMUM_LINE:    80% (or "not enforced" — must be explicit)
  MINIMUM_BRANCH:  70%
  COVERAGE_TOOL:   istanbul | coverage.py | go cover
  COVERAGE_IN_CI:  yes | no
  EXCLUSIONS:      /migrations/*, /scripts/*, /mocks/*
  ```
  VERIFIER format for STANDARD stories: if COVERAGE_IN_CI=yes →
  `npm test -- --coverage --coverageThreshold='{"global":{"lines":80,"branches":70}}'`
  Coverage drop = VERIFIER exits non-zero = story cannot close. No exceptions.

  **Section 3 — Tool Decisions (resolved once, referenced everywhere)**
  ```
  UNIT_FRAMEWORK:   jest | pytest | go test | vitest
  MOCK_LIBRARY:     jest.mock | sinon | unittest.mock | testify
  API_TEST_TOOL:    supertest | httpx | requests
  E2E_TOOL:         Playwright | Cypress
  LOAD_TEST_TOOL:   k6 | autocannon | Artillery
  CONTRACT_TOOL:    Pact | none
  ```
  Fix 30C VERIFIER fallback logic uses this. If LOAD_TEST_TOOL=k6 here → k6 is primary, autocannon is fallback ONLY if k6 binary missing.

  **Section 4 — Test Data Strategy**
  ```
  APPROACH:       factory-boy | fishery | fixtures | seeds | mocks
  NON_PROD_DATA:  synthetic only | anonymized prod | none (none + HIPAA = auto-flag)
  TEST_DB:        docker container | separate schema | in-memory
  CLEANUP:        truncate-per-test | transaction-rollback | none
  ```
  `qa_engineer/test_data_management.md` inherits from this. No re-derivation per sprint.
  If NON_PROD_DATA=none AND security-posture.md has HIPAA=yes → BLOCK SM-PLAN, create TECH-DEBT story for test data anonymization.

  **Section 5 — Critical User Journey List (E2E scope boundary)**
  ```
  E2E runs ONLY on these journeys (not every screen):
  1. [Journey name]: [brief description]
  2. [Journey name]: [brief description]
  ...
  ```
  loop-engine.md: E2E VERIFIER required ONLY on stories that touch a listed journey.
  Stories not touching listed journeys → E2E VERIFIER not required (saves CI time, prevents sprawl).
  SM-PLAN flags a story as "E2E-REQUIRED" if it modifies a critical journey path.

  **Section 6 — Story Done Definition (testing dimension)**
  ```
  STANDARD stories:    unit tests passing + coverage threshold met + VERIFIER exit 0
  SECURITY-CRITICAL:   above + SAST clean + property-based test passing
  E2E-REQUIRED:        above + Playwright/Cypress journey test passing
  LOAD-REQUIRED:       above + k6/autocannon benchmark within target
  MODE 3 TRIVIAL:      VERIFIER exit 0 only (no coverage requirement — by design)
  ```
  SM-RETRO Sprint Discipline Card row "VERIFIER compliance" references this definition — not loop-engine.md's generic rule.

  **Section 7 — Accessibility Testing Standard**
  ```
  WCAG_LEVEL:    AA | AAA
  A11Y_TOOL:     axe-core | none
  A11Y_IN_CI:    yes | no (if yes: axe violations block merge)
  ```
  fe/a11y stories inherit WCAG_LEVEL from here — not re-declared per story.
  Lighthouse --assert accessibility target (Fix 31B) uses WCAG_LEVEL from this doc.

  **Section 8 — Security Testing Integration**
  ```
  SAST_TOOL:        semgrep | bandit | eslint-security | none
  SAST_IN_CI:       yes | no
  DEPENDENCY_SCAN:  npm audit | snyk | none — frequency: per-PR | nightly | none
  SECRET_SCAN:      gitleaks | trufflehog | none — trigger: pre-commit
  ```
  If SAST_IN_CI=yes: semgrep run added as STANDARD VERIFIER item on ALL [security-critical] stories.
  Cross-references security-posture.md Section 7 (32J). Testing doc owns tooling + CI config; security-posture.md owns schedule + pen test policy.

  **GATE 2 additions:**
  - `/docs/foundation/testing-strategy.md` required before GATE 2 passes
  - `qa_engineer` owns creation. `backend_lead` reviews Sections 3+4. `cto` approves Section 6 Done Definition.
  - GATE 2 structural check (32H): all 8 testing-strategy.md sections non-empty + E2E journey list has ≥1 entry?
  - Log: `[TESTING-STRATEGY: unit=jest | e2e=Playwright | coverage=80% | E2E journeys=3 | GATE 2: ✅]`

**Files:**
  - kiro/skills/qa_engineer/testing_strategy_template.md (NEW — LOAD-TYPE: CHECKLIST)
  - kiro/steering/loop-engine.md (VERIFIER type selection reads testing-strategy.md Section 3 before fallback)
  - kiro/steering/loop-engine.md (STANDARD VERIFIER format includes coverage threshold if COVERAGE_IN_CI=yes)
  - kiro/steering/team-orchestrator-sprint.md (GATE 2: testing-strategy.md required + structural check)
  - kiro/steering/team-orchestrator-core.md (SM-PLAN: mark story E2E-REQUIRED if touches critical journey)

---

## Fix 39 — Dry Run v7 gaps — 2026-07-09 ✅ IMPLEMENTED 2026-07-10

### Fix 39A — GATE S2 Jira template missing ponytail verdict line (P2)
**File:** `kiro/steering/team-orchestrator-rules.md`
**Section:** GATE S2 item 6 — Security verdict written to Jira
**Problem:** Ponytail check (item 5) runs and blocks violations at commit time, but the Jira comment
template does not include a `Ponytail: PASS/FAIL` line. Audit trail is incomplete — reviewers cannot
tell from the ticket whether the ponytail check passed or failed.
**Fix:** Add to Jira comment template (after "New deps" line):
```
"Ponytail: PASS — all new code at correct rung\n" +   (or: FAIL — rung violation: <details>)
```

### Fix 39B — Fix 33A IAM scan misses signals in PRD (P1)
**File:** `kiro/steering/team-orchestrator-core.md`
**Section:** IAM SPRINT BUDGET PRE-WARNING (Fix 33A)
**Problem:** Current trigger reads only `security-posture.md Section 3`. Early-stage projects have stub
security docs — IAM signals (sso / rbac / oauth / mfa / jwt) appear in PRD Section 3 (Features) but
not in security-posture.md. Budget warning never fires for these projects, which are the ones that
most need it.
**Fix:** Expand scan to include PRD Section 3:
```
Scan BOTH:
  (a) security-posture.md Section 3
  (b) prd.md Section 3 (Features list)
for signals: auth / identity / iam / sso / oauth / saml / scim / rbac / mfa / session management / jwt
```

---

## Fix 41 — Dry Run v8 gaps — 2026-07-10 ✅ IMPLEMENTED 2026-07-10

### Fix 41A — Hook bloat: extract 40C + 40E into session-guards.md (P1)
**Problem:** Hook is now 245 lines — violates lessons.md rule: "Hook ≤ 60 lines. Constitution stays in
steering files." Fix 40C (constraint drift guard) and Fix 40E (bad loop domains) are 26 lines of
content that belongs in an always-loaded steering file, not embedded in the hook.
**Files:**
  - CREATE `kiro/steering/session-guards.md` (`inclusion: always`)
  - Move CONSTRAINT DRIFT GUARD and BAD LOOP DOMAINS blocks into it
  - In hook SYSTEM AUTHORITY: replace those blocks with single reference line:
    `Session guards (constraint drift + bad-loop domains): see kiro/steering/session-guards.md (always-loaded)`

### Fix 41B — Comprehension debt scoring rubric (P2)
**File:** `kiro/steering/team-orchestrator-sprint.md`
**Section:** SM-RETRO COMPREHENSION DEBT CHECK block
**Problem:** debt=low/medium/high is determined by scrum_master with no rubric. Inconsistent sprint to sprint.
**Fix:** Add scoring below the 4 checklist items:
```
Debt scoring (count of YES answers to the 4 questions above):
  4/4 YES → debt=low  → proceed to Sprint N+1
  3/4 YES → debt=medium → note in retro, monitor next sprint, proceed
  2/4 YES → debt=high → BLOCK Sprint N+1 (manual review sprint required)
  1/4 YES or 0/4 → debt=critical → BLOCK + escalate to user immediately
  Any module flagged "owned by loop, understood by no one" → debt=high minimum regardless of score
```

### Fix 41C — Scope bad-loop check to high-risk verbs only (P2)
**File:** `kiro/hooks/elite-team-orchestrator.kiro.hook`
**Section:** BAD LOOP DOMAINS block in SYSTEM AUTHORITY
**Problem:** Keyword-only match causes false positives. "Update the auth docs" triggers human gate
unnecessarily. Trains team to dismiss the gate (cry wolf problem).
**Fix:** Change trigger condition to require BOTH domain keyword AND high-risk verb:
```
Only trigger BAD LOOP DOMAIN gate if prompt contains:
  (a) domain keyword: auth / payments / billing / rbac / deploy / migrate / security-policy / permissions
  AND
  (b) high-risk verb: redesign / rewrite / replace / restructure / migrate / remove / delete / overhaul / refactor
Docs updates, comments, read-only analysis, test additions: NOT blocked.
```

---


## Fix 40 — Loop engineering insights from 0xCodez — 2026-07-10 ✅ IMPLEMENTED 2026-07-10
Source: https://x.com/0xCodez/status/2065089060104720776 + https://x.com/0xCodez/status/2064374643729773029
Sourced from Anthropic engineering docs, Addy Osmani loop engineering essay, Continual Learning Bench 1.0 experiment.

### Fix 40A — 5-stage memory progression in lessons.md (P1)
**File:** `kiro/skills/shared/lessons.md` (or wherever lessons guidance lives)
**Problem:** Our `lessons.md` exists but has no formal structure. Roles write failure notes and never
distill them into reusable rules. Continual Learning Bench shows Sonnet-class agents exit at stage 1
(document failure), Fable 5 completes all 5 stages → 73% verification coverage vs 17%.
**The 5 stages:** Fail → Investigate → Verify → Distill → Consult
**Fix:** Add structured lessons.md template with 5 sections:
```
## Verified facts       ← stage 3: things we stopped guessing about
## General rules        ← stage 4: distilled rules that apply across stories
## Open failures        ← stage 1-2: documented failures under investigation
## Lessons learned      ← stage 4 output: write-once rules that travel with the project
## Last session         ← stage 5: resume pointer (what was done, what is next)
```
Rule: every confirmed lesson goes into the Skill file AND lessons.md — not just checkpoint.md.
checkpoint.md is project-scoped and session-scoped. Skills travel across projects.

### Fix 40B — Comprehension debt + cognitive surrender check at SM-RETRO (P1)
**File:** `kiro/steering/team-orchestrator-sprint.md`
**Section:** SM-RETRO block
**Problem:** No human-facing check exists for two silent failure modes:
  (1) Comprehension debt — code ships faster than the team reads it. Debt compounds.
  (2) Cognitive surrender — humans stop forming opinions and accept loop output uncritically.
Both accelerate as the system gets better, not worse.
**Fix:** Add to SM-RETRO checklist:
```
COMPREHENSION DEBT CHECK (Fix 40B):
  □ Did every team member READ the diffs shipped this sprint (not just approve)?
  □ Spot-check: pick 2 PRs the agents opened. Verify the gate that approved them actually
    catches the failure mode it was written for. Gates rot silently.
  □ Is any module now "owned by the loop, understood by no one"? Flag it for a manual review sprint.
  □ Cognitive surrender check: can each team member explain WHY the top 3 changes were made?
    If not → comprehension debt is accumulating. Slow the loop, read the code.
```

### Fix 40C — Goal drift protection: constraint reread at session start (P1)
**File:** `kiro/hooks/elite-team-orchestrator.kiro.hook`
**Section:** SYSTEM AUTHORITY block / session start
**Problem:** "Don't do X" constraints disappear at turn 47 via lossy summarization in long sessions.
Agents forget constraints that were clear at session start. No mitigation currently in the hook.
**Fix:** Add to session-start block (after checkpoint read):
```
CONSTRAINT DRIFT GUARD (Fix 40C):
  Before ANY work begins, reread:
  1. /docs/foundation/project-index.md Section 3 (binding decisions + constraints)
  2. kiro/steering/team-orchestrator-rules.md NON-NEGOTIABLES list
  Any constraint marked "binding" in either doc → ACTIVE for this session.
  If a later instruction conflicts with a binding constraint → flag conflict, do not silently override.
  Log: [CONSTRAINT-LOAD: N binding decisions active | N non-negotiables active]
```

### Fix 40D — Ralph Wiggum trap → add to NON-NEGOTIABLES (P1)
**File:** `kiro/steering/team-orchestrator-rules.md`
**Section:** NON-NEGOTIABLES list
**Problem:** Agents emit completion signal on partial work, loop exits on a half-done job.
Root cause: soft stop conditions ("done when it looks good", "looks reasonable", "mostly passing").
Named by Geoffrey Huntley — agent tells itself it's done, nothing objective catches it.
**Fix:** Add NON-NEGOTIABLE #10:
```
10. **No soft stop conditions (Ralph Wiggum trap).** Every story, task, and agent invocation
    requires an OBJECTIVE stop condition: tests pass, build green, linter exits 0, type check clean.
    "Looks good", "seems correct", "mostly passing", "handled enough" = NOT a stop condition.
    A role that declares done without an objective signal → QA must re-open the story.
    The agent that wrote the code cannot be the agent that declares it done. See Fix 27C (VERIFIER).
```

### Fix 40E — Bad loop domain blocklist in SYSTEM AUTHORITY (P1) ✅ IMPLEMENTED
**File:** `kiro/hooks/elite-team-orchestrator.kiro.hook`
**Section:** SYSTEM AUTHORITY block
**Problem:** No single authoritative list of domains where agents cannot self-declare done.
We have GATE 2 for architecture and S1/S2/S3 for security but no explicit "human required" blocklist.
Agents can drift into architecture rewrites, auth/payments decisions, or production deploys and
declare themselves done without a human gate.
**Fix:** Add to SYSTEM AUTHORITY block:
```
BAD LOOP DOMAINS — human gate REQUIRED before any completion claim:
  ✗ Architecture rewrites (service boundaries, data model changes, API contract changes)
  ✗ Auth / payments / billing code (any touch to auth flow, session handling, payment processing)
  ✗ Production deploys or database migrations on live data
  ✗ Security policy changes (permissions, RBAC rules, secrets rotation)
  ✗ Vague product decisions ("make it better", "redesign this", "figure out the right approach")
  For any of the above: STOP, surface to user, get explicit approval before proceeding.
  An agent that proceeds without approval in these domains = NON-NEGOTIABLE violation.
```
---


## Fix 42 — Dry Run v9 gaps — 2026-07-10 ✅ IMPLEMENTED 2026-07-10

### Fix 42C — Deploy self-triggers bad-loop gate (P1 — HIGH)
**File:** `kiro/steering/session-guards.md`
**Problem:** GUARD 2 required BOTH domain keyword AND high-risk verb. 'deploy / release / production' were domain keywords but 'deploy' was not a high-risk verb. "Deploy to prod NOW" had no high-risk verb → gate didn't fire. Prod deploy is the highest-risk bad-loop action and self-escaped.
**Fix:** Added self-triggering exception: `deploy / release / production` domain keywords fire the gate on domain alone — no verb required. Also added `deploy / release / rollout / promote / ship` to the high-risk verb list for other domains. Added inline examples to table.

### Fix 42A — Post-discovery bad-loop re-evaluation (P2 — MEDIUM)
**File:** `kiro/steering/discovery-engine.md`
**Problem:** Bad-loop gate ran only on the original prompt. Discovery could reveal enterprise SSO+MFA+RBAC scope from "improve login page" — gate already passed on original prompt, didn't re-run.
**Fix:** Added STEP 4B between mode confirmation and STEP 5 execution. After discovery scope confirmed, re-run GUARD 2 check against the discovered scope string. If bad-loop domain keywords + high-risk scope detected → gate fires post-discovery before any execution begins. Log: `[POST-DISCOVERY-GATE: ...]`

### Fix 42B — Stage-1 lesson age enforcement (P2 — MEDIUM)
**File:** `kiro/steering/team-orchestrator-sprint.md`
**Problem:** Fix 40A added 5-stage structure to lessons.md but no SM-RETRO gate for lesson age. Stage-1-Fail lessons could persist indefinitely across sprints with no consequence.
**Fix:** Added LESSON AGE CHECK to SM-RETRO (runs after comprehension debt check). Any Stage-1-Fail lesson from a prior sprint that hasn't advanced to Stage 2+ = "stale blocker". 2+ stale blockers → BLOCK Sprint N+1 (separate from comprehension debt). Any stale lesson in auth/payments/billing/security → BLOCK regardless of count. Exact resume phrase included. Log: `[LESSON-AGE: N stale blockers | oldest=... | action: BLOCK/FLAG/OK]`

## Fix 42C — Deploy self-triggers bad-loop gate (P1 — HIGH) ✅ IMPLEMENTED 2026-07-10
**Found in:** Dry Run v9 Scenario S3
**Problem:** `session-guards.md` GUARD 2 lists 'deploy / release / production' as domain keywords but 'deploy' is NOT in the high-risk verb list. A prompt like "Deploy to prod NOW" has no high-risk verb → gate doesn't fire. Prod deploy is the highest-risk bad-loop action and self-escapes the gate it's supposed to trigger.
**Root cause:** The gate requires BOTH domain keyword AND high-risk verb. But for deploy, the action IS the domain — there's no separate verb.
**Fix:** In `session-guards.md` GUARD 2 high-risk verbs column, add: `deploy / release / rollout / promote / ship` — OR — add a note: "deploy/production domain → self-triggering (no verb required)."
**File:** `kiro/steering/session-guards.md`

---

## Fix 42A — Bad-loop gate not re-evaluated after discovery (P2 — MEDIUM) ✅ IMPLEMENTED 2026-07-10
**Found in:** Dry Run v9 Scenario S1
**Problem:** Bad-loop gate evaluates the ORIGINAL prompt only. If "Improve the login page" passes (no domain/verb match), gate is done. Discovery then reveals SSO+MFA+RBAC enterprise scope — a textbook bad-loop domain — but gate doesn't re-run. Agent proceeds on auth redesign scope without human gate.
**Fix:** After discovery completes, re-run GUARD 2 check on the DISCOVERED scope string. If discovery answers contain bad-loop domain keywords + high-risk scope → gate fires post-discovery.
**File:** `kiro/steering/team-orchestrator-core.md` — add post-discovery bad-loop re-check step after discovery score is computed.

---

## Fix 42B — Stage-1 lesson age not enforced (P2 — MEDIUM) ✅ IMPLEMENTED 2026-07-10
**Found in:** Dry Run v9 Scenarios S2 + S4 (confirmed)
**Problem:** Fix 40A added 5-stage structure to lessons.md but no SM-RETRO gate for lesson age. A Stage-1-Fail lesson can persist across unlimited sprints. In S4: Lesson 1 (Firebase token) was Stage-1-Fail for 3 consecutive sprints with no consequence. Comprehension debt (Fix 41B) catches this only if debt=critical; at debt=medium the sprint proceeds with multi-sprint unresolved failures.
**Fix:** Add LESSON AGE CHECK to SM-RETRO in `team-orchestrator-sprint.md`:
```
LESSON AGE CHECK (Fix 42B) — before Sprint N+1:
  Any Stage-1-Fail lesson from a prior sprint that has NOT advanced to Stage 2+ = "stale blocker"
  1 stale blocker → flag in retro, note responsible role, proceed
  2+ stale blockers → BLOCK Sprint N+1 (separate from comprehension debt)
  Log: [LESSON-AGE: N stale blockers | oldest: [lesson] age=[N sprints] | action: BLOCK/FLAG]
```
**File:** `kiro/steering/team-orchestrator-sprint.md`

---

---

### Fix 43A — Lesson Age Clock Uses Written-At Not Gate-Fired-At
**Severity:** MEDIUM
**Root cause:** Stage-1-Fail lessons are written at SM-RETRO, not at the moment the gate fired.
If retro is delayed (runs 2 days into Sprint N+1), the age check in Sprint N+2 reads
"1 sprint old" when the issue is actually "2 sprints unresolved."
**Fix:** Add `gate_fired_at: Sprint N` metadata to lessons at gate-fire time. LESSON AGE CHECK uses `gate_fired_at`, not `written_at`.
**Files:** `docs/lessons.md` (template), `kiro/steering/team-orchestrator-sprint.md` (LESSON AGE CHECK block)

---

### Fix 43B — Ponytail Has No Rung Disqualification Escalation Path
**Severity:** MEDIUM
**Root cause:** When a dep at Rung 2 is disqualified (CVE, abandoned, license-incompatible),
agents are stuck: Ponytail says "use the dep," security says "you cannot." No documented path.
**Fix:** Add Rung Disqualification Protocol to ponytail.md — RDR (Rung Disqualification Record),
same-rung alternative check, one-rung-at-a-time escalation, mandatory ADR, security sign-off for CVEs.
**User artifact:** `docs/ponytail-rung-disqualification-guide.md` ← reference this
**Files:** `kiro/steering/ponytail.md` (new section), `kiro/steering/team-orchestrator-rules.md` (GATE S2 escalation note)

---

### Fix 43C — No Cross-Tenant Isolation Test Enforcement at GATE S2
**Severity:** HIGH
**Root cause:** GATE S2 checks "coverage ≥ 80%" but has no specific requirement for
cross-tenant isolation tests on `security/rbac` or `data/multi-tenant` stories.
A story can pass GATE S2 with 83% coverage while completely missing tenant-boundary tests.
The bug surfaces at SM-RETRO (Ralph Wiggum) instead of being caught at PR review — one gate too late for PCI-DSS.
**Fix:** Add GATE S2 conditional item: "For stories tagged `security/rbac` or `data/multi-tenant`:
at least ONE explicit cross-tenant access-denial test REQUIRED. Absence = GATE S2 FAIL regardless of coverage %."
**Files:** `kiro/steering/team-orchestrator-rules.md` (GATE S2 checklist, new conditional item)

---