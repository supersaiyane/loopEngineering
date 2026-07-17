# Kiro Elite Team — AI Professional System Review v4
**Date:** 2026-06-30  
**Reviewer lens:** Senior AI systems engineer — token economics, model behavior, orchestration, prompt engineering  
**Based on:** Post-Fix-19 state. All measurements taken from live files.  
**Prior review:** v3 (same day, pre-Fix-19). Compare this against v3 to see what changed.

---

## CONFIDENCE STATEMENT (read this first)

I'm rating every finding by confidence level so you know what to act on vs what to investigate.

| Rating | What it means |
|--------|--------------|
| 🟢 HIGH | Verified by file inspection, exact measurements, or published research. Act on it. |
| 🟡 MEDIUM | Logically sound but not empirically verified in this system. Worth investigating. |
| 🔴 LOW | Based on general AI model behavior patterns — may not apply to your specific usage. Treat as hypothesis. |

**Overall confidence in this review: HIGH on token economics, MEDIUM on behavioral predictions, LOW on edge cases.**

The biggest gap: I cannot observe actual model behavior during builds. Everything about how the model follows (or doesn't follow) gates, compression rules, and discipline tiers is inferred from prompt structure, not from execution traces. A real eval suite would close this gap.

---

## EXECUTIVE SUMMARY

Fix 19 solved the problems it targeted — verified. GATE 4 is now at line 9 of `team-orchestrator-sprint.md` (was line 417 of a 1,264-line file). Security Discipline is now the first `##` section of `team-orchestrator-rules.md` (was at line 1,085). These are genuine improvements to attention distribution.

**However, Fix 19 introduced a functional regression:** the adapter system prompts (`claude-system-prompt.md`, `chatgpt-system-prompt.md`) still reference `team-orchestrator.md` as the Knowledge file to upload. Users following those instructions will upload the 17-line redirect stub and get nothing. This breaks the Claude Projects and ChatGPT adapter paths for anyone who set them up after Fix 19 — or anyone who re-reads the setup guide.

**New critical finding (🟢 HIGH confidence):** The adapter files have 10+ stale references to `team-orchestrator.md`. This is a functional regression that needs fixing before Fix 19 can be considered complete.

---

## 1. TOKEN ECONOMICS — POST FIX 19 (MEASURED)

### 1A. Always-Loaded Budget (Every Session, Every Mode)

🟢 HIGH confidence — exact byte counts measured.

| File | Lines | Tokens | Status |
|------|-------|--------|--------|
| orchestrator-routing.md | 365 | ~4,724 | ✅ Correct — always needed |
| context-memory-discipline.md | 131 | ~1,176 | ✅ Correct — always needed |
| shared/SKILL.md | 41 | ~783 | ⚠️ Created with `inclusion: always` — see §1C |
| **Total always-on** | **537** | **~6,683** | **✅ Lean and correct** |

This is genuinely good. ~6,683 tokens is a tight always-on budget. The big wins happened in Fix 12 (hook thinning) and Fix 19 (discovery-engine.md made manual).

### 1B. Mode 1 Session Start Cost (Measured)

| File | Tokens | Load trigger |
|------|--------|-------------|
| Hook prompt | ~1,403 | Every session |
| orchestrator-routing.md (always) | ~4,724 | Every session |
| context-memory-discipline.md (always) | ~1,176 | Every session |
| shared/SKILL.md (always) | ~783 | Every session |
| team-orchestrator-core.md | ~5,234 | Mode 1/4/5 start |
| team-orchestrator-rules.md | ~6,751 | Mode 1/4/5 start |
| skill-selection-matrix.md | ~5,150 | Mode 1/4/5 start |
| **Subtotal before first story** | **~25,221** | |
| loop-engine.md (at DEVELOP) | ~3,467 | DEVELOP phase |
| team-orchestrator-sprint.md (at sprint end) | ~3,184 | Sprint end |
| **Full Mode 1 build total (all loaded)** | **~31,872** | |

On Claude Sonnet (200K window): **~16% of context used before first line of code.** Workable.  
On GPT-4o (128K window): **~25% of context at full load.** Tight for long sprints — Mode 5 recommended.

**Comparison to pre-Fix-19:**
- Mode 3 sessions: saved ~2,319 tokens (discovery no longer always-loads) 🟢
- Mode 1 full build: similar total (~31,872 vs ~32,796 before) — marginal improvement
- The real win is *attention distribution*, not token count

### 1C. shared/SKILL.md Always-Load — Minor Issue

🟢 HIGH confidence this is suboptimal; LOW confidence it causes real problems.

I created `kiro/skills/shared/SKILL.md` with `inclusion: always` in its frontmatter. At 783 tokens it's cheap, but semantically it only matters when shared skill files are being selected. For Mode 3 fix/question sessions, it loads and serves no purpose.

**Recommendation:** Change to `inclusion: manual`. Add a note to hook Step 5 (ROLE TRIGGER TABLE): "If any role has shared/ skills in its matrix row, `kiro/skills/shared/SKILL.md` is your path resolution guide."

---

## 2. CRITICAL: ADAPTER FUNCTIONAL REGRESSION (Fix 19 Incomplete)

🟢 HIGH confidence — verified by grep. This is the most urgent finding.

Fix 19 updated `claude-setup-guide.md` and `chatgpt-setup-guide.md` partially, but **the actual system prompt files used in Claude Projects and ChatGPT Custom GPTs were not updated:**

**Stale references confirmed in:**

| File | Stale Reference | Impact |
|------|----------------|--------|
| `claude-system-prompt.md` line 3 | `# Also upload: team-orchestrator.md` | User uploads 17-line stub — no constitution |
| `claude-system-prompt.md` line 36 | `Mode 1/4/5 → read team-orchestrator.md` | Model tries to read a stub |
| `claude-system-prompt.md` line 56 | `Load team-orchestrator.md. Run full chain.` | Same |
| `chatgpt-system-prompt.md` line 6 | `# team-orchestrator.md, skill-selection-matrix.md` | Same |
| `chatgpt-system-prompt.md` line 37 | `read team-orchestrator.md + skill-selection-matrix.md` | Same |
| `chatgpt-system-prompt.md` line 52 | `Load team-orchestrator.md.` | Same |
| `chatgpt-system-prompt.md` line 253 | `kiro/steering/team-orchestrator.md` | Knowledge file list stale |
| `chatgpt-setup-guide.md` line 204 | Quick reference table | Wrong filename |
| `claude-setup-guide.md` line 160 | Quick reference table | Wrong filename |
| Hook JSON `description` field | `delegates ALL role execution to team-orchestrator.md` | Metadata only — not runtime |

**Fix required:** In all adapter system prompts, replace `team-orchestrator.md` with:
- `team-orchestrator-core.md` (for session start / Mode 1 loads)
- `team-orchestrator-sprint.md` (upload alongside for sprint gate coverage)
- `team-orchestrator-rules.md` (upload alongside for security + branch rules)

This is Fix 19B incomplete — needs a 19C pass.

---

## 3. SPLIT FILE QUALITY ASSESSMENT

🟢 HIGH confidence on structure; 🟡 MEDIUM on behavioral effect.

### Verified wins:

**GATE 4 is now at line ~9 of team-orchestrator-sprint.md** ✅  
Was at line 417 in the 1,264-line original — deep in the lost-in-middle zone. Now it's the first major content block. The MEMORY WRITE step (Fix 17H) and SM-RETRO Sprint Discipline Card (Fix 15C) will receive significantly higher attention.

**SECURITY DISCIPLINE is now the first `##` section of team-orchestrator-rules.md** ✅  
Was at line 1,085 of the original — the lowest-attention position possible in the file. Now at line ~9. All three security gates (S1, S2, S3) are in the high-attention leading zone.

### New concern identified:

**team-orchestrator-rules.md is 6,751 tokens — the largest of the three split files.**  
It's heavier than core (5,234) because SECURITY DISCIPLINE + DOCUMENT OWNERSHIP together are dense. This is loaded at session start alongside core. Combined Mode 1 constitution load = 11,985 tokens.

This is acceptable — but watch for a future scenario where rules.md grows. If it exceeds ~8,000 tokens, the later sections (CONFLICT RESOLUTION at the bottom) will start entering the lost-in-middle zone of rules.md itself. The file has a self-similar version of the original problem in embryo.

### 3A. Section Ordering in rules.md — Could Be Better

🟡 MEDIUM confidence this matters.

Current order in rules.md:
1. SECURITY DISCIPLINE ← ✅ correct (highest-priority, now first)
2. *(then:)* rules_without_security — which means NON-NEGOTIABLES, QUALITY BARS, CONFLICT RESOLUTION, SUBAGENT ISOLATION, AGILE ENGINE, SPRINT PARALLELISM, FEATURE BRANCH LIFECYCLE, SESSION CONTINUITY, WORKSPACE LAYOUT, DOCUMENT OWNERSHIP

DOCUMENT OWNERSHIP & PUBLICATION (~150 lines, covers TW trigger points, doc quality bar) is at the bottom of rules.md. This means the section that governs when technical_writer fires and what quality bar to enforce is in the low-attention zone. This is likely less critical than SECURITY but worth noting.

**Recommendation:** In a future pass, move NON-NEGOTIABLES immediately after SECURITY DISCIPLINE. NON-NEGOTIABLES blocks the entire pipeline — it deserves second position.

---

## 4. PROMPT ENGINEERING QUALITY DELTA (v3 → v4)

### What improved since v3:

| Issue from v3 | Status in v4 |
|---|---|
| GATE 4 in low-attention zone | ✅ Fixed — line 9 of sprint file |
| Security Discipline at line 1,085 | ✅ Fixed — first section of rules file |
| discovery-engine.md wasted on Mode 3 | ✅ Fixed — manual-inclusion |
| team-orchestrator.md lost-in-middle risk | ✅ Fixed — split into 3 phase files |

### What remains from v3:

| Issue from v3 | Status in v4 | Priority |
|---|---|---|
| Step 0 keyword list too narrow (missing WRITE, REVIEW, ANALYZE) | ❌ Not fixed | P1 |
| Memory confidence criteria subjective | ❌ Not fixed | P1 |
| Role handoff no structured format | ❌ Not fixed | P2 |
| Domain tags for lessons.md filtering | ❌ Not fixed | P2 |
| Goal Anchor tied to count not 85% threshold | ❌ Not fixed | P2 |
| shared-routing-core.md for adapter sync | ❌ Not fixed | P2 (now more urgent given Fix 19 drift) |
| Model-specific mode recommendations in adapters | ❌ Not fixed | P3 |
| System regression eval suite | ❌ Not fixed | P3 |

---

## 5. SKILL FILE SYSTEM — NEW OBSERVATION

🟡 MEDIUM confidence.

**Role file counts (top 5):**
- website_creator: 24 files
- security_engineer: 21 files
- ml_engineer: 18 files
- database_architect: 17 files
- backend_lead: 14 files

**website_creator at 24 files is worth examining.** Fix 13D split it into 4 subdomains (website_creator, performance, SEO, analytics). If each subdomain has ~6 files, that's 24. The matrix must navigate all 24 to select 3 per activation. This is fine in theory — the matrix lookup is the selection mechanism — but 24 files is a large namespace to reason over in a single matrix lookup.

**A more structural concern:** The matrix has **no validation layer.** If a skill file referenced in the matrix doesn't exist on disk, the model falls back to `SKILL.md` (per Fix 16D fallback rule). Silent fallback is invisible — the model produces output without the specialized skill, and there's no observable failure signal except the log line `[SKILL MISSING: ...]`. In a build session where you're not monitoring logs, you could go multiple sprints with missing skill files without knowing.

🟢 **Recommendation:** Add a session-start verification step to the hook. After skill-selection-matrix.md loads, scan the matrix for all referenced shared/ skill files and confirm they exist. Log any missing ones as `[INIT WARNING: skill file missing — path/to/file.md]` before the first role activates. This makes silent fallbacks visible.

---

## 6. MEMORY SYSTEM — STRUCTURAL GAP FOUND

🟡 MEDIUM confidence on the problem; 🔴 LOW confidence on severity without seeing actual lessons.md content.

The MEMORY WRITE step (Fix 17H) at GATE 4 instructs the model to:
1. Read kiro/memory/lessons.md
2. Append unrecorded patterns with `confidence: low`
3. Upgrade confirmed patterns

**Structural gap:** The MEMORY WRITE reads `kiro/memory/lessons.md` at sprint end. But kiro/memory/lessons.md is also supposed to be loaded at session start (Fix 17F — memory load before first role). If the session is long (50+ exchanges) and lessons.md grew during the session, the version loaded at session start is stale by sprint end.

**Scenario:** Sprint runs 3 stories. At GATE 4, scrum_master writes 2 new lessons to lessons.md. Next sprint starts in the same session. Memory load already happened at session start — the new lessons don't apply until a fresh session. The memory write and memory read are desynchronized within a session.

**Fix:** Add to MEMORY WRITE protocol (team-orchestrator-sprint.md, step 2b): "After writing lessons.md, re-load the 3 most recent entries into active context with a note `[MEMORY REFRESH: N new entries available this session]`." This ensures sprint-over-sprint learning within a session.

---

## 7. HOOK INTEGRITY CHECK

🟢 HIGH confidence — verified.

Hook prompt at 1,403 tokens. Step 4 now correctly references:
- `team-orchestrator-core.md` — loads at session start ✅
- `team-orchestrator-rules.md` — loads at session start ✅
- `team-orchestrator-sprint.md` — loads at sprint end ✅
- `loop-engine.md` — loads at DEVELOP ✅
- `skill-selection-matrix.md` — loads at session start ✅

**One residual issue:** Hook JSON `description` field still says `"delegates ALL role execution to team-orchestrator.md"`. This is metadata only — Kiro displays it in the hook UI but doesn't inject it into the model context. Not runtime-critical, but misleading for anyone reading the hook configuration.

**Hook Step 2 classification table is missing "WRITE/ANALYZE/REVIEW" patterns** that would correctly route Mode 2 requests. This remains from v3 — no change. The FIX class catches "bug fix / debugging / question / conversational" but not "write architecture doc" or "review this PR" — those could fall through to MODE 3 instead of MODE 2.

---

## 8. WHAT THE v4 SYSTEM LOOKS LIKE TO A MODEL

🟡 MEDIUM confidence — this is inferred model behavior, not observed.

When a Mode 1 build starts, here's what the model's effective context looks like:

**Layer 1 — Always present (every session):**
```
[orchestrator-routing.md — ~4,724 tokens] — routing rules, ENV detection, mode table
[context-memory-discipline.md — ~1,176 tokens] — degradation tiers, goal anchor, pruning rules
[shared/SKILL.md — ~783 tokens] — shared skill index
[hook prompt — ~1,403 tokens] — step-by-step session protocol
```

**Layer 2 — Loaded at Mode 1 session start:**
```
[team-orchestrator-core.md — ~5,234 tokens] — constitution part 1
[team-orchestrator-rules.md — ~6,751 tokens] — security gates first, then rules
[skill-selection-matrix.md — ~5,150 tokens] — skill routing table
```

**Layer 3 — Loaded on-demand:**
```
[discovery-engine.md — ~2,319 tokens] — new builds only
[loop-engine.md — ~3,467 tokens] — DEVELOP phase only
[team-orchestrator-sprint.md — ~3,184 tokens] — sprint end only
[3 skill files — ~1,500 tokens] — per role activation
```

Total Layer 1 + 2 = **25,221 tokens** before work starts. The model begins generating with ~25K tokens of instruction context, leaving 174K (Claude) or 102K (GPT-4o) for actual work.

**How the model likely experiences this:** The hook prompt and orchestrator-routing.md (loaded first, in context leading position) will be followed most reliably. team-orchestrator-rules.md security gates (at position ~12K tokens into context) will be followed reliably because they're near the beginning of their file and the model was told to load them specifically. team-orchestrator-core.md content in the middle-to-late sections (Phase Overview, JIRA lifecycle, sprint plan templates) is at ~18-20K tokens into context — moderate attention zone. Fine for templates; risky for complex logic.

---

## 9. UPDATED PRIORITY STACK

### P0 — Must Fix Before Adapters Work (Fix 19C)

**Fix stale `team-orchestrator.md` references in adapter system prompts.**  
Files: `claude-system-prompt.md`, `chatgpt-system-prompt.md`, and remaining references in setup guides.  
Impact: Without this, anyone using Claude Projects or ChatGPT Custom GPT will load a 17-line stub instead of the constitution. Mode 1 builds via adapters are broken.

### P1 — High Value

**P1-A: Add session-start skill file verification to hook**  
Check shared/ skill paths referenced in matrix actually exist. Log `[INIT WARNING]` for missing files.  
🟢 HIGH confidence this is worth doing.

**P1-B: Step 0 keyword expansion**  
Add WRITE, REVIEW, ANALYZE, AUDIT, RUN to the trigger keyword list (or tighten to ≤5 words).  
🟢 HIGH confidence this fixes real false positives.

**P1-C: Memory resync within session**  
After MEMORY WRITE at GATE 4, re-load the 3 newest entries to close the desynchronization gap.  
🟡 MEDIUM confidence this matters in practice.

### P2 — Medium Value

**P2-A: Measurable memory confidence criteria** (v3 carry-over)  
Low = 1 sprint, Medium = 2+ sprints, High = 5+ sprints. Objective, not impressionistic.

**P2-B: shared/SKILL.md inclusion: always → manual**  
Saves 783 tokens on Mode 3 sessions. Minor but correct.

**P2-C: Move NON-NEGOTIABLES to second position in team-orchestrator-rules.md**  
Currently NON-NEGOTIABLES is ~50th percentile of the file. Should be immediately after SECURITY DISCIPLINE.

**P2-D: shared-routing-core.md bridge file for adapter sync**  
Single source for routing rules that both adapter system prompts include. Prevents the Fix 19 drift problem from recurring.

### P3 — Long Term

**P3-A: System regression eval suite** (10 canonical scenarios)  
**P3-B: Model-specific mode recommendations in adapters**  
**P3-C: Role handoff structured format template**

---

## 10. CONFIDENCE SCORECARD BY DOMAIN

| Domain | My confidence | Why |
|--------|--------------|-----|
| Token counts / file sizes | 🟢 HIGH | Direct measurement |
| Stale adapter references | 🟢 HIGH | Verified by grep |
| Split file attention improvement | 🟢 HIGH | Well-established research (lost-in-middle), structure verified |
| discovery-engine.md fix | 🟢 HIGH | Confirmed in frontmatter |
| Memory resync gap | 🟡 MEDIUM | Logical analysis — depends on session patterns I can't observe |
| Step 0 false positive rate | 🟡 MEDIUM | Based on common request patterns — depends on your actual usage |
| Skill file matrix navigation at 24 files | 🟡 MEDIUM | No benchmark data on this specific count |
| Model gate compliance rates | 🔴 LOW | Cannot observe actual execution without eval runs |
| Attention decay exact percentages (40-60%) | 🔴 LOW | Research averages — varies by model and prompt structure |
| Whether rules.md bottom sections are ignored | 🔴 LOW | Hypothesis based on position — not verified |

---

## 11. SYSTEM HEALTH DELTA v3 → v4

| Dimension | v3 Rating | v4 Rating | Change |
|-----------|-----------|-----------|--------|
| Always-on token budget | B | A | +1 (discovery-engine fixed) |
| Lost-in-middle risk | D | B+ | +3 (split solved GATE 4 + Security position) |
| Adapter correctness | A | C | -2 (Fix 19 introduced stale refs) |
| Hook integrity | B | B+ | +0.5 (Step 4 updated, description stale) |
| Memory system | B | B | → (no change; resync gap newly identified) |
| Skill routing | B | B | → (no change this cycle) |
| Prompt engineering | B+ | B+ | → (Step 0 still needs tuning) |

**Net: The split was worth it. The adapter regression needs immediate attention.**

---

## FINAL VERDICT

The system architecture post-Fix-19 is the best it's been. The token budget is lean, the most critical instructions (GATE 4, Security Discipline) are now in high-attention positions, and the always-on load is just ~6,683 tokens.

The one thing that needs fixing before anything else is the adapter system prompts — they still tell users to upload `team-orchestrator.md`, which is now a stub. That's a silent failure mode that will confuse users who set up Claude Projects or ChatGPT adapters.

After that: Fix 19C (adapter references), then P1-B (Step 0 keywords), then P2-A (memory confidence criteria). Everything else is polish.

---

*Review produced: 2026-06-30 | Measurements: live file byte counts | Research basis: Liu et al. 2023 (lost-in-middle), documented instruction-following degradation curves | Confidence: High on structure, Medium on behavior, Low on edge cases*
