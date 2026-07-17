# Dry Run — JWT Auth API (End-to-End System Trace)
**Date:** 2026-06-30
**Input:** "Build a rate-limited JWT authentication API with Redis caching, retry logic, and integration tests"
**Purpose:** End-to-end system trace covering hook routing, mode selection, dynamic skill loading (Fix 23), loop engine, all gates, all disciplines. Reference for Fix 24 gap analysis.

---

## HOOK TRACE

### STEP 0 — COMPLEXITY GATE
Word count: 16 → >8 → continue.
Keyword: `Build` matched.

### STEP 1 — ENV DETECTION
```
[ENV] TRACKER_MODE=markdown | GIT_MODE=LOCAL
```

### STEP 2 — REQUEST CLASSIFICATION
TRIVIAL check: 16 words (>12) ❌ + contains "integration" ❌ → NOT TRIVIAL
BUILD check: `Build` + `API` ✅ → CLASS: BUILD → STEP 3

### STEP 3 — MODE SELECTION
No explicit override. discovery-engine.md loaded → 7 scoping questions → user confirms Mode 1.
```
[MODE: 1 selected]
```
**GAP A:** Single-shot input stalls here — no user to answer scoping questions.

### STEP 4 — LOAD STEERING + SPRINT STATE
Sprint state: checkpoint.md last row = Fix 23A-D entry → no sprint context → fresh build.
```
[SPRINT STATE: fresh build]
[MEMORY: 0 lessons loaded (domain: backend+all), 0 ADRs loaded]
```

Mandatory files loaded:
| File | ~Tokens |
|------|---------|
| team-orchestrator-core.md | 4,200 |
| team-orchestrator-rules.md | 3,800 |
| skill-selection-matrix.md | 6,500 |
| context-memory-discipline.md | 1,200 |
| memory-management.md | 900 |
| **Total before any role** | **~16,600** |

Shared skill verification (Fix 21A):
```
[INIT WARNING: skill file absent — kiro/skills/shared/api_versioning_strategy.md]
[INIT WARNING: skill file absent — kiro/skills/shared/error_handling_strategies.md]
[INIT WARNING: skill file absent — kiro/skills/shared/privacy_engineering.md]
```
**GAP B:** ~30 shared skill files named in Fix 23C index do not exist. Backlog flooded every session.

---

## THINK PHASE

market_researcher → cto → architect (abbreviated)

CTO decisions: JWT RS256, Redis sliding-window rate limiter, exponential backoff + jitter.

ROLE HANDOFF — cto → architect:
```
Artifact: docs/foundation/tech-decisions.md
Key decisions:
  1. JWT (jsonwebtoken) — stateless, RS256 signing
  2. Redis sliding-window counter for rate limits
  3. Exponential backoff + jitter for retry logic
Blockers: none
Next role needs: system diagram, API contract
Token count: ~18,200 tok
```

**GATE 1: 🟢 GREEN**

---

## GATE 2 / SM-GATE

```
[x] DESIGN SYSTEM GATE (Fix 22C): no fe/mobile stories → N/A ✅
[ ] LABEL GATE (Fix 23B): stories don't exist yet — NOTHING TO CHECK
```
**GAP C:** SM-GATE runs before SM-PLAN. LABEL GATE fires on stories that don't exist. No-op on Sprint 1.

All other items pass. **VERDICT: 🟢 GREEN**

---

## SM-PLAN — Story Creation + Label Assignment

| ID | Title | Points | Labels |
|----|-------|--------|--------|
| AUTH-1 | Rate-limit middleware (Redis sliding window) | 5 | `be/resilience`, `be/caching` |
| AUTH-2 | JWT sign / verify / refresh endpoints | 8 | `be/auth`, `security-critical` |
| AUTH-3 | Retry logic with exponential backoff + jitter | 3 | `be/resilience`, `be/api` |
| AUTH-4 | Integration test suite (test containers) | 5 | `testing/integration`, `be/api` |

### Dynamic Skill Resolution — AUTH-2 (`be/auth`, `security-critical`)
Section 1: be/auth → `[auth_patterns_jwt_oauth.md, shared/security_baseline.md]`
Section 1: security-critical → `[shared/security_baseline.md]` + security_engineer DEVELOP pass
Role override (senior_engineer_be): no delta
Union + dedup: `[auth_patterns_jwt_oauth.md, shared/security_baseline.md]` → ~280 tok compressed

```
[SKILLS: labels=[be/auth, security-critical] | role=senior_engineer_be
         | files=auth_patterns_jwt_oauth.md, shared/security_baseline.md | Σ~280tok]
```
**GAP D:** `auth_patterns_jwt_oauth.md` has no path prefix — system cannot locate it. Non-shared files have no folder resolution rule.

---

## DEVELOP — AUTH-2 (Full Loop Trace)

`loop-engine.md` loaded at DEVELOP start.

### LOOP SPEC — AUTH-2: JWT sign/verify/refresh
```
GOAL: JWT middleware passing RS256 sign, validate, refresh — all verifier commands green.

VERIFIER:
  - npm test -- --testPathPattern=auth --coverage
  - npx tsc --noEmit
  - npx eslint src/auth/
  - npx semgrep --config=p/jwt-security

CRITERIA (label-sourced, Fix 23D):
  From be/auth summary:
    C1. Token expiry enforced? (exp claim + validated)
    C2. Refresh rotation? (old token invalidated on refresh)
    C3. Scope/role validated per request?
  From security-critical summary:
    C4. Algorithm whitelist enforced? (no "none" / HS256 downgrade)
    C5. Secret externalized? (no hardcoded secret)

STOP WHEN: all ≥ 8, OR 8 iterations.
```
**GAP E:** "SM approves loop spec" (per loop-engine.md) — not wired. No hook step triggers this.

### ITERATION 1 — PLAN→DO→CHECK→ACT
DO: Auth middleware stub produced.

CHECK:
```
C1. Token expiry enforced?  → 9 ✅
C2. Refresh rotation?       → 4 ❌ ← lowest
C3. Scope validated?        → 7
C4. Algorithm whitelist?    → 8 ✅
C5. Secret externalized?    → 5 ❌
Score: 33/50 = 6.6 → < 7 → ACT fires
```

```
[ACT: reloading auth_patterns_jwt_oauth.md FULL CONTENT
      — criteria C2 (refresh rotation) + C5 (secret externalized)]
```
Guidance extracted: refresh token blacklist + `process.env.JWT_SECRET`.
Revision applied: blacklist store added, secret moved to env.

### ITERATION 2 — re-CHECK
```
C1. Token expiry?    → 9 ✅
C2. Refresh rotation?→ 8 ✅
C3. Scope validated? → 8 ✅
C4. Alg whitelist?   → 9 ✅
C5. Secret external? → 8 ✅
Score: 42/50 = 8.4 → ALL ≥ 8 → MAKER done ✅
```

### Security_engineer DEVELOP pass (Fix 22D — scoped)
- ADR match: JWT approach matches CTO decision ✅
- S2: no new trust boundaries ✅
- S3: secret in env var ✅
- Full STRIDE: architecture unchanged → NOT triggered ✅

### CHECKER — qa_engineer (fresh context)
Runs verifier independently → all pass → Score: 8.5 → **ACCEPT ✅**

### impl-decision
```
[AUTH-2] jsonwebtoken v9 over jose/passport-jwt — RS256 support, ecosystem fit.
[PROMOTE] — reusable across any BE service needing JWT
```

### Git + Tracker
```
Branch: feature/AUTH-2-jwt-sign-verify-refresh
Commit: feat(auth): JWT sign/verify/refresh with RS256 + token rotation
PR #4 → main | CI: green | Reviewed ✅
[TRACKER] AUTH-2: In Progress → Done | comment: PR #4 merged
```

AUTH-1, AUTH-3, AUTH-4: abbreviated — same loop pattern, all closed ✅

---

## GATE 4 / SM-RETRO

### Sprint Discipline Card
| Dimension | This sprint | Target | Status |
|-----------|-------------|--------|--------|
| Velocity | 21/21 pts | ≥80% | 🟢 |
| Token discipline | GOOD (peaked ~24K) | GOOD+ | 🟢 |
| Git hygiene | 0 direct to main, 0 unreviewed | 0/0 | 🟢 |
| $TRACKER sync | 0 stories missing | 0 | 🟢 |
| Test coverage | 78% (Δ +78%) | ≥70% | 🟢 |

### GATE 4 step 2b
1. Confidence: Sprint 1 → stays `low` ✅
2. Lessons:
   - `"JWT refresh rotation must be designed upfront"` domain=security
   - `"Redis sliding-window preferred over fixed-window for rate limits"` domain=backend
3. ADR: AUTH-2 [PROMOTE] → promoted to kiro/memory/decisions.md ✅
4. IMPL-DECISIONS review: AUTH-2 flagged [PROMOTE] → promoted ✅
5. Memory refresh:
```
[MEMORY REFRESH: 2 new lessons + 1 ADR now active]
```

**GAP F:** Mode 1 hits DEGRADING tier by story 3 (~23K tokens). security_engineer + loop iterations running at DEGRADING = compressed reads only for final two stories. No graceful degradation path for mid-sprint DEVELOP.

---

## AGENT ACTIVATION REPORT

| Stage | Agent/Gate | Activated | Labels | Skills loaded | Loop iters | Token tier |
|-------|-----------|-----------|--------|---------------|------------|------------|
| Hook | Router | ✅ | — | mandatory ×5 | — | PEAK |
| THINK | market_researcher | ✅ | — | 2 | — | PEAK |
| THINK | cto | ✅ | — | 2 | — | PEAK |
| THINK | architect | ✅ | — | 3 | — | GOOD |
| GATE 1 | discovery-engine | ✅ | — | — | — | GOOD |
| GATE 2 | scrum_master (SM-GATE) | ✅ | — | 2 | — | GOOD |
| PLAN | scrum_master (SM-PLAN) | ✅ | 4 stories labeled | index lookup ×4 | — | GOOD |
| DEVELOP | senior_engineer_be (AUTH-1) | ✅ | be/resilience, be/caching | 4 | 2 | GOOD |
| DEVELOP | security_engineer (AUTH-2) | ✅ | security-critical | scoped | — | DEGRADING |
| DEVELOP | senior_engineer_be (AUTH-2) | ✅ | be/auth, security-critical | 2 | 2 | DEGRADING |
| DEVELOP | qa_engineer (AUTH-2 checker) | ✅ | — | testing_pyramid | 1 | DEGRADING |
| DEVELOP | senior_engineer_be (AUTH-3/4) | ✅ | be/resilience, testing/integration | 3 | 1-2 | DEGRADING |
| GATE 4 | scrum_master (SM-RETRO) | ✅ | — | retro ×2 | — | CRITICAL |

**Total activations: 13**

---

## GAP REPORT (→ Fix 24)

| ID | Where | Gap | Severity |
|----|-------|-----|----------|
| A | STEP 3 / discovery-engine | Mode selection blocks on 7 scoping questions — no auto-inference rule for single-shot input | 🔴 High |
| B | Fix 21A + Fix 23C | ~30 skill index files don't exist — backlog flooded with warnings every session start | 🔴 High |
| C | Fix 23B / SM-GATE timing | LABEL GATE fires before stories exist (Sprint 1) — gate is a no-op | 🔴 High |
| D | Fix 23C path resolution | Non-shared skill files have no folder resolution rule — cannot locate `auth_patterns_jwt_oauth.md` | 🔴 High |
| E | loop-engine.md | SM loop-spec approval not wired — no hook step or gate triggers it before DEVELOP | 🟡 Medium |
| F | Token budget | Mode 1 hits DEGRADING by story 3 — no graceful degradation path for mid-sprint DEVELOP | 🟡 Medium |
| G | skill-selection-matrix.md size | Fix 23C inflated matrix to ~600 lines (~6,500 tok loaded every Mode 1 session) | 🟡 Medium |
