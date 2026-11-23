#!/usr/bin/env python3
"""Create an opt-in project security workflow and Makefile from declared scope."""
import argparse
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys


def safe_file(root, name):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*', name) or '..' in Path(name).parts:
        raise ValueError(f'unsafe project path: {name}')
    path = (root / name).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError(f'project file missing or outside project: {name}')
    return name


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path.cwd())
    p.add_argument('--manifest', action='append', default=[])
    p.add_argument('--compose')
    p.add_argument('--no-images', action='store_true')
    p.add_argument('--sprint', type=int, default=1)
    p.add_argument('--run-security', action='store_true')
    command_names = ('setup', 'lint', 'test', 'db-verify', 'docs-refresh')
    for name in command_names:
        p.add_argument(f'--{name}-command', help=f'Explicit {name} command, parsed as arguments without a shell')
    p.add_argument('--run-command', choices=command_names)
    args = p.parse_args()
    root = args.root.resolve(strict=True)
    config_path = root / '.loop/security-config.json'
    if args.run_command:
        config = json.loads(config_path.read_text(encoding='utf-8'))
        command = config.get('commands', {}).get(args.run_command)
        if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
            raise ValueError(f'{args.run_command} command not configured; edit .loop/security-config.json')
        return subprocess.run(command, cwd=root).returncode
    if args.run_security:
        config = json.loads(config_path.read_text(encoding='utf-8'))
        cmd = [sys.executable, str(root / 'scripts/security_scan.py'), '--root', str(root), '--secrets']
        for manifest in config['manifests']:
            cmd.extend(['--manifest', safe_file(root, manifest)])
        if config.get('compose'):
            cmd.extend(['--compose', safe_file(root, config['compose'])])
        elif config.get('no_images') is True:
            cmd.append('--no-images')
        else:
            raise ValueError('image inventory was not declared')
        cmd.append(str(int(config['sprint'])))
        return subprocess.run(cmd, cwd=root).returncode
    if not args.manifest or bool(args.compose) == args.no_images or args.sprint < 1:
        raise ValueError('declare manifests and either a Compose file or --no-images, and a positive sprint')
    manifests = [safe_file(root, name) for name in args.manifest]
    compose = safe_file(root, args.compose) if args.compose else None
    commands = {}
    for name in command_names:
        supplied = getattr(args, name.replace('-', '_') + '_command')
        if supplied is not None:
            commands[name] = shlex.split(supplied)
            if not commands[name]:
                raise ValueError(f'{name} command cannot be empty')
    makefile = root / 'Makefile'
    workflow = root / '.github/workflows/loop-security.yml'
    for target in (config_path, makefile, workflow):
        if not target.resolve().is_relative_to(root) or target.exists() or target.is_symlink():
            raise ValueError(f'refusing to overwrite or escape project: {target}')
    config_path.parent.mkdir(parents=True, exist_ok=True)
    workflow.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps({'sprint': args.sprint, 'manifests': manifests, 'compose': compose, 'no_images': args.no_images, 'commands': commands}, indent=2) + '\n', encoding='utf-8')
    project_targets = ''.join(f'{name}:\n\tpython3 scripts/delivery_setup.py --run-command {name}\n' for name in command_names)
    image_build = f'docker compose -f {compose} build' if compose else "@printf '%s\\n' 'Image build not applicable: project declared no images'"
    preflight_build = '\t$(MAKE) image-build\n' if compose else ''
    makefile.write_text('''.PHONY: help setup lint test db-verify docs-refresh image-build preflight security-scan db-upgrade db-downgrade
help: ## Show available commands
\t@printf '%s\\n' 'setup / lint / test / db-verify / docs-refresh  Run configured project commands' 'image-build  Build declared Compose images' 'security-scan  Scan declared inventory' 'preflight  Run lint, test, image build when applicable, and security scan' 'db-upgrade / db-downgrade  Run Alembic against LOOP_DATABASE_URL (downgrade is destructive)'
security-scan:
\tpython3 scripts/delivery_setup.py --run-security
image-build:
\t''' + image_build + '''
preflight:
\t$(MAKE) lint
\t$(MAKE) test
''' + preflight_build + '''\t$(MAKE) security-scan
db-upgrade:
\tpython3 -m alembic upgrade head
db-downgrade:
\tpython3 -m alembic downgrade -1
''' + project_targets, encoding='utf-8')
    build = f'      - name: Build declared Compose images\n        run: docker compose -f {compose} build\n' if compose else ''
    workflow.write_text('''name: Loop security
on: [push, pull_request]
permissions:
  contents: read
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Trivy
        uses: aquasecurity/setup-trivy@e07451d2e059ed86c2870430ea286b3a9e0bf241
        with:
          version: v0.74.0
''' + build + f'''      - name: Scan declared inventory
        if: always()
        run: make security-scan
      - name: Retain security report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: loop-security-reports
          path: docs/reports/sprint-*-security.*
          if-no-files-found: warn
''', encoding='utf-8')
    print('Created Makefile, security scope and GitHub workflow. Review inventory and run CI; update the sprint in the security config each sprint.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'BLOCKED: {exc}', file=sys.stderr)
        sys.exit(1)
