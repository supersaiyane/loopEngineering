---
id: database_performance_tuning
version: 1.0.0
owners: [database_architect, senior_engineer_be]
tags: [performance, indexing, query-optimization, explain, vacuum, connection-pool, postgres]
when_to_use: |
  When queries are slow, CPU/IO is high on the database, or the application
  is experiencing timeouts. Also run proactively before a traffic spike or
  before a table grows beyond 10M rows.
inputs:
  - slow_queries, table_sizes, index_usage_stats, connection_count
outputs:
  - "tuning_report: slow query diagnosis + index recommendations + config changes"
---

# Database Performance Tuning

> You cannot optimize what you have not measured.
> Always start with EXPLAIN ANALYZE, never with assumptions.

## Step 1: Find the slow queries

```sql
-- Postgres: top 10 slowest queries (requires pg_stat_statements)
SELECT
    query,
    calls,
    total_exec_time / calls AS avg_ms,
    rows / calls AS avg_rows,
    stddev_exec_time AS stddev_ms
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;

-- Long-running queries right now
SELECT pid, now() - query_start AS duration, state, query
FROM pg_stat_activity
WHERE state != 'idle' AND query_start < now() - interval '30 seconds'
ORDER BY duration DESC;
```

## Step 2: EXPLAIN ANALYZE

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT u.name, COUNT(o.id) as order_count
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE u.created_at > '2026-01-01'
GROUP BY u.id;
```

**What to look for:**
- `Seq Scan` on large tables → missing index.
- `Hash Join` with large row estimates → consider index.
- `Buffers: hit=X read=Y` → high Y = disk I/O, check cache.
- Rows estimated vs actual: large discrepancy → stale statistics → run ANALYZE.

## Step 3: Index strategy

```sql
-- Single column index
CREATE INDEX CONCURRENTLY idx_orders_user_id ON orders(user_id);

-- Composite index (column order matters: equality first, then range)
CREATE INDEX CONCURRENTLY idx_orders_user_status ON orders(user_id, status)
WHERE status != 'completed';   -- partial index: exclude completed orders

-- Covering index (include all columns the query needs)
CREATE INDEX CONCURRENTLY idx_orders_covering
ON orders(user_id, created_at DESC)
INCLUDE (total_amount, status);  -- avoids heap fetch

-- Check index usage
SELECT indexrelname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
WHERE relname = 'orders'
ORDER BY idx_scan ASC;          -- low scan count = unused index → remove it
```

## Step 4: Connection pooling

Raw connections are expensive (~5MB RAM each, slow to create).
Use PgBouncer in transaction mode.

```ini
# pgbouncer.ini
[databases]
mydb = host=postgres port=5432 dbname=mydb

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20           # connections to Postgres
min_pool_size = 5
```

Application connects to PgBouncer (port 6432), not Postgres directly.
20 Postgres connections serve 1000 application threads.

## Step 5: Maintenance

```sql
-- Check table bloat
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
       n_dead_tup AS dead_rows
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;

-- Manual VACUUM if autovacuum not keeping up
VACUUM ANALYZE orders;

-- Reindex if index bloat > 30%
REINDEX INDEX CONCURRENTLY idx_orders_user_id;
```

## Key Postgres config parameters

```
shared_buffers = 25% of RAM              # buffer cache
effective_cache_size = 75% of RAM        # planner hint for cache
work_mem = 64MB                          # per-sort/hash operation (careful: per connection)
maintenance_work_mem = 512MB             # for VACUUM, index builds
max_connections = 100                    # use PgBouncer, not a high value here
random_page_cost = 1.1                   # for SSD (default 4 is for spinning disk)
```

## Anti-patterns

- **Adding indexes blindly**: every index slows down writes. Add only what EXPLAIN shows is needed.
- **`SELECT *` on wide tables**: fetches columns you don't need, wastes I/O.
- **`LIKE '%term%'`**: can't use a B-tree index. Use full-text search or pg_trgm.
- **N+1 queries**: querying in a loop. Use JOINs or batch queries.
- **High `max_connections`**: each connection uses RAM. Use PgBouncer instead.
- **No connection pooling in serverless**: every Lambda/function creates a new connection.

## Validation

- [ ] pg_stat_statements enabled. Top 10 slow queries reviewed weekly.
- [ ] All foreign keys have indexes.
- [ ] EXPLAIN ANALYZE run on any query touching > 100K rows.
- [ ] PgBouncer (or equivalent) in front of Postgres.
- [ ] Autovacuum keeping up (dead_rows < 10% of live rows).
- [ ] random_page_cost set to 1.1 for SSD storage.
