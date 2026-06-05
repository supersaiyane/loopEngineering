---
inclusion: always
---


## ⚡ QUICK REFERENCE — Context & Token Discipline (read this first)
- **Token tiers (Fix 27A)**: PEAK <60K | GOOD 60–120K | DEGRADING 120–160K | CRITICAL >160K
- **Token estimate is PRIMARY trigger**. Read-count is secondary. Log: `[TOKEN ESTIMATE: ~NKB | Tier: X]`
- **At DEGRADING**: max 2 ACT reloads/story (security-critical: 3). Compress all skills. [Fix 25G]
- **Compound DEGRADING (Fix 26F)**: 2+ consecutive max-ACT stories → pre-warn remaining stories.
- **At CRITICAL**: complete current story only → STOP (unless last story → proceed to SM-RETRO). [Fix 25D]
- **Byte-based supplement**: >50KB accumulated = DEGRADING override. >100KB = CRITICAL override. [Fix 20F]
- **Goal Anchor**: inject at 85% threshold. All work must advance `$ORIGINAL_OBJECTIVE`.
---
# Context & Token Discipline (Core Rules)

Lean behavioral constraints loaded every session. Memory management and reporting
templates split into conditional files to reduce always-on context cost.

---

## 1. CONTEXT BUDGET ALLOCATION

| Section | Max % of Context | Strategy |
|---------|-----------------|----------|
| System prompt + steering | 15% | Always loaded, keep lean |
| Hook outputs | 10% | Cap length, most-recent-only |
| Memory (init_docs) | 15% | Retrieval-based: load RELEVANT only |
| Tool outputs (bash, reads) | 25% | Cap 80 lines, summarize, strip noise |
| Code generation (primary work) | 35% | Main output — this gets priority |

Enforcement: exceed cap → compress/truncate BEFORE proceeding. Maintain 10% headroom minimum.

---

## 2. CAVEMAN ULTRA — STRICT ENFORCEMENT

- Max 1 status sentence before acting. No preambles.
- Fragments > prose. Technical shorthand > full English.
- BANNED: "Let me...", "I'll now...", "Here's what I did", "Sure!", "Great question", "Absolutely"
- Q&A: 1-3 lines max unless user asks "explain" or "why"
- Self-check: "Can I cut 50% and lose zero info?" If yes → cut.

---

## 3. CONTEXT HEADROOM

- At 85% → "[HEADROOM WARNING]" + summary-only mode
- At 90% → FULL STOP. Checkpoint. Recommend new session.
- Collapse tool outputs to 1-line summaries after use.
- Each tool call ≈ 500 tokens. Budget accordingly.

| Exchanges | Action |
|-----------|--------|
| < 20 | Normal ops |
| 20-35 | Compress aggressively |
| 35-50 | Summary-only, no new reads unless editing |
| 50+ | MANDATORY checkpoint + fresh session |

---

## 4. SELF-ADAPTIVE CONTEXT PRUNING

KEEP IN FULL: files being modified, errors being debugged, current role artifacts.
SUMMARIZE TO 3 LINES: explored-but-not-modified, different subsystem, >15 exchanges old.
DISCARD: already-summarized tool output, dead-end exploration, processed hooks.
SKILL FILES: Load ALL activity-relevant files from the skill matrix row (no hard count cap).
             For EACH file: read → compress to 5-line takeaway → discard full content.
             Work from summaries. Soft cap: Σ compressed skill context ≤ 2,000 tokens per activation.
             On-demand full load: re-load ONE file for a specific protocol-heavy substep → execute → discard.
             Pattern: Load-All → Compress-Each → Work-From-Summaries → On-Demand-Single
             Old "max 3 files" hard cap (Fix 9) SUPERSEDED by this rule (Fix 20G).
             Token math: 8 files × 60 tokens = 480 compressed vs 3 files × 500 full = 1,500 tokens.
             Log: [SKILLS: role=X | N files | Σ~Ntok compressed]
**BYTE-BASED PRESSURE SUPPLEMENT (Fix 20F):**
Track accumulated tool output volume as a secondary pressure signal:
  - Estimate each tool output at ~2-4KB average.
  - If cumulative output > 50KB since session start → treat as DEGRADING regardless of read-count tier.
  - If cumulative output > 100KB → treat as CRITICAL regardless of read-count tier.
  Log: `[PRESSURE: ~NKB accumulated. Tier override: DEGRADING/CRITICAL]`
  Formula shortcut: 20+ tool calls with non-trivial output ≈ 50KB threshold.
  This supplements (does not replace) the read-count degradation tiers in CLAUDE.md §4.

---

## 5. GOAL ANCHOR + CONTINUOUS EVICTION (at 85% threshold — Fix 20E)

**GOAL ANCHOR (inject first, before eviction scoring):**

At session start, capture the user's first message as `$ORIGINAL_OBJECTIVE`. Never paraphrase it.

At every 85% THRESHOLD CHECK, inject verbatim (before eviction — Fix 20E):
```
[GOAL ANCHOR — tool call N]: Original objective: "<$ORIGINAL_OBJECTIVE>".
All current work must advance this objective directly.
If the last 3 tool calls did not advance this → STOP. Re-read the objective. Re-route.
```

Goal drift signal: agent re-narrates earlier reasoning instead of advancing toward the objective. If detected, inject the anchor immediately without waiting for the 10-call interval.

**CONTEXT LEVEL CHECK (at every 85% threshold check — also triggers Goal Anchor):**
```
Context level check IS the trigger — 85% threshold fires Goal Anchor + eviction together.
  Log: [CONTEXT CHECK — ~X% used. Goal Anchor injected. Offloading: YES/NO]
```

**CONTINUOUS EVICTION (run after goal anchor injection):**

Score retained items (0-10): relevance(0-5) + recency(0-3) + uniqueness(0-2).
- Score < 4 → evict (1-line stub)
- Score 4-6 → compress (2-3 lines)
- Score 7-10 → keep full

**85% THRESHOLD OFFLOADING (Fix 13G):**

When context reaches 85% of the model's window:
1. For each tool call result older than 5 turns: compress to `"[tool_name result: <5-word summary>. Full output: checkpoint.md §N]"`
2. Write the compressed content to checkpoint.md under a new section
3. Log: `[85% THRESHOLD — context offloaded, estimated N tokens recovered]`
4. Continue session with the compressed context

---

## 6. STRICT AGENT ISOLATION

Subagent prompts < 2000 tokens total. Pass summaries only (max 500 tokens each).
Never pass: full docs they won't modify, other roles' outputs, conversation history, raw tool outputs.

---

## 7. TOKEN ESTIMATION (Per-Task Micro Report)

```
> Reads: X. Tier: Y. Estimated tokens saved: Z%.
```

Formula: savings_percent = (naive_total - actual_total) / naive_total × 100

---

## CONTEXT ROT THRESHOLDS

| Metric | Green | Yellow | Red |
|--------|-------|--------|-----|
| Steering total lines | < 300 | 300-500 | > 500 |
| checkpoint.md entries | < 20 | 20-30 | > 30 |
| lessons.md entries | < 15 | 15-20 | > 20 |
| init_docs size | < 15KB | 15-25KB | > 25KB |
| Session exchanges | < 30 | 30-50 | > 50 |
| Tool calls | < 15 | 15-25 | > 25 |

Red = mandatory action (archive/split/fresh session).

---

## DEVELOP-PHASE DEGRADATION RULES (Fix 24F / Fix 27A)

Default degradation tiers (PEAK/GOOD/DEGRADING/CRITICAL) apply globally. These rules add
DEVELOP-specific behavior when the tier is hit mid-sprint.

### TOKEN-ESTIMATE TIERS (Fix 27A — primary trigger, replaces read-count)

Use cumulative tool output size as token proxy (~2-4KB per tool call avg):

| Tier | Token estimate | % of 200K window | Behavior |
|------|---------------|-----------------|----------|
| PEAK | < 60K | < 30% | Full ops — all reads, reloads allowed |
| GOOD | 60K–120K | 30–60% | Targeted reads (offset+limit). Prefer map. |
| DEGRADING | 120K–160K | 60–80% | Compressed only. Suppressed reloads (see below). |
| CRITICAL | > 160K | > 80% | FULL STOP after current story. |

Log at each DEVELOP story start: `[TOKEN ESTIMATE: ~NKB accumulated | Tier: X]`
Read-count tiers remain as SECONDARY signal. Token estimate is PRIMARY. Higher tier wins.

### At DEGRADING tier during DEVELOP:
- Skill loading: labels → index lookup → compressed summaries ONLY
- On-demand full reloads: SUPPRESSED — except for `security-critical` stories (non-negotiable)
  - OWASP substep and STRIDE threat model: FULL LOAD always allowed regardless of tier
- Loop engine: max 2 ACT full-reloads per story (Fix 25G: raised from 1 — multi-criteria failures need 2+ targeted reloads)
  - Security-critical stories: max 3 ACT reloads regardless of tier
  - Priority: reload LOWEST scoring criterion's skill file first; second reload for next-lowest
  - If 2 ACTs exhausted AND score still <8 at iteration 8: SM-UNBLOCK fires (see loop-engine.md Fix 25F)
- Log: `[DEGRADING: story X — full skill reload suppressed | exception: security-critical substeps | ACT used: N/2]`

### Compound DEGRADING Warning (Fix 26F):
If 2+ consecutive stories each exhausted max ACTs at DEGRADING tier:
- Pre-compute: will remaining stories fit in token budget?
- Formula: remaining_stories × avg_story_tokens > remaining_budget → WARN
- Emit: `[COMPOUND-DEGRADING: N consecutive stories hit max ACT. Remaining: M stories. Projected CRITICAL in ~K stories. Options: (1) Fresh session now. (2) Scope-cut remaining stories. (3) Continue with SUPPRESSED reloads.]`
- Offer scope-cut: SM may invoke SM-UNBLOCK SCOPE-CUT preemptively for all remaining stories
- Log: `[COMPOUND-DEGRADING: streak=N | remaining=M | projected_critical=K]`

### At CRITICAL tier during DEVELOP:
- PAUSE DEVELOP. Do not start the next story.
- Emit: `[CRITICAL TOKEN TIER — completing story X only. Recommend fresh session for remaining N stories.]`
- Complete current story's loop to closure (or hard-stop at 8 iterations).
- Write final loop-state to $TRACKER / docs/phase-N/loop-states/[story-id].md before stopping.
- **Last-story rule (Fix 25D):**
  IF CRITICAL fires AND no stories remain after current one:
    → complete current story → proceed to GATE 4 / SM-RETRO (~2K tok, cheaper than DEVELOP)
    → emit: `[CRITICAL: last story — proceeding to SM-RETRO]`
  IF CRITICAL fires AND stories remain:
    → complete current story → STOP. Do not start next story.
- SM-RETRO can still run at CRITICAL if sprint stories are all closed — retro is lower token cost than DEVELOP.

**SM-RETRO CRITICAL exception (Fix 29D):**
SM-RETRO writes are EXPLICITLY PERMITTED at CRITICAL tier. This is the ONLY category of writes allowed after CRITICAL fires.
Permitted SM-RETRO writes at CRITICAL:
  - `docs/lessons.md` — lesson entries (~500 tokens)
  - `docs/checkpoint.md` — sprint row (~200 tokens)
  - `docs/phase-N/impl-decisions.md` — key decisions (~500 tokens)
Total estimated SM-RETRO write cost: ~2K tokens. This is required for session continuity.
Log: `[CRITICAL: SM-RETRO writes permitted — ~2K tok. Writing lessons + checkpoint + impl-decisions.]`
Do NOT skip SM-RETRO at CRITICAL. The stop rule applies to DEVELOP stories only.

### Token math reference (Mode 1 baseline):
| Stage | ~Tokens consumed |
|-------|-----------------|
| Mandatory files (STEP 4) | ~11,900 (after Fix 24G split) |
| THINK phase (3 roles) | ~3,500 |
| SM-GATE + SM-PLAN | ~2,800 |
| skill-label-index.md (SM-PLAN load) | ~4,700 |
| **Baseline at DEVELOP start** | **~22,900** |
| Per story DEVELOP (avg 2 loop iters) | ~2,500 |
| **Recalibrated DEGRADING trigger** [Fix 27A] | **~120K tokens (~60% of 200K window)** |
| **Recalibrated CRITICAL trigger** [Fix 27A] | **~160K tokens (~80% of 200K window)** |
| ~~Old DEGRADING~~ | ~~After story 2 (~27,900 tok) — was 14% of window~~ |
| ~~Old CRITICAL~~ | ~~After story 3 (~30,400 tok) — was 15% of window~~ |

**Implication:** Mode 1 sprints with 4+ stories will hit DEGRADING by story 3. This is expected.
Mitigation: sub-agent isolation (each story in a fresh sub-agent context) is the long-term fix.
Short-term: apply DEVELOP degradation rules above for stories 3+.

**CHECKLIST token cost addendum (Fix 29B):**
CHECKLIST files (<!-- LOAD-TYPE: CHECKLIST -->) are full-loaded and DO consume actual context tokens.
They are excluded from the 2,000-token soft cap calculation but are NOT excluded from total context consumption.
Always account for CHECKLIST files in tier estimation: add their full token size to the running total.
Log format: `[SKILLS: narrative=A,B ~Ntok | checklist=C,D ~Ntok full | Total: ~Ntok | Tier: X]`
