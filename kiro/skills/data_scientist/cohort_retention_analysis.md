---
id: cohort_retention_analysis
version: 1.0.0
owners:
  - data_scientist
tags:
  - retention
  - cohort
  - user-behavior
  - churn
when_to_use: "When analyzing user retention curves, identifying churn patterns, or comparing retention across acquisition cohorts."
inputs:
  - user signup dates
  - activity/event data with timestamps
  - cohort definition
outputs:
  - retention matrix
  - retention curve plot
  - cohort comparison
  - churn analysis
---

> "Retention is the product metric. Everything else is a leading indicator."

## Cohort Retention Matrix

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def build_retention_matrix(events: pd.DataFrame, date_col: str = "event_date", user_col: str = "user_id") -> pd.DataFrame:
    """
    events: DataFrame with user_id and event_date columns (one row per activity)
    Returns: cohort × period retention matrix (%)
    """
    events[date_col] = pd.to_datetime(events[date_col])

    # Assign users to cohorts by first activity month
    cohort_df = events.groupby(user_col)[date_col].min().reset_index()
    cohort_df.columns = [user_col, "cohort_month"]
    cohort_df["cohort_month"] = cohort_df["cohort_month"].dt.to_period("M")

    events = events.merge(cohort_df, on=user_col)
    events["period"] = (events[date_col].dt.to_period("M") - events["cohort_month"]).apply(lambda x: x.n)

    cohort_sizes = cohort_df.groupby("cohort_month")[user_col].nunique()
    retention = events.groupby(["cohort_month", "period"])[user_col].nunique().reset_index()
    retention.columns = ["cohort_month", "period", "users"]
    retention = retention.pivot(index="cohort_month", columns="period", values="users")
    retention = retention.divide(cohort_sizes, axis=0).mul(100).round(1)

    return retention

def plot_retention_heatmap(retention_matrix: pd.DataFrame) -> None:
    plt.figure(figsize=(14, 8))
    sns.heatmap(
        retention_matrix,
        annot=True, fmt=".0f",
        cmap="YlOrRd_r",
        vmin=0, vmax=100,
        cbar_kws={"label": "Retention (%)"},
    )
    plt.title("Monthly Cohort Retention (%)")
    plt.xlabel("Months Since First Activity")
    plt.ylabel("Cohort Month")
    plt.tight_layout()
```

## Retention Curve (D1, D7, D30)

```python
def compute_day_n_retention(events: pd.DataFrame, user_col: str, date_col: str, n: int) -> float:
    events[date_col] = pd.to_datetime(events[date_col])
    first_seen = events.groupby(user_col)[date_col].min().reset_index()
    first_seen.columns = [user_col, "first_seen"]
    events = events.merge(first_seen, on=user_col)
    events["days_since_first"] = (events[date_col] - events["first_seen"]).dt.days
    day_n_users = events[events["days_since_first"] == n][user_col].nunique()
    total_users = first_seen[user_col].nunique()
    return round(day_n_users / total_users * 100, 2)

# Benchmarks by product type
benchmarks = {
    "D1": {"social": 25, "ecommerce": 35, "saas_b2b": 60},
    "D7": {"social": 10, "ecommerce": 15, "saas_b2b": 40},
    "D30": {"social": 5, "ecommerce": 8, "saas_b2b": 25},
}
```

## Anti-Patterns

- **Cohort by acquisition channel without controlling for signup date** — mixes time effects with channel effects
- **Using calendar month as period for apps** — use relative period (Day 0, Day 1, Day 7) not absolute dates
- **Reporting average retention** — always show retention by cohort; averages hide degrading new cohorts

## Validation Checklist

- [ ] Cohort defined by first meaningful action (not just signup)
- [ ] Retention matrix shows at least 6 cohort rows for trend detection
- [ ] D1 / D7 / D30 computed and compared to industry benchmarks
- [ ] New cohorts vs old cohorts compared to detect product regression
