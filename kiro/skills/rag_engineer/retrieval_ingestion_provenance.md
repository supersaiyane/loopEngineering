---
id: retrieval_ingestion_provenance
version: 1.0.0
when_to_use: "Use when the task requires retrieval ingestion and provenance."
---

# Retrieval ingestion and provenance

## Approach

Track document identity, version, permissions, chunk boundaries and deletion through indexing.

## Verification and handoff

Test access controls and stale/deleted source handling before exposing retrieved content.

Report the inputs, decisions, evidence, assumptions and blockers to the next role. Use existing project constraints and explicit authorization; do not invent an execution or external result.
