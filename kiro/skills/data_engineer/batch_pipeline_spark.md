---
id: batch_pipeline_spark
version: 1.0.0
owners:
  - data_engineer
tags:
  - spark
  - batch
  - etl
  - pyspark
when_to_use: "When building large-scale batch ETL pipelines, data transformations over historical data, or scheduled data processing jobs using Apache Spark."
inputs:
  - source data location
  - transformation logic
  - output schema
  - schedule/SLA
outputs:
  - PySpark job
  - transformation code
  - job configuration
  - test suite
---

> "Batch is just streaming with a very long window."

## PySpark Job Structure

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType

def create_spark_session(app_name: str) -> SparkSession:
    return (SparkSession.builder
        .appName(app_name)
        .config("spark.sql.adaptive.enabled", "true")          # AQE — auto partition tuning
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
        .config("spark.sql.parquet.compression.codec", "snappy")
        .getOrCreate())

def run_orders_etl(spark: SparkSession, date: str) -> None:
    # Read with schema enforcement — no inference on production data
    schema = StructType([
        StructField("order_id", StringType(), nullable=False),
        StructField("customer_id", StringType(), nullable=False),
        StructField("amount", DoubleType(), nullable=True),
        StructField("created_at", TimestampType(), nullable=False),
    ])

    raw = (spark.read
        .schema(schema)
        .parquet(f"s3://data-lake/raw/orders/dt={date}/"))

    # Transform
    clean = (raw
        .filter(F.col("order_id").isNotNull())
        .filter(F.col("amount") > 0)
        .withColumn("date", F.to_date("created_at"))
        .withColumn("amount_usd", F.round(F.col("amount"), 2)))

    # Aggregate
    daily_revenue = (clean
        .groupBy("date", "customer_id")
        .agg(
            F.sum("amount_usd").alias("total_revenue"),
            F.count("order_id").alias("order_count"),
        ))

    # Write partitioned
    (daily_revenue.write
        .mode("overwrite")
        .partitionBy("date")
        .parquet("s3://data-lake/processed/daily_revenue/"))

if __name__ == "__main__":
    spark = create_spark_session("orders-etl")
    run_orders_etl(spark, date=sys.argv[1])
    spark.stop()
```

## Performance Tuning

```python
# 1. Partition sizing — target 128-256 MB per partition
df = df.repartition(200)   # explicit repartition for large datasets
# Or let AQE handle it with spark.sql.adaptive.enabled=true

# 2. Broadcast joins for small tables (< 10 MB)
from pyspark.sql.functions import broadcast
result = large_df.join(broadcast(small_lookup_df), "key")

# 3. Persist frequently reused DataFrames
df.persist(StorageLevel.MEMORY_AND_DISK)
# ... use df multiple times ...
df.unpersist()

# 4. Avoid UDFs when possible — use built-in functions
# BAD:  df.withColumn("x", udf(lambda x: x.upper())(col("x")))
# GOOD: df.withColumn("x", F.upper(col("x")))
```

## Data Quality Checks

```python
def validate_output(df, expected_min_rows: int) -> None:
    row_count = df.count()
    assert row_count >= expected_min_rows, f"Too few rows: {row_count}"
    null_amounts = df.filter(F.col("total_revenue").isNull()).count()
    assert null_amounts == 0, f"Null revenue values: {null_amounts}"
    assert df.filter(F.col("total_revenue") < 0).count() == 0, "Negative revenue found"
```

## Anti-Patterns

- **collect() on large datasets** — brings all data to driver, OOM
- **Schema inference in production** — slow and fragile; always define schema
- **Nested UDFs** — cannot be optimized by Catalyst; use native functions
- **No partitioning on write** — full table scan on every read downstream

## Validation Checklist

- [ ] Schema explicitly defined (no inferSchema in production)
- [ ] AQE enabled for dynamic partition tuning
- [ ] Output partitioned by date or appropriate key
- [ ] Data quality assertions run before overwrite
- [ ] Job is idempotent (re-runnable for the same date)
