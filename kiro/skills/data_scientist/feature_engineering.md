---
id: feature_engineering
version: 1.0.0
owners:
  - data_scientist
tags:
  - feature-engineering
  - ml
  - pandas
  - scikit-learn
when_to_use: "When preparing data for machine learning models, transforming raw features into model-ready inputs, or improving model performance through feature creation."
inputs:
  - raw DataFrame
  - target variable
  - feature hypotheses from domain knowledge
outputs:
  - feature pipeline
  - engineered feature set
  - feature importance analysis
---

> "Features beat algorithms. Garbage in, garbage out — no matter how sophisticated the model."

## Feature Engineering Pipeline (scikit-learn)

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
from sklearn.impute import SimpleImputer
import pandas as pd
import numpy as np

numeric_features = ["amount_usd", "days_since_last_order", "order_count_30d"]
categorical_features = ["customer_segment", "payment_method"]
ordinal_features = ["subscription_tier"]  # has natural order: free < pro < enterprise

numeric_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),   # median robust to outliers
    ("scaler", StandardScaler()),
])

categorical_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="constant", fill_value="unknown")),
    ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
])

ordinal_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OrdinalEncoder(categories=[["free", "pro", "enterprise"]])),
])

preprocessor = ColumnTransformer([
    ("num", numeric_transformer, numeric_features),
    ("cat", categorical_transformer, categorical_features),
    ("ord", ordinal_transformer, ordinal_features),
])
```

## Common Feature Transformations

```python
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # 1. Log transform for skewed numeric features
    df["log_amount"] = np.log1p(df["amount_usd"])      # log1p handles 0 values

    # 2. Date features
    df["signup_date"] = pd.to_datetime(df["signup_date"])
    df["account_age_days"] = (pd.Timestamp.now() - df["signup_date"]).dt.days
    df["signup_dayofweek"] = df["signup_date"].dt.dayofweek
    df["signup_month"] = df["signup_date"].dt.month

    # 3. Ratio features
    df["revenue_per_order"] = df["total_revenue"] / (df["order_count"] + 1)  # +1 avoids div-by-zero

    # 4. Rolling window features (requires sorted data)
    df = df.sort_values(["user_id", "date"])
    df["orders_last_7d"] = df.groupby("user_id")["order_id"].transform(
        lambda x: x.rolling("7D", on=df.loc[x.index, "date"]).count()
    )

    # 5. Binning
    df["amount_bucket"] = pd.qcut(df["amount_usd"], q=5, labels=["xs", "s", "m", "l", "xl"])

    return df
```

## Feature Importance (after fitting)

```python
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Get feature names from ColumnTransformer
feature_names = (
    numeric_features
    + list(preprocessor.named_transformers_["cat"]["encoder"].get_feature_names_out(categorical_features))
    + ordinal_features
)

importance_df = pd.DataFrame({
    "feature": feature_names,
    "importance": model.feature_importances_,
}).sort_values("importance", ascending=False)

print(importance_df.head(10))
```

## Anti-Patterns

- **Data leakage** — using future information to predict the past; always compute features from data available at prediction time
- **Scaling before split** — fit `StandardScaler` on train only, transform both train and test
- **Imputing with mean before outlier removal** — outliers distort mean imputation

## Validation Checklist

- [ ] No data leakage: all features computable at inference time from available data
- [ ] Train/test split done before any feature fitting (scaler, imputer, encoder)
- [ ] Missing value strategy documented per feature (median/mode/constant/model-impute)
- [ ] Feature importance computed and top 10 reviewed with domain expert
- [ ] Correlation matrix checked — highly correlated features considered for removal
