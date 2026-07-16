# gstack Research & Integration Analysis

> Parked: 2026-07-15 — ongoing reference for Loop Engineering decisions
> Source repo: https://github.com/garrytan/gstack

---

## What Is gstack?

Garry Tan's (President & CEO, Y Combinator) personal Claude Code setup.
**122K stars · 18.2K forks** — one of the most starred AI tooling repos on GitHub.

**Core idea:** A set of 30+ slash commands that each invoke a specialist role — CEO, Eng Manager, Designer, QA Lead, Security Officer, Release Engineer. Works across Claude Code, Kiro, Codex, Cursor, and 7 other agents.

**Install for Kiro:**
```bash
./setup --host kiro
# installs to ~/.kiro/skills/gstack-*/
```

**Philosophy:** Think → Plan → Build → Review → Test → Ship → Reflect. Each skill feeds the next. `/office-hours` writes a design doc that `/plan-ceo-review` reads. `/plan-eng-review` writes a test plan that `/qa` picks up.

**Key quote from README:**
> "I've been building products for twenty years. In the last 60 days: 3 production services, 40+ shipped features, part-time, while running YC full-time. My 2026 run rate is ~810× my 2013 pace."

---

## gstack's 30+ Slash Commands (Full List)

| Command | Specialist | What it does |
|---|---|---|
| `/office-hours` | YC Office Hours | 6 forcing questions that reframe product before writing code |
| `/plan-ceo-review` | CEO / Founder | Rethink the problem. 4 modes: Expansion, Hold Scope, Reduction |
| `/plan-eng-review` | Eng Manager | Lock architecture, data flow, diagrams, edge cases, tests |
| `/plan-design-review` | Senior Designer | Rates each design dimension 0-10, edits plan to get there |
| `/plan-devex-review` | DX Lead | 20-45 forcing questions on developer experience |
| `/design-consultation` | Design Partner | Build complete design system from scratch |
| `/design-shotgun` | Design Explorer | 4-6 AI mockup variants → comparison board → iterate |
| `/design-html` | Design Engineer | Approved mockup → production HTML. 30KB, zero deps |
| `/design-review` | Designer Who Codes | Same as plan-design-review, then fixes what it finds |
| `/review` | Staff Engineer | Find production bugs that pass CI. Auto-fixes obvious ones |
| `/investigate` | Debugger | Root-cause debugging. Iron Law: no fixes without investigation. Stop after 3 fails |
| `/devex-review` | DX Tester | Live onboarding audit. Actually tests your docs |
| `/qa` | QA Lead | Opens real browser, clicks flows, finds bugs, fixes, re-verifies |
| `/qa-only` | QA Reporter | Same as /qa but report only, no code changes |
| `/pair-agent` | Multi-Agent Coordinator | Share browser across multiple AI agents (Claude + OpenClaw + Codex) |
| `/cso` | Chief Security Officer | OWASP Top 10 + STRIDE. 17 false-positive exclusions. 8/10+ confidence gate |
| `/ship` | Release Engineer | Sync main, run tests, audit coverage, push, open PR |
| `/land-and-deploy` | Release Engineer | Merge PR → wait for CI → verify production health |
| `/canary` | SRE | Post-deploy monitoring. Watches for errors, performance regressions |
| `/benchmark` | Performance Engineer | Baseline page load, Core Web Vitals, resource sizes |
| `/document-release` | Technical Writer | Update all docs to match what just shipped |
| `/document-generate` | Documentation Author | Generate missing docs using Diataxis framework |
| `/retro` | Eng Manager | Weekly retro. Per-person breakdown, shipping streaks, test health |
| `/browse` | QA Engineer | Real Chromium browser, real clicks, real screenshots. ~100ms/command |
| `/autoplan` | Review Pipeline | Runs CEO → design → eng review automatically |
| `/spec` | Spec Author | 5-phase spec. Codex quality gate (blocks <7/10) |
| `/learn` | Memory | Manage learnings across sessions. Compounds over time |
| `/make-pdf` | Publisher | Markdown → publication-quality PDF with rendered diagrams |
| `/diagram` | Diagram Maker | English → Mermaid + Excalidraw + SVG/PNG |
| `/codex` | Second Opinion | Independent code review from OpenAI Codex CLI |
| `/careful` | Safety Guardrails | Warns before rm -rf, DROP TABLE, force-push |
| `/freeze` | Edit Lock | Restrict file edits to one directory |
| `/guard` | Full Safety | /careful + /freeze in one command |
| `/unfreeze` | Unlock | Remove /freeze boundary |
| `/context-save` | Checkpoint | WIP commits with structured context body |
| `/context-restore` | Session Resume | Reconstruct session from WIP commits |
| `/skillify` | Skill Creator | Turn anything into a reusable skill |
| `/ios-qa` | iOS QA | Drive real iPhone over USB CoreDevice |

---

## Fundamental Difference: gstack vs Loop Engineering

| Dimension | Loop Engineering (ours) | gstack |
|---|---|---|
| **Trigger** | Hook fires automatically on every prompt | Manual slash commands |
| **Architecture** | 22 agents in sequence, 3 phases | ~30 standalone slash commands |
| **Routing** | 25-signal confidence scoring, auto mode selection | Manual invocation |
| **Gates** | GATE S1 + S2, non-negotiable blockers | No hard gates |
| **Memory** | 5-stage lesson progression, gate_fired_at | Per-session `/learn` + WIP commits |
| **Security** | Cross-tenant test, STRIDE, RBAC enforcement | `/cso` on demand |
| **Ponytail** | 7-rung mandatory discipline | No equivalent |
| **Design** | website_creator subdomain skills | /design-shotgun → /design-html pipeline |
| **Browser** | No execution capability | Real Chromium, Playwright |
| **Team** | 22 specialists in coordinated pipeline | 1 specialist per command |

**Core conflict:** Our hook intercepts every `promptSubmit` — including when you type `/office-hours` or `/review`. Our orchestrator always runs first. gstack's planning layer and our orchestration layer fight for the same slot.

---

## The Core Integration Question

**Can gstack slash commands be invoked from within our orchestration?**

Yes — in Kiro, if gstack is installed at `~/.kiro/skills/`, slash commands are available. When our agent's skill file says "invoke `/qa <url>`", Kiro resolves the gstack skill and executes it. Our orchestrator routes to it; gstack executes it.

**The right mental model:**
```
Our system = Orchestration + Planning layer
gstack     = Execution tooling layer
```

They can coexist if we treat gstack as a tool provider, not a competing orchestrator.

---

## What gstack Adds to Our System — Full Analysis

### ✅ Genuinely Additive (we lack this entirely)

**1. Real Browser Automation (`/qa`, `/browse`)**
- Our `qa_engineer` writes test plans and testing-strategy.md
- It CANNOT click anything, open a URL, screenshot a page, or detect runtime errors
- gstack opens real Chromium (anti-bot stealth), navigates, clicks, finds bugs, fixes with atomic commits, re-verifies
- This is the BIGGEST capability gap — our qa_engineer is a test architect, not a test executor
- Classification: **Execution capability — needs actual tooling, not just skill file content**

**2. Edit Scope Locking (`/careful`, `/freeze`, `/guard`)**
- Our GUARD 2 blocks bad-loop domain + verb combinations
- Nothing in our system prevents accidental writes OUTSIDE the current debug scope
- `/freeze` = restrict all edits to one directory. `/careful` = warn before destructive commands (rm -rf, DROP TABLE, force-push)
- Classification: **Behavioral constraint — can be added to session-guards.md as a new GUARD 3**

**3. Debugging Iron Law (3-failed-fixes stop rule)**
- Our `shared/debugging_methodology.md` exists but has no hard stop protocol
- gstack's investigate rule: no fix without root-cause investigation → trace data flow → test hypothesis → stop and report after 3 consecutive failures
- Classification: **Behavioral rule — can be added to shared/debugging_methodology.md directly**

**4. Diagram Rendering (`/diagram`)**
- Our `technical_writer` describes diagrams in prose
- gstack generates: Mermaid source + `.excalidraw` file + rendered SVG/PNG
- Mermaid syntax generation: can be added to technical_writer skill file NOW (pure prompt)
- SVG/PNG rendering: needs Mermaid CLI tool
- Classification: **Split — Mermaid syntax = pure skill content; rendering = needs tool**

**5. PDF Generation (`/make-pdf`)**
- Our dry run reports, docs, and outputs are all markdown
- gstack converts Markdown → publication-quality PDF with rendered diagrams, proper page layout
- Classification: **Execution capability — needs PDF tool or gstack `/make-pdf`**

---

### ❌ Conflicts / Redundant (we already do this better)

| gstack skill | Why redundant with our system |
|---|---|
| `/office-hours`, `/plan-ceo-review` | We have `market_researcher` + `cto` in THINK phase, enforced by hook |
| `/plan-eng-review` | We have `architect` + `database_architect` + `cloud_architect` in DESIGN phase |
| `/autoplan` | Our hook IS autoplan — it routes automatically |
| `/retro` | SM-RETRO + comprehension debt + lessons.md covers this |
| `/spec` | PRD template + TRD template + SM-PLAN gate covers this |
| `/review` | `qa_engineer` + GATE S2 covers this |
| `/ship` | `devops_engineer` + SM-PLAN sprint execution covers this |
| `/cso` | `security_engineer` with STRIDE, OWASP, GATE S1 is more integrated |
| `/learn` | lessons.md + 5-stage memory progression covers this |

---

## Implementation Options for Browser Automation

The biggest gap. Three architectural choices:

**Option A — Depend on gstack**
Install gstack at `~/.kiro/skills/`. `qa_engineer` skill file says: "if gstack available, invoke `/qa <url>`."
- Pro: battle-tested, anti-bot stealth, 122K stars
- Con: external dependency, version drift risk

**Option B — Add Playwright MCP**
Install a Playwright MCP directly into Kiro. `qa_engineer` gets native `browser_navigate()`, `browser_click()`, `browser_screenshot()` tools.
- Pro: no gstack dependency, agents own the full capability
- Con: more setup work, need to find/maintain the MCP

**Option C — Conditional referencing (recommended)**
Update skill files to be tool-aware but not tool-dependent:
- If Playwright MCP available → use it natively
- If gstack installed → invoke `/qa <url>`
- If neither → produce structured test plan document for human execution

Agents degrade gracefully. Environment determines what's possible.

---

## Implementation Plan (When Ready)

### Phase 1 — Pure behavioral additions (no tooling, do now)

**Fix 44B: Debugging Iron Law → `shared/debugging_methodology.md`**
```
IRON LAW:
1. No fix without investigation first. Reproduce → isolate → hypothesize → verify.
2. After 3 consecutive failed fixes: STOP. Do not attempt Fix 4.
3. Write investigation report: what was tried, what failed, current hypothesis.
4. Present to user with explicit ask: "Need more context before proceeding."
```

**Fix 44C: Edit Scope Lock → `session-guards.md` as GUARD 3**
```
GUARD 3 — SCOPE LOCK (fires when debugging)
When agent is in a debug loop on a specific file/directory:
- Warn before modifying files outside that directory
- Require explicit user confirmation for out-of-scope writes
- Block rm -rf, DROP TABLE, git push --force without explicit confirmation
```

**Fix 44D: Mermaid syntax generation → `technical_writer` skill addition**
```
DIAGRAM PROTOCOL:
When producing architecture docs, data flow docs, or sequence diagrams:
1. Always emit Mermaid source alongside prose description
2. Wrap in ```mermaid code fence
3. Include entity relationships, sequence flows, and state machines in Mermaid
4. Label: "Render at mermaid.live or with Mermaid CLI"
```

### Phase 2 — Tooling-dependent additions (decide on Option A/B/C first)

**Fix 44E: QA Executor layer**
New concept — separate from qa_engineer (planner). The QA Executor:
- Runs AFTER code is written
- Activates on staging URL
- Uses browser tooling (gstack /qa OR Playwright MCP)
- Wired into GATE S2 as a mandatory step for E2E-REQUIRED stories

**Fix 44F: PDF output for dry runs and reports**
- Currently: dry run reports saved as .md
- With fix: `technical_writer` produces PDF at sprint close
- Needs: gstack `/make-pdf` OR pdf tool

### Phase 3 — gstack partial install (optional)

If choosing Option A for browser + PDF:
```bash
./setup --host kiro
# installs only: /browse, /qa, /make-pdf, /diagram, /careful, /freeze
# do NOT install: /office-hours, /plan-*, /review, /ship, /retro
# (these conflict with our orchestrator)
```

---

## Sequencing by Daily Impact

```
High daily impact (every coding session):
1. Debugging Iron Law          → shared/debugging_methodology.md   [Fix 44B]
2. Edit scope lock             → session-guards.md                 [Fix 44C]
3. Mermaid syntax generation   → technical_writer skill file       [Fix 44D]

Medium daily impact (every sprint):
4. QA Executor layer           → new qa_executor concept           [Fix 44E]
5. PDF report generation       → technical_writer + tool           [Fix 44F]

Lower frequency (post-deploy only):
6. Real browser QA             → tooling decision required         [Fix 44E]
```

---

## Current qa_engineer Capability Audit

**What qa_engineer DOES today (planning/specification):**
- Produces `testing-strategy.md` — mandatory GATE 2 artifact (8 sections)
- Declares test pyramid: which levels active, which framework, coverage targets
- Selects tools per category: one tool, no ambiguity
- Defines test data strategy (factory vs fixtures, docker containers)
- Lists critical user journeys for E2E scope (keeps E2E focused)
- Writes Done Definition per story type (STANDARD, SECURITY-CRITICAL, E2E-REQUIRED, LOAD-REQUIRED)
- Sets accessibility standard (WCAG level, axe-core in CI)
- Defines security testing in CI (semgrep, secret scanning, dependency scanning)
- Also loads: contract testing specs, load test design, mutation testing strategy, property-based test design, visual regression setup, test data management, exploratory testing charters

**What qa_engineer CANNOT do (execution):**
- Run `jest`, `pytest`, or any test command
- Open a browser or navigate a URL
- Click UI elements or observe what happens
- Screenshot a broken layout
- Detect runtime errors or 500s
- Execute k6 load tests against a real endpoint
- Verify whether Playwright tests actually pass

**Conclusion:** qa_engineer is a **test architect**, not a **test executor**. The two responsibilities should remain separate. A new QA Executor layer (gstack /qa or Playwright MCP) slots in after qa_engineer's planning is complete, without changing the existing qa_engineer structure.

---

## Decision Log

| Decision | Status | Notes |
|---|---|---|
| Port Debugging Iron Law | ✅ Agreed | Pure behavioral, add to shared/debugging_methodology.md |
| Port Edit Scope Lock | ✅ Agreed | Add to session-guards.md as GUARD 3 |
| Port Mermaid syntax | ✅ Agreed | Add to technical_writer skill |
| Browser automation approach | 🔲 Pending | Option A (gstack) vs B (Playwright MCP) vs C (conditional) |
| PDF generation approach | 🔲 Pending | Same tooling decision as browser |
| Keep qa_engineer as planner only | ✅ Agreed | Don't merge planning + execution |
| QA Executor as separate concept | ✅ Agreed | New layer, activates post-build on staging URL |
| Don't install gstack's planning skills | ✅ Agreed | Conflicts with our hook orchestration |
