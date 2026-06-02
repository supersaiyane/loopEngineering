# KIRO SYSTEM — ONGOING FIXES
# Fixes 1–15 are APPLIED and documented in CLAUDE-implemented.md (reference only, never auto-loads).
# This file = pending work only. Read this every session. Skip CLAUDE-implemented.md unless debugging.

Last updated: 2026-07-10
# All fixes through Fix 42C implemented. See CLAUDE-implemented.md for full history.
# Next: Dry Run v10 to find new gaps.

---
# No pending fixes. System is clean.
---



---

## MASTER FIX REGISTER — All Fixes (Fix 1 → Fix 42C)
Last synced: 2026-07-10 | Total: 47 sub-fixes across 42 fix groups | All implemented ✅

| Fix | Name | Why It Was Needed | Status | File(s) |
|-----|------|-------------------|--------|---------|
| Fix 1 | $TRACKER Abstraction | Hard-coded `jira.*` calls broke pipeline when Jira was unavailable | ✅ | orchestrator-routing.md, team-orchestrator-core.md |
| Fix 2 | Scrum Master Role Split | SM gating itself — planning + gates + retro in one call | ✅ | team-orchestrator-sprint.md |
| Fix 3 | FE/BE Skill Differentiation | FE and BE engineers had identical skill sets | ✅ | skills/senior_engineer_be/, skills/senior_engineer_fe/ |
| Fix 4 | Steering File Inclusion | Steering files not loading before agents activated | ✅ | orchestrator-routing.md |
| Fix 5 | Conflict Resolution Protocol | No arbitration chain when CTO/Architect/Security disagreed | ✅ | team-orchestrator-core.md |
| Fix 6 | Lean Team Mode (Mode 5) | No lightweight path for small teams / solo developers | ✅ | orchestrator-routing.md, discovery-engine.md |
| Fix 7 | Loop Engineering Integration | Linear story execution — no PLAN→DO→VERIFY→DECIDE loop | ✅ | loop-engine.md |
| Fix 8 | Token/Memory/Context Discipline | No token budgets, context rot undetected, per-role limits missing | ✅ | context-memory-discipline.md, hook |
| Fix 9 | Skill Activation Pipeline | Skills loaded randomly; job label → skill file mapping was guesswork | ✅ | hook, skill-selection-matrix.md |
| Fix 10 | Remaining Execution Gaps | Code not persisting to disk; loop spec gaps; sprint parallelism undefined | ✅ | team-orchestrator-core.md, loop-engine.md |
| Fix 11 | Routing + Matrix Precision | Routing rules conflicting; matrix had "ALL files" entries | ✅ | orchestrator-routing.md, skill-selection-matrix.md |
| Fix 12 | Hook Rewrite as Thin Router | Hook was 1,000+ lines; constitution embedded in router | ✅ | elite-team-orchestrator.kiro.hook |
| Fix 13 | Cleanup + Deduplication | 7 dead hooks; duplicate discipline tiers; shared skills scattered | ✅ | hooks/, kiro/skills/shared/ |
| Fix 14 | Design System Enforcement | No gate preventing agents from bypassing the design system | ✅ | skills/shared/design_system_gate.md |
| Fix 15 | Documentation + Reporting Gaps | Missing report templates; no Sprint Discipline Card at retro | ✅ | team-orchestrator-sprint.md |
| Fix 16 | Critical Bugs | Duplicate report sections, mode routing errors, skill loading failures | ✅ | orchestrator-routing.md, team-orchestrator-core.md |
| Fix 17 | Medium Improvements | Discipline gaps compounding silently over time | ✅ | multiple steering files |
| Fix 18 | Low Priority Polish | Health-check signals, minor correctness, completeness | ✅ | multiple files |
| Fix 19 | Team-Orchestrator Split | 1,264-line single file caused lost-in-middle attention degradation | ✅ | team-orchestrator-core.md + team-orchestrator-sprint.md |
| Fix 20 | Performance + Intelligence | Step 0 keyword expansion; role handoff structure missing | ✅ | hook, team-orchestrator-core.md |
| Fix 21 | Structural Integrity | Missing shared skill files failing silently at session start | ✅ | hook Step 5, skill-label-index.md |
| Fix 22 | Dry Run v1 Gaps | Hook STEP 6 conflicting with Fix 20C ROLE HANDOFF template | ✅ | hook |
| Fix 23 | Dynamic Skill × Agent Selection | Static keyword-match matrix; filename guessing ~30% wrong | ✅ | skill-selection-matrix.md, team-orchestrator-core.md |
| Fix 24 | JWT Dry Run Gap Closure | Mode auto-inference stalling on single-shot prompts; 4 red gaps | ✅ | hook STEP 3, orchestrator-routing.md |
| Fix 25 | Dry Run 2 Gap Closure (19 items) | 26 filename mismatches in skill-label-index; 19 gaps across dry runs | ✅ | skill-label-index.md, steering files, hook |
| Fix 26 | Fraud Platform Dry Run Gaps | checkpoint.md TYPE column migration; 5 gaps from fraud platform run | ⚠️ Absorbed into Fix 27+ | superseded |
| Fix 27 | P0 Calibration + Runtime Enforcement | Degradation thresholds for 30K-era; mode false positives; VERIFIER theater | ✅ | context-memory-discipline.md, hook, loop-engine.md |
| Fix 28 | P1 Attention + Memory | Lessons decorative not active; QUICK REFERENCE cards missing | ✅ | team-orchestrator-core.md, skill files |
| Fix 29 | Dry Run v2 Gaps | Design system owner undefined; creation protocol missing | ✅ | team-orchestrator-core.md |
| Fix 30 | Dry Run v3 Gaps (7 items) | 7 gaps from Healthcare/FinTech/B2B SaaS/IoT scenarios | ✅ | multiple files |
| Fix 31 | Dry Run v4 Gaps (8 items) | 8 gaps from data lake/edtech/marketplace/IoT adversarial scenarios | ✅ | multiple files |
| Fix 32 | Doc Knowledge Architecture | No source-of-truth framework; doc conflicts silent; 6-doc structure undefined | ✅ | team-orchestrator-core.md, team-orchestrator-sprint.md, skill templates |
| Fix 33A | IAM Budget Pre-Warning | Auth scope routinely 1.5–2× estimates; no warning before sprint planning | ✅ | team-orchestrator-core.md |
| Fix 33B | OQ Auto-Prompt | SM-PLAN stalling on open questions with no resume phrase | ✅ | team-orchestrator-core.md |
| Fix 34 | Strix Security Integration | security_engineer had no specialized pentesting skill files | ✅ | skills/security_engineer/ |
| Fix 35 | Dual-Routing Conflict | Two competing routing hooks causing undefined behavior at prompt entry | ✅ | orchestrator-routing.md |
| Fix 36 | Hook SYSTEM AUTHORITY | Kiro's native "Build a Feature" dialog overriding orchestration on every prompt | ✅ | elite-team-orchestrator.kiro.hook |
| Fix 37 | Ponytail Lazy Senior Dev | Agents writing 200+ line custom code when stdlib/deps already covered it | ✅ | team-orchestrator-rules.md, team-orchestrator-core.md |
| Fix 38A | Confidence Signal List (25 signals) | Only 8 signals; enterprise prompts scoring LOW → wrong mode | ✅ | elite-team-orchestrator.kiro.hook |
| Fix 38B | Mobile Engineer Auto-Routing | No automatic mobile_engineer activation for Platform=Mobile | ✅ | discovery-engine.md |
| Fix 38C | Ponytail GATE S2 Commit Block | Ponytail check had no commit-time enforcement; violations reached main | ✅ | team-orchestrator-rules.md (GATE S2 item 5) |
| Fix 39A | GATE S2 Jira Ponytail Verdict | Jira comment template missing Ponytail: PASS/FAIL — audit trail incomplete | ✅ | team-orchestrator-rules.md (GATE S2 item 6) |
| Fix 39B | IAM Scan PRD Coverage | IAM scan only read security-posture.md; missed signals in PRD Section 3 | ✅ (already in place) | team-orchestrator-core.md |
| Fix 40A | 5-Stage Memory Progression | Lessons stuck at Stage 1-Fail forever; knowledge never compounded | ✅ | docs/lessons.md |
| Fix 40B | Comprehension Debt Gate | Agents approving code without reading diffs; no sprint-boundary gate | ✅ | team-orchestrator-sprint.md (SM-RETRO) |
| Fix 40C | Constraint Drift Guard | Binding constraints forgotten by turn 47 via lossy summarization | ✅ | session-guards.md (GUARD 1) |
| Fix 40D | Ralph Wiggum NON-NEG #10 | Stories closed on "looks good" / "mostly passing" — no objective gate | ✅ | team-orchestrator-rules.md (NON-NEG #10) |
| Fix 40E | Bad Loop Domain Blocklist | Agents self-declaring done on arch rewrites / auth / prod deploys | ✅ | session-guards.md (GUARD 2) |
| Fix 41A | Hook Bloat → session-guards.md | Hook reached 245 lines, violating its own lessons.md thin-router rule | ✅ | session-guards.md (new file), hook (reference only) |
| Fix 41B | Comprehension Debt Scoring Rubric | Debt severity was subjective; scrum_master had unconstrained discretion | ✅ | team-orchestrator-sprint.md (4-item binary rubric) |
| Fix 41C | Bad-Loop Verb Scoping | Keyword-only gate caused false positives; team trained to ignore it | ✅ | session-guards.md (domain + high-risk verb both required) |
| Fix 42A | Post-Discovery Bad-Loop Re-Check | Gate ran on original prompt only; discovery-revealed scope not re-gated | ✅ | discovery-engine.md (STEP 4B) |
| Fix 42B | Stage-1 Lesson Age Enforcement | Stage-1-Fail lessons persisted indefinitely across sprints with no block | ✅ | team-orchestrator-sprint.md (LESSON AGE CHECK) |
| Fix 42C | Deploy Self-Triggering Gate | 'deploy' was domain keyword but not high-risk verb; prod deploys escaped gate | ✅ | session-guards.md (self-triggering exception) |

