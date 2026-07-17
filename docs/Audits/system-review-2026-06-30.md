# Loop Engineering System — Deep Review Analysis
**Date:** 2026-06-30  
**Scope:** All kiro/ files — steering (7), hooks (8), skills (261), CLAUDE.md, memory discipline

---

## SYSTEM SNAPSHOT

| Layer | Files | Lines | Status |
|-------|-------|-------|--------|
| Steering files | 7 | 2,730 | Active — mixed quality |
| Active hooks | 1 | ~900 (prompt) | Working but architecturally inverted |
| Disabled hooks | 7 | ~100 | Dead weight — delete candidates |
| Skill files | 261 | ~18,000 est. | Solid — well-structured |
| CLAUDE.md | 1 | 1,668 | Bloated — needs surgery |
| Memory files | 0 | — | Not initialized — broken continuity |

---

## HIGHS — What's Working Exceptionally Well

**Skill Selection Matrix** is the best architectural decision in the system. 261 skill files mapped to specific activities means max 3 files load per role activation instead of all 20. The 60-80% token savings claim is real. The Step 0 existence check (Fix 11F), 5-line takeaway rule, and second-pass trigger conditions (Fix 11G) make it a complete, production-grade loading protocol.

**$TRACKER abstraction** cleanly decouples orchestration language from tooling. The DETECT_TRACKER boot sequence (Jira → Linear → GitHub → Asana → markdown) with session-start detection is solid. Any team can plug in their tracker and the orchestration language stays constant.

**SM 4-mode split** (SM-GATE / SM-PLAN / SM-RETRO / SM-UNBLOCK) is the right separation of concerns. Each mode loads only its 1-3 relevant skill files. The SM-GATE checklist has 13 concrete items with binary pass/fail — no vagueness.

**Loop spec per story** (Fix 10B) — GOAL / VERIFIER / CRITERIA / STOP WHEN, with VERIFIER required to be an automated command, is the right gate design. Prevents subjective "done" calls.

**Phase Parallelism documentation** (Fix 11D) — correctly identifies that database_architect, cloud_architect, and finops_architect can run concurrently in DESIGN since their inputs (PRD + architecture) are the same and their outputs don't depend on each other. This is real throughput work.

**Memory discipline file split** — context-memory-discipline.md (always-loaded, 97 lines) vs memory-management.md (fileMatch on init_docs/ only) vs phase-reporting.md (fileMatch on docs/phase-*/) is the right pattern. Don't pay for context unless you're in that directory.

**GIT_MODE detection** prevents silent failure when a remote isn't available. The downgrade path (`push fails → downgrade to LOCAL, notify SM-UNBLOCK`) is the right error-handling pattern.

**Mode 5 Lean** is pragmatic. Three roles covering 10 original roles, with a simpler loop spec and a 4-iteration cap instead of 8, correctly trades depth for speed for solo/small-team contexts.

---

## LOWS — Critical Problems

### 1. The Hook IS the Constitution (Architecture Inversion)

`elite-team-orchestrator.kiro.hook` is ~893 lines of prompt that duplicates everything in `team-orchestrator.md`. The hook fires on **every** `promptSubmit` — including Mode 3 bug fixes, questions, and conversational turns. Fix 8A's HOOK COMPLEXITY GATE (return immediately if not Mode 1/4) is the band-aid, but the LLM still has to evaluate that gate, parse the 900-line prompt, and then return. That's token waste on every single turn.

The correct architecture is the inverse: **hook = thin router (≤50 lines)**, steering files = constitution. The hook should detect mode and load steering files, not be the constitution itself.

### 2. CLAUDE.md Has Become Unmaintainable

At 1,668 lines, CLAUDE.md is a running log of 11 fix iterations. The "applied fixes" sections (Fixes 1–11) describe changes that are already baked into the steering files. They serve no operational purpose — they're a history log. Every session that loads CLAUDE.md pays for 1,600+ lines of historical commentary. The PENDING CLEANUP section at line 1,413 has been "pending" across multiple sessions.

### 3. Contradiction: Discovery vs Mode Selection (Lines 97–133)

`orchestrator-routing.md` has two CRITICAL MANDATORY rules that conflict:

- **Lines 97–114**: "Discovery Engine runs FIRST. This file only fires AFTER discovery completes."
- **Lines 117–133**: "On the FIRST request, you MUST present mode options to the user BEFORE doing anything else. No auto-detection."

These cannot both be true. Discovery recommends a mode. The mode table is presented before a mode is selected. If discovery runs first and recommends Mode 2, does the user still see all 5 mode options? Neither rule defers to the other.

### 4. Seven Dead Hooks Are Still on Disk

Hooks 01–05, `context-rot-detection.kiro.hook`, and `enforce-orchestrator-pipeline.kiro.hook` are all `"enabled": false` and marked "SUPERSEDED." They exist solely "for reference." They add cognitive load to anyone reading the hooks directory and create false confidence that the system has more active rules than it does. They should be archived or deleted.

### 5. data_engineer / mobile_engineer / data_scientist Missing from the Hook

These three roles were created (Tasks #16–18) with full skill files and matrix entries. But the active hook's DEVELOP and LAUNCH sections only activate: `backend_lead`, `frontend_lead`, `ml_engineer`, `senior_engineer_be/fe`, `qa_engineer`, `devops_engineer`, `sre_engineer`, `technical_writer`. The new roles will never fire in a Mode 1/4 run because the hook has no trigger conditions for them.

The Phase Parallelism rules (Fix 11D) correctly reference `data_scientist → website_creator → scrum_master` in LAUNCH, but the hook's RELEASE section only activates `website_creator`, `devops_engineer`, `sre_engineer`, `technical_writer`. Data scientist is missing.

### 6. Memory Continuity Is Effectively Broken

The memory architecture references `lessons.md`, `decisions.md`, and `project_map.md` in multiple places (CLAUDE.md §1, memory-management.md, hooks 03/04). None of these files exist on disk. The hooks that were responsible for writing them (03-memory-discipline, 04-auto-memory-retrieval, 05-compression-feedback) are disabled. The checkpoint system just had its first entry written today — it was empty before this session. There is no cross-session memory.

### 7. senior_engineer_be and senior_engineer_fe Share 8 Identical Files

Both roles have their own copies of: `code_review_excellence.md`, `concurrency_safety.md`, `debugging_methodology.md`, `error_handling_strategies.md`, `feature_flags_safely.md`, `performance_profiling.md`, `refactoring_safely.md`, `tdd_red_green_refactor.md`. These 8 files are duplicated. When one needs updating, both need updating — and they'll inevitably drift.

### 8. Mode 4 "Lite vs Standard" Is Undefined

The testing table in `orchestrator-routing.md` distinguishes Mode 4 Lite (≥60% coverage) from Mode 4 Standard (≥70% coverage). No definition exists for what makes a Mode 4 run "Lite" vs "Standard." The user selects Mode 4 and gets one of two coverage requirements with no way to know which applies.

### 9. $TRACKER Translation Is Jira-Centric

The translation table maps `$TRACKER.createProject`, `$TRACKER.createEpic`, `$TRACKER.createSprint` etc. to either "jira.*()" or "markdown file at /docs/." There's no Linear translation (Linear uses cycles/projects, not sprints/epics), no GitHub Projects translation (uses iterations/milestones), no Asana translation (uses sections/projects). TRACKER_MODE=linear resolves to the Jira API call at runtime, which will fail.

### 10. `context-memory-discipline.md` Duplicates CLAUDE.md Fix 8

Both define degradation tiers (PEAK/GOOD/DEGRADING/CRITICAL) with slightly different thresholds. CLAUDE.md Fix 8 defines GOOD as "5-7 reads," context-memory-discipline.md doesn't specify read numbers — it uses context percentage. Having two authoritative sources for the same discipline rules means the LLM may pick whichever was loaded last.

---

## FILES TO DELETE

These files are confirmed dead, superseded, and adding zero value:

| File | Reason |
|------|--------|
| `hooks/01-token-discipline.kiro.hook` | Superseded by CLAUDE.md Fix 8 |
| `hooks/02-context-discipline.kiro.hook` | Superseded by CLAUDE.md Fix 8 |
| `hooks/03-memory-discipline.kiro.hook` | Superseded by CLAUDE.md Fix 8 |
| `hooks/04-auto-memory-retrieval.kiro.hook` | Superseded by CLAUDE.md Fix 8 |
| `hooks/05-compression-feedback.kiro.hook` | Superseded by CLAUDE.md Fix 8 |
| `hooks/context-rot-detection.kiro.hook` | Superseded by CLAUDE.md Fix 8 |
| `hooks/enforce-orchestrator-pipeline.kiro.hook` | Superseded by elite hook v2 |
| `kiro/.DS_Store` | macOS noise |
| `kiro/skills/.DS_Store` | macOS noise |

9 files. Total recovery: minor disk, major cognitive clarity.

---

## IMPROVEMENTS: CONTEXT + TOKENS + MEMORY DISCIPLINE

### A. Invert the Hook Architecture (High Impact)

Replace the 900-line hook with a thin 50-line router:

```json
{
  "name": "Orchestrator Router",
  "when": { "type": "promptSubmit" },
  "then": {
    "type": "askAgent",
    "prompt": "Run ENV detection (DETECT_TRACKER + DETECT_REMOTE). Log [ENV] line. If task is Mode 1/4/5 build task: load team-orchestrator.md, skill-selection-matrix.md. If DEVELOP phase: load loop-engine.md. Delegate all role execution to team-orchestrator.md — do not replicate its content here. Return immediately for Mode 2/3/conversational/bug-fix prompts."
  }
}
```

All role definitions, artifact chains, gates, and sprint logic stay in `team-orchestrator.md`. The hook becomes a loader, not a constitution. This eliminates the 900-line context hit on every prompt and fixes the duplication problem.

### B. Surgery on CLAUDE.md

Split into three files:

- `CLAUDE-operating.md` — Session start, modes, Caveman Ultra rules, smart triggers (active instructions only, ~200 lines)
- `CLAUDE-history.md` — Fix 1–11 descriptions (archive, not always loaded, ~1,200 lines)  
- `CLAUDE-pending.md` — Pending cleanup checklist (~100 lines)

Only `CLAUDE-operating.md` needs always-loaded. The history is reference-only and should never be in the active context window.

### C. Resolve the Discovery vs Mode-Selection Contradiction

The correct canonical order:

```
1. ENV detection (DETECT_TRACKER + DETECT_REMOTE)
2. Classify request type (build task vs bug fix vs question)
3. If build task AND no explicit "mode N" bypass:
   → discovery-engine.md asks 7 questions → scores → recommends mode
   → show recommended mode + option to override
   → user confirms
4. If "mode N" explicit → skip discovery, use that mode
5. If bug fix / question / refactor → Mode 3 direct
```

Remove the "CRITICAL RULE: present mode options to the user BEFORE doing anything" at line 119 — it contradicts the discovery engine. Discovery IS the mode presentation step.

### D. Fix Mode 4 Lite vs Standard

Define the trigger explicitly in `orchestrator-routing.md`:

```
Mode 4 Lite:      project has ≤ 5 user stories OR single sprint planned
Mode 4 Standard:  project has > 5 user stories OR multi-sprint plan
```

Or collapse to a single Mode 4 with per-phase coverage ramp: Phase 1 ≥60%, Phase 2+ ≥70%.

### E. Add the Three New Roles to the Hook's DEVELOP + LAUNCH Sections

The hook needs explicit activation paths for:

- `data_engineer` — triggers when story labels include `data/pipeline`, `data/streaming`, `data/batch`, `data/cdc`
- `mobile_engineer` — triggers when story labels include `mobile/ios`, `mobile/android`, `mobile/rn`
- `data_scientist` — triggers in LAUNCH phase before website_creator (as per Phase Parallelism rules)

Without this, the 20 skill files and all matrix rows for these roles are unreachable.

### F. Deduplicate senior_engineer_be/fe Shared Skills

Move the 8 shared files to `kiro/skills/shared/`. Update both SKILL.md files and the matrix to reference `shared/<filename>.md`. Role-specific overlays stay in their own directories. This cuts 88 duplicate files to 8 shared + role-specific additions (~40% reduction in that skill set).

### G. Expand $TRACKER Translation Table

Add per-TRACKER_MODE sections:

| $TRACKER verb | TRACKER_MODE=linear | TRACKER_MODE=github | TRACKER_MODE=asana |
|---|---|---|---|
| createSprint | createCycle() | createIteration() | createSection() |
| createEpic | createProject() | createMilestone() | createProject() |
| createStory | createIssue() | createIssue() | createTask() |

Without this, any team not on Jira gets broken $TRACKER calls that silently fall through to markdown.

### H. Initialize the Memory System

The three memory files need to exist for the system to function as documented:

- `loopEngineering/kiro/memory/project_map.md` — module-level map of the kiro system itself
- `loopEngineering/kiro/memory/lessons.md` — corrections and rules from past sessions
- `loopEngineering/kiro/memory/decisions.md` — ADR index

The disabled memory hooks (03/04/05) had the right write patterns. Extract those write protocols into a section of `CLAUDE-operating.md` that fires on session end — no hook required, just instructions to the LLM.

### I. Make context-memory-discipline.md the Single Source for Discipline Tiers

Remove the degradation tier definitions from CLAUDE.md Fix 8 (they'll be in the archive anyway). `context-memory-discipline.md` is always-loaded and should be the authoritative source. One definition, one place.

---

## ROLE + SKILL COVERAGE GAPS

| Gap | Detail | Impact |
|-----|--------|--------|
| No `market_researcher` in ongoing DEVELOP/LAUNCH | Market conditions can change mid-build; no re-invocation path | Medium |
| No `website_creator` in DESIGN phase | Content strategy should inform architecture; only appears in RELEASE | Low |
| `product_manager/experiment.md` doesn't exist | Only in matrix "skip" column — naming mismatch with `experiment_design_ab.md` | Low |
| `website_creator` (24 files) too broad | Should split: SEO, conversion, content, technical subdomains | Medium |
| `security_engineer` (21 files) too broad | Already has good matrix coverage; but file count creates maintenance risk | Low |
| `database_architect` (17 files) is the heaviest non-security role | Matrix coverage is excellent; no action needed | None |

---

## PRIORITY MATRIX

| Fix | Impact | Effort | Priority |
|-----|--------|--------|----------|
| Delete 7 dead hooks + DS_Store | High (clarity) | Zero | Do now |
| Add new roles to hook DEVELOP/LAUNCH | High (correctness) | Small | Do now |
| Resolve discovery vs mode-selection contradiction | High (correctness) | Small | Do now |
| Invert hook architecture | Very High (tokens) | Medium | Fix 12 |
| Split CLAUDE.md | High (maintainability) | Medium | Fix 12 |
| Initialize memory files | High (continuity) | Small | Fix 12 |
| Define Mode 4 Lite vs Standard trigger | Medium (clarity) | Tiny | Fix 12 |
| Expand $TRACKER translation for non-Jira | Medium (correctness) | Small | Fix 12 |
| Deduplicate senior_engineer shared skills | Medium (maintainability) | Medium | Fix 13 |
| Single source for discipline tiers | Low (consistency) | Small | Fix 13 |

---

## SUMMARY VERDICT

**Architecture:** Correct direction, wrong execution layer. The skill matrix + loop spec + phase parallelism are the right foundations. But the active hook has absorbed the constitution and become a God Object. Fix the inversion and the whole system becomes maintainable.

**Token discipline:** Good on paper (CAVEMAN ULTRA, degradation tiers, 5-line takeaway), broken in practice (900-line hook fires on every prompt, 1,668-line CLAUDE.md, dead memory system).

**Coverage:** 261 skill files across 22 roles is impressive depth. The three new roles (data_engineer, mobile_engineer, data_scientist) are well-documented but unreachable because the hook doesn't know about them.

**Memory/continuity:** Not functioning. Cross-session context is lost every time. The memory architecture is designed but not initialized.

**Immediate wins (zero-effort):** Delete the 7 dead hooks. That alone removes confusion, reduces directory noise, and eliminates the possibility of accidentally re-enabling a superseded rule.
