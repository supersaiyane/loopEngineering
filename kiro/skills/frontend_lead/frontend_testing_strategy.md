---
id: frontend_testing_strategy
version: 1.0.0
owners: [frontend_lead, qa_engineer]
tags: [testing, vitest, react-testing-library, playwright, storybook, msw, a11y]
when_to_use: |
  When establishing the testing pyramid for a frontend codebase.
  Covers unit tests for components, integration tests for user flows,
  and E2E tests for critical paths.
inputs:
  - component_count, critical_user_flows, ci_time_budget, team_testing_maturity
outputs:
  - "testing_plan: test type distribution + tooling decisions + CI integration"
---

# Frontend Testing Strategy

> Test behavior, not implementation.
> A test that breaks when you rename a CSS class is worthless.
> A test that breaks when users can't check out is priceless.

## Testing pyramid for frontend

```
E2E (Playwright): 5-10 tests
  Critical happy paths only — checkout, auth, core workflow

Integration (React Testing Library): 70% of tests
  Component behavior from user perspective
  Mock network (MSW), not internal state

Unit (Vitest): 25% of tests
  Pure functions, hooks, utility logic
  Not: "does this component render without error"
```

## Component tests with React Testing Library

```tsx
// Test what users see and do — not implementation details
import { render, screen, userEvent } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { server } from '../mocks/server'
import { AddToCart } from './AddToCart'

test('adds item to cart and shows confirmation', async () => {
  const user = userEvent.setup()

  // MSW intercepts the actual fetch — no mocking of internals
  server.use(
    http.post('/api/cart', () => HttpResponse.json({ success: true, count: 1 }))
  )

  render(<AddToCart productId="prod_1" productName="Widget" />)

  await user.click(screen.getByRole('button', { name: /add to cart/i }))

  expect(await screen.findByText(/added to cart/i)).toBeInTheDocument()
  expect(screen.getByLabelText(/cart count/i)).toHaveTextContent('1')
})

// DON'T test: component state, internal method calls, CSS classes
// DO test: what appears on screen, what happens after user interactions
```

## MSW (Mock Service Worker) for network

```typescript
// mocks/handlers.ts
import { http, HttpResponse } from 'msw'

export const handlers = [
  http.get('/api/products', () => {
    return HttpResponse.json([
      { id: 'p1', name: 'Widget', price: 2999 },
    ])
  }),

  http.post('/api/orders', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({ id: 'ord_123', ...body }, { status: 201 })
  }),
]

// Same handlers work in tests (Node) and browser (development)
```

## E2E with Playwright

```typescript
// tests/checkout.spec.ts
import { test, expect } from '@playwright/test'

test('complete checkout flow', async ({ page }) => {
  await page.goto('/products/widget')
  await page.getByRole('button', { name: 'Add to cart' }).click()
  await page.getByRole('link', { name: 'Cart' }).click()
  await page.getByRole('button', { name: 'Checkout' }).click()

  await page.fill('[name="email"]', 'test@example.com')
  await page.fill('[name="card-number"]', '4242424242424242')
  await page.getByRole('button', { name: 'Place order' }).click()

  await expect(page.getByText('Order confirmed')).toBeVisible()
})
```

## Accessibility testing

```tsx
import { axe, toHaveNoViolations } from 'jest-axe'
expect.extend(toHaveNoViolations)

test('form has no accessibility violations', async () => {
  const { container } = render(<CheckoutForm />)
  const results = await axe(container)
  expect(results).toHaveNoViolations()
})
```

## Anti-patterns

- **Testing implementation (`wrapper.state()`, internal method calls)**: breaks on every refactor.
- **Mocking React internals**: `jest.mock('react', ...)` — this is a smell.
- **Snapshot tests for everything**: snapshots break constantly and are rarely read.
- **E2E tests for unit-testable logic**: E2E is slow. Test pure functions with Vitest.
- **No MSW — mocking `fetch` directly**: your test no longer tests your actual network layer.

## Validation

- [ ] Zero tests that import and call internal component methods.
- [ ] MSW configured for all network calls in tests.
- [ ] E2E limited to critical happy paths (< 15 tests, CI < 5 min).
- [ ] axe accessibility checks on at least form components.
- [ ] Coverage target: behavior coverage (key user flows), not line coverage %.
