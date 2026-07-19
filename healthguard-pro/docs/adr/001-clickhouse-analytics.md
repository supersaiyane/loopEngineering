# ADR-001: ClickHouse for Population Health Analytics

**Date:** 2026-07-17  
**Status:** Accepted  

## Context

Population health analytics requires aggregating vitals, sepsis scores, and alert events across millions of patient-records per hospital network. PostgreSQL OLTP queries at this scale (10B+ rows/day at 500-hospital scale) would be prohibitively slow.

## Decision

Use ClickHouse as the analytics warehouse. PostgreSQL remains the OLTP store for transactional data.

## Rationale

- Column-store: 10–100x faster aggregation vs row-store for analytical queries
- Materialized views: pre-aggregate hourly vitals rollups automatically
- PARTITION BY (month, tenant_id): tenant isolation at storage level
- TTL clauses: HIPAA/GDPR retention enforced at engine level
- ClickHouse Cloud available if self-hosted ops burden is too high

## Alternatives Rejected

| Option | Rejected because |
|--------|-----------------|
| PostgreSQL + TimescaleDB | Aggregation speed insufficient at 10B+ rows |
| Amazon Redshift | Higher cost, no MergeTree TTL, vendor lock-in |
| BigQuery | EU data residency complexity, per-query cost unpredictable |

## Consequences

✅ Sub-second aggregations at billion-row scale  
✅ GDPR TTL enforced at engine level — no application-layer cleanup needed  
✅ Tenant isolation via PARTITION BY tenant_id  
⚠️ Eventual consistency (MergeTree merges happen async)  
⚠️ No UPDATE/DELETE semantics (use CollapsingMergeTree for corrections)  
⚠️ Schema migrations require careful coordination  

## Implementation

Library: `github.com/ClickHouse/clickhouse-go/v2` (Rung 2, MIT)  
Service: `analytics-ingestion-service` (Go) writes to ClickHouse  
Schema: [docs/schema/clickhouse.sql](../schema/clickhouse.sql)
