# 🔁 Loop Engineering — Kiro AI Orchestration System

<div align="center">

[![GitHub](https://img.shields.io/badge/GitHub-supersaiyane%2FloopEngineering-181717?style=for-the-badge&logo=github)](https://github.com/supersaiyane/loopEngineering)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen?style=for-the-badge)
![Phase](https://img.shields.io/badge/phase%201-complete%20%E2%9C%85-brightgreen?style=for-the-badge)
![Dry Runs](https://img.shields.io/badge/dry%20runs-v11-blue?style=for-the-badge)
![Ship Confidence](https://img.shields.io/badge/ship%20confidence-9.5%2F10-success?style=for-the-badge)
![Fixes](https://img.shields.io/badge/fixes%20implemented-Fix%201--47D-orange?style=for-the-badge)
![Roles](https://img.shields.io/badge/agent%20roles-22-purple?style=for-the-badge)
![Skill Files](https://img.shields.io/badge/skill%20files-173%20wired-informational?style=for-the-badge)
![pxpipe](https://img.shields.io/badge/pxpipe-token%20compression%20%E2%88%9260%25-ff6b35?style=for-the-badge)
![White Paper](https://img.shields.io/badge/white%20paper-v5%20published-blueviolet?style=for-the-badge)

</div>

---

> **Who this README is for:** Someone who has never seen this project before.
> No prior knowledge of Kiro, AI agents, or orchestration systems is assumed.

---

## 📖 Table of Contents

1. [What Is This Project?](#-what-is-this-project)
2. [The Problem It Solves](#-the-problem-it-solves)
3. [How Kiro Works (Background)](#-how-kiro-works-background)
4. [System Architecture](#-system-architecture)
5. [The 5 Execution Modes](#-the-5-execution-modes)
6. [The 22 Agent Roles](#-the-22-agent-roles)
7. [Key Concepts Explained](#-key-concepts-explained)
8. [File Structure](#-file-structure)
9. [Steering Files — What Each One Does](#-steering-files--what-each-one-does)
10. [Quality Gates & Guards](#-quality-gates--guards)
11. [⚡ Setup & Usage — Kiro, Claude, ChatGPT](#-setup--usage--kiro-claude-chatgpt)
12. [🗜️ Token Compression — pxpipe](#️-token-compression--pxpipe)
13. [The Fix Register — What Was Built](#-the-fix-register--what-was-built)
14. [Dry Run History](#-dry-run-history)
15. [R&D Research Files](#-rd-research-files)
16. [Roadmap](#-roadmap)
17. [Glossary](#-glossary)

---

## 🤔 What Is This Project?

> **The context:** By mid-2026, frontier AI coding agents score ~88% on SWE-bench benchmarks but fail in **70–95% of production deployments**. Only 14% of enterprise AI pilots ever reach org-wide scale. The gap is not model capability — it's process architecture. No production-validated framework for sustained, multi-session LLM coding agents existed in the literature. Loop Engineering is the first.

**Loop Engineering** is a system of rules, files, and protocols that tells the **Kiro AI IDE** how to behave like a structured engineering team — instead of just answering prompts one at a time.

Think of it as **a constitution for an AI development team.** When you type a prompt into Kiro, this system decides:

- What kind of task is this? (bug fix, new feature, quick question?)
- Which AI agents should work on it? (just one? a full team of 22?)
- What quality checks must pass before any code is merged?
- How should agents remember past mistakes?

Without this system, Kiro answers each prompt independently — like a contractor who shows up fresh every day with no memory of yesterday. **With this system**, Kiro behaves like a senior engineering org with sprint planning, code reviews, security gates, and institutional memory.

---

## 🎯 The Problem It Solves

The production reliability crisis in agentic AI systems is real and documented. Frontier models are capable. The process architectures are not. Loop Engineering is the process layer that closes the gap.

| Problem Without This System | How This System Fixes It |
|-----------------------------|--------------------------|
| Kiro re-invents solutions it already wrote | Memory system + lessons.md compounds knowledge across sessions |
| Kiro launches 19 agents for a simple bug fix | Discovery engine scores your request and picks the right-sized team |
| Agents write 200-line custom code when a library already exists | Ponytail ladder enforces "use existing before building new" |
| A security flaw passes code review because coverage % looked fine | GATE S2 forces explicit cross-tenant isolation tests on auth stories |
| One AI agent can unilaterally restructure your entire auth system | Bad-loop guard requires human confirmation for high-risk operations |
| Team forgets architectural decisions by sprint 3 | ADR (Architecture Decision Records) + steering files persist decisions |
| AI agents guess at which tools/skills to use | Skill selection matrix maps every story label to the exact skill files |

---

## ⚙️ How Kiro Works (Background)

> **New to Kiro?** Here's the minimum you need to know.

[Kiro](https://kiro.dev) is an AI-powered IDE. When you write a prompt, Kiro can:
- Read files in your project
- Write and edit code
- Activate specialized AI agents for different tasks
- Load "steering files" that shape how it behaves

The `.kiro/` folder (or `kiro/` in this repo) is where Kiro looks for its configuration. This project fills that folder with a structured orchestration system.

```
You type a prompt
       ↓
Kiro reads the .kiro/hooks/ file first  ← this is the entry point
       ↓
Hook decides what kind of task it is
       ↓
Hook loads the right steering files
       ↓
Steering files activate the right agents with the right skill files
       ↓
Agents do the work → quality gates run → code merges
```

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    YOUR PROMPT                          │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│         HOOK  (elite-team-orchestrator.kiro.hook)       │
│  ≤60 lines · thin router · reads ENV, classifies task   │
│                                                         │
│  STEP 0: Is this trivial? → Mode 3 (direct answer)     │
│  STEP 1: Detect environment (Jira/Linear/markdown)      │
│  STEP 2: BUILD or MAINTAIN?                             │
│  STEP 3: Confidence scoring → Mode 1/2/3/4/5            │
│  STEP 4: Low confidence? → Discovery Engine             │
│  STEP 5: Load steering files                            │
│  STEP 6: Activate agents                                │
└─────────────────────┬───────────────────────────────────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
   ┌──────────┐ ┌──────────┐ ┌──────────┐
   │STEERING  │ │  SKILL   │ │  GUARDS  │
   │  FILES   │ │  FILES   │ │& GATES   │
   │(14 files)│ │(173 wired│ │(GATE S1  │
   │          │ │ 22 roles)│ │ GATE S2) │
   └──────────┘ └──────────┘ └──────────┘
          │           │           │
          └───────────┼───────────┘
                      ▼
          ┌─────────────────────┐
          │   AGENT EXECUTION   │
          │  PLAN→DO→VERIFY     │
          │     →DECIDE         │
          └──────────┬──────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │   SM-RETRO + MEMORY │
          │  lessons.md updates │
          │  checkpoint.md      │
          └─────────────────────┘
```

---

## 🎭 The 5 Execution Modes

The system picks one of 5 modes based on how complex your request is.

| Mode | Name | When Used | Agents Activated |
|------|------|-----------|-----------------|
| **Mode 1** | 🏰 Full Army | Large platform, enterprise, multi-service | All 22 roles |
| **Mode 2** | 🎯 Targeted | Single service, clear scope | 3–8 matched roles |
| **Mode 3** | ⚡ Direct | Bug fix, trivial task, quick question | 1 role or none |
| **Mode 4** | 🔬 Research | Technical evaluation, spike, ADR | CTO + Architect + Researcher |
| **Mode 5** | 🌱 Lean | MVP, startup, solo dev, small team | 3 core roles (lite) |

### How the Mode is Chosen

```
Your prompt → signal scan (25 keywords) → confidence score

≥3 signals + single sentence + clear scope  →  HIGH (95%)  →  Mode 1 auto
2 signals  + single sentence + clear scope  →  MEDIUM (75%) →  PAUSE + confirm
2 signals  + scope unclear                  →  LOW (55%)   →  Discovery Engine
0–1 signals                                 →  LOW (55%)   →  Discovery Engine
```

> **MEDIUM confidence:** The system **stops and asks you** — "Is this a full platform (Mode 1) or a single microservice (Mode 2)?" It never guesses wrong when the stakes are high.

---

## 👥 The 22 Agent Roles

Each role has its own `SKILL.md` and a library of specialist skill files.

| # | Role | What They Do | Skill Files |
|---|------|-------------|-------------|
| 1 | 🧠 **CTO** | Tech strategy, stack selection, build-vs-buy decisions | 10 |
| 2 | 📐 **Architect** | System design, ADRs, threat modeling | 13 |
| 3 | 🗄️ **Database Architect** | Schema design, query optimization, migrations | 8 |
| 4 | ☁️ **Cloud Architect** | AWS/GCP/Azure infrastructure, VPC, IAM | 10 |
| 5 | 💰 **FinOps Architect** | Cloud cost optimization, budget alerts | 5 |
| 6 | 🔒 **Security Engineer** | OWASP, CVE scanning, pentesting, compliance | 12 |
| 7 | 🎯 **Product Manager** | PRD, user stories, acceptance criteria | 6 |
| 8 | 🔄 **Scrum Master** | Sprint planning, gates, retrospectives | 5 |
| 9 | 🖥️ **Backend Lead** | API design, microservices, database patterns | 14 |
| 10 | 🎨 **Frontend Lead** | Component architecture, design systems | 10 |
| 11 | ⚙️ **Senior Engineer BE** | Backend implementation, code quality | 8 |
| 12 | 🖌️ **Senior Engineer FE** | Frontend implementation, accessibility | 8 |
| 13 | 📱 **Mobile Engineer** | iOS/Android, React Native, App Store rules | 7 |
| 14 | 🚀 **DevOps Engineer** | CI/CD pipelines, Docker, Kubernetes | 9 |
| 15 | 🛡️ **SRE Engineer** | Reliability, SLOs, incident response | 8 |
| 16 | 🤖 **ML Engineer** | Model serving, embeddings, ML pipelines | 9 |
| 17 | 📊 **Data Engineer** | Kafka, Spark, dbt, data pipelines | 7 |
| 18 | 🔬 **Data Scientist** | A/B testing, cohort analysis, EDA | 6 |
| 19 | 🧪 **QA Engineer** | Test strategy, automation, coverage | 8 |
| 20 | ✍️ **Technical Writer** | Documentation, runbooks, app flow docs | 6 |
| 21 | 📣 **Market Researcher** | Competitor analysis, market positioning | 4 |
| 22 | 🌐 **Website Creator** | Landing pages, SEO, web content | 6 |

> **173 total skill files** across all roles, fully wired (Fix 47A-D) — each one is a focused protocol for a specific engineering task.

---

## 💡 Key Concepts Explained

### 🪢 The Ponytail Ladder

> **Problem:** AI agents love writing custom code. They'll build a 300-line auth system when `passport.js` already exists. This wastes time and creates maintenance debt.

The Ponytail system enforces a **7-rung ladder** — agents must use the lowest possible rung before moving higher.

```
Rung 1 → Use the standard library (built-in language features)
Rung 2 → Use an installed dependency (existing package)
Rung 3 → Use a configuration file (environment variable, config)
Rung 4 → Use an existing tool/CLI
Rung 5 → Compose existing services (API calls, wrappers)
Rung 6 → Fork an existing open-source project
Rung 7 → Write custom code from scratch ← LAST RESORT ONLY
```

If a rung is disqualified (e.g., a CVE vulnerability in a package), agents must write a **Rung Disqualification Record (RDR)** and check for a same-rung alternative before moving up. See [`docs/ponytail-rung-disqualification-guide.md`](docs/ponytail-rung-disqualification-guide.md).

---

### 🔍 The Discovery Engine

When your request is ambiguous (low confidence), instead of guessing wrong, the system asks 7 structured questions:

```
1. PLATFORM     — Web / Mobile / Desktop / CLI / Library?
2. SCALE        — Just you / Small team / Public product / SaaS?
3. COMPLEXITY   — Simple / Medium / Complex / Enterprise?
4. DEPLOYMENT   — Local / Single server / Cloud managed / Multi-region?
5. REVENUE      — None / Ads / One-time / Subscription / Enterprise?
6. DESIGN & UX  — None / Basic / Polished / Branded?
7. SECURITY     — Minimal / Basic auth / User data / Regulated?
```

Score 0–21 → maps to a mode:

| Score | Tier | Mode |
|-------|------|------|
| 0–4 | Micro | Mode 5 (Lean) |
| 5–9 | Lean | Mode 5 (Lean) |
| 10–14 | Standard | Mode 2 (Targeted) |
| 15–18 | Full | Mode 1 (Full Army) |
| 19–21 | Enterprise | Mode 1 (Full Army + extras) |

---

### 🛡️ Bad Loop Guard (GUARD 2)

> **Problem:** AI agents can get excited and propose restructuring your entire database schema mid-sprint. This is dangerous.

The bad loop guard blocks agents from self-declaring high-risk scope changes. It fires when **both** a domain keyword AND a high-risk verb appear together:

```
Domain keywords:  auth / payments / billing / database / production / security
High-risk verbs:  redesign / restructure / rewrite / replace / refactor / migrate

auth + refactor  →  BLOCKED (requires human confirmation)
deploy           →  BLOCKED (self-triggering, no verb needed)
auth + implement →  ALLOWED (implement is not high-risk)
```

---

### 🧠 The Memory System (5-Stage Progression)

Lessons don't just get written — they must graduate through 5 stages before becoming rules:

```
Stage 1 — FAIL      → Document the failure in detail
Stage 2 — INVESTIGATE → Find the root cause (the WHY, not just the WHAT)
Stage 3 — VERIFY    → Confirm with actual evidence (not a feeling)
Stage 4 — DISTILL   → Write a general rule that applies beyond this case
Stage 5 — CONSULT   → Read this entry BEFORE starting the next related task
```

> A lesson stuck at Stage 1-Fail for more than 1 sprint is a **stale blocker** — the system flags it and can block Sprint N+1 until resolved.

---

### 📋 Comprehension Debt Gate

At the end of every sprint, the Scrum Master runs a 4-question binary check (yes/no only):

```
□ Did every agent read the full diff before approving it?
□ Did VERIFIER produce evidence (test output / logs) — not just "looks good"?
□ Were all architectural constraints re-confirmed at session start?
□ Were any "mostly working" or "looks fine" close conditions present?
```

`0/4` failures = **CRITICAL** → Sprint is blocked. No new stories until debt is cleared.

---

## 📁 File Structure

```
loopEngineering/
│
├── 📄 README.md                    ← You are here
├── 🔗 .kiro → kiro/                ← Symlink: Kiro reads from here
│
├── 📂 kiro/                        ← All orchestration files live here
│   │
│   ├── 📂 hooks/
│   │   └── elite-team-orchestrator.kiro.hook  ← Entry point (≤60 lines)
│   │
│   ├── 📂 steering/                ← The constitution (14 files)
│   │   ├── orchestrator-routing.md      ← Mode routing + phase/event auto-triggers (Fix 47B)
│   │   ├── team-orchestrator-core.md    ← Core execution rules
│   │   ├── team-orchestrator-sprint.md  ← Sprint lifecycle + GATE 5 graph merge (Fix 46A)
│   │   ├── team-orchestrator-rules.md   ← NON-NEGOTIABLES + GATE S1/S2
│   │   ├── discovery-engine.md          ← 7-question discovery + scoring
│   │   ├── ponytail.md                  ← 7-rung ladder enforcement
│   │   ├── session-guards.md            ← GUARD 1 + GUARD 2 + GUARD 3 (pxpipe)
│   │   ├── skill-selection-matrix.md    ← Story label → skill file mapping (119 rows, Fix 47C/D)
│   │   ├── skill-label-index.md         ← 173 skill files indexed across 22 roles (Fix 47A)
│   │   ├── loop-engine.md               ← PLAN→DO→VERIFY→DECIDE loop spec
│   │   ├── context-memory-discipline.md ← Token budgets + degradation tiers
│   │   ├── memory-management.md         ← Cross-session memory protocols
│   │   ├── phase-reporting.md           ← Report templates per phase
│   │   └── team-orchestrator.md         ← Legacy (superseded by split files)
│   │
│   ├── 📂 memory/                  ← Runtime state (live session files)
│   │   ├── checkpoint.md           ← Session continuity (resume from here)
│   │   ├── lessons.md              ← Cross-session learning log
│   │   ├── decisions.md            ← Architectural decisions
│   │   ├── project_map.md          ← Module-level map of the whole system
│   │   └── flow.md                 ← End-to-end system flow reference
│   │
│   ├── 📂 skills/                  ← 22 agent roles, 173 wired skill files
│   │   ├── cto/                    ← CTO skill library
│   │   ├── architect/              ← Architect skills + product_graph_update.md (Fix 46A)
│   │   ├── security_engineer/      ← Security skills
│   │   ├── backend_lead/           ← Backend skills
│   │   ├── ... (18 more roles)
│   │   └── shared/                 ← Cross-role shared skills + graph_patch_emit.md (Fix 46A)
│   │
│   ├── 📄 CLAUDE.md               ← Active fix register + pxpipe note
│   └── 📄 CLAUDE-implemented.md   ← Full history: Fix 1–47D
│
├── 📂 scripts/                     ← Utility scripts
│   └── start-kiro-pxpipe.sh        ← Launch Kiro through pxpipe proxy (run this)
│
├── 📄 gstack-research.md           ← R&D: gstack vs Loop Engineering analysis
├── 📄 pxpipe-research.md           ← R&D: pxpipe token compression assessment
├── 📄 oneagent-search.md           ← R&D: 67TB logs/metrics/traces search architecture
│
└── 📂 docs/                        ← Evidence, decisions, artifacts
    ├── product-graph.yaml          ← Living product knowledge graph (Fix 46A)
    ├── product-graph.html          ← D3 interactive graph viz, updated each GATE 5 (Fix 46A)
    ├── ponytail-rung-disqualification-guide.md  ← Dep disqualification protocol
    ├── dry-run-*.md                ← 11 full pipeline verification runs
    ├── Audits/
    │   └── external-validator-outreach.md  ← R1: HN/Reddit/LinkedIn/Discord posts (R1)
    └── research/
        ├── compression-fidelity-methodology.md  ← Fix 45B: exact test methodology
        └── competitor-comparison.md             ← Fix 45C: MemGPT, LangMem, Devin comparison
```

---

## 📜 Steering Files — What Each One Does

| File | Inclusion | Purpose |
|------|-----------|---------|
| `orchestrator-routing.md` | On demand | Mode detection + routing logic (Modes 1–5) |
| `team-orchestrator-core.md` | On demand | Core execution rules, role handoffs, NON-NEGOTIABLES |
| `team-orchestrator-sprint.md` | On demand | Sprint lifecycle: SM-PLAN → DEVELOP → SM-GATE → SM-RETRO |
| `team-orchestrator-rules.md` | On demand | GATE S1 (security) + GATE S2 (PR review) checklists |
| `discovery-engine.md` | On demand | 7 discovery questions → score → mode recommendation |
| `ponytail.md` | **Always** | 7-rung ladder — loaded before any agent fires |
| `session-guards.md` | **Always** | GUARD 1 (constraint drift) + GUARD 2 (bad loop) + GUARD 3 (pxpipe image context) |
| `skill-selection-matrix.md` | On demand | Maps story labels → exact skill files to load |
| `skill-label-index.md` | On demand | Filename index for all 254 skill files |
| `loop-engine.md` | On demand | PLAN→DO→VERIFY→DECIDE loop specification |
| `context-memory-discipline.md` | On demand | Token budgets, degradation tiers (PEAK→CRITICAL) |
| `memory-management.md` | On demand | How to write, promote, and expire lessons |
| `phase-reporting.md` | On demand | Report format templates for each sprint phase |

> **Always loaded** = present in every session, even Mode 3 (trivial). Everything else loads on demand.

---

## 🚪 Quality Gates & Guards

### GATE S1 — Security Pre-Check (before DEVELOP)

Runs **before** development starts. Blocks stories with security implications until reviewed.

```
□ OWASP Top 10 threat model completed
□ IAM/auth scope estimated (IAM stories routinely run 1.5–2× estimate — warned here)
□ CVE scan on new dependencies → if CVE found, RDR required + same-rung alt check
□ Secrets/credentials not hardcoded
□ Compliance scope confirmed (GDPR, PCI-DSS, SOC2, HIPAA as applicable)
```

### GATE S2 — PR Review (before merge)

Runs **before** any code merges to main.

```
□ SAST scan clean (e.g., gosec, semgrep)
□ OWASP A01 (Broken Access Control) + A07 (Identification Failures) checked
□ Secrets scan clean (e.g., gitleaks)
□ New dependencies reviewed (Ponytail rung documented)
□ PONYTAIL CHECK: lowest qualifying rung used? RDR if disqualified?
   └─ If story tagged security/rbac OR data/multi-tenant:
      → At least 1 explicit cross-tenant access-DENIAL test REQUIRED
      → Absence = GATE S2 FAIL regardless of coverage %
□ Jira comment written with: SAST / OWASP / Secrets / Deps / Ponytail verdict
```

### GUARD 1 — Constraint Drift

Re-reads all binding constraints at **every session start**. Prevents the model from forgetting "we don't use Redis" by turn 47.

### GUARD 2 — Bad Loop Detection

Blocks agents from self-escalating scope without human approval. Fires on high-risk domain + verb combinations. See [Key Concepts](#-key-concepts-explained) above.

### GUARD 3 — pxpipe Image Context (Fix 44G)

When the pxpipe token-compression proxy is active, old history turns are stored as PNG images. The model reads them at gist-level accuracy (decisions, paths, values = **98/98 lossless**) but NOT at byte-exact level — ~13% silent misread rate on exact strings.

GUARD 3 tells every agent: never recall exact strings from image context — always re-fetch from the canonical source.

```
BLOCKED from image recall:  git SHAs · file:line refs · camelCase identifiers
                             exact error codes · checkpoint timestamps

SAFE from image recall:     decisions made · file names · architecture intent
                             status summaries · counts and relative values
```

See [Token Compression — pxpipe](#️-token-compression--pxpipe) for full setup.

---

## ⚡ Setup & Usage — Kiro, Claude, ChatGPT

This system runs on **three platforms**. Pick the one you use.

---

### 🟣 PLATFORM 1 — Kiro IDE (Native)

> **This is the primary platform.** The `.kiro/` folder and hook were built specifically for Kiro.

#### Why Kiro sometimes reverts to its native behavior

Kiro has a built-in "Build a Feature" dialog and spec-driven workflow (`.kiro/specs/`). Without explicit suppression, Kiro ignores the orchestration hook and falls back to its own defaults — asking "Is this a new feature or a bug fix?" and creating files you didn't ask for.

**The fix is already baked into the hook** — it starts with a `SYSTEM AUTHORITY` block that explicitly disables all Kiro native behaviors. But the symlink must exist for the hook to load correctly.

#### Step 1 — Clone the repo into your project

```bash
# Inside your project root (where you open Kiro):
git clone https://github.com/supersaiyane/loopEngineering.git
cd loopEngineering
```

#### Step 2 — Create the `.kiro` symlink (CRITICAL)

Kiro reads from `.kiro/` at the project root. This repo stores everything in `kiro/`. The symlink bridges them:

```bash
# Run this from the loopEngineering directory:
ln -s kiro .kiro
```

Verify it worked:
```bash
ls -la .kiro          # should show → kiro
ls .kiro/hooks/       # should show elite-team-orchestrator.kiro.hook
ls .kiro/steering/    # should show all 14 steering files
```

> ⚠️ **If `.kiro` already exists** in your project, remove it first: `rm -rf .kiro` then re-create the symlink.

#### Step 3 — Open the project in Kiro

Open the `loopEngineering/` folder in Kiro. The hook loads automatically on every prompt via `promptSubmit` event — no manual activation needed.

#### Step 4 — Verify the hook is active

Type any prompt and look for this log line at the start of the response:
```
[ENV] TRACKER_MODE=markdown | GIT_MODE=LOCAL
```
If you see this → the hook is active. ✅

If you **don't** see it → the symlink is broken. Re-run Step 2.

#### Step 5 — Start your first build

```
Build me a SaaS billing platform with Stripe integration
```

The system will:
1. Score signals → HIGH confidence → Mode 1 selected
2. Log `[MODE: 1 auto-inferred | confidence=HIGH]`
3. Activate the full 22-agent pipeline
4. Start with Think phase (Market Researcher + CTO)

#### 🚨 Troubleshooting — Kiro Reverting to Native Behavior

| Symptom | Root cause | Fix |
|---------|-----------|-----|
| Kiro asks "New feature or bug fix?" | Hook not loading — symlink missing | Run `ln -s kiro .kiro` from project root |
| Kiro creates `.kiro/specs/` folder | Hook loaded but SYSTEM AUTHORITY ignored | Check hook file exists at `.kiro/hooks/elite-team-orchestrator.kiro.hook` |
| Steering files "not found" errors | Kiro can't resolve `kiro/steering/` paths | Verify symlink: `ls -la .kiro` → should say `kiro` |
| Hook fires but uses wrong mode | Signal count below threshold | Prefix prompt with `[LOOP]` to force full routing |
| Kiro ignores orchestration mid-session | Native dialog intercepted a prompt | Prefix prompt with `[LOOP]` to bypass the complexity gate |

#### Force Override — `[LOOP]` prefix

If Kiro ever falls back to native behavior mid-session, prefix your prompt with `[LOOP]`:

```
[LOOP] Build me a notification service with real-time updates
```

`[LOOP]` bypasses the Step 0 complexity gate and guarantees the full orchestration pipeline runs regardless of prompt length or signal count.

#### Mode Shortcuts

```
mode 1: build me a [full platform]        → Full 22-agent army
mode 2: write the architecture doc for X  → Single role (Architect)
mode 3: fix the null pointer in auth.go   → Direct execution, no overhead
mode 5: lean mode — 2-person startup      → 3 lite roles, 4-iteration cap
run discovery questions                   → Forces 7-question scoping wizard
```

---

### 🔵 PLATFORM 2 — Claude (claude.ai Projects)

> Best for: ongoing builds without Kiro, or using Claude as the AI engine alongside the system.

#### Step 1 — Create a Claude Project

1. Go to **[claude.ai](https://claude.ai)** → left sidebar → **"New Project"**
2. Name it: `Loop Engineering` or your product name
3. Click **Create Project**

#### Step 2 — Paste the system prompt

1. Inside the project → **"Project Instructions"** (gear icon or top right)
2. Open `kiro/adapters/claude-system-prompt.md` in any text editor
3. Copy everything **below** the `# ─────` comment line
4. Paste into Project Instructions → **Save**

#### Step 3 — Upload Knowledge files

Click **"Add Content" → "Upload files"** and upload these from `kiro/steering/`:

| File | Purpose |
|------|---------|
| `team-orchestrator-core.md` | Core execution rules + role handoffs |
| `team-orchestrator-rules.md` | NON-NEGOTIABLES + GATE S1 + GATE S2 |
| `team-orchestrator-sprint.md` | Sprint lifecycle + SM-RETRO |
| `skill-selection-matrix.md` | Story label → skill file mapping |
| `loop-engine.md` | PLAN→DO→VERIFY→DECIDE loop |
| `discovery-engine.md` | 7 scoping questions + scoring |
| `ponytail.md` | 7-rung lazy load ladder |
| `session-guards.md` | GUARD 1 + GUARD 2 |

**Optional (recommended for existing projects):**
- `docs/lessons.md` — past lessons (HIGH-confidence rules apply immediately)
- `docs/decisions.md` — ADR constraints (bind all roles)

#### Step 4 — Start your first session

Open a new conversation in the project and type:
```
[NEW SESSION]
Product: <what you're building>
Phase: THINK (or DESIGN / DEVELOP if resuming)
Last action: <what was done last, or "starting fresh">
```

#### Step 5 — Resuming a build

Paste your latest checkpoint entry at the start of each new conversation:
```
Resuming from checkpoint:
Sprint 2 / Phase 1. Last: backend auth complete. Next: FE integration story AUTH-003.
Files: docs/phase-1/sprint-plan.md (Sprint 2 section)
```

Claude Projects remember Knowledge files but not conversation history — the checkpoint paste is your resume mechanism.

#### Mode shortcuts (same as Kiro)
```
mode 1: build me a [platform]
mode 2: write the PRD for [feature]
mode 5: lean mode — small team
run discovery questions
```

---

### 🟢 PLATFORM 3 — ChatGPT (Custom GPT or Project)

> Best for: teams who prefer GPT-4o, or for sharing the system with others via a Custom GPT link.

#### Option A — Custom GPT (shareable, persistent) — Recommended

**Requires:** ChatGPT Plus, Team, or Enterprise.

1. Go to **[chat.openai.com](https://chat.openai.com)** → **"Explore GPTs"** → **"Create"**
2. Click the **"Configure"** tab
3. Set **Name:** `Loop Engineering Elite Team`
4. Set **Description:** `Senior engineering orchestrator — 22 specialist roles, 5 execution modes, structured sprint pipeline with security gates`
5. In the **Instructions** field: open `kiro/adapters/chatgpt-system-prompt.md`, copy everything below the `# ─────` line, paste it in
6. **Knowledge → Upload files:** same 8 steering files as Claude setup above
7. **Capabilities:** enable ✅ Web Search + ✅ Code Interpreter
8. **Conversation starters** (paste these in):
   ```
   [NEW SESSION] Product: [name] | Starting: THINK phase
   mode 1: build me a [describe your app]
   mode 5: lean mode — 2-person team, build [describe]
   run discovery questions
   ```
9. Click **Save** → **"Anyone with a link"** (for sharing) or **"Only me"**

#### Option B — ChatGPT Project (personal, no sharing)

1. Left sidebar → **"New Project"** → name it `Loop Engineering`
2. Inside project → **"Customize ChatGPT"**
3. Paste the `chatgpt-system-prompt.md` content into Instructions
4. **Add files** → same 8 steering files

#### Verify setup works

Start with:
```
[NEW SESSION] Product: test | Starting: THINK phase
```
You should see:
```
[ENV] TRACKER_MODE=markdown | GIT_MODE=LOCAL
```

#### Important: ChatGPT pair-programming model

ChatGPT produces commands — **you run them in your terminal.** When the system outputs:
```bash
git checkout -b feature/AUTH-001-user-login
```
Copy that and run it yourself. Think of ChatGPT as the brain, your terminal as the hands.

#### Model recommendations

| Task | Recommended model |
|------|--------------------|
| Full Mode 1 build (all phases) | GPT-4o |
| Architecture + ADR reasoning | o3 or o1 |
| Code generation (senior_engineer roles) | GPT-4o |
| Market research + THINK phase | GPT-4o with web search |
| Mode 3 quick fixes | GPT-4o mini (cost-efficient) |
| Mode 5 lean / fast builds | GPT-4o mini |

---

### 📊 Platform Comparison

| | Kiro IDE | Claude Projects | ChatGPT Custom GPT |
|---|---|---|---|
| Hook auto-loads | ✅ (every prompt) | ✅ (Project Instructions) | ✅ (Instructions field) |
| Steering files auto-loaded | ✅ (symlink) | ✅ (Knowledge upload) | ✅ (Knowledge upload) |
| Runs code directly | ✅ | ❌ (describes code) | ✅ (Code Interpreter) |
| File system access | ✅ | ❌ | ❌ |
| Shareable with team | ✅ (git repo) | ❌ (personal project) | ✅ (GPT link) |
| Best for | Primary dev work | Long-form builds | Teams / GPT preference |
| Setup time | ~5 min | ~10 min | ~15 min |
| Adapter file needed | ❌ (hook handles it) | ✅ `claude-system-prompt.md` | ✅ `chatgpt-system-prompt.md` |

---

### 📁 Adapter Files Location

All adapter files are in `kiro/adapters/`:

```
kiro/adapters/
├── claude-system-prompt.md    ← Paste into Claude Project Instructions
├── claude-setup-guide.md      ← Detailed Claude setup walkthrough
├── chatgpt-system-prompt.md   ← Paste into ChatGPT Instructions
└── chatgpt-setup-guide.md     ← Detailed ChatGPT setup walkthrough
```

> Both system prompts are synced to **Fix 43C · Dry Run v11 · 9.5/10 ship confidence.**

---

## 🗜️ Token Compression — pxpipe

> **What it is:** A local proxy that intercepts every API call from Kiro/Claude and converts bulky old context (system prompt, tool results, history) into PNG images before they leave your machine. Image tokens are billed by pixel area — not by content. Dense code/JSON runs at ~1 char/token as text, but ~3.1 chars/image-token, so you pay ~3x less per character of context.

**Measured results on our workload:**
- ~59–70% lower end-to-end token bill on dense coding sessions
- Gist recall: **98/98** — decisions, values, paths, names survive perfectly
- Verbatim recall: **13/15** — ~13% silent misread on exact hex strings (addressed by GUARD 3)
- Effective context window: **~3x larger** — same 1M window, old turns take ⅓ the tokens

**Why this matters for Loop Engineering specifically:**
Our hook fires on every prompt, sending the full orchestrator + 22 agent descriptions every time. That's ~15-25k tokens per prompt before any task begins. With pxpipe, that static slab compresses to ~5-8k image tokens — the biggest single saving in our setup.

### Quick Start (30 seconds)

**Step 1 — Install once:**
```bash
npm install -g pxpipe-proxy
```

**Step 2 — Launch every session:**
```bash
cd loopEngineering
./scripts/start-kiro-pxpipe.sh
```

The script starts the proxy, waits for it to be ready, then launches Kiro or Claude automatically. Dashboard at `http://127.0.0.1:47821` — shows live token savings per request with a kill switch.

**Step 3 — Validate (first sprint only):**
Check `~/.pxpipe/events.jsonl` after one sprint to see your actual compression ratio.

### What Gets Compressed

| Content | Compressed? | Why |
|---|---|---|
| System prompt + tool docs | ✅ Yes | Static slab — biggest single saving |
| Old history turns (beyond live tail) | ✅ Yes | Dense code/JSON — ~3x compression |
| Recent turns (active working window) | ❌ No | Stays text — agents need byte-exact access |
| Sparse prose | ❌ No | Profitability gate: images only win on dense content |
| git log / SHA output | ❌ No | GUARD 3 keepSharp — exact string protection |

### GUARD 3 Integration

GUARD 3 (in `session-guards.md`) makes agents aware of image context. When pxpipe is active, any exact-string lookup — git SHA, file:line, camelCase identifier — must come from a fresh tool call, not from memory. This aligns with our existing re-read-before-edit protocol.

### Research & Benchmarks

Full analysis in [`pxpipe-research.md`](pxpipe-research.md), including:
- Benchmark table (gist recall 98/98, verbatim recall 13/15, SWE-bench 10/10 at -65% cost)
- Why our workload is ideal (dense code/JSON, re-reads before edits)
- Comparison with `/compact` (pxpipe keeps content as images vs. `/compact` discards it as prose)
- keepSharp configuration for protecting exact strings

---

## 🔧 The Fix Register — What Was Built

This system was built across **47D+ incremental fixes** over multiple sessions. **Phase 1 is complete as of 2026-07-17.**

![Fixes](https://img.shields.io/badge/fix%20cycles-Fix%201--47D-blue) ![Phase](https://img.shields.io/badge/phase%201-complete-brightgreen) ![Skills](https://img.shields.io/badge/skill%20files%20wired-173-informational)

### By Type

| Type | Count | Description |
|------|-------|-------------|
| 🚀 **Feature** | 22 | New capabilities added to the system |
| 🔧 **Fix** | 18 | Bugs and gaps patched |
| 🛡️ **Guard** | 7 | Runtime protection mechanisms |
| 🚪 **Gate** | 8 | Quality enforcement checkpoints |
| 🏗️ **Architecture** | 5 | Structural changes to how files are organized |
| 📊 **Audit/Coverage** | 4 | Fix 47A-D skill activation coverage sweep |

### Key Milestones

| Fixes | What Was Accomplished |
|-------|-----------------------|
| Fix 1–10 | Foundation: tracker abstraction, role splits, skill pipeline, loop engine |
| Fix 11–15 | Precision: routing conflicts, hook rewrite as thin router, cleanup |
| Fix 16–25 | Intelligence: dynamic skill selection, dry run gaps, 22-role library |
| Fix 26–32 | Calibration: confidence scoring, memory system, doc knowledge architecture |
| Fix 33–38 | Enforcement: ponytail ladder, confidence signals, mobile routing |
| Fix 39–42 | Protection: memory progression, comprehension debt, bad loop scoping |
| Fix 43 | Verification: lesson age clock, dep disqualification, cross-tenant gate |
| Fix 44G | ✅ Infra: pxpipe integration — GUARD 3, launch script, CLAUDE.md note |
| Fix 44A | ✅ Mode 5 advisory for security/rbac stories |
| Fix 45A | ✅ Open-source artifacts: LICENSE (MIT) + CONTRIBUTING.md |
| Fix 45B | ✅ Compression-fidelity methodology doc (docs/research/) |
| Fix 45C | ✅ Competitor comparison: MemGPT, LangMem, Cognition Devin |
| Fix 46A | ✅ Product Knowledge Graph: graph_patch_emit, product_graph_update, D3 viz |
| Fix 47A–D | ✅ Skill Activation Audit: 37→119 label rows, phase auto-triggers, universal defaults |
| R1 | ✅ External Validator Outreach: HN + Reddit + LinkedIn + Discord posts drafted |

> **Phase 1 complete.** Full history: [`kiro/CLAUDE-implemented.md`](kiro/CLAUDE-implemented.md) · Active register: [`kiro/CLAUDE.md`](kiro/CLAUDE.md)

---

## 🧪 Dry Run History

All pipeline verification runs are documented in `docs/`. Each dry run tests the full system against realistic scenarios.

| Version | Date | Scenario | Confidence | Key Finding |
|---------|------|----------|------------|-------------|
| v1 | 2026-06-30 | JWT Auth | Baseline | Hook STEP 6 conflict |
| v2 | 2026-06-30 | Fraud Platform | Improving | Mode false positives |
| v3 | 2026-07-01 | Healthcare / FinTech / B2B / IoT | 7 gaps | 7 gaps → Fix 30 |
| v4 | 2026-07-01 | Data lake / EdTech / Marketplace / IoT | 8 gaps | 8 gaps → Fix 31 |
| v5 | 2026-07-03 | HealthTech / Multiplayer / Enterprise IAM | 6.5/10 | Full wiring trace |
| v6 | 2026-07-09 | Kundli app / Enterprise SaaS / Bugfix / Ponytail | 7.0/10 | Ponytail enforcement |
| v7 | 2026-07-09 | Fix 38 + 33 verification | 7.5/10 | Signal list + mobile routing |
| v8 | 2026-07-10 | Fix 40A–E full audit | 8.5/10 | Memory + guard system |
| v9 | 2026-07-10 | 4 adversarial stress tests | 8.5/10 | Full system coverage |
| v10 | 2026-07-10 | Fintech Fraud SaaS — full pipeline | 9.0/10 | 3 gaps → Fix 43 |
| **v11** | **2026-07-10** | **MEDIUM confidence / Mode 5 / Fix 43 verify** | **9.5/10** | **Gap 44A (LOW)** |

---

## 🔬 R&D Research Files

Three research documents park findings from experiments and third-party tool analysis. These are reference material — not active system files.

| File | What It Contains |
|------|-----------------|
| [`loop-engineering-white-paper-v5.pdf`](loop-engineering-white-paper-v5.pdf) | **Publication draft white paper (34 pages).** Problem-first framing: the 2026 production reliability crisis → why existing approaches fail → the Loop Engineering Framework as the response. Includes 12-pattern failure taxonomy, gist/exact-string recall bifurcation finding, compression data, guard effectiveness analysis. |
| [`GOAT.md`](GOAT.md) | **Honest gap analysis.** Where this framework is genuinely first in field (failure mode taxonomy, degradation tiers, compression-fidelity bifurcation, session continuity architecture) vs. what is missing for full academic validation (external reproducibility, controlled methodology, competitor comparison). |
| [`pxpipe-research.md`](pxpipe-research.md) | Full pxpipe assessment: benchmarks, compression math, Loop Engineering fit analysis, gist vs verbatim recall boundary, GUARD 3 rationale |
| [`gstack-research.md`](gstack-research.md) | gstack vs Loop Engineering: 30+ slash command inventory, 5 additive capabilities, architectural conflict analysis, decision log (Debugging Iron Law, Edit Scope Lock, QA Executor concept) |
| [`oneagent-search.md`](oneagent-search.md) | 67TB logs/metrics/traces search: AI agent as query layer on ClickHouse + VictoriaMetrics + Tempo, MCP server spec, cross-signal correlation architecture |

---

## 🔁 How to Reproduce

The core claim: a process layer structurally independent of model capability reduces production failure rates in agentic AI. Here is how to test that yourself.

**1. Clone:**
```bash
git clone https://github.com/supersaiyane/loopEngineering.git
cd loopEngineering
```

**2. Activate (Kiro IDE):**
```bash
ln -s kiro .kiro
# Open Kiro — hook auto-loads on first prompt
```

**Claude Projects:** Paste `kiro/adapters/claude-system-prompt.md` as system prompt + attach 8 knowledge files (see `kiro/adapters/claude-setup-guide.md`).

**3. Run on a real project for ≥5 sessions.** The 12 failure modes (F01–F12) surface within the first 3–5 sessions.

**4. Record observations** — which failure modes appeared, at what frequency, before and after the framework. Open a GitHub Issue with your findings.

Full reproduction guide: [CONTRIBUTING.md](CONTRIBUTING.md) · White paper: [loop-engineering-white-paper-v5.pdf](loop-engineering-white-paper-v5.pdf)

---

## 🗺️ Roadmap

> Based on the [GOAT analysis](GOAT.md) — where the framework is already first in field, and what it needs to become the definitive reference.

The roadmap is organized into four horizons. Each is grounded in a specific gap identified during the white paper research and GOAT analysis.

---

### ✅ Phase 0 — Foundation (Complete)
*Completed by 2026-07-10*

| Item | Status |
|------|--------|
| 12-pattern production failure taxonomy | ✅ Documented + cataloged |
| Four-layer process architecture | ✅ Production-validated (47+ fix cycles) |
| Degradation tier system (PEAK → CRITICAL) | ✅ Implemented in CLAUDE.md + session-guards.md |
| Session continuity (resume vector + checkpoint) | ✅ Active across all sessions |
| Gist/exact-string recall bifurcation finding | ✅ Measured, documented, mitigated via GUARD 3 |
| Compression data (59–70% on code-heavy sessions) | ✅ Measured across 47+ sessions |
| Three-tier guard architecture | ✅ In session-guards.md |
| White paper v5 (problem-first, 34 pages) | ✅ DOCX + PDF published |
| GOAT analysis | ✅ Honest gap + strength inventory |

---

### ✅ Phase 1 — Reproducibility (Complete · 2026-07-17)
*Transform the practitioner contribution into a replicable one*

| Item | Status | What Was Done |
|------|--------|---------------|
| **Open-source the core artifacts** | ✅ Done | LICENSE (MIT) + CONTRIBUTING.md published. Fix 45A. |
| **Methodology doc for compression-fidelity finding** | ✅ Done | `docs/research/compression-fidelity-methodology.md` — exact test conditions, session count, content types, misread detection methodology. Fix 45B. |
| **Fix 44A** | ✅ Done | Mode 5 advisory for security/RBAC stories wired into session-guards.md + orchestrator-routing.md. |
| **Competitor comparison section** | ✅ Done | `docs/research/competitor-comparison.md` — MemGPT, LangMem, LangGraph, Cognition Devin. Fix 45C. |
| **Fix 46A — Product Knowledge Graph** | ✅ Done | Two-agent flow: SE emits graph-patch YAML per story; ARCHITECT merges at GATE 5. D3 HTML viz at `docs/product-graph.html`. |
| **Fix 47A-D — Skill Activation Audit** | ✅ Done | 37→119 label rows, phase auto-triggers, universal role defaults, ~60 keyword fallback patterns. 173 skill files now wired. |
| **R1 — External Validator Outreach** | ✅ Drafted | HN + Reddit + LinkedIn + Discord posts at `docs/Audits/external-validator-outreach.md`. Ready to post. |

---

### 📅 Phase 2 — Validation (Next 90 days)
*Turn single-team evidence into reproducible findings*

| Item | What + Why |
|------|------------|
| **External validator study** | Recruit one other developer to apply the framework to their own codebase and document what happens. Even one external replication transforms this from case study to evidence. This is the single highest-leverage action for academic credibility. |
| **Before/after baseline measurement** | Run the same development workflow with the framework disabled for one sprint, then enabled — measure failure mode recurrence, session continuity score, tool call counts. Without a control group, the evaluation claims are assertions. |
| **Formal evaluation protocol** | Define measurable KPIs: session continuity score, failure mode recurrence rate, constraint drift incidents per 10 sessions, guard activation rate. Metrics enable others to benchmark against the framework, not just use it. |
| **MOMENTO evaluation scenarios** | Build evaluation scenarios from the checkpoint/resume vector patterns and test against the MOMENTO framework. This connects the framework to the only published multi-session benchmark, providing an academic anchor point. |

---

### 🔭 Phase 3 — Publication (3–6 months)
*Place the work in the academic record*

| Item | What + Why |
|------|------------|
| **arXiv preprint** | Submit the white paper v5 (with Phase 1 additions: methodology, competitor comparison) as an arXiv preprint. This establishes a timestamp on the failure taxonomy and bifurcation finding before others document them. |
| **Practitioner venue submission** | Target MLSys, EMNLP Systems track, or the ACL Workshop on Natural Language Processing for Programming — venues that accept practitioner research with production-validated findings. The MOMENTO paper creates a natural citation bridge. |
| **Case study publication** | Write the 44-fix development history as a structured case study. The progression from patch-level to framework-level resolution across 44 iterations is itself a publishable finding about how production AI frameworks emerge iteratively. |
| **Open standard proposal** | Propose the CLAUDE.md behavioral spec format and checkpoint schema as a community standard for process-layer LLM agent configuration. Similar to how `.editorconfig` standardized editor behavior — a `process.md` format could standardize agent process-layer contracts. |

---

### 🌐 Phase 4 — Field Impact (6–12 months)
*From framework to ecosystem*

| Item | What + Why |
|------|------------|
| **Multi-team validation study** | Coordinate 3–5 development teams running the framework across different codebases, tech stacks, and team sizes. Report aggregate failure mode rates and framework adoption patterns. This is what moves the work from "strong practitioner contribution" to "field-defining paper." |
| **Generalization research** | Test whether the failure mode taxonomy generalizes beyond software development. The twelve failure modes were derived from coding agents — how many apply to agents in other stateful domains (legal document review, financial analysis, scientific research automation)? |
| **Benchmark contribution** | Contribute production-derived test cases to MOMENTO or a successor benchmark. The resume vector + checkpoint patterns are directly translatable to multi-session evaluation scenarios with ground-truth correctness criteria. |
| **Tooling** | Build a lightweight framework validation tool — something that audits an existing agent configuration against the twelve failure modes and reports which ones are mitigated vs. exposed. Makes the framework accessible to teams without the 44-fix development journey. |

---

### 🎯 The One That Matters Most

> **External reproducibility is the critical path item.** Everything in Phase 1–4 is achievable, but external reproducibility is what separates a well-documented practitioner system from a contribution that reshapes the field. One other developer. One other codebase. One published report. That's the unlock.

---

| Term | What It Means |
|------|---------------|
| **Hook** | The entry point Kiro reads on every prompt. Like a traffic cop — routes requests, never does the work itself. |
| **Steering File** | A markdown file that shapes agent behavior. Think of it as a policy document the agents must follow. |
| **Skill File** | A focused protocol for one specific task (e.g., `api_versioning.md`, `caching_strategies.md`). |
| **Mode** | The execution tier — from Mode 5 (1 developer, lean) to Mode 1 (full 22-agent army). |
| **GATE S1** | Security check that runs BEFORE development starts. |
| **GATE S2** | PR review gate that runs BEFORE any code merges. |
| **GUARD 1** | Constraint drift protection — re-reads binding constraints every session. |
| **GUARD 2** | Bad loop protection — blocks agents from self-escalating dangerous scope changes. |
| **GUARD 3** | pxpipe image context protection — prevents agents from recalling exact strings (SHAs, line numbers, identifiers) from compressed image history. |
| **Ponytail** | The 7-rung lazy-load ladder. Forces agents to use what already exists before building from scratch. |
| **RDR** | Rung Disqualification Record — written when a dep on a rung is disqualified (CVE, license, etc.). |
| **ADR** | Architecture Decision Record — permanent doc explaining WHY an architectural choice was made. |
| **SM** | Scrum Master — the role that runs sprint planning, gates, and retrospectives. |
| **SM-RETRO** | Sprint retrospective — run at the end of every sprint, updates lessons.md. |
| **Comprehension Debt** | When agents approve code without actually reading it. The gate catches this. |
| **Bad Loop** | When an agent proposes changing scope it was never asked to change (e.g., "let me also refactor auth while I'm here"). |
| **Confidence Score** | A 0–100% signal from the 25-keyword scan that determines which mode to use. |
| **Discovery Engine** | 7-question wizard that scores your request and recommends the right mode when confidence is low. |
| **Stage 1-Fail** | A lesson that's been documented but not yet investigated or verified — the weakest lesson state. |
| **gate_fired_at** | The sprint when a bad-loop gate actually fired. Used for accurate lesson age calculations. |
| **Cross-Tenant Test** | A test that proves user A from company A cannot access user B's data from company B. Required at GATE S2 for RBAC stories. |
| **NON-NEG** | Non-Negotiable — a rule that cannot be overridden by any agent, prompt, or circumstance. |
| **Dry Run** | A simulated full pipeline run used to find gaps before real-world use. |
| **pxpipe** | A local proxy that compresses dense context (system prompt, tool results, old history) to PNG images — saves ~59-70% on token cost for code-heavy sessions. |
| **Silent confabulation** | When an agent confidently returns a wrong value from imaged history with no error signal. GUARD 3 prevents this by requiring re-fetch from source for exact strings. |

---

## 🚦 Current System Status

```
┌─────────────────────────────────────────────────────────┐
│  LOOP ENGINEERING — STATUS BOARD · 2026-07-17           │
├─────────────────────────────────────────────────────────┤
│  Phase 0 complete              ✅ Foundation             │
│  Phase 1 complete              ✅ 2026-07-17             │
│  Dry Run v11                   ✅ 9.5/10                │
│  Fix 44G pxpipe integration    ✅ GUARD 3 + script      │
│  Fix 44A Mode 5 advisory       ✅ Done                  │
│  Fix 45A open-source artifacts ✅ LICENSE + CONTRIBUTING│
│  Fix 45B compression methodology ✅ docs/research/       │
│  Fix 45C competitor comparison ✅ docs/research/         │
│  Fix 46A product knowledge graph ✅ D3 viz + YAML       │
│  Fix 47A-D skill coverage      ✅ 173 files wired       │
│  R1 outreach                   ✅ Drafted · Ready to post│
│  pxpipe token compression      ✅ ~59-70% savings       │
│  White paper v5                ✅ 34pp · DOCX + PDF     │
│  Git repo                      ⏸️ Push pending (SSH/PAT)│
├─────────────────────────────────────────────────────────┤
│  Next actions                                           │
│    → git push (run from terminal via SSH)               │
│    → Post R1 outreach: HN → Reddit → LinkedIn → Discord │
│    → Phase 2: External validator study (recruit 1 dev)  │
└─────────────────────────────────────────────────────────┘
```

---

<div align="center">

![Built with](https://img.shields.io/badge/built%20with-Claude%20Sonnet-blueviolet?style=flat-square)
![IDE](https://img.shields.io/badge/IDE-Kiro-orange?style=flat-square)
![Sessions](https://img.shields.io/badge/sessions-multi--session%20build-lightgrey?style=flat-square)
![Memory](https://img.shields.io/badge/memory-cross--session%20compounding-blue?style=flat-square)

*Loop Engineering — because AI agents shouldn't need to relearn what they already know.*

**Repository:** [github.com/supersaiyane/loopEngineering](https://github.com/supersaiyane/loopEngineering)
**Author:** GURPREET · [@supersaiyane](https://github.com/supersaiyane)

</div>
