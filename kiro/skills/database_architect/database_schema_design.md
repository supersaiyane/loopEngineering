<!-- LOAD-TYPE: CHECKLIST -->
---
id: database_schema_design
version: 1.0.0
owners: [database_architect]
tags: [database, schema, design, gdpr, query-patterns, be/database]
when_to_use: >
  When creating /docs/phase-N/db-architecture.md. Mandatory at GATE 2.
  database_architect owns creation. architect reviews STRIDE annotations (Section 4).
  security_engineer reviews GDPR column classification (Section 3) for HIPAA/PCI tables.
  Query patterns (Section 1) drive index design — do NOT design indexes without query patterns first.
  Volume estimates (Section 2) determine tech stack choice (Postgres vs ClickHouse vs DynamoDB).
  GATE 2 stays RED until all 4 per-table sections are complete for all tables.
---

# Database Schema Design — Query-First Methodology

FULL-LOAD REQUIRED — checklist for schema creation with mandatory query patterns, volume estimates, GDPR classification, and STRIDE annotations.
Output file: `/docs/phase-N/db-architecture.md`
Owner: `database_architect`

---

## QUICK REFERENCE

- **Query-first rule**: Write the queries before designing the tables. Tables exist to serve queries.
- **Volume-first tech choice**: Check Section 2 volume estimates BEFORE committing to Postgres.
  >1M rows/table + analytics → consider ClickHouse. >10K writes/sec → consider DynamoDB/Redis.
- **GDPR inline**: Classify every column at creation time — not in a later be/pii story.
- **STRIDE annotations**: Mark security-relevant tables so architect STRIDE finds them without re-reading.
- Index design derives from query patterns (Section 1) — never design indexes first.
- Feeds into: skill-label-index.md be/database label + be/pii auto-labeling (GDPR classification).

---

## PER-TABLE TEMPLATE (Fix 32E)

Repeat this template for EVERY table in the schema. All 4 sections mandatory.

---

### TABLE: [table_name]

**Purpose:** [one sentence — what this table stores and why it exists]
**Owner role:** [backend_lead | database_architect | data_engineer]

#### Section 1 — Columns + Types

```sql
CREATE TABLE [table_name] (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  -- [column]  [type]  [NOT NULL?]  [DEFAULT?]  [comment]
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

Column constraints to specify:
- NOT NULL vs nullable (be explicit — never leave ambiguous)
- DEFAULT values (especially for flags, status enums)
- CHECK constraints (e.g., CHECK (status IN ('active','inactive','deleted')))
- UNIQUE constraints (where applicable)

#### Section 2 — Query Patterns → Index Design

**Write queries BEFORE designing indexes. Index design derives FROM query patterns.**

```
Query 1: [description of query]
  SQL: SELECT * FROM [table] WHERE [condition]
  Frequency: [per-request | per-minute | per-hour | batch]
  → INDEX: [table]([column]) [UNIQUE?]

Query 2: [description]
  SQL: SELECT * FROM [table] WHERE [col1] = $1 AND [col2] BETWEEN $2 AND $3
  Frequency: [...]
  → INDEX: [table]([col1], [col2])  -- composite, order matters

Query 3: [description]
  SQL: SELECT * FROM [table] WHERE [col] = $1 AND deleted_at IS NULL
  Frequency: [...]
  → PARTIAL INDEX: [table]([col]) WHERE deleted_at IS NULL  -- filters inactive rows

Indexes to create:
  CREATE INDEX idx_[table]_[col] ON [table]([col]);
  CREATE UNIQUE INDEX idx_[table]_[col]_unique ON [table]([col]);
  CREATE INDEX idx_[table]_[col1_col2] ON [table]([col1], [col2]);
```

Common index patterns:
- Auth lookup: `CREATE UNIQUE INDEX idx_users_email ON users(email);`
- Status + date filter: `CREATE INDEX idx_orders_status_created ON orders(status, created_at);`
- Soft delete: `CREATE INDEX idx_items_active ON items(owner_id) WHERE deleted_at IS NULL;`
- Foreign key: `CREATE INDEX idx_items_user_id ON items(user_id);` (always index FK columns)

#### Section 3 — GDPR / Data Classification

**Classify EVERY column at table creation time. Use data classification schema from security-posture.md Section 4.**
Do NOT defer to a be/pii story — classify here.

```
| Column | Classification | Controls Required | Retention |
|--------|----------------|-------------------|-----------|
| id | PII:NONE | — | indefinite |
| email | PII:HIGH | encrypted at rest, excluded from logs | user-deletable |
| name | PII:HIGH | encrypted at rest, masked in non-prod | user-deletable |
| phone | PII:HIGH | encrypted at rest, excluded from logs | user-deletable |
| ip_address | PII:MEDIUM | pseudonymised, not in error logs | 30 days |
| user_agent | PII:MEDIUM | anonymised after session | 90 days |
| status | PII:NONE | — | indefinite |
| created_at | PII:NONE | — | indefinite |
```

Auto-label rule: if ANY column is PII:HIGH → automatically add [be/pii] to all stories touching this table.
Auto-label rule (HIPAA): if any column is PHI → [security-critical] added to ALL stories touching this table.

Deletion requirement (GDPR right to erasure):
- Strategy: hard delete | soft delete with scrub | anonymize (replace PII with placeholder)
- Cascades: which related tables must also be deleted/anonymized?
- Time to comply: within 30 days of request (GDPR) | immediate (user expectation)

#### Section 4 — STRIDE Annotations

**architect reads these annotations when running STRIDE (TRD Trust Boundary Map + these annotations = full STRIDE surface).**
Do NOT force architect to re-read all tables — surface threats here.

```
| Threat | Description | Mitigation | STRIDE Letter |
|--------|-------------|------------|---------------|
| Enumeration | Sequential UUIDs expose record counts | Use gen_random_uuid() — already in schema | S |
| Injection | Raw string concat in queries | Parameterized queries enforced — verify in SAST | T |
| PII exposure | email/name in error logs | Logger must scrub PII columns — add to testing checklist | I |
| Privilege escalation | User accessing other users' records | Row-level filter: WHERE owner_id = $current_user_id | E |
```

---

## VOLUME ESTIMATES (Fix 32E — drives tech stack validation)

**Fill this for EVERY table BEFORE committing to the tech stack.**

```
| Table | Rows at Launch | Rows at 6mo | Rows at 12mo | Write Rate (peak) | Read Pattern |
|-------|----------------|-------------|--------------|-------------------|--------------|
| users | 1,000 | 10,000 | 50,000 | 10/min | by id, by email |
| events | 100,000 | 5M | 50M | 10,000/min | by user + date range |
| sessions | 5,000 | 50,000 | 200,000 | 1,000/min | by token (TTL 30d) |
| audit_logs | 10,000 | 1M | 10M | 5,000/min | by user + action type |
```

**Volume-driven tech stack decision tree:**
```
events table:
  12mo estimate = 50M rows + analytics queries (aggregations, date ranges):
  → Postgres: viable if queries are pre-aggregated via materialized views. Monitor at 10M.
  → ClickHouse: evaluate if ad-hoc analytics are needed. Load analytical_datastore_patterns.md.

sessions table:
  High write rate (1,000/min) + short TTL (30 days):
  → Redis: ideal. TTL handled natively. No DELETE loops.
  → Postgres: viable but adds write pressure. Add TTL cleanup job.

audit_logs table:
  10M rows + append-only + time-range queries:
  → Postgres + partitioning by month: viable with index on (created_at).
  → Consider archival to S3 after 90 days (reduces hot table size).
```

Log: `[SCHEMA-VOLUME: table=events | 12mo=50M | analytics=yes → RECOMMENDATION: ClickHouse. Validate with database_architect before Sprint 2.]`

---

## RELATIONSHIPS + FOREIGN KEYS

```
| Relationship | From Table | FK Column | To Table | On Delete | On Update |
|---|---|---|---|---|---|
| user → orders | orders | user_id | users | CASCADE | CASCADE |
| order → items | order_items | order_id | orders | CASCADE | CASCADE |
| user → sessions | sessions | user_id | users | CASCADE | CASCADE |
```

Cascade rules:
- ON DELETE CASCADE: child records follow parent (orders belong to user — delete user → delete orders)
- ON DELETE SET NULL: FK becomes null (comment author deleted — comment stays, author_id = NULL)
- ON DELETE RESTRICT: block parent deletion if children exist (category with products cannot be deleted)
- Default to RESTRICT unless business rule explicitly requires CASCADE

---

## MIGRATION STANDARDS

Every schema change via migration file. No ad-hoc ALTER TABLE in production.

```
Migration naming: YYYYMMDDHHMMSS_[description].sql or [NN]_[description].ts
Migration rules:
  ✅ Always include DOWN migration (rollback path)
  ✅ Non-destructive first: add column nullable → backfill → add NOT NULL constraint
  ✅ Index creation: CREATE INDEX CONCURRENTLY (no table lock in Postgres)
  ❌ BANNED: DROP COLUMN without data archival confirmation
  ❌ BANNED: ALTER COLUMN TYPE on large tables without lock-timeout
  ❌ BANNED: Adding NOT NULL without default on tables with existing rows
```

VERIFIER for schema stories:
```bash
# Migration runs clean
npm run migrate && echo "PASS: migration applied"

# Rollback works
npm run migrate:undo && echo "PASS: rollback clean"
npm run migrate && echo "PASS: re-apply after rollback"

# No N+1 queries (check with query logging)
npm run test:integration 2>&1 | grep "SELECT" | sort | uniq -c | sort -rn | head -20
```

---

## VALIDATION LOG

When schema doc is complete, emit:
```
[SCHEMA-COMPLETE: tables=N | query-patterns: ✅ | volume-estimates: ✅ | GDPR-classified: ✅ | STRIDE-annotations: ✅ | auto-labels: [be/pii] on M tables | tech-stack recommendation: <notes>]
```
