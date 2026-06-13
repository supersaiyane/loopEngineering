---
id: micro_frontend_architecture
version: 1.0.0
owners: [frontend_lead, architect]
tags: [micro-frontend, module-federation, single-spa, monorepo, team-autonomy, webpack]
when_to_use: |
  When multiple teams need to develop, deploy, and own different parts
  of a large frontend independently. Not for small apps — overhead
  is significant. Justify with team size (4+ teams) or deployment independence.
inputs:
  - team_count, deployment_frequency, shared_component_needs, routing_ownership
outputs:
  - "mfe_design: composition strategy + routing + shared dependencies + communication"
---

# Micro-Frontend Architecture

> Micro-frontends solve team scaling problems, not technical problems.
> If you have one team, this is over-engineering.
> If you have 4+ teams stepping on each other's deployments, this is the fix.

## Composition strategies

| Strategy | How | Best for |
|---|---|---|
| Module Federation (Webpack 5) | Runtime code sharing via dynamic imports | Teams using same framework (React) |
| iFrames | True isolation, oldest approach | Legacy systems, strong sandboxing |
| Web Components | Framework-agnostic custom elements | Multi-framework teams |
| Single-SPA | Routing-level composition | Full SPA with multiple frameworks |

## Module Federation (Webpack 5) — recommended

```javascript
// Team A: navigation app (shell/host)
// webpack.config.js
const { ModuleFederationPlugin } = require('webpack').container

module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: 'shell',
      remotes: {
        'team-catalog': 'teamCatalog@https://catalog.example.com/remoteEntry.js',
        'team-checkout': 'teamCheckout@https://checkout.example.com/remoteEntry.js',
      },
      shared: {
        react: { singleton: true, requiredVersion: '^18.0.0' },
        'react-dom': { singleton: true, requiredVersion: '^18.0.0' },
      },
    }),
  ],
}

// Team B: catalog app (remote)
new ModuleFederationPlugin({
  name: 'teamCatalog',
  filename: 'remoteEntry.js',
  exposes: {
    './ProductList': './src/ProductList',
    './ProductDetail': './src/ProductDetail',
  },
  shared: { react: { singleton: true } },
})
```

```jsx
// Shell app consuming remote component
const ProductList = React.lazy(() => import('team-catalog/ProductList'))

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <ProductList />   {/* loaded from catalog team's deployment */}
    </Suspense>
  )
}
```

## Routing ownership

```
/                    → Shell team
/catalog/*           → Catalog team
/checkout/*          → Checkout team
/account/*           → Account team
```

Shell app owns the router. Each team owns routes under their prefix.

## Cross-MFE communication

Avoid tight coupling. Use:
1. **URL/routing**: navigate to a URL, the other MFE picks it up.
2. **Custom events**: `window.dispatchEvent(new CustomEvent('cart:updated', { detail: { count: 3 } }))`.
3. **Shared state store**: only if teams agree on contract (use event bus, not shared Redux store).

Never: import directly from another team's bundle at compile time.

## Shared dependencies

The `shared` config in Module Federation ensures React loads once (singleton).
Without it: two React instances → hooks fail, context breaks.

```javascript
shared: {
  react: { singleton: true, eager: true, requiredVersion: '^18.2.0' },
  'react-dom': { singleton: true, eager: true, requiredVersion: '^18.2.0' },
  'react-router-dom': { singleton: true, requiredVersion: '^6.0.0' },
  // Do NOT share: team-specific libraries, state management solutions
}
```

## Anti-patterns

- **Micro-frontends for a single team**: the communication overhead isn't worth it.
- **Shared state store across MFEs**: creates tight coupling between deployments.
- **Mismatched React versions**: hooks will fail silently. Enforce with `singleton: true`.
- **One MFE per component**: composition should be at the feature/domain level, not component.
- **No visual regression tests after federation updates**: remote changes can break shell UI.

## Validation

- [ ] Each MFE has its own CI/CD pipeline and deploys independently.
- [ ] React and other framework libraries marked as `singleton` in shared config.
- [ ] Cross-MFE communication uses events or routing, not imports.
- [ ] Shell app handles remote load failures gracefully (error boundary + fallback).
- [ ] E2E tests run against the composed application, not individual MFEs only.
