---
id: monorepo_polyrepo_strategy
version: 1.0.0
owners: [architect, cto]
tags: [monorepo, polyrepo, nx, turborepo, repository-strategy, code-sharing, ci]
when_to_use: |
  When deciding repository structure for a new product or restructuring an existing one.
  This decision affects CI speed, code sharing, team autonomy, and deployment independence.
inputs:
  - team_size, service_count, shared_code_volume, deployment_independence_need
outputs:
  - "repo_strategy: monorepo or polyrepo decision + tooling recommendation + migration plan"
---

# Monorepo vs Polyrepo Strategy

> Neither is universally better. The right answer depends on
> how much code you share and how independently teams need to deploy.

## Decision matrix

| Factor | Monorepo | Polyrepo |
|---|---|---|
| Shared code (> 30% shared) | Strong fit | Painful (package versioning hell) |
| Team autonomy needed | Harder | Strong fit |
| Large team (> 50 devs) | Needs tooling (Nx/Turborepo) | Natural isolation |
| Cross-service refactoring | Atomic (one PR) | Requires coordination |
| CI time | Grows without caching | Independent per repo |
| Deployment independence | Harder to enforce | Natural |

## Monorepo tooling

**Turborepo** (JS/TS focused):
```json
// turbo.json
{
  "pipeline": {
    "build": { "dependsOn": ["^build"], "outputs": ["dist/**"] },
    "test": { "dependsOn": ["^build"] },
    "lint": {}
  }
}
```
Remote caching: only rebuild what changed. 10x CI speedup on large repos.

**Nx** (polyglot, more opinionated):
```bash
nx affected:test --base=main   # only test what changed since main
nx affected:build --base=main  # only build affected packages
```

## Monorepo structure

```
monorepo/
  apps/
    api/           ← deployable service
    web/           ← deployable app
    mobile/        ← deployable app
  packages/
    ui/            ← shared React components
    config/        ← shared ESLint, TypeScript config
    types/         ← shared TypeScript types
    utils/         ← shared utility functions
  package.json     ← workspace root
```

## Polyrepo with shared packages

When going polyrepo but needing code sharing:
1. Publish shared code to private npm/PyPI registry.
2. Use Renovate bot to auto-create PRs for dependency updates across repos.
3. Accept: changes to shared code require a release + PR per consumer.

## Migration: polyrepo → monorepo

1. Create monorepo with workspace tooling.
2. Import repos as packages (preserve git history with `git subtree`).
3. Set up CI to only run affected tests/builds.
4. Migrate shared code to `packages/` directory.
5. Keep old repos read-only for 1 sprint, then archive.

## Anti-patterns

- **Monorepo without affected-only CI**: every commit rebuilds everything. CI becomes unusable.
- **Polyrepo with copy-pasted shared code**: drift is guaranteed.
- **Monorepo with no ownership boundaries**: becomes a giant blob where anyone changes anything.
- **Mixing deployment units in one package**: `apps/` = deployable, `packages/` = libraries.

## Validation

- [ ] CI only tests/builds what's affected by the change (not everything).
- [ ] Shared code has clear ownership (CODEOWNERS file).
- [ ] Each deployable app can be deployed independently.
- [ ] Remote caching configured (Turborepo or Nx Cloud).
- [ ] New package creation has a documented template/generator.
