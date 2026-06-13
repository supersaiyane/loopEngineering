---
id: api_platform_strategy
version: 1.0.0
owners: [cto, architect]
tags: [api-platform, developer-experience, api-governance, versioning, sdk, portal]
when_to_use: |
  When your company exposes APIs to external developers or internal teams at scale.
  When API inconsistency is slowing development or causing partner integration failures.
  When planning a platform business model where APIs are a product.
inputs:
  - api_consumer_types, team_count, api_count, governance_maturity
outputs:
  - "platform_strategy: governance model + versioning policy + portal plan + SDK roadmap"
---

# API Platform Strategy

> An API is a product. It has users (developers), it needs documentation,
> versioning, support, and a deprecation policy.
> Without treating it as a product, you accumulate breaking changes and angry partners.

## API-as-product principles

1. **Consistency over local optimization**: one style guide for all APIs. Cognitive load reduction.
2. **Stability contracts**: version promises. Deprecation windows. No surprise breaking changes.
3. **Self-service discoverability**: portal + API reference. No email required to integrate.
4. **Developer experience metrics**: time-to-first-successful-call is your activation metric.

## API governance

```yaml
# API design standards (enforced via Spectral linter in CI)
# .spectral.yml
rules:
  api-version-in-path:
    description: All paths must include API version
    given: "$.paths"
    then:
      function: pattern
      functionOptions:
        match: "^/v[0-9]+"

  resource-names-plural:
    description: Resource names must be plural nouns
    given: "$.paths[*]~"
    then:
      function: pattern
      functionOptions:
        match: "/(users|orders|products|payments)"

  response-has-request-id:
    description: All responses must include X-Request-Id header
    given: "$.paths[*][*].responses[*].headers"
    then:
      field: X-Request-Id
      function: defined
```

## Versioning strategy

```
URL versioning (recommended for external APIs):
  /v1/orders/{id}
  /v2/orders/{id}   <- breaking change gets new version

Header versioning (internal APIs):
  GET /orders/{id}
  API-Version: 2026-01-01   <- Stripe-style date versioning

Semantic versioning (libraries/SDKs):
  v1.2.3 -> patch: bug fixes
  v1.3.0 -> minor: new non-breaking features
  v2.0.0 -> major: breaking changes
```

**Deprecation policy:**
- Announce deprecation 12 months before removal (external APIs).
- Deprecation header in responses: `Deprecation: Sat, 01 Jan 2028 00:00:00 GMT`.
- Monitor usage of deprecated endpoints. Do not remove until traffic drops to zero.

## Developer portal essentials

```markdown
## What every API portal must have

1. Getting Started guide (time-to-hello-world < 15 minutes)
2. Authentication setup (OAuth, API keys -- clear examples)
3. Interactive API reference (Swagger UI / Redoc)
4. Code samples in top 3 languages (Python, JavaScript, Go or Java)
5. SDKs for major languages (generated from OpenAPI spec)
6. Changelog (every API change documented with migration guide)
7. Status page link
8. Support channel (Slack community, Discord, support email)
```

## SDK generation from OpenAPI

```bash
# Auto-generate SDKs from OpenAPI spec
openapi-generator generate   -i openapi.yaml   -g python   -o sdks/python   --additional-properties=packageName=mycompany-sdk,projectName=mycompany-sdk

# Keep SDKs in sync with spec via CI
# On every API spec change: regenerate + publish to package registries
```

## Anti-patterns

- **Different API styles across teams**: `/getUser` vs `/users/{id}` vs `/user/fetch`. Use a style guide.
- **No versioning policy**: any API change is a potential breaking change for partners.
- **API documentation as afterthought**: docs written months after API ships. Partners struggle.
- **No deprecation tracking**: you cannot sunset an API if you do not know who uses it.

## Validation

- [ ] API style guide exists and is enforced in CI (Spectral or equivalent).
- [ ] Versioning policy documented and communicated to all API consumers.
- [ ] Developer portal has getting-started guide with < 15 min time-to-hello-world.
- [ ] Deprecation notices sent 12 months in advance with migration guide.
- [ ] SDK usage analytics tracked (which versions are still in use).
