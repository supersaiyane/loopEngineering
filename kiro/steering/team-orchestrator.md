---
inclusion: manual
---

# team-orchestrator.md — SPLIT (Fix 19)

This file has been split into 3 phase-specific files for context efficiency.
Do NOT load this file directly. Load the appropriate file per phase:

| File | Load When | Contains |
|------|-----------|----------|
| `team-orchestrator-core.md` | Mode 1/4/5 session start | Roles, SM modes, artifact chain, GATE 1, GATE 2, GATE 3, JIRA lifecycle, impl-decisions |
| `team-orchestrator-rules.md` | Mode 1/4/5 session start (with core) | SECURITY DISCIPLINE (first), NON-NEGOTIABLES, QUALITY BARS, CONFLICT RESOLUTION, SUBAGENT ISOLATION, AGILE ENGINE, BRANCH LIFECYCLE, WORKSPACE LAYOUT, DOCUMENT OWNERSHIP |
| `team-orchestrator-sprint.md` | Sprint end (GATE 4 trigger) | GATE 4 (memory write + SM-RETRO), GATE 5 (phase-end reports), MODE 1 SELF-CHECK, PHASE PARALLELISM RULES |

The hook (Step 4) and orchestrator-routing.md (MANDATORY LOADS) reference the correct files.
See also: kiro/adapters/ for Claude Projects and ChatGPT setup.
