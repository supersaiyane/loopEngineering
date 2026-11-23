#!/usr/bin/env python3
"""Score supplied discovery answers without inventing missing responses."""
import argparse
import json
from pathlib import Path
import sys

WEIGHTS = {
    'platform': {'cli': 0, 'library': 0, 'web': 1, 'desktop': 1, 'mobile': 2, 'multiple': 3},
    'scale': {'personal': 0, 'small_team': 1, 'public_product': 2, 'saas': 3},
    'complexity': {'simple': 0, 'medium': 1, 'complex': 2, 'enterprise': 3},
    'deployment': {'local': 0, 'single_server': 1, 'cloud': 2, 'app_stores': 2, 'multi_region': 3},
    'revenue': {'none': 0, 'ads': 1, 'one_time': 2, 'subscription': 2, 'enterprise_licensing': 3},
    'design': {'none': 0, 'basic': 1, 'polished': 2, 'branded': 3},
    'security': {'minimal': 0, 'basic': 1, 'privacy': 2, 'regulated': 3},
}


def recommendation(score):
    if score <= 4:
        return 3
    if score <= 9:
        return 5
    if score <= 14:
        return 4
    return 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--mode', type=int, choices=(1, 3, 4, 5), help='Explicit user-selected mode')
    args = parser.parse_args()
    supplied = json.loads(args.input.read_text(encoding='utf-8'))
    if not isinstance(supplied, dict) or set(supplied) - set(WEIGHTS):
        raise ValueError('input must be an object with the seven recognized question names')
    answers, unknown, total = {}, [], 0
    for question, options in WEIGHTS.items():
        value = supplied.get(question)
        if value is None:
            answers[question] = {'answer': None, 'points': None}
            unknown.append(question)
        elif not isinstance(value, str) or value not in options:
            raise ValueError(f'invalid {question} answer; choose from {", ".join(options)}')
        else:
            points = options[value]
            answers[question] = {'answer': value, 'points': points}
            total += points
    maximum = total + 3 * len(unknown)
    print(json.dumps({'answers': answers, 'unknown': unknown,
                      'score': total if not unknown else None, 'minimum': total,
                      'maximum': maximum, 'recommended_mode': recommendation(total) if not unknown else None,
                      'possible_modes': sorted({recommendation(score) for score in range(total, maximum + 1)}),
                      'selected_mode': args.mode,
                      'note': 'Score depends on supplied answers; unknown fields are not assumptions. User-selected mode is independent of the score.'}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, TypeError) as exc:
        print(f'BLOCKED: {exc}', file=sys.stderr)
        sys.exit(1)
