# Architecture Decision Records — Loop Engineering System

Temporal decision log. Every significant architectural or system decision is recorded here with validity windows.

**Rules:**
- When a decision is superseded: update `valid_to` on the old row, add a new row — never delete
- Query "current decisions" → filter rows where `valid_to = present`
- Query "decision in [month]" → filter rows where `valid_from ≤ date ≤ valid_to`

| ADR | Title | Date | Status | valid_from | valid_to | Decision |
|-----|-------|------|--------|-----------|---------|---------|
| ADR-001 | Hook architecture — constitution in hook | 2026-01-01 | Superseded | 2026-01-01 | 2026-06-30 | elite-team-orchestrator.kiro.hook contained the full team constitution (~900 lines). All role definitions, artifact chains, and gates lived inside the hook prompt. |
| ADR-002 | Hook architecture — thin router | 2026-06-30 | Accepted | 2026-06-30 | present | Hook is a ≤60-line router. Constitution lives in team-orchestrator.md. Hook detects mode, loads steering files, delegates all execution. Eliminates 900-line per-prompt token cost. |
| ADR-003 | CLAUDE.md — monolithic always-loaded | 2026-01-01 | Superseded | 2026-01-01 | 2026-06-30 | Single CLAUDE.md file (~1,668 lines) was always-loaded, accumulating all fix iterations as patch history. |
| ADR-004 | CLAUDE.md — split into implemented/ongoing | 2026-06-30 | Accepted | 2026-06-30 | present | CLAUDE.md (≤700 lines, ongoing fixes + operating rules, always-loaded) + CLAUDE-implemented.md (Fixes 1–11 history, manual-inclusion only). |
| ADR-005 | $TRACKER — Jira-only mapping | 2026-01-01 | Superseded | 2026-01-01 | 2026-06-30 | $TRACKER translation table mapped only to Jira or markdown fallback. Linear/GitHub/Asana modes would silently fail. |
| ADR-006 | $TRACKER — full multi-tracker mapping | 2026-06-30 | Accepted | 2026-06-30 | present | Translation table expanded with columns for jira/linear/github/asana/markdown. Every $TRACKER verb maps to the correct native API for all supported TRACKER_MODEs. |
| ADR-007 | Skill file creation — batch without evals | 2026-01-01 | Superseded | 2026-01-01 | 2026-06-30 | 261 skill files created in batch sessions without adversarial testing or before/after eval evidence. |
| ADR-008 | Skill file modification — eval-gated | 2026-06-30 | Accepted | 2026-06-30 | present | All skill file modifications require ≥3 adversarial sessions before + ≥3 after, with documented delta. No intuition-based edits. |
| ADR-009 | Shared skill path convention | 2026-06-30 | Accepted | 2026-06-30 | present | Shared skills in skill-selection-matrix.md use prefix `shared/<filename>`. Resolve as `kiro/skills/shared/<filename>`. Fallback: `kiro/skills/shared/SKILL.md` index. Added Fix 16D. |
| ADR-010 | Platform adapters — model-agnostic | 2026-06-30 | Accepted | 2026-06-30 | present | Kiro methodology is model-agnostic. Steering .md files load on any platform. `.kiro.hook` is Kiro-specific. Adapters live in `kiro/adapters/` — zero changes to existing steering files. Created Fix 17 adapter work. |
| ADR-011 | Memory lifecycle — load + write-back | 2026-06-30 | Accepted | 2026-06-30 | present | Memory loads at session start (Step 4 of hook — before first role activates). Memory writes at GATE 4 (step 2b — before SM-RETRO). HIGH-confidence lessons apply immediately. ADRs are binding constraints. Added Fixes 17F + 17H. |
| ADR-012 | Skill file context discipline | 2026-06-30 | Accepted | 2026-06-30 | present | After extracting principles from a skill file: compress to 5-line takeaway, discard full file content. Pattern: Extract → Produce artifact → Discard. Full file in context after artifact = context rot. Added Fix 17C. |
