---
id: react_native_patterns
version: 1.0.0
owners:
  - mobile_engineer
tags:
  - react-native
  - expo
  - mobile
  - cross-platform
when_to_use: "When building cross-platform mobile apps with React Native or Expo, sharing code between iOS and Android, or managing mobile-specific state."
inputs:
  - feature requirements
  - Expo vs bare workflow decision
  - navigation structure
outputs:
  - React Native components
  - navigation setup
  - platform-specific code
  - tests
---

> "One codebase, two platforms, infinite edge cases."

## Navigation Setup (Expo Router)

```typescript
// app/(tabs)/_layout.tsx — file-based routing
import { Tabs } from "expo-router";

export default function TabLayout() {
  return (
    <Tabs screenOptions={{ tabBarActiveTintColor: "#007AFF" }}>
      <Tabs.Screen name="orders" options={{ title: "Orders", tabBarIcon: ... }} />
      <Tabs.Screen name="profile" options={{ title: "Profile", tabBarIcon: ... }} />
    </Tabs>
  );
}

// Typed navigation push
import { router } from "expo-router";
router.push({ pathname: "/orders/[id]", params: { id: order.id } });
```

## State Management (Zustand)

```typescript
import { create } from "zustand";

interface OrdersStore {
  orders: Order[];
  isLoading: boolean;
  error: string | null;
  fetchOrders: () => Promise<void>;
}

const useOrdersStore = create<OrdersStore>((set) => ({
  orders: [],
  isLoading: false,
  error: null,
  fetchOrders: async () => {
    set({ isLoading: true, error: null });
    try {
      const orders = await api.getOrders();
      set({ orders, isLoading: false });
    } catch (e) {
      set({ error: e.message, isLoading: false });
    }
  },
}));
```

## Platform-Specific Code

```typescript
import { Platform, StyleSheet } from "react-native";

const styles = StyleSheet.create({
  container: {
    paddingTop: Platform.select({ ios: 44, android: 24 }),
    ...Platform.select({
      ios: { shadowColor: "#000", shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1 },
      android: { elevation: 4 },
    }),
  },
});

// Platform-specific files (auto-selected by bundler)
// Button.ios.tsx   — iOS-specific implementation
// Button.android.tsx — Android-specific implementation
// Button.tsx       — fallback
```

## Anti-Patterns

- **`useEffect` for data fetching** — use React Query or Zustand async actions
- **Inline styles** — use `StyleSheet.create()` for performance (styles are validated and cached)
- **Ignoring keyboard avoidance** — wrap forms in `KeyboardAvoidingView`
- **Not testing on both platforms** — iOS and Android render differently; test both

## Validation Checklist

- [ ] Navigation types defined (Expo Router types or typed navigation params)
- [ ] Platform-specific code isolated to `.ios.tsx` / `.android.tsx` files
- [ ] `KeyboardAvoidingView` wraps all forms
- [ ] Deep links tested (Expo Router handles this automatically)
- [ ] Tested on physical device or simulator for both platforms
