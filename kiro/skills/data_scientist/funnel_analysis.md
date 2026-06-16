---
id: funnel_analysis
version: 1.0.0
owners:
  - data_scientist
tags:
  - funnel
  - conversion
  - user-behavior
  - drop-off
when_to_use: "When analyzing where users drop off in a conversion flow, measuring step-by-step conversion rates, or identifying optimization opportunities."
inputs:
  - event data with step names and timestamps
  - funnel definition (ordered steps)
outputs:
  - conversion rates per step
  - drop-off waterfall chart
  - time-to-convert distribution
  - segment comparison
---

> "A funnel shows where people leave. The real question is why."

## Funnel Computation

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def compute_funnel(
    events: pd.DataFrame,
    user_col: str,
    event_col: str,
    date_col: str,
    steps: list[str],
    window_days: int = 30,
) -> pd.DataFrame:
    """
    Strict ordered funnel: user must complete each step after the previous one,
    within window_days of completing the first step.
    """
    events[date_col] = pd.to_datetime(events[date_col])
    step_users = []
    current_users = None

    for i, step in enumerate(steps):
        step_events = events[events[event_col] == step][[user_col, date_col]].copy()
        step_events = step_events.sort_values(date_col).drop_duplicates(subset=user_col, keep="first")

        if i == 0:
            current_users = step_events.rename(columns={date_col: f"{step}_date"})
        else:
            prev_step = steps[i - 1]
            current_users = current_users.merge(
                step_events.rename(columns={date_col: f"{step}_date"}),
                on=user_col, how="inner"
            )
            # Enforce ordering and time window
            current_users = current_users[
                current_users[f"{step}_date"] >= current_users[f"{prev_step}_date"]
            ]
            if window_days:
                current_users = current_users[
                    (current_users[f"{step}_date"] - current_users[f"{steps[0]}_date"]).dt.days <= window_days
                ]

        step_users.append(len(current_users))

    funnel = pd.DataFrame({
        "step": steps,
        "users": step_users,
        "conversion_from_top": [n / step_users[0] * 100 for n in step_users],
        "step_conversion": [100.0] + [step_users[i] / step_users[i-1] * 100 for i in range(1, len(steps))],
        "drop_off_pct": [0.0] + [100 - step_users[i] / step_users[i-1] * 100 for i in range(1, len(steps))],
    })
    return funnel.round(1)

def plot_funnel_waterfall(funnel: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ["#2196F3" if v >= 70 else "#FF9800" if v >= 50 else "#F44336"
              for v in funnel["conversion_from_top"]]
    bars = ax.bar(funnel["step"], funnel["users"], color=colors)
    for bar, row in zip(bars, funnel.itertuples()):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 50,
                f"{row.conversion_from_top:.0f}%
({row.users:,})",
                ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.set_title("Conversion Funnel")
    ax.set_ylabel("Users")
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
```

## Segment Comparison

```python
def compare_funnel_segments(events: pd.DataFrame, segment_col: str, ...) -> None:
    """Compare funnel conversion across user segments."""
    for segment, group in events.groupby(segment_col):
        funnel = compute_funnel(group, ...)
        print(f"
--- {segment} ---")
        print(funnel[["step", "step_conversion"]].to_string(index=False))
```

## Anti-Patterns

- **Unordered funnel** — treating step completion as independent (users can skip steps in the data)
- **No time window** — a user converting step 1 and step 5 six months apart is not the same journey
- **Ignoring segment differences** — mobile vs desktop, new vs returning users often have very different funnels

## Validation Checklist

- [ ] Steps are ordered with time window enforced
- [ ] Each step counts unique users (not events)
- [ ] Biggest drop-off step identified and labeled
- [ ] Funnel compared across key segments (device, channel, user type)
- [ ] Time-to-convert distribution analyzed (not just conversion rate)
