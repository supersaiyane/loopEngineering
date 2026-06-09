# Infrastructure as Code

## Core Principles
1. All infrastructure is version-controlled — no manual console changes without a matching IaC commit.
2. Modules are reusable and parameterized — no copy-pasted resource blocks.
3. State is remote and locked (Terraform: S3+DynamoDB or Terraform Cloud).
4. Plan before apply: `terraform plan` output reviewed in PR before `apply`.
5. Secrets never in IaC source — use variable injection or secrets manager references.

## Checklist (loop verifier)
- [ ] No hardcoded secrets in IaC files
- [ ] Remote state configured with locking
- [ ] Plan output reviewed in PR
- [ ] Modules used for repeated patterns
