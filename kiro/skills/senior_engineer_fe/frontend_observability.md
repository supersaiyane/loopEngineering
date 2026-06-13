---
id: frontend_observability
version: 1.0.0
owners: [senior_engineer_fe, sre_engineer]
tags: [observability, error-tracking, sentry, rum, core-web-vitals, session-replay, alerting]
when_to_use: |
  Every production frontend. You are blind in production without this.
  Set up before launch, not after the first bug report.
inputs:
  - traffic_volume, error_budget, user_journey_criticality
outputs:
  - "observability_config: error tracking setup + RUM metrics + alert thresholds + session replay config"
---

# Frontend Observability

> Backend has logs and traces. Frontend has users experiencing errors silently.
> Without frontend observability, you learn about bugs from customer support, not dashboards.

## Error tracking with Sentry

```typescript
// main.tsx / _app.tsx
import * as Sentry from "@sentry/react"

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  release: process.env.NEXT_PUBLIC_APP_VERSION,

  // Capture 100% of errors, 10% of performance traces
  tracesSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,    // always replay on error
  replaysSessionSampleRate: 0.05,   // 5% of all sessions

  beforeSend(event) {
    // Strip PII before sending
    if (event.user) {
      delete event.user.email
      delete event.user.ip_address
    }
    return event
  },
})

// Error boundary — catches React render errors
export function ErrorBoundary({ children }) {
  return (
    <Sentry.ErrorBoundary
      fallback={<ErrorPage />}
      beforeCapture={scope => scope.setTag("boundary", "root")}
    >
      {children}
    </Sentry.ErrorBoundary>
  )
}
```

## Real User Monitoring (RUM) — Core Web Vitals

```typescript
// Track CWV with web-vitals library
import { onCLS, onFID, onLCP, onFCP, onTTFB } from 'web-vitals'

function reportWebVitals({ name, value, rating }: Metric) {
  // Send to your analytics/monitoring
  analytics.track('web_vital', {
    metric: name,
    value: Math.round(name === 'CLS' ? value * 1000 : value),
    rating,                  // 'good' | 'needs-improvement' | 'poor'
    page: window.location.pathname,
  })

  // Alert on poor CWV in production
  if (rating === 'poor') {
    Sentry.captureMessage(`Poor ${name}: ${value}`, 'warning')
  }
}

onCLS(reportWebVitals)
onFID(reportWebVitals)
onLCP(reportWebVitals)
onFCP(reportWebVitals)
onTTFB(reportWebVitals)
```

## Custom error boundaries per feature

```tsx
// Isolate feature failures — one broken widget shouldn't crash the page
<ErrorBoundary fallback={<RecommendationsFallback />}>
  <RecommendationsWidget />
</ErrorBoundary>

<ErrorBoundary fallback={<CartErrorMessage />}>
  <CartSummary />
</ErrorBoundary>
```

## User-facing error messages

```tsx
// Expose error ID to user for support
function ErrorPage({ eventId }: { eventId: string }) {
  return (
    <div>
      <h1>Something went wrong</h1>
      <p>Our team has been notified.</p>
      <code>Error ID: {eventId}</code>
      <button onClick={() => Sentry.showReportDialog({ eventId })}>
        Tell us what happened
      </button>
    </div>
  )
}
```

## Alerts to configure

| Alert | Threshold | Channel |
|---|---|---|
| Error rate spike | > 2x baseline for 5 min | Slack #alerts |
| LCP "poor" rate | > 10% of sessions | Slack #perf |
| JS exception count | > 100/min | PagerDuty |
| Session replay on checkout errors | All | Review in Sentry |

## Anti-patterns

- **No error boundary at root**: one unhandled React error white-screens the app for all users.
- **Logging PII in error events**: email addresses, auth tokens in Sentry → compliance violation.
- **High replay sample rate in production**: session replays are expensive and contain user data.
- **Catching and swallowing errors**: `try { ... } catch(e) {}` → Sentry never sees it.

## Validation

- [ ] Sentry initialized before first render.
- [ ] Root-level error boundary in place.
- [ ] PII stripped in `beforeSend` hook.
- [ ] Core Web Vitals tracked and alerted.
- [ ] Error rate alert configured in monitoring platform.
