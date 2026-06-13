---
id: database_migrations_cicd
version: 1.0.0
owners: [devops_engineer, senior_engineer_be]
tags: [database, migrations, cicd, zero-downtime, flyway, alembic, schema-change, rollback]
when_to_use: |
  Every database schema change in a production system with CI/CD.
  Zero-downtime deployments require the migration to be compatible with
  the old code AND the new code simultaneously during rollout.
inputs:
  - database_type, deployment_strategy, migration_tool, table_sizes
outputs:
  - "migration_plan: expand-contract steps + CI integration + rollback strategy"
---

# Database Migrations in CI/CD

> The most dangerous moment in a deploy is when new code runs against old schema
> or old code runs against new schema. Zero-downtime = no such moment exists.

## Expand-contract pattern (zero-downtime)

Never: rename column in one migration. The old code reads the old name; it breaks.

Instead, use expand-contract:

```
Step 1 (Expand): Add new column. Old code ignores it. New code writes to both.
  ALTER TABLE orders ADD COLUMN customer_ref VARCHAR(100);
  -- Deploy new code that writes to both order_id AND customer_ref

Step 2 (Migrate data): Backfill new column.
  UPDATE orders SET customer_ref = customer_id WHERE customer_ref IS NULL;

Step 3 (Contract): Remove old column once no code reads it.
  ALTER TABLE orders DROP COLUMN customer_id;
```

This takes 3 deploys but is safe at every step.

## Migration tooling

**Alembic (Python/SQLAlchemy)**:
```python
# alembic/versions/2026_01_15_add_customer_ref.py
def upgrade():
    op.add_column("orders", sa.Column("customer_ref", sa.String(100), nullable=True))
    # Index creation: CONCURRENTLY to avoid lock
    op.execute("CREATE INDEX CONCURRENTLY idx_orders_customer_ref ON orders(customer_ref)")

def downgrade():
    op.drop_index("idx_orders_customer_ref")
    op.drop_column("orders", "customer_ref")
```

**Flyway (Java/any)**:
```sql
-- V20260115__add_customer_ref.sql
ALTER TABLE orders ADD COLUMN customer_ref VARCHAR(100);
CREATE INDEX CONCURRENTLY idx_orders_customer_ref ON orders(customer_ref);
```

## CI pipeline integration

```yaml
# .github/workflows/deploy.yml
jobs:
  migrate:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Run migrations
        run: |
          # Apply pending migrations
          alembic upgrade head

          # Verify: check current revision matches expected
          ACTUAL=$(alembic current 2>&1 | grep -o '[a-f0-9]*')
          EXPECTED=$(cat .alembic_head)
          if [ "$ACTUAL" != "$EXPECTED" ]; then
            echo "Migration mismatch: got $ACTUAL, expected $EXPECTED"
            exit 1
          fi

  deploy-app:
    needs: migrate   # app deploys AFTER migrations succeed
    runs-on: ubuntu-latest
    steps:
      - name: Deploy application
        run: kubectl rollout restart deployment/api-service
```

## Large table migrations

For tables > 1M rows:
```sql
-- NEVER: adds table lock for minutes
ALTER TABLE orders ADD COLUMN archived BOOLEAN DEFAULT FALSE;

-- INSTEAD: add nullable column first (instant)
ALTER TABLE orders ADD COLUMN archived BOOLEAN;  -- no default = no rewrite

-- Backfill in batches (no lock contention)
DO $$
DECLARE batch_size INT := 10000;
DECLARE offset_val INT := 0;
BEGIN
  LOOP
    UPDATE orders SET archived = FALSE
    WHERE id IN (
      SELECT id FROM orders WHERE archived IS NULL LIMIT batch_size
    );
    EXIT WHEN NOT FOUND;
    PERFORM pg_sleep(0.1);  -- small pause between batches
  END LOOP;
END $$;

-- After backfill: set NOT NULL (fast metadata operation)
ALTER TABLE orders ALTER COLUMN archived SET NOT NULL;
ALTER TABLE orders ALTER COLUMN archived SET DEFAULT FALSE;
```

## Rollback strategy

```bash
# Alembic: rollback one migration
alembic downgrade -1

# Verify downgrade scripts exist for every migration (CI check)
# The expand-contract pattern makes most migrations forward-only safe
# Destructive changes (DROP COLUMN) are irreversible -- take a backup first
```

## Anti-patterns

- **Renaming columns in one step**: breaks old code that reads the old name.
- **Synchronous backfill on large tables**: full table scan with lock = downtime.
- **Migrations without downgrade scripts**: you cannot roll back safely.
- **App deploys before migration runs**: new code hits old schema = errors.
- **No migration in version control**: hand-applied SQL changes are untracked.

## Validation

- [ ] Every migration has a tested downgrade script.
- [ ] Large table changes use batched backfill.
- [ ] Index creation uses CONCURRENTLY (Postgres) to avoid table lock.
- [ ] Migrations run before app deploy in CI pipeline.
- [ ] Expand-contract pattern followed for rename/type changes.
