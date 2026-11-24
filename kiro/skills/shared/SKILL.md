---
inclusion: manual
---

# Shared Skills — Index

Skills in `kiro/skills/shared/` are cross-role utilities used by multiple roles.
They are NOT role-specific — any role may load them when the activity matches.

## PATH CONVENTION

In `skill-selection-matrix.md`, shared skills are listed as `shared/<filename>`.
Resolve as: `kiro/skills/shared/<filename>`
Example: `shared/design_system_gate.md` → `kiro/skills/shared/design_system_gate.md`

If a shared skill file is missing: log `[SKILL MISSING: kiro/skills/shared/<filename>]`, fall back to this SKILL.md for context, add to sprint backlog.

---

## SHARED SKILL FILES

| File | Purpose | Primary Users |
|------|---------|---------------|
| `design_system_gate.md` | PREREQUISITE gate — `/docs/design_system.md` must exist before any UI component is written. Blocks all UI stories until design system is established. | website_creator, senior_engineer_fe, mobile_engineer, frontend_lead |
| `api_versioning_strategy.md` | API versioning patterns (path, header, query param), deprecation policy, breaking vs non-breaking change classification. | senior_engineer_be, architect, backend_lead |
| `code_review_checklist.md` | Universal code review checklist covering security, performance, readability, test coverage, and architectural alignment. | All roles doing code review |
| `debugging_systematic.md` | Structured debugging methodology: reproduce → isolate → hypothesis → verify → fix. Covers logging, binary search, time-travel debugging. | All engineering roles |
| `error_handling_strategies.md` | Error classification (transient / permanent / partial), retry patterns, fallback design, error boundary placement. | senior_engineer_be, senior_engineer_fe, architect |
| `performance_profiling.md` | Profiling approach: establish baseline → measure → identify hotspot → fix → verify. Covers CPU, memory, I/O, rendering bottlenecks. | senior_engineer_be, senior_engineer_fe, devops_engineer |
| `security_baseline.md` | Universal security baseline: input validation, output encoding, auth checks, secrets handling, dependency hygiene. Applies to all code-producing roles. | All roles writing code |
| `testing_pyramid.md` | Test pyramid ratios (unit 70% / integration 20% / e2e 10%), test naming conventions, coverage targets per mode, test data management principles. | All roles writing tests |
| `test_driven_development.md` | TDD red-green-refactor cycle, when to apply (new features, bug fixes), when to skip (spikes, prototypes), test-first discipline patterns. | senior_engineer_be, senior_engineer_fe, qa_engineer |

---

## USAGE RULES

1. **Load on match only** — do not preload. Load the shared skill only when the current activity matches.
2. **Prerequisite skills block** — `design_system_gate.md` must resolve GREEN before any UI story proceeds.
3. **Compress after use** — after extracting principles, compress to 5-line takeaway. Do not hold the full file in context while producing the artifact.
4. **Fallback** — if a specific shared skill file is missing, this SKILL.md provides the directory overview as context fallback.

## Additional activity

- [agent_handoff_evidence.md](agent_handoff_evidence.md) — task-specific guidance; see the specialist catalog for when to load it.

## Additional activity

- [agent_run_recovery.md](agent_run_recovery.md) — task-specific guidance; see the specialist catalog for when to load it.
