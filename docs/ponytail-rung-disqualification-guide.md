# Ponytail Rung Disqualification Guide
**Version:** 1.0 | **Created:** 2026-07-10 | **Fix:** 43B
**Audience:** Engineers, AI Agents, Tech Leads, Security Reviewers

---

## What Is This?

The **Ponytail Ladder** (Fix 37) prevents agents from jumping straight to writing custom code
when a standard library, installed package, or composable solution already exists.

The 7-rung ladder is:

| Rung | What It Means |
|------|--------------|
| 1 | **stdlib** — language's built-in library |
| 2 | **installed dep** — package already in package.json / go.mod / requirements.txt |
| 3 | **config** — solve it with a config change, not code |
| 4 | **installed tool** — CLI or service already available in the stack |
| 5 | **compose** — combine existing pieces (middleware chain, plugin, adapter) |
| 6 | **fork** — fork an existing OSS project and modify |
| 7 | **custom** — write it from scratch (last resort only) |

**The rule:** Start at Rung 1. Use the lowest rung that solves the problem. Justify skipping each rung before moving to the next.

---

## The Problem This Guide Solves

Sometimes **the lowest qualifying rung is disqualified** — meaning you can't use it even though it exists.

Common disqualification reasons:

| Reason | Example |
|--------|---------|
| **CVE / Security vulnerability** | `casbin v2.8` has CVE-2024-XXXXX (privilege escalation) |
| **Abandoned / unmaintained** | Last commit 3 years ago, no security patches |
| **License incompatibility** | GPL-3.0 in a commercial SaaS product |
| **Breaking API change** | v3.0 has incompatible API, no migration path |
| **Performance cliff** | Dep works but 10× slower than requirement |
| **Platform incompatibility** | Works on Linux, not on target (iOS, edge, WASM) |

Without a defined escalation path, agents get **stuck** between two rules:
- Ponytail says: "Use the dep (Rung 2)"
- Security/Legal says: "You cannot use this dep"

---

## The Disqualification Escalation Protocol

### STEP 1 — Document the Disqualification

Before skipping any rung, write a **Rung Disqualification Record (RDR)**:

```
RUNG DISQUALIFICATION RECORD
Rung: 2 (installed dep)
Package: casbin v2.8.1
Reason: CVE-2024-XXXXX — privilege escalation in multi-tenant RBAC
Evidence: https://nvd.nist.gov/vuln/detail/CVE-2024-XXXXX
Checked by: security_engineer
Date: 2026-07-10
```

This record **must exist before escalating**. No escalation without evidence.

---

### STEP 2 — Check Within the Same Rung First

Before jumping to the next rung, exhaust the CURRENT rung:

**Rung 2 disqualified? Check:**
- Is there a **patched version** of the same package? (e.g., casbin v2.9.0 patches the CVE)
- Is there an **alternative package** at the same rung? (e.g., `ory/keto` as an alternative to casbin)
- Is there a **fork** of the package maintained by the security team?

```
SAME-RUNG ALTERNATIVES CHECK
Rung 2 alternatives for RBAC:
  ✅ ory/keto v0.11 — no known CVEs, CNCF project, actively maintained → USE THIS
  ✅ casbin v2.9.1 — CVE patched → USE THIS (upgrade, not switch)
  ❌ authzed — enterprise license, not compatible
```

If a same-rung alternative exists → **use it. Do not escalate.**

---

### STEP 3 — Escalate to Next Qualifying Rung

If no same-rung alternative exists, escalate **one rung at a time**:

```
RUNG ESCALATION LOG
Rung 2 DISQUALIFIED: casbin (CVE), ory/keto (AGPL license incompatible)
Rung 3 CHECK: Can RBAC be solved with config only?
  → No. Requires logic, not config.
Rung 4 CHECK: Is there an installed tool/service that handles RBAC?
  → Auth0 RBAC rules — YES ✅
  → USE Rung 4 (Auth0 built-in RBAC engine)

RESULT: Escalated from Rung 2 → Rung 4. Rungs 2 and 3 formally disqualified.
```

**Rules:**
- Skip NO rungs without documenting why each is disqualified.
- Escalating from Rung 2 directly to Rung 7 (custom) is **not allowed** unless Rungs 3–6 are all disqualified with evidence.

---

### STEP 4 — Mandatory ADR for Any Escalation

Any escalation past Rung 2 **requires an ADR** (Architecture Decision Record):

```markdown
# ADR-XXX: RBAC Implementation — Rung 4 (Auth0) over Rung 2 (casbin/keto)

## Status: ACCEPTED

## Context
Sprint 1 — Story FRAUD-12 requires multi-tenant RBAC.

## Rung Disqualification Trail
- Rung 2 (casbin): CVE-2024-XXXXX — privilege escalation. Evidence: [link]
- Rung 2 (ory/keto): AGPL-3.0 license — incompatible with commercial SaaS
- Rung 3 (config): not applicable — RBAC requires logic
- Rung 4 (Auth0 RBAC rules): ✅ SELECTED

## Decision
Use Auth0 built-in RBAC engine. Roles and permissions defined in Auth0 dashboard.
No custom code for role evaluation.

## Consequences
+ No CVE risk
+ Maintained by Auth0 (enterprise SLA)
- Vendor lock-in to Auth0 for RBAC logic
- Role changes require Auth0 dashboard access (not code changes)

## Approved by: Architect + Security Engineer
```

---

### STEP 5 — Security Sign-Off Gate

For any escalation where the disqualification reason is a **CVE or security issue**:

The security_engineer must sign off on the replacement rung **before** the story can enter DEVELOP.

```
SECURITY SIGN-OFF REQUIRED:
Story: FRAUD-12
Disqualification: CVE-2024-XXXXX (casbin)
Replacement: Auth0 RBAC (Rung 4)
Security review: [PENDING / APPROVED]

→ Story is BLOCKED until security_engineer approves the replacement rung.
```

For license or performance disqualifications: Architect sign-off is sufficient.

---

## Quick Reference — Disqualification Decision Tree

```
Is a package at Rung N disqualified?
│
├─ Why?
│   ├─ CVE → Step 1 (document) → Step 2 (patched version? alt package?)
│   ├─ License → Step 1 → Step 2 (license-compatible alternative?)
│   ├─ Abandoned → Step 1 → Step 2 (active fork?)
│   └─ Performance → Step 1 → Step 2 (faster alt at same rung?)
│
├─ Same-rung alternative found? → USE IT. No escalation needed.
│
└─ No same-rung alternative?
    └─ Check Rung N+1
        └─ Repeat until qualifying rung found
            └─ Write ADR for escalation
                └─ Security sign-off (if CVE was the trigger)
                    └─ Proceed to DEVELOP
```

---

## What Agents Must NEVER Do

| ❌ Anti-Pattern | ✅ Correct Behavior |
|----------------|-------------------|
| Skip straight from Rung 2 to Rung 7 because "dep has a CVE" | Check same-rung alternatives first |
| Write custom RBAC code without documenting why all lower rungs were disqualified | Full disqualification trail in ADR |
| Mark a dep as "disqualified" without evidence | RDR with CVE link / license reference / metrics |
| Begin DEVELOP before security sign-off (on CVE disqualification) | Wait for sign-off gate |
| Write "Rung 2 not applicable" without checking alternatives at Rung 2 | Enumerate and rule out each alternative |

---

## Integration with GATE S2

When a story involved a rung escalation, the GATE S2 Jira comment must include:

```
Ponytail: ESCALATION — Rung 2 disqualified (CVE-2024-XXXXX)
  → Same-rung alternatives: casbin (CVE), ory/keto (license) — both disqualified
  → Escalated to: Rung 4 (Auth0 RBAC)
  → ADR: ADR-007
  → Security sign-off: ✅ [security_engineer name, 2026-07-10]
```

A GATE S2 with a rung escalation and NO ADR reference = **GATE S2 FAIL**.

---

## When to Reference This Document

- Any time an agent proposes Rung 7 (custom) and a lower rung exists but is "problematic"
- When security_engineer flags a CVE on a dep mid-story
- When a dependency license audit reveals incompatibility
- When a PR review question is: "Why didn't you just use the existing package?"

---

*This document is the authoritative escalation protocol for all Ponytail rung disqualifications.
Reference: `docs/ponytail-rung-disqualification-guide.md`*
