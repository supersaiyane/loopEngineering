---
id: airflow_dag_design
version: 1.0.0
owners:
  - data_engineer
tags:
  - airflow
  - orchestration
  - scheduling
  - dag
when_to_use: "When orchestrating data pipelines, scheduling batch jobs, managing dependencies between pipeline steps, or building workflow automation with Apache Airflow."
inputs:
  - pipeline steps and dependencies
  - schedule/SLA requirements
  - failure handling policy
outputs:
  - DAG file
  - task definitions
  - alerting config
  - idempotency design
---

> "A DAG is a promise about what will run and when. Make it a promise you can keep."

## DAG Structure Template

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.utils.task_group import TaskGroup

DEFAULT_ARGS = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email_on_failure": True,
    "email": ["data-alerts@company.com"],
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(hours=2),
}

with DAG(
    dag_id="orders_etl_daily",
    description="Load and transform daily orders from source to data warehouse",
    schedule_interval="0 6 * * *",          # 6 AM UTC daily
    start_date=datetime(2026, 1, 1),
    catchup=False,                           # don't backfill on first deploy
    max_active_runs=1,                       # prevent overlapping runs
    default_args=DEFAULT_ARGS,
    tags=["orders", "etl", "daily"],
) as dag:

    with TaskGroup("extract") as extract_group:
        extract_orders = PythonOperator(
            task_id="extract_orders",
            python_callable=extract_orders_from_source,
            op_kwargs={"date": "{{ ds }}"},  # use template — not datetime.now()
        )

    with TaskGroup("transform") as transform_group:
        run_dbt = BashOperator(
            task_id="run_dbt_models",
            bash_command="dbt run --select tag:orders --target prod",
        )
        run_dbt_tests = BashOperator(
            task_id="run_dbt_tests",
            bash_command="dbt test --select tag:orders --target prod",
        )
        run_dbt >> run_dbt_tests

    with TaskGroup("load") as load_group:
        update_dashboard = PythonOperator(
            task_id="refresh_dashboard_cache",
            python_callable=refresh_cache,
        )

    extract_group >> transform_group >> load_group
```

## Idempotency Rules

```python
# Every task MUST be idempotent — safe to re-run for the same logical date
# BAD: appending to a table without checking for existing data
def load_orders_bad(date):
    df = load(date)
    df.to_sql("orders", if_exists="append")   # duplicates on retry

# GOOD: merge/upsert or delete-then-insert
def load_orders_good(date):
    delete_existing(date)                      # clean state
    df = load(date)
    df.to_sql("orders", if_exists="append")   # safe retry
```

## SLA + Alerting

```python
from airflow.models.slaalmiss import SlaMiss

with DAG(
    ...,
    sla_miss_callback=notify_pagerduty,
) as dag:
    critical_transform = PythonOperator(
        task_id="critical_transform",
        python_callable=run_transform,
        sla=timedelta(hours=1),    # alert if this task hasn't completed in 1h
    )
```

## Anti-Patterns

- **`datetime.now()` in tasks** — use `{{ ds }}` or `{{ execution_date }}` Jinja templates
- **`catchup=True` on new DAGs** — triggers backfill runs from `start_date` immediately
- **`max_active_runs` unlimited** — concurrent runs for same DAG corrupt shared state
- **Fat operators** — each task should do one thing; split long scripts into steps

## Validation Checklist

- [ ] All tasks are idempotent (safe to re-run for same `ds`)
- [ ] `catchup=False` on new DAGs until backfill strategy is decided
- [ ] `max_active_runs=1` for pipelines with shared downstream state
- [ ] SLA defined on critical path tasks
- [ ] `{{ ds }}` used instead of `datetime.now()`
