---
id: mobile_offline_sync
version: 1.0.0
owners:
  - mobile_engineer
tags:
  - offline
  - sync
  - mobile
  - conflict-resolution
when_to_use: "When building mobile apps that need to work without network connectivity and sync changes when connection is restored."
inputs:
  - data entities to sync
  - conflict resolution strategy
  - sync frequency
outputs:
  - local SQLite/WatermelonDB schema
  - sync queue
  - conflict resolution logic
  - network monitoring
---

> "Assume the network is down. Design accordingly."

## Offline-First Architecture

```
User Action → Local DB (immediate) → Sync Queue → Server (when online)
                                           ↓
                                    Conflict Resolution
                                           ↓
                                    Merge + Update Local DB
```

## WatermelonDB Setup (React Native)

```typescript
import { Database, Model, field, date } from "@nozbe/watermelondb";
import SQLiteAdapter from "@nozbe/watermelondb/adapters/sqlite";

// Schema
const schema = appSchema({
  version: 1,
  tables: [
    tableSchema({
      name: "orders",
      columns: [
        { name: "server_id", type: "string", isOptional: true },
        { name: "customer_name", type: "string" },
        { name: "amount", type: "number" },
        { name: "status", type: "string" },
        { name: "is_synced", type: "boolean" },
        { name: "sync_version", type: "number" },
        { name: "created_at", type: "number" },
        { name: "updated_at", type: "number" },
      ],
    }),
  ],
});

// Sync function
import { synchronize } from "@nozbe/watermelondb/sync";

async function syncDatabase(database: Database) {
  await synchronize({
    database,
    pullChanges: async ({ lastPulledAt }) => {
      const response = await api.sync({ since: lastPulledAt });
      return { changes: response.changes, timestamp: response.timestamp };
    },
    pushChanges: async ({ changes }) => {
      await api.syncPush({ changes });
    },
    migrationsEnabledAtVersion: 1,
  });
}
```

## Conflict Resolution Strategies

| Strategy | When to use | Implementation |
|----------|------------|----------------|
| Last-write-wins | Non-critical fields | Compare `updated_at` timestamps |
| Server-wins | Financial data, inventory | Server version always prevails |
| Client-wins | User preferences | Client version always prevails |
| Merge fields | Rich text, lists | Deep merge per field type |

## Network Monitoring

```typescript
import NetInfo from "@react-native-community/netinfo";

const useSyncOnReconnect = () => {
  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener((state) => {
      if (state.isConnected && state.isInternetReachable) {
        syncDatabase(database).catch(console.error);
      }
    });
    return unsubscribe;
  }, []);
};
```

## Validation Checklist

- [ ] All mutations go to local DB first, network second
- [ ] Sync queue survives app restart (persisted, not in-memory)
- [ ] Conflict resolution strategy documented per entity
- [ ] Sync errors surface to user ("syncing failed, will retry")
- [ ] Offline state visually indicated in UI
