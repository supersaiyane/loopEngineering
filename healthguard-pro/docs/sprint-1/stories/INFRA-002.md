# INFRA-002 — CI/CD Pipeline (GitHub Actions)

**Epic:** HEALTHGUARD-006 — Infrastructure  
**Sprint:** 1  
**Points:** 3 (M)  
**Labels:** `infra/deploy`  
**Primary Agent:** DEVOPS_ENGINEER  
**Status:** ✅ DONE  

---

## User Story

> **As a** developer on the HealthGuard Pro team,  
> **I want to** every PR automatically run tests, security scans, and Terraform validation,  
> **So that** no code merges to main unless all quality and security gates pass.

---

## Acceptance Criteria

- [ ] `auth-service` job: Postgres + Redis services spun up, schema applied, `go test -race`, coverage gate ≥ 70%
- [ ] `patient-data-service` job: conditionally triggered (skip if service doesn't exist yet)
- [ ] `sepsis-scoring-service` job: conditionally triggered (skip if service doesn't exist yet)
- [ ] `terraform-validate` job: `terraform validate` for both us-east-1 and eu-west-1
- [ ] `security-scan` job: gitleaks (secrets), semgrep (`p/golang`, `p/owasp-top-ten`, `p/cwe-top-25`)
- [ ] `all-checks-pass` final gate: blocks merge if ANY required job fails
- [ ] Secrets (`SEMGREP_APP_TOKEN`, AWS credentials) stored in GitHub Actions secrets — never in workflow YAML
- [ ] Workflow triggers: push to `main`, push to `feature/**`, PRs to `main`
- [ ] `-race` flag on all Go tests (data race detection)
- [ ] Coverage report uploaded as artifact for review

---

## Pipeline Architecture

```
Push / PR
    │
    ├── auth-service (parallel)
    │     ├── Postgres + Redis services
    │     ├── Schema applied
    │     ├── go vet
    │     ├── go test -race -coverprofile
    │     └── coverage ≥ 70% gate
    │
    ├── patient-data-service (parallel, conditional)
    │
    ├── sepsis-scoring-service (parallel, conditional, Python)
    │
    ├── terraform-validate (parallel)
    │     ├── us-east-1: init + validate
    │     └── eu-west-1: init + validate
    │
    ├── security-scan (parallel)
    │     ├── gitleaks (secrets)
    │     └── semgrep (SAST)
    │
    └── all-checks-pass ← needs: [auth-service, terraform, security]
              ↑
         BLOCKS MERGE if any fail
```

---

## Technical Notes

**File:** `.github/workflows/ci.yml`  
**Go version:** 1.22 (pinned, not floating `latest`)  
**Terraform version:** 1.8.x (pinned)  
**No GITHUB_ACTIONS_RUNNER_CONTEXT secrets** — sensitive env vars must be in repo/org secrets, not hardcoded.  

Sprint 2 additions (out of scope for this story): k8s manifest linting (`kubeval`), Docker image build + SBOM (`syft`), Trivy container scan.

---

## GATE S2 Checklist

```
✅  No secrets in workflow YAML             — env vars use ${{ secrets.* }} ✅
✅  -race flag on all Go tests              — confirmed in ci.yml ✅
✅  Coverage gate wired                     — fails build if < 70% ✅
✅  Semgrep rulesets reviewed               — p/golang + p/owasp-top-ten + p/cwe-top-25 ✅
✅  Conditional job guards                  — patient-data-service/sepsis skip cleanly ✅
✅  Final gate job present                  — all-checks-pass blocks merge ✅
```

**GATE S2: PASS → INFRA-002 MERGED**

---

## Linked Files

- `.github/workflows/ci.yml`
- `services/auth-service/go.sum` (cache-dependency-path)
- `docs/schema/postgres.sql` (applied in CI)
