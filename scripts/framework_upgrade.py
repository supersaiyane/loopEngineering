#!/usr/bin/env python3
"""Preview or apply a conflict-checked project snapshot upgrade with rollback.

The caller supplies the framework version originally installed as --baseline.
Project memory, documents, reference files and unknown files are never managed.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys
import tempfile

GROUPS = ('agents', 'hooks', 'steering', 'skills', 'adapters')
SCRIPTS = ('bootstrap-project.sh', 'start-kiro-pxpipe.sh', 'validate-framework.py',
           'sprint_gate.py', 'sprint_report.py', 'usage_report.py', 'security_scan.py',
           'delivery_setup.py', 'design_audit.py', 'discovery_score.py', 'migration_setup.py',
           'project_index.py', 'product_graph.py', 'product_graph_template.html',
           'team_flow.py', 'prepare_kiro_agents.py', 'framework_upgrade.py')


def digest(content):
    return hashlib.sha256(content).hexdigest()


def managed(name):
    path = PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or '.' in path.parts:
        return False
    parts = path.parts
    return (len(parts) >= 3 and parts[0] == '.kiro' and parts[1] in GROUPS
            or parts == ('.kiro', 'framework-contract.json')
            or len(parts) == 2 and parts[0] == 'scripts' and parts[1] in SCRIPTS)


def project_path(root, name):
    if not isinstance(name, str) or not managed(name):
        raise ValueError(f'invalid managed path: {name!r}')
    path = root
    parts = PurePosixPath(name).parts
    for index, part in enumerate(parts):
        path = path / part
        if path.is_symlink():
            raise ValueError(f'symlink in managed path: {name}')
        if index < len(parts) - 1 and path.exists() and not path.is_dir():
            raise ValueError(f'not a directory in managed path: {name}')
    return path


def inventory(root):
    result = {}
    for group in GROUPS:
        folder = root / 'kiro' / group
        if not folder.exists():
            continue
        if folder.is_symlink() or not folder.is_dir():
            raise ValueError(f'invalid framework directory: {folder}')
        for directory, children, files in os.walk(folder, followlinks=False):
            for name in children + files:
                path = Path(directory) / name
                if path.is_symlink():
                    raise ValueError(f'symlink in framework source: {path}')
            for name in files:
                path = Path(directory) / name
                relative = '.kiro/' + path.relative_to(root / 'kiro').as_posix()
                content = path.read_bytes()
                if group == 'steering':
                    content = content.replace(b'docs/research/', b'kiro/reference/')
                result[relative] = (content, stat.S_IMODE(path.stat().st_mode))
    for original, destination in [(root / 'kiro/framework-contract.json', '.kiro/framework-contract.json'),
                                  *((root / 'scripts' / name, 'scripts/' + name) for name in SCRIPTS)]:
        if original.is_symlink():
            raise ValueError(f'symlink in framework source: {original}')
        if original.is_file():
            result[destination] = (original.read_bytes(), stat.S_IMODE(original.stat().st_mode))
    return result


def write_atomic(path, content, mode):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='.loop-upgrade-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(content)
        os.chmod(temp, mode)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def upgrade(source, baseline, target, apply, backup):
    if not (target / '.kiro').is_dir() or (target / '.kiro').is_symlink():
        raise ValueError('target must contain a real .kiro directory')
    old, new = inventory(baseline), inventory(source)
    if not old or not new:
        raise ValueError('baseline and source must contain managed framework files')
    plan, conflicts = [], []
    for name, (content, mode) in sorted(new.items()):
        path = project_path(target, name)
        previous = old.get(name)
        # An unchanged upstream file is outside the upgrade, even if a project
        # customized or removed it after bootstrap.
        if previous is not None and previous[0] == content and (previous[1] & 0o111) == (mode & 0o111):
            continue
        if path.exists() and not path.is_file():
            conflicts.append(name)
            continue
        current = path.read_bytes() if path.is_file() else None
        old_mode = stat.S_IMODE(path.stat().st_mode) if current is not None else None
        executable_changed = previous is not None and (previous[1] & 0o111) != (mode & 0o111)
        if current == content and (not executable_changed or (old_mode & 0o111) == (mode & 0o111)):
            continue
        if (previous is None and current is not None or previous is not None and
                (current != previous[0] or executable_changed and (old_mode & 0o111) != (previous[1] & 0o111))):
            conflicts.append(name)
            continue
        # Preserve user read/write permissions. Only propagate upstream executable
        # bits when they changed relative to the exact installed baseline.
        installed_mode = (old_mode & ~0o111 | mode & 0o111) if executable_changed else (old_mode if old_mode is not None else mode)
        plan.append((name, current, content, installed_mode, old_mode))
    if conflicts:
        raise ValueError('conflict: project files differ from the supplied baseline: ' + ', '.join(conflicts))
    retained = sorted(set(old) - set(new))
    for name in retained:
        project_path(target, name)
    print(f'Planned: {len(plan)} additions/updates; {len(retained)} removed-upstream files retained; no project documents or memory modified.')
    if not apply:
        for name, current, _, _, _ in plan:
            print(('ADD ' if current is None else 'UPDATE ') + name)
        return
    if backup is None or backup.exists() or backup.is_symlink():
        raise ValueError('supply a new, nonexistent --backup-dir when using --apply')
    backup = backup.resolve()
    if backup.is_relative_to(target) or target.is_relative_to(backup):
        raise ValueError('backup directory must be outside the project')
    backup.mkdir(parents=True, exist_ok=False)
    records = []
    for name, current, content, mode, old_mode in plan:
        if current is not None:
            stored = backup / 'originals' / name
            stored.parent.mkdir(parents=True, exist_ok=True)
            stored.write_bytes(current)
        records.append({'path': name, 'original': digest(current) if current is not None else None,
                        'installed': digest(content), 'original_mode': old_mode, 'installed_mode': mode})
    (backup / 'manifest.json').write_text(json.dumps({'version': 1, 'target': str(target), 'files': records}, indent=2) + '\n')
    for name, current, content, mode, old_mode in plan:
        path = project_path(target, name)
        observed = path.read_bytes() if path.is_file() else None
        observed_mode = stat.S_IMODE(path.stat().st_mode) if observed is not None else None
        if (observed, observed_mode) != (current, old_mode):
            raise ValueError(f'conflict: {name} changed during upgrade; backup: {backup}')
        write_atomic(path, content, mode)
    print(f'Applied upgrade; retain backup for rollback: {backup}')


def restore(target, backup):
    backup = backup.resolve(strict=True)
    manifest = json.loads((backup / 'manifest.json').read_text())
    if not isinstance(manifest, dict) or manifest.get('version') != 1 or manifest.get('target') != str(target) or not isinstance(manifest.get('files'), list):
        raise ValueError('invalid backup manifest or target mismatch')
    plan, seen = [], set()
    for record in manifest['files']:
        name = record['path']
        if name in seen:
            raise ValueError(f'duplicate backup path: {name}')
        seen.add(name)
        path = project_path(target, name)
        if path.exists() and not path.is_file():
            raise ValueError(f'conflict: {name} is not a file')
        current = digest(path.read_bytes()) if path.is_file() else None
        current_mode = stat.S_IMODE(path.stat().st_mode) if current is not None else None
        original = (record['original'], record.get('original_mode'))
        installed = (record['installed'], record.get('installed_mode'))
        if type(installed[1]) is not int or (current, current_mode) not in (original, installed):
            raise ValueError(f'conflict: {name} changed after upgrade')
        content = None
        if original[0] is not None:
            stored = backup / 'originals' / name
            if stored.is_symlink() or not stored.resolve().is_relative_to(backup) or not stored.is_file():
                raise ValueError(f'invalid backup for {name}')
            content = stored.read_bytes()
            if digest(content) != original[0] or type(original[1]) is not int:
                raise ValueError(f'invalid backup content for {name}')
        plan.append((path, (current, current_mode), installed, content, original[1]))
    for path, current, installed, content, mode in plan:
        observed = digest(path.read_bytes()) if path.is_file() else None
        observed_mode = stat.S_IMODE(path.stat().st_mode) if observed is not None else None
        if (observed, observed_mode) != current:
            raise ValueError(f'conflict: {path} changed during rollback')
        if current != installed:
            continue
        if content is None:
            path.unlink()
        else:
            write_atomic(path, content, mode)
    print('Restored unchanged upgraded files from backup; backup retained.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--baseline', type=Path)
    parser.add_argument('--target', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--backup-dir', type=Path)
    parser.add_argument('--restore', type=Path)
    args = parser.parse_args()
    target = args.target.resolve(strict=True)
    if args.restore:
        if args.apply or args.baseline or args.backup_dir:
            raise ValueError('--restore cannot be combined with upgrade options')
        restore(target, args.restore)
    else:
        if args.baseline is None:
            raise ValueError('supply the exact previously installed framework checkout as --baseline')
        upgrade(args.source.resolve(strict=True), args.baseline.resolve(strict=True), target, args.apply, args.backup_dir)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'BLOCKED: {exc}', file=sys.stderr)
        sys.exit(1)
