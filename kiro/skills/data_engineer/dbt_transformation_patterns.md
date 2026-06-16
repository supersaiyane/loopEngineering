---
id: dbt_transformation_patterns
version: 1.0.0
owners:
  - data_engineer
tags:
  - dbt
  - sql
  - transformation
  - data-modeling
when_to_use: "When building SQL-based data transformations, maintaining a layered data model (staging/intermediate/mart), or managing transformation dependencies in a data warehouse."
inputs:
  - source system schemas
  - business metric definitions
  - warehouse dialect (BigQuery/Snowflake/Redshift)
outputs:
  - dbt model files
  - schema.yml with tests
  - sources.yml
  - documentation
---

> "dbt is version control for your data transformations."

## Layered Architecture

```
sources/          ← raw tables, defined in sources.yml
models/
  staging/        ← stg_*.sql: 1:1 with sources, light cleaning only
  intermediate/   ← int_*.sql: business logic, joins, deduplication
  marts/          ← fct_*.sql (facts), dim_*.sql (dimensions)
```

## Staging Model Pattern

```sql
-- models/staging/stg_orders.sql
-- Purpose: clean and rename raw columns only. No business logic here.
with source as (
    select * from {{ source('ecommerce', 'orders') }}
),
renamed as (
    select
        order_id::varchar        as order_id,
        customer_id::varchar     as customer_id,
        amount_cents / 100.0     as amount_usd,
        status::varchar          as status,
        created_at::timestamp    as created_at,
        _loaded_at               as _loaded_at
    from source
    where order_id is not null   -- only structural filter here
)
select * from renamed
```

## Intermediate / Fact Model Pattern

```sql
-- models/marts/fct_orders.sql
with orders as (
    select * from {{ ref('stg_orders') }}
),
customers as (
    select * from {{ ref('dim_customers') }}
),
final as (
    select
        o.order_id,
        o.customer_id,
        c.customer_segment,
        o.amount_usd,
        o.status,
        case
            when o.status = 'completed' then o.amount_usd
            else 0
        end as revenue_usd,
        o.created_at,
        date_trunc('day', o.created_at) as order_date
    from orders o
    left join customers c using (customer_id)
)
select * from final
```

## Schema Tests (schema.yml)

```yaml
models:
  - name: fct_orders
    description: "One row per order with customer and revenue attributes"
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      - name: amount_usd
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 100000
      - name: status
        tests:
          - accepted_values:
              values: ['pending', 'completed', 'cancelled', 'refunded']
```

## Incremental Models

```sql
-- models/marts/fct_orders.sql
{{ config(
    materialized='incremental',
    unique_key='order_id',
    incremental_strategy='merge',       -- upsert on unique_key
    on_schema_change='append_new_columns'
) }}

with orders as (
    select * from {{ ref('stg_orders') }}
    {% if is_incremental() %}
    where created_at > (select max(created_at) from {{ this }})
    {% endif %}
)
select * from orders
```

## Anti-Patterns

- **Business logic in staging models** — staging = rename + cast only
- **Hardcoded table references** — always use `{{ ref() }}` and `{{ source() }}`
- **No tests on primary keys** — silent duplicates break downstream models
- **Materializing everything as table** — use views for staging, tables for marts

## Validation Checklist

- [ ] Every model uses `{{ ref() }}` or `{{ source() }}` — no hardcoded table names
- [ ] All primary keys have `unique` + `not_null` tests
- [ ] Incremental models have `unique_key` defined
- [ ] `dbt test` passes in CI before merge
- [ ] Model descriptions written in schema.yml
