---
id: frontend_build_optimization
version: 1.0.0
owners: [frontend_lead]
tags: [webpack, vite, bundle-size, code-splitting, tree-shaking, lighthouse, performance]
when_to_use: |
  When bundle size is too large (> 500KB initial JS), builds are slow (> 2min),
  or Lighthouse performance scores are below 80.
  Run this analysis before any performance sprint.
inputs:
  - bundle_analyzer_output, lighthouse_scores, build_time, largest_dependencies
outputs:
  - "optimization_plan: bundle reduction targets + code splitting strategy + build config"
---

# Frontend Build Optimization

> You can't optimize what you can't measure.
> Start with `webpack-bundle-analyzer` or Vite's `rollup-plugin-visualizer`.
> Find the largest packages. Then decide: tree-shake, lazy-load, or replace.

## Measure first

```bash
# Vite
npm install --save-dev rollup-plugin-visualizer

# vite.config.ts
import { visualizer } from 'rollup-plugin-visualizer'
export default { plugins: [visualizer({ open: true })] }
npm run build
# Opens browser with treemap of bundle

# Webpack
npx webpack-bundle-analyzer dist/stats.json
```

## Code splitting (the highest ROI optimization)

```tsx
// Split by route — most impactful
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Settings = lazy(() => import('./pages/Settings'))
const Analytics = lazy(() => import('./pages/Analytics'))

// Split heavy libraries
const ReactQuill = lazy(() => import('react-quill'))  // rich text editor
const MonacoEditor = lazy(() => import('@monaco-editor/react'))  // 2MB
const { jsPDF } = lazy(() => import('jspdf'))
```

## Tree shaking

```javascript
// BAD — imports entire lodash (531KB)
import _ from 'lodash'
const debounced = _.debounce(fn, 300)

// GOOD — imports only debounce (3KB)
import debounce from 'lodash/debounce'
// or
import { debounce } from 'lodash-es'   // ESM version, tree-shakeable

// BAD — imports all icons
import { MdHome, MdUser } from 'react-icons/md'   // whole icon set

// GOOD — import per icon
import MdHome from 'react-icons/md/MdHome'
```

## Vite build config

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunks — cached separately from app code
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          'vendor-ui': ['@radix-ui/react-dialog', '@radix-ui/react-tooltip'],
          'vendor-charts': ['recharts'],
        },
      },
    },
    // Warn when any chunk > 500KB
    chunkSizeWarningLimit: 500,
  },
})
```

## Image optimization

```tsx
// Next.js — always use next/image
import Image from 'next/image'
<Image src="/hero.jpg" width={1200} height={600} priority alt="Hero" />
// Generates WebP automatically, lazy loads, prevents CLS with fixed dimensions

// Vite — vite-imagetools for explicit optimization
import heroUrl from './hero.jpg?w=1200&format=webp&quality=80'
```

## Critical CSS and fonts

```html
<!-- Preload critical fonts -->
<link rel="preload" href="/fonts/Inter.woff2" as="font" type="font/woff2" crossorigin>

<!-- Inline critical CSS (above-the-fold styles) -->
<!-- next/head with inline <style> for critical CSS -->

<!-- Google Fonts: use next/font to avoid render-blocking -->
```

```typescript
// next/font — loads font with zero layout shift, no external request
import { Inter } from 'next/font/google'
const inter = Inter({ subsets: ['latin'], display: 'swap' })
```

## Targets

| Metric | Target | Action if missed |
|---|---|---|
| Initial JS (gzipped) | < 150KB | Split by route, defer heavy deps |
| Total JS (gzipped) | < 500KB | Tree-shake, replace heavy libraries |
| Build time | < 60s | Switch to Vite/Turbopack, cache node_modules |
| Lighthouse Performance | > 85 | Check LCP image, eliminate render-blocking |

## Anti-patterns

- **Importing entire libraries**: `import moment from 'moment'` (329KB) vs `date-fns/format` (3KB).
- **No code splitting on routes**: entire app JS loads on every page.
- **Unoptimized images**: JPEG/PNG without WebP, no dimensions (CLS).
- **Third-party scripts in `<head>`**: render-blocking. Use `async`/`defer` or load after hydration.

## Validation

- [ ] Bundle analyzer run. Top 5 packages by size reviewed.
- [ ] All routes lazy-loaded (code-split by route).
- [ ] Initial JS bundle < 150KB gzipped.
- [ ] Lighthouse Performance score > 85 on key pages.
- [ ] Build time < 60s in CI.
