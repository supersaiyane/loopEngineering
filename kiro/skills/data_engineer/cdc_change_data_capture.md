---
id: cdc_change_data_capture
version: 1.0.0
owners:
  - data_engineer
tags:
  - cdc
  - debezium
  - replication
  - streaming
when_to_use: "When replicating database changes to a data warehouse or event stream in real-time, or when implementing event sourcing from an existing OLTP database."
inputs:
  - source database type
  - tables to replicate
  - target (Kafka/warehouse)
  - latency requirement
outputs:
  - Debezium connector config
  - Kafka topic design for CDC events
  - sink connector config
  - schema evolution plan
---

> "CDC turns your database into an event log. The database was always an event log."

## Debezium PostgreSQL Connector

```json
{
  "name": "orders-cdc-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "debezium_user",
    "database.password": "${file:/opt/kafka/config/secrets.properties:db.password}",
    "database.dbname": "ecommerce",
    "database.server.name": "ecommerce",
    "table.include.list": "public.orders,public.customers",
    "plugin.name": "pgoutput",
    "slot.name": "debezium_slot",
    "publication.name": "debezium_pub",
    "heartbeat.interval.ms": "10000",
    "decimal.handling.mode": "double",
    "transforms": "unwrap",
    "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
    "transforms.unwrap.add.fields": "op,ts_ms",
    "transforms.unwrap.delete.handling.mode": "rewrite"
  }
}
```

## CDC Event Structure

```json
{
  "before": {"order_id": "O-1", "status": "pending"},
  "after":  {"order_id": "O-1", "status": "completed"},
  "op": "u",          // c=create, u=update, d=delete, r=read (snapshot)
  "ts_ms": 1700000000000,
  "source": {"table": "orders", "lsn": 12345}
}
```

## Sink: BigQuery via Kafka Connect

```json
{
  "name": "orders-bq-sink",
  "config": {
    "connector.class": "com.wepay.kafka.connect.bigquery.BigQuerySinkConnector",
    "topics": "ecommerce.public.orders",
    "project": "my-project",
    "defaultDataset": "cdc_raw",
    "autoCreateTables": "true",
    "allowNewBigQueryFields": "true",
    "upsertEnabled": "true",
    "deleteEnabled": "true",
    "mergeIntervalMs": "60000"
  }
}
```

## Postgres Prerequisites

```sql
-- Logical replication must be enabled
ALTER SYSTEM SET wal_level = logical;
ALTER SYSTEM SET max_replication_slots = 10;
ALTER SYSTEM SET max_wal_senders = 10;

-- Grant permissions to Debezium user
CREATE ROLE debezium_user WITH LOGIN REPLICATION PASSWORD '...';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO debezium_user;

-- Create publication
CREATE PUBLICATION debezium_pub FOR TABLE public.orders, public.customers;
```

## Anti-Patterns

- **No heartbeat configured** — idle connectors lose their replication slot silently
- **Using pglogical plugin** — use `pgoutput` (built into Postgres 10+)
- **Replication slot accumulates WAL** — set `max_slot_wal_keep_size` to prevent disk fill

## Validation Checklist

- [ ] Replication slot name is unique per connector
- [ ] Heartbeat interval set (prevents slot lag on quiet tables)
- [ ] `max_slot_wal_keep_size` configured on source DB
- [ ] Schema registry enforced for CDC topics
- [ ] Delete handling mode matches downstream requirements (`rewrite` or `none`)
