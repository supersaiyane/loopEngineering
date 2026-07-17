# KIRO SYSTEM — ONGOING FIXES
# All implemented fixes (Fix 1 → Fix 47D, Fix 44A, 45A/B/C, 46A, R1-outreach) are in CLAUDE-implemented.md
# (reference only, never auto-loads). This file = PENDING work only.
# Read this every session. Skip CLAUDE-implemented.md unless debugging.

Last updated: 2026-07-17

# ══════════════════════════════════════════════════════════════════════
# POST-FIX WIRING VERIFICATION — MANDATORY AFTER EVERY FIX
# ══════════════════════════════════════════════════════════════════════
# After implementing ANY fix, run this 7-point wiring check before marking ✅ DONE.
# A fix is NOT complete until all applicable layers below are verified.
# Skip a layer only if the fix provably does not touch that layer — state why when skipping.
#
# LAYER 1 — SKILL FILES EXIST
#   New skill files created? → Verify path is correct: kiro/skills/<role>/<filename>.md
#   Existing files modified? → Confirm LOAD-TYPE annotation at top is still accurate
#
# LAYER 2 — LABEL INDEX (skill-label-index.md)
#   New skills added? → Do they have a label row in Section 1?
#   New labels introduced? → Are they documented with all skill file paths?
#   Keyword fallback: do the new labels have keyword patterns in LABEL-BASED FALLBACK?
#
# LAYER 3 — SKILL SELECTION MATRIX (skill-selection-matrix.md)
#   New agent added? → Does it have activity rows in the matrix?
#   New activity pattern? → Is there a matrix row for it under the correct agent?
#   Role overrides (Section 2 of label index): does the role need additional files beyond Section 1?
#
# LAYER 4 — PHASE / EVENT TRIGGERS (orchestrator-routing.md + team-orchestrator-*.md)
#   Fix adds behavior that fires WITHOUT a story label? (e.g., at THINK, GATE 2, SM-PLAN, GATE 5)
#   → Must be wired as a phase trigger in orchestrator-routing.md or team-orchestrator-sprint.md
#   Fix adds GATE checklist item? → Confirm it appears in the gate checklist in team-orchestrator-sprint.md
#
# LAYER 5 — ROLE DEFAULTS (skill-selection-matrix.md)
#   Fix adds behavior that should fire for ALL agents or ALL stories in a given mode?
#   → Must be a role default or mode default in skill-selection-matrix.md
#
# LAYER 6 — SESSION GUARDS (session-guards.md)
#   Fix adds a cross-session constraint, compression guard, or non-bypassable check?
#   → Must be documented in session-guards.md with its trigger condition
#
# LAYER 7 — FAILURE MODE COVERAGE (F01–F12 table)
#   Fix addresses a new failure mode not in F01–F12? → Add to the table with ID, name, description
#   Fix addresses an existing failure mode? → Confirm the fix appears in the fix register with correct Fx reference
#
# WIRING STATUS FORMAT (add to each fix entry in this file):
#   Wiring: L1✅ L2✅ L3✅ L4⬜ L5⬜ L6⬜ L7✅  ← ⬜ = not applicable / skipped with reason
#
# ══════════════════════════════════════════════════════════════════════
# PHASE 1 COMPLETE ✅ (2026-07-17)
# Fix 44A ✅ · Fix 45A ✅ · Fix 45B ✅ · Fix 45C ✅ · R1 ✅
# All fixes through Fix 43C implemented. Dry Run v11 complete. White paper v5 published (34pp, July 2026).
# GOAT.md created. README.md + index.html updated with crisis framing, research section, roadmap.
# pxpipe integration complete (2026-07-15): GUARD 3 added to session-guards.md, launch script at scripts/start-kiro-pxpipe.sh
# Research parked: gstack-research.md, pxpipe-research.md, oneagent-search.md


# ── PENDING FIXES ──────────────────────────────────────────────
# Fixes 44A, 45A, 45B, 45C, R1(outreach), 46A, 47A–D moved to CLAUDE-implemented.md

## Fix 46B — White Paper v6: Add External Validation Section  [PRIORITY: LOW · Phase 2 Roadmap]
# What: When external validator(s) reproduce findings, update white paper with Section 11 results.
#   Also add: competitor comparison table (Fix 45C), compression methodology (Fix 45B).
# Action: Update gen_whitepaper_v5.js → gen_whitepaper_v6.js with:
#   - New subsection 10.4: External Validation Results
#   - Updated Section 1.3: Competitor comparison table
#   - Appendix A: Compression-fidelity methodology
# File: gen_whitepaper_v6.js (new, based on v5)
# Status: 🔲 PENDING — blocked on external validation data

## Research Task R1 — Recruit First External Validator  [PRIORITY: HIGH · Critical Path]
# What: The GOAT analysis identifies external reproducibility as the #1 gap.
#   One independent developer who clones, follows the process, and reports back
#   is the diff between a practitioner journal and a field contribution.
# Action:
#   - Post on relevant communities (HN, r/MachineLearning, AI engineering forums)
#   - Share the repo + white paper v5 PDF
#   - Ask: "Does your production setup hit failure modes F01–F12?"
#   - Collect: before/after data if they adopt the framework
# Prerequisite: Fix 45A (open-source artifacts) must be done first.
# Status: 🔲 PENDING — blocked on Fix 45A

# ── PHASE 2 ROADMAP ITEMS (90 days) ─────────────────────────────
# Prerequisite: Phase 1 (Fix 44A, 45A, 45B, 45C) must be complete first.

## R2 — Before/After Baseline Study
# What: Without a before/after comparison, all improvement claims are self-reported.
#   Need a structured baseline: capture failure mode occurrence rates BEFORE framework adoption,
#   then measure again AFTER, across at least one external team.
# Action:
#   - Define baseline measurement protocol: which failure modes (F01–F12), how measured,
#     session count required, what counts as an "occurrence"
#   - Write docs/baseline-protocol.md
#   - Instrument own sessions to capture occurrence rates as ground truth
# File: docs/baseline-protocol.md (new)
# Status: 🔲 PENDING — blocked on R1 (external validator)

## R3 — MOMENTO Evaluation Protocol
# What: MOMENTO (2025) is the first multi-session evaluation benchmark.
#   Using MOMENTO scenarios to formally evaluate Loop Engineering gives the paper
#   a credible, reproducible evaluation framework instead of ad-hoc dry runs.
# Action:
#   - Read MOMENTO paper and extract scenario types
#   - Map our 12 failure modes to MOMENTO scenario categories
#   - Run ≥3 MOMENTO scenarios with and without the framework
#   - Document delta as Section 10.X in white paper
# File: docs/momento-evaluation.md (new)
# Status: 🔲 PENDING — blocked on R1

# ── PHASE 3 ROADMAP ITEMS (3–6 months) ──────────────────────────
# Prerequisite: Phase 2 complete, external validation data in hand.

## P3A — arXiv Preprint
# What: Submit the white paper to arXiv (cs.SE or cs.AI) for public record and citation.
# Action:
#   - Convert white paper v6 to LaTeX (arXiv standard)
#   - Add abstract in arXiv format (≤150 words)
#   - Add author affiliation and contact
#   - Submit to cs.SE (Software Engineering) category
# File: docs/arxiv-submission/ (new directory with .tex source)
# Status: 🔲 PENDING — blocked on Phase 2 data + white paper v6

## P3B — Practitioner Venue Submission
# What: Submit to a practitioner-friendly venue to reach the audience that would use this.
# Target venues (in priority order):
#   1. EMNLP Industry Track — natural language / agent engineering audience
#   2. ICLR Workshop on LLM Agents — direct audience fit
#   3. FSE/ICSE Industry Track — software engineering practitioners
# Action:
#   - Monitor CFPs for above venues
#   - Adapt white paper v6 to 8-page conference format
#   - Prepare camera-ready if accepted
# File: docs/venue-submission.md (new — track CFP deadlines)
# Status: 🔲 PENDING — blocked on Phase 2

## P3C — Open Standard Proposal: Session Continuity Architecture
# What: The session continuity pattern (checkpoint + resume vector + CLAUDE.md process contract)
#   is general enough to be a field standard, not just a Loop Engineering internal.
#   Propose it as an open standard for AI agent session management.
# Action:
#   - Write docs/session-continuity-standard.md as a draft RFC
#   - Define: checkpoint schema, resume vector format, process contract spec
#   - Publish as standalone doc for community feedback
# File: docs/session-continuity-standard.md (new)
# Status: 🔲 PENDING — blocked on Phase 2 validation

# ── PHASE 4 ROADMAP ITEMS (6–12 months) ─────────────────────────
# Long horizon. Don't plan implementation until Phase 3 is underway.

## P4A — Multi-Team Multi-Model Validation
# What: Validate whether process-layer gains generalize across models (not just Claude)
#   and across teams (not just solo practitioner Gurpreet).
# Questions to answer:
#   - Do failure modes F01–F12 appear with GPT-4o? Gemini? Open-source models?
#   - Does the framework produce the same reliability lift with a 5-person team?
#   - Which failure modes are model-specific vs. process-layer universal?
# Status: 🔲 PENDING — Phase 4

## P4B — Benchmark Contribution
# What: Contribute a Loop Engineering evaluation suite to an existing benchmark
#   (SWE-bench, MOMENTO, or a new multi-session reliability benchmark).
# Action:
#   - Package our 12 failure mode scenarios as reproducible test cases
#   - Propose addition to MOMENTO or create LE-Bench as standalone
# Status: 🔲 PENDING — Phase 4

## P4C — Open-Source Validation Tooling
# What: Build a lightweight CLI that any team can run to:
#   - Detect which of F01–F12 failure modes are present in their sessions
#   - Score their process layer against the Loop Engineering rubric
#   - Output a gap report with fix recommendations
# Action: Design the CLI spec first (docs/validation-cli-spec.md), then build
# Status: 🔲 PENDING — Phase 4

# ── END BACKLOG ───────────────────────────────────────────────────

# ── PXPIPE TOKEN COMPRESSION ────────────────────────────────────
# pxpipe proxy reduces input token cost ~59-70% on dense code/JSON sessions
# by rendering old history + system prompt + tool docs as PNG images.
#
# LAUNCH:  cd loopEngineering && ./scripts/start-kiro-pxpipe.sh
#
# TOKEN DISCIPLINE NOTE (from global CAVEMAN ULTRA):
# The degradation tier thresholds (PEAK/GOOD/DEGRADING/CRITICAL) measure
# BEHAVIOR discipline, not just cost. Tiers remain the same.
# But with pxpipe active: financial pressure per tier is ~3x lower.
# A DEGRADING session without pxpipe ≈ a GOOD session with pxpipe, dollar-for-dollar.
# Check ~/.pxpipe/events.jsonl after a sprint to see actual compression on our workload.
#
# GUARD 3 applies when pxpipe is active — see kiro/steering/session-guards.md
# ────────────────────────────────────────────────────────────────

---





---

## MASTER FIX REGISTER — All Fixes (Fix 1 → Fix 44A)
Last synced: 2026-07-17 | Total: 57 sub-fixes across 46 fix groups | 57 implemented ✅ · 0 pending 🔲 · Phase 2 queued

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
| Fix 40A | 5-Stage Memory Progression | Lessons stuck at Stage 1-Fail forever; knowledge never compounded | ✅ | kiro/memory/lessons.md |
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
| Fix 43A | Lesson Age Clock Accuracy | Age check used written_at (retro time); delayed retros made stale lessons appear fresh | ✅ | kiro/memory/lessons.md (gate_fired_at field), team-orchestrator-sprint.md (LESSON AGE CHECK) |
| Fix 43B | Ponytail Rung Disqualification | No escalation path when Rung N dep is disqualified (CVE/abandoned/license) — agents stuck | ✅ | ponytail.md (disqualification section), team-orchestrator-rules.md (GATE S2 item 5+6), skill-selection-matrix.md (S1/S2 rows) · artifact: docs/ponytail-rung-disqualification-guide.md |
| Fix 43C | Cross-Tenant Gate at S2 | GATE S2 coverage % check missed cross-tenant isolation tests; bugs surfaced at retro not PR | ✅ | team-orchestrator-rules.md (GATE S2 item 5b) |
| Fix 44A | Mode 5 Security/RBAC Advisory | Mode 5 (Lean) skips security_engineer — no warning emitted when security/rbac story ships without GATE S2; cross-tenant test enforcement silently absent | ✅ | orchestrator-routing.md (Mode 5 advisory block) |
| Fix 45A | Open-Source Artifacts | Framework not reproducible externally — no LICENSE, no CONTRIBUTING.md, no "how to reproduce" guide | ✅ | LICENSE, CONTRIBUTING.md, README.md |
| Fix 45B | Compression-Fidelity Methodology Doc | 11–17% exact-string misread finding has no methodology — it's an anecdote without documented test protocol, sample size, and limitations | ✅ | docs/research/compression-fidelity-methodology.md |
| Fix 45C | Competitor Comparison | White paper mentions MemGPT/Reflexion as prior work but has no structured side-by-side table; reviewers will require it | ✅ | docs/research/competitor-comparison.md |
| Fix 46A | Product Knowledge Graph | No living architecture map of the product Kiro builds — structural drift invisible across sprints | ✅ | docs/product-graph.yaml, docs/product-graph.html, skills/architect/product_graph_update.md, skills/shared/graph_patch_emit.md · Wiring: L1✅ L2✅ L3✅ L4✅ L5⬜ L6⬜ L7⬜ |
| Fix 46B | White Paper v6 | Update white paper when external validation data arrives | 🔲 PENDING (blocked on R1) | docs/white-paper/loop-engineering-white-paper-v6.* |
| Fix 47A | Skill Label Coverage (119 rows) | 173 skill files unreachable — only 37 label rows, 82 new lanes had zero coverage | ✅ | skill-label-index.md (37 → 119 rows; 82 new labels across ml/*, arch/*, cloud/*, finops/*, sre/*, product/*, web/*, docs/*) |
| Fix 47B | Phase/Event Triggers | CTO/SM/TW/ARCHITECT only fired on story labels — never at their natural system phases | ✅ | orchestrator-routing.md (PHASE/EVENT AUTO-TRIGGERS block), team-orchestrator-sprint.md (SM-PLAN section + GATE 5 TW trigger) |
| Fix 47C | Universal Role Defaults | code_review_excellence / debugging / refactoring / devops defaults never loaded without labels | ✅ | skill-selection-matrix.md (UNIVERSAL ROLE DEFAULTS table) |
| Fix 47D | Fallback Keyword Expansion | LABEL-BASED FALLBACK had 9 patterns; 82 new labels had zero fallback coverage for unlabeled stories | ✅ | skill-label-index.md (9 → ~60 keyword patterns covering all new lanes) |
| Skill: sprint_artifacts | SM Document Generation | SM had no way to produce pptx/pdf/xlsx sprint artifacts at GATE 5 / SM-RETRO / SM-PLAN | ✅ | kiro/skills/scrum_master/sprint_artifacts.md (HYBRID) |
| Skill: web_app_testing | QA Browser Testing | QA had no browser-based testing capability; Anthropic web-app-tester unpublished | ✅ | kiro/skills/qa_engineer/web_app_testing.md (CHECKLIST) using claude-in-chrome tools |
| R1 | Recruit External Validator | No independent reproduction — the single biggest gap to academic credibility | 🔲 PENDING | docs/external-validator-outreach.md (posts ready, not yet published) |

---

## FEATURE / FIX DIVISION TABLE
Last synced: 2026-07-10 | Found in: Dry Run v11
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
| 🛡️ Guard | Fix 44A | Mode 5 Security/RBAC Advisory — warn when security/rbac story ships in Lean mode without GATE S2 | Security |

### Summary by Type

| Type | Count | % of total | Last added |
|------|-------|-----------|------------|
| 🚀 Feature (new capability) | 20 | 39% | Fix 43B |
| 🔧 Fix (bug / gap patched) | 18 | 35% | Fix 43A |
| 🛡️ Guard (runtime protection) | 7 | 14% | Fix 44A 🔲 |
| 🚪 Gate (quality enforcement) | 7 | 14% | Fix 43C |
| 🏗️ Architecture (structural) | 5 | 10% | Fix 41A |

> Note: Some fixes span multiple types (e.g., Fix 19 is both a Fix and Architecture). Categorized by primary intent.
> 🔲 = candidate (not yet implemented)

