# Mobile Offline Sync

## Core Principles
1. Optimistic UI: apply changes locally first; sync to server asynchronously.
2. Conflict resolution strategy must be defined before implementation: last-write-wins vs. CRDT vs. manual merge.
3. Queue mutations locally when offline; flush queue in order on reconnect.
4. Sync state must be visible to user — no silent failures or silent data overwrites.
5. Test offline→online transition explicitly; edge cases cluster here.

## Checklist (loop verifier)
- [ ] Conflict resolution strategy documented and implemented
- [ ] Mutation queue persists across app restarts
- [ ] Sync status visible to user (not silent)
- [ ] Offline→online transition test exists
