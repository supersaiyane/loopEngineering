# KIRO SYSTEM — ONGOING FIXES
# Fixes 1–15 are APPLIED and documented in CLAUDE-implemented.md (reference only, never auto-loads).
# This file = pending work only. Read this every session. Skip CLAUDE-implemented.md unless debugging.

Last updated: 2026-07-10
# All fixes through Fix 43C implemented. See CLAUDE-implemented.md for full history.
# Next: Dry Run v11 to find new gaps.

---
# No pending fixes. System is clean.
---

## PENDING FIXES

*(none — all fixes through 43C implemented)*

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



---

## MASTER FIX REGISTER — All Fixes (Fix 1 → Fix 43C)
Last synced: 2026-07-10 | Total: 50 sub-fixes across 43 fix groups | All implemented ✅

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
| Fix 43A | Lesson Age Clock Accuracy | Age check used written_at (retro time); delayed retros made stale lessons appear fresh | ✅ | docs/lessons.md (gate_fired_at field), team-orchestrator-sprint.md (LESSON AGE CHECK) |
| Fix 43B | Ponytail Rung Disqualification | No escalation path when Rung N dep is disqualified (CVE/abandoned/license) — agents stuck | ✅ | ponytail.md (disqualification section), team-orchestrator-rules.md (GATE S2 item 5+6), skill-selection-matrix.md (S1/S2 rows) · artifact: docs/ponytail-rung-disqualification-guide.md |
| Fix 43C | Cross-Tenant Gate at S2 | GATE S2 coverage % check missed cross-tenant isolation tests; bugs surfaced at retro not PR | ✅ | team-orchestrator-rules.md (GATE S2 item 5b) |

---

## FEATURE / FIX DIVISION TABLE
Last synced: 2026-07-10
**Type key:** 🚀 Feature (new capability) · 🔧 Fix (bug/gap patched) · 🛡️ Guard (runtime protection) · 🚪 Gate (quality enforcement) · 🏗️ Architecture (structural change)

| Type | Fix | Capability / What Was Added | Category |
|------|-----|-----------------------------|----------|
| 🏗️ Architecture | Fix 1 | $TRACKER abstraction — pipeline works without Jira | Infrastructure |
| 🔧 Fix | Fix 2 | SM role split — SM no longer gates itself | Sprint Execution |
| 🚀 Feature | Fix 3 | FE/BE skill differentiation — separate skill libraries per lane | Agent Roles |
| 🔧 Fix | Fix 4 | Steering file inclusion — files load before agents activate | Infrastructure |
| 🚀 Feature | Fix 5 | Conflict resolution protocol — CTO/Architect/Security arbitration chain | Governance |
| 🚀 Feature | Fix 6 | Lean Team Mode (Mode 5) — 3-role lightweight path for MVPs | Routing |
| 🚀 Feature | Fix 7 | Loop Engineering — PLAN→DO→VERIFY→DECIDE replaces linear execution | Sprint Execution |
| 🚀 Feature | Fix 8 | Token / memory / context discipline system — budgets, rot detection, per-role limits | Performance |
| 🚀 Feature | Fix 9 | Skill Activation Pipeline — label → matrix → compress-all protocol | Agent Roles |
| 🔧 Fix | Fix 10 | Code persistence + loop spec + sprint parallelism defined | Sprint Execution |
| 🔧 Fix | Fix 11 | Routing precision — conflicts resolved, matrix "ALL files" entries removed | Routing |
| 🏗️ Architecture | Fix 12 | Hook rewrite as thin router — constitution moved to steering files | Infrastructure |
| 🔧 Fix | Fix 13 | Cleanup — 7 dead hooks deleted, shared skills consolidated | Infrastructure |
| 🚪 Gate | Fix 14 | Design System Gate — blocks agents from bypassing design system | Code Quality |
| 🔧 Fix | Fix 15 | Report templates + Sprint Discipline Card added | Documentation |
| 🔧 Fix | Fix 16 | Critical bugs — duplicate sections, mode routing errors, skill load failures | Infrastructure |
| 🔧 Fix | Fix 17 | Medium improvements — discipline gaps compounding silently | Sprint Execution |
| 🔧 Fix | Fix 18 | Low priority polish — health-check signals, minor correctness | Infrastructure |
| 🏗️ Architecture | Fix 19 | Team-orchestrator split — 1,264-line file → core + sprint + rules | Infrastructure |
| 🚀 Feature | Fix 20 | Step 0 keyword expansion + Role Handoff template (200-token structured format) | Routing |
| 🔧 Fix | Fix 21 | Shared skill file verification at session start — missing files warned not silenced | Infrastructure |
| 🔧 Fix | Fix 22 | Dry Run v1 gaps — STEP 6 / ROLE HANDOFF conflict resolved | Routing |
| 🚀 Feature | Fix 23 | Dynamic Skill × Agent Selection — label-to-matrix-to-compress replaces filename guessing | Agent Roles |
| 🔧 Fix | Fix 24 | JWT gap closure — Mode auto-inference stalling on single-shot prompts fixed | Routing |
| 🔧 Fix | Fix 25 | 26 filename mismatches + 19 gaps across dry runs patched | Infrastructure |
| 🔧 Fix | Fix 26 | Absorbed into Fix 27+ — superseded | (superseded) |
| 🔧 Fix | Fix 27 | P0 calibration — degradation thresholds, mode false positives, VERIFIER theater | Performance |
| 🚀 Feature | Fix 28 | Quick Reference cards + lessons scan made active (not decorative) | Memory |
| 🔧 Fix | Fix 29 | Design system owner + creation protocol defined | Documentation |
| 🔧 Fix | Fix 30 | Dry Run v3 — 7 gaps (Healthcare/FinTech/B2B SaaS/IoT scenarios) | Sprint Execution |
| 🔧 Fix | Fix 31 | Dry Run v4 — 8 gaps (data lake/edtech/marketplace/IoT adversarial) | Sprint Execution |
| 🚀 Feature | Fix 32 | Doc Knowledge Architecture — 6-doc source-of-truth framework, 8 templates | Documentation |
| 🚀 Feature | Fix 33A | IAM Budget Pre-Warning — auth scope estimate appears before sprint planning | Sprint Execution |
| 🚀 Feature | Fix 33B | OQ Auto-Prompt — SM-PLAN blocked until open questions resolved with resume phrase | Sprint Execution |
| 🚀 Feature | Fix 34 | Strix Security Integration — pentesting skill files for security_engineer | Agent Roles |
| 🔧 Fix | Fix 35 | Dual-routing conflict — two competing hooks causing undefined behavior removed | Infrastructure |
| 🔧 Fix | Fix 36 | Hook SYSTEM AUTHORITY — Kiro native "Build a Feature" dialog suppressed | Infrastructure |
| 🚀 Feature | Fix 37 | Ponytail Lazy Senior Dev — 7-rung ladder enforced before any code is written | Code Quality |
| 🚀 Feature | Fix 38A | 25-signal confidence list — enterprise prompts no longer score LOW incorrectly | Routing |
| 🚀 Feature | Fix 38B | Mobile Engineer auto-routing — force-activated on Platform=Mobile | Agent Roles |
| 🚪 Gate | Fix 38C | Ponytail GATE S2 commit block — rung violations caught at PR, not post-merge | Code Quality |
| 🚪 Gate | Fix 39A | GATE S2 Jira Ponytail verdict — PASS/FAIL line in every Jira comment for audit trail | Code Quality |
| 🔧 Fix | Fix 39B | IAM scan PRD coverage — already in place; confirmed | Security |
| 🚀 Feature | Fix 40A | 5-Stage Memory Progression — lessons compound (Fail→Investigate→Verify→Distill→Consult) | Memory |
| 🚪 Gate | Fix 40B | Comprehension Debt Gate — SM-RETRO blocks sprint if agents approved without reading diffs | Sprint Execution |
| 🛡️ Guard | Fix 40C | Constraint Drift Guard (GUARD 1) — binding constraints re-read every session start | Memory |
| 🛡️ Guard | Fix 40D | Ralph Wiggum NON-NEG #10 — "mostly passing" / "looks good" are not close conditions | Code Quality |
| 🛡️ Guard | Fix 40E | Bad Loop Domain Blocklist (GUARD 2) — auth/payments/prod/arch rewrites need human gate | Security |
| 🏗️ Architecture | Fix 41A | session-guards.md created — hook bloat extracted, always-loaded guard file | Infrastructure |
| 🚪 Gate | Fix 41B | Comprehension Debt scoring rubric — 4-item binary (0=critical, replaces subjective SM call) | Sprint Execution |
| 🔧 Fix | Fix 41C | Bad-loop verb scoping — keyword-only gate caused false positives; both domain + verb now required | Security |
| 🛡️ Guard | Fix 42A | Post-Discovery Bad-Loop Gate (STEP 4B) — discovered scope re-checked, not just original prompt | Security |
| 🚪 Gate | Fix 42B | Stage-1 Lesson Age Enforcement — stale blockers block Sprint N+1 | Memory |
| 🛡️ Guard | Fix 42C | Deploy Self-Triggering Gate — 'deploy/release/production' fire gate without needing a verb | Security |
| 🔧 Fix | Fix 43A | Lesson Age Clock Accuracy — `gate_fired_at` field added; delayed retros no longer inflate age | Memory |
| 🚀 Feature | Fix 43B | Ponytail Rung Disqualification Protocol — RDR + escalation path + ADR + artifact for users | Code Quality |
| 🚪 Gate | Fix 43C | Cross-Tenant Isolation Test at GATE S2 — absence = GATE FAIL on rbac/multi-tenant stories | Security |

### Summary by Type

| Type | Count | % of total |
|------|-------|-----------|
| 🚀 Feature (new capability) | 20 | 40% |
| 🔧 Fix (bug / gap patched) | 18 | 36% |
| 🛡️ Guard (runtime protection) | 6 | 12% |
| 🚪 Gate (quality enforcement) | 7 | 14% |
| 🏗️ Architecture (structural) | 5 | 10% |

> Note: Some fixes span multiple types (e.g., Fix 19 is both a Fix and Architecture). Categorized by primary intent.

