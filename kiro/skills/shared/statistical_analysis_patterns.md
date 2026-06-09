---
inclusion: manual
---

# Statistical Analysis Patterns

## Hypothesis testing framework
1. State null hypothesis (H₀) and alternative (H₁) before data collection
2. Choose significance level α (default 0.05; use 0.01 for high-stakes decisions)
3. Calculate required sample size for desired power (1-β ≥ 0.80) before experiment
4. Run test → compute p-value → reject H₀ if p < α
5. Always report effect size (Cohen's d, relative lift %), not just p-value

## A/B test design
- **SUTVA** — stable unit treatment value assumption: users in control ≠ influenced by treatment
- Randomization at user level (not session) for persistent experiences
- Minimum detectable effect (MDE) drives sample size — smaller MDE = longer experiment
- Pre-experiment AA test to validate randomization quality
- Sequential testing or fixed-horizon — never peek and stop early without correction

## Common pitfalls
- **p-hacking** — testing many metrics and reporting only significant ones; pre-register metrics
- **Novelty effect** — early lift may decay; run ≥ 2 weeks minimum, covering full weekly cycle
- **Simpson's paradox** — aggregate result can reverse in subgroups; always segment-check
- **Multiple comparisons** — apply Bonferroni or Benjamini-Hochberg correction when testing N metrics
- **Selection bias** — ensure sample drawn from same population for control and treatment

## Metrics hierarchy
- **Primary metric** — 1 only, statistical test decides go/no-go
- **Secondary metrics** — directional signal, not decision criteria
- **Guardrail metrics** — must not regress (e.g., latency, error rate); experiment auto-stops if breached

## Distributions and tests
- Continuous, normal-ish → t-test (Welch's for unequal variance)
- Skewed / heavy-tailed → Mann-Whitney U or log-transform then t-test
- Proportions (CTR, conversion) → z-test for proportions or chi-squared
- Count data → Poisson or negative binomial regression
- Time-to-event → log-rank test, Cox proportional hazards

## Reporting format
```
Experiment: <name>
Period: <start>–<end> (N days)
Sample: treatment=N₁, control=N₂
Primary metric: <metric name>
  Control: μ=X, σ=Y | Treatment: μ=X', σ=Y'
  Relative lift: +Z% (95% CI: [a%, b%])
  p-value: P | Significant: YES/NO (α=0.05)
Effect size: Cohen's d = D
Decision: SHIP / NO SHIP / EXTEND
```
