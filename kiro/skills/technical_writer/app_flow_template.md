<!-- LOAD-TYPE: CHECKLIST -->
---
id: app_flow_template
version: 1.0.0
owners: [technical_writer, frontend_lead]
tags: [foundation, app-flow, ux, planning]
when_to_use: >
  When creating /docs/foundation/app-flow.md. Mandatory GATE 2 artifact.
  SM-PLAN reads GIVEN/WHEN/THEN from this doc for loop spec acceptance criteria.
  frontend_lead reviews for technical feasibility after technical_writer drafts.
  GATE 2 stays RED until app-flow.md exists with all screens documented.
---

# App Flow Template — User Journey & Screen Specification

FULL-LOAD REQUIRED — creation checklist and structural template.
Output file: `/docs/foundation/app-flow.md`
Owner: `technical_writer` (drafts) + `frontend_lead` (feasibility review)

---

## QUICK REFERENCE

- Every screen MUST have: GIVEN/WHEN/THEN + ERROR STATE + EMPTY STATE + SUCCESS STATE.
- VERIFIER ANCHOR per screen tells the loop engine how to verify the screen works in CI.
- SM-PLAN reads this doc to write loop spec criteria — not from PRD user stories.
- loop-engine.md: GIVEN/WHEN/THEN from App Flow → become loop spec criteria directly (scored 1-10).
- Missing error/empty states = agent invents them mid-sprint (wrong 60% of the time).
- Navigation flow must cover: unauthenticated paths, authenticated paths, admin paths separately.

---

## APP FLOW STRUCTURE CHECKLIST

Before marking App Flow complete, verify:

- [ ] Navigation map exists (all routes listed)
- [ ] Every screen has GIVEN/WHEN/THEN
- [ ] Every screen has ERROR STATE (at least one failure case)
- [ ] Every screen has EMPTY STATE (zero-data scenario)
- [ ] Every screen has SUCCESS STATE (confirmation/next step)
- [ ] Every screen has VERIFIER ANCHOR (bash command or test reference)
- [ ] Auth flows covered: login, register, logout, session expiry, password reset
- [ ] All user roles have separate flow paths documented (if role-based UI differs)

---

## SECTION 1 — Navigation Map

List ALL routes with their access rules. Unauthenticated access to protected routes → redirect rule.

```
ROUTE MAP:
  Public (no auth required):
    /                     → Landing page
    /login                → Login screen
    /register             → Registration screen
    /forgot-password      → Password reset request
    /reset-password/:token → Password reset form

  Authenticated (redirect to /login if unauthenticated):
    /dashboard            → Main dashboard
    /settings             → User settings
    /settings/security    → Security settings (MFA, passkeys)
    /[feature]            → [feature description]

  Admin only (redirect to /dashboard if non-admin):
    /admin                → Admin panel
    /admin/users          → User management

REDIRECT RULES:
  Unauthenticated → /protected-route: redirect to /login?next=[original-url]
  Authenticated → /login: redirect to /dashboard
  Non-admin → /admin: redirect to /dashboard with toast "Access denied"
```

---

## SECTION 2 — Auth Flows (MANDATORY — cover all paths)

### Login Screen — `/login`

```
GIVEN:  user is unauthenticated
WHEN:   user submits valid email + password
THEN:   POST /auth/login → 200 | session created | redirect to /dashboard (or ?next= URL)

WHEN:   user submits invalid credentials (attempt 1-4)
THEN:   POST /auth/login → 401 | inline error: "Incorrect email or password" | password field cleared | focus on password

WHEN:   user submits invalid credentials (attempt 5)
THEN:   POST /auth/login → 423 | account locked | redirect to /login?locked=true | lockout banner shown | recovery email sent

WHEN:   user clicks "Continue with Google"
THEN:   redirect to Google OAuth | on success: redirect to /dashboard | on failure: toast "Google login failed, try again"

EMPTY STATE:  n/a (login always has form — no empty state)
SUCCESS STATE: redirect to /dashboard + welcome toast "Welcome back, [name]"
ERROR STATE:   inline field error (not page-level toast) | no error codes exposed to user

VERIFIER ANCHOR:
  curl -X POST /api/auth/login -d '{"email":"test@test.com","password":"wrong"}' → 401
  curl -X POST /api/auth/login [valid creds] → 200 + Set-Cookie header
```

### Registration Screen — `/register`

```
GIVEN:  user is unauthenticated
WHEN:   user submits valid registration form (email, password, name)
THEN:   POST /auth/register → 201 | verification email sent | redirect to /register/verify-email

WHEN:   user submits email that already exists
THEN:   POST /auth/register → 409 | inline error on email field: "An account with this email already exists" | link: "Log in instead"

WHEN:   password does not meet requirements
THEN:   client-side validation fires | requirements list highlights (length, uppercase, special char) | submit blocked

EMPTY STATE:  n/a
SUCCESS STATE: /register/verify-email screen shown with "Check your inbox" message
ERROR STATE:   409 Conflict shown as email field error (not generic toast)

VERIFIER ANCHOR:
  POST /api/auth/register [valid payload] → 201 + { userId, emailVerificationPending: true }
  POST /api/auth/register [duplicate email] → 409
```

### Session Expiry

```
GIVEN:  user is authenticated with an expired session
WHEN:   user makes any authenticated API request
THEN:   API returns 401 | frontend intercepts 401 | redirect to /login?session=expired | banner: "Your session expired. Please log in again."

WHEN:   user returns to the app after session expiry (passive)
THEN:   on next navigation or page load: session check fails | same redirect + banner as above

VERIFIER ANCHOR:
  Use expired JWT → GET /api/me → 401 | frontend redirects to /login
```

---

## SECTION 3 — Screen Template

Use this template for EVERY screen in the app. Copy and fill for each route.

```
## Screen: [Screen Name] — Route: [/path]
Owner: [role responsible for implementation]
Labels: [fe/component, fe/state, ...] ← copied to story label in SM-PLAN

GIVEN:  [precondition — what state is user/system in before this screen is relevant]
WHEN:   [primary user action or trigger]
THEN:   [expected result — specific: URL change, API call made, data displayed, state updated]

SECONDARY ACTIONS:
  WHEN: [secondary action]
  THEN: [result]

ERROR STATE:
  WHEN: [failure condition — API error, network failure, validation fail]
  THEN: [what user sees — error message text, recovery option, is data preserved?]
  Toast / Inline / Page-level error? [pick one and be consistent]

EMPTY STATE:
  WHEN: [user arrives with no data — new account, empty list, no results]
  THEN: [what is displayed — illustration, headline, CTA, example/demo content?]
  CTA: [what action is offered to fill the empty state]

SUCCESS STATE:
  WHEN: [action completes successfully]
  THEN: [confirmation — toast message, redirect, updated UI element, animation]
  Message: "[exact text of success message]"

LOADING STATE:
  WHEN: [async operation in progress]
  THEN: [skeleton loader / spinner / progress bar — be specific]
  Timeout: [if loading exceeds Xs → show "Taking longer than expected..." with retry]

VERIFIER ANCHOR:
  [bash command or test reference that proves this screen/state works in CI]
  Example: `npx playwright test tests/dashboard.spec.ts --grep "empty state"`
  Example: `curl -X GET /api/dashboard -H "Authorization: Bearer [token]" → 200 + { items: [] }`
```

---

## SECTION 4 — Example: Dashboard Screen

```
## Screen: Main Dashboard — Route: /dashboard
Owner: frontend_lead + senior_engineer_be
Labels: [fe/component, fe/state, data/eda]

GIVEN:  user is authenticated
WHEN:   user navigates to /dashboard
THEN:   GET /api/dashboard/summary → 200 | activity feed loaded | KPI cards rendered | last 7 days by default

SECONDARY ACTIONS:
  WHEN: user changes date range filter
  THEN: filter state updated | GET /api/dashboard/summary?from=X&to=Y triggered | data refreshes without full page reload

  WHEN: user clicks on an activity item
  THEN: navigate to /[feature]/[id] detail view

ERROR STATE:
  WHEN: GET /api/dashboard/summary returns 500 or network timeout
  THEN: page-level error banner: "Unable to load dashboard. Try refreshing." | retry button | KPI cards show "—" placeholder

EMPTY STATE:
  WHEN: user has no activity yet (new account or empty period)
  THEN: illustration + "No activity yet" headline + "Get started" CTA button → /onboarding
  Do NOT show empty table with headers — show the empty state component

SUCCESS STATE: n/a (dashboard is a view, not an action)

LOADING STATE:
  WHEN: initial load or filter change
  THEN: KPI card skeletons (4 cards) + activity feed skeleton (5 rows)
  Timeout: if > 5s → "Taking longer than usual…" message with retry

VERIFIER ANCHOR:
  curl -X GET /api/dashboard/summary → 200 + { kpis: [...], activity: [...] }
  Playwright: tests/e2e/dashboard.spec.ts → "shows empty state for new user"
```

---

## SECTION 5 — Navigation Flows (User Journeys)

List the critical end-to-end journeys. These become the E2E test scope in testing-strategy.md.

```
Journey 1: New User Onboarding
  /register → email verify → /onboarding → /dashboard (first use)
  Critical path: YES — E2E test required

Journey 2: Core Value Action (e.g., Create Report)
  /dashboard → /reports/new → fill form → submit → /reports/[id] → share
  Critical path: YES — E2E test required

Journey 3: Settings & Security
  /settings → /settings/security → add passkey → confirm → return to settings
  Critical path: YES — E2E test required (WebAuthn declared in security-posture.md)

Journey 4: Admin — User Management
  /admin/users → search user → deactivate → confirm → user deactivated
  Critical path: YES — E2E test required
```

---

## VALIDATION LOG

When App Flow is complete, emit:
```
[APP-FLOW-COMPLETE: screens=N | error-states=M | empty-states=K | verifier-anchors=P | critical-journeys=Q | GATE 2: ✅]
```
