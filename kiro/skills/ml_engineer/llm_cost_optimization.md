---
id: llm_cost_optimization
version: 1.0.0
owners: [ml_engineer]
tags: [llm, cost, token-optimization, caching, model-routing, prompt-compression, batching]
when_to_use: |
  When LLM API costs are growing or projected to exceed budget.
  Run this analysis before scaling any LLM-powered feature.
  Also run when optimizing latency -- cost and latency optimizations usually overlap.
inputs:
  - monthly_token_usage, cost_per_feature, latency_sla, quality_requirements
outputs:
  - "cost_reduction_plan: model routing strategy + caching config + prompt optimization + savings estimate"
---

# LLM Cost Optimization

> LLM costs scale linearly with tokens. Every optimization compounds.
> Measure: cost per feature, not total cost.
> Then: model routing -> caching -> prompt compression -> batching.

## Measure first

```python
import tiktoken

def count_tokens(text: str, model: str = "gpt-4o") -> int:
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

def log_request_cost(prompt: str, completion: str, model: str):
    COSTS = {
        "gpt-4o": {"input": 5.00, "output": 15.00},        # per 1M tokens
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "claude-3-5-haiku": {"input": 0.80, "output": 4.00},
    }
    input_tokens = count_tokens(prompt, model)
    output_tokens = count_tokens(completion, model)
    cost = (input_tokens * COSTS[model]["input"] +
            output_tokens * COSTS[model]["output"]) / 1_000_000
    metrics.record("llm.cost", cost, tags={"model": model})
```

## Model routing (biggest lever)

```python
def route_model(task_type: str, context_length: int) -> str:
    # Simple tasks -> cheapest model
    if task_type in ("classification", "extraction", "summarization_short"):
        if context_length < 4000:
            return "gpt-4o-mini"    # 25x cheaper than gpt-4o

    # Complex reasoning -> expensive model
    if task_type in ("code_generation", "complex_reasoning"):
        return "gpt-4o"

    # Long context -> efficient long-context pricing
    if context_length > 50_000:
        return "claude-3-5-haiku"

    return "gpt-4o-mini"   # default to cheapest
```

## Semantic caching

```python
from sentence_transformers import SentenceTransformer
import numpy as np

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

def get_cached_response(prompt: str, cache_store, threshold=0.95):
    embedding = embed_model.encode(prompt)
    for key, data in cache_store.items():
        similarity = np.dot(embedding, data["embedding"])
        if similarity > threshold:
            return data["response"]   # cache hit
    return None   # cache miss

def cache_response(prompt: str, response: str, cache_store):
    cache_store[prompt] = {
        "embedding": embed_model.encode(prompt),
        "response": response,
    }
```

## Prompt compression

```python
# 1. Remove whitespace
prompt = " ".join(prompt.split())

# 2. Use LLMLingua for dynamic compression (keeps semantics)
from llmlingua import PromptCompressor
compressor = PromptCompressor()
compressed = compressor.compress_prompt(long_prompt, ratio=0.5)

# 3. Prompt caching with Anthropic (auto-cached for prompts > 1024 tokens)
messages = [
    {"role": "user", "content": [
        {"type": "text", "text": long_system_context,
         "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": user_question},
    ]}
]
```

## Cost reduction priority

| Technique | Typical Savings | Effort |
|---|---|---|
| Model routing (simple tasks -> mini model) | 70-90% | Low |
| Semantic caching | 30-50% | Medium |
| Prompt caching (long system prompts) | 20-40% | Low |
| Prompt compression | 20-40% | Medium |
| Output length limits | 10-20% | Low |

## Anti-patterns

- **Using GPT-4o for classification**: gpt-4o-mini is 25x cheaper and matches quality on simple tasks.
- **No caching**: repeated similar prompts with no semantic cache wastes money.
- **Unbounded max_tokens**: LLMs will use whatever you give them. Set limits.
- **Not measuring per-feature cost**: you cannot optimize what you cannot attribute.

## Validation

- [ ] Cost tracked per feature (not just total API bill).
- [ ] Model routing implemented (simple tasks on cheapest model).
- [ ] Semantic cache in place with > 30% hit rate target.
- [ ] Output token limits set on all completions.
- [ ] Monthly cost projection reviewed before feature launch.
