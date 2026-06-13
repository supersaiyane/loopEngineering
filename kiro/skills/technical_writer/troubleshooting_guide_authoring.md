---
id: troubleshooting_guide_authoring
version: 1.0.0
owners: [technical_writer]
tags: [troubleshooting, documentation, error-messages, runbook, support, debugging]
when_to_use: |
  When writing troubleshooting guides, error message documentation,
  or FAQ content for users who are stuck.
  Also when converting support ticket patterns into self-service docs.
inputs:
  - common_errors, support_ticket_themes, user_technical_level, product_area
outputs:
  - "troubleshooting_guide: problem-solution format + diagnostic tree + common errors reference"
---

# Troubleshooting Guide Authoring

> Users read troubleshooting guides when they are frustrated.
> Structure for scanning, not reading. Get them to the fix in < 2 minutes.

## Structure: symptom -> diagnosis -> fix

Users search for what they SEE, not what is wrong internally.

```markdown
## "Connection refused" error

**You see this error when:**
Your application returns: `ConnectionRefusedError: [Errno 111] Connection refused`

**Most common causes:**
1. The service is not running (check this first -- it is the cause 80% of the time)
2. Wrong port in configuration
3. Firewall blocking the connection

**Fix -- Step 1: Check if the service is running**
```bash
systemctl status myapp
# OR
ps aux | grep myapp
```
If not running: `systemctl start myapp`

**Fix -- Step 2: Verify port configuration**
Check your config file at `/etc/myapp/config.yml`:
```yaml
server:
  port: 8080   # must match the port your client connects to
```

**Fix -- Step 3: Check firewall**
```bash
ufw status
# If port 8080 is not listed as ALLOW:
ufw allow 8080/tcp
```

**Still stuck?** [Open a support ticket](https://support.example.com) with:
- Output of `systemctl status myapp`
- Your config file (redact passwords)
- Error message and stack trace
```

## Diagnostic tree for complex issues

```markdown
## Authentication Issues

Start here:

Is your API key valid?
-> Run: `curl -H "Authorization: Bearer $API_KEY" https://api.example.com/health`
-> If 401: your key is invalid or expired. [Regenerate it.](#regenerate-key)
-> If 200: key is valid. [Continue to next step.](#check-permissions)

[check-permissions]
Does your key have the required permissions?
-> Dashboard -> API Keys -> View Permissions
-> If missing "orders:read": [Add the permission.](#add-permission)
-> If permissions look correct: [Continue.](#check-ip-allowlist)

[check-ip-allowlist]
Is IP allowlisting enabled on your account?
-> Dashboard -> Security -> IP Allowlist
-> If your IP is not listed: [Add it.](#add-ip)
-> If no allowlist configured: [Contact support.](https://support.example.com)
```

## Mining support tickets for content

```
Process: weekly support ticket review
1. Export last week's tickets
2. Group by error message or symptom
3. Top 3 issues -> add to troubleshooting guide
4. Measure: does the guide deflect future tickets?
```

## Error message documentation

For every user-facing error message, document:

```markdown
## Error: ORDER_MINIMUM_NOT_MET

**Message:** "Order total must be at least $10.00"

**When it appears:** Customer tries to place an order under the minimum threshold.

**Fix:** Add more items to the cart until the total reaches $10.00.

**API response:**
```json
{
  "error": {
    "code": "ORDER_MINIMUM_NOT_MET",
    "message": "Order total must be at least $10.00",
    "minimum_cents": 1000,
    "current_total_cents": 499
  }
}
```

**For developers:** The `minimum_cents` and `current_total_cents` fields tell you
exactly how much more is needed. Display the difference to the user.
```

## Formatting for scannability

- **Bold the key symptom and fix action**: users scan, they do not read.
- **Use numbered steps**: order matters for troubleshooting.
- **Include exact commands**: copy-paste, not paraphrase.
- **Show expected output**: users need to know what success looks like.
- **"If X, go to Y"**: decision trees help users skip irrelevant sections.

## Anti-patterns

- **"Check your configuration"**: which configuration? Which setting? Be specific.
- **Prerequisites buried at the end**: state required permissions/versions upfront.
- **No expected output for commands**: users do not know if it worked.
- **Writing for the intern who knows the system**: write for a frustrated user who does not.

## Validation

- [ ] Every issue starts with the symptom the user sees (not the internal cause).
- [ ] Each fix step includes exact commands with expected output.
- [ ] Tested by someone unfamiliar with the product: did they resolve their issue?
- [ ] "Still stuck?" path leads to support with specific info to include.
- [ ] Guide updated within 1 week when product changes affect the steps.
