---
id: ab_test_statistical_analysis
version: 1.0.0
owners:
  - data_scientist
tags:
  - ab-testing
  - statistics
  - hypothesis-testing
  - experimentation
when_to_use: "When analyzing A/B test results, calculating statistical significance, or determining whether a product change had a measurable effect."
inputs:
  - control/treatment assignment
  - metric values
  - experiment duration
  - business success metric
outputs:
  - statistical significance result
  - effect size
  - confidence interval
  - recommendation
---

> "Statistical significance is not business significance. Report both."

## Pre-Experiment: Sample Size Calculation

```python
from scipy import stats
import numpy as np

def required_sample_size(
    baseline_rate: float,     # current conversion rate, e.g. 0.10
    minimum_detectable_effect: float,  # e.g. 0.02 (want to detect 2pp lift)
    alpha: float = 0.05,      # false positive rate
    power: float = 0.80,      # 1 - false negative rate
) -> int:
    effect = minimum_detectable_effect / baseline_rate  # relative effect
    treatment_rate = baseline_rate * (1 + effect)
    pooled_p = (baseline_rate + treatment_rate) / 2
    z_alpha = stats.norm.ppf(1 - alpha / 2)   # two-tailed
    z_beta = stats.norm.ppf(power)
    n = (2 * pooled_p * (1 - pooled_p) * (z_alpha + z_beta) ** 2) / (baseline_rate - treatment_rate) ** 2
    return int(np.ceil(n))

# Example: detect 10% relative lift on 10% baseline at 80% power
n = required_sample_size(baseline_rate=0.10, minimum_detectable_effect=0.01)
print(f"Need {n:,} users per variant")
```

## Post-Experiment Analysis

```python
import pandas as pd
from scipy.stats import chi2_contingency, ttest_ind

def analyze_conversion_test(control: pd.Series, treatment: pd.Series, alpha: float = 0.05) -> dict:
    """Binary metric (conversion, click) analysis."""
    ctrl_n, trt_n = len(control), len(treatment)
    ctrl_conv, trt_conv = control.sum(), treatment.sum()
    ctrl_rate = ctrl_conv / ctrl_n
    trt_rate = trt_conv / trt_n

    # Chi-squared test
    contingency = [[ctrl_conv, ctrl_n - ctrl_conv],
                   [trt_conv, trt_n - trt_conv]]
    chi2, p_value, _, _ = chi2_contingency(contingency)

    # Effect size (relative lift)
    relative_lift = (trt_rate - ctrl_rate) / ctrl_rate

    # 95% confidence interval on absolute difference
    se = np.sqrt(ctrl_rate * (1 - ctrl_rate) / ctrl_n + trt_rate * (1 - trt_rate) / trt_n)
    ci_lower = (trt_rate - ctrl_rate) - 1.96 * se
    ci_upper = (trt_rate - ctrl_rate) + 1.96 * se

    return {
        "control_rate": round(ctrl_rate, 4),
        "treatment_rate": round(trt_rate, 4),
        "absolute_lift": round(trt_rate - ctrl_rate, 4),
        "relative_lift_pct": round(relative_lift * 100, 2),
        "p_value": round(p_value, 4),
        "significant": p_value < alpha,
        "ci_95": (round(ci_lower, 4), round(ci_upper, 4)),
        "recommendation": "Ship" if p_value < alpha and relative_lift > 0 else "Do not ship",
    }

def analyze_continuous_test(control: pd.Series, treatment: pd.Series, alpha: float = 0.05) -> dict:
    """Continuous metric (revenue, time-on-page) analysis."""
    t_stat, p_value = ttest_ind(control.dropna(), treatment.dropna())
    effect_size = (treatment.mean() - control.mean()) / control.std()  # Cohen's d
    return {
        "control_mean": round(control.mean(), 4),
        "treatment_mean": round(treatment.mean(), 4),
        "t_statistic": round(t_stat, 4),
        "p_value": round(p_value, 4),
        "cohens_d": round(effect_size, 4),
        "significant": p_value < alpha,
    }
```

## Anti-Patterns

- **Peeking** — checking significance daily and stopping early inflates false positives by 2-3x
- **Multiple metrics without correction** — apply Bonferroni: `alpha_corrected = alpha / n_metrics`
- **Ignoring novelty effect** — run experiment ≥ 2 full business cycles before concluding
- **p < 0.05 = ship** — also verify practical significance: is the effect size worth the engineering cost?

## Validation Checklist

- [ ] Sample size calculated before experiment started
- [ ] Assignment is random and mutually exclusive
- [ ] SRM (Sample Ratio Mismatch) check: expected vs actual split ratio
- [ ] Primary metric pre-registered before analysis
- [ ] Experiment ran for full pre-determined duration
