#!/usr/bin/env python3
"""Record and check local task dependencies and artifact handoffs.

This is a coordination aid, not proof that an independent agent ran a task.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile


def fail(message):
    raise ValueError(message)


def project_file(root, name):
    if not isinstance(name, str) or not name or Path(name).is_absolute() or '..' in Path(name).parts:
        fail(f'Invalid project path: {name!r}')
    path = (root / name).resolve()
    if not path.is_relative_to(root) or path == root:
        fail(f'Path escapes project: {name}')
    return path


def digest(path):
    if not path.is_file():
        fail(f'Missing output: {path}')
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_plan(root, name):
    plan = json.loads(project_file(root, name).read_text())
    tasks = plan.get('tasks') if isinstance(plan, dict) else None
    if not isinstance(tasks, list) or not tasks:
        fail('Plan must contain a nonempty tasks list')
    by_id = {}
    for task in tasks:
        if not isinstance(task, dict):
            fail('Each task must be an object')
        ident, role = task.get('id'), task.get('role')
        if not all(isinstance(x, str) and re.fullmatch(r'[A-Za-z0-9_-]+', x) for x in (ident, role)) or ident in by_id:
            fail('Task IDs and roles must be valid and task IDs unique')
        deps, outputs = task.get('depends_on'), task.get('outputs')
        if not isinstance(deps, list) or not all(isinstance(d, str) for d in deps) or len(set(deps)) != len(deps):
            fail(f'Invalid dependencies for {ident}')
        if not isinstance(outputs, list) or not outputs or len(set(outputs)) != len(outputs):
            fail(f'Expected unique outputs for {ident}')
        for output in outputs:
            project_file(root, output)
        skills = task.get('required_skills', [])
        if not isinstance(skills, list) or not all(isinstance(s, str) for s in skills) or len(set(skills)) != len(skills):
            fail(f'Invalid required skills for {ident}')
        for skill in skills:
            digest(project_file(root, skill))
        verification = task.get('verification')
        if verification is not None and verification not in outputs:
            fail(f'Verification must be a declared output for {ident}')
        by_id[ident] = {'role': role, 'depends_on': deps, 'declared_outputs': outputs,
                        'verification': verification, 'required_skills': skills,
                        'status': 'pending', 'outputs': {}}
    visiting, visited = set(), set()
    def visit(ident):
        if ident in visiting:
            fail('Dependency cycle detected')
        if ident in visited:
            return
        if ident not in by_id:
            fail(f'Unknown dependency: {ident}')
        visiting.add(ident)
        for dep in by_id[ident]['depends_on']:
            visit(dep)
        visiting.remove(ident)
        visited.add(ident)
    for ident in by_id:
        visit(ident)
    return by_id


@contextmanager
def state_lock(directory):
    directory.mkdir(parents=True, exist_ok=True)
    lock = directory / 'team-flow.lock'
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        fail(f'Team flow is locked; check for another process or stale lock: {lock}')
    try:
        os.close(fd)
        yield
    finally:
        lock.unlink()


def save(path, state):
    fd, temp = tempfile.mkstemp(prefix='.team-flow-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(state, f, indent=2)
            f.write('\n')
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    sub = parser.add_subparsers(dest='action', required=True)
    init = sub.add_parser('init')
    init.add_argument('plan')
    status = sub.add_parser('status')
    status.add_argument('--stale-after-minutes', type=float, default=30)
    for action in ('start', 'complete', 'block', 'retry'):
        p = sub.add_parser(action)
        p.add_argument('task')
        p.add_argument('--role', required=True)
        if action == 'complete':
            p.add_argument('--summary', required=True)
            p.add_argument('--skill', action='append', default=[], help='Claimed project skill path; repeat for each skill')
        if action in ('block', 'retry'):
            p.add_argument('--reason', required=True)
        if action == 'retry':
            p.add_argument('--confirmed-stopped', action='store_true', required=True,
                           help='Claim that the earlier host attempt is no longer running; verify it first')
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    state_path = project_file(root, '.loop/team-flow.json')
    if args.action == 'status':
        if not 0 < args.stale_after_minutes <= 10080:
            fail('Stale threshold must be positive and at most one week')
        state = json.loads(state_path.read_text())
        tasks = {}
        for ident, task in state['tasks'].items():
            elapsed = None
            if task['status'] == 'in_progress':
                starts = [event for event in state['events'] if event.get('task') == ident and event.get('action') == 'start']
                if starts:
                    try:
                        start = datetime.fromisoformat(starts[-1]['timestamp'].replace('Z', '+00:00'))
                        if start.tzinfo is not None:
                            elapsed = (datetime.now(timezone.utc) - start).total_seconds() / 60
                            if elapsed < 0:
                                elapsed = None
                    except (KeyError, TypeError, ValueError):
                        pass
            tasks[ident] = {'role': task['role'], 'status': task['status'],
                            'elapsed_minutes': round(elapsed, 1) if elapsed is not None else None,
                            'stale': elapsed >= args.stale_after_minutes if elapsed is not None else None}
        print(json.dumps({'tasks': tasks, 'note': 'Elapsed time is since the recorded start, not a heartbeat or proof that a host task is stalled.'}, indent=2))
        return
    with state_lock(state_path.parent):
        if args.action == 'init':
            if state_path.exists():
                fail('Team flow already exists; preserve or archive it before starting another')
            state = {'version': 1, 'plan': args.plan, 'tasks': load_plan(root, args.plan), 'events': []}
            details = {'action': 'init', 'plan': args.plan}
        else:
            state = json.loads(state_path.read_text())
            task = state['tasks'].get(args.task)
            if task is None or task['role'] != args.role:
                fail('Unknown task or role does not match the assigned role')
            if args.action == 'start':
                if task['status'] != 'pending':
                    fail('Task is not pending')
                handoff = {}
                for dep in task['depends_on']:
                    upstream = state['tasks'][dep]
                    if upstream['status'] != 'complete':
                        fail(f'Dependency {dep} is not complete')
                    for name, expected in upstream['outputs'].items():
                        if digest(project_file(root, name)) != expected:
                            fail(f'Dependency output changed: {name}')
                        handoff[name] = expected
                task['status'] = 'in_progress'
                details = {'action': 'start', 'task': args.task, 'role': args.role, 'handoff': handoff}
                print(json.dumps({'task': args.task, 'handoff': handoff}))
            elif args.action == 'block':
                if task['status'] != 'in_progress' or not args.reason.strip():
                    fail('Only an in-progress task can be blocked with a reason')
                task['status'] = 'blocked'
                details = {'action': 'block', 'task': args.task, 'role': args.role, 'summary': args.reason}
            elif args.action == 'retry':
                if task['status'] != 'blocked' or not args.reason.strip():
                    fail('Only a blocked task can be retried with a reason')
                task['status'] = 'pending'
                details = {'action': 'retry', 'task': args.task, 'role': args.role, 'summary': args.reason,
                           'earlier_attempt_confirmed_stopped': True}
            else:
                if task['status'] != 'in_progress' or not args.summary.strip():
                    fail('Task must be in progress and have a nonempty summary')
                for dep in task['depends_on']:
                    upstream = state['tasks'][dep]
                    if upstream['status'] != 'complete':
                        fail(f'Dependency {dep} is not complete')
                    for name, expected in upstream['outputs'].items():
                        if digest(project_file(root, name)) != expected:
                            fail(f'Dependency output changed: {name}')
                outputs = {name: digest(project_file(root, name)) for name in task['declared_outputs']}
                claimed_skills = {name: digest(project_file(root, name)) for name in args.skill}
                missing = set(task.get('required_skills', [])) - set(claimed_skills)
                if missing:
                    fail('Required skill claims missing: ' + ', '.join(sorted(missing)))
                if task['verification']:
                    evidence = json.loads(project_file(root, task['verification']).read_text())
                    command = evidence.get('command') if isinstance(evidence, dict) else None
                    if (not isinstance(evidence, dict) or type(evidence.get('exit_code')) is not int or evidence['exit_code'] != 0
                        or not isinstance(command, list) or not command or not all(isinstance(v, str) and v for v in command)
                        or not isinstance(evidence.get('commit'), str) or not evidence['commit']):
                        fail('Verification requires a successful exit code, command, and commit')
                task['outputs'], task['status'] = outputs, 'complete'
                details = {'action': 'complete', 'task': args.task, 'role': args.role, 'summary': args.summary, 'outputs': outputs,
                           'claimed_skills': claimed_skills}
        details['timestamp'] = datetime.now(timezone.utc).isoformat()
        state['events'].append(details)
        save(state_path, state)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f'Team flow blocked: {exc}', file=sys.stderr)
        sys.exit(1)
