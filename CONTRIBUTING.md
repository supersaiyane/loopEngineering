# Contributing to Loop Engineering

Loop Engineering is a process-layer framework for production AI agent reliability. This document explains how to clone it, use it, reproduce the findings, and report failure modes you observe.

---

## How to Reproduce

The core claim of this framework is that a process layer — structurally independent of model capability — can reduce production failure rates in agentic AI systems. Here is how to test that claim yourself.

### 1. Clone the repo

```bash
git clone https://github.com/supersaiyane/loopEngineering.git
cd loopEngineering
```

### 2. Choose your platform

**Kiro IDE (native — recommended):**
```bash
ln -s kiro .kiro
# Open Kiro in this directory. The hook auto-loads on first prompt.
```

**Claude Projects:**
- Paste `kiro/adapters/claude-system-prompt.md` into your Claude Project system prompt
- Attach all 8 knowledge files listed in `kiro/adapters/claude-setup-guide.md`

**ChatGPT:**
- Paste `kiro/adapters/chatgpt-system-prompt.md` into a Custom GPT
- See `kiro/adapters/chatgpt-setup-guide.md` for setup options

### 3. Run it on a real project

Use the framework for at least 5 agentic sessions on a real codebase or non-trivial task. The failure modes (F01–F12) tend to surface within the first 3–5 sessions.

### 4. Check for failure modes

The 12 failure modes documented in the white paper are:

| ID  | Name | Observable symptom |
|-----|------|--------------------|
| F01 | Context Amnesia | Agent ignores constraints set earlier in session |
| F02 | Constraint Drift | Decisions made in Session N are forgotten in Session N+1 |
| F03 | Scope Creep | Agent expands task boundary beyond what was requested |
| F04 | Premature Completion | Agent declares done before verification |
| F05 | Auth Scope Violation | Agent attempts auth/payments changes without human gate |
| F06 | Deployment Self-Trigger | Agent triggers deploy/release without explicit instruction |
| F07 | Comprehension Theater | Agent approves artifacts it did not actually read |
| F08 | Memory Rot | Lessons written but never applied in future sessions |
| F09 | Lesson Age Inflation | Stale lessons appear fresh due to retro timing |
| F10 | Ponytail Violation | New dependency added when stdlib or existing tool suffices |
| F11 | Cross-Tenant Blindspot | Security test omitted on multi-tenant stories |
| F12 | Compression Confabulation | Exact strings (SHAs, file:line refs) silently misread from image-compressed context |

Record which of these you observe, with what frequency, before and after applying the framework.

### 5. Report back

Open a GitHub Issue with:
- Which failure modes you observed
- Your stack (model, IDE, project type)
- Whether the framework's guards caught them or missed them
- Any new failure modes not in the F01–F12 taxonomy

This is the external validation the framework needs to move from practitioner journal to field contribution.

---

## What NOT to commit

- **Do not commit your global `~/.claude/CLAUDE.md`** — this contains your personal kernel and session state. Add it to `.gitignore`.
- **Do not commit `docs/lessons.md`** if it contains proprietary project details.
- **Do not commit `.kiro/specs/`** — these are project-specific and usually contain unpublished work.

A recommended `.gitignore` addition:
```
.claude/
docs/lessons.md
kiro/specs/
*.local.md
```

---

## Improving the Framework

Pull requests welcome for:
- New failure mode observations (with evidence)
- Platform adapter improvements (Kiro, Claude, ChatGPT, Cursor, etc.)
- Skill file additions or corrections
- White paper corrections or additions
- Methodology improvements for the compression-fidelity finding

Please open an Issue before a large PR so we can align on direction.

---

## Citing the White Paper

If you use Loop Engineering in your research or reference its findings:

> Singh, G. (2026). *Loop Engineering: The Production Reliability Crisis and a Process-Layer Response*. Version 5.0. Publication Draft. July 2026. https://github.com/supersaiyane/loopEngineering

The white paper is available as PDF and DOCX in the repo root.

---

## Contact

GitHub: [@supersaiyane](https://github.com/supersaiyane)
Email: senghgurpreett@gmail.com
