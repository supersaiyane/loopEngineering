---
inclusion: manual
---

# Data Modeling Principles

## Core principles
- **Normalize to 3NF first** — denormalize only when query performance demands it, with explicit ADR
- **Immutable history** — prefer append-only event tables over mutable state; soft deletes over hard
- **Surrogate keys** — UUID or BIGSERIAL primary keys; natural keys as unique constraints, not PKs
- **Explicit nullability** — every nullable column needs a documented reason; nulls = unknown, not false/zero
- **Column naming** — snake_case, `_id` suffix for foreign keys, `_at` suffix for timestamps, `is_` prefix for booleans

## Relationships
- Avoid polymorphic associations — use STI (single table inheritance) or separate tables
- Many-to-many → always explicit join table with its own PK and metadata columns
- Self-referential hierarchies → use closure tables or ltree for deep querying

## Schema evolution
- All migrations reversible by default — `up` and `down` methods required
- Additive changes only in production: add columns/tables, never rename or drop without 2-phase migration
- Backfill in separate migration from schema change — decouple structure from data

## Indexing strategy
- Index every FK column — prevents sequential scans on joins
- Partial indexes on filtered queries (`WHERE status = 'active'`)
- Composite index column order: most selective first
- Avoid indexes on low-cardinality columns (boolean, enum with <5 values)

## Anti-patterns to flag
- EAV (Entity-Attribute-Value) — escalate to architect if proposed
- JSON blob for queryable data — use proper columns; JSON only for truly opaque payloads
- Shared mutable sequence tables — use DB-native sequences
