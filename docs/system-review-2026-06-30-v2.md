# Kiro System Deep Review — 2026-06-30 (v2, post Fixes 12–15)

Evidence-based. Every finding references the exact file and line where the issue lives.
Fixes 1–15 all implemented. This review finds what the fixes introduced, missed, or broke.

---

## HIGHS — What Is Working Well

**H1. Always-loaded context reduction: massive.**
CLAUDE.md went from 1,918 lines (always-loaded) to ~700 lines. The hook went from 900 lines to ~110. Together this saves roughly 1,700 tokens on every single prompt. The split into CLAUDE.md (ongoing) + CLAUDE-implemented.md (history) is the right architecture.

**H2. Thin hook router is structurally correct.**
The hook no longer replicates the constitution. It is a 6-step router that detects ENV, classifies, loads steering files, and delegates. The handoff compression note (≤300 tokens per role output) and Goal Anchor injection (every 10 tool calls) are the right signals to have in the hook where they fire automatically.

**H3. shared/ directory solves the real duplication problem.**
8 skill files moved from two role dirs into one canonical location. Both SKILL.md files and the matrix now reference `../shared/`. This is the correct pattern for cross-role skills.

**H4. $TRACKER abstraction is now complete.**
The translation table covers 5 tracker modes (jira/linear/github/asana/markdown) × 9 verbs. This is production-usable.

**H5. design_system_gate.md fills a genuine quality gap.**
The 6-section gate (typography, color, spacing, layout direction, animation intent, component voice) with an explicit anti-pattern reject table is well-structured. The prerequisite rows in the matrix are correctly placed. Banning Inter/Roboto/Arial/Space Grotesk in typography is a strong and correct call.

**H6. Fix 15 closes the reporting gap.**
All 6 phase-end reports now have templates. The Sprint Discipline Card is the right mechanism — 5 rows, blocking, every sprint. SM-RETRO now can't skip discipline accounting.

**H7. Memory system initialized with right structure.**
lessons.md (confidence-scored), decisions.md (temporal ADR with valid_from/valid_to), project_map.md (orientation before file reads). The lifecycle rules in project_map.md (who writes, who reads, when) are correct.

---

## CRITICAL — Breaking Issues That Must Be Fixed

### C1. DUPLICATE REPORT DEFINITIONS — Wrong file names, two formats
**Files:** `orchestrator-routing.md` (lines 419–476) and `team-orchestrator.md` (Fix 15B section)
**Problem:** orchestrator-routing.md defines:
- Section E: `JIRA-TASK-REPORT.md` with Epic Summary / Story Breakdown / Task Detail / Sprint Metrics tables
- Section F: `GIT-TRACKING-REPORT.md` with Branch Summary / Commit Log / Git Discipline tables

Fix 15B added to team-orchestrator.md:
- `JIRA-REPORT.md` with Velocity / Story Status / Blocker Log tables
- `GIT-REPORT.md` with Commit Summary / PR Health / Branch Hygiene / Coverage Delta tables

**Two different file names, two different schemas, for the same reports.** The model will produce either format depending on which file it loaded most recently. No report will be comparable phase-to-phase.
**Fix:** Delete sections E and F from `orchestrator-routing.md`. team-orchestrator.md's Fix 15B templates are the canonical versions. Update orchestrator-routing.md's "All 6 reports" references to point to team-orchestrator.md.

---

### C2. PRIORITY TABLE CONTRADICTS ITSELF
**File:** `orchestrator-routing.md` lines 253–257
**Problem:**
```
Line 253: Mode Override > Mode 1 > Mode 4 > Mode 2 > Mode 5 > Mode 3
Line 256: "If both Mode 1 and Mode 4 could match... Mode 4 wins."
```
Mode 1 > Mode 4 in the priority list, but Mode 4 wins when both match. These say opposite things. Every "build an app" request is ambiguous between Mode 1 and Mode 4 if a spec workflow is running.
**Fix:** Replace line 256 with: `"Mode 4 wins over Mode 1 ONLY when .kiro/specs/ directory already exists from a prior spec workflow run. Otherwise Mode 1 wins."` Then update the priority table to reflect this: `Mode Override > Mode 4 (when specs/ present) > Mode 1 > Mode 2 > Mode 5 > Mode 3`.

---

### C3. NESTED CODE BLOCK IN SM-RETRO DEFINITION WILL BREAK PARSING
**File:** `team-orchestrator.md` — SM-RETRO definition section
**Problem:** The SM-RETRO definition is inside a triple-backtick code block (lines ~121–147). Fix 15C added another triple-backtick block *inside* that block (the Sprint Discipline Card). Triple-backtick nesting breaks in every Markdown parser — the inner block closes the outer block prematurely, mangling the rest of the SM modes definition.
**Fix:** Remove the inner code fence. Represent the Sprint Discipline Card table using plain Markdown table syntax inside the outer code block, or move the card template OUTSIDE the SM modes code block entirely (as a standalone section headed `### SM-RETRO — SPRINT DISCIPLINE CARD (Fix 15C)`).

---

### C4. SKILL LOADING PROTOCOL STEP 0 DOESN'T HANDLE SHARED/ PATHS
**File:** `skill-selection-matrix.md` lines 315–319
**Problem:** Step 0 says: `"confirm it exists at kiro/skills/<role>/<filename>.md"`. But shared/ files are referenced as `shared/design_system_gate.md` in the matrix, and the role for website_creator, mobile_engineer, frontend_lead would expand to `kiro/skills/website_creator/shared/design_system_gate.md` — which does **not exist**. The actual path is `kiro/skills/shared/design_system_gate.md`.
**Fix:** Update Step 0 to: `"If filename starts with 'shared/', resolve as kiro/skills/shared/<filename without 'shared/' prefix>. Otherwise resolve as kiro/skills/<role>/<filename>.md."`

---

### C5. ALWAYS-LOADED CONTEXT TOTAL HAS CREPT BACK UP
**Files:** `orchestrator-routing.md` (477 lines) + `context-memory-discipline.md` (120 lines) + `CLAUDE.md` (still has Fix 12–15 full detail)
**Problem:** After the split, CLAUDE.md was supposed to be ≤700 lines of operating rules + pending fixes. But Fixes 12, 13, 14, 15 are all marked IMPLEMENTED yet their full 150–200 line detail sections are still in CLAUDE.md, not archived to CLAUDE-implemented.md. CLAUDE.md is likely 680+ lines. Add orchestrator-routing.md (always-loaded, 477 lines) and the always-loaded total is ~1,300 lines — approaching the pre-split level.

**Context ROT check:**
- orchestrator-routing.md: 477 lines → **YELLOW** (threshold: 300–500)
- CLAUDE.md: ~680 lines → **YELLOW** (threshold: <700)
- Total always-loaded steering: ~1,300 lines → **RED** (threshold: >500 for all steering combined)

**Fix A:** Move Fix 12, 13, 14, 15 implemented sections from CLAUDE.md to CLAUDE-implemented.md. Keep only OPERATING RULES + any genuinely pending fixes in CLAUDE.md.
**Fix B:** Move 3 sections from orchestrator-routing.md to team-orchestrator.md (where they belong):
1. `PHASE PARALLELISM RULES` (~40 lines) — pipeline content, not routing
2. `SELF-CHECK` (~15 lines) — Mode 1 pipeline content
3. `PER-PHASE REPORTS sections E+F` (~60 lines) — now superseded by Fix 15B, delete entirely

---

## MEDIUM — Important Improvements

### M1. HOOK HAS NO COMPLEXITY GATE — fires on every message including trivial ones
**File:** `elite-team-orchestrator.kiro.hook`
**Problem:** `"when": {"type": "promptSubmit"}` — fires for every prompt, including "what time is it?", "explain OAuth", "thanks". For Mode 3 (direct execution), the hook adds 110 lines of processing before passing through to the LLM. Fix 8 originally added a HOOK COMPLEXITY GATE but it was removed during the v3 rewrite.
**Fix:** Add back the gate as Step 0 in the hook:
```
STEP 0 — COMPLEXITY GATE
If prompt is ≤8 words AND contains no BUILD/CREATE/MAKE/DEVELOP/IMPLEMENT/DEPLOY/DESIGN/PLAN keyword:
  → Skip all steps. Respond directly. No routing.
If prompt is a continuation of an active session (mode already logged this session):
  → Skip Steps 1-3. Go directly to Step 4 for the active mode.
```

### M2. MODE 2 TABLE MISSING THREE ROLES: data_engineer, mobile_engineer, data_scientist
**File:** `orchestrator-routing.md` lines 149–163
**Problem:** The Mode 2 trigger table has 13 role rows but data_engineer, mobile_engineer, and data_scientist are absent. If a user says "design me a Kafka pipeline" in Mode 2, there's no matching row to trigger data_engineer. The model will either guess or trigger a wrong role.
**Fix:** Add three rows:
```
| "pipeline / streaming / data engineering / Kafka / Spark / dbt / batch" | Data Engineer | pipeline-design doc |
| "mobile / iOS / Android / React Native / offline sync / push notifications" | Mobile Engineer | mobile-design doc |
| "funnel analysis / cohort / A/B test / EDA / retention / data storytelling" | Data Scientist | analysis doc |
```

### M3. SKILL LOADING PROTOCOL STEP 6 NOT ENFORCED IN DISCIPLINE RULES
**Files:** `skill-selection-matrix.md` line 326, `context-memory-discipline.md`
**Problem:** Step 6 says "Do NOT keep full skill file content in context after extraction — summarize to 5-line takeaway." This is a critical token discipline rule that prevents skill files (some 200+ lines) from bloating context. But it only appears in the skill matrix (manual-inclusion) — it's not in context-memory-discipline.md (always-loaded). The model only sees this rule when the matrix is loaded, and may forget it mid-session.
**Fix:** Add to context-memory-discipline.md Section 4 (SELF-ADAPTIVE CONTEXT PRUNING):
```
SKILL FILES: After extracting principles from a skill file, reduce to 5-line takeaway in context.
             Do NOT hold the full 200-line file while producing the artifact. Summarize → produce → discard.
```

### M4. shared/ DIRECTORY HAS NO SKILL.MD INDEX
**File:** `kiro/skills/shared/` (missing `SKILL.md`)
**Problem:** Every other role directory has a SKILL.md. The shared/ directory doesn't. Step 0 of the SKILL LOADING PROTOCOL falls back to "role's top-level SKILL.md for context" if a file is missing — but shared/ has no SKILL.md, so this fallback silently fails for shared/ files.
**Fix:** Create `kiro/skills/shared/SKILL.md` listing all 9 files with their purpose and the path convention.

### M5. impl-decisions.md HAS NO MATRIX TRIGGER
**Files:** `team-orchestrator.md` (Fix 15A), `skill-selection-matrix.md`
**Problem:** Fix 15A added impl-decisions.md to the artifact chain in team-orchestrator.md. But the skill-selection-matrix.md has no row that says "when implementing a non-trivial story → create/update impl-decisions.md". The implementing role (senior_engineer_be/fe) will see the chain diagram but has no explicit matrix trigger to remember to write the log.
**Fix:** Add to senior_engineer_be and senior_engineer_fe sections in skill-selection-matrix.md:
```
| Writing impl-decisions entry | [no skill file needed] — template in Fix 15A; write entry for any non-trivial architectural choice made during DO step |
```

### M6. HOOK STEP 4 DOESN'T SPECIFY MEMORY-MANAGEMENT.MD LOAD AT SESSION START
**File:** `elite-team-orchestrator.kiro.hook`
**Problem:** `kiro/steering/memory-management.md` is a `fileMatch: init_docs/` file — it loads on init_docs/ file matches. But the hook's Step 4 never loads it explicitly. For sessions without init_docs/ files present, memory-management.md may never load, meaning the session-start memory retrieval protocol doesn't fire.
**Fix:** Add to Step 4:
```
ALL MODES (session start only):
  IF kiro/docs/lessons.md OR kiro/docs/decisions.md exist:
    LOAD: kiro/steering/memory-management.md
    Execute memory retrieval before first role activates.
```

### M7. decisions.md AND lessons.md MISSING ENTRIES FOR FIXES 14 AND 15
**Files:** `docs/decisions.md`, `docs/lessons.md`
**Problem:** ADR-001 through ADR-008 document Fixes 12 and 13 architectural decisions. Fixes 14 and 15 introduced equally significant decisions (design gate prerequisite pattern, Sprint Discipline Card as blocking gate, impl-decisions.md as ephemeral artifact) that have no ADR.
**Fix:** Add ADR-009 through ADR-012 covering:
- ADR-009: UI prerequisite gate approach (design_system_gate.md) vs inline linting rules
- ADR-010: Sprint Discipline Card as SM-RETRO blocker vs optional appendix
- ADR-011: impl-decisions.md as per-sprint ephemeral doc vs permanent ADR index
- ADR-012: shared/ skill directory vs per-role copies

---

## LOW PRIORITY — Polish and Completeness

### L1. Mode 3 trigger description is incomplete
`orchestrator-routing.md` line 173: "Neither Mode 1, Mode 2, nor Mode 4 matches." Should say "nor Mode 5" since Mode 5 has an explicit trigger that, if not met, falls through to Mode 3.

### L2. DISCOVERY-FIRST section duplicates hook Step 3 logic
`orchestrator-routing.md` lines 97–115 describes discovery-first flow. Hook Step 3 also describes this. They're consistent but two places to maintain. Low risk since both are correct.

### L3. Mode 5 LEAN LOOP SPEC missing from Fix 7 cross-reference
`orchestrator-routing.md` line 224 defines LEAN LOOP SPEC. loop-engine.md (Fix 7) defines the full loop spec. These should explicitly cross-reference each other so the QUALITY role knows which spec format to expect in lean mode.

### L4. website_creator SKILL.md has no "see matrix" reminder
All other SKILL.md files say "See .kiro/steering/skill-selection-matrix.md for the loading rules." website_creator's SKILL.md does too — but now that it has 4 subdirectories, it should also note that sub-paths (e.g., `conversion/landing_page_patterns.md`) are fully qualified and don't need the subdirectory prepended at the orchestrator level.

### L5. Hook prompt caching note only targets API callers
`elite-team-orchestrator.kiro.hook` end: "API callers: place cache_control..." — but Kiro desktop doesn't use the API directly. This note is currently only relevant if using the API. Should note: "In Kiro desktop, prompt caching is automatic for static steering files — no explicit configuration needed."

---

## FILES TO DELETE OR ARCHIVE

### DELETE — orchestrator-routing.md sections E and F (PER-PHASE REPORTS)
`orchestrator-routing.md` lines 413–476: "Section E. Jira Task Tracking Report" and "Section F. Git Commit/Branch Tracking Report."
These are now superseded by Fix 15B in team-orchestrator.md, with different (better) schemas and different file names. Keeping both creates the C1 confusion. Delete sections E and F entirely. Keep the "All 6 reports (QA, Security, Mapping, Discipline, Jira, Git)" reference line — just remove the inline templates.

### ARCHIVE — Fix 12, 13, 14, 15 detail sections from CLAUDE.md
CLAUDE.md currently has `## FIX 12`, `## FIX 13`, `## FIX 14`, `## FIX 15` in full detail, all marked IMPLEMENTED. These are now history, same as Fixes 1–11. Move to CLAUDE-implemented.md. CLAUDE.md should contain only:
- OPERATING RULES (the 2-page permanent rules section)
- Any genuinely pending or in-progress fixes

Estimated token savings: ~400 lines removed from always-loaded context.

### CONSOLIDATE — SELF-CHECK and PHASE PARALLELISM RULES
Move these from `orchestrator-routing.md` to `team-orchestrator.md`:
- `SELF-CHECK` (lines 352–366) — Mode 1 pipeline checklist; belongs in the constitution
- `PHASE PARALLELISM RULES` (lines 370–410) — pipeline execution content; belongs in the constitution

Orchestrator-routing.md should be purely routing logic: ENV detection, mode classification, mode descriptions, mode priority, bypass conditions.

---

## CONTEXT / TOKEN / MEMORY DISCIPLINE — Specific Findings

### CTM-1. Always-loaded total will hit ROT RED within 2-3 more edits
Current always-loaded:
- `context-memory-discipline.md`: ~120 lines ✅
- `orchestrator-routing.md`: ~477 lines 🟡 YELLOW
- `CLAUDE.md` (with implemented fixes still in): ~680 lines 🟡 YELLOW
- **Total: ~1,277 lines 🔴 RED** (threshold for all steering combined: 500–800 max)

Target after cleanup:
- `orchestrator-routing.md`: ~300 lines (remove E+F, parallelism, self-check)
- `CLAUDE.md`: ~250 lines (archive Fix 12–15 detail, keep only OPERATING RULES)
- Total always-loaded: ~670 lines ✅ GREEN

### CTM-2. Skill file summarization (Step 6) is not being enforced
The "summarize to 5-line takeaway after extraction" rule is invisible when the matrix isn't loaded. High-risk in Mode 3 where only the hook fires. A 200-line skill file left in context after a Mode 2 activation costs ~500 tokens for every subsequent turn in the session.

### CTM-3. 85% threshold offloading has no trigger mechanism
`context-memory-discipline.md` Section 5 defines the 85% offloading rule. But there's no hook or periodic signal that tells the model to check its context level. The model checks this level passively (if it notices), not actively. The Goal Anchor (every 10 tool calls) is the closest thing to a periodic check — but it checks objective drift, not context size.
**Recommendation:** Add to Goal Anchor injection: "At call N, also check: am I above 85% context? If yes, run offloading before continuing."

### CTM-4. lessons.md has only 3 entries after 6 sessions of work
The session-end write protocol (write to lessons.md when corrected or pattern identified) is defined in project_map.md. But there's nothing in the hook or orchestrator that reminds the model to execute it. Every session end passes without updating lessons.md. The memory system is write-once initialized, not actively maintained.
**Recommendation:** Add to SM-RETRO (which runs at sprint end, the natural session boundary) a step: "Before producing retro: read docs/lessons.md + docs/decisions.md. If any pattern from this sprint isn't captured → add it."

### CTM-5. handoff compression rule (≤300 tokens) is in hook but not enforced between sub-agents
The hook says "role output → compress to ≤300 tokens before passing to orchestrator." This is a correct rule. But team-orchestrator.md's role definitions don't have a corresponding reminder that their output should be compressed before handoff. The 300-token limit only exists in the hook, which may not be in context during deep DEVELOP phase work.

---

## ORCHESTRATOR ANALYSIS

| Dimension | Finding | Severity |
|-----------|---------|----------|
| Hook fires on every prompt | No complexity gate — wastes tokens on trivial Mode 3 requests | Medium |
| Hook Step 2 classification | BUILD/SINGLE/FIX → correct, but Mode 5 has no explicit class | Low |
| Priority table vs Mode 4 win condition | Contradictory — Mode 1 > Mode 4 but Mode 4 wins when both match | High |
| DISCOVERY-FIRST rule | Duplicated in hook and orchestrator-routing.md | Low |
| Mode 2 missing 3 roles | data_engineer, mobile_engineer, data_scientist not in trigger table | Medium |
| Mode 3 trigger wording | Missing "nor Mode 5" in description | Low |
| Orchestrator-routing.md size | 477 lines always-loaded — contains pipeline content that belongs in constitution | High |
| Report format duplication | 2 schemas for Jira+Git reports across 2 files | Critical |
| market_researcher re-invocation | Correctly placed in Mode 2 | ✅ |
| $TRACKER abstraction | Complete, 5 trackers × 9 verbs | ✅ |
| Mode 4 Lite vs Standard | Correctly defined | ✅ |
| Phase parallelism rules | Correct but in wrong file (routing vs constitution) | Medium |

---

## SKILL MATRIX ANALYSIS

| Dimension | Finding | Severity |
|-----------|---------|----------|
| Step 0 path resolution for shared/ | Breaks — uses role-relative path, not kiro/skills/shared/ | High |
| Step 6 skill summarization rule | Correct rule but only visible when matrix is loaded | Medium |
| design_system_gate prerequisite rows | Bold markdown in table cells — may not render in all clients | Low |
| website_creator subdirectory paths | Paths like `conversion/landing_page_patterns.md` require updated Step 0 | Medium (already works if Step 0 uses full path) |
| data_engineer, mobile_engineer, data_scientist | All 3 have matrix sections ✅ | ✅ |
| impl-decisions.md trigger | No matrix row for "write impl-decisions entry" activity | Medium |
| Second-pass trigger rules | Only market_researcher and cto have On-demand columns | Medium — other roles lack this |
| shared/SKILL.md missing | No index file for shared/ directory | Medium |

---

## FIX ROADMAP (prioritized)

| Fix ID | Description | Files | Priority |
|--------|-------------|-------|----------|
| Fix 16A | Delete sections E+F from orchestrator-routing.md | orchestrator-routing.md | 🔴 Critical |
| Fix 16B | Resolve priority contradiction (Mode 1 vs Mode 4) | orchestrator-routing.md | 🔴 Critical |
| Fix 16C | Fix nested code block in SM-RETRO definition | team-orchestrator.md | 🔴 Critical |
| Fix 16D | Update Step 0 to handle shared/ paths | skill-selection-matrix.md | 🔴 Critical |
| Fix 16E | Archive Fix 12–15 from CLAUDE.md to CLAUDE-implemented.md | CLAUDE.md, CLAUDE-implemented.md | 🟠 High |
| Fix 16F | Move SELF-CHECK + PHASE PARALLELISM to team-orchestrator.md | orchestrator-routing.md → team-orchestrator.md | 🟠 High |
| Fix 17A | Add HOOK COMPLEXITY GATE (Step 0) back to hook | elite-team-orchestrator.kiro.hook | 🟠 High |
| Fix 17B | Add data_engineer / mobile_engineer / data_scientist to Mode 2 table | orchestrator-routing.md | 🟡 Medium |
| Fix 17C | Add skill summarization rule to context-memory-discipline.md | context-memory-discipline.md | 🟡 Medium |
| Fix 17D | Create kiro/skills/shared/SKILL.md | shared/SKILL.md | 🟡 Medium |
| Fix 17E | Add impl-decisions.md trigger row to skill matrix | skill-selection-matrix.md | 🟡 Medium |
| Fix 17F | Add memory file load to hook Step 4 | elite-team-orchestrator.kiro.hook | 🟡 Medium |
| Fix 17G | Add Goal Anchor context-level check (85% threshold reminder) | context-memory-discipline.md | 🟡 Medium |
| Fix 17H | Add lessons.md write step to SM-RETRO | team-orchestrator.md | 🟡 Medium |
| Fix 18A | Add ADR-009–012 to decisions.md | docs/decisions.md | 🟢 Low |
| Fix 18B | Fix Mode 3 trigger wording (add "nor Mode 5") | orchestrator-routing.md | 🟢 Low |
| Fix 18C | Add loop-engine.md ↔ lean loop spec cross-reference | orchestrator-routing.md, loop-engine.md | 🟢 Low |
| Fix 18D | Update hook prompt caching note for Kiro desktop | elite-team-orchestrator.kiro.hook | 🟢 Low |

---

## SUMMARY SCORECARD

| Category | Score | Notes |
|----------|-------|-------|
| Hook architecture | 8/10 | Thin router is correct; needs complexity gate back |
| Orchestrator routing | 6/10 | Priority contradiction + duplicate reports are breaking issues |
| Skill matrix | 7/10 | Core logic correct; shared/ path resolution broken |
| Context discipline | 6/10 | Always-loaded total crept back up; skill summarization not enforced |
| Token discipline | 7/10 | Hook savings significant; Step 6 enforcement gap is real cost |
| Memory system | 5/10 | Correct structure but lessons.md/decisions.md not actively maintained |
| Reporting | 7/10 | All 6 templates exist now; but duplicate schemas for Jira+Git create ambiguity |
| Design gate | 9/10 | Strong concept, well-structured; minor shared/ path issue |
| Overall | 7/10 | Strong foundation, 4 critical bugs to fix before next run |

*Generated: 2026-06-30 | Reviewed by: deep analysis of all active steering files*
