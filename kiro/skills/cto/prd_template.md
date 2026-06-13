<!-- LOAD-TYPE: CHECKLIST -->
---
id: prd_template
version: 1.0.0
owners: [cto, market_researcher]
tags: [foundation, prd, product, planning]
when_to_use: >
  When creating or reviewing /docs/foundation/prd.md. Mandatory at GATE 1.
  SM-PLAN reads the Label Map section (Section 6) before any story creation.
  GATE 1 stays RED until all 8 sections are present and non-empty.
---

# PRD Template — Product Requirements Document

FULL-LOAD REQUIRED — this is a creation checklist and structural template.
Output file: `/docs/foundation/prd.md`
Owner: `cto` (drafts) + `market_researcher` (validates user/market claims)

---

## QUICK REFERENCE

- Write PRD BEFORE architecture. Architecture answers "how" — PRD answers "what and why."
- Every user story MUST be in GIVEN/WHEN/THEN format (not "As a user I can…").
- Success metrics MUST be testable numbers (not adjectives like "fast" or "intuitive").
- Anti-goals MUST include the reason for deferral (no reason = agent may add it anyway).
- Section 6 (Label Map) is the most important section for Kiro — SM-PLAN reads it first.
- Open Questions (Section 8) block the next gate until resolved.

---

## PRD STRUCTURE CHECKLIST

Before marking PRD complete, verify ALL sections exist and are non-empty:

- [ ] Section 1: App Overview
- [ ] Section 2: Target Users
- [ ] Section 3: Problem Statement
- [ ] Section 4: Feature List with confidence levels
- [ ] Section 5: User Stories (GIVEN/WHEN/THEN)
- [ ] Section 6: Kiro Label Map ← SM-PLAN reads this FIRST
- [ ] Section 7: Success Metrics (testable)
- [ ] Section 8: Anti-Goals with reasons
- [ ] Section 9: MVP Scope boundary
- [ ] Section 10: Open Questions

---

## SECTION 1 — App Overview

```
APP NAME:      [name]
ONE-LINER:     [one sentence describing what the app does and for whom]
VERSION:       v1 (PRD) | last updated: YYYY-MM-DD
CHANGELOG:     [YYYY-MM-DD: initial | YYYY-MM-DD: added feature X]
```

---

## SECTION 2 — Target Users

List each user type with context:
```
PRIMARY USER:  [role/persona] — [context: what they do, why they'd use this]
SECONDARY USER: [role/persona] — [context]
ADMIN USER:    [role/persona] — [context]
```

Do NOT write vague personas like "busy professionals." Write: "B2B SaaS ops manager at a 50-person company who manually exports CSVs from 3 tools every Monday morning."

---

## SECTION 3 — Problem Statement

Format:
```
CURRENT STATE:  [What do users do today? What is the painful manual process?]
ROOT CAUSE:     [Why does this problem exist?]
CONSEQUENCE:    [What does it cost users — time, money, errors, frustration?]
OUR SOLUTION:   [One paragraph: what we build and why it specifically solves the root cause]
```

---

## SECTION 4 — Feature List

Confidence levels are MANDATORY. They control sprint prioritization and scope-cut decisions.

```
| Feature | Description | Confidence | Notes |
|---------|-------------|------------|-------|
| [name]  | [1 sentence] | MUST / SHOULD / NICE | [constraint or dependency] |
```

- **MUST**: MVP blocker. Cannot ship without it.
- **SHOULD**: Strong intent for v1. Can scope-cut if sprint capacity requires.
- **NICE**: Aspirational. Only if MUST + SHOULD done with time remaining.

---

## SECTION 5 — User Stories

Format: GIVEN/WHEN/THEN. One story per distinct user action. Group by feature.

```
Feature: [Feature Name]

Story: [short title]
GIVEN:  [precondition — what state is the user/system in]
WHEN:   [user action or system trigger]
THEN:   [expected outcome — specific, observable]

ERROR:  [what happens when the action fails — message, recovery]
EMPTY:  [what the user sees if no data exists yet]
```

BANNED formats:
- "As a user I can log in" — not testable
- "The system should handle errors gracefully" — not specific
- "Users will be able to view their dashboard" — no precondition, no error path

---

## SECTION 6 — Kiro Label Map ← SM-PLAN READS THIS FIRST

This section is the primary input to SM-PLAN. Labels here override label inference from prose.
SM-PLAN MUST read this section before creating any story. If this section is missing → SM-PLAN BLOCKS.

```
| Feature | Story Title | Labels | Primary Role | Notes |
|---------|-------------|--------|--------------|-------|
| Auth    | OAuth login | [be/auth, security-critical] | security_engineer | Google + GitHub OAuth |
| Auth    | WebAuthn passkey | [be/auth, security-critical] | security_engineer | FIDO2 — load webauthn_fido2.md |
| Dashboard | Activity feed | [fe/component, fe/state, data/eda] | frontend_lead | real-time updates |
| API     | Export CSV | [be/api, testing/e2e] | backend_lead | large dataset, streaming |
| Infra   | CI/CD setup | [devops/ci, devops/infra] | devops_engineer | GitHub Actions |
```

Label taxonomy reference: kiro/steering/skill-label-index.md

---

## SECTION 7 — Success Metrics

All metrics MUST be measurable. No adjectives. Format: metric + target + measurement method.

```
| Metric | Target | How Measured | When |
|--------|--------|--------------|------|
| Dashboard load time (LCP) | < 2.0s | Lighthouse CI | every PR |
| API p95 response time | < 200ms | k6 load test | weekly |
| 7-day user retention | ≥ 40% | analytics cohort | 4 weeks post-launch |
| Error rate (5xx) | < 0.1% | Datadog SLO | continuous |
| Onboarding completion | ≥ 70% | funnel analytics | 2 weeks post-launch |
```

BANNED metric formats:
- "Users find the dashboard useful" — not measurable
- "Fast load times" — no number
- "Low error rate" — no threshold

---

## SECTION 8 — Anti-Goals (NOT in v1)

Every anti-goal MUST have a reason. Without reason, agents may add the feature "to be helpful."

```
| Feature | Why Deferred | Target Version |
|---------|--------------|----------------|
| Real-time notifications | WebSocket infra adds 3 sprints. Polling is sufficient for v1. | v2 |
| Mobile app | Web-first to validate core loop. Mobile adds 4 weeks. | v2 |
| AI recommendations | Requires training data from v1 usage. Can't build before data exists. | v3 |
| Multi-tenancy | Single-tenant is sufficient for initial customers. | v2 |
```

---

## SECTION 9 — MVP Scope Boundary

Explicit line between v1 and post-v1. Answers: "if we had to cut 30% of features to ship on time, what's the irreducible core?"

```
CORE (must ship for MVP to be viable):
  - [feature 1]
  - [feature 2]

NICE-TO-HAVE (cut first if scope pressure):
  - [feature A]
  - [feature B]

POST-MVP (never cut — defer to v2):
  - [anti-goal features from Section 8]
```

---

## SECTION 10 — Open Questions

Unresolved decisions that block design or implementation. Each question has an owner and a gate it blocks.

```
| Question | Blocks | Owner | Due |
|----------|--------|-------|-----|
| SAML SSO required or OAuth-only? | GATE 2 (TRD trust boundary) | architect + cto | before Sprint 1 |
| Self-hosted or cloud-only? | GATE 2 (infra architecture) | architect | before Sprint 1 |
| GDPR scope: EU users only or all? | GATE 2 (schema GDPR classification) | cto | before Sprint 1 |
| Mobile v1 or web-only? | Label Map (mobile/* labels) | cto | before SM-PLAN |
```

Open questions are surfaced in project-index.md and block the listed gate.
SM-PLAN cannot run until all questions blocking SM-PLAN gate are resolved.

---

## VALIDATION LOG

When PRD is complete, emit:
```
[PRD-COMPLETE: app=<name> | features=N (MUST=X/SHOULD=Y/NICE=Z) | stories=M | label-map: ✅ | metrics: testable ✅ | open-questions: K blocking GATE 2]
```
