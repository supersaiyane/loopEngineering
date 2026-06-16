---
id: fine_tuning_llms
version: 1.0.0
owners: [ml_engineer]
tags: [fine-tuning, llm, lora, qlora, peft, huggingface, instruction-tuning, sft]
when_to_use: |
  When a base LLM or prompted model does not meet quality requirements for
  a specific task after prompt engineering is exhausted.
  Fine-tuning is expensive - exhaust prompt engineering and RAG first.
inputs:
  - base_model, task_type, training_data_size, gpu_budget, latency_sla
outputs:
  - "fine_tune_plan: method selection + dataset requirements + training config + evaluation plan"
---

# Fine-Tuning LLMs

> Fine-tune as a last resort, not a first step.
> Order: prompt engineering -> few-shot -> RAG -> fine-tuning.
> Fine-tuning is expensive to run, maintain, and re-run when the base model updates.

## When fine-tuning is worth it

Use fine-tuning when:
- Style/format consistency: model must always output a specific JSON schema or tone.
- Domain-specific language: medical, legal, code in a proprietary language.
- Task accuracy > 90% required and prompting tops out at 80%.
- Latency: fine-tuned small model (7B) can be faster + cheaper than GPT-4 with long prompts.

Do not fine-tune when:
- You have fewer than 500 high-quality examples.
- The use case changes frequently (retraining is expensive).
- RAG can provide the knowledge instead.

## Method selection

| Method | VRAM | Quality | Use when |
|---|---|---|---|
| Full fine-tune | 80GB+ | Best | You have A100/H100 fleet |
| LoRA | 16-24GB | Very good | Most production fine-tuning |
| QLoRA (4-bit + LoRA) | 8-12GB | Good | Single GPU / cost-constrained |
| Prefix tuning | 8GB | Moderate | Very limited compute |

LoRA is the standard choice. Trains adapter weights, freezes base. Fast to train, merge for inference.

## QLoRA training setup

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, TaskType
from trl import SFTTrainer
import torch

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
)

model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-v0.1",
    quantization_config=bnb_config,
    device_map="auto",
)

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.1,
    task_type=TaskType.CAUSAL_LM,
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# Trainable: 0.25% of 7B params

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=2048,
    args=TrainingArguments(
        output_dir="./checkpoints",
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        num_train_epochs=3,
        learning_rate=2e-4,
        bf16=True,
        logging_steps=10,
    ),
)
trainer.train()
```

## Dataset format (instruction tuning)

```python
def format_example(instruction: str, output: str) -> str:
    # ChatML format
    lines = [
        "<|im_start|>system",
        "You are a helpful assistant that classifies customer support tickets.<|im_end|>",
        "<|im_start|>user",
        instruction + "<|im_end|>",
        "<|im_start|>assistant",
        output + "<|im_end|>",
    ]
    return "\n".join(lines)

# Quality over quantity: 500 perfect examples > 5000 noisy ones
# Always hold out 10-20% for evaluation
```

## Evaluation

```python
from sklearn.metrics import f1_score, classification_report

def evaluate_model(model, test_examples):
    predictions = [model.predict(ex["instruction"]) for ex in test_examples]
    labels = [ex["label"] for ex in test_examples]
    print(classification_report(labels, predictions))
    print(f"Macro F1: {f1_score(labels, predictions, average='macro'):.3f}")
```

## Anti-patterns

- **Fine-tuning before prompt engineering**: 80% of cases solved by a better prompt.
- **Training on noisy data**: fine-tuning amplifies patterns -- bad data = bad model.
- **Not evaluating on a held-out set**: training loss does not equal task performance.
- **Fine-tuning for knowledge**: model memorizes facts poorly. Use RAG for knowledge instead.

## Validation

- [ ] Prompt engineering baseline established before fine-tuning decision.
- [ ] Dataset quality reviewed: > 95% of examples are accurate.
- [ ] Held-out evaluation set (10-20%) used for metrics.
- [ ] Task metric (F1, BLEU, human eval) defined before training starts.
- [ ] Merge LoRA adapter into base model tested before serving.
