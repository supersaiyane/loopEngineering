# Kiro Elite Team — AI Professional System Review
**Date:** 2026-06-30  
**Reviewer lens:** Senior AI systems engineer — token economics, model behavior, orchestration architecture, prompt engineering  
**Prior reviews:** v1 (Fix 11), v2 (2026-06-30 post-Fix 15). This review covers Fixes 16–18 and re-evaluates fundamentals.

---

## EXECUTIVE SUMMARY

The system has matured significantly across 18 fix cycles. The core architecture — thin hook router, always/manual-inclusion split, role-scoped skill files, degradation tiers — is sound and reflects good prompt engineering instincts. However, several latent issues invisible to a software engineer become obvious through an AI model behavior lens: a critical always-load bug burning ~23K tokens per session, attention decay risk in a 1,264-line constitution file, instruction-following assumptions that models cannot reliably honor, and a memory confidence system that is subjective where it needs to be measurable.

**Overall rating: B+ architecture, C execution on token hygiene.**

The system would benefit more from fixing the always-load bug and splitting team-orchestrator.md than from any additional feature work.

---

## 1. TOKEN ECONOMICS — QUANTIFIED

### 1A. Always-Loaded Token Budget (Every Session, Every Mode)

| File | Lines | Approx Tokens | Verdict |
|------|-------|--------------|---------|
| Hook prompt | — | ~1,321 | ✅ Excellent (thin) |
| orchestrator-routing.md | 364 | ~4,589 | ✅ Acceptable |
| context-memory-discipline.md | 131 | ~1,177 | ✅ Lean |
| discovery-engine.md | 241 | ~2,319 | ⚠️ Should be conditional |
| shared/SKILL.md | 41 | ~250 | ✅ Good index |
| **CLAUDE-implemented.md** | **2,296** | **~23,000** | **🔴 CRITICAL BUG** |

**CLAUDE-implemented.md has `inclusion: always` in its frontmatter.** This file — intended as a manual-inclusion-only archive of Fixes 1–15 — is loading in every single session and burning approximately **23,000 tokens** before any work begins. This is the single most impactful bug in the system right now.

**Fix:** Change `inclusion: always` → `inclusion: manual` in CLAUDE-implemented.md frontmatter. This recovers 23K tokens per session immediately.

### 1B. Conditional Load Budget (Mode 1/4/5 Only)

| File | Lines | Approx Tokens | Load Trigger |
|------|-------|--------------|-------------|
| team-orchestrator.md | 1,264 | ~12,600 | Mode 1/4/5 session start |
| skill-selection-matrix.md | 334 | ~3,340 | Mode 1/4/5 session start |
| loop-engine.md | 345 | ~3,450 | DEVELOP phase |
| 3 skill files (avg) | ~150 | ~1,500 | Per role per story |

**Mode 1 full-load context cost before first line of code:**
Hook (1,321) + routing (4,589) + discipline (1,177) + discovery (2,319) + orchestrator (12,600) + matrix (3,340) = **~25,346 tokens** consumed before any work product is generated.

On a 200K-token Claude Sonnet window, this leaves 174K for actual work — workable. On GPT-4o's 128K window, it leaves ~102K — tight for multi-sprint builds.

### 1C. discovery-engine.md Always-Load Problem

The discovery engine has `inclusion: always` but the Step 4 conditional logic in the hook says it only needs to load for new build tasks. In Mode 3 (fix/question), it never fires. Keeping it always-loaded wastes ~2,319 tokens on every Mode 3 request — which is likely the majority of daily usage.

**Recommendation:** Change discovery-engine.md to `inclusion: manual`. Add explicit load to hook Step 3: `LOAD: kiro/steering/discovery-engine.md` (alongside the existing "STOP if absent" check). The hook already handles this conditionally — the always-load flag is redundant and wasteful.

---

## 2. PROMPT ARCHITECTURE ANALYSIS

### 2A. team-orchestrator.md — Lost-in-the-Middle Risk

**1,264 lines in a single file is the system's most significant prompt engineering risk.**

There is well-documented evidence (Liu et al., 2023; subsequent replications) that LLMs have significantly reduced attention to content positioned in the middle of long prompts. They attend well to the beginning and end; middle content receives ~40–60% of the attention of leading content.

team-orchestrator.md structure:
- Lines 1–200: Role registry, SM modes, role sequence (high attention ✅)
- Lines 200–500: DESIGN phase, DEVELOP phase headers (medium attention ⚠️)
- Lines 500–900: DEVELOP artifact chains, loop spec, gates 1–3 (low attention 🔴)
- Lines 900–1264: GATE 4 (MEMORY WRITE, SM-RETRO), GATE 5 (phase-end reports), conflict resolution (very low attention 🔴)

**GATE 4's new MEMORY WRITE step (Fix 17H) sits at line ~420 — in the danger zone.** The Sprint Discipline Card blocking rule (Fix 15C/16C) sits around line 154 — safer.

**Recommendation: Split team-orchestrator.md into 3 phase-specific files:**

```
team-orchestrator-core.md        (~350 lines) — roles, SM modes, THINK phase, DESIGN phase
team-orchestrator-develop.md     (~450 lines) — DEVELOP phase, loop, story lifecycle, GATE 1-3
team-orchestrator-gates.md       (~250 lines) — GATE 4, GATE 5, conflict resolution, report templates
```

Hook Step 4 loads only the section relevant to the current phase. GATE content only enters context when a gate is actually being executed. This brings each loaded file to ≤450 lines, putting all critical content in the high-attention leading portion.

### 2B. Instruction Density and Ambiguity Audit

**GOOD patterns found:**
- `BLOCKING RULE:` prefix on hard constraints — models attend to capitalized keywords
- Code block formatting for step-by-step protocols — better instruction following than prose
- `→ STOP if absent` pattern — clear fail-fast signal
- Log line requirements `[ENV]`, `[MODE]`, `[SKILLS ACTIVATED]` — observable compliance markers

**PROBLEMATIC patterns found:**

1. **Mixed imperative and conditional in the same section.** Example from orchestrator-routing.md: Mode 3 trigger section mixes "trigger when X" with "also trigger when Y but not Z" in prose. Models handle `if/then` tables better than nested prose conditions.

2. **The phrase "in order" appears in GATE 4 but isn't numbered.** When steps have dependencies, number them explicitly: `Step 1:`, `Step 2:`, `Step 2b:`. The "2b" designation (Fix 17H) is creative but non-standard — models may treat 2b as optional or as a substep of 2 rather than a mandatory gate between 2 and 3.

3. **"Others" in the skill matrix Skip column.** `| skip |` → `| skip all others |` is slightly clearer but still relies on the model knowing which files are "others." A small risk but worth noting.

4. **Multiple definitions of the same concept.** "Degradation tiers" appear in context-memory-discipline.md AND were historically in the hook. The current system has the canonical source in context-memory-discipline.md with a pointer from the hook — correct. But the adapters (claude-system-prompt.md, chatgpt-system-prompt.md) replicate the tier table inline. Now there are 3 copies. Any future change requires 3-file synchronization.

### 2C. Step 0 Complexity Gate — Calibration Issue (Fix 17A)

The gate fires when: prompt ≤8 words AND no BUILD/CREATE/MAKE/DEVELOP/IMPLEMENT/DESIGN/PLAN/ARCHITECT/SPRINT/PHASE.

**False positive risk (legitimate requests incorrectly skipped):**
- "Write the architecture doc" — 5 words, no trigger keyword → would skip all steps ❌
- "Review this PR" — 4 words, no trigger keyword → would skip all steps ❌
- "Run the QA gate" — 5 words, no trigger keyword → would skip all steps ❌

The keyword list includes DESIGN and PLAN but not WRITE, REVIEW, ANALYZE, AUDIT, or RUN. These are common Mode 2 request verbs.

**Recommendation:** Expand keyword list or loosen the AND condition:
```
IF prompt ≤ 5 words AND no trigger keyword → skip
```
OR
```
IF prompt ≤ 8 words AND no trigger keyword AND no role name mentioned → skip
```

The session-resume check (already logged [ENV] + [MODE]) is excellent and well-calibrated — keep it.

---

## 3. MULTI-AGENT ORCHESTRATION ASSESSMENT

### 3A. Role Isolation Quality

The 22-role system is architecturally strong. Each role has:
- A defined trigger condition (story labels, phase gates)
- Bounded skill file loading (max 3)
- A defined output format
- A defined handoff compression target (≤300 tokens to orchestrator)

**What's working:** The skill-selection-matrix.md as a lookup table (vs. embedding skill routing in every role prompt) is the right abstraction. It centralizes routing logic and makes it auditable. The shared/ skill pattern eliminates duplication across roles.

**What's fragile:**

1. **Handoff compression (≤300 tokens) is self-enforced.** In a real multi-agent API call chain, you can hard-truncate. In an LLM session, the role output just… exists in context. The "compress to ≤300 tokens before passing to orchestrator" instruction relies entirely on the model's instruction following — which degrades as context grows. There is no mechanism to verify this happened.

2. **Role activation ordering creates context accumulation.** In Mode 1 DEVELOP, a single story activates: backend_lead → senior_engineer_be → qa_engineer → devops_engineer in sequence. Each role's output stays in context for the next role. By devops_engineer, the context contains: hook + orchestrator + matrix + loop engine + skill files × 3 + be_lead output + senior_be output + qa output. This is fine for a single story but compounds across a sprint.

3. **"Fresh context invocation" for qa_engineer and checker roles.** The system specifies "fresh context invocation" for QA and QUALITY (lean mode) roles. In Kiro's hook architecture, this presumably means a separate API call. In Claude Projects or ChatGPT, a "fresh context invocation" doesn't exist in a single conversation — everything is in context. The adapters don't address this gap. The qa_engineer will see all prior work, which is actually fine for review purposes but breaks the isolation guarantee.

### 3B. The 19-Role Scaling Problem

22 roles × avg 10 skill files = 220+ skill files the matrix must navigate. The system uses labels (story labels → matrix lookup) which is the right approach. But:

- The model must read skill-selection-matrix.md (~3,340 tokens) to find 3 files
- The model then reads those 3 files (~1,500 tokens)
- Then compresses to 5-line takeaway
- Then produces artifact
- Then discards

This is 5 sequential operations per role activation. For a 3-story sprint with 4 roles per story = 12 role activations × 5 ops = 60 operations before any sprint output is produced. In a single LLM context, this is viable but expensive. It's the right tradeoff for quality — just be clear-eyed about it.

### 3C. The Orchestrator-as-Router Doesn't Exist at Runtime

The hook is the router. But in a single Claude/ChatGPT conversation, there's no true orchestrator — the LLM IS the orchestrator AND every role. The "delegate to team-orchestrator.md" instruction means "follow the rules in that file" not "call a separate agent." This distinction matters:

**In Kiro (actual):** Hook fires → loads constitution → LLM follows it. ✅ Works.
**In Claude Projects:** System prompt loads constitution → LLM follows it. ✅ Works.
**In API multi-agent setup:** This would need actual separate API calls per role. The current architecture could support this with modification — but nothing in the current docs describes it.

The system is implicitly designed as a single-LLM-session orchestration pattern, not a true multi-agent API architecture. This is fine, but should be made explicit. The word "invoke" throughout team-orchestrator.md implies role isolation that doesn't actually exist in the execution model.

---

## 4. MEMORY SYSTEM ASSESSMENT

### 4A. Architecture — Correct Pattern

The two-file memory system (lessons.md for patterns, decisions.md for ADRs) maps well to how LLMs should use long-term knowledge:
- lessons.md: probabilistic knowledge ("usually true" — use confidence scoring)
- decisions.md: deterministic knowledge ("always binding" — ADRs as constraints)

This is the right separation. Loading decisions.md as binding constraints before role activation (Fix 17F) is correct — constraint knowledge should be in context before the model starts generating, not discovered mid-generation.

### 4B. Memory Confidence Scoring — Subjectivity Problem

The current confidence levels (low/medium/high) are assigned by the model during MEMORY WRITE (Fix 17H). This creates a measurement problem:

- Model assigns "high" confidence to a lesson after 2 positive confirmations in the same sprint
- Next sprint uses the lesson as a hard constraint
- The lesson is wrong for this project's context
- No mechanism to detect or correct this

**AI professional diagnosis:** The confidence system needs measurable, not impressionistic, criteria.

**Proposed objective criteria:**
```
confidence: low     → Observed once. Not yet validated in a separate sprint.
confidence: medium  → Observed in 2+ separate sprints. No contradictions.
confidence: high    → Observed in 5+ sprints. Zero contradictions. Explicitly confirmed by user.
```

The model can apply these rules mechanically. "Applied in 2 separate sprints" is verifiable by checking checkpoint.md dates.

### 4C. Memory Load Scope — Missing Specificity

Fix 17F instructs: "Load relevant entries into context BEFORE first role activates." But it doesn't define what "relevant" means. A lessons.md with 25 entries loads all 25, even if only 3 apply to the current sprint's domain.

**Recommendation:** Add domain tags to lesson entries. On load, filter to entries where tag matches current build domain. This requires a lessons.md schema update:

```
## [date] [confidence] [domain:backend|frontend|data|mobile|all] 
Lesson text here.
```

Load rule: "Load entries where `domain` matches current sprint's primary lane, plus all `domain:all` entries."

### 4D. ADR Query Interface

The decisions.md query pattern (filter by valid_from/valid_to) requires the model to manually evaluate date ranges. This is unreliable — models don't reliably filter tabular data under time pressure.

**Recommendation:** Add a `STATUS` column with machine-readable values (Accepted/Superseded) and define the query as: "Load ALL rows where STATUS=Accepted." Let the temporal columns serve audit purposes only.

---

## 5. CONTEXT WINDOW MANAGEMENT — HONEST ASSESSMENT

### 5A. The Degradation Tier System Is Optimistic

The tiers (PEAK 0-4, GOOD 5-7, DEGRADING 8-11, CRITICAL 12+) count "reads." But:

1. **Models cannot reliably count tool calls autonomously.** There's no system-level counter. The model must self-count using working memory in a long context. As context grows, self-counting accuracy degrades — exactly when accurate counting matters most.

2. **Tool call count ≠ context pressure.** A session with 4 large file reads (PEAK tier) may be more context-pressured than a session with 12 small bash commands (CRITICAL tier). Bytes consumed is a better signal than operation count.

3. **The CRITICAL tier action ("FULL STOP, recommend fresh session") is the right answer** but relies on the model voluntarily halting work. In practice, most LLMs will continue working past the threshold under user instruction pressure.

**Recommendation:** Add a byte-based threshold alongside the count-based tier as a secondary trigger. Something like: "If context content from tool outputs exceeds 50KB, treat as DEGRADING regardless of count." This is more mechanical and harder to accidentally override.

### 5B. Goal Anchor Every 10 Tool Calls — Reliability

This is a good anti-drift mechanism in principle. In practice:
- Claude 3.5/4 series: follows this reliably for ~30 tool calls
- GPT-4o: follows this reliably for ~20 tool calls
- Beyond those counts: instruction following of meta-level rules (like "inject this every N calls") degrades significantly

The 85% threshold offloading (Fix 13G) is a better mechanism because it's triggered by a detectable condition (context size) rather than self-counted events.

**Recommendation:** Make the Goal Anchor tie to the 85% threshold check rather than a count: "Every time you run the CONTEXT LEVEL CHECK (at 85% threshold detection), ALSO inject the Goal Anchor." This links the anti-drift mechanism to a more reliable trigger.

### 5C. Role Output Compression Rate

The ≤300 token handoff target is well-calibrated. A role's artifact (API spec, architecture doc, test plan) typically runs 800–2,000 tokens. Compressing to 300 = ~15–35% retention. This is lossy but appropriate — the orchestrator needs the decision, not the reasoning.

However, "compress to ≤300 tokens" with no format specification produces inconsistent outputs. A structured summary format would be more reliable:

```
ROLE HANDOFF — [role_name]
Artifact: [type + filename]
Key decisions: [2-3 bullet points, 50 tokens max each]
Blockers: [none | description]
Next role needs: [specific context required]
Token count: ~[N]
```

This format is ~200 tokens, structured, and gives the next role exactly what it needs.

---

## 6. SKILL FILE SYSTEM — EFFICIENCY ANALYSIS

### 6A. The 255-File Inventory

255 skill files across 22 roles + shared. Average ~11.6 files per role. This is a large library.

**Usage pattern problem:** The matrix activates max 3 files per role per story. Statistically, many skill files may never load in a typical project. Files for niche scenarios (chaos_engineering.md, forensics_log_analysis_dfir.md, ai_ml_security_prompt_injection.md) may never activate on most builds.

This isn't a bug — a never-loaded skill file costs zero tokens. But it has a maintenance cost: 255 files to keep updated, validated, and coherent. The eval-gated modification rule (ADR-008) is the right policy but creates a high barrier to improvement.

### 6B. 5-Line Takeaway Rule (Fix 17C) — Correct and Important

This is one of the highest-value fixes in the batch. Skill files average ~150 lines. Without compression, loading 3 files = ~450 lines persisting in context for the entire role invocation + potentially beyond. With the Extract→Produce→Discard pattern, peak skill-file context cost drops from 450 lines to 15 lines (3 × 5-line summaries). That's a 30x context reduction.

The only risk: information loss. A 5-line summary of a 150-line security checklist will miss specific items. For precision tasks (security reviews, compliance checks), consider allowing 10-line takeaways for security_engineer and qa_engineer roles specifically.

### 6C. Shared Skills — Path Resolution

The `shared/` prefix convention (Fix 16D) is clean. The fallback to `kiro/skills/shared/SKILL.md` when a specific shared file is missing is the right graceful degradation.

One gap: shared/SKILL.md lists 9 shared skills, but the skills directory may have been populated with more or fewer than 9. The index file will go stale as shared/ evolves.

**Recommendation:** Add a check to shared/SKILL.md header: "This index was last verified [date]. If adding new shared files, update this index."

---

## 7. PLATFORM PORTABILITY — ADAPTER ASSESSMENT

### 7A. What the Adapters Get Right

- Zero changes to existing steering files (correct — adapters are additive)
- Self-contained system prompts (correct — a platform-specific prompt shouldn't depend on Kiro internals)
- Manual session start ritual replacing the hook's `promptSubmit` auto-trigger (necessary and well-designed)
- Explicit Knowledge file upload instructions (practical and complete)

### 7B. Synchronization Drift Risk

The adapters replicate routing logic, degradation tiers, and skill activation protocols inline. When the canonical source changes:

| What changes | Files that need updating |
|---|---|
| Mode routing trigger words | orchestrator-routing.md + claude-system-prompt.md + chatgpt-system-prompt.md |
| Degradation tier counts | context-memory-discipline.md + both adapter prompts |
| Skill activation rules | hook + both adapter prompts |

This is a 3-file synchronization problem. After 18 fix cycles on the canonical files, the adapters are already partially stale — they don't include Fixes 16/17/18 changes.

**Architecture recommendation:** Create `kiro/adapters/shared-routing-core.md` — a single file containing the 5 routing rules, tier table, and skill activation protocol that both adapter prompts reference (or include via copy-paste note). When the canonical source changes, only this bridge file needs updating.

### 7C. "Fresh Context Invocation" Gap

Both adapters silently inherit this problem from the main system: qa_engineer is specified as a "fresh context invocation" (separate API call) in the architecture, but in Claude Projects or ChatGPT conversations, there is no mechanism for this. The QA role will execute in the same context as all prior roles — which is actually acceptable for review tasks, but the architecture documentation overpromises isolation.

### 7D. Model Capability Mismatch

The adapters don't currently include model-specific mode recommendations. Given different capability profiles:

| Model | Context | Reasoning | Recommendation |
|---|---|---|---|
| Claude Sonnet 4+ | 200K | High | Mode 1/4/5 safe |
| GPT-4o | 128K | High | Mode 5 preferred for safety on long builds |
| Claude Haiku | 200K | Medium | Mode 2/3 only |
| GPT-4o mini | 128K | Lower | Mode 3 only |
| o1/o3 | 200K | Very High | Architecture/ADR tasks; slow for implementation |

Adding a "Recommended model per mode" section to the setup guides would prevent users from running Mode 1 multi-sprint builds on models that can't sustain them.

---

## 8. FAILURE MODE ANALYSIS

### 8A. Failure Mode Catalog

| Failure | Probability | Detection | Current Recovery |
|---|---|---|---|
| CLAUDE-implemented.md always-loading | 🔴 CERTAIN | Token count audit | None (unknown) |
| Gate compliance failure (model skips SM-RETRO blocking rule) | ⚠️ Medium | Checkpoint review | None automated |
| Skill file not found (path wrong) | ⚠️ Medium | [SKILL MISSING] log | Backlog entry |
| Context overflow (mode 1 sprint > 80 exchanges) | 🟡 Likely | [HEADROOM WARNING] | Fresh session |
| Memory confidence inflation (wrong lessons at high confidence) | 🟡 Likely | Sprint retrospective | Manual downgrade |
| Lost-in-middle on team-orchestrator.md | 🟡 Likely | Inconsistent gate behavior | None |
| Step 0 gate incorrectly skipping Mode 2 requests | 🟡 Likely | User notices wrong mode | Retype with keyword |
| Adapter/canonical drift after future fixes | 🔴 Certain over time | Manual audit | 3-file sync |
| Role handoff >300 tokens (self-enforcement fails) | 🟡 Likely at sprint end | None | None |

### 8B. Highest Impact Unmitigated Risks

**Risk 1: CLAUDE-implemented.md always-load (23K token burn)**
Impact: Every session runs with 23K phantom tokens from an archive that should never auto-load. At scale, this is the difference between a 20-exchange session and a 15-exchange session before hitting 85% threshold. **Fix is one frontmatter line change.**

**Risk 2: team-orchestrator.md attention decay**
Impact: GATE 4 logic (MEMORY WRITE, SM-RETRO) may be inconsistently followed. Hard to detect because the model will still produce gate outputs — they just won't follow the exact protocol. **Fix requires file split.**

**Risk 3: Memory confidence inflation**
Impact: Wrong lessons elevated to HIGH confidence become binding constraints. A bad pattern applied as a "law" in a new sprint will degrade build quality silently. **Fix requires measurable criteria.**

---

## 9. WHAT'S WORKING EXCEPTIONALLY WELL

These are genuinely good AI systems engineering decisions worth preserving:

1. **Thin hook router (Fix 12C):** The move from 900-line constitution-in-hook to ≤60-line router is the most impactful single change in the system's history. It's architecturally correct and saves ~8,000 tokens of repeated loading per prompt.

2. **always/manual-inclusion split:** Loading steering files conditionally by mode is the right pattern. Most systems fail by always-loading everything.

3. **[ENV], [MODE], [SKILLS ACTIVATED] log lines:** Observable compliance markers are essential for debugging LLM systems. These make the system's behavior inspectable. More systems should do this.

4. **Skill activation max 3 files:** A hard cap prevents the "load everything relevant" failure mode that wastes context and reduces precision.

5. **ADRs as binding constraints (not suggestions):** The decisions.md pattern of architectural decisions as hard constraints (not guidelines) is correct. Models follow hard constraints more consistently than soft preferences.

6. **85% threshold offloading (Fix 13G):** Mechanically triggered offloading is more reliable than count-based triggers. This is the most robust context management mechanism in the system.

7. **Extract→Produce→Discard for skill files (Fix 17C):** The 5-line takeaway pattern is the correct way to use skill files. Keeping full file content in context after extraction is a common anti-pattern; this explicitly forbids it.

8. **SM-RETRO blocking rule (Sprint Discipline Card must be populated before retro):** A BLOCKING RULE that creates a hard dependency is the right enforcement mechanism for quality gates. Soft "try to populate" rules are ignored.

---

## 10. PRIORITIZED RECOMMENDATIONS

### P0 — Fix Immediately (Breaking Issues)

**P0-A: Fix CLAUDE-implemented.md always-load bug**
File: `kiro/CLAUDE-implemented.md`
Change: Line 2: `inclusion: always` → `inclusion: manual`
Impact: Recovers ~23,000 tokens per session. Highest ROI change in the system.

**P0-B: Fix discovery-engine.md always-load**
File: `kiro/steering/discovery-engine.md`
Change: `inclusion: always` → `inclusion: manual`
Impact: Recovers ~2,319 tokens on every Mode 3 session. Add explicit load to hook Step 3.

### P1 — High Value (Next Fix Cycle)

**P1-A: Split team-orchestrator.md into 3 phase files**
Eliminates lost-in-middle risk on GATE 4/5 content.
Files: team-orchestrator-core.md, team-orchestrator-develop.md, team-orchestrator-gates.md.

**P1-B: Expand Step 0 keyword list**
Add: WRITE, REVIEW, ANALYZE, AUDIT, RUN, CREATE to Step 0 bypass keywords.
Or tighten the word-count threshold from 8 to 5.

**P1-C: Measurable memory confidence criteria**
Update memory-management.md and MEMORY WRITE protocol with sprint-count-based criteria (low = 1 sprint, medium = 2+ sprints, high = 5+ sprints).

### P2 — Medium Value (Fix 19)

**P2-A: Role handoff structured format**
Define a standard ROLE HANDOFF template in team-orchestrator.md. Replace "compress to ≤300 tokens" with "use ROLE HANDOFF format." More consistent, more inspectable.

**P2-B: Domain tags in lessons.md**
Add `[domain:backend|frontend|data|mobile|all]` tags to each lesson entry. Update MEMORY WRITE to filter on domain before loading. Reduces irrelevant lesson loading.

**P2-C: Goal Anchor → tie to 85% threshold, not count**
More reliable trigger. Simpler instruction. Fewer missed injections.

**P2-D: shared-routing-core.md bridge file**
Single source of truth for adapter routing logic. Prevents 3-file drift on future fixes.

### P3 — Low Value / Long Term

**P3-A: Model-specific mode recommendations in adapter setup guides**
"Use Mode 5 on GPT-4o for builds longer than 2 sprints" type guidance.

**P3-B: System regression eval suite**
10 canonical scenarios in `docs/system-evals.md`. Run against any new model before adopting. Measures: mode routing accuracy, gate compliance, skill file selection.

**P3-C: Byte-based context pressure metric**
Supplement count-based degradation tiers with a KB-consumed metric.

---

## 11. FIX CYCLE HEALTH TREND

| Fix Range | Focus | System Health Change |
|---|---|---|
| Fixes 1–6 | Core routing, mode detection | +++ Foundation established |
| Fixes 7–9 | Hook thinning, skill activation | +++ Biggest efficiency gain |
| Fixes 10–11 | Loop engine, precision gaps | ++ Reliability improved |
| Fix 12 | Context discipline, memory | +++ Major quality improvement |
| Fix 13 | Cleanup, shared skills | ++ Maintainability improved |
| Fixes 14–15 | Design gate, report templates | + Feature completeness |
| Fix 16 | Critical bug fixes | ++ Correctness restored |
| Fixes 17–18 | Medium + low improvements | + Polish |
| **P0 fixes** | **Always-load bugs** | **+++ Token budget recovered** |

The system is mature. The highest remaining leverage is not new features — it's fixing the P0 always-load bugs and splitting team-orchestrator.md. Those two changes will have more practical impact on session quality than the entire Fix 17 batch.

---

## 12. FINAL ASSESSMENT

**Architecture:** The thin-router + constitution delegation + role-scoped skill files pattern is genuinely well-designed. It reflects understanding of how to work with LLM context windows rather than against them.

**Execution gaps:** The CLAUDE-implemented.md always-load bug, discovery-engine.md always-load, and team-orchestrator.md attention risk are the system's current ceilings on performance. They're not obscure edge cases — they affect every session.

**Model behavior alignment:** The system makes several assumptions (reliable tool-call counting, voluntary STOP at CRITICAL tier, self-enforced handoff compression) that models honor inconsistently. The design would be more robust if these relied on structural mechanisms rather than instruction compliance.

**Maturity verdict:** The system is production-ready for Mode 3 and Mode 5 usage. Mode 1 multi-sprint builds are viable but require careful session management and will benefit significantly from the P1-A team-orchestrator.md split.

The next fix cycle should focus exclusively on P0 fixes and P1-A. Everything else can wait.

---

*Review produced: 2026-06-30 | Based on: Fixes 1–18, token measurements, model behavior research (Liu et al. 2023 lost-in-middle study, documented instruction-following degradation curves for Claude 3.5/4 and GPT-4o series)*
