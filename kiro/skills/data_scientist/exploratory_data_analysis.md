---
id: exploratory_data_analysis
version: 1.0.0
owners:
  - data_scientist
tags:
  - eda
  - pandas
  - data-exploration
  - statistics
when_to_use: "When first encountering a new dataset, before building models, or when diagnosing data quality issues."
inputs:
  - raw dataset (CSV, parquet, SQL table)
  - business question to investigate
outputs:
  - data quality report
  - distribution plots
  - correlation analysis
  - key findings summary
---

> "Before you model, you must understand. Before you understand, you must look."

## Systematic EDA Template

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

def quick_eda(df: pd.DataFrame, target_col: str = None) -> None:
    print("=" * 60)
    print(f"SHAPE: {df.shape[0]:,} rows × {df.shape[1]} columns")
    print("=" * 60)

    # 1. Data types + nulls
    summary = pd.DataFrame({
        "dtype": df.dtypes,
        "null_count": df.isnull().sum(),
        "null_pct": (df.isnull().sum() / len(df) * 100).round(1),
        "unique": df.nunique(),
        "sample": df.iloc[0],
    })
    print("
COLUMN SUMMARY:")
    print(summary.to_string())

    # 2. Numeric distributions
    print("
NUMERIC STATS:")
    print(df.describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]).round(2))

    # 3. Duplicate detection
    dup_count = df.duplicated().sum()
    print(f"
DUPLICATES: {dup_count:,} ({dup_count/len(df)*100:.1f}%)")

    # 4. Target variable analysis (if provided)
    if target_col and target_col in df.columns:
        print(f"
TARGET ({target_col}) distribution:")
        if df[target_col].dtype in ['object', 'category', 'bool']:
            print(df[target_col].value_counts(normalize=True).mul(100).round(1))
        else:
            print(df[target_col].describe())
            skewness = df[target_col].skew()
            print(f"Skewness: {skewness:.2f} {'(consider log transform)' if abs(skewness) > 1 else ''}")

def plot_distributions(df: pd.DataFrame, cols: list, bins: int = 30) -> None:
    fig, axes = plt.subplots(len(cols), 2, figsize=(14, 4 * len(cols)))
    for i, col in enumerate(cols):
        df[col].hist(bins=bins, ax=axes[i, 0])
        axes[i, 0].set_title(f"{col} — histogram")
        stats.probplot(df[col].dropna(), plot=axes[i, 1])
        axes[i, 1].set_title(f"{col} — QQ plot")
    plt.tight_layout()

def correlation_heatmap(df: pd.DataFrame) -> None:
    numeric_df = df.select_dtypes(include=np.number)
    mask = np.triu(np.ones_like(numeric_df.corr(), dtype=bool))
    plt.figure(figsize=(10, 8))
    sns.heatmap(numeric_df.corr(), mask=mask, annot=True, fmt=".2f", cmap="RdBu_r", center=0)
    plt.title("Correlation Matrix")
    plt.tight_layout()
```

## Outlier Detection

```python
def detect_outliers_iqr(series: pd.Series) -> pd.Series:
    Q1, Q3 = series.quantile(0.25), series.quantile(0.75)
    IQR = Q3 - Q1
    return (series < Q1 - 1.5 * IQR) | (series > Q3 + 1.5 * IQR)

def detect_outliers_zscore(series: pd.Series, threshold: float = 3.0) -> pd.Series:
    return (np.abs(stats.zscore(series.dropna())) > threshold)
```

## Validation Checklist

- [ ] Null rates documented per column — columns > 20% null flagged for discussion
- [ ] Duplicates checked (exact + near-duplicate on key columns)
- [ ] Date range verified — no future dates, no dates before product launched
- [ ] Numeric columns checked for impossible values (negative ages, >100% rates)
- [ ] Target variable distribution understood (class balance, skewness)
