---
inclusion: manual
---

# Kiro model selection

After discovery and the mode recommendation, explain relevant options and ask
the user to select a model or keep the current one before design begins. Model
availability varies by Kiro surface, version, subscription, geography and
organization policy. Never assert that an option is available without checking.

## Find the user's actual options

1. In an authenticated Kiro CLI, use `kiro-cli chat --list-models --format json`
   if supported. If unavailable, ask the user to open `/model` and share the list.
2. In the IDE, use the model picker or ask the user which options it shows.
   Do not start a login flow automatically. If the list cannot be obtained,
   offer the current model and explain that the catalog below is illustrative.
3. Present only confirmed available options as selectable. Identify experimental
   and end-of-life choices where the picker or current official documentation
   identifies them. Offer **keep current model** and, if available, **Auto**.
4. Match the recommendations to the discovery answers. Include a short reason,
   trade-off, and verified relative credit multiplier where available. Cost and
   capability comparisons are guidance, not a performance guarantee.
5. Wait for the user. In the IDE the user chooses in the model picker; in the
   CLI use `/model`. Starting a new CLI session can use `kiro-cli chat --model
   <model-id>`. Do not claim a change occurred without confirmation from Kiro.

## Model family guide

The following are examples from Kiro's published catalog, checked 2026-11-18.
They are not a list of models available to every account. Recheck the source
and current picker before relying on names, availability, or credit rates.

| Option or family | Useful for | Trade-off |
|---|---|---|
| Auto | General work when the user prefers Kiro to route the request. | Less direct control over the underlying model. |
| Claude Opus / Fable | Complex architecture, difficult debugging, security reviews and sustained multi-file work. | Often higher credit use; access varies. |
| Claude Sonnet | Balanced implementation, scoped debugging, review and documentation. | Cost and capability depend on version. |
| Claude Haiku | Quick questions and simple, high-volume tasks. | Complex work may need a stronger model or additional review. |
| GPT Sol | Long-running, difficult coding and terminal tasks. | Often higher credit use than smaller tiers. |
| GPT Terra | Balanced multi-step development. | May be less suitable than a stronger model for the hardest tasks. |
| GPT Luna | Fast, routine and high-volume work. | Lower-cost tier; validate complex output carefully. |
| Kimi / GLM / MiniMax / Qwen | Alternative coding and long-context models where offered. | Availability and lifecycle vary; some models may be experimental. |

Recommend a stronger available model for high-complexity architecture or
security-sensitive work, and consider balanced or faster models for scoped work.
Always let the user decide based on their quality, latency and credit priorities.

Sources: [Kiro available models](https://kiro.dev/docs/models/available-models/),
[Kiro models overview](https://kiro.dev/docs/models/), and
[CLI session settings](https://kiro.dev/docs/cli/chat/settings/).
