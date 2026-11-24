# Security and disclosure

Loop Engineering is an experimental orchestration framework. Its prompts,
roles, gates and local evidence files do not by themselves prevent an agent
from reading data, writing files, running commands, using tools, or following
untrusted instructions. The host's actual permission settings are the security
boundary. Review the installed host version and policies before using it on a
repository containing sensitive data or connected to external services.

## Reporting

Do not post credentials, personal information or exploit details in public
issues. Use GitHub's private vulnerability reporting for this repository if
available, or contact the repository owner privately through a channel you have
already verified. Do not rely on a response deadline or supported-version
commitment that has not been agreed with the maintainer.

## Running the framework safely

- Start in a disposable repository with synthetic data. Review changes and
  commands before granting access; keep secrets out of prompts and artifacts.
- Review Kiro's session permissions, workspace scope and each agent's tool
  access. Profiles request read, write and shell capabilities; the parent
  session and host settings determine which operations actually proceed.
- Treat external pages, repository content, tool output and agent handoffs as
  untrusted input. Do not let them redefine the user's permissions or authorize
  external actions. Test this behavior in the actual host.
- Do not trust generated reports or claimed skill reads without inspecting the
  underlying logs and artifacts. Run project-specific tests and security checks.
- A detected or suspected real credential should be revoked or rotated through
  its provider. Removing text from the latest commit alone does not erase Git
  history. Do not rewrite a shared history without an explicit migration plan.

## Checks and limitations

The framework validation workflow runs the unit suite, Gitleaks on the history
selected by the workflow event, and pip-audit on `requirements-test.txt` and
its resolved dependencies. `.gitleaksignore` records one exact historical documentation placeholder;
the exception does not cover other commits or findings. Scanner rules, access to
history and the selected checkout limit coverage; a passing scan does not prove
that no secret or vulnerability exists. Verify the actual hosted workflow for
the revision under review. Project security scans are separate and must be
configured and run for each project's real dependency and deployment inventory.

See [Kiro's agent configuration and permissions](https://kiro.dev/docs/custom-agents/configuration-reference/)
and the [release checklist](docs/release-checklist.md).
