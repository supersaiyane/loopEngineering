---
id: open_source_strategy
version: 1.0.0
owners: [cto]
tags: [open-source, oss, licensing, contribution, inner-source, community, legal]
when_to_use: |
  When deciding whether to open-source internal tools.
  When establishing contribution policies for external open-source dependencies.
  When building an OSS-based developer community strategy.
inputs:
  - tool_type, competitive_sensitivity, community_goal, legal_requirements
outputs:
  - "oss_strategy: open vs closed decision + license choice + contribution policy + community plan"
---

# Open Source Strategy

> Open source is a distribution and community strategy, not just a licensing choice.
> Open source a tool because you want community contributions and ecosystem effects.
> Not because "open source is the right thing to do."

## When to open source

Open source when:
- The tool is not a competitive differentiator (infrastructure, dev tools, frameworks).
- Community contributions would improve it faster than internal resourcing.
- You want to attract engineers who contribute to and use the project.
- You want ecosystem effects (plugins, integrations, case studies).

Keep closed when:
- It encodes proprietary business logic (pricing algorithms, fraud models).
- It requires competitive secrecy to maintain market position.
- You lack resources to maintain a public project (issues, PRs, docs).

## License selection

| License | Copyleft | Commercial use | Best for |
|---|---|---|---|
| MIT | None | Yes | Libraries, tools you want maximum adoption for |
| Apache 2.0 | None | Yes | Same as MIT + explicit patent grant |
| GPL v3 | Strong (derived works must be GPL) | Yes, but derivatives open | When you want contributions back |
| AGPL v3 | Network copyleft (SaaS must open-source) | Yes, forces open competing SaaS | Competing against SaaS wrappers |
| Business Source License (BSL) | Time-delayed | Converts to OSS after N years | Protect commercial advantage short-term |

Default recommendation: **Apache 2.0** for tools and infrastructure.

## Contribution policy

```markdown
## Contributing to [Project]

### What we accept
- Bug fixes (always welcome)
- Documentation improvements (always welcome)
- Performance improvements with benchmarks
- New features that align with the roadmap (open a discussion first)

### What we do not accept
- Features not on the roadmap without prior discussion
- Rewrites of core components without RFC process
- Changes with no tests

### Process
1. Open an issue describing the change
2. Get maintainer sign-off before coding
3. Submit PR with tests and docs
4. Two maintainer reviews required for merge
```

## Inner source (OSS practices internally)

Apply OSS contribution model to internal tools:
- Internal tools in discoverable repositories (service catalog).
- Anyone can submit PRs to any internal tool.
- Owning team reviews and merges.
- Result: silos break down. Good ideas spread across the org.

## Dependency management for OSS

```yaml
# .github/workflows/license-check.yml
# Block unapproved licenses from entering the dependency tree

- name: Check licenses
  run: |
    pip install pip-licenses
    pip-licenses --fail-on "GPL;AGPL;LGPL" --format=json > licenses.json
    # Fails CI if GPL/AGPL code enters the dependency tree
```

## Anti-patterns

- **Open-sourcing without maintenance commitment**: a repo with 200 open issues and no responses is worse than closed source.
- **GPL for a tool you want maximum adoption**: companies with legal teams will reject GPL dependencies.
- **No CLA (Contributor License Agreement)**: you cannot relicense contributions without CLA.
- **Open source as a marketing stunt**: OSS requires ongoing engineering investment. Plan for it.

## Validation

- [ ] Open/closed decision justified against strategic criteria.
- [ ] License choice reviewed by legal.
- [ ] Contribution guidelines published and linked in README.
- [ ] Maintenance commitment defined (response SLA for issues/PRs).
- [ ] License scanning in CI prevents incompatible dependencies.
