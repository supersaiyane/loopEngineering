#!/usr/bin/env python3
"""Check the structure of a project's system design without asserting accuracy."""
import argparse
from pathlib import Path
import re
import sys

REQUIRED = ('Product and actors', 'Requirements and scope', 'System context',
            'Components and interfaces', 'Architecture and deployment', 'Data model and tenancy',
            'End-to-end flows', 'Security and privacy', 'Reliability and recovery',
            'Observability and operations', 'Scalability and performance',
            'Decisions and trade-offs', 'Traceability and verification')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    db = parser.add_mutually_exclusive_group(required=True)
    db.add_argument('--schema', action='append', help='Project-relative executable schema or migration')
    db.add_argument('--no-database', help='Reason the project has no database')
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    issues = []
    design = root / 'docs/foundation/system_design.md'
    if not design.resolve().is_relative_to(root) or not design.is_file():
        content = ''
        issues.append('Missing system design: docs/foundation/system_design.md')
    else:
        content = design.read_text(encoding='utf-8')
    # Remove fenced blocks while finding headings, so diagram text is not mistaken for a section.
    without_blocks = re.sub(r'^```[^\n]*\n[\s\S]*?^```\s*$', '', content, flags=re.M)
    headings = list(re.finditer(r'^#{2,3}\s+(.+?)\s*$', without_blocks, flags=re.M))
    sections = {}
    for index, match in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(without_blocks)
        sections[match.group(1).strip().casefold()] = without_blocks[match.end():end].strip()
    for name in REQUIRED:
        body = sections.get(name.casefold(), '')
        if len(body) < 30 or re.fullmatch(r'(?is)(?:todo|tbd|unknown|not yet implemented)[.\s]*', body):
            issues.append(f'Missing or incomplete section: {name}')
    blocks = re.findall(r'^```([^\n]*)\n([\s\S]*?)^```\s*$', content, flags=re.M)
    if not any(lang.strip().lower() in ('text', 'ascii', 'plaintext') and re.search(r'(?:->|-->|\+--|\|)', body) for lang, body in blocks):
        issues.append('Missing ASCII architecture diagram in a text fence')
    for token, label in [('mindmap', 'mind map'), ('sequenceDiagram', 'UML sequence diagram')]:
        if not any(lang.strip().lower() == 'mermaid' and re.search(r'^\s*' + token + r'\b', body, flags=re.M | re.I) for lang, body in blocks):
            issues.append(f'Missing {label}')
    if args.schema:
        if not any(lang.strip().lower() == 'mermaid' and re.search(r'^\s*erDiagram\b', body, flags=re.M | re.I) for lang, body in blocks):
            issues.append('Missing database ER diagram')
        for schema in args.schema:
            path = (root / schema).resolve()
            if not path.is_relative_to(root) or not path.is_file() or path.stat().st_size == 0:
                issues.append(f'Missing, empty or unsafe schema/migration: {schema}')
    elif not args.no_database.strip():
        issues.append('An explanation is required when a database is not applicable')
    if issues:
        print('BLOCKED:')
        for issue in issues:
            print(f'- {issue}')
    else:
        print('Required design sections, diagrams and declared schema evidence are present.')
    print('This structural check does not verify completeness, correctness, diagram validity, security or schema execution; specialist review and tests are required.')
    return 1 if issues else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError) as exc:
        print(f'BLOCKED: {exc}', file=sys.stderr)
        sys.exit(1)
