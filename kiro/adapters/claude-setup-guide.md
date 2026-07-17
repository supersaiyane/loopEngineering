# KIRO SYSTEM — CLAUDE SETUP GUIDE (v2.0)

Complete setup instructions for running the Loop Engineering elite-team system on Claude (claude.ai).
System prompt synced to: Fix 43C · Dry Run v11 · 9.5/10 ship confidence.
No changes to your kiro/ directory are needed.

---

## OPTION A — Claude Project (Recommended)

Claude Projects persist your instructions and knowledge files across every conversation.
Best for: ongoing product builds, returning to the same project across sessions.

---

### STEP 1 — Create the Project

1. Go to **claude.ai** and sign in
2. In the left sidebar, click **"New Project"** (or the + icon next to Projects)
3. Name it something like: `Kiro Elite Team` or your product name
4. Click **Create Project**

---

### STEP 2 — Add Project Instructions (the system prompt)

1. Inside your new project, click **"Project Instructions"** (top right or gear icon)
2. Open `kiro/adapters/claude-system-prompt.md` in a text editor
3. Copy everything **below** the comment header (start from `---` after the first block of `#` comments)
4. Paste it into the Project Instructions text box
5. Click **Save**

> **Why this works:** Claude loads Project Instructions at the start of every conversation in this project — replacing what the Kiro hook did automatically.

---

### STEP 3 — Upload Knowledge Files (steering files)

These are the large files the model reads on demand during a build.

1. Still inside your project, click **"Add Content"** → **"Upload files"**
2. Navigate to your `kiro/steering/` folder and upload all of these:

   **Core (required for all modes):**
   - `team-orchestrator-core.md` — core execution rules + role handoffs
   - `team-orchestrator-rules.md` — NON-NEGOTIABLES + GATE S1 + GATE S2 full checklist
   - `team-orchestrator-sprint.md` — sprint lifecycle: SM-PLAN → SM-RETRO + comprehension debt
   - `skill-selection-matrix.md` — story label → skill file mapping
   - `loop-engine.md` — PLAN→DO→VERIFY→DECIDE story loop (DEVELOP phase)
   - `discovery-engine.md` — 7 scoping questions + scoring → mode recommendation
   - `ponytail.md` — 7-rung ladder + rung disqualification protocol (always-loaded)
   - `session-guards.md` — GUARD 1 (constraint drift) + GUARD 2 (bad loop) (always-loaded)

3. Click **Save** or **Done**

> **Optional — upload skill files upfront:**
> If you know which roles you'll use most, upload those skill files too.
> Example: if you're building a web app, upload everything in `kiro/skills/senior_engineer_be/` and `kiro/skills/website_creator/`.
> The model will pull them when a matching role activates.

---

### STEP 4 — Upload Memory Files (if they exist)

If your project already has memory files from previous Kiro sessions:

1. Click **"Add Content"** → **"Upload files"**
2. Upload from your `docs/` folder:
   - `kiro/memory/lessons.md` ← accumulated lessons (HIGH-confidence ones apply immediately)
   - `kiro/memory/decisions.md` ← ADR index (architectural constraints)
   - `kiro/memory/checkpoint.md` ← where you left off (optional — paste the latest entry in your first message instead)

---

### STEP 5 — Start Your First Session

Open a new conversation inside the project and say:

```
[NEW SESSION]
Product: <what you're building>
Phase: <THINK / DESIGN / DEVELOP / or "starting fresh">
Last action: <what was done last, or "none — starting now">
```

Claude will:
1. Log `[ENV] TRACKER_MODE=... | GIT_MODE=...`
2. Ask the 7 scoping questions (if new build) or resume from checkpoint
3. Confirm the mode and proceed

---

### STEP 6 — How to Trigger Each Mode Mid-Conversation

| What you want | Say this |
|---|---|
| Full build pipeline | "mode 1: build me a [product]" |
| Single role only | "mode 2: write the architecture doc" |
| Quick fix / question | Just ask — Mode 3 fires automatically |
| Hybrid with Kiro spec | "mode 4: build using the existing .kiro/specs/" |
| Small team / fast | "mode 5: lean mode — 3-person team" |
| Explicit discovery | "run discovery questions first" |

---

### STEP 7 — Handling Skill Files On Demand

When Claude logs `[SKILLS ACTIVATED: role=architect | files=clean_architecture.md, api_design_patterns.md]`:

- If those files are already in Project Knowledge → Claude reads them automatically
- If not → open the file from `kiro/skills/architect/clean_architecture.md` and paste the content into the chat

Claude will extract what it needs and compress the file to a 5-line summary before producing the artifact.

---

### TIPS FOR BEST RESULTS

**Session start ritual:**
Always open with a one-line context statement. Claude Projects remember files but not conversation history beyond what's in context. A quick "Resuming Sprint 2 of Phase 1 — auth story" gets you back on track instantly.

**Paste checkpoint entries:**
If resuming a long project, paste the relevant checkpoint.md entry at the start:
```
Resuming from checkpoint:
[2026-06-30] Sprint 2 / Phase 1. Last: backend auth implemented. Next: QA gate + FE integration.
Files: docs/phase-1/sprint-plan.md, docs/foundation/architecture.md
```

**Context management:**
Claude will tell you when context is getting full (`[HEADROOM WARNING]`). When that happens, open a new conversation in the same project — your Knowledge files and Instructions carry over automatically.

**Long builds:**
For multi-phase projects, use one conversation per sprint. The Knowledge files persist; the conversation context resets cleanly.

---

## OPTION B — Claude Code (CLI)

If you're using Claude Code in your terminal inside the project repo:

1. Your `CLAUDE.md` already loads automatically — no extra setup needed
2. The hook (`kiro/hooks/elite-team-orchestrator.kiro.hook`) handles everything in Kiro
3. In Claude Code (outside Kiro), you can reference steering files with `@kiro/steering/team-orchestrator.md` syntax
4. Claude Code has direct file + shell access — closest to full Kiro parity

---

## OPTION C — Claude.ai (No Project — Single Conversation)

If you don't want to set up a Project:

1. Start a new conversation
2. Paste the entire content of `kiro/adapters/claude-system-prompt.md` as your **first message**
3. Then immediately say: `[SESSION START] — building: <product name>`
4. Paste any steering files you need inline as you go

> **Limitation:** Instructions don't persist between conversations. You re-paste the prompt each time.
> For any serious build, Option A (Project) is strongly recommended.

---

## QUICK REFERENCE — Files by Function

| File | Location | When needed |
|---|---|---|
| System prompt | `kiro/adapters/claude-system-prompt.md` | Once — paste into Project Instructions |
| Pipeline constitution | `kiro/steering/team-orchestrator.md` | Mode 1/4/5 builds |
| Skill routing | `kiro/steering/skill-selection-matrix.md` | Every role activation |
| Story loop | `kiro/steering/loop-engine.md` | DEVELOP phase |
| Mode selection | `kiro/steering/discovery-engine.md` | New builds |
| Memory | `kiro/memory/lessons.md`, `kiro/memory/decisions.md` | Session start |
| Skill files | `kiro/skills/<role>/*.md` | Per role activation |
| Shared skills | `kiro/skills/shared/*.md` | UI, code review, debugging |
| Design gate | `kiro/skills/shared/design_system_gate.md` | Before any UI code |
