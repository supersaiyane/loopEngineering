# API Versioning Strategy

## Core Principles
1. Version in URL path (`/v1/`, `/v2/`) for major breaking changes; headers for minor variants.
2. Never remove a version without a deprecation window (minimum 1 sprint / 2 weeks notice).
3. Maintain backward compatibility within a major version — additive changes only.
4. Document the delta between versions in CHANGELOG.md at every release.
5. Use semantic versioning signals: MAJOR=breaking, MINOR=additive, PATCH=fix.

## Checklist (loop verifier)
- [ ] Version prefix present in all new routes
- [ ] Deprecated endpoints return `Deprecation` header with sunset date
- [ ] Both old and new versions tested in integration suite
- [ ] Migration guide written for any breaking change
