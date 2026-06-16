---
id: mobile_performance_profiling
version: 1.0.0
owners:
  - mobile_engineer
tags:
  - performance
  - profiling
  - mobile
  - react-native
when_to_use: "When diagnosing slow scroll, janky animations, high memory usage, or slow startup times in a mobile app."
inputs:
  - symptom description (slow scroll, crash, startup lag)
  - platform
outputs:
  - profiling results
  - root cause analysis
  - optimized code
---

> "Profile first. Optimize second. Never guess."

## React Native Performance Targets

| Metric | Target | Tool to measure |
|--------|--------|----------------|
| JS frame rate | 60 fps | React Native Perf Monitor |
| List scroll | No dropped frames | Flipper + React DevTools |
| App cold start | < 2s | `react-native-startup-time` |
| Memory (idle) | < 200 MB | Xcode Instruments / Android Studio |
| Bundle size (initial) | < 5 MB | Metro bundle analyzer |

## React Native Perf Monitor

```typescript
// Enable in dev: shake device → "Perf Monitor"
// Watch for: JS fps drops below 60, RAM spikes during scroll

// Common culprit: inline functions in FlatList renderItem
// BAD — new function reference on every render:
<FlatList renderItem={({ item }) => <OrderItem order={item} />} />

// GOOD — stable reference with useCallback:
const renderItem = useCallback(
  ({ item }: { item: Order }) => <OrderItem order={item} />,
  []  // no deps — OrderItem is stable
);
<FlatList renderItem={renderItem} keyExtractor={(item) => item.id} />
```

## Heavy List Optimization

```typescript
// 1. FlashList — 10x faster than FlatList for large lists
import { FlashList } from "@shopify/flash-list";
<FlashList
  data={orders}
  renderItem={renderItem}
  estimatedItemSize={80}   // required — prevents layout jank
  keyExtractor={(item) => item.id}
/>

// 2. getItemLayout for fixed-height items (FlatList)
<FlatList
  getItemLayout={(_, index) => ({ length: 80, offset: 80 * index, index })}
  removeClippedSubviews={true}
/>
```

## Image Optimization

```typescript
// Use expo-image — cached, progressive, blurhash placeholder
import { Image } from "expo-image";
<Image
  source={{ uri: product.imageUrl }}
  placeholder={{ blurhash: product.blurhash }}
  contentFit="cover"
  transition={200}
  cachePolicy="memory-disk"   // cache on device
/>
```

## Anti-Patterns

- **Anonymous functions in JSX** — `onPress={() => fn(item)}` creates new ref every render
- **`console.log` in production** — measurable perf cost; use `__DEV__` guard
- **Large images without resize** — always serve device-appropriate sizes from CDN
- **setState inside render** — causes infinite re-render loop

## Validation Checklist

- [ ] FlatList / FlashList `keyExtractor` returns stable unique ID
- [ ] `renderItem` wrapped in `useCallback`
- [ ] No anonymous functions passed as props to list items
- [ ] Images served at correct resolution (2x for Retina, not 4x)
- [ ] Profiled with Flipper or Xcode Instruments — not just "it feels fast"
