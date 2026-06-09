# Privacy Engineering

## Core Principles
1. Data minimization: collect only what is strictly necessary; delete when no longer needed.
2. PII classification: tag every field as PII / sensitive / public in schema definitions.
3. Scrub PII before logging — never log emails, passwords, tokens, or IDs in plain text.
4. Retention periods: every PII dataset must have a documented retention and deletion policy.
5. Right to erasure: deletion must cascade to backups within policy window (typically 30 days).

## Checklist (loop verifier)
- [ ] All PII fields tagged in schema
- [ ] Logging scrubber verified (no PII in log output)
- [ ] Retention period documented
- [ ] Deletion cascade tested
