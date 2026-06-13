---
id: sdk_documentation
version: 1.0.0
owners: [technical_writer]
tags: [sdk, documentation, getting-started, code-samples, reference, readme, quickstart]
when_to_use: |
  When writing documentation for an SDK, client library, or developer tool.
  The goal: developer can make a successful API call within 15 minutes of landing
  on the docs, without reading anyone.
inputs:
  - sdk_language, api_surface, target_developer_experience_level, use_cases
outputs:
  - "sdk_docs: quickstart + authentication guide + code reference + error handling guide"
---

# SDK Documentation

> The test of SDK docs: can a developer with no prior knowledge
> make their first successful API call in under 15 minutes?
> If not, the docs failed -- not the developer.

## Structure

```
SDK Documentation
  1. Introduction (what this SDK does, 1 paragraph)
  2. Installation (copy-paste command)
  3. Authentication (get credentials, configure SDK)
  4. Quickstart (one complete working example)
  5. Core concepts (2-3 key concepts with code)
  6. How-to guides (common tasks: "How to handle pagination", etc.)
  7. API Reference (auto-generated from code)
  8. Error handling
  9. Changelog
```

## Quickstart (the most important page)

```markdown
## Quickstart

Install the SDK:
```bash
pip install mycompany-sdk
```

Get your API key from the [dashboard](https://app.example.com/keys).

Make your first request:

```python
from mycompany import Client

client = Client(api_key="your_api_key_here")

# List your first 10 orders
orders = client.orders.list(limit=10)
for order in orders:
    print(f"{order.id}: {order.status}")
```

Expected output:
```
ord_123: completed
ord_124: pending
...
```

[Next: Authentication guide] | [Next: Working with orders]
```

## Authentication guide

```markdown
## Authentication

All API requests require authentication via API key.

### Get your API key
1. Log in to the [dashboard](https://app.example.com)
2. Go to Settings > API Keys
3. Click "Create new key"
4. Copy the key -- it will not be shown again

### Configure the SDK

**Environment variable (recommended):**
```bash
export MYCOMPANY_API_KEY="sk_live_..."
```

```python
# SDK reads from environment automatically
from mycompany import Client
client = Client()  # reads MYCOMPANY_API_KEY
```

**Direct configuration:**
```python
client = Client(api_key="sk_live_...")
```

### Key types
- `sk_live_*`: Production. Real charges.
- `sk_test_*`: Test mode. No real charges.

Always use test keys in development.
```

## Code sample principles

1. **Working, copy-paste examples**: every code sample must run without modification (except credentials).
2. **Minimal examples**: show the task, not error handling that distracts.
3. **Progressive complexity**: quickstart is 5 lines, advanced guide is 50 lines.
4. **Multiple languages**: top 3 languages for your audience.
5. **Show real output**: include the expected output or response.

## Error handling guide

```markdown
## Error Handling

The SDK raises typed exceptions for all error cases.

```python
from mycompany import Client
from mycompany.exceptions import (
    AuthenticationError,
    RateLimitError,
    InvalidRequestError,
    APIError,
)

client = Client(api_key="sk_test_...")

try:
    order = client.orders.retrieve("ord_invalid")
except AuthenticationError:
    print("Invalid API key. Check your credentials.")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds.")
    time.sleep(e.retry_after)
    order = client.orders.retrieve("ord_invalid")
except InvalidRequestError as e:
    print(f"Bad request: {e.message}")
except APIError as e:
    print(f"API error {e.status_code}: {e.message}")
```

### Common errors

| Error | Cause | Fix |
|---|---|---|
| `AuthenticationError` | Invalid or missing API key | Check key in dashboard |
| `RateLimitError` | Too many requests | Implement exponential backoff |
| `InvalidRequestError` | Missing required field | Check the field in the API reference |
| `NotFoundError` | Resource ID does not exist | Verify the ID |
```

## Anti-patterns

- **No working code examples**: "here is a pseudocode example" -- developers copy and it breaks.
- **Examples that require 10 setup steps**: show the minimal working case first.
- **Reference docs only, no guides**: "the `orders.list()` method lists orders" is unhelpful.
- **Stale examples**: code samples that do not match the current SDK version.

## Validation

- [ ] Quickstart tested: new developer can follow it in < 15 min.
- [ ] All code samples tested and produce documented output.
- [ ] Authentication guide covers test vs production keys.
- [ ] Error handling guide covers all exception types.
- [ ] Docs versioned alongside SDK releases.
