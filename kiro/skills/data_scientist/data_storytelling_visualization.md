---
id: data_storytelling_visualization
version: 1.0.0
owners:
  - data_scientist
tags:
  - visualization
  - storytelling
  - matplotlib
  - plotly
  - reporting
when_to_use: "When presenting analysis findings to stakeholders, building data reports, or creating charts that drive business decisions."
inputs:
  - analysis results
  - audience (technical/executive)
  - key message to communicate
outputs:
  - stakeholder-ready charts
  - narrative structure
  - executive summary
---

> "A chart that requires explanation has failed."

## Chart Selection Guide

| Data relationship | Best chart | Avoid |
|------------------|-----------|-------|
| Part-to-whole | Treemap, Waffle | Pie chart (> 4 slices) |
| Trend over time | Line chart | Bar chart for time series |
| Comparison (categories) | Bar chart (horizontal) | 3D bar chart |
| Distribution | Histogram, Box plot | Mean-only bar chart |
| Correlation | Scatter, Heatmap | Line chart |
| Funnel/steps | Waterfall, Funnel | Table |

## Matplotlib — Publication Quality

```python
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# Corporate style defaults
plt.rcParams.update({
    "font.family": "Inter, DejaVu Sans",
    "font.size": 12,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "figure.dpi": 150,
})

def plot_kpi_trend(df, date_col, value_col, title, yformat="{:,.0f}", target=None):
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df[date_col], df[value_col], linewidth=2, color="#2196F3")
    ax.fill_between(df[date_col], df[value_col], alpha=0.1, color="#2196F3")

    if target:
        ax.axhline(target, color="#F44336", linestyle="--", linewidth=1.5, label=f"Target: {target:,}")
        ax.legend()

    # Annotate last value
    last = df.iloc[-1]
    ax.annotate(
        yformat.format(last[value_col]),
        xy=(last[date_col], last[value_col]),
        xytext=(8, 0), textcoords="offset points",
        fontsize=12, fontweight="bold", color="#2196F3",
    )

    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: yformat.format(x)))
    ax.set_title(title)
    ax.set_xlabel("")
    plt.tight_layout()
    return fig
```

## Plotly — Interactive (for dashboards)

```python
import plotly.graph_objects as go
import plotly.express as px

fig = px.line(
    df, x="date", y="revenue", color="region",
    title="Revenue by Region — Last 90 Days",
    labels={"revenue": "Revenue ($)", "date": ""},
    template="plotly_white",
)
fig.update_layout(
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
fig.write_html("revenue_trend.html")
```

## Narrative Structure (Situation → Complication → Resolution)

```
Executive summary format:

HEADLINE: Revenue grew 22% YoY but new user retention dropped to 18% (from 24%)
SITUATION: Q2 acquisition was strong — 40K new users, 15% above target.
COMPLICATION: Day-30 retention for Q2 cohort is 18%, vs 24% for Q1. If this trend holds,
              Q2 users will generate 25% less LTV than Q1 users despite higher acquisition volume.
RESOLUTION: Three hypotheses for root cause + recommended experiment.
```

## Anti-Patterns

- **Title = chart type** ("Bar Chart of Revenue") — title = the insight ("Revenue grew 22% in Q2")
- **Dual y-axis** — almost always misleading; use two separate charts
- **Too many colors** — max 5-6 colors per chart; use gray for non-focus data

## Validation Checklist

- [ ] Chart title states the insight, not the data type
- [ ] Axis labels have units
- [ ] Color used purposefully (not just aesthetically)
- [ ] Executive summary follows SCR structure (Situation, Complication, Resolution)
- [ ] Key number is the largest text element on the page
