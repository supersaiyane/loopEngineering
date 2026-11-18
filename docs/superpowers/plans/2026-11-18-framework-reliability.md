# Loop Engineering Reliability Implementation Plan

**Goal:** Make the framework consistent, testable, and honest about its guarantees, while preserving mandatory discovery for new builds and adding Kiro model guidance.

**Architecture:** Define a single canonical execution model and apply it across the framework. Add deterministic validation and scenario-based checks, with model selection after discovery. Keep host-specific integration behavior separate from portable process guidance.

**Tech stack:** Markdown, JSON, Bash, Python standard library, GitHub Actions, and Kiro IDE/CLI integration.

**Baseline:** Branch `improve/framework-reliability` started from `6387bc4`.
On 2026-11-18 the hook JSON and Bash syntax checks passed. `scripts/sheet_generator.py` was already untracked and is outside this work.

**Scope:** Framework reliability, safety, discovery, Kiro model choice, documentation, and evaluation. HealthGuard is an example and is outside scope.

## Phase 0 — Branch and baseline

- [x] Create and switch to `improve/framework-reliability` from the current `main`; retain the existing untracked script and this plan.
- [x] Record `git status`, current commit, available runtimes, and reproducible baseline test results. Do not overwrite user changes.
- [ ] Confirm each reported issue against the current source, especially Kiro hook behavior, before changing it.

## Phase 1 — One authoritative framework contract

**Files:** `README.md`, `kiro/hooks/elite-team-orchestrator.json`, `kiro/steering/discovery-engine.md`, `kiro/steering/orchestrator-routing.md`, `kiro/steering/session-guards.md`, `kiro/adapters/`, and `scripts/bootstrap-project.sh`.

- [x] Create a concise canonical reference for all five modes: names, triggers, discovery score ranges, default roles, and override behavior. Compatibility decision: use the repository routing file's Mode 4 Hybrid and Mode 2 Single Role definitions; research is a task rather than a separate mode.
- [ ] Run all seven discovery questions for each new build, score the answers, recommend a mode, then offer model selection before design. Align the hook, README, adapters, and generated trigger prompt to it.
- [ ] Normalize accepted artifact paths and distinguish existence checks from content validation. Keep explicit user overrides visible.
- [ ] Correct outdated role and skill-file counts and avoid promising independent agents or deterministic enforcement where neither is present.
- [x] Verify representative mode mappings and generated bootstrap instructions agree with the canonical reference through offline checks.

## Phase 2 — Safer integration and tooling

**Files:** Kiro hook, `scripts/bootstrap-project.sh`, `scripts/start-kiro-pxpipe.sh`, and `.github/workflows/deploy-pages.yml`.

- [ ] Verify the hook schema and event payloads against the actual supported Kiro version; record the version tested. Test that normal user input and clarification are not blocked. Narrow or remove a blocking rule if picker-specific behavior cannot be identified reliably.
- [x] Test new-project bootstrap in a temporary directory, including symlinks, generated files, path references, clean failure reporting, and behavior when a target already exists. Preserve existing user files and avoid implicitly committing unrelated changes.
- [ ] Change the pxpipe launcher so an occupied port produces a clear message and does not kill an unidentified process; document the external dependency and validate startup behavior. A fake executable verifies invocation; a real proxy startup remains untested. The launcher now requires an installed binary and does not auto-download it.
- [ ] Publish only the intended site files in the Pages artifact. The workflow assembles an explicit file list; actual deployment verification remains open.

## Phase 3 — Automated validation and CI

**Files:** new focused validation scripts and tests, plus a root `.github/workflows/` workflow.

- [x] Add an offline validator for hook JSON, required local framework files, expected role and role-qualified skill paths, and selected canonical mode definitions. Historical references, bare filenames, and arbitrary prose links are outside its scope.
- [x] Add tests using temporary fixtures that show a valid configuration passes and missing referenced files, invalid JSON, and conflicting mode mappings fail with actionable messages.
- [ ] Add repeatable scenario checks for a trivial fix, a new build, session resume, security-sensitive change, and an explicit user override. The manual host scenarios are documented in `docs/research/kiro-live-verification.md`; live executions remain open.
- [ ] Run validators and tests in root-level GitHub Actions on pull requests; restrict permissions and report failures clearly. Workflow added; no hosted CI run yet.
- [x] Provide a documented local command that runs the same checks.

## Phase 4 — Evidence and claims

**Files:** `README.md`, relevant research and audit documents, and an evaluation protocol.

- [ ] Replace unsupported readiness, confidence, savings, or first-of-kind claims with descriptions tied to their evidence and limitations; retain historical dry runs as historical records.
- [x] Define a reproducible comparison: tasks, baseline and framework conditions, model and host versions, scoring, failure criteria, cost, elapsed time, and independently inspectable results.
- [x] Add a template for external validation and explicitly label external studies as pending until completed. Do not fabricate results.
- [ ] Test claims and counts against repository contents and the evaluation record.

## Phase 5 — Kiro model selection

- [x] After the seven discovery answers and mode recommendation, offer model options with task fit, relative cost, and availability/lifecycle caveats in the prompt guidance.
- [x] For CLI, use `kiro-cli chat --list-models --format json` when the signed-in environment supports it; otherwise request the available options. For IDE, use its picker or user-provided available list. Never present a model as available without evidence.
- [x] Show how to select the model in the IDE picker or CLI `/model`, and wait for the user's choice. Do not claim that a prompt changes the session model.
- [x] Document representative model families, official source links, refresh date, and a safe fallback for unavailable or retired models.
- [ ] Validate the flow for both IDE and CLI without treating fixture tests as live-host proof.

## Phase 6 — Final verification and handoff

- [ ] Run the framework validator and scenario suite, shell/JSON checks, and CI configuration checks. Record exact commands, results, and environment limitations.
- [ ] Inspect the final diff for accidental publication, unrelated changes, and unsupported claims. Preserve the pre-existing untracked script.
- [ ] Produce a finding-by-finding status report: resolved, partially resolved, blocked, or deferred, with evidence and remaining risks. External validation and Kiro host integration can only be marked complete after actual execution.

## Execution order and dependencies

Phases 1–2 establish behavior; Phase 3 codifies it; Phase 4 fixes claims and measures evidence; Phase 5 implements Kiro model selection; Phase 6 verifies the entire branch. Tasks within a phase can be split into reviewable changes, but do not treat a design document, an instruction, or an unexecuted CI workflow as a passing test.
