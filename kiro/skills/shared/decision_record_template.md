# Decision Record Template

## Format (for docs/phase-N/impl-decisions.md entries)

```
## [STORY-ID] [Short title of decision]
**Date:** YYYY-MM-DD
**Decision:** [What was decided in one sentence]
**Alternatives considered:** [List 2-3 alternatives with one-line reason each was rejected]
**Rationale:** [Why this option was chosen — max 3 sentences]
**Consequences:** [What this decision makes easier / harder going forward]
**[PROMOTE]** — add this marker if: decision is reusable across stories or sprints
```

## Promotion criteria (Fix 22E)
Add [PROMOTE] marker when:
- Decision applies to ≥2 stories or will recur in future sprints
- Decision encodes a non-obvious trade-off worth remembering
- SM-RETRO GATE 4 step 2b item 4b: any [PROMOTE]-marked entry → move to kiro/memory/decisions.md as ADR
