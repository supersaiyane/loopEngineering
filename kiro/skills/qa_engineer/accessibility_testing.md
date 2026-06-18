---
id: accessibility_testing
version: 1.0.0
owners: [qa_engineer, senior_engineer_fe]
tags: [accessibility, a11y, wcag, axe, screen-reader, keyboard-nav, aria, testing]
when_to_use: |
  On every form, modal, navigation, and interactive component.
  Before shipping any new page or major UI change.
  As part of the PR checklist for frontend changes.
inputs:
  - component_types, wcag_level_target, user_base
outputs:
  - "a11y_plan: automated checks + manual test cases + ARIA patterns + CI integration"
---

# Accessibility Testing

> Accessibility bugs are often the easiest to miss and the most impactful to users.
> 15% of the world has a disability. Automated tools catch ~30-40% of issues.
> The rest requires manual testing.

## WCAG 2.1 AA — the baseline

The four principles (POUR):
- **Perceivable**: content visible to all senses (alt text, captions, color contrast)
- **Operable**: keyboard navigable, no time limits, no seizure-inducing content
- **Understandable**: readable, predictable behavior, error messages
- **Robust**: works with assistive technologies (screen readers, voice control)

## Automated testing with axe

```tsx
// Jest + jest-axe
import { axe, toHaveNoViolations } from "jest-axe"
expect.extend(toHaveNoViolations)

test("checkout form has no accessibility violations", async () => {
  const { container } = render(<CheckoutForm />)
  const results = await axe(container)
  expect(results).toHaveNoViolations()
})

// Playwright + axe-core
import { test, expect } from "@playwright/test"
import AxeBuilder from "@axe-core/playwright"

test("checkout page is accessible", async ({ page }) => {
  await page.goto("/checkout")
  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa"])
    .analyze()

  expect(results.violations).toEqual([])
})
```

## Manual test checklist

Keyboard navigation:
- [ ] Tab order is logical (top-left to bottom-right)
- [ ] All interactive elements reachable by Tab
- [ ] Modals trap focus (Tab cycles within modal)
- [ ] Escape closes modals and dropdowns
- [ ] Enter/Space activates buttons and checkboxes

Screen reader (test with VoiceOver on Mac, NVDA on Windows):
- [ ] Images have descriptive alt text (or alt="" if decorative)
- [ ] Form inputs have associated labels
- [ ] Error messages announced when form submission fails
- [ ] Dynamic content changes announced (live regions)
- [ ] Page title updates on navigation (SPA)

Color and contrast:
- [ ] Text contrast ratio >= 4.5:1 (small text) or 3:1 (large text >= 18pt)
- [ ] Information not conveyed by color alone (e.g., error state has icon + text, not just red)
- [ ] Focus indicators visible (not removed with outline: none)

## ARIA patterns

```tsx
// Modal with focus trap
function Modal({ isOpen, onClose, title, children }) {
  return (
    <dialog
      open={isOpen}
      aria-modal="true"
      aria-labelledby="modal-title"
      role="dialog"
    >
      <h2 id="modal-title">{title}</h2>
      {children}
      <button onClick={onClose} aria-label="Close modal">X</button>
    </dialog>
  )
}

// Form with proper labels and error announcement
function EmailField({ error }) {
  return (
    <div>
      <label htmlFor="email">Email address</label>
      <input
        id="email"
        type="email"
        aria-describedby={error ? "email-error" : undefined}
        aria-invalid={!!error}
      />
      {error && (
        <span id="email-error" role="alert">
          {error}
        </span>
      )}
    </div>
  )
}

// Live region for dynamic updates
<div aria-live="polite" aria-atomic="true">
  {statusMessage}   {/* announced to screen readers when it changes */}
</div>
```

## Common violations and fixes

| Violation | Fix |
|---|---|
| Missing alt text | `<img alt="Description">` or `alt=""` for decorative |
| Missing form label | `<label htmlFor="field-id">` + `<input id="field-id">` |
| Low contrast text | Increase color contrast to 4.5:1 minimum |
| Keyboard trap | Ensure Tab can always exit a component |
| Missing focus style | Never use `outline: none` without replacement |
| Icon button no label | `<button aria-label="Close">` |

## Anti-patterns

- **`outline: none` with no replacement**: keyboard users lose focus visibility entirely.
- **Click-only interactions**: all mouse actions need keyboard equivalents.
- **`div` as button**: use `<button>` which gets keyboard and ARIA semantics for free.
- **Auto-playing media**: violates WCAG 1.4.2. Always allow user control.
- **Relying on automated tests only**: axe catches ~35% of issues. Manual testing required.

## Validation

- [ ] axe automated scan passes with zero violations.
- [ ] Manual keyboard navigation test completed.
- [ ] Screen reader test completed on at least one assistive technology.
- [ ] Color contrast verified with browser devtools or Colour Contrast Analyser.
- [ ] All form inputs have associated labels (verified in DOM, not just visually).
