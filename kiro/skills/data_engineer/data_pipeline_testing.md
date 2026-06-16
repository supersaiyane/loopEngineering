---
id: data_pipeline_testing
version: 1.0.0
owners:
  - data_engineer
tags:
  - testing
  - data-quality
  - pipeline
  - great-expectations
when_to_use: "When writing tests for data pipelines, validating data quality at pipeline boundaries, or building automated data contract checks."
inputs:
  - pipeline code
  - expected data schemas
  - business rules for data
outputs:
  - unit tests for transformations
  - data quality assertions
  - contract tests between pipeline stages
---

> "Data pipelines fail silently. Tests make the silence loud."

## Unit Testing Transformations (pytest + pandas)

```python
import pytest
import pandas as pd
from your_pipeline.transforms import clean_orders, compute_revenue

@pytest.fixture
def raw_orders():
    return pd.DataFrame({
        "order_id": ["O-1", "O-2", "O-3", None],
        "amount": [100.0, -50.0, 200.0, 100.0],
        "status": ["completed", "cancelled", "completed", "completed"],
    })

def test_clean_orders_removes_nulls(raw_orders):
    result = clean_orders(raw_orders)
    assert result["order_id"].notna().all()
    assert len(result) == 3   # null order_id row removed

def test_clean_orders_removes_negative_amounts(raw_orders):
    result = clean_orders(raw_orders)
    assert (result["amount"] >= 0).all()

def test_revenue_only_counts_completed(raw_orders):
    cleaned = clean_orders(raw_orders)
    revenue = compute_revenue(cleaned)
    assert revenue == 300.0   # only O-1 and O-3 (both completed, both positive)
```

## PySpark Unit Tests (pyspark.testing)

```python
from pyspark.testing.utils import assertDataFrameEqual
from pyspark.sql import Row

def test_daily_revenue_aggregation(spark):
    input_data = spark.createDataFrame([
        Row(order_id="O-1", region="US", amount=100.0, date="2026-01-01"),
        Row(order_id="O-2", region="US", amount=50.0, date="2026-01-01"),
        Row(order_id="O-3", region="EU", amount=200.0, date="2026-01-01"),
    ])
    expected = spark.createDataFrame([
        Row(region="EU", date="2026-01-01", total_revenue=200.0, order_count=1),
        Row(region="US", date="2026-01-01", total_revenue=150.0, order_count=2),
    ])
    result = compute_daily_revenue(input_data)
    assertDataFrameEqual(result.orderBy("region"), expected.orderBy("region"))
```

## Great Expectations — Data Contract

```python
import great_expectations as gx

context = gx.get_context()
batch = context.sources.pandas_default.read_dataframe(df)

results = batch.validate(
    expectation_suite=gx.ExpectationSuite(
        expectations=[
            gx.expectations.ExpectColumnValuesToNotBeNull(column="order_id"),
            gx.expectations.ExpectColumnValuesToBeBetween(column="amount", min_value=0, max_value=100000),
            gx.expectations.ExpectColumnValuesToBeInSet(column="status", value_set={"completed", "cancelled", "pending"}),
            gx.expectations.ExpectTableRowCountToBeBetween(min_value=1, max_value=10_000_000),
        ]
    )
)
assert results.success, f"Data quality failed: {results}"
```

## Anti-Patterns

- **Testing only happy path** — test null inputs, empty DataFrames, schema mismatches
- **Using production data in tests** — synthetic fixtures prevent PII leakage and flakiness
- **asserting on float equality** — use `pytest.approx` or round to 2 decimal places

## Validation Checklist

- [ ] Unit tests cover: null inputs, empty DataFrames, boundary values
- [ ] Great Expectations suite attached to pipeline output
- [ ] Tests run in CI before DAG deploys
- [ ] Schema contract test between producer and consumer stages
