---
id: react_performance_patterns
version: 1.0.0
owners: [senior_engineer_fe, frontend_lead]
tags: [react, performance, memo, useMemo, useCallback, virtualization, re-renders, profiler]
when_to_use: |
  When a React component is slow, janky, or causing visible lag.
  Profile FIRST with React DevTools Profiler.
  Never optimize without measuring — premature memoization has costs too.
inputs:
  - component_tree, re_render_frequency, list_item_count, interaction_latency
outputs:
  - "optimization_plan: memoization targets + virtualization decision + state colocation fixes"
---

# React Performance Patterns

> Optimization without profiling is guess work.
> Open React DevTools Profiler. Find the component with the longest render bar.
> Fix that. Repeat.

## Step 1: Identify with React Profiler

```tsx
// Wrap suspect subtree
import { Profiler } from 'react'

<Profiler id="ProductList" onRender={(id, phase, actualDuration) => {
  if (actualDuration > 16) {  // 16ms = 60fps budget
    console.warn(`${id} took ${actualDuration.toFixed(1)}ms (${phase})`)
  }
}}>
  <ProductList products={products} />
</Profiler>
```

## Memoization: when it helps and when it hurts

```tsx
// React.memo — skip re-render if props haven't changed (shallow equality)
const ProductCard = React.memo(({ product, onAddToCart }) => {
  return (
    <div>
      <h3>{product.name}</h3>
      <button onClick={() => onAddToCart(product.id)}>Add to cart</button>
    </div>
  )
})
// ONLY useful when: (1) parent re-renders often, (2) this component is slow to render

// useMemo — memoize expensive computed value
const sortedProducts = useMemo(
  () => [...products].sort((a, b) => a.price - b.price),
  [products]   // only recompute when products array reference changes
)
// ONLY for genuinely expensive computations (> 1ms). Not for simple filtering.

// useCallback — stable function reference (prevents child re-render via React.memo)
const handleAddToCart = useCallback((productId: string) => {
  dispatch({ type: 'ADD_TO_CART', productId })
}, [dispatch])
// Only needed when the function is passed to a React.memo child
```

## State colocation (free optimization)

```tsx
// BAD: unrelated state at root causes full tree re-render
function App() {
  const [searchQuery, setSearchQuery] = useState('')   // causes App to re-render
  const [darkMode, setDarkMode] = useState(false)

  return <ProductList />   // re-renders on every keystroke in search
}

// GOOD: colocate state with the component that needs it
function SearchBar() {
  const [query, setQuery] = useState('')    // re-renders only SearchBar
  return <input value={query} onChange={e => setQuery(e.target.value)} />
}
```

## Virtualization for long lists

Without virtualization, 10,000 items = 10,000 DOM nodes. Renders in seconds.

```tsx
// @tanstack/react-virtual (most flexible)
import { useVirtualizer } from '@tanstack/react-virtual'

function ProductList({ products }: { products: Product[] }) {
  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    count: products.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 80,      // estimated row height in px
  })

  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
        {virtualizer.getVirtualItems().map(item => (
          <div
            key={item.key}
            style={{ position: 'absolute', top: item.start, width: '100%' }}
          >
            <ProductCard product={products[item.index]} />
          </div>
        ))}
      </div>
    </div>
  )
}
```

## Context performance

```tsx
// BAD: one context for everything — any value change re-renders all consumers
const AppContext = createContext({ user, theme, cart, notifications })

// GOOD: split contexts by update frequency
const UserContext = createContext(user)          // rarely changes
const ThemeContext = createContext(theme)         // rarely changes
const CartContext = createContext(cart)           // changes on add/remove
```

## Anti-patterns

- **Memoizing everything**: `useMemo` has overhead. For simple values, inline is faster.
- **Array/object literals in JSX**: `<List items={[1,2,3]}` creates a new array each render → memo won't help.
- **Context for high-frequency updates**: state that changes every keystroke in Context → every subscriber re-renders.
- **Profiling in dev mode**: React dev mode is 2-3x slower. Profile in production build.

## Validation

- [ ] Performance issue identified with React Profiler before optimizing.
- [ ] Lists > 100 items use virtualization.
- [ ] `React.memo` only on components that: (a) receive stable props AND (b) are expensive to render.
- [ ] Context split by update frequency (not one big context).
- [ ] No new object/array literals created in render and passed to memoized children.
