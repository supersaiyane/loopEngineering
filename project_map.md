# Project Map — Loop Engineering

**What this repo is:** Loop Engineering is a process-layer framework — "a constitution for an AI
development team" — that governs how the **Kiro AI IDE** (and, via adapters, Claude/ChatGPT) behaves
when asked to build or maintain software. It is not an app itself; it is a set of rules, role
definitions ("skills"), and gates that turn a single LLM into a simulated 22-role engineering org
(THINK → DESIGN → DEVELOP phases, sprint gates, security gates, memory/lessons system). The repo
also hosts its own marketing/documentation site (`index.html`, GitHub Pages) and a research/audit
trail proving the framework's own claims via iterative "dry run" validations.

Two path systems refer to the same files: Mac (`/Users/supersaiyane/MyTechExploration/loopEngineering`)
and Linux sandbox (`/sessions/affectionate-lucid-bardeen/mnt/loopEngineering`).

**Excluded from this map (out of scope by explicit instruction):**
- `healthguard-pro/` — an unrelated experiment app that happens to live in this repo (has its own project_map.md/context_index.md)
- `kiro/memory/` — runtime memory (lessons.md, decisions.md, checkpoint.md for actual builds) — excluded on purpose

---

## Top-Level Root

| Item | Responsibility | Relates to |
|---|---|---|
| `README.md` (54KB) | Full onboarding doc for a first-time reader: problem statement, architecture diagram, 5 execution modes, 22 roles, key concepts (Ponytail ladder, Discovery Engine), file structure, steering file summaries, setup/usage, pxpipe compression, fix register, dry run history, roadmap, glossary. | Describes everything under `kiro/` and `docs/`; the canonical human-facing explanation. |
| `CONTRIBUTING.md` | How external contributors can participate (added as part of Fix 45A — "open-source artifacts" so the framework is externally reproducible). | Supports the "external validator" research goal in `docs/CLAUDE-working.md`. |
| `LICENSE` | Open-source license (Fix 45A). | — |
| `index.html` (119KB) | The live marketing/product site for the project. `<title>Loop Engineering — Elite AI Orchestration System</title>`. Deployed via GitHub Pages. | Built/maintained as part of DEVELOP-phase deliverables; content mirrors README claims (crisis framing, research links, roadmap). |
| `.claude/state/session.json` | Local Claude Code session state file. | Tooling-internal. |
| `.kiro` (symlink → `kiro/`) | Lets Kiro IDE (which looks for `.kiro/`) and this repo's `kiro/` naming coexist. | Central to how Kiro actually discovers the framework. |

---

## `docs/` — Documentation, Research, Audits, Knowledge Graph

| Subarea | Responsibility | Depends on / relates to |
|---|---|---|
| `docs/CLAUDE-working.md` | **Living backlog.** Pending fixes/gaps (GAP-48A…D format), Phase 2/3/4 roadmap (external validation, arXiv preprint, benchmark contribution), pxpipe token-compression notes, and the master **Fix Register** (Fix 1 → GAP-48D, ~61 entries) — the authoritative history of every change made to the framework itself. | Directly reflects/edits files under `kiro/steering/`, `kiro/skills/`, `kiro/hooks/`. |
| `docs/CLAUDE-implemented.md` | Archive of all already-implemented fixes (reference only, never auto-loaded — kept separate from CLAUDE-working.md so sessions don't re-read solved history). | Companion to CLAUDE-working.md. |
| `docs/product-graph.yaml` + `docs/product-graph.html` | A "living architecture map" schema (nodes: service/module/component/function/api/database/decision) meant to be filled in per real project built with the framework, merged at GATE 5 by the architect role. Currently an empty schema/template in this repo. | Produced/updated by `kiro/skills/architect/product_graph_update.md` and `kiro/skills/shared/graph_patch_emit.md`. |
| `docs/Audits/` (~26 files) | Iterative QA validation logs: `dry-run-*.md` (simulated end-to-end builds, e.g. JWT auth, fraud platform, four-scenario batches, versioned v2→v12) and `system-review-*.md` / `Agentaudit.md` (structural audits of the framework itself). `dry-run-v12-2026-07-17-comprehensive.md` traces a single HealthGuard Pro prompt through every fix (Fix 1–47D) to prove wiring. `dry_run.txt` / `kiro-flow-2026-07-01.txt` are raw session transcripts. `external-validator-outreach.md` is prepared recruitment copy for Research Task R1 (get an independent developer to reproduce results). | These are the framework's own regression-test suite — each dry run either passes cleanly or produces a new Fix/GAP entry in CLAUDE-working.md. |
| `docs/research/` | R&D backing the white paper: `GOAT.md`, `competitor-comparison.md` (vs MemGPT/Reflexion etc.), `compression-fidelity-methodology.md` (pxpipe accuracy study), `gstack-research.md`, `oneagent-search.md`, `ponytail-rung-disqualification-guide.md`, `research-context-token-memory-2026-06-30.md`. | Cited by the white paper and by README's "R&D Research Files" section. |
| `docs/white-paper/` | `loop-engineering-white-paper-v5.docx/.pdf` — the formal write-up (34pp) intended for arXiv / practitioner venues per the Phase 3 roadmap. | Downstream of research/ and the audits. |

---

## `kiro/` — The Framework Itself (symlinked as `.kiro/` for Kiro IDE discovery)

| Subarea | Responsibility | Depends on / relates to |
|---|---|---|
| `kiro/hooks/elite-team-orchestrator.kiro.hook` | **The single entry point.** A thin JSON hook (`promptSubmit` event, `askAgent` action) that fires on every user prompt. Stays silent during Kiro's native spec phase; activates the DEVELOP pipeline once specs/PRD exist and dev work begins. Its embedded prompt: reads session/sprint state, runs GUARD 4 (pre-code artifact gate), loads `team-orchestrator-core.md` + `team-orchestrator-rules.md` + `skill-selection-matrix.md` (STOP if any missing), then `loop-engine.md`, then delegates all role/gate logic to the steering files — it deliberately does not duplicate constitution content (kept ≤ a router, per Fix 12/41A history of hook bloat). | Loads everything in `kiro/steering/`; is the runtime trigger for the whole system. |
| `kiro/adapters/` | Setup guides + ready-to-paste system prompts so the same framework can run outside Kiro: `claude-setup-guide.md`/`claude-system-prompt.md` (Claude Projects / API), `chatgpt-setup-guide.md`/`chatgpt-system-prompt.md`. | Mirrors the hook + steering constitution for non-Kiro runtimes. |
| `kiro/skills/` | **23 folders** (22 engineering roles + `shared/`), each with a `SKILL.md` (role description) plus a library of topic-specific reference docs (e.g. `architect/adr_authoring.md`, `security_engineer/auth_design.md`). ~173 skill files total, wired to story labels via `skill-selection-matrix.md` / `skill-label-index.md`. Also `website_creator/` has nested `content/conversion/seo/technical/` subfolders. | Loaded selectively (2-4 files per activity, compressed to 5-line takeaways) — never bulk-loaded. Mapped from labels in `kiro/steering/skill-label-index.md`. See `context_index.md` for per-role one-liners. |
| `kiro/steering/` | **14 files** — the actual "constitution": role registry, execution modes, gates, loop protocol, security rules, memory discipline. This is where almost all real behavior is defined (the hook just routes to it). See `context_index.md` for what each file governs. | Loaded by the hook in a strict order; cross-referenced heavily (e.g. loop-engine.md is loaded at DEVELOP phase only). |
| `kiro/memory/` | **EXCLUDED per user instruction** — not read, described, or referenced beyond this note. (Conceptually: lessons.md / decisions.md / checkpoint.md for whatever real project is being built with the framework — distinct from the repo's own `docs/checkpoint.md`.) | — |

---

## `scripts/`

| Script | Responsibility |
|---|---|
| `bootstrap-project.sh` | Scaffolds a brand-new Kiro-ready project directory: copies framework hooks/steering/skills/adapters, moves `docs/research/` reference files to `.kiro/reference/`, sets up a fresh project memory, creates the `.kiro`↔`kiro` symlink pair, and lays out `docs/`, `services/`, `infra/`, `scripts/` in the new project. Usage: `./scripts/bootstrap-project.sh <ProjectName> [/path/to/parent]`. |
| `start-kiro-pxpipe.sh` | Launch wrapper for the **pxpipe** token-compression proxy (renders old context/system-prompt/tool-docs as PNG images to cut input token cost ~59-70%). Starts a local dashboard on port 47821; meant to be run before opening Kiro in a separate terminal. |

---

## `.github/workflows/deploy-pages.yml`

GitHub Actions workflow: on push to `main` (or manual dispatch), checks out the repo, configures GitHub Pages, uploads the entire repo root as the Pages artifact, and deploys — i.e. `index.html` is the site root. This is how the marketing/doc site goes live.

---

## How the Pieces Fit Together

1. A user prompt arrives in Kiro (or Claude/ChatGPT via adapters).
2. `kiro/hooks/elite-team-orchestrator.kiro.hook` fires, detects phase (spec vs develop), and — once in DEVELOP — loads the steering constitution in `kiro/steering/`.
3. The steering files define 5 execution modes (Full Army / Targeted / Direct / Research / Lean), a strict role artifact chain (market_researcher → cto → product_manager → architect → ... → scrum_master), and phase gates (GATE 1-5) that block progress until checklists pass.
4. Each role, when activated, pulls 2-4 targeted files from its `kiro/skills/<role>/` library (chosen via `skill-selection-matrix.md` / `skill-label-index.md`), not the whole library.
5. `loop-engine.md` governs how each story is iterated (PLAN→DO→VERIFY→DECIDE, max 8 iterations, maker/checker split) once DEVELOP work starts.
6. All of this is validated against itself in `docs/Audits/` (dry runs / system reviews), and gaps found there feed back into `docs/CLAUDE-working.md` as new Fix/GAP entries, which get implemented in the steering/skill files — a closed self-improvement loop.
7. Separately, `index.html` + `docs/white-paper/` + `docs/research/` package the project as a public-facing research artifact/marketing site, deployed via `.github/workflows/deploy-pages.yml`.
8. `scripts/bootstrap-project.sh` is how someone actually starts a *new* product using this framework (copies the framework into a fresh project directory).

So: **this is a meta-framework for AI-assisted software development** (steering docs + role skills + orchestrator hook), **plus** a self-documenting research project (audits, white paper, marketing site) proving that the framework works. Both purposes coexist in one repo.
