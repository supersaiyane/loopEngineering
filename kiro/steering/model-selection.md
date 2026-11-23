---
inclusion: manual
---

# Kiro model selection

After discovery and the mode recommendation, explain relevant options and ask
the user to select a model or keep the current one before design begins. Model
availability varies by Kiro surface, version, subscription, geography and
organization policy. Never assert that an option is available without checking.

## Required evidence and fallback

- Before recommending models, explicitly read this file.
- Do not name or recommend unconfirmed models as choices. If the IDE does not
  expose its picker to the assistant, ask the user for the model picker list
  and displayed credit multipliers, or offer to keep the current selection.
  Wait for the list or selection before making a specific comparison.
- Compare only confirmed options. Copy their displayed rates and experimental
  labels exactly; an absent label does not establish a lifecycle status.
  Check numerical cost rankings against the displayed multipliers.
- Do not invent model capabilities, proven reliability, benchmarks, or
  comparative performance. Mark unsupported claims as unknown and describe
  recommendations as tentative. Do not claim a cost is small without the
  user's budget and expected usage.
- A model name and credit multiplier alone are not evidence that it is more
  reliable than another, that it will save debugging time, or that a premium
  is worthwhile. Do not make those claims without a verified source or the
  user's own evaluation. If no such evidence is available, recommend keeping
  the current model as a practical default and explain that fit is unverified.
- Do not claim to see the IDE picker or switch the model unless the host
  exposes that capability. Guide the user through the picker instead.

## Find the user's actual options

1. In an authenticated Kiro CLI, use `kiro-cli chat --list-models --format json`
   if supported. If unavailable, ask the user to open `/model` and share the list.
2. In the IDE, use the model picker or ask the user which options it shows.
   Do not start a login flow automatically. If the list cannot be obtained,
   offer to keep the current model without guessing the available catalog.
3. Present only confirmed available options as selectable. Identify experimental
   and end-of-life choices where the picker or current official documentation
   identifies them. Offer **keep current model** and, if available, **Auto**.
4. Match the recommendations to the discovery answers. Include a short reason,
   trade-off, and verified relative credit multiplier where available. Cost and
   capability comparisons are guidance, not a performance guarantee.
5. Wait for the user. In the IDE the user chooses in the model picker; in the
   CLI use `/model`. Starting a new CLI session can use `kiro-cli chat --model
   <model-id>`. Do not claim a change occurred without confirmation from Kiro.

## Describe confirmed options

Use current, verifiable model documentation or the user's own evaluation to
describe what each confirmed option can do and its fit for the task. If such
evidence is unavailable, say that capabilities and comparative fit are unknown;
do not infer them from the model name, price, or an experimental label. Always
let the user decide based on their quality, latency and credit priorities.

Sources: [Kiro available models](https://kiro.dev/docs/models/available-models/),
[Kiro models overview](https://kiro.dev/docs/models/), and
[CLI session settings](https://kiro.dev/docs/cli/chat/settings/).
