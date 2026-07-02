---
inclusion: manual
---

# Team Orchestrator — Architecture Rules (Fix 19 split)
# Loads at: DEVELOP phase start
# Contains: SECURITY DISCIPLINE (first — highest attention), NON-NEGOTIABLES, QUALITY BARS, CONFLICT RESOLUTION,
#           SUBAGENT ISOLATION, AGILE ENGINE, BRANCH LIFECYCLE, SESSION CONTINUITY, WORKSPACE LAYOUT, DOCUMENT OWNERSHIP
# See also: team-orchestrator-core.md (session start), team-orchestrator-sprint.md (GATE 4/5)

## SECURITY DISCIPLINE — NON-NEGOTIABLE GATES

Security is not a phase. It is a continuous gate. The `security_engineer` is embedded at three mandatory checkpoints. Nothing advances past any gate with an open HIGH or CRITICAL finding.

---

### GATE S1 — THIRD-PARTY PACKAGE APPROVAL (before any package is used in code)

**Trigger:** Any role proposes adding a new dependency (npm, pip, go mod, maven, cargo, etc.)

**`security_engineer` must execute ALL of the following before the package is approved:**

```
1. CVE scan:
   - npm:  npx audit --audit-level=high <package>@<version>
   - pip:  pip-audit --requirement <package>==<version>
   - go:   govulncheck ./...
   - rust: cargo audit

2. Supply chain check:
   - Verify package name is exact (typosquatting check — google "<package> typosquatting")
   - Check download count + last publish date + maintainer count (packages with 1 maintainer + recent ownership transfer = HIGH RISK)
   - Check for known malicious indicators: install scripts that make network calls, obfuscated code, unusual permissions

3. License check:
   - Confirm license is compatible with project's license (GPL contamination, AGPL in SaaS = block)
   - Flag: LGPL, AGPL, Commons Clause, BUSL

4. SBOM update:
   - Add package to /docs/security/sbom.json (Software Bill of Materials)
   - Fields: name, version, license, CVE-status, approved-by, approved-date, risk-level

5. Verdict:
   APPROVED  → proceed, log in SBOM
   REJECTED  → name specific reason, propose alternative if exists
   DEFERRED  → name what additional info is needed before decision
```

**Zero exceptions.** If a role adds a package without S1 approval: revert, run S1, re-add only after APPROVED.

---

### GATE S2 — FEATURE SECURITY REVIEW (before every commit)

**Trigger:** QA gate passes (all tests green). Before `git commit` is allowed.

**`security_engineer` must execute ALL of the following:**

```
1. SAST (Static Application Security Testing):
   Tool per language:
   - JS/TS:  npx semgrep --config=p/typescript --config=p/owasp-top-ten
   - Python: bandit -r . -ll
   - Go:     gosec ./...
   - Java:   spotbugs / semgrep --config=p/java
   Zero HIGH or CRITICAL findings allowed. MEDIUM findings must be documented in Jira with remediation plan.

2. OWASP Top 10 checklist (per feature — check only what applies):
   A01 Broken Access Control   → auth check on every new endpoint
   A02 Cryptographic Failures  → no plaintext secrets, PII encrypted at rest
   A03 Injection               → parameterized queries only, no string concat in SQL/shell
   A04 Insecure Design         → threat model updated if new trust boundary introduced
   A05 Security Misconfiguration → no debug mode, no default credentials, no open CORS
   A06 Vulnerable Components   → all deps passed S1 gate
   A07 Auth Failures           → session timeout, rate limiting on auth endpoints
   A08 Software Integrity      → no unsigned packages, CI pipeline integrity verified
   A09 Logging Failures        → no PII in logs, security events logged
   A10 SSRF                    → no user-controlled URLs fetched without allowlist

3. Secrets scan (pre-commit hard block — see GATE S3):
   Runs automatically via pre-commit hook. Must be GREEN before S2 review begins.

4. Dependency diff:
   Any new package added since last commit → must have S1 APPROVED status in SBOM.

5. PONYTAIL CHECK — before commit:
   □ Walk the 7-rung ladder for each new function/class added this story
   □ Flag any rung-7 code (new custom implementation) where rung 1-6 applies
   □ Violations: revert to correct rung. Mark with `ponytail:` comment if shortcut has a known ceiling.
   Blocker: any role that skipped rungs 1-6 without justification → reject commit, rewrite at correct rung.

   RUNG DISQUALIFICATION — if a lower rung was skipped due to CVE / license / abandonment (Fix 43B):
   □ Rung Disqualification Record (RDR) must exist — package name, reason, evidence link
   □ Same-rung alternatives must have been checked and ruled out
   □ ADR must exist for any escalation past Rung 2
   □ CVE disqualification → security_engineer sign-off in ADR before DEVELOP started
   Missing RDR or ADR = GATE S2 FAIL (same severity as unjustified rung skip)
   Full protocol: docs/ponytail-rung-disqualification-guide.md

6. Security verdict written to Jira:
   jira.addComment(story_id,
     "SECURITY REVIEW [S2]: PASSED\n" +
     "SAST: clean (semgrep + <tool>)\n" +
     "OWASP: A01✓ A03✓ A06✓ [list all checked]\n" +
     "Secrets: clean (gitleaks)\n" +
     "New deps: <list> — all SBOM APPROVED\n" +
     "Ponytail: PASS — all new code at correct rung\n" +   // (Fix 39A) or: "FAIL — rung violation: <function/class> should use rung <N>: <reason>"
     // If rung escalation occurred: "Ponytail: ESCALATION — Rung N disqualified (<reason>) → Rung M used | RDR: ✅ | ADR: <ADR-XXX> | Security sign-off: ✅" (Fix 43B)
     "Reviewer: security_engineer\n" +
     "Date: <ISO timestamp>"
   )
   If ANY finding: status = FAILED, return to implementing engineer with specific remediation.
```

**Commit is BLOCKED until S2 verdict = PASSED.** No exceptions.

---

### GATE S3 — PRE-COMMIT SECRETS DETECTION (hard block — automated)

**This runs as a git pre-commit hook on every `git commit` attempt. It cannot be bypassed.**

**Setup (DevOps engineer provisions this at project init):**
```bash
# Install gitleaks
brew install gitleaks          # macOS
# or: pip install detect-secrets

# Install pre-commit framework
pip install pre-commit

# .pre-commit-config.yaml (committed to repo root)
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.4
    hooks:
      - id: gitleaks

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-added-large-files    # blocks files > 500KB
      - id: check-merge-conflict
      - id: detect-private-key         # catches PEM/RSA keys

# Activate
pre-commit install
```

**What it blocks:**
- AWS access keys / secret keys
- GitHub tokens (ghp_, ghs_, github_pat_)
- Generic API keys (any 32+ char hex/base58 string in assignment context)
- Private keys (-----BEGIN * PRIVATE KEY-----)
- Database connection strings with credentials
- JWT secrets
- Stripe, Twilio, SendGrid, Slack tokens
- Any pattern matching `password=`, `secret=`, `api_key=` with a value

**If a secret is detected:**
```
COMMIT BLOCKED — secret detected in <file>:<line>
Pattern matched: <type>
Action required:
  1. Remove the secret from the file
  2. Rotate the secret immediately (assume it's compromised)
  3. Add to .gitignore or use environment variables / vault reference
  4. Run: git rm --cached <file> if already staged
  5. Re-commit after removal
DO NOT use --no-verify to bypass this hook.
```

**`--no-verify` is permanently banned.** If a role attempts it: block, escalate to security_engineer, treat as a security incident.

---

### SECURITY ENGINEER BEHAVIORAL CONTRACT

The `security_engineer` does not rubber-stamp. These are hard rules:

- **Never approve a package with a CRITICAL CVE.** No exceptions, no "we'll fix it later."
- **Never approve a package with a recent ownership transfer** (< 6 months) without manual source review.
- **Never pass S2 with a HIGH SAST finding.** Document + remediate first.
- **Any new trust boundary = new threat model entry.** Update `/docs/security/threat-model.md`.
- **Secrets in code = security incident.** Log in `/docs/security/incidents.md`, rotate immediately, inform user.
- **SBOM is updated every sprint.** `/docs/security/sbom.json` reflects all current dependencies + CVE status.
- **Security findings go to Jira immediately** with severity, affected component, remediation steps, and deadline.

---

### SECURITY DOCUMENT OUTPUTS (TW publishes at TRIGGER points)

| Document | Owner | Path | Updated |
|---|---|---|---|
| SBOM | `security_engineer` | `/docs/security/sbom.json` | Every package addition |
| Threat Model | `security_engineer` | `/docs/security/threat-model.md` | Every new trust boundary |
| Security Design Doc | `security_engineer` | `/docs/security/security-design.md` | Post-DESIGN gate |
| Security Incidents Log | `security_engineer` | `/docs/security/incidents.md` | On any incident |
| OWASP Review Log | `security_engineer` | `/docs/security/owasp-reviews.md` | Per sprint |
| Pre-commit config | `devops_engineer` | `.pre-commit-config.yaml` (repo root) | Project init |

---


---

## NON-NEGOTIABLES (violations block the entire pipeline)

1. **ADR for every consequential decision.** No ADR = no decision. Format: ADR-NNN with Context / Decision / Alternatives / Consequences.
2. **CTO tech_strategy is binding.** Every downstream role's choices must trace to it. Contradiction requires a superseding ADR routed back to CTO.
3. **No re-derivation.** A role never re-derives what an upstream role already decided. It reads the artifact and builds on it.
4. **Specificity or silence.** Named vendors, version pins, real RPS numbers, concrete acceptance criteria. "Large market", "fast API", "best practices" without specifics = auto-reject.
5. **Skills loaded per matrix before artifact produced.** Every role loads its targeted skill files from `.kiro/skills/<role>/` using the selection matrix in `.kiro/steering/skill-selection-matrix.md`. Max 3-5 files per activation. This is not optional — but "read all" is banned.
6. **Gate before advance.** Explicit user confirmation required at GATE 1, 2, and 4. GATE 3 is automatic on QA pass.
7. **Git commit = feature done + QA passed.** Never commit before QA gate. Never merge before CI is green.
8. **$TRACKER is the source of truth** for all work items from GATE 2 onward. No work item exists outside $TRACKER. (TRACKER_MODE detected at session start — see orchestrator-routing.md Fix 1)
9. **Lazy senior dev rule (ponytail).** Before writing ANY code, every role walks the ladder: (1) Does this need to exist? (2) Does stdlib do it? (3) Native platform feature? (4) Installed dep? (5) One line? — stop at the first rung that holds. No abstractions not asked for. No new dep if avoidable. Violation = over-engineered output → reject, rewrite at the correct rung. See `kiro/steering/ponytail.md` (always-loaded).
10. **No soft stop conditions (Ralph Wiggum trap).** Every story, task, and agent invocation requires an OBJECTIVE stop condition: tests pass, build green, linter exits 0, type check clean. "Looks good", "seems correct", "mostly passing", "handled enough", "looks reasonable" are NOT stop conditions. A role that declares done without an objective signal → QA must re-open the story. The agent that wrote the code cannot be the agent that declares it done — see Fix 27C (VERIFIER enforcement). If no automated gate exists for a task, the role must SURFACE this to the user and request an explicit human sign-off before marking done.

---

---

## CONFLICT RESOLUTION PROTOCOL (Fix 5)

When two roles produce conflicting outputs (e.g., Architect's design contradicts PM's PRD,
or Security blocks something CTO approved), use this chain. Never silently pick a side.

### ARBITRATION CHAIN

```
1. CTO         → owns: tech stack, build-vs-buy, engineering org, scalability strategy
2. Architect   → owns: system design, service boundaries, data model, API contracts
3. Security    → owns: threat model, auth design, compliance gates, secrets policy
4. User        → final escalation if chain cannot resolve (present both sides, ask explicitly)
```

**Rule:** The role that owns the conflicting domain makes the final call.
If two owned domains conflict (e.g., Architect vs Security), escalate to User — do not guess.

### PROCEDURE

```
Step 1 — Detect conflict: two roles output contradictory constraints or decisions.
Step 2 — Identify domain: which arbitration chain role owns each side?
Step 3 — Higher-chain role wins (CTO > Architect > Security for tech decisions).
          Security > all for security decisions within Security's domain.
Step 4 — File ADR immediately (do not defer to sprint end):
          File: /docs/decisions/ADR-NNN-CONFLICT.md
          Format:
            # ADR-NNN-CONFLICT: [one-line description of the conflict]
            ## Parties: [role A] vs [role B]
            ## Domain owner: [arbitrating role]
            ## Decision: [what was decided]
            ## Rejected alternative: [what was overruled and why]
            ## Impact: [what changes downstream]
Step 5 — Log in $TRACKER: "ADR-NNN-CONFLICT filed — [one-line decision] — see /docs/decisions/ADR-NNN-CONFLICT.md"
Step 6 — Update /docs/decisions/index.md immediately (do not wait for TW trigger).
Step 7 — Continue sprint with the decided direction.
```

### MID-SPRINT CONFLICT (during DEVELOP — Fix 10D)

If a conflict arises mid-sprint (not at a gate):
- File ADR immediately using the procedure above
- DO NOT wait for sprint-end TW trigger to write the index
- senior_engineer or lead role updates index inline
- TW sprint-end trigger only verifies the index, not writes it

### ESCALATION TO USER

Escalate to user when:
- Both roles are at the same chain level and domains genuinely overlap
- The decision has irreversible architectural consequences
- Security and CTO directly contradict on the same decision

Format: "CONFLICT ESCALATION: [Role A] says [X]. [Role B] says [Y]. Domain owner is ambiguous.
Your call — which direction do we take? Decision will be filed as ADR-NNN-CONFLICT."

---

## SUBAGENT ISOLATION MODEL

Each role runs as a **context-isolated subagent** to prevent token bleed across the full team.

**Pattern:**
```
Orchestrator holds: phase state + artifact summaries + gate status
Each role subagent receives: its upstream artifact summaries + its skill files
Each role subagent returns: its artifact (structured output) + any blockers
Orchestrator never loads full role artifacts into main context — summaries only
```

**Blocker escalation:**
- Role cannot complete artifact → surfaces named blocker: `"BLOCKED: <role> needs <specific input> from <upstream role>"`
- Orchestrator routes back to the upstream role to resolve
- Resolution re-triggers the blocked role
- If blocker cannot be resolved → escalate to user with specific question

---

## AGILE ENGINE

- **Sprint length:** 2 weeks (adjust at GATE 2 based on velocity baseline)
- **Ceremonies:** Planning (sprint start) → implicit dailies → Review + Retro (sprint end)
- **Velocity baseline:** Set at GATE 2 from Gantt v1 estimates. Updated after every sprint.
- **Capacity model:** Account for 20% overhead (meetings, reviews, unplanned). Never plan to 100%.
- **Story size:** No story > 8 points. Stories > 8 must be split before sprint planning.
- **Definition of Done (default — override per project at GATE 2):**
  - Code reviewed and merged to main
  - Unit + integration tests passing
  - Contract tests green
  - Deployed to staging
  - Acceptance criteria verified by QA (checker approved — Fix 7)
  - $TRACKER status = Done
  - API docs updated (if applicable)

### SPRINT PARALLELISM (Fix 10C)

Multiple stories can run in parallel lanes within a sprint, up to a maximum of 3 lanes.
Each lane is independent: its own senior_engineer, its own budget counter, its own feature branch.

```
LANE RULES:
- Max 3 parallel lanes per sprint. SM-PLAN sets lane count at sprint planning.
- Each lane has its own Fix 8D read counter — one lane hitting CRITICAL does not block others.
- File conflict detection: before assigning stories to lanes, SM-PLAN checks for overlapping
  files. Stories that touch the same module must be in the same lane (sequential, not parallel).
- Merge step: after all lanes commit, devops_engineer runs merge sequentially:
    git checkout main && git merge --no-ff feature/<lane-1-id>
    git merge --no-ff feature/<lane-2-id>   ← resolve conflicts before this
    git merge --no-ff feature/<lane-3-id>
  If merge conflict → SM-UNBLOCK resolves before proceeding.
- Post-merge regression: qa_engineer runs full test suite after all lanes merge.
  If regression found → identify which lane caused it, re-open that story (SM-UNBLOCK).
- SM-RETRO reports: "Parallelism: N lanes, M merge conflicts — recommendation: [increase/hold/reduce]"
  Adjust lane count for next sprint based on conflict rate.
```

### FEATURE BRANCH LIFECYCLE (Fix 10D)

Every story follows this 4-stage lifecycle. See CLAUDE.md Fix 10D for full detail.

```
STAGE 1 — BRANCH CREATION at story assignment (not at commit time)
  devops_engineer: git checkout main [+ pull if GIT_MODE=REMOTE]
                   git checkout -b feature/<tracker-id>-<slug>
                   [GIT_MODE=REMOTE: git push --set-upstream origin feature/<tracker-id>-<slug>]
  $TRACKER.addComment("Branch created: feature/<tracker-id>-<slug> [GIT_MODE=<mode>]")

STAGE 2 — LOOP EXECUTION on the feature branch (Fix 7 + Fix 10A)
  Every DO step writes to the branch working tree and stages changes (git add).
  No commits during the loop. Staged changes accumulate.

STAGE 3 — CHECKER REVIEW + COMMIT (after maker writes FINAL)
  qa_engineer reviews git diff main..<branch> + AC + loop spec + skill activation summary.
  On approval: git commit → [GIT_MODE=REMOTE: git push] → $TRACKER.transitionIssue("Done")

STAGE 4 — PR + CI + MERGE
  REMOTE_MODE: PR opened → CI runs → lead review → git merge --no-ff → branch deleted
  LOCAL_MODE:  git diff to /docs/reviews/<id>-diff.txt → lead reviews locally →
               local CI run → git merge --no-ff local → branch deleted
```

## QUALITY BARS (role-specific, enforced at artifact review)

| Role | Automatic reject if... |
|---|---|
| market_researcher | Personas paraphrased (not quoted) · TAM without source · SOM > 5% of SAM without named moat |
| cto | Strategic principle is not falsifiable · Build decision without 18-month payback calc · Risk without mitigation |
| product_manager | Goal is feature-shaped · AC uses "fast"/"intuitive" · Story spans FE+BE+infra without split |
| architect | ADR has no rejected alternative · API returns top-level array · No idempotency key on mutating endpoints |
| database_architect | Index not tied to a documented access pattern · Migration is offline on large table · PII without retention policy |
| cloud_architect | No blast-radius analysis · IAM uses wildcard permissions · No cost guardrails |
| security_engineer | Auth decision deferred · No STRIDE per trust boundary · Secrets in environment variables without vault |
| scrum_master | Story > 8 points in sprint · No velocity baseline · DoD not defined |
| qa_engineer | No contract tests · Load test not against architecture targets · Security scan skipped |
| devops_engineer | No rollback plan · IaC not in version control · Deployment has no health check |

---

## SESSION CONTINUITY

At the start of every session involving a product build:
1. Read `.kiro/init_docs/checkpoint.md` — get current phase + resume vector
2. Read `.kiro/init_docs/decisions.md` — load ADR index (binding constraints)
3. Read `.kiro/init_docs/project_map.md` — workspace orientation
4. Announce: `"Resuming [product]. Phase: [X]. Last: [action]. Next: [action]."`

At the end of every session:
- Write checkpoint entry (phase, last artifact, resume vector)
- Update ADR index if any ADRs were created
- Write session handoff seed

---

## WORKSPACE LAYOUT (canonical paths — use these in all instructions)

```
.kiro/
├── skills/<role>/          ← role capability contracts (loaded per skill-selection-matrix)
├── hooks/
│   ├── elite-team-orchestrator.kiro.hook   ← main orchestration trigger
│   ├── 01-token-discipline.kiro.hook       ← Caveman Ultra + Headroom
│   ├── 02-context-discipline.kiro.hook     ← ContentRouter + compaction
│   └── 03-memory-discipline.kiro.hook      ← checkpoint + lessons + ADR index
├── steering/
│   ├── team-orchestrator.md                ← THIS FILE — master constitution
│   ├── skill-selection-matrix.md           ← targeted skill loading per activity
│   ├── orchestrator-routing.md             ← mode detection (always-loaded)
│   └── context-memory-discipline.md        ← token/memory rules (always-loaded)
└── init_docs/
    ├── project_map.md      ← workspace module map
    ├── checkpoint.md       ← session resume vectors
    ├── lessons.md          ← self-improvement rules
    └── decisions.md        ← ADR index
```


---

## DOCUMENT OWNERSHIP & PUBLICATION

Every role writes their domain document as part of their artifact. No role completes its phase without producing its doc. `technical_writer` never writes from scratch — they format, cross-link, and publish what the domain expert produced.

### /docs/ Folder Structure (created by TW at DESIGN gate)

```
/docs/
├── foundation/        ← ONE-TIME strategic docs (created at THINK/DESIGN, never repeated)
│   ├── market-research.md       ← market_researcher (THINK)
│   ├── vision-strategy.md       ← cto (THINK)
│   ├── system-design.md         ← architect (DESIGN)
│   ├── cloud-design.md          ← cloud_architect (DESIGN)
│   ├── erd.md                   ← database_architect (DESIGN)
│   ├── schema.sql               ← database_architect (DESIGN)
│   └── security-design.md       ← security_engineer (DESIGN)
│
├── decisions/         ← ADR index + all ADR files (living, updated any phase)
├── api/               ← OpenAPI spec + generated HTML (living, updated per phase)
├── product/           ← PRD (living doc, updated per phase with new stories)
│
├── phase-N/           ← PER-PHASE execution docs (scoped to that phase's features)
│   ├── prd-phase-N.md           ← product_manager: stories for THIS phase only
│   ├── sprint-plan.md           ← scrum_master: sprints for this phase
│   ├── security-review.md       ← security_engineer: threats for new features
│   ├── test-plan.md             ← qa_engineer: test strategy for phase scope
│   ├── devops.md                ← devops_engineer: deployment changes for phase
│   ├── architecture-delta.md    ← architect: ONLY new/changed components (if any)
│   └── [6 reports at phase end] ← QA, Security, Mapping, Discipline, Jira, Git
│
├── ops/               ← runbooks, deployment guide, SLI/SLO (living)
├── incidents/         ← incident runbooks, post-mortems
└── changelog.md       ← full project changelog (TW owned)
```

### Foundation vs Per-Phase Rule

**Foundation docs** (created ONCE during THINK + DESIGN, referenced thereafter):
- market-research.md — product-level, does not change per phase
- vision-strategy.md — tech stack, build-vs-buy, decided once
- system-design.md — baseline architecture (living doc, addenda allowed)
- cloud-design.md — infrastructure baseline
- erd.md + schema.sql — initial data model
- security-design.md — baseline threat model + auth design

**Per-phase docs** (created fresh for EACH phase, scoped to that phase's features):
- Phase PRD — only user stories being built in this phase
- Sprint plan — only sprints in this phase
- Security review — only new attack surface introduced this phase
- Test plan — only tests for this phase's scope
- DevOps — only CI/CD changes needed for this phase
- Architecture delta — only if new components/services are introduced

**Rule:** If a foundation doc needs updates due to phase work (e.g., new microservice added), create an `architecture-delta.md` in the phase folder AND update the foundation doc with an addendum section. Never recreate the full foundation doc per phase.

---

### Per-Role Document Obligations

Each role MUST produce their document before their phase artifact is considered complete.

**FOUNDATION docs (ONE-TIME at THINK/DESIGN — never repeated per phase):**

| Role | Document | Output path | When |
|---|---|---|---|
| `market_researcher` | Market Research Report | `/docs/foundation/market-research.md` | THINK |
| `cto` | Vision & Strategy Doc | `/docs/foundation/vision-strategy.md` | THINK |
| `architect` | System Design Doc + ADRs | `/docs/foundation/system-design.md` · `/docs/decisions/ADR-NNN.md` | DESIGN |
| `architect` + `backend_lead` | API Contract (OpenAPI spec) | `/docs/api/openapi.yaml` | DESIGN (living) |
| `database_architect` | Data Model / ERD + schema | `/docs/foundation/erd.md` · `/docs/foundation/schema.sql` | DESIGN |
| `cloud_architect` | Cloud Design Doc | `/docs/foundation/cloud-design.md` | DESIGN |
| `security_engineer` | Security Design Doc | `/docs/foundation/security-design.md` · `/docs/decisions/ADR-SEC-NNN.md` | DESIGN |
| `scrum_master` | Product Roadmap (all phases/sprints/features) | `/docs/foundation/roadmap.md` | DESIGN (after GATE 2) |

**PER-PHASE docs (created fresh for EACH phase, scoped to that phase's features):**

| Role | Document | Output path | When |
|---|---|---|---|
| `product_manager` | Phase PRD (stories for this phase) | `/docs/phase-N/prd-phase-N.md` | Phase start |
| `architect` | Architecture Delta (if new components) | `/docs/phase-N/architecture-delta.md` | Phase start (only if needed) |
| `scrum_master` | Sprint Plan | `/docs/phase-N/sprint-plan.md` | Phase start |
| `security_engineer` | Security Review (new attack surface) | `/docs/phase-N/security-review.md` | Per phase |
| `qa_engineer` | Test Plan (for phase scope) | `/docs/phase-N/test-plan.md` | Per phase |
| `devops_engineer` | DevOps / Deployment changes | `/docs/phase-N/devops.md` | Per phase |
| `sre_engineer` | SLI/SLO updates + Runbooks | `/docs/ops/sli-slo.md` (update) | Per sprint |
| `technical_writer` | Changelog + Living Context | `/docs/changelog.md` · `/docs/living-context.md` | Per sprint |

**LIVING docs (updated incrementally, never fully recreated):**

| Doc | Updated when |
|---|---|
| `/docs/api/openapi.yaml` | New/changed endpoints |
| `/docs/decisions/index.md` | New ADR filed |
| `/docs/changelog.md` | Every sprint end |
| `/docs/living-context.md` | Every sprint end |
| `/docs/ops/sli-slo.md` | New services deployed |

---

### TW Trigger Points (three mandatory invocations per product build)

**TRIGGER 1 — After DESIGN gate passes (before DEVELOP starts)**

`technical_writer` receives all DESIGN artifacts and executes:
1. Create `/docs/` folder structure in repo
2. Format + publish: Market Research Report, Vision & Strategy Doc, PRD, System Design Doc, API Contract draft, ERD + schema, Security Design Doc, Cloud Design Doc
3. Generate ADR index at `/docs/decisions/index.md` — link every ADR filed so far
4. Commit: `docs(design): publish DESIGN phase documentation [<JIRA-EPIC>]`

**TRIGGER 2 — After each sprint ends (part of Sprint End sequence)**

`technical_writer` executes after SRE and before Scrum Master retro:
1. Update `/docs/living-context.md` — what changed this sprint, current system state
2. Append to `/docs/changelog.md` — all features shipped this sprint, compiled from commit logs
3. Update `/docs/decisions/index.md` — any new ADRs from this sprint
4. Update `/docs/api/` — delta from any API changes this sprint
5. Publish any new runbooks from `sre_engineer` or `devops_engineer`
6. Archive sprint plan to `/docs/sprints/sprint-N-plan.md`
7. Commit: `docs(sprint-N): update living context, changelog, ADR index [<JIRA-EPIC>]`

**TRIGGER 3 — After RELEASE**

`technical_writer` executes as part of RELEASE phase:
1. Finalize `/docs/living-context.md` — release-state snapshot
2. Publish final `/docs/api/index.html` from final OpenAPI spec
3. Version-stamp `/docs/ops/deployment-guide.md`
4. Publish `/docs/ops/sli-slo.md` with live dashboard links
5. Publish all incident runbooks to `/docs/incidents/`
6. Compile full `/docs/changelog.md` from all sprint changelogs
7. Generate post-mortem template at `/docs/incidents/postmortem-template.md`
8. Archive all sprint plans and retros
9. Commit: `docs(release): publish release documentation [<JIRA-EPIC>]`

---

### Document Quality Bar (enforced by orchestrator at each trigger)

TW artifact is rejected and must be redone if:
- Any doc is missing its section headings (copy-pasted raw artifact = rejected)
- ADR index is missing any ADR filed this phase
- Living Context File doesn't reflect the actual current system state
- Changelog doesn't link to Jira IDs
- API docs don't match the actual deployed OpenAPI spec
- Any doc in `/docs/` has a broken internal cross-link


---

