---
id: data_quality_great_expectations
version: 1.0.0
owners:
  - data_engineer
tags:
  - data-quality
  - great-expectations
  - validation
  - monitoring
when_to_use: "When implementing data quality checks at pipeline boundaries, building data contracts between teams, or alerting on data anomalies before they reach dashboards."
inputs:
  - DataFrame or SQL table
  - expected schema
  - business rules (nulls, ranges, distributions)
outputs:
  - Expectation Suite
  - validation results
  - Data Docs site
  - CI integration
---

> "Data quality is not a feature — it is the absence of silent failures."

## Core Setup

```python
import great_expectations as gx

context = gx.get_context()

# Connect to data source
datasource = context.sources.add_pandas("my_datasource")
asset = datasource.add_dataframe_asset("orders")
batch_request = asset.build_batch_request(dataframe=df)
```

## Expectation Suite

```python
suite = context.add_expectation_suite("orders.critical")

validator = context.get_validator(
    batch_request=batch_request,
    expectation_suite_name="orders.critical",
)

# Schema expectations
validator.expect_column_to_exist("order_id")
validator.expect_column_values_to_not_be_null("order_id")
validator.expect_column_values_to_be_unique("order_id")

# Value range
validator.expect_column_values_to_be_between("amount_usd", min_value=0, max_value=100_000)

# Categorical
validator.expect_column_values_to_be_in_set(
    "status", {"pending", "completed", "cancelled", "refunded"}
)

# Volume — catch truncated loads
validator.expect_table_row_count_to_be_between(min_value=1_000, max_value=5_000_000)

# Distribution — catch data drift
validator.expect_column_mean_to_be_between("amount_usd", min_value=50, max_value=500)

validator.save_expectation_suite()
```

## Checkpoint (Run in CI/CD)

```python
checkpoint = context.add_or_update_checkpoint(
    name="orders_daily_checkpoint",
    validations=[{
        "batch_request": batch_request,
        "expectation_suite_name": "orders.critical",
    }],
    action_list=[
        {"name": "store_validation_result", "action": {"class_name": "StoreValidationResultAction"}},
        {"name": "update_data_docs", "action": {"class_name": "UpdateDataDocsAction"}},
        {
            "name": "slack_notification",
            "action": {
                "class_name": "SlackNotificationAction",
                "slack_webhook": "${SLACK_WEBHOOK}",
                "notify_on": "failure",
            }
        },
    ],
)

results = checkpoint.run()
assert results.success, "Data quality validation failed — pipeline halted"
```

## SQL-Based Expectations (for warehouse data)

```python
datasource = context.sources.add_sql(
    name="warehouse",
    connection_string="postgresql+psycopg2://user:pass@host/db",
)
asset = datasource.add_table_asset("orders", schema_name="public")
# Same expectation API works against SQL tables
```

## Anti-Patterns

- **Running GE only in dev** — attach checkpoint to every production pipeline run
- **Too many expectations** — focus on the 5 rules that would actually cause a business incident
- **Ignoring distribution expectations** — row count and mean catch the most silent failures

## Validation Checklist

- [ ] Expectation suite covers: nulls, uniqueness, value ranges, row count bounds
- [ ] Checkpoint wired to pipeline (runs on every execution, not just ad-hoc)
- [ ] Slack/PagerDuty alert on failure
- [ ] Data Docs auto-published for stakeholder visibility
- [ ] Volume expectations updated as data grows (not hardcoded at launch values)
