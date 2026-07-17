<!-- LOAD-TYPE: HYBRID -->
# Sprint Artifact Generation — SM Document Skills

## Purpose
SCRUM_MASTER invokes Anthropic document skills to produce sprint-level artifacts at GATE 5 and SM-RETRO.
This skill defines WHEN and HOW to invoke pptx, pdf, and xlsx for sprint outputs.

---

## Three artifact types and when to produce them

### 1. Sprint Review Deck (pptx)
**When:** GATE 5 — stakeholder review meeting is scheduled OR story has `docs/leadership` label
**What:** One slide per sprint story: title, what was built, acceptance criteria status, demo screenshot placeholder
**Structure:**
  - Slide 1: Sprint N Summary (goals, velocity, highlights)
  - Slide 2–N: One story per slide (story ID, title, status, key decision)
  - Final slide: Next sprint preview + open questions

**Invoke:** Load pptx skill. Provide story list + sprint summary from `docs/sprint-N/` as input.

---

### 2. Retrospective Report (pdf)
**When:** SM-RETRO is complete — after 5-stage memory entry is written to lessons.md
**What:** Single-page PDF summarizing retro output for async stakeholders
**Structure:**
  - Sprint N Retrospective — [date]
  - What went well (max 5 bullets)
  - What to improve (max 5 bullets)
  - Action items: owner + due date
  - Comprehension debt score (if non-zero, flag it)
  - Key lesson promoted to Stage 3+ (quote verbatim)

**Invoke:** Load pdf skill. Source content from SM-RETRO output already produced in session.

---

### 3. Velocity / Capacity Spreadsheet (xlsx)
**When:** SM-PLAN — when sprint capacity is being calculated OR after SM-RETRO when actuals are known
**What:** Running velocity tracker + next sprint capacity model
**Columns:** Sprint | Committed points | Delivered points | Velocity | Team capacity (%) | Notes
**Rows:** One per sprint, current sprint at bottom
**Derived cells:** Rolling 3-sprint avg velocity, next sprint capacity suggestion

**Invoke:** Load xlsx skill. Pull velocity data from `kiro/memory/checkpoint.md` sprint entries + story point totals from JIRA/tracker.

---

## Trigger priority

| Situation | Artifact | Timing |
|-----------|----------|--------|
| Stakeholder review approaching | pptx | Before GATE 5 |
| SM-RETRO complete | pdf | After SM-RETRO |
| SM-PLAN starting | xlsx | At SM-PLAN open |
| `docs/leadership` story label | pptx | During DEVELOP |
| `docs/sales` story label | pdf (one-pager) | During DEVELOP |

---

## File output convention
All artifacts saved to `docs/sprint-N/` where N is current sprint number:
- `docs/sprint-N/review-deck.pptx`
- `docs/sprint-N/retro-report.pdf`
- `docs/sprint-N/velocity-tracker.xlsx`

Commit alongside other GATE 5 artifacts.

---

## Notes
- pptx/pdf/xlsx are Anthropic-published skills installed in the environment. Invoke them via the Skill tool.
- Do NOT produce artifacts speculatively — only when the trigger conditions above are met.
- If no sprint data is available yet (Sprint 1 kickoff), skip xlsx — no historical data to populate.
