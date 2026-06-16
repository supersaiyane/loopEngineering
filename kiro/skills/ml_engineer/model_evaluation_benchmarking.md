---
id: model_evaluation_benchmarking
version: 1.0.0
owners: [ml_engineer]
tags: [evaluation, benchmarking, evals, llm-eval, ragas, human-eval, regression-testing]
when_to_use: |
  Before deploying any model or prompt change to production.
  When comparing two models or prompt versions.
  When setting quality baselines for a new ML feature.
inputs:
  - task_type, success_criteria, baseline_model, sample_size
outputs:
  - "eval_plan: metric definitions + test set design + baseline results + regression threshold"
---

# Model Evaluation & Benchmarking

> You cannot ship a model without an eval. An eval without ground truth is an opinion.
> Build the eval before the model. Treat it like a test suite.

## Evaluation taxonomy

| Level | What it measures | Example |
|---|---|---|
| Unit eval | Single output correctness | Does the JSON parse? Is the classification correct? |
| Integration eval | End-to-end task quality | Does the RAG pipeline answer correctly? |
| Human eval | Nuanced quality | Is the tone appropriate? Is the response helpful? |
| A/B eval | Relative preference | Which model response is better? |

## Automated evaluation with RAGAS (for RAG)

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from datasets import Dataset

dataset = Dataset.from_list([
    {
        "question": example["question"],
        "answer": model_response,
        "contexts": retrieved_chunks,
        "ground_truth": example["ground_truth"],
    }
    for example, model_response, retrieved_chunks in test_cases
])

results = evaluate(dataset, metrics=[faithfulness, answer_relevancy, context_precision])
print(results)
# faithfulness: 0.87   (answer grounded in context)
# answer_relevancy: 0.92  (answer addresses question)
# context_precision: 0.79  (retrieved chunks are relevant)
```

## LLM-as-judge

```python
import json

def evaluate_response(question: str, response: str, criteria: list) -> dict:
    criteria_str = "\n".join(f"- {c}" for c in criteria)
    judge_prompt = f"""
Evaluate this response on each criterion. Score 1-5. Return JSON.

Question: {question}
Response: {response}

Criteria:
{criteria_str}

Return: {{"scores": {{"criterion_name": score}}, "reasoning": "..."}}
"""
    result = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": judge_prompt}],
        response_format={"type": "json_object"},
    )
    return json.loads(result.choices[0].message.content)

scores = [
    evaluate_response(q, answer, ["accuracy", "completeness", "tone"])
    for q, answer in test_pairs
]
mean_accuracy = sum(s["scores"]["accuracy"] for s in scores) / len(scores)
```

## Regression testing on prompt/model changes

```python
import json

GOLDEN_SET = json.load(open("evals/golden_set.json"))

def regression_test(new_model_fn):
    results = []
    for example in GOLDEN_SET:
        output = new_model_fn(example["input"])
        score = compute_similarity(output, example["expected"])
        results.append({"input": example["input"], "score": score})

    pass_rate = sum(1 for r in results if r["score"] > 0.8) / len(results)

    if pass_rate < 0.90:
        raise Exception(f"Regression: pass rate {pass_rate:.1%} below 90% threshold")

    print(f"Regression test passed: {pass_rate:.1%}")
```

## Statistical significance

```python
from scipy import stats

model_a_scores = [0.87, 0.91, 0.84, ...]
model_b_scores = [0.83, 0.88, 0.79, ...]

t_stat, p_value = stats.ttest_rel(model_a_scores, model_b_scores)
print(f"p-value: {p_value:.4f}")
# p < 0.05 -> statistically significant difference
# p >= 0.05 -> difference could be noise -> need more samples
```

## Anti-patterns

- **Evaluating only on training data**: eval set must be held out and never used for training.
- **No automated eval, only vibes**: "it feels better" is not a shipping criterion.
- **LLM-as-judge without calibration**: judges have biases (length, position). Compare to human labels.
- **Single metric evaluation**: accuracy alone misses tone, safety, hallucination rate.
- **Eval set too small**: fewer than 50 examples means statistical noise dominates.

## Validation

- [ ] Eval set held out (never used in training or prompt tuning).
- [ ] Baseline established before any optimization.
- [ ] Regression test runs in CI on every prompt/model change.
- [ ] At least 100 examples in eval set for statistical validity.
- [ ] Multiple metrics used (not just accuracy or BLEU).
