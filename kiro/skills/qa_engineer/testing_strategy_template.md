<!-- LOAD-TYPE: CHECKLIST -->
---
id: testing_strategy_template
version: 1.0.0
owners: [qa_engineer, backend_lead]
tags: [foundation, testing, quality, verifier, coverage]
when_to_use: >
  When creating /docs/foundation/testing-strategy.md. Mandatory GATE 2 artifact.
  qa_engineer owns creation. backend_lead reviews Sections 3+4. cto approves Section 6 Done Definition.
  loop-engine.md VERIFIER type selection reads Section 3 before applying fallback rules.
  VERIFIER coverage format reads Section 2 (coverage targets) before writing VERIFIER command.
  GATE 2 stays RED until all 8 sections are present and non-empty.
---

# Testing Strategy Template — Project Test Foundation

FULL-LOAD REQUIRED — this drives VERIFIER command format, tool selection, coverage enforcement, and Done Definition system-wide.
Output file: `/docs/foundation/testing-strategy.md`
Owner: `qa_engineer` (drafts) + `backend_lead` (reviews Sections 3+4) + `cto` (approves Section 6)

**Feeds into:**
- loop-engine.md VERIFIER type classification (Section 3 overrides fallback guessing)
- loop-engine.md STANDARD VERIFIER format (Section 2 coverage targets added to command)
- SM-PLAN E2E-REQUIRED story flagging (Section 5 critical journey list)
- SM-RETRO Sprint Discipline Card "VERIFIER compliance" row (Section 6 Done Definition)
- security-posture.md Section 7 SAST tooling (Section 8 is the CI implementation of that policy)

---

## TESTING STRATEGY CHECKLIST

Before marking testing-strategy.md complete, verify ALL sections present and non-empty:

- [ ] Section 1: Test Pyramid Declaration (all applicable levels declared)
- [ ] Section 2: Coverage Targets (numbers, not "as much as possible")
- [ ] Section 3: Tool Decisions (one tool per category — no ambiguity)
- [ ] Section 4: Test Data Strategy
- [ ] Section 5: Critical User Journey List (E2E scope boundary)
- [ ] Section 6: Story Done Definition (per story type)
- [ ] Section 7: Accessibility Testing Standard
- [ ] Section 8: Security Testing in CI (implements security-posture.md Section 7)

---

## SECTION 1 — Test Pyramid Declaration

Declare each level explicitly. "none" is a valid value — but must be stated, not absent.

```
UNIT:
  Status:   active | none
  Framework: jest | pytest | go test | vitest | JUnit | RSpec
  Target:   ≥80% line coverage | ≥70% branch coverage | not enforced (must be explicit)
  Applies to: all business logic, API handlers, utility functions

INTEGRATION:
  Status:   active | none
  Framework: supertest | httpx | testcontainers | REST-assured
  Target:   all API contracts covered (happy path + primary error paths)
  Applies to: API endpoints, DB queries, external service boundaries

E2E:
  Status:   active | none
  Tool:     Playwright | Cypress
  Scope:    CRITICAL JOURNEYS ONLY (listed in Section 5) — not every screen
  Applies to: user flows listed in Section 5

CONTRACT:
  Status:   active | none
  Tool:     Pact | Spring Cloud Contract | none
  Required if: microservices with independent deployment | 3rd-party API integrations
  Applies to: service boundaries with independent release cycles

VISUAL_REGRESSION:
  Status:   active | none
  Tool:     Percy | Chromatic | none
  Required if: shared component library | design system with versioned components
  Applies to: all components in /components/shared/ or storybook

PROPERTY_BASED:
  Status:   active | none
  Tool:     fast-check (TypeScript) | hypothesis (Python) | jqwik (Java)
  Required if: [be/resilience] stories (CRDT, distributed lock) | [security-critical] (ABAC, crypto)
  Applies to: stateful protocol tests, permission boundary tests

LOAD:
  Status:   active | none
  Tool:     k6 | autocannon | Artillery | locust
  Required if: [be/perf] stories in roadmap | >1000 concurrent users expected
  Applies to: all public API endpoints + critical background jobs

MOBILE:
  Status:   active | none
  Tool:     Detox | XCTest + Espresso | none
  Required if: mobile/* labels in roadmap
  Applies to: all critical journeys (Section 5) on iOS + Android
```

---

## SECTION 2 — Coverage Targets

**loop-engine.md VERIFIER format for STANDARD stories uses these values.**
If COVERAGE_IN_CI=yes: coverage drop blocks merge. No exceptions.

```
MINIMUM_LINE:      80%   (or: not enforced — must be explicit, not omitted)
MINIMUM_BRANCH:    70%   (or: not enforced)
MINIMUM_FUNCTION:  85%   (or: not enforced)

COVERAGE_TOOL:     istanbul (jest) | coverage.py | go cover | simplecov | jacoco

COVERAGE_IN_CI:    yes | no
  If yes — VERIFIER command format for STANDARD stories:
    Jest:   "jest --coverage --coverageThreshold='{\"global\":{\"lines\":80,\"branches\":70}}'"
    Pytest: "pytest --cov=src --cov-fail-under=80"
    Go:     "go test ./... -coverprofile=coverage.out && go tool cover -func=coverage.out | grep total | awk '{if ($3+0 < 80) exit 1}'"
  Coverage exit non-zero = VERIFIER fails = story cannot close.

EXCLUSIONS:        /migrations/*, /scripts/*, /mocks/*, /fixtures/*, *.config.js
  (Excluded paths do not count toward coverage — reduces noise from boilerplate)

COVERAGE_BADGE:    yes | no (update README on each main branch merge)
```

---

## SECTION 3 — Tool Decisions

**loop-engine.md Fix 30C VERIFIER type classification uses this section.**
One tool per category. Primary tool is used; fallback only if primary binary is unavailable.

```
UNIT_FRAMEWORK:      jest | pytest | go test | vitest | JUnit
ASSERTION_LIBRARY:   jest built-in expect | chai | should.js | assert (built-in)
MOCK_LIBRARY:        jest.mock + @testing-library | sinon | unittest.mock | testify/mock

API_TEST_TOOL:       supertest | httpx | requests | RestAssured
DB_TEST_STRATEGY:    docker + testcontainers | separate test schema | in-memory (H2/SQLite)

E2E_TOOL:            Playwright | Cypress
  Primary:   Playwright (recommended — faster, multi-browser, no Electron)
  Fallback:  Cypress (if Playwright unsupported in CI environment)
  BANNED:    Selenium (too slow, too brittle for modern SPAs)

LOAD_TEST_TOOL:
  Primary:   k6 (recommended — JS scripting, Grafana integration)
  Fallback:  autocannon (npm i -g autocannon — use ONLY if k6 binary unavailable in CI)
  Note: Fix 30C fallback rule uses this declaration. If PRIMARY=k6, never default to autocannon unless k6 not installed.

VISUAL_TOOL:         Percy | Chromatic | none
CONTRACT_TOOL:       Pact | none
PROPERTY_TOOL:       fast-check | hypothesis | none
MOBILE_TOOL:         Detox | XCTest/Espresso | none
```

---

## SECTION 4 — Test Data Strategy

**qa_engineer/test_data_management.md reads this as baseline.**

```
APPROACH:           factory-boy | fishery | fixtures | seeds | inline mocks
  Recommended:      factory-boy (Python) | fishery (TypeScript) — factories > fixtures
  Avoid:            hardcoded test data in test files | production data snapshots

NON_PROD_DATA:      synthetic only (recommended) | anonymized prod snapshot | none
  If HIPAA=yes (from security-posture.md Section 3): MUST be synthetic only.
    Violation: automatic TECH-DEBT story "Implement PHI-safe test data generation"
  If none: flag as TECH-DEBT — tests with no data strategy become production-risk tests

TEST_DATABASE:      docker container (isolated per test run — recommended)
                    | separate schema in shared dev DB
                    | in-memory (SQLite/H2 — only for unit tests, not integration)

CLEANUP_STRATEGY:   truncate-per-test (fast, explicit) | transaction-rollback (slower, automatic)
  Truncate-per-test: `beforeEach(() => truncateAllTables(db))`
  Transaction-rollback: wrap each test in a transaction, rollback in afterEach

SEED_DATA:          minimal — only what the test needs (no "load everything" seeds)
  Shared fixtures:  /tests/fixtures/ — imported explicitly (not auto-loaded)
  Factory defaults: sensible defaults, override per test case
```

---

## SECTION 5 — Critical User Journey List (E2E Scope Boundary)

**SM-PLAN marks a story as E2E-REQUIRED if it modifies any journey listed here.**
**E2E VERIFIER is NOT required on stories that don't touch these journeys — prevents E2E sprawl.**

```
Journey 1: [name]
  Path:     /start → /step1 → /step2 → /end
  Trigger:  story modifies auth, registration, or onboarding screens
  E2E file: tests/e2e/[name].spec.ts

Journey 2: [name]
  Path:     [route] → [action] → [result]
  Trigger:  story modifies [which screens/APIs]
  E2E file: tests/e2e/[name].spec.ts

Journey 3: [name]
  ...
```

Minimum: 1 journey. Recommended: 3-5 core journeys covering 80% of user value.
BANNED: "E2E on every page" — this guarantees slow CI and unmaintained tests.

---

## SECTION 6 — Story Done Definition (Per Story Type)

**SM-RETRO Sprint Discipline Card "VERIFIER compliance" row references this.**
Done Definition tells the loop engine what VERIFIER exit conditions close a story.

```
STANDARD story (unit/integration only):
  ✅ Unit tests passing (coverage threshold met if COVERAGE_IN_CI=yes)
  ✅ Linter passing (tsc / eslint / ruff — zero errors)
  ✅ VERIFIER exits 0
  ✅ PR approved by 1 reviewer

SECURITY-CRITICAL story (be/auth, security-critical label):
  ✅ All STANDARD requirements above
  ✅ SAST (semgrep) passing — zero HIGH/CRITICAL findings
  ✅ Property-based test passing (if PROPERTY_BASED=active in Section 1)
  ✅ Security-posture.md auth CHECKLIST criteria all ≥ 8

E2E-REQUIRED story (touches a critical journey in Section 5):
  ✅ All STANDARD requirements above
  ✅ Playwright/Cypress test for affected journey passing in CI
  ✅ Screenshot baseline updated (if VISUAL_TOOL active)

LOAD-REQUIRED story (be/perf label or performance criterion in loop spec):
  ✅ All STANDARD requirements above
  ✅ k6/autocannon benchmark within target (p95 < Xms for Y concurrent users)
  ✅ Benchmark results logged to CI artifact (for trend comparison)

MOBILE story (mobile/* labels):
  ✅ All STANDARD requirements above
  ✅ Detox/XCTest tests passing on iOS simulator
  ✅ Detox/Espresso tests passing on Android emulator
  ✅ Or: unified RN — single Jest suite + manual smoke note (per Fix 30A)

MODE 3 TRIVIAL story:
  ✅ VERIFIER exits 0 (no coverage requirement — by design for trivial stories)
  Coverage and security checks waived. Document reason in loop spec.
```

---

## SECTION 7 — Accessibility Testing Standard

**fe/a11y stories inherit WCAG_LEVEL from here — not re-declared per story.**
**Lighthouse --assert accessibility target (Fix 31B) uses WCAG_LEVEL declared here.**

```
WCAG_LEVEL:     AA (minimum for most products) | AAA (enhanced — banking, healthcare)

A11Y_TOOL:      axe-core (automated — @axe-core/playwright or jest-axe)
                | none

A11Y_IN_CI:     yes | no
  If yes: axe-core violations of impact=critical or serious → fail VERIFIER
  If no: manual audit required before release (log in Sprint Discipline Card)

CONTRAST_CHECK: Lighthouse automated (--assert.assertions.accessibility>=95)
                | manual (document results in PR description)
                | none

KEYBOARD_TEST:  manual checklist per E2E journey | automated (Playwright keyboard nav)
SCREEN_READER:  manual NVDA (Windows) + VoiceOver (Mac) before each release
                | automated aria-label checks only
```

---

## SECTION 8 — Security Testing in CI

**Implements security-posture.md Section 7 in CI.**
This section owns tooling and CI integration. security-posture.md owns scope and schedule.

```
SAST:
  Tool:       semgrep | bandit | eslint-plugin-security | gosec
  Config:     .semgreprc or semgrep.yml in repo root
  CI step:    runs on every PR (before unit tests — fail fast)
  Failure:    HIGH or CRITICAL severity findings block merge
  Auto-add:   If POSTURE_LEVEL=HIGH → semgrep added to VERIFIER on ALL [security-critical] stories

DEPENDENCY_SCANNING:
  Tool:       npm audit | snyk | dependabot | pip-audit
  CI step:    runs nightly + on dependency file changes
  Failure:    HIGH severity CVE in direct dependency blocks next deployment

SECRET_SCANNING:
  Tool:       gitleaks | trufflehog
  Trigger:    pre-commit hook (.git/hooks/pre-commit) + CI check on every PR
  On detect:  block commit immediately | rotate compromised credential | log incident

SECURITY_REGRESSION:
  After any security fix or pen test finding:
  → Write automated test reproducing the attack vector
  → Add test to [security-critical] VERIFIER suite permanently
  → Tag test with CVE or incident ID for traceability
```

---

## VALIDATION LOG

When testing-strategy.md is complete, emit:
```
[TESTING-STRATEGY: unit=<framework> | e2e=<tool> | coverage=<N%> | load=<tool> | E2E-journeys=N | Done-Definition: per-type ✅ | GATE 2: ✅]
```
