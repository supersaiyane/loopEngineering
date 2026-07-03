# Lessons — Loop Engineering System

Cross-session learning log. Written at session end when the LLM was corrected, a pattern was identified, or a rule emerged from practice.

---

## THE 5-STAGE MEMORY PROGRESSION (Fix 40A)

Every lesson MUST complete all 5 stages before it can be marked `confidence: high`.
Stages 1–2 are notes. Stage 3 is fact. Stage 4 is rule. Stage 5 is habit.

```
Stage 1 — FAIL      Document the failure with enough detail to reproduce it.
Stage 2 — INVESTIGATE  Root cause. Not "what went wrong" but WHY it went wrong.
Stage 3 — VERIFY    Turn the diagnosis into a checked fact, not a guess.
                    Evidence: a test, a session run, a counter-example tried and failed.
Stage 4 — DISTILL   Write the general rule that applies BEYOND this specific case.
                    If it only applies to one file → it's a note, not a lesson.
Stage 5 — CONSULT   On the next task, READ this entry before starting. Don't re-derive.
```

**Sections in this file map to stages:**

| Section | Stage | What goes here |
|---------|-------|----------------|
| `## Open Failures` | 1–2 | Documented failures under active investigation |
| `## Verified Facts` | 3 | Things we stopped guessing about — checked against evidence |
| `## General Rules` | 4 | Distilled rules that apply across sessions / projects |
| `## Lessons (dated entries below)` | 4–5 | Full format entries for audit trail |

**Compounding contract (Fix 40A):**
- When a lesson reaches `confidence: high` → promote it to a Skill file AND to CLAUDE.md NON-NEGOTIABLES.
- `docs/lessons.md` is project-scoped. Skills in `kiro/skills/` travel across projects.
- Do NOT leave lessons only in checkpoint.md — that file is session-scoped and does not compound.

---

## Open Failures
*(Stage 1–2 — under investigation. Move to Verified Facts once root cause is confirmed.)*

*(none currently)*

---

## Verified Facts
*(Stage 3 — checked against evidence. Not guesses.)*

*(none currently)*

---

## General Rules
*(Stage 4 — distilled, cross-project rules. If a lesson only applies to one file, it belongs in dated entries, not here.)*

- **Always-loaded context >400 lines causes token waste on every prompt.** Keep CLAUDE.md to pending fixes + operating rules only. History goes in CLAUDE-implemented.md.
- **Hook is a thin router, not the constitution.** Hook ≤60 lines. Constitution stays in steering files. Hook detects mode; it never replicates content.
- **Skill files written in batch without adversarial testing degrade silently.** Run ≥3 adversarial sessions before AND after modification. Only apply if delta is positive.

---

## Lessons (full entries — audit trail)

**Format:**
```
## [YYYY-MM-DD] — [pattern title]
**Type:** Mistake | Correction | Rule | Anti-pattern
**Stage:** 1-Fail | 2-Investigate | 3-Verify | 4-Distill | 5-Consult
**Confidence:** low | medium | high
**Trigger:** [situation that activates this lesson]
**Body:** [what happened and what to do instead]
**Review:** [date of last confirmation / upgrade]
**gate_fired_at:** Sprint N   ← REQUIRED for Stage 1-Fail entries (Fix 43A)
```

> **Fix 43A — gate_fired_at rule:** Stage 1-Fail entries MUST record `gate_fired_at: Sprint N`
> at the moment the gate fired — not at retro write time. The LESSON AGE CHECK uses
> `gate_fired_at` to compute staleness. If retro runs late, the clock is still accurate.
> Missing `gate_fired_at` on a Stage 1-Fail entry = treated as Sprint 0 (worst-case age).

Confidence lifecycle:
- `low` → new entry, stage 1–2 only
- `medium` → stage 3 verified, confirmed in 3+ sessions without exception
- `high` → stage 4 distilled, promoted to Skill file + CLAUDE.md NON-NEGOTIABLES

---

---

## 2026-06-30 — Skill files written in batch without adversarial testing degrade silently

**Type:** Anti-pattern
**Stage:** 4-Distill
**Confidence:** medium
**Trigger:** Any session where a skill file is modified or a new batch of skill files is created
**Body:** 261 skill files were created across multiple sessions without running adversarial test cases. The result is that skill files may look correct but fail on hard, ambiguous tasks. Before modifying any skill file, run ≥3 adversarial sessions against the current version, document what breaks, then run ≥3 against the modified version and document the delta. Only apply the change if delta is positive.
**Review:** 2026-06-30 — initial entry

---

## 2026-06-30 — Always-loaded context that is 1600+ lines causes token waste on every prompt

**Type:** Correction
**Stage:** 5-Consult
**Confidence:** high
**Trigger:** Any session where CLAUDE.md grows beyond ~400 lines
**Body:** CLAUDE.md accumulated 11 fix iterations (1,668 lines) all marked always-loaded. 90% of the content was applied-fix history with no operational value in active sessions. Fix: split into CLAUDE.md (ongoing, ≤700 lines) + CLAUDE-implemented.md (history, manual-inclusion). Keep always-loaded content to operating rules + pending fixes only.
**Review:** 2026-06-30 — confirmed by implementing the split

---

## 2026-06-30 — Hook that IS the constitution fires 900-line prompt on every promptSubmit

**Type:** Anti-pattern
**Stage:** 5-Consult
**Confidence:** high
**Trigger:** Any time a Kiro hook grows beyond ~100 lines
**Body:** elite-team-orchestrator.kiro.hook absorbed team-orchestrator.md's full constitution (900 lines) and fired on every prompt including Mode 3 bug fixes and casual questions. Even with HOOK COMPLEXITY GATE, the model must parse 900 lines before returning. Fix: hook = thin router (≤60 lines). Constitution stays in team-orchestrator.md. Hook detects mode and loads steering files; it never replicates their content.
**Review:** 2026-06-30 — confirmed by implementing Fix 12C
