---
inclusion: manual
---


## ⚡ QUICK REFERENCE — Loop Engine (read this first)
- **Max 8 iterations** per story. Score each criterion 1–10. STOP WHEN: all ≥ 8.
- **VERIFIER must execute** via Bash tool. No bash output = CHECK invalid. [Fix 27C]
- **VERIFIER types**: STANDARD (+ coverage threshold if COVERAGE_IN_CI=yes in testing-strategy.md §2) | LOAD-TEST (tool from testing-strategy.md §3, fallback: autocannon) | BROWSER-REQUIRED (start-server-and-test/RTL). [Fix 30C/30G/32K]
- **Mobile split**: story with mobile/ios + mobile/android BOTH → VERIFIER must cover BOTH platforms or note "unified RN." [Fix 30A]
- **STRIDE-BRIDGE**: architect STRIDE mitigations → story criteria (max 2/story). [Fix 26D]
- **Co-maker DUAL SPEC**: PRIMARY (ML) + SECONDARY (API or UI, lane-aware FE/BE). Both must reach ≥8. [Fix 29C/30F]
- **At iter 8 score <8**: SM-UNBLOCK fires → SCOPE-CUT / RE-SPEC / ESCALATE. [Fix 25F]
- **ACT reloads**: max 2/story at DEGRADING (security-critical: 3). Reload lowest-scoring skill. [Fix 25G]
- **Loop spec**: GOAL + VERIFIER (typed) + LABEL-SOURCED CRITERIA + STRIDE criteria + STOP WHEN. Written BEFORE first line of code.
---
# Loop Engine — Iterative Quality Protocol

**Purpose:** Replace the kiro pipeline's linear story execution with true loops. Each feature
iterates until it meets a scored bar, not until the implementing agent says it is done.
Load this file whenever a role is in the DEVELOP phase executing a story.

---

## CORE CONCEPT

A prompt hands the AI an instruction.
A loop hands the AI a job, a way to know when the job is done, and a rule for when to give up.

The kiro pipeline has phases and gates. This file adds **loops inside each story** so that
quality compounds within a feature — not just between sprints.

```
OLD (linear):  senior_engineer → writes code → QA reviews → pass/fail
NEW (loop):    senior_engineer LOOPS until criteria ≥ 8 → then QA checker runs fresh
```

---

## THE FIVE LOOP BLOCKS (required in every feature loop)

### 1. GOAL — what done looks like (objective, not a judgment)
Must be falsifiable. "Clean code" = invalid. "All auth tests pass, lint clean, zero type errors" = valid.

### 2. ITERATION PROTOCOL — what happens every pass
```
Each iteration:
  1. READ FROM DISK — read current file state from the feature branch working tree.
     Do not rely on in-context copies — context may have been pruned by Fix 8B.
     This read counts toward Fix 8D per-role budget (1 read per iteration).
  2. IDENTIFY FIX — read the verifier output from last iteration's VERIFY block.
     Pick the SINGLE criterion that scored lowest. That is the only thing being fixed.
  3. WRITE THE FIX — make the smallest change that addresses the weakest criterion.
  4. WRITE TO DISK — write ALL changed files to the feature branch working tree.
     Use Edit/Write tool. Confirm write succeeded before proceeding.
     git add <changed files only> — stage changes. Do NOT commit yet.
     git diff --staged — verify only intended files are staged. Unstage anything else.
     Note: these git steps run identically in GIT_MODE=REMOTE and GIT_MODE=LOCAL.
     The loop does not push. Branch exists locally in both modes during iteration.
  5. RUN VERIFIER — run loop spec VERIFIER commands against the staged working tree.
  6. SCORE — score each criterion 1-10 (see scoring rubric below).
  7. PRUNE CONTEXT (Fix 8B) — discard step 3 raw output from context.
     KEEP: VERIFY score row + staged file paths. "Current file state" = git-staged tree.
     ACT (Fix 23D): If score < 7 on any criterion: identify which label that criterion came from
     → reload THAT SPECIFIC skill file at FULL content (not compressed) → revise → re-CHECK.
     Log: [CHECK: story=X | labels=[Y,Z] | score=S/10 | ACT=YES/NO | reloaded=<file>]
```

### 3. VERIFY — the gate that makes it a real loop
The verifier must be automatic. It cannot be the implementing agent's own opinion.
Valid verifiers: test suite, linter, type checker, build, contract test, security scan.
Invalid verifiers: "I think this looks good", "the code seems correct".

### 4. STATE — what the loop remembers between passes
Every loop maintains a `loop-state` block in the story's $TRACKER comment (or markdown at
`/docs/phase-N/loop-states/[story-id].md` if no tracker is connected — per Fix 1):
```
Iteration N:
  Tried:   <what was changed>
  Result:  <verifier output summary, ≤ 3 lines>
  Scores:  criterion-1=X, criterion-2=X, criterion-3=X
  Weakest: <criterion name — this is what next iteration fixes>
```
The loop READS its own state at the start of each iteration. It never re-derives what it already tried.

### 5. STOP CONDITION — two exits, no exceptions
```
SUCCESS:   every criterion scores ≥ 8 AND the checker agent confirms
HARD STOP: 8 iterations reached → stop, report remaining failures → SM-UNBLOCK fires (Fix 25F)
```
A loop with no exit runs until it breaks or drains budget. The hard stop at 8 is non-negotiable.

### SM-UNBLOCK PROTOCOL (Fix 25F — activates on iteration 8 hard-stop)

**Trigger:** Iteration count = 8 AND any criterion still scores <8.

**Step 1 — Write loop-state to $TRACKER:**
Write this block: [LOOP-STUCK] story=<ID> | failing-criteria=<list> | last-scores=<criterion:score,...> | iterations=8
SM-PLAN reads this block at SM-RETRO to make the SCOPE-CUT/RE-SPEC/ESCALATE decision.

**Step 2 — SM-UNBLOCK decision table:**

| Decision | Meaning | Who acts | Iteration counter |
|----------|---------|---------|-------------------|
| SCOPE-CUT | Remove failing criterion from loop spec. Story marked DONE. | scrum_master | N/A: story closes |
| RE-SPEC | Rewrite loop spec criteria only. No code change. | scrum_master then maker | RESETS to 0. Max 1 RE-SPEC per story. |
| ESCALATE | Mark story BLOCKED in sprint-plan.md. Notify user. Sprint continues. | scrum_master | N/A: story blocked |

**SCOPE-CUT rules:**
- Max 1 criterion cut per story. Log: [SCOPE-CUT: criterion=<name> reason=<one line>]
- Story velocity: FULL points (scope reduced, not quality dropped).
- Cut criterion → add backlog story [TECH-DEBT: <criterion> deferred from <story-ID>].

**ESCALATE rules:**
- Write BLOCKED card: [BLOCKED: story=<ID> | reason=loop-unstuck | failing=<criteria>]
- Story velocity: 0 points. Other sprint stories continue.
- User must review BLOCKED story before next sprint starts.

---

## FEATURE LOOP SPEC FORMAT

Every story in DEVELOP gets a loop spec before the first line of code is written.
`senior_engineer` (maker) produces it. `scrum_master` approves it. It is written into the Jira story.

**STRIDE-BRIDGE RULE (Fix 26D):**
After architect runs STRIDE for a trust boundary, SM-PLAN MUST:
1. Extract each mitigation from the STRIDE output (format: "T/R/I/D/E/S: [threat] → [mitigation]")
2. For each story that touches the affected trust boundary: add 1 criterion per mitigation
3. Format: `STRIDE-[T/R/I/D/E/S]: <mitigation description> (score 1=no impl, 10=impl+tested)`
4. Max 2 STRIDE criteria per story to avoid spec bloat (queue excess as TECH-DEBT stories)
5. Log: `[STRIDE-BRIDGE: N mitigations → N story criteria added to [story IDs]]`
Note: STRIDE criteria count toward the ≥1/label and max 2/label soft caps independently.

STRIDE EXCESS → MANDATORY TECH-DEBT STORIES (Fix 31E):
When total STRIDE mitigations exceed the 2/story cap across all affected stories:
  → SM-PLAN MUST create explicit TECH-DEBT stories for deferred mitigations. This is NOT optional.
  → Format: story title = "TECH-DEBT: STRIDE [T/R/I/D/E/S] mitigation — <threat description>"
    Labels: [security-critical, tech-debt]
    Criteria: `STRIDE-[letter]: <mitigation> (score 1=no impl, 10=impl+tested)`
    Priority: HIGH by default — deferred security mitigations are not low-priority.
  → Do NOT silently drop excess mitigations. "Queue excess" means create the story now.
  Log: `[STRIDE-DEFERRED: N excess mitigations → TECH-DEBT stories: TD-<N> created in backlog]`

```
▸ LOOP SPEC — [Story ID]: [Story title]

GOAL:
  [Concrete, falsifiable statement of what "done" means.
   Must reference the story's Acceptance Criteria.]

VERIFIER (Fix 27C — execution is mandatory):
  Command(s) that auto-reject bad work. MUST be executed via Bash tool.
  - [e.g., npm test -- --coverage]
  - [e.g., npx tsc --noEmit]
  - [e.g., npx eslint src/]
  - [e.g., npx semgrep --config=p/owasp-top-ten]
  All must be runnable non-interactively. If you cannot write this line, the story
  is not ready to develop. Escalate to architect.

  EXECUTION RULES (Fix 27C):
  ► VERIFIER must be run via Bash tool. Actual stdout/stderr = ground truth for CHECK phase.
  ► Imagining or describing what the output "would be" is BANNED. This produces quality theater.
  ► If Bash tool is unavailable in current runtime:
      → Mark story BLOCKED:VERIFIER-UNEXECUTABLE
      → Log: `[VERIFIER-BLOCKED: Bash tool unavailable. Story <ID> cannot enter CHECK phase.]`
      → Do NOT score criteria. Do NOT proceed to iteration N+1.
      → SM decision: defer story or switch to CHECKER ROLE PASS pattern
        (CHECKER ROLE PASS: fresh-context agent reads generated files + spec, scores mechanically)
  ► VERIFIER output must appear in loop log before any criterion score is written.
      Format: `[VERIFIER OUTPUT: exit=0/1 | stdout=<first 10 lines> | pass=Y/N]`

  VERIFIER TOOL-TYPE CLASSIFICATION (Fix 30C + 30G):
  Before writing a VERIFIER, classify each command by type:

  STANDARD (always safe):
    Unit/integration tests — npm test, pytest, jest, go test, cargo test
    Static analysis — tsc, eslint, semgrep, tflint
    Schema validation — ajv, jsonschema
    → COVERAGE THRESHOLD (Fix 32K): Check /docs/foundation/testing-strategy.md Section 2.
      IF COVERAGE_IN_CI=yes → VERIFIER MUST include coverage threshold command:
        `npm test -- --coverage --coverageThreshold='{"global":{"lines":<MINIMUM_LINE>,"branches":<MINIMUM_BRANCH>}}'`
      IF COVERAGE_IN_CI=no or testing-strategy.md missing → standard test command, no threshold enforcement.
      Log: `[VERIFIER COVERAGE: COVERAGE_IN_CI=yes | threshold=lines≥N,branches≥N]` or `[VERIFIER COVERAGE: not enforced in CI]`

  LOAD-TEST (may not be in CI):
    k6, locust, Artillery, autocannon, wrk
    → TOOL SELECTION (Fix 32K): Read /docs/foundation/testing-strategy.md Section 3 (Tool Decisions) FIRST.
      Use LOAD_TEST_TOOL declared there as primary load-test tool.
      Fallback to autocannon ONLY if declared tool binary unavailable (install: npm i -g autocannon).
      If testing-strategy.md missing → default to autocannon.
      Fallback criterion format: `be/performance: autocannon -c 100 -d 10 <url> p99 < Xms`
      Log: `[VERIFIER LOAD-TEST: tool=<declared> | available=yes/no | fallback=autocannon if no]`

  BROWSER-REQUIRED (needs running app at URL):
    Lighthouse, Cypress, Playwright E2E, Percy visual regression
    → Before writing: note the dev server start command.
      Use start-server-and-test pattern: `npx start-server-and-test 'npm run dev' 3000 '<tool-cmd>'`
      If running app not feasible in CI: fallback to component-level tests (React Testing Library)
        + note `[BROWSER-VERIFIER: manual Lighthouse run required before story merge]`
      Log: `[VERIFIER BROWSER-REQUIRED: <tool> | start-cmd=<cmd> | fallback=RTL]`
    LIGHTHOUSE --ASSERT MANDATE (Fix 31B):
      Lighthouse without --assert flags is BANNED. Exit code 0 without score assertions is meaningless.
      Required format: `lhci autorun --assert.preset=lighthouse:no-pwa --assert.assertions.performance>=90 --assert.assertions.accessibility>=95`
      OR via lighthouserc.js: { assert: { assertions: { 'categories:performance': ['error', {minScore: 0.9}] } } }
      → VERIFIER must include at least ONE scored assertion that fails CI on score drop.
      → Lighthouse referenced in criteria without --assert: mark criterion score ≤ 5 (invoked but unverified).
      Log: `[VERIFIER LIGHTHOUSE: --assert present | performance≥N | accessibility≥N | exit-code enforced]`

  MOBILE PLATFORM SPLIT (Fix 30A):
    If story labels include BOTH mobile/ios AND mobile/android:
    → VERIFIER must cover BOTH platforms explicitly. Options:
      (a) Platform-specific commands: `xcodebuild test -scheme AppTests` AND `./gradlew test`
      (b) Detox matrix: `detox test --configuration ios.sim` AND `detox test --configuration android.emu`
      (c) If unified RN codebase: note explicitly in loop spec:
          `[MOBILE-VERIFIER: unified RN — single Jest suite covers ios+android. Platform-split manual smoke on both before merge.]`
    → Never leave mobile/ios+android story with only `npx jest` and no platform note.

  CONCURRENCY (Fix 31A — race-condition/stateful protocol/CRDT stories):
    Stories with be/resilience label + concurrency/race/CRDT/distributed-lock in title OR criteria:
    → STANDARD jest/pytest is insufficient. Must use one of:
      (a) Promise.all parallel invocation: `await Promise.all([...Array(N)].map(() => fn()))` — N ≥ 10
      (b) Property-based testing: fast-check `fc.asyncProperty(...)` with concurrent model
      (c) Go: `-race` flag via `go test -race ./...`
      (d) Explicit concurrency test harness (piscina, worker_threads stress test)
    → Criteria: add `concurrency/<name>: N concurrent calls produce consistent state (score 1-10)`
    → Never mark a concurrency story DONE with only sequential unit tests.
    Log: `[VERIFIER CONCURRENCY: approach=<Promise.all|property-based|race-flag> | N=<concurrency factor>]`

CRITERIA (scored 1-10 each iteration):
  LABEL-SOURCED CRITERIA (Fix 23D): Derive criteria FROM the compressed skill file summaries
  that were loaded for this story's labels. Do NOT use generic criteria when labels are present.

  How to build CRITERIA at loop spec creation:
    1. Story labels are already in context (e.g., [be/api, be/resilience])
    2. Skill files for those labels are compressed in context (5-line summaries)
    3. Extract the quality bars NAMED in those summaries — these become your criteria
    4. Add ≥1 criterion per label (max 2 per label to keep spec tight)

  Label → typical criteria extracted from skill summaries:
    be/api        → idempotency key present?, API versioned?, error format standardized?
    be/resilience → retry with backoff?, circuit breaker wired?, rate limit enforced?
    be/database   → migration is reversible?, N+1 queries absent?, indexes on join cols?
    be/auth       → token expiry enforced?, refresh rotation correct?, scope validated?
                   If SAML story: SAML-XXE blocked?, assertion signature validated?, InResponseTo checked? (see saml_security.md CHECKLIST)
    be/pii        → PII scrubbed before logging?, retention period tagged?
    fe/component  → component renders in isolation?, no prop drilling >2 levels?
    fe/a11y       → ARIA roles correct?, keyboard accessible?, contrast ratio ≥ 4.5:1?
    devops/k8s    → resource limits set?, liveness probe defined?, image pinned (no :latest)?
    security-critical → threat model reviewed?, STRIDE items addressed?
    testing/unit  → coverage ≥ target?, edge cases covered?, no test logic in prod code?

  FALLBACK (no labels on story): use generic criteria below:
  - criterion-1: [e.g., All unit tests pass]
  - criterion-2: [e.g., Zero lint warnings]
  - criterion-3: [e.g., Type check clean]
  - criterion-4: [e.g., OWASP scan: zero HIGH/CRITICAL]

STOP WHEN: every criterion ≥ 8, OR 8 iterations reached.

ON HARD STOP: write [LOOP-STUCK] block to $TRACKER → SM-UNBLOCK fires (Fix 25F). Summarize iteration history, name unresolved criteria, flag in Jira.
```

---

## CO-MAKER DUAL LOOP SPEC (Fix 29C)

Co-maker stories (PRIMARY + SECONDARY roles, Fix 26B) MUST use two independent loop specs.
A single shared VERIFIER cannot validate both the PRIMARY deliverable and the SECONDARY deliverable.

**Rule:** Co-maker story = DONE only when BOTH loop specs independently reach all criteria ≥ 8.

```
▸ LOOP SPEC A — [Story ID]-PRIMARY: [Story title] — PRIMARY role: data_scientist
  
  GOAL: [Data/ML deliverable — experiment design, model evaluation, feature pipeline]
  
  VERIFIER (must execute via Bash):
    - [e.g., pytest tests/ml/ --cov=src/ml/]
    - [e.g., python scripts/eval_model.py --threshold 0.90]
  
  CRITERIA (Primary focus — ML/data quality):
    - data/ml criterion-1: [experiment reproducible? seed set?]
    - data/ml criterion-2: [model metric ≥ target threshold?]
    - data/eda criterion-1: [feature drift detected + handled?]
  
  STOP WHEN: all PRIMARY criteria ≥ 8, OR 8 iterations reached.

▸ LOOP SPEC B — [Story ID]-SECONDARY: [Story title] — SECONDARY role: senior_engineer_be

  GOAL: [API/integration deliverable — contract, performance, error handling]
  
  VERIFIER (must execute via Bash):
    - [e.g., npm test -- --coverage]
    - [e.g., npx semgrep --config=p/owasp-top-ten src/api/]
  
  CRITERIA (Secondary focus — API/integration quality):
    - be/api criterion-1: [contract schema validated?]
    - be/resilience criterion-1: [retry + circuit breaker wired?]
    - be/performance criterion-1: [p99 latency < target under load test?]
  
  STOP WHEN: all SECONDARY criteria ≥ 8, OR 8 iterations reached.
```

Log when both close: `[CO-MAKER DONE: story=<ID> | PRIMARY SPEC: all ≥8 | SECONDARY SPEC: all ≥8 | CHECKER: PASS]`
If one spec reaches hard stop while the other is open: SM-UNBLOCK fires for that spec only. Other spec continues.

---

## MAKER / CHECKER HARD SPLIT

**This is the single highest-value structural change.**

The model that wrote the code is too generous grading its own homework.
The checker must be a separate agent with a fresh context and no knowledge of why choices were made.

```
MAKER  = senior_engineer_be / senior_engineer_fe
         → Fast. Runs the loop. Produces the code. Tracks loop-state.
         → CANNOT transition a story to "Done". Cannot self-declare success.
         → Hands off: loop-state summary + final verifier output + code diff

CHECKER = qa_engineer
         → Strict. Fresh context. Receives ONLY: story AC + code diff + verifier output.
         → Does NOT read the maker's self-scores or loop-state narrative.
         → Runs its OWN independent verifier pass (same commands, different agent).
         → Scores criteria independently. Confirms or rejects.
         → If checker scores differ from maker by ≥ 2 on any criterion → rejection,
           return to maker with specific discrepancy noted.
```

**Rule:** The checker never loads the maker's reasoning or loop-state narrative.
It only sees: what the story required + what the code does + what the tests say.
Giving the checker the maker's self-assessment defeats the entire purpose.

---

## SCORING RUBRIC (used by both maker and checker)

Score each criterion independently. Do not average. A single criterion at < 8 = not done.

| Score | Meaning |
|-------|---------|
| 1–4   | Fundamentally broken. Major rework needed. |
| 5–6   | Partially works. Key cases missing or failing. |
| 7     | Mostly works. Minor gaps remain. One more iteration likely fixes it. |
| 8     | Meets the bar. Ship-ready. |
| 9     | Exceeds bar. No obvious gaps. |
| 10    | Flawless against all known edge cases. Reserve for deliberate excellence. |

**VERIFY step format (maker writes this each iteration):**
```
ITERATION N — VERIFY
  criterion-1 [test pass]:     score=X — [what failed if < 8]
  criterion-2 [lint clean]:    score=X — [what failed if < 8]
  criterion-3 [type check]:    score=X — [what failed if < 8]
  criterion-4 [OWASP scan]:    score=X — [what failed if < 8]
  Weakest: [criterion name]
  DECIDE: [ITERATING / FINAL — READY FOR CHECKER]
```

A maker can only write `FINAL — READY FOR CHECKER` when ALL criteria are ≥ 8.
Writing FINAL with any criterion < 8 = Ralph Wiggum violation (see below).

---

## RALPH WIGGUM GUARD

**Named for the pattern:** agent decides it is done too early, exits on a half-finished job,
the loop keeps running and spending while producing nothing useful.

**Signs the guard catches:**
- Maker writes FINAL when a criterion is < 8
- Maker skips a verifier step because "it should pass"
- Maker's loop-state shows the same failure in iteration N and N+1 (no progress)
- Checker's independent score differs from maker's by ≥ 2

**When the guard fires:**
```
[RALPH WIGGUM DETECTED]
  Story:     [ID]
  Iteration: [N]
  Issue:     [specific violation — e.g., "maker scored lint=8 but checker found 12 warnings"]
  Action:    Return to maker. Maker must address the specific discrepancy.
             Iteration counter does NOT reset — count continues toward hard stop at 8.
  Tracker:   $TRACKER.addComment(id, "LOOP VIOLATION: [details] — returned to maker, iteration N")
```

---

## SELF-CHECKING LOOP PROMPT (embed in senior_engineer skill invocations)

When a senior_engineer activates for a story, prepend this to their context:

```
You are working in a LOOP. You will PLAN, DO, VERIFY, and DECIDE — repeatedly —
until every criterion scores ≥ 8 or you hit 8 iterations.

LOOP SPEC: [paste the story's loop spec here]

LOOP PROTOCOL (repeat every iteration):
  1. PLAN   — state the single next step. One sentence.
  2. DO     — make the smallest change that addresses the weakest criterion.
  3. VERIFY — run the verifier commands. Score each criterion 1-10. Be brutal.
              List exactly what is still weak. No soft-pedaling.
  4. DECIDE — if every criterion is ≥ 8, write "FINAL — READY FOR CHECKER" and stop.
              Otherwise write "ITERATING — weakest: [criterion]" and go again.

RULES:
  - Never call it done until every criterion is ≥ 8.
  - Each pass MUST fix the criterion that scored lowest last pass.
  - Do not re-derive what you already tried — read your loop-state.
  - Do not ask questions. Make a sensible assumption, note it, keep going.
  - After 8 iterations, stop regardless. Write "HARD STOP — escalating". Write [LOOP-STUCK] block to $TRACKER. SM-UNBLOCK protocol fires (Fix 25F).
  - After EVERY iteration, apply Fix 8B context prune BEFORE starting next PLAN:
      KEEP: loop spec + scored VERIFY table row + current file state (latest version only)
      DISCARD: all prior iterations' raw PLAN text, DO output, full VERIFY text
      This is mandatory. Do not skip even on iteration 1.
```

---

## LOOP STATE FILE (per story, per sprint)

Location: `/docs/phase-N/loop-states/[story-id].md`

Created by maker at iteration 1. Updated each iteration. Read-only for checker.

```markdown
# Loop State — [Story ID]: [Story title]
Sprint: N  |  Phase: N  |  Maker: senior_engineer_be/fe  |  Started: [ISO date]

## Iteration Log
| # | Changed | Verifier result | Scores | Weakest |
|---|---------|-----------------|--------|---------|
| 1 | [what] | [pass/fail summary] | c1=X c2=X c3=X | [criterion] |
| 2 | [what] | [pass/fail summary] | c1=X c2=X c3=X | [criterion] |
...

## Current Status
Iteration: N of 8 max
All criteria ≥ 8: YES / NO
Ready for checker: YES / NO

## What Was Tried and Failed
- [attempt]: [why it didn't work — prevents repeating]
- [attempt]: [why it didn't work]

## Checker Review (filled by qa_engineer after maker hands off)
Independent verifier run: [PASS / FAIL]
Independent scores: c1=X c2=X c3=X c4=X
Delta from maker: [none / criterion X differed by N]
Verdict: [APPROVED / REJECTED — reason]
```

---

## LOOP BUILD ORDER (skill promotion protocol)

From the article: "Get one manual run reliable → skill → loop → schedule."
Applied to kiro recurring work patterns:

```
STAGE 1 — PROVE IT (Sprint 1 of any new workflow):
  Run the task manually with a human in the loop.
  Don't automate yet. Just confirm the steps actually work.
  Output: notes on what broke, what assumptions were wrong.

STAGE 2 — HARDEN IT (add to a skill file):
  Capture the working steps as a skill file in kiro/skills/<role>/<task>.md
  Include: exact commands, expected outputs, failure modes found in Stage 1.
  Do NOT loop yet — the skill is still run manually.

STAGE 3 — LOOP IT (add gate + stop condition):
  Wrap the skill in the LOOP SPEC format above.
  Add the verifier. Add the stop condition. Add the loop-state file.
  Run it 2-3 times supervised to confirm loop exits cleanly.

STAGE 4 — SCHEDULE IT (only after Stage 3 is clean):
  Add to a hook, cron, or GitHub Actions.
  Set a token/cost budget cap.
  Monitor cost-per-accepted-change for the first 2 sprints.

VIOLATION: scheduling something you have not proven reliable by hand
is exactly how loops blow up while you sleep.
```

---

## COST-PER-ACCEPTED-CHANGE METRIC

**The metric that actually matters.** Track it per story, report it at sprint end.

```
cost_per_accepted_change = total_iterations_spent / stories_checker_approved

Target: ≥ 1 story approved per 3 iterations average
Warning: < 50% accept rate → loop spec quality is the problem, not the code
Action at warning: scrum_master reviews loop specs before next sprint — are criteria
                   objective? Is the verifier actually rejecting bad work?
```

**Sprint end loop report (scrum_master adds to retro):**
```
Loop Engine Report — Sprint N
  Stories looped:         [N]
  Total iterations used:  [N] (avg [N] per story)
  Hard stops hit:         [N] (stories that hit 8-iteration cap)
  Checker approve rate:   [N]% (target ≥ 50%)
  Ralph Wiggum events:    [N]
  Cost-per-accepted:      [N] iterations/story

If hard stops > 20% of stories → loop specs need tightening.
If checker approve rate < 50% → maker is self-declaring FINAL too early.
If Ralph Wiggum events > 3 → add review of self-scoring honesty to retro.
```

---

## INTEGRATION POINTS WITH EXISTING KIRO PIPELINE

| Existing gate/step | Loop engine adds |
|---|---|
| GATE 2 (pre-build) | Loop spec required for every story before sprint starts |
| senior_engineer activation | Self-checking loop prompt prepended to context |
| QA gate (GATE 3) | QA = checker agent, fresh context, independent verifier run |
| $TRACKER story update | Loop-state appended as comment each iteration (markdown fallback per Fix 1) |
| Sprint end (GATE 4) | Loop Engine Report added to retro |
| /docs/phase-N/ | /loop-states/ subfolder added |

---

## WHAT LOOP ENGINE DOES NOT CHANGE

- Phase structure (THINK → DESIGN → DEVELOP) — unchanged
- Security gates S1, S2, S3 — unchanged, run inside the verifier step
- Git commit rules — unchanged, commit only after checker approves
- Role definitions and skill loading — unchanged
- Document ownership — unchanged

Loop engine operates INSIDE the DEVELOP sprint loop. It does not restructure phases.
