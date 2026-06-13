---
id: server_side_rendering_strategies
version: 1.0.0
owners: [frontend_lead]
tags: [ssr, ssg, isr, csr, nextjs, streaming, hydration, core-web-vitals, seo]
when_to_use: |
  When deciding the rendering strategy for a React/Next.js application.
  SSR vs SSG vs ISR vs CSR is the most impactful performance decision
  you make for a frontend. Wrong choice → slow LCP → bad SEO → lost users.
inputs:
  - seo_requirements, data_freshness, traffic_volume, personalization_needs
outputs:
  - "rendering_strategy: per-route rendering decision + caching headers + streaming plan"
---

# Server-Side Rendering Strategies

> The right rendering strategy per page type, not one strategy for the whole app.
> Next.js lets you mix strategies per route.

## Strategy comparison

| Strategy | When HTML is generated | Freshness | Use when |
|---|---|---|---|
| SSG (Static) | Build time | Stale until rebuild | Marketing pages, docs, blogs |
| ISR (Incremental Static) | Build + background revalidate | Near-real-time | Product pages, pricing |
| SSR (Server) | Every request | Always fresh | Personalized pages, auth-required |
| CSR (Client) | In browser | Always fresh (from API) | Admin dashboards, private tools |
| Streaming SSR | Request, in chunks | Always fresh | Complex pages with slow data |

## Next.js 14+ App Router patterns

```tsx
// SSG — no fetch = static at build time
export default async function MarketingPage() {
  const content = await cms.getPage('home')  // runs at build time
  return <Hero content={content} />
}

// ISR — revalidate every 60 seconds
async function getProducts() {
  const res = await fetch('https://api.example.com/products', {
    next: { revalidate: 60 }
  })
  return res.json()
}

// SSR — no cache = per request
async function getOrder(id: string) {
  const res = await fetch(`https://api.example.com/orders/${id}`, {
    cache: 'no-store'   // SSR: always fetch fresh
  })
  return res.json()
}

// Streaming — Suspense boundaries stream in as data resolves
export default async function Dashboard() {
  return (
    <div>
      <Header />                             {/* static, renders immediately */}
      <Suspense fallback={<MetricsSkeleton />}>
        <Metrics />                          {/* streams in when ready */}
      </Suspense>
      <Suspense fallback={<ChartSkeleton />}>
        <RevenueChart />                     {/* streams in independently */}
      </Suspense>
    </div>
  )
}
```

## Core Web Vitals targets

| Metric | Good | Needs work | Poor |
|---|---|---|---|
| LCP (Largest Contentful Paint) | < 2.5s | 2.5-4s | > 4s |
| FID / INP | < 100ms | 100-300ms | > 300ms |
| CLS (Cumulative Layout Shift) | < 0.1 | 0.1-0.25 | > 0.25 |

SSR/SSG directly improve LCP (HTML arrives pre-rendered).
CSR relies on JavaScript parse + API calls before LCP element renders.

## Hydration mismatch prevention

```tsx
// Common cause: using browser APIs in SSR render
// BAD:
const [width, setWidth] = useState(window.innerWidth)   // crashes on server

// GOOD:
const [width, setWidth] = useState(0)
useEffect(() => setWidth(window.innerWidth), [])         // runs client-only

// Common cause: date formatting with locale
// BAD:
const formatted = new Date().toLocaleDateString()        // differs server vs client

// GOOD:
const formatted = date.toISOString().split('T')[0]       // deterministic
```

## Caching headers for ISR

```typescript
// Next.js sets cache headers automatically for ISR
// For custom SSR responses:
export async function GET() {
  const data = await fetchData()
  return Response.json(data, {
    headers: {
      'Cache-Control': 'public, s-maxage=60, stale-while-revalidate=600',
    },
  })
}
```

## Anti-patterns

- **SSR everything including static content**: wasted CPU on every request. SSG/ISR is free after build.
- **CSR for SEO-critical pages**: Googlebot may not wait for JS. Use SSR/SSG.
- **No streaming for slow data**: users see blank page until all data resolves. Use Suspense.
- **Hydration mismatch ignored**: React re-renders entire tree. Causes CLS and performance hit.
- **`cache: 'no-store'` on public pages**: kills CDN caching. Only for private/auth pages.

## Validation

- [ ] Marketing and public pages use SSG or ISR (not SSR or CSR).
- [ ] Personalized and auth-required pages use SSR.
- [ ] Streaming used for pages with multiple independent data dependencies.
- [ ] LCP < 2.5s on key pages (measured with Lighthouse or CrUX).
- [ ] No hydration mismatches (check React DevTools console warnings).
