<!-- LOAD-TYPE: CHECKLIST -->
---
id: project_index_template
version: 1.0.0
owners: [technical_writer]
tags: [foundation, index, gates, planning]
when_to_use: >
  When creating /docs/foundation/project-index.md. Created at GATE 1 kickoff.
  Hook reads this file BEFORE checkpoint.md on every session start.
  Open Questions blocking the current gate prevent SM-PLAN from running.
  technical_writer owns creation and maintenance. Updated at each gate transition.
---

# Project Index Template — Foundation Doc Registry & Gate Tracker

FULL-LOAD REQUIRED — the hook reads this on session start to determine project state.
Output file: `/docs/foundation/project-index.md`
Owner: `technical_writer` (create + maintain) — updated at every gate transition.

Hook session-start read order: project-index.md FIRST → checkpoint.md SECOND.
If open questions block current gate → emit blocker before resuming any work.

---

## PROJECT INDEX STRUCTURE CHECKLIST

- [ ] Section 1: Foundation Docs Status table
- [ ] Section 2: Current Gate + Status
- [ ] Section 3: Open Questions (unresolved decisions)
- [ ] Section 4: Doc Conflict Log
- [ ] Section 5: Project Identity

---

## SECTION 1 — Foundation Docs Status

Update this table at every gate transition and whenever a doc is created/completed.

```
| Doc | Output Path | Status | Gate Required | Owner | Last Updated |
|-----|-------------|--------|---------------|-------|--------------|
| PRD | /docs/foundation/prd.md | ✅ Complete | GATE 1 | cto | YYYY-MM-DD |
| TRD / Architecture | /docs/foundation/architecture.md | 🟡 In Progress | GATE 2 | architect | YYYY-MM-DD |
| App Flow | /docs/foundation/app-flow.md | 🔴 Missing | GATE 2 | technical_writer | — |
| Design System | /docs/design_system.md | 🔴 Missing | GATE 2 | frontend_lead | — |
| Backend Schema | /docs/phase-N/db-architecture.md | 🔴 Missing | GATE 2 | database_architect | — |
| Security Posture | /docs/foundation/security-posture.md | 🔴 Missing | GATE 2 | security_engineer | — |
| Testing Strategy | /docs/foundation/testing-strategy.md | 🔴 Missing | GATE 2 | qa_engineer | — |
| Impl Plan / Roadmap | /docs/foundation/roadmap.md | 🔴 Missing | SM-PLAN | scrum_master | — |
```

Status values: ✅ Complete | 🟡 In Progress | 🔴 Missing | ⚠️ Outdated (content stale — needs update)

---

## SECTION 2 — Current Gate + Status

```
CURRENT_GATE:     1 | 2 | 3 (DEVELOP) | 4 (SM-RETRO) | 5 (RELEASE)

GATE_STATUS:      🔴 BLOCKED | 🟡 IN PROGRESS | ✅ CLEARED

BLOCKER_SUMMARY:
  - [specific blocker — which doc missing or which open question unresolved]
  - [blocker 2]

GATE_HISTORY:
  GATE 1: [date cleared or "not yet cleared"]
  GATE 2: [date cleared or "not yet cleared"]
  GATE 3: [sprint N started on date]
  GATE 4: [SM-RETRO date]
  GATE 5: [release date or "not yet"]
```

---

## SECTION 3 — Open Questions

**Each open question that blocks a gate prevents SM-PLAN from proceeding.**
Hook session start: if open questions exist for CURRENT_GATE → emit blocker message before resuming.

```
| ID | Question | Blocks | Owner | Status | Due | Resolution |
|----|----------|--------|-------|--------|-----|------------|
| OQ-1 | SAML SSO required or OAuth-only? | GATE 2 (TRD trust boundary, auth CHECKLIST selection) | architect + cto | 🔴 Unresolved | YYYY-MM-DD | — |
| OQ-2 | Self-hosted or cloud deployment? | GATE 2 (infra architecture, hosting costs) | architect | 🔴 Unresolved | YYYY-MM-DD | — |
| OQ-3 | GDPR scope: EU users only or all? | GATE 2 (schema GDPR classification) | cto | 🔴 Unresolved | YYYY-MM-DD | — |
| OQ-4 | Mobile v1 or web-only? | PRD Label Map (mobile/* labels) | cto | ✅ Resolved | YYYY-MM-DD | Web-only for v1 — mobile in v2 |
```

**Hook log on session start (if unresolved questions for current gate):**
```
[PROJECT-INDEX: gate=2 | BLOCKED | Open questions: OQ-1 (SAML/OAuth?), OQ-2 (hosting?), OQ-3 (GDPR scope?) — resolve before SM-PLAN can run]
```

**When a question is resolved:**
1. Update Status → ✅ Resolved
2. Fill Resolution column with the decision
3. Update the affected doc (TRD, PRD, security-posture, etc.)
4. Update CURRENT_GATE status if this was the last blocker

---

## SECTION 4 — Doc Conflict Log

When two foundation docs contradict each other, log here and block SM-PLAN until resolved.

**Conflict resolution precedence (Fix 32G):**
- WHAT to build → **PRD wins**
- HOW to build it → **TRD wins**
- Data shape / schema → **Backend Schema wins**
- UI behavior / states → **App Flow wins**
- Security decisions → **security-posture.md wins**

```
| ID | Conflict | Doc A says | Doc B says | Winner | Resolved | Resolution |
|----|----------|-----------|-----------|--------|----------|------------|
| DC-1 | Auth mechanism | PRD: "OAuth login" | TRD: "SAML for enterprise" | security-posture.md wins | 🔴 No | — |
| DC-2 | (example resolved) | PRD: "v1 has mobile" | App Flow: "web-only" | PRD wins → App Flow updated | ✅ Yes | App Flow updated to include mobile screens |
```

**SM-PLAN cannot run with unresolved doc conflicts.**
Log format: `[DOC-CONFLICT: PRD says X | TRD says Y | Winner: security-posture.md | Status: unresolved — blocks SM-PLAN]`

---

## SECTION 5 — Project Identity

Quick reference — loaded by hook on session start for context.

```
APP_NAME:         [name]
ONE_LINER:        [one sentence from PRD]
CURRENT_SPRINT:   Sprint N (or "pre-sprint — in DESIGN phase")
TECH_STACK:       [e.g., Next.js + Fastify + PostgreSQL + AWS]
POSTURE_LEVEL:    LOW | MEDIUM | HIGH (from security-posture.md)
COMPLIANCE:       [e.g., GDPR + SOC2 | none]
TRACKER:          [Jira project key | Linear workspace | GitHub Projects]
REPO:             [GitHub/GitLab URL]
LAST_UPDATED:     YYYY-MM-DD
```

---

## MAINTENANCE RULES

- Update Section 1 whenever any foundation doc status changes.
- Update Section 2 whenever a gate clears or a blocker is added/resolved.
- Update Section 3 when a new decision is needed OR a decision is made.
- Update Section 4 when docs conflict (add row) or conflict is resolved (update row).
- technical_writer is responsible for keeping this file current — it is the single source of project state.

**Log on session start:**
```
[PROJECT-INDEX: app=<name> | gate=<N> | status=<BLOCKED/IN-PROGRESS/CLEARED> | open-questions=<K> | doc-conflicts=<M> | docs-complete=<X/8>]
```
