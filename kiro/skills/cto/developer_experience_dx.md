---
id: developer_experience_dx
version: 1.0.0
owners: [cto, devops_engineer]
tags: [dx, developer-experience, productivity, onboarding, tooling, golden-path, platform-engineering]
when_to_use: |
  When engineers spend significant time on non-product work:
  slow CI, complex local setup, unclear onboarding, inconsistent tooling.
  DX investment compounds -- every hour saved per engineer per week is 2.5 weeks per year.
inputs:
  - team_size, onboarding_time, ci_build_time, local_setup_complexity
outputs:
  - "dx_roadmap: golden path definition + friction inventory + tooling investments + metrics"
---

# Developer Experience (DX)

> Bad DX is an engineering tax that compounds every day.
> Good DX is a force multiplier that lets engineers focus on product.
> Measure it. Fix the worst friction first.

## DX metrics (measure monthly)

| Metric | Target | How to measure |
|---|---|---|
| Time to first PR (new hire) | < 2 days | Onboarding survey |
| Local setup time | < 30 min | Time first `make dev` to running tests |
| CI build time (PR) | < 10 min | CI pipeline metrics |
| Deployment frequency | > 1/day per team | DORA metrics |
| Change failure rate | < 5% | Rollback rate |
| Developer NPS (DSAT) | > 30 | Quarterly survey |

## The golden path

One opinionated, supported way to start a new service:

```bash
# One command to scaffold a new service
./scripts/new-service.sh my-service

# What it does:
# 1. Creates repo from template (correct structure, dependencies, CI config)
# 2. Sets up local dev environment (Docker Compose, env vars)
# 3. Registers in service catalog
# 4. Creates Slack channel
# 5. Sets up monitoring dashboards
# 6. First deployment to staging

# Result: engineer is deploying code in < 4 hours, not 2 weeks
```

## Local development

```yaml
# docker-compose.yml -- every repo has one
# engineers run: make dev
version: "3.9"
services:
  api:
    build: .
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql://dev:dev@postgres:5432/dev
      - REDIS_URL=redis://redis:6379
    volumes:
      - .:/app              # hot-reload
    depends_on: [postgres, redis]

  postgres:
    image: postgres:16
    environment: { POSTGRES_PASSWORD: dev, POSTGRES_USER: dev }
    ports: ["5432:5432"]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

# Makefile -- standard commands across all repos
dev:     docker-compose up
test:    docker-compose run api pytest
migrate: docker-compose run api alembic upgrade head
lint:    docker-compose run api ruff check .
```

## CI/CD speed investment

```yaml
# CI targets
# PR check: < 10 minutes
# Full test suite: < 20 minutes
# Deploy to production: < 15 minutes

# Speed tactics:
# 1. Cache dependencies (node_modules, pip, cargo)
# 2. Parallelise test suites across runners
# 3. Run only affected tests (Nx affected, pytest-split)
# 4. Docker layer caching

# .github/workflows/ci.yml
jobs:
  test:
    strategy:
      matrix:
        shard: [1, 2, 3, 4]   # 4 parallel shards
    steps:
      - uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ hashFiles('requirements.txt') }}
      - run: pytest --shard-id=${{ matrix.shard }} --num-shards=4
```

## Onboarding checklist automation

```markdown
## Day 1 Checklist (auto-generated from template)

### Access (automated via okta provisioning)
- [ ] GitHub organization member
- [ ] AWS SSO access (read-only)
- [ ] PagerDuty (observer role)
- [ ] Datadog

### Environment setup (script: ./scripts/setup.sh)
- [ ] Homebrew + dependencies installed
- [ ] `make dev` runs successfully
- [ ] First test PR merged

### Codebase orientation (buddy assignment)
- [ ] Service catalog reviewed (which services do we own?)
- [ ] Architecture diagram walkthrough with buddy
- [ ] Shadowed one on-call session
```

## Anti-patterns

- **Every team uses different tooling**: cognitive load spikes when switching contexts.
- **Onboarding documented in a Google Doc updated in 2023**: docs rot. Automate the setup.
- **CI that takes 45 minutes**: engineers wait, context-switch, miss the feedback.
- **Requiring 10 manual steps to start local dev**: `docker-compose up` must be the answer.

## Validation

- [ ] New engineer can run tests locally in < 30 minutes (measured, not assumed).
- [ ] CI PR check completes in < 10 minutes.
- [ ] Golden path service template generates a deployable service in < 4 hours.
- [ ] Developer NPS measured and tracked quarterly.
- [ ] Friction backlog exists and is reviewed in each planning cycle.
