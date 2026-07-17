# KIRO SYSTEM — CHATGPT SETUP GUIDE (v2.0)

Complete setup instructions for running the Loop Engineering elite-team system on ChatGPT.
System prompt synced to: Fix 43C · Dry Run v11 · 9.5/10 ship confidence.
Two options: Custom GPT (shareable, reusable) or ChatGPT Project (personal, persistent).
No changes to your kiro/ directory are needed.

---

## OPTION A — Custom GPT (Recommended for teams / reuse)

A Custom GPT saves your instructions and knowledge files permanently.
Anyone you share it with gets the full Kiro system without any setup.
Best for: teams, repeated use, sharing the system with others.

**Requirement:** ChatGPT Plus, Team, or Enterprise subscription.

---

### STEP 1 — Create the Custom GPT

1. Go to **chat.openai.com**
2. In the left sidebar, click **"Explore GPTs"**
3. Click **"Create"** (top right)
4. You'll land on the GPT Editor — click **"Configure"** tab (not "Create" tab)

---

### STEP 2 — Fill in Basic Info

| Field | What to enter |
|---|---|
| Name | `Kiro Elite Team` (or your product name) |
| Description | `Senior engineering orchestrator running a multi-role AI pipeline. Coordinates 19 specialist roles across Think → Design → Develop → Launch phases.` |
| Profile picture | Optional — leave blank or generate one |

---

### STEP 3 — Paste the System Prompt (Instructions)

1. In the **"Instructions"** text box (large field in Configure tab)
2. Open `kiro/adapters/chatgpt-system-prompt.md` in a text editor
3. Copy everything **below** the comment header (start from `---` after the `#` comment block)
4. Paste it into the Instructions field

> **Character limit:** ChatGPT instructions support ~32,000 characters. The system prompt fits comfortably.

---

### STEP 4 — Upload Knowledge Files

1. Scroll down to the **"Knowledge"** section in Configure
2. Click **"Upload files"**
3. Upload these files from your `kiro/steering/` folder:

   **Core steering files (required for Mode 1/4/5 builds):**
   - `team-orchestrator-core.md` — core execution rules + role handoffs
   - `team-orchestrator-rules.md` — NON-NEGOTIABLES + GATE S1 + GATE S2 full checklist
   - `team-orchestrator-sprint.md` — sprint lifecycle + comprehension debt + retro
   - `skill-selection-matrix.md` — story label → skill file mapping
   - `loop-engine.md` — PLAN→DO→VERIFY→DECIDE story loop (DEVELOP phase)
   - `discovery-engine.md` — 7 scoping questions + mode scoring
   - `ponytail.md` — 7-rung ladder + rung disqualification protocol
   - `session-guards.md` — GUARD 1 (constraint drift) + GUARD 2 (bad loop)

   **Memory files (highly recommended):**
   - `kiro/memory/lessons.md` — accumulated lessons (HIGH-confidence ones apply immediately)
   - `kiro/memory/decisions.md` — ADR index / architectural constraints

4. For skill files — either upload them all upfront, or paste them on demand during a build (see Step 7)

---

### STEP 5 — Set Capabilities

In the Capabilities section, enable:

| Capability | Enable? | Why |
|---|---|---|
| Web Search | ✅ Yes | Market research, competitor lookup, package CVE checks |
| Code Interpreter | ✅ Yes | Running code, generating test output, data analysis |
| Image Generation | Optional | For design deliverables |

---

### STEP 6 — Set Conversation Starters (Optional but helpful)

Add these as starter prompts so users know how to begin:

```
[NEW SESSION] Product: [name] | Starting: THINK phase
mode 1: build me a [describe your app]
mode 2: write the architecture doc for [describe system]
mode 5: lean mode — build [describe] with a 2-person team
```

---

### STEP 7 — Save and Test

1. Click **"Save"** (top right) → choose **"Only me"** or **"Anyone with a link"**
2. Click **"View GPT"** to open it
3. Start with: `[NEW SESSION] Product: test app | Starting: THINK phase`
4. Verify you see: `[ENV] TRACKER_MODE=markdown | GIT_MODE=LOCAL`

---

### STEP 8 — How to Trigger Each Mode

| What you want | Say this |
|---|---|
| Full pipeline build | `mode 1: build me a [product]` |
| Single role only | `mode 2: write the PRD for [feature]` |
| Quick fix / question | Just ask — Mode 3 fires automatically |
| Hybrid with existing spec | `mode 4: build using existing .kiro/specs/` |
| Small team / fast | `mode 5: lean mode — 2-person team` |
| Run discovery first | `run discovery questions` |

---

### STEP 9 — Handling Skill Files On Demand

When the GPT logs `[SKILLS ACTIVATED: role=senior_engineer_be | files=clean_architecture.md, error_handling_strategies.md]`:

- **If uploaded to Knowledge:** GPT reads them automatically
- **If not uploaded:** Open the file from your local `kiro/skills/senior_engineer_be/clean_architecture.md` and paste the content into the chat

The GPT will extract what it needs, compress to a 5-line takeaway, and proceed with the artifact.

---

### TIPS FOR BEST RESULTS WITH CHATGPT

**Context window management:**
GPT-4o has a 128K token window. For long builds, start a new chat when the conversation gets long (>40 exchanges). Your Custom GPT's Instructions and Knowledge carry over to every new chat automatically.

**Code execution gap:**
ChatGPT produces code and commands — you run them in your terminal. When the GPT says `git checkout -b feature/AUTH-001-user-login`, copy that command and run it yourself. Think of ChatGPT as the brain, you as the hands.

**Resuming a build:**
Paste your latest checkpoint entry at the start of each new chat:
```
Resuming build. Sprint 2 / Phase 1.
Last: backend auth API complete, QA gate passed.
Next: frontend integration story AUTH-003.
Relevant files: docs/phase-1/sprint-plan.md (Sprint 2 section)
```

**TRACKER_MODE in markdown mode:**
If you're not using Jira/Linear/GitHub Projects, say "TRACKER_MODE=markdown" at session start. The GPT will maintain all sprint state in markdown file outputs that you save locally.

**Uploading large skill sets upfront:**
If you're running a full Mode 1 build, upload all role skill files at setup time. Organize by role — ChatGPT's file retrieval works best with descriptive filenames (which your kiro/skills/ files already have).

---

## OPTION B — ChatGPT Project (Personal, No Sharing)

ChatGPT Projects are simpler than Custom GPTs — personal use only, no sharing.
Best for: solo developers who want persistent context without building a Custom GPT.

**Requirement:** ChatGPT Plus or higher.

### Setup:

1. In the left sidebar, click **"New Project"** (or the **+** icon)
2. Name it `Kiro Elite Team` or your product name
3. Inside the project, click **"Customize ChatGPT"** (top right area)
4. Paste the system prompt from `kiro/adapters/chatgpt-system-prompt.md` into the **Instructions** field
5. Click **"Add files"** → upload the same steering files as Option A Step 4
6. Start a new conversation inside the project

> **Note:** ChatGPT Projects remember files but not conversation history across chats. Use the checkpoint paste technique (above) to resume builds.

---

## OPTION C — Single Chat (No Setup, Immediate Use)

If you just want to try the system right now without creating a GPT or Project:

1. Open a new ChatGPT chat (GPT-4o recommended)
2. Paste the entire content of `kiro/adapters/chatgpt-system-prompt.md` as your first message
3. Immediately follow with: `[SESSION START] Building: <describe your product>`
4. Paste `team-orchestrator.md` content when the model asks to run Mode 1
5. Paste skill files as roles activate

> **Limitation:** You re-paste the system prompt for every new chat. Option A or B is better for ongoing work.

---

## MODEL RECOMMENDATIONS

| Task | Best model |
|---|---|
| Full Mode 1 build (all phases) | GPT-4o or o1 |
| Architecture + ADRs | o1 (best at structured reasoning) |
| Code generation (senior_engineer roles) | GPT-4o |
| Market research + strategy (THINK phase) | GPT-4o with web search on |
| Quick Mode 3 fix | GPT-4o |
| Mode 5 lean / fast | GPT-4o mini (cost-efficient) |

---

## QUICK REFERENCE — Files by Function

| File | Location | When needed |
|---|---|---|
| System prompt | `kiro/adapters/chatgpt-system-prompt.md` | Once — paste into Instructions |
| Pipeline constitution | `kiro/steering/team-orchestrator.md` | Mode 1/4/5 — upload to Knowledge |
| Skill routing | `kiro/steering/skill-selection-matrix.md` | Every role activation — upload |
| Story loop | `kiro/steering/loop-engine.md` | DEVELOP phase — upload |
| Mode selection | `kiro/steering/discovery-engine.md` | New builds — upload |
| Memory | `kiro/memory/lessons.md`, `kiro/memory/decisions.md` | Session start — upload or paste |
| Skill files | `kiro/skills/<role>/*.md` | Per role — upload or paste on demand |
| Shared skills | `kiro/skills/shared/*.md` | UI, debugging, code review |
| Design gate | `kiro/skills/shared/design_system_gate.md` | Before any UI code |

---

## SIDE-BY-SIDE COMPARISON

| | Custom GPT | ChatGPT Project | Single Chat |
|---|---|---|---|
| Instructions persist | ✅ | ✅ | ❌ re-paste each time |
| Knowledge files persist | ✅ | ✅ | ❌ re-paste each time |
| Shareable with team | ✅ | ❌ | ❌ |
| Code execution | ✅ (Code Interpreter) | ✅ | ✅ |
| Web search | ✅ (enable in caps) | ✅ | ✅ |
| Setup time | ~10 min | ~5 min | ~1 min |
| Best for | Teams / repeat use | Solo dev | Quick test |
