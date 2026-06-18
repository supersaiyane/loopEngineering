---
id: visual_regression_testing
version: 1.0.0
owners: [qa_engineer, senior_engineer_fe]
tags: [visual-regression, percy, chromatic, playwright, screenshot, storybook, ui-testing]
when_to_use: |
  When a UI change could break the visual appearance without breaking functionality.
  CSS refactors, component library upgrades, theme changes, responsive breakpoints.
  Functional tests pass but pixels are wrong.
inputs:
  - component_library, ci_pipeline, screenshot_baseline, review_workflow
outputs:
  - "vrt_plan: tooling choice + baseline strategy + review process + CI integration"
---

# Visual Regression Testing

> Functional tests check behavior. Visual regression tests check appearance.
> A button that works but looks broken is still broken.

## Tool selection

| Tool | Best for | How it works |
|---|---|---|
| Chromatic (Storybook) | Component library, design system | Renders Storybook stories, diffs pixels |
| Percy (BrowserStack) | Full pages, cross-browser | Screenshots in CI, cloud diff |
| Playwright snapshots | Custom flows, no Storybook needed | Snapshot in test, compare on next run |
| Loki (Storybook OSS) | Self-hosted, cost-sensitive | Docker-based screenshot + diff |

## Playwright visual regression

```typescript
// tests/visual/checkout.spec.ts
import { test, expect } from "@playwright/test"

test("checkout page matches snapshot", async ({ page }) => {
  await page.goto("/checkout")
  await page.waitForLoadState("networkidle")

  // Hide dynamic content (dates, prices that change) before snapshot
  await page.evaluate(() => {
    document.querySelectorAll("[data-testid=price]").forEach(el => {
      el.textContent = "$0.00"
    })
    document.querySelectorAll("[data-testid=timestamp]").forEach(el => {
      el.textContent = "2026-01-01"
    })
  })

  await expect(page).toHaveScreenshot("checkout.png", {
    maxDiffPixels: 100,       // allow minor anti-aliasing diffs
    threshold: 0.1,           // 10% pixel diff tolerance
  })
})

// Run against multiple viewports
["mobile", "tablet", "desktop"].forEach(viewport => {
  test(`checkout - ${viewport}`, async ({ page }) => {
    const viewports = {
      mobile: { width: 375, height: 812 },
      tablet: { width: 768, height: 1024 },
      desktop: { width: 1440, height: 900 },
    }
    await page.setViewportSize(viewports[viewport])
    await page.goto("/checkout")
    await expect(page).toHaveScreenshot(`checkout-${viewport}.png`)
  })
})
```

## Storybook + Chromatic

```bash
# Install
npm install --save-dev @chromatic-com/storybook

# .storybook/main.ts
import type { StorybookConfig } from "@storybook/react-vite"
const config: StorybookConfig = {
  addons: ["@chromatic-com/storybook"],
}

# CI: upload stories to Chromatic for visual comparison
npx chromatic --project-token=$CHROMATIC_TOKEN --exit-zero-on-changes
```

Chromatic workflow:
1. PR pushes → Chromatic renders all stories
2. Diffs shown in Chromatic UI
3. Team reviews and approves/rejects changes
4. Approved changes become the new baseline

## Baseline management

```bash
# Playwright: update snapshots intentionally
npx playwright test --update-snapshots

# Never auto-update in CI -- that defeats the purpose
# Update locally, review the diff, commit the new baseline

# Ignore dynamic regions
await expect(page).toHaveScreenshot("page.png", {
  mask: [page.locator("[data-testid=user-avatar]")],  # mask user-specific content
})
```

## CI integration

```yaml
# .github/workflows/visual.yml
visual-regression:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Install Playwright
      run: npx playwright install --with-deps chromium
    - name: Run visual tests
      run: npx playwright test tests/visual/
    - name: Upload diffs on failure
      if: failure()
      uses: actions/upload-artifact@v4
      with:
        name: visual-diffs
        path: test-results/
```

## Anti-patterns

- **Running VRT on every PR without review workflow**: noise causes snapshot fatigue -- people approve without looking.
- **No masking of dynamic content**: timestamps, prices, user avatars cause constant false positives.
- **Updating baselines in CI automatically**: the whole point is human review of changes.
- **Screenshot the entire page**: focus on components and critical sections. Full-page screenshots have high noise.

## Validation

- [ ] Baselines committed to source control (or stored in Chromatic/Percy).
- [ ] Dynamic content masked before capture.
- [ ] Review workflow defined: who approves visual changes?
- [ ] CI fails on unreviewed visual changes.
- [ ] Mobile and desktop viewports both covered.
