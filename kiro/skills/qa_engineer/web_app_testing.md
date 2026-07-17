<!-- LOAD-TYPE: CHECKLIST -->
# Web App Testing — Browser-Based QA

## Purpose
QA_ENGINEER uses claude-in-chrome tools to run browser-based functional, visual, and regression tests
against the running web application. Load when story label includes `testing/web` or `testing/e2e`
and the story involves a user-facing web interface.

---

## Prerequisites
Before running any browser test:
1. Confirm the app is running (local dev server or staging URL)
2. Load `mcp__claude-in-chrome__*` tools via ToolSearch if not already loaded
3. Open a tab to the target URL: `mcp__claude-in-chrome__navigate`

---

## Testing Checklist

### Phase 1 — Page Load & Structure
- [ ] Navigate to the URL and confirm page loads without console errors
  - `mcp__claude-in-chrome__navigate` → target URL
  - `mcp__claude-in-chrome__read_console_messages` → assert zero errors
- [ ] Confirm key page elements are present
  - `mcp__claude-in-chrome__read_page` → check for required headings, CTAs, nav
- [ ] Confirm no network request failures (4xx/5xx)
  - `mcp__claude-in-chrome__read_network_requests` → scan for error status codes

### Phase 2 — Functional Happy Path
For each acceptance criterion in the story:
- [ ] Execute the user action (click, fill form, navigate)
  - `mcp__claude-in-chrome__find` → locate element by label/selector
  - `mcp__claude-in-chrome__form_input` → fill form fields
  - `mcp__claude-in-chrome__javascript_tool` → trigger complex interactions
- [ ] Assert expected outcome (URL change, element appears, toast message)
  - `mcp__claude-in-chrome__read_page` → confirm output state
- [ ] Check console for new errors after interaction

### Phase 3 — Edge Cases
- [ ] Empty inputs / boundary values
- [ ] Invalid data (wrong format, overflow)
- [ ] Rapid repeated submission (double-click prevention)
- [ ] Navigate away mid-flow and return

### Phase 4 — Regression Sweep
For each story that MODIFIES existing UI:
- [ ] Visit all pages that share components with the changed area
- [ ] Confirm no visual regressions (layout breaks, missing elements)
- [ ] If `qa_engineer/visual_regression_testing.md` is loaded: apply screenshot comparison protocol

### Phase 5 — Screenshot Evidence
- [ ] Capture screenshots of key states as test evidence
  - `mcp__claude-in-chrome__computer` → take screenshot
- [ ] Save to `docs/qa/sprint-N/story-ID/` directory
- [ ] One screenshot per: initial state, post-action state, error state (if tested)

---

## Browser test output format

After completing all phases, emit a QA Test Report:

```
QA WEB TEST REPORT — [Story ID]
URL: [tested URL]
Date: [date]
Browser: Chrome (claude-in-chrome)

PHASE 1 — Page Load:  PASS / FAIL
  - Console errors: 0 / N
  - Network errors: 0 / N

PHASE 2 — Happy Path:  PASS / FAIL
  - [AC1]: PASS / FAIL — [one-line observation]
  - [AC2]: PASS / FAIL — [one-line observation]

PHASE 3 — Edge Cases:  PASS / FAIL
  - Empty input: PASS / FAIL
  - Invalid data: PASS / FAIL

PHASE 4 — Regression:  PASS / FAIL / SKIPPED
  - Affected pages checked: [list]

PHASE 5 — Evidence:
  - Screenshots: docs/qa/sprint-N/story-ID/ ([N] files)

VERDICT: PASS / FAIL / CONDITIONAL
BLOCKING ISSUES: [list or NONE]
```

---

## Integration with existing QA skills
- If the story also has `fe/a11y` label → run `qa_engineer/accessibility_testing.md` in the same browser session
- If the story has `testing/e2e` label → complement with `qa_engineer/exploratory_testing_charters.md` for exploratory pass
- If `fe/perf` label present → capture Core Web Vitals via `mcp__claude-in-chrome__javascript_tool` (window.performance API)

---

## Failure escalation
If PHASE 2 (happy path) fails:
→ Block story from GATE S3 — do NOT mark as done
→ Create a defect story: "BUG: [observed failure] on [URL]"
→ Tag with `testing/e2e` + the discipline lane label of the broken feature

If PHASE 1 (console/network errors) fails but PHASE 2 passes:
→ Flag as WARNING — story can proceed but errors must be resolved before GATE 5
