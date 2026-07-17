# Compression-Fidelity Bifurcation — Methodology & Findings

**Fix 45B · Loop Engineering · July 2026**

---

## Summary

When AI agents work in image-compressed context windows (e.g., Kiro's pxpipe, or any tool that renders context as rendered images rather than raw text), a previously undocumented failure mode emerges: **exact strings are misread at 11–17% rates while semantic recall remains at 97–98%.**

This creates a dangerous gap — the agent appears to understand the task correctly but silently corrupts critical identifiers like commit SHAs, camelCase identifiers, and file:line references.

We call this **compression-fidelity bifurcation**: the fidelity of meaning and the fidelity of exact characters diverge.

---

## The Problem

### What happens

In a standard text-based context window:
- Exact string recall: ~99%
- Semantic recall: ~99%

In an image-compressed context window (rendered HTML/PDF view passed as image):
- **Exact string recall: 83–89%** (11–17% silent misread rate)
- **Semantic recall: 97–98%** (largely unaffected)

### Why it is dangerous

An agent that misreads `abc123f` as `abc123e` will:
1. Appear to understand the task correctly (semantic recall intact)
2. Produce code or commands referencing the wrong identifier
3. Pass code review (the reviewer sees intent, not the exact character)
4. Fail at runtime — often in production

This is classified as **Failure Mode F12: Compression Confabulation**.

---

## Test Setup

### Trigger condition
- Kiro IDE with pxpipe integration active (context rendered as image stream)
- Or: any agent receiving context as image-compressed HTML/PDF render

### Test protocol

**Round 1 — Baseline (raw text context)**

1. Present agent with a document containing 20 exact-string targets:
   - 5 × git commit SHAs (40-char hex strings)
   - 5 × camelCase identifiers (`getUserByEmailAndTenant`, `onAuthStateChanged`)
   - 5 × file:line references (`src/auth/middleware.ts:147`)
   - 5 × semver strings (`2.14.0-rc.3+build.44`)

2. Ask agent to transcribe all 20 strings verbatim into a new document.

3. Diff output against originals. Record per-category error rate.

**Round 2 — Image-compressed context**

Same 20 strings, but context is delivered as image-compressed render (pxpipe or equivalent).

Same transcription task. Diff and record.

**Round 3 — With GUARD 3 mitigation**

Same image-compressed context. GUARD 3 active (re-verification step required before any exact string is used in code or commands).

Same transcription task. Diff and record.

### Measuring semantic recall separately

Alongside the exact-string test, include 20 semantic questions about the document content (who does X, what is the purpose of Y, when does Z happen). Score correct/incorrect.

---

## Results

| Condition | Exact-string accuracy | Semantic accuracy |
|-----------|----------------------|-------------------|
| Raw text context | 99.1% | 99.0% |
| Image-compressed (no guard) | **84.7%** | 97.6% |
| Image-compressed + GUARD 3 | **99.3%** | 97.6% |

**Error rate by string type (image-compressed, no guard):**

| String type | Error rate |
|------------|------------|
| Git commit SHAs | 17.2% |
| camelCase identifiers | 13.8% |
| file:line references | 11.4% |
| Semver strings | 9.6% |

### Common error patterns

- **Adjacent character transposition:** `abc123f` → `abc123e`
- **Zero/O substitution:** `0a4f` → `0a4F` or `Oa4f`
- **camelCase boundary collapse:** `getUserByEmail` → `getuserbyemail` or `GetUserByEmail`
- **Line number off-by-one:** `middleware.ts:147` → `middleware.ts:148`

---

## GUARD 3 Mitigation

GUARD 3 (Image Exact-String Guard) is defined in `kiro/steering/session-guards.md`.

### Protocol

When GUARD 3 is active, the agent must:

1. **Flag** any exact string extracted from image-compressed context before use.
2. **Re-verify** by asking the user to confirm the exact string, or by re-reading from a raw text source.
3. **Block** code generation or command execution that depends on the unverified exact string.

### Effectiveness

Post-GUARD 3 exact-string accuracy: **99.3%** — indistinguishable from raw text baseline.

The guard adds one confirmation step per unique exact string per session. In practice this adds 30–90 seconds to tasks involving SHAs or identifiers, which is acceptable given the alternative (silent production corruption).

---

## Limitations

1. **Sample size is small.** This finding is based on practitioner observation across ~40 sessions with pxpipe, not a controlled academic study. The 11–17% figure should be treated as an estimate, not a precise measurement.

2. **Model-dependent.** Different models may have different compression-to-image OCR characteristics. Results here apply to Claude Sonnet 3.5+.

3. **Resolution-dependent.** Higher-resolution image context reduces error rate. The test above used pxpipe default resolution.

4. **Not reproducible without pxpipe or equivalent.** Reproduction requires a tool that delivers context as image. Standard Claude Projects or API usage is not affected.

---

## Relationship to Failure Mode F12

F12 (Compression Confabulation) is formally defined as:

> The agent transcribes or uses exact strings (commit SHAs, identifiers, file references) from image-compressed context with silent character-level errors, while semantic understanding remains intact. The error is invisible in code review and only surfaces at runtime.

This methodology is the primary empirical support for F12's inclusion in the taxonomy.

---

## Recommendations

1. **Any tool delivering context as image** should enable GUARD 3 by default.
2. **Code review checklists** for agentic workflows should explicitly include exact-string spot-checks when image-compressed context was used.
3. **Future work:** extend the test to Cursor, GitHub Copilot Workspace, and Devin to determine whether F12 is pxpipe-specific or a general image-context phenomenon.

---

## Citation

If referencing this finding:

> Singh, G. (2026). *Loop Engineering: The Production Reliability Crisis and a Process-Layer Response*. Version 5.0, Section 4.3 (Compression-Fidelity Bifurcation). July 2026. https://github.com/supersaiyane/loopEngineering
