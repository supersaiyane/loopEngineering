---
title: Session Guards
inclusion: always
---

# Session Guards (Fix 41A)

Two guards that run at the start of EVERY session and on EVERY prompt.
Extracted from the hook to keep the hook thin (hook = router, not constitution).

---

## GUARD 1 — CONSTRAINT DRIFT GUARD (Fix 40C)

**When:** Any session where `checkpoint.md` shows Phase ≥ 2 OR `sprint_plan.md` exists.
**Why:** "Don't do X" constraints disappear at turn 47 via lossy summarization. Agents forget
constraints that were clear at session start. This guard re-loads them every session.

**Protocol:**
At the start of any non-trivial session, before any work begins, reread:
1. `/docs/foundation/project-index.md` Section 3 (binding decisions + constraints)
2. `kiro/steering/team-orchestrator-rules.md` NON-NEGOTIABLES list

Any constraint marked "binding" in project-index.md → **ACTIVE for this entire session.**

If a later instruction conflicts with a binding constraint:
- Flag the conflict explicitly: `"⚠️ CONSTRAINT CONFLICT: [constraint] vs [new request]"`
- Do NOT silently override the binding constraint to satisfy the new request
- Surface to user: ask which takes precedence

`Log: [CONSTRAINT-LOAD: N binding decisions active | N non-negotiables active]`

If `project-index.md` does not exist yet → skip silently (new project, no constraints yet).

---

## GUARD 2 — BAD LOOP DOMAINS (Fix 40E + 41C)

**When:** On any prompt that contains BOTH a domain keyword AND a high-risk verb (see below).
**Why:** Some domains require human judgment before an agent proceeds. An agent that
self-declares done in these domains — without user approval — is a NON-NEGOTIABLE violation.

**Trigger condition:**

Standard: BOTH a domain keyword AND a high-risk verb must be present.
Self-triggering exception: `deploy / release / production` domain keywords fire the gate alone — no verb required (the deploy IS the high-risk action).

| Domain keywords | High-risk verbs |
|----------------|-----------------|
| auth / authentication / session | redesign / rewrite / replace |
| payments / billing / subscription | restructure / migrate / overhaul |
| rbac / permissions / access control | remove / delete / deprecate |
| deploy / release / production | ⚡ SELF-TRIGGERING — gate fires on domain alone |
| database migration / schema change | refactor (scope > 1 file) |
| security policy / secrets / credentials | rebuild / rearchitect |
| — | deploy / release / rollout / promote / ship |

**Docs updates, read-only analysis, test additions, comments → NOT triggered.**
- "update the auth docs" → NOT triggered (no high-risk verb)
- "add a test for billing" → NOT triggered (no high-risk verb)
- "redesign the auth flow" → triggered (auth + redesign) ✅
- "deploy to prod NOW" → triggered (deploy = self-triggering domain) ✅ (Fix 42C)

**Protocol when triggered:**
```
⚠️ BAD LOOP DOMAIN: This request touches [domain] with a [verb] scope.
Human gate required before proceeding. Please confirm:
  1. What specifically should change?
  2. What must NOT change?
  3. Who approved this work?
I will proceed once you confirm all three.
```

`Log: [BAD-LOOP-GATE: domain=[auth] verb=[redesign] → human approval required]`

An agent that proceeds in these domains without explicit user approval = NON-NEGOTIABLE #10 violation.

---

## GUARD 3 — PXPIPE IMAGE CONTEXT GUARD (Fix 44G)

**When:** pxpipe proxy is active (`ANTHROPIC_BASE_URL=http://127.0.0.1:47821`).
**Why:** Old history turns are stored as PNG images, not text. The model reads them at
gist-level accuracy (decisions, values, paths, names = 98/98 lossless) but NOT at
byte-exact level. Silent misreads — plausible wrong values, no error signal — occur on
exact strings at ~13% rate on Fable 5, ~100% on Opus 4.8.

**NEVER recall from imaged context (re-fetch from source instead):**
- Git commit SHAs / hashes → run `git log` or `git show` fresh
- File:line references → re-check `project_map.md` or grep
- Exact error codes, IDs, ticket numbers → re-read the relevant file or tool result
- camelCase function/variable names → re-read the source file
- API keys, secrets, credentials → never in images (verbatim-risk guard)
- Checkpoint timestamps / gate_fired_at values → re-read `kiro/memory/checkpoint.md`

**What IS safe to use from imaged context:**
- Decisions made ("we chose Postgres over MySQL")
- File names and directory paths (not line numbers)
- Architecture intent ("auth service handles session tokens")
- Status summaries ("Sprint 3 complete, fix 44B merged")
- Counts and relative values ("3 files changed", "~15% improvement")

**Protocol:**
Any agent that needs an exact string from session history older than the live text
tail MUST re-fetch it from the canonical source before using it. This is the
re-read-before-edit protocol already in debugging_methodology.md — now with an
explicit reason: the old context may be an image, not text.

`Log: [GUARD-3: exact-string needed → re-fetching from source, not image memory]`
