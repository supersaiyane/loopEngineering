<!-- LOAD-TYPE: HYBRID -->
---
id: analytical_datastore_patterns
version: 1.0.0
owners: [database_architect, data_engineer]
tags: [database, analytics, clickhouse, cassandra, dynamodb, data/pipeline, data/streaming]
when_to_use: >
  Any story using ClickHouse (analytical queries, usage metrics), Cassandra/ScyllaDB
  (time-series, wide-column), or DynamoDB (single-table design, GSI patterns).
  Load at data/pipeline or data/streaming stories where the data store is one of these three.
---

# Analytical Data Store Patterns

HYBRID — compress for context; full-load the specific engine section when writing criteria.

---

## QUICK REFERENCE (compress to this 5-line summary)

- **ClickHouse**: avoid OFFSET pagination; use cursor/keyset. MergeTree partitioned by date. Materialized views for pre-aggregation. No transactions — eventual consistency on replicas.
- **Cassandra/ScyllaDB**: model for query first, not schema first. Partition key = even distribution. Avoid large partitions (>100MB). Denormalize aggressively — no JOINs. ALLOW FILTERING = banned in prod.
- **DynamoDB**: single-table design; GSIs for access patterns. Hot partition risk: add random suffix to partition keys for high-write items. Don't use Scan in prod. TTL for expiry, not DELETE loops.

---

## SECTION 1 — CLICKHOUSE

### Schema Design
- `MergeTree` family is the default. Choose engine by use case:
  - `ReplacingMergeTree` — for deduplication (usage events with idempotency key)
  - `SummingMergeTree` — for pre-aggregated counters
  - `AggregatingMergeTree` — for materialized views with partial aggregations
- Partition by date: `PARTITION BY toYYYYMM(event_date)`. Never partition by high-cardinality column.
- Order key (primary sort): choose columns used in WHERE and GROUP BY filters.

### Query Patterns
- **BANNED in production:**
  - `OFFSET N` pagination on large tables — ClickHouse reads and discards N rows. Use keyset pagination: `WHERE (date, id) > (last_date, last_id) ORDER BY date, id LIMIT 100`
  - `SELECT *` on large tables
  - `JOIN` across tables with large result sets — use dictionary lookups or pre-join at ingest
- **Recommended:**
  - Materialized views for common aggregations (daily totals, hourly counts) — query the view, not raw data
  - `toStartOfDay()` / `toStartOfHour()` for time bucketing
  - `countIf()` / `sumIf()` instead of filtered subqueries

### Performance Criteria
```
ch/pagination: keyset pagination used (not OFFSET) for all paginated endpoints (score 1-10)
ch/materialized: aggregation queries hit materialized view, not raw table (score 1-10)
ch/partition: query includes partition key in WHERE clause (date range filter present) (score 1-10)
ch/query-time: query runs in < Xms for Y-day window on production-scale data (score 1-10)
```

---

## SECTION 2 — CASSANDRA / SCYLLADB

### Data Modeling Rules
- **Query-first modeling**: write the queries first, design the table around them. Not schema-first.
- **One table per query pattern** — denormalization is expected and required.
- **Partition key**: must distribute evenly. If one partition grows > 100MB → re-model. Time-series: partition by `(device_id, year_month)` not just `device_id`.
- **Clustering columns**: define read sort order. Use for range queries within a partition.

### BANNED Patterns
- `ALLOW FILTERING` — full-table scan in disguise. Never in production queries.
- `SELECT COUNT(*)` without partition key — scans all nodes.
- Secondary indexes on high-cardinality columns — use materialized views instead.
- Unbounded partition growth (all events for a device in one partition) — add time bucket to partition key.

### Write Patterns
- Use `BATCH` only for atomicity across related tables, NOT for performance (batches are anti-patterns for throughput).
- TTL on time-series data: `INSERT ... USING TTL 86400` instead of manual DELETE.
- Lightweight transactions (`IF NOT EXISTS`) only where truly needed — they're expensive.

### Performance Criteria
```
cass/partition: partition key chosen for even distribution (verified with nodetool tablestats) (score 1-10)
cass/no-allow-filtering: no ALLOW FILTERING in any production query (score 1-10)
cass/ttl: time-series data has TTL set at write time (score 1-10)
cass/model: one query pattern = one table; no cross-partition queries in hot path (score 1-10)
```

---

## SECTION 3 — DYNAMODB

### Single-Table Design
- All entity types in one table. PK and SK encode entity type and relationships.
  - User: `PK=USER#<userId>`, `SK=PROFILE`
  - Order: `PK=USER#<userId>`, `SK=ORDER#<orderId>`
  - Product: `PK=PRODUCT#<productId>`, `SK=META`
- GSIs provide alternative access patterns. Design GSIs at modeling time, not after.

### BANNED Patterns
- `Scan` operation in production — reads entire table. Use Query always.
- Hot partition: writing many items with the same PK at high throughput. Add random shard suffix for high-write PKs: `PK=COUNTER#<name>#<shard 0-N>`.
- `TransactWriteItems` with > 25 items — DynamoDB limit.
- Using DynamoDB for full-text search — use Elasticsearch/OpenSearch for that.
- Manual DELETE loops for expiry — use TTL attribute instead.

### GSI Design
- GSI PK should have same cardinality as main table PK — avoid GSI hot partitions.
- Sparse GSIs: only set GSI PK attribute on items that need this access pattern (items without the attribute don't appear in GSI — saves cost).
- GSI replication is eventually consistent — reads may lag writes by seconds.

### Performance Criteria
```
dynamo/no-scan: no Scan operations in production code paths (score 1-10)
dynamo/gsi: GSI PK has high cardinality (no hot partition risk) (score 1-10)
dynamo/ttl: expiring data uses DynamoDB TTL attribute, not DELETE loops (score 1-10)
dynamo/single-table: entity types co-located in single table per access pattern design (score 1-10)
```

---

## VERIFIER GUIDANCE

ClickHouse:
```bash
# Check for OFFSET in queries
grep -r "OFFSET" src/analytics/ | grep -v "test" && echo "FAIL: OFFSET found" || echo "PASS"
# Query plan check (explain doesn't exit non-zero — must parse output)
clickhouse-client --query "EXPLAIN SELECT ..." | grep -i "full scan" && echo "WARN: full scan"
```

DynamoDB:
```bash
# Check for Scan in code
grep -r "\.scan(" src/ | grep -v "test" | grep -v "node_modules" && echo "FAIL: Scan found" || echo "PASS"
```
