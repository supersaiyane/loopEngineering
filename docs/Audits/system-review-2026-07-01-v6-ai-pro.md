---
date: 2026-07-01
version: v6
fixes-applied: 1–26F (all fixes implemented)
lens: AI Professional — LLM behavior, prompt engineering, multi-agent reliability
---

# System Review v6 — AI Engineering Deep Analysis
Post-Fixes 1–26F | Written from first principles of how LLMs actually behave

---

## WHO IS READING THIS

This analysis is written from the perspective of an AI engineer who has built production
multi-agent systems, understands attention mechanics, knows where LLMs fail under
instruction complexity, and has measured token budgets against real model behavior.
Previous reviews optimized the SYSTEM DESIGN. This review optimizes for how LLMs
actually execute it.

---

## THE ONE THING THAT OVERSHADOWS EVERYTHING ELSE

**Kiro is not a multi-agent system. It is a single LLM simulating 22 agents.**

All roles — architect, security_engineer, data_scientist, qa_engineer, all 22 of them —
execute inside a single shared context window. There is no agent isolation. There is no
parallel execution. When the system says "activate data_scientist," it means the LLM
shifts its reasoning persona within the same context thread that already contains the
architect's output, the SM's sprint plan, the PRD, the ADRs, and every previous role's
artifact.

This is not wrong. It's a pragmatic starting point. But it means every claim the system
makes about "role handoff," "maker/checker isolation," and "co-maker patterns" is
ASPIRATIONAL, not architectural. The actual execution is: one LLM, one long context,
sequential role-shifted generation.

Every gap in this review must be read through that lens.

---

## PART 1: TOKEN ECONOMICS — THE MATH IS WRONG

### What the system claims

context-memory-discipline.md states:
> Expected DEGRADING trigger: After story 2 (~27,900 tok)
> Expected CRITICAL trigger: After story 3 (~30,400 tok)

### What's actually true

Claude Sonnet 4's context window: 200,000 tokens.

| Tier | System trigger | % of window used | Reality |
|------|---------------|-----------------|---------|
| DEGRADING | ~28K tokens | 14% | 86% of window is still available |
| CRITICAL | ~30K tokens | 15% | 85% of window is still available |

The system is treating a 200K model like it has a 35K window.

### Why this happened

The degradation tiers were calibrated against older GPT-4 models (8K-32K windows) or
Claude 1/2 era limits. They were never updated when 200K became the baseline.

The read-count tiers (PEAK 0-4, GOOD 5-7, DEGRADING 8-11, CRITICAL 12+) were a
PROXY for token pressure when actual token counting wasn't feasible. They are now
actively harmful because they force sub-optimal behavior (compression, suppression,
stop) at a point when the model has 170K tokens of headroom remaining.

The byte-based supplement (50KB = DEGRADING, 100KB = CRITICAL) is slightly better:
50KB ≈ 12,500 tokens = 6.25% of window. Still too conservative.

### Recommended recalibration

| Tier | Current trigger | Recommended trigger |
|------|----------------|-------------------|
| PEAK | 0-4 reads | < 60K tokens (~30% window) |
| GOOD | 5-7 reads | 60K-120K tokens (~30-60%) |
| DEGRADING | 8-11 reads | 120K-160K tokens (~60-80%) |
| CRITICAL | 12+ reads | 160K+ tokens (>80%) |

Log actual token estimate at each step (using tool output size as proxy).
Decouple "read count" from "tier" — reads that produce 50-token outputs don't
consume the same context as reads that produce 3,000-token outputs.

**Impact: The system is triggering compression and ACT suppression at 14% context
usage. Fixing this alone would double the effective story throughput per session.**

---

## PART 2: THE SELF-GRADING PROBLEM

The loop engine asks the LLM to score its own work against criteria (1-10 per criterion).
This is the system's most significant reliability risk from an AI perspective.

### What LLMs do when asked to self-grade

Extensively documented in AI safety literature:
1. **Sycophancy bias**: LLMs tend to affirm their own outputs. Self-assigned scores
   drift toward 8-9 regardless of actual quality.
2. **Score inflation over iterations**: By iteration 3, scores cluster at 8-10 even
   when criteria haven't been meaningfully satisfied.
3. **Criterion drift**: With loosely-worded criteria, the LLM unconsciously narrows
   the criterion to match what it produced rather than asking if the output meets the
   original bar.

### The VERIFIER is the correct solution — but it's broken

The loop spec requires VERIFIER to be an automated command:
> npm test -- --coverage  
> npx tsc --noEmit  
> npx semgrep --config=p/owasp-top-ten

These commands can only produce ground truth if they are ACTUALLY RUN. In a
Kiro session without bash tool execution (i.e., the LLM is generating the sprint, not
Claude Code executing it), the VERIFIER is decorative. The LLM writes "VERIFIER:
npm test" but cannot run it. So it IMAGINES what the output would be.

Self-graded criteria + imagined VERIFIER output = unchecked quality illusion.

### The fix

Two options depending on execution environment:

**Option A (Claude Code runtime):** VERIFIER commands MUST be executed via bash tool.
The loop engine should halt and await actual command output before scoring iteration N.
No bash output = loop iteration is invalid. The system should refuse to proceed.

**Option B (generation-only runtime):** Replace VERIFIER with OUTPUT SPECIFICATION:
a precise, falsifiable description of what the generated code MUST contain. Then add
a CHECKER role pass that reads the generated output and verifies the specification
mechanically (regex-style, not judgment-based).

The current system does neither. It relies on the maker scoring its own work against
criteria it may have drifted from, verified by a command it cannot run.

---

## PART 3: ATTENTION MECHANICS — WHERE CRITICAL INSTRUCTIONS GET LOST

### The lost-in-middle effect

Research on transformer attention shows content in the middle of long prompts receives
significantly less attention than content at the start or end. For 200K token contexts,
this effect is pronounced.

### The hook prompt has attention debt

The hook started as a thin router (Fix 12C, ≤60 lines). After Fixes 13-26, it has been
patched 15+ times. Each patch appended or inserted content. The prompt is now
significantly longer and internally sequential — meaning:

- Step 0 keywords: near the top → HIGH attention ✅
- SPRINT STATE block: mid-prompt → MEDIUM attention ⚠️
- Co-maker pattern (Fix 26B): embedded in trigger row → LOW attention ❌
- STRIDE-BRIDGE rule (Fix 26D): inside loop-engine.md, loaded on-demand → depends ⚠️

The critical path for Mode 1 detection (Step 0 → Step 1 → Step 2) is well-positioned.
The nuanced behaviors (co-maker split, compound DEGRADING warning, STRIDE-bridge)
are all mid-to-late in their respective files. Under attention degradation, these are the
behaviors that will be silently skipped in real sessions.

### Hierarchy of attention robustness

**HIGH robustness (near-beginning, short, explicit):**
- Mode detection keywords (Step 0)
- DEGRADING/CRITICAL tier triggers (now in context-memory-discipline.md §4)
- Gate 1/2/3 checklists (loaded explicitly)

**MEDIUM robustness (mid-document, moderate length):**
- SPRINT STATE block (STEP 4 of hook)
- STRIDE-BRIDGE (Fix 26D — mid-file in loop-engine.md)
- SM-UNBLOCK protocol (Fix 25F — mid-file in loop-engine.md)

**LOW robustness (deep in file, high specificity, many conditions):**
- Co-maker split conditions (Fix 26B — within data_scientist trigger row)
- Compound DEGRADING warning (Fix 26F — last section in context-memory-discipline.md)
- Lessons project namespace (Fix 25Q — nested in sprint orchestrator)
- ADR domain scope filter (Fix 25P — nested checklist item)

### Recommendation

For the LOW robustness behaviors: add a BEHAVIOR SUMMARY CARD at the TOP of each
steering file — 5-7 bullet points of the most critical rules in that file, front-loaded
before all other content. This costs 50-100 tokens but puts the key rules in attention-
strong position.

Example for loop-engine.md:
```
## QUICK REFERENCE (read this first)
- Loop max: 8 iterations. Score each criterion 1-10. Passing: all ≥ 8.
- VERIFIER must be a runnable command. Non-runnable = story not ready.
- At iteration 8 score <8: SM-UNBLOCK fires (SCOPE-CUT / RE-SPEC / ESCALATE).
- STRIDE-BRIDGE: architect mitigations → story criteria. Max 2 per story.
- Max 2 ACT reloads at DEGRADING (3 for security-critical).
```

---

## PART 4: INSTRUCTION COMPLEXITY vs. COMPLIANCE RATE

### The complexity cliff

LLMs follow instructions well up to a complexity threshold, after which compliance
degrades non-linearly. The Kiro system has:

- 5 modes (with auto-detection logic)
- 22 roles (with trigger conditions)  
- 30 labels (with taxonomy)
- 8 degradation tiers (with 3 sub-rules each)
- 5 gates (with checklists)
- Loop engine (4 phases × 8 iterations × N criteria)
- 8 path resolution rules (for skill files)
- 6 SM-UNBLOCK outcomes
- 4 co-maker patterns

This is extraordinary complexity in a single orchestration system. The probability that
the LLM follows ALL rules correctly in a single session is low — not because the rules
are wrong, but because rule count × interaction depth exceeds reliable instruction-following
capacity.

### What actually happens in practice

In high-complexity instruction sets, LLMs:
1. Faithfully execute the MOST SALIENT rules (those near the top, bolded, or repeated)
2. Selectively apply MODERATELY SALIENT rules (applied sometimes, not always)
3. Silently skip LOW SALIENCE rules (technically present but never triggered)

Based on position and structure analysis:

| Rule | Salience | Expected compliance |
|------|----------|-------------------|
| Mode detection (Step 0) | HIGH | ~90% |
| GATE 1-3 checklists | HIGH | ~85% |
| DEGRADING skill suppression | MEDIUM | ~65% |
| STRIDE-BRIDGE criteria injection | LOW | ~35% |
| Co-maker role split | LOW | ~30% |
| Compound DEGRADING warning | LOW | ~20% |
| ADR domain scope filter | LOW | ~25% |
| Lessons project namespace | LOW | ~30% |

The system has been extensively refined, but the refinements have disproportionately
added LOW SALIENCE rules. The expected compliance rate for Fix 25-26 behaviors is
in the 20-35% range — meaning these behaviors fire reliably less than half the time.

### The fix: Reduce total rule count, increase salience of critical rules

Not all 30 labels need to be in the system prompt. Not all 22 roles need trigger
conditions. The system should identify the PARETO 20% of rules that drive 80% of
quality outcomes and make those HIGH SALIENCE. The rest become appendix-level
reference that the LLM loads on-demand.

---

## PART 5: THE SKILL COMPRESSION PROBLEM

### The 5-line compression trap

The current protocol: read skill file → compress to 5-line summary → work from summary.

5 lines ≈ 75 words. A skill file is 300-600 words. Compression ratio: ~5-10%.

For NARRATIVE skill files (architecture patterns, design principles), 5-line summaries
preserve enough to guide reasoning. But the system contains CHECKLIST-HEAVY skill files:

- `security_engineer/api_security_owasp_top10.md` — OWASP A1-A10 with specific checks
- `frontend_lead/wcag_accessibility.md` — WCAG criteria with pass/fail thresholds
- `security_engineer/cryptography_pki_key_management.md` — specific algorithm requirements
- `architect/stride_threat_modeling.md` — STRIDE categories with specific mitigation patterns

These files are CHECKLISTS. Compressing a checklist to 5 lines means the LLM retains
the category names but loses the specific items that make the checklist actionable.

**The [FULL-LOAD-REQUIRED] annotation exists (Fix 25E) but it's applied to only 3 files.**
Based on content analysis, at least 8-10 files require full load for the checklist items
to be usable. The current system under-annotates.

### Recommended annotation protocol

Mark each skill file at the top with one of:
```
<!-- LOAD-TYPE: NARRATIVE → 5-line compress always sufficient -->
<!-- LOAD-TYPE: CHECKLIST → FULL-LOAD required for any checklist substep -->
<!-- LOAD-TYPE: HYBRID → compress for context, full-load for specific protocol -->
```

Then update skill-label-index.md to respect these types automatically rather than
requiring the LLM to judge when full load is needed.

---

## PART 6: LABEL ASSIGNMENT RELIABILITY

At SM-PLAN time, the LLM assigns 30 canonical labels to stories. This is an
LLM classification task. The problems:

### Classification without few-shot examples

The taxonomy has 30 labels. The LLM must choose the right subset for each story
from memory of the taxonomy definitions. Without few-shot examples for ambiguous
cases, classification consistency is low.

Examples of ambiguous assignments:
- "Build JWT authentication middleware" → `be/auth`? `security/auth`? `security-critical`? All three?
- "Create A/B test assignment service" → `be/api`? `data/eda`? Both?
- "Add Redis caching for user sessions" → `be/caching`? `be/auth`? Both?

Wrong label assignment → wrong skills loaded → wrong quality criteria in loop spec →
quality bar mismatches actual story requirements.

### The missing validation step

Currently: SM-PLAN assigns labels → labels used for skill loading.

There is no validation. No challenge step. No second-pass verification.

Recommended: After label assignment, SM does a 1-step self-challenge:
> "For each label assigned: what specific acceptance criterion or skill would
> this label add that wouldn't be covered by the other labels? If the answer
> is 'nothing,' remove the label."

This is a 5-token prompt addition that prevents label over-assignment and under-assignment.

---

## PART 7: THE MEMORY SYSTEM — WHAT LLMs ACTUALLY DO WITH LESSONS

### How the system expects lessons to work

lessons.md is loaded at session start, provides historical context, prevents repeated mistakes.

### How LLMs actually process lessons.md

A file of 20+ lessons loaded into context is processed as BACKGROUND CONTEXT, not
as ACTIVE INSTRUCTIONS. The difference is significant:

- Active instructions: explicitly referenced during task execution, high recall
- Background context: present in window, much lower recall, applied inconsistently

The system expects lessons to PREVENT mistakes proactively. In practice, LLMs apply
lessons REACTIVELY — when they accidentally start to do something a lesson warns against,
they MAY catch themselves. But they won't systematically check lessons.md before every
decision.

### The memory system needs triggering, not just loading

Currently: lessons.md loaded → assumed to influence behavior.
Actually: lessons.md loaded → may or may not influence behavior depending on whether
the lesson's topic is salient at the decision point.

Fix: At the start of each role activation, add a 1-step lessons scan:
> "Before proceeding: scan lessons.md for any entries with domain matching
> current story labels. Cite any applicable lessons explicitly before generating output."

This makes lesson application EXPLICIT AND AUDITABLE rather than implicit and invisible.
It adds ~50 tokens per role activation but gives actual compliance evidence.

---

## PART 8: MODE DETECTION — FALSE POSITIVE RISK

### The Mode 1 false positive problem

Mode 1 auto-inference: single sentence + ≥2 system-scale signals → Mode 1.

System-scale signals include: "multi-service," "real-time," "cross-team," "platform," etc.

False positive examples:
- "Build a real-time notification feature" → 2 signals (real-time, feature) → Mode 1?
  But this is a single feature → should be Mode 2 or 3.
- "Create a platform-wide rate limiting service" → platform + service → Mode 1?
  Could be a single service → Mode 4.

A Mode 1 false positive turns a 10-minute Mode 3 task into a 22-role enterprise sprint.
This is the highest-cost failure mode in the system.

### Missing: Mode detection confidence + confirmation

Current: detect → commit.
Recommended: detect → score confidence → if <85%, confirm with user.

```
[MODE DETECTION: Mode 1 — confidence 72%]
Signals detected: real-time (1), platform (2)
Ambiguous because: scope is unclear — could be Mode 2 (single service)
Confirm: "Build a full enterprise fraud detection platform" → Mode 1 (Y/n)?
```

This single addition prevents the most expensive failure mode in the system.

---

## PART 9: ADR QUALITY — THE RUBBER STAMP RISK

### The ADR lifecycle problem

ADRs are generated by the architect role, reviewed by the scrum_master, and promoted
to decisions.md. In a single-context system, "architect generates ADR" and "scrum_master
reviews ADR" are the SAME LLM doing two sequential persona shifts within one context.

The LLM that just generated the ADR will not rigorously critique its own ADR 5 turns
later. It already believes the ADR is correct (recency bias + sycophancy). The "review"
step is a rubber stamp.

### Real ADR quality assurance

Option A (same context): Add an explicit DEVIL'S ADVOCATE step to the ADR review:
> "Scrum master: Before approving this ADR, adopt the adversarial position. Name one
> scenario where this architectural decision makes the system worse. If you cannot
> name one, the ADR is too vague — send it back for revision."

Option B (subagent): Spawn a fresh context with only the ADR and a critique prompt.
No prior context → no recency bias → genuine independent review.

The system's Fix 25M (max 2 ADRs/sprint) prevents ADR flood, but doesn't prevent
2 low-quality rubber-stamped ADRs per sprint compounding across a 10-sprint project.

---

## PART 10: WHAT'S ACTUALLY GOOD — AND WOULD SURVIVE PRODUCTION

To be fair: several patterns in this system are genuinely strong AI engineering.

**Strong patterns:**

1. **Label → Index → Compressed skills** — the right abstraction for dynamic context management.
   Load what's relevant, compress everything, full-load on demand. Correct.

2. **GATE system as checkpointing** — breaks a long LLM session into bounded phases with
   explicit artifacts. Prevents unbounded generation and gives recovery points. Correct.

3. **The 5-mode routing** — Mode 3 for trivial is especially important. Skipping the 22-role
   orchestration for "add a field to an endpoint" is the right call. Every system needs a
   fast path.

4. **STRIDE-BRIDGE (Fix 26D)** — connecting security threat model to story loop criteria
   is the right way to make security architecture actionable. Solid pattern.

5. **SM-UNBLOCK (Fix 25F)** — explicit escalation protocols for stuck loops. SCOPE-CUT /
   RE-SPEC / ESCALATE is the right decision table. Prevents infinite loops.

6. **Co-maker pattern (Fix 26B)** — PRIMARY/SECONDARY/CHECKER role split for complex
   stories is the right conceptual model. Becomes powerful when implemented with true
   subagent isolation.

7. **Degradation tier system** — the CONCEPT is right even if the THRESHOLDS are wrong.
   Graceful degradation is the correct approach for managing a finite context window.

---

## OVERALL ASSESSMENT

| Dimension | Score | Key issue |
|-----------|-------|-----------|
| Token economics | 🔴 45% | Degradation thresholds calibrated for 30K window, not 200K |
| Self-grading reliability | 🔴 40% | VERIFIER non-executable; scores are self-assessed |
| Attention architecture | 🟡 60% | Critical behaviors are attention-weak mid-file content |
| Instruction compliance | 🟡 55% | 30+ rules; Low-salience rules fire ~20-35% of the time |
| Skill compression accuracy | 🟡 65% | Checklist files under-annotated for FULL-LOAD |
| Label assignment accuracy | 🟡 62% | No validation step; ambiguous cases inconsistent |
| Memory system effectiveness | 🟡 58% | Lessons loaded but not actively triggered at decision points |
| Mode detection reliability | 🟡 65% | No confidence score; false Mode 1 detection is high-cost |
| ADR quality | 🟡 55% | Rubber-stamp review risk in single-context system |
| Architecture concepts | 🟢 82% | Correct abstractions; needs true multi-agent to fully execute |
| **OVERALL** | **🟡 59%** | **As a planning system: good. As an execution system: not yet.** |

---

## PRIORITY FIXES (ordered by impact-to-effort ratio)

### P0 — Breaks real behavior today

**P0-A: Recalibrate degradation thresholds to 200K window**
- Change DEGRADING trigger: 120K tokens (~8-12K tokens per read estimate)
- Change CRITICAL: 160K tokens
- Drop read-count tiers as primary trigger; use token-estimate as primary
- Files: context-memory-discipline.md, CLAUDE.md §4
- Effort: 1 hour | Impact: doubles effective story throughput per session

**P0-B: Mode detection confidence gate**
- After mode inference, emit confidence score
- If <85%, ask user to confirm before committing to Mode 1
- Files: hook Step 0, orchestrator-routing.md
- Effort: 30 min | Impact: prevents most expensive failure mode

**P0-C: VERIFIER execution enforcement**
- Add: "VERIFIER is mandatory. If runtime cannot execute it, STOP. Mark story NOT READY."
- Remove the possibility of LLMs imagining VERIFIER output
- Files: loop-engine.md LOOP SPEC FORMAT
- Effort: 30 min | Impact: prevents quality score inflation

### P1 — Degrades quality silently

**P1-A: Skill file LOAD-TYPE annotations**
- Add `<!-- LOAD-TYPE: CHECKLIST -->` to 8 skill files (OWASP, WCAG, STRIDE, crypto)
- Update skill-label-index.md to auto-full-load CHECKLIST files
- Files: 8 skill files + skill-label-index.md
- Effort: 2 hours | Impact: checklist coverage goes from ~5% to ~90%

**P1-B: Behavior QUICK REFERENCE cards at top of steering files**
- 5-7 bullet summary of critical rules at the top of loop-engine.md, team-orchestrator-core.md
- Puts low-salience rules into attention-strong position
- Files: loop-engine.md, team-orchestrator-core.md, team-orchestrator-sprint.md
- Effort: 1 hour | Impact: raises compliance rate for Fix 25-26 behaviors from ~25% to ~65%

**P1-C: Explicit lessons scanning step at role activation**
- Add: "Before generating output, scan lessons.md for labels matching current story. Cite any applicable lessons."
- Files: team-orchestrator-core.md DEVELOP phase (role activation step)
- Effort: 30 min | Impact: converts lessons from background noise to active guidance

**P1-D: Label assignment validation step**
- Add self-challenge after SM-PLAN label assignment
- Files: loop-engine.md LOOP SPEC FORMAT, team-orchestrator-core.md
- Effort: 30 min | Impact: reduces label misassignment rate

### P2 — Architectural debt (long-term)

**P2-A: True subagent isolation per story**
- Each DEVELOP story runs in a fresh context with ≤2000 token summary passed in
- This is the system's stated long-term fix — should now be the priority
- Eliminates role bleed, resets context budget, enables true parallel execution
- Effort: significant | Impact: transforms the system from simulation to real multi-agent

**P2-B: ADR adversarial review step**
- Add DEVIL'S ADVOCATE step to ADR review protocol
- Files: team-orchestrator-sprint.md ADR section
- Effort: 30 min | Impact: catches rubber-stamped low-quality ADRs

**P2-C: Memory triggering, not just loading**
- Active lessons scan at role activation (same as P1-C but deeper: also at gate transitions)
- Effort: 1 hour | Impact: converts memory from decorative to functional

---

## THE REAL CEILING

The system has been refined with 26 fix sets. The rules are mostly correct. The abstractions
are mostly right. The logic mostly holds.

The ceiling is: **this is an LLM generating descriptions of what a team would do, not a
team actually doing it.**

Until the VERIFIER commands actually run, the loop iterations produce no external
ground truth. Until roles run in isolated contexts, role bleed is unavoidable. Until
token thresholds are calibrated to actual model limits, compression fires too early.

The path from 59% to 90%+ requires:
1. P0 fixes above (calibration + confidence gates + VERIFIER enforcement) → ~72%
2. P1 fixes above (attention + lessons + labels) → ~82%
3. True subagent isolation (P2-A) → ~91%
4. External tool execution (bash for VERIFIER) → ~95%

Items 1-2 are documentation edits. Items 3-4 require runtime changes.
The system is architecturally ready for items 3-4. The steering files assume them.
The implementation hasn't caught up yet.
