#!/usr/bin/env python3
"""Create Kiro-native role profiles and skill wrappers without replacing originals."""
import argparse
import json
from pathlib import Path
import re
import sys


def desired_files(root):
    kiro = root / "kiro"
    contract = json.loads((kiro / "framework-contract.json").read_text(encoding="utf-8"))
    required = contract["required_roles"]
    optional = contract.get("optional_roles", [])
    if not isinstance(required, list) or not isinstance(optional, list):
        raise ValueError("required_roles and optional_roles must be lists")
    roles = required + optional
    if len(set(roles)) != len(roles):
        raise ValueError("role names must be unique across the catalog")
    if optional and not (kiro / "steering/optional-specialists.md").is_file():
        raise ValueError("optional roles require the specialist routing catalog")
    result = {}
    for role in roles:
        if not re.fullmatch(r"[a-z][a-z0-9_]*", role):
            raise ValueError(f"invalid role: {role!r}")
        original = kiro / "skills" / role / "SKILL.md"
        content = original.read_text(encoding="utf-8")
        match = re.search(r"^description:\s*(.+)$", content, re.MULTILINE)
        description = match.group(1).strip() if match else "Shared engineering practices for all project roles."
        alias = "loop-" + role.replace("_", "-")
        wrapper = (f"---\nname: {alias}\ndescription: {json.dumps(description)}\n---\n\n"
                   f"# {role.replace('_', ' ').title()}\n\n"
                   f"Read `.kiro/skills/{role}/SKILL.md` and the matching activity in "
                   "`.kiro/steering/skill-selection-matrix.md`. Read the relevant referenced "
                   "skill files before acting. Record the exact skills used, artifacts, "
                   "verification evidence, blockers and handoff. Do not invent test results.\n")
        result[kiro / "skills" / alias / "SKILL.md"] = wrapper
        if role == "shared":
            continue
        agent = {"name": alias, "description": f"Loop Engineering {role.replace('_', ' ')} specialist: {description}",
                 "prompt": f"Act as the {role} specialist for the delegated task. Reading the assigned role skill and choosing relevant activity skills from the matrix is mandatory; do not skip it as optional. "
                           "Read the selected skill files before acting and include exact skill paths and evidence of use in the handoff. "
                           "Use the provided artifacts, verify outcomes with real evidence, and return a concise handoff with "
                           "files, checks, decisions, blockers and next role. Respect parent permissions. Never claim a check ran without evidence.",
                 "tools": ["read", "write", "shell"],
                 "resources": [f"skill://.kiro/skills/{alias}/SKILL.md", f"file://.kiro/skills/{role}/SKILL.md",
                               "skill://.kiro/skills/loop-shared/SKILL.md",
                               "file://.kiro/steering/skill-selection-matrix.md"]}
        if role in optional:
            agent["resources"].append("file://.kiro/steering/optional-specialists.md")
        result[kiro / "agents" / f"{alias}.json"] = json.dumps(agent, indent=2, ensure_ascii=False) + "\n"
    selection = " using the optional specialist catalog when relevant" if optional else ""
    resources = ["file://.kiro/steering/execution-contract.md", "file://.kiro/steering/sprint-tracking-contract.md", "file://.kiro/steering/team-orchestrator-core.md"]
    if optional:
        resources.append("file://.kiro/steering/optional-specialists.md")
    coordinator = {"name": "loop-coordinator", "description": "Coordinate Loop Engineering specialists and verified handoffs.",
                   "prompt": "Run discovery for new builds, select the appropriate specialists" + selection + ", and delegate independent tasks "
                             "as actual subagents where supported. Supply each task's inputs, outputs and checks. "
                             "Use team_flow.py for declared specialist dependencies and handoffs. Require evidence from QA and DevOps, use the sprint and graph gates, and report blockers. "
                             "If native delegation is unavailable, say so; do not claim separate agents ran.",
                   "tools": ["read", "write", "shell", "subagent"],
                   "resources": resources}
    result[kiro / "agents" / "loop-coordinator.json"] = json.dumps(coordinator, indent=2) + "\n"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        files = desired_files(args.root.resolve())
        conflicts = [str(path) for path, content in files.items() if path.exists() and path.read_text(encoding="utf-8") != content]
        if conflicts:
            raise ValueError("existing custom files would be overwritten: " + ", ".join(conflicts))
        for path, content in files.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_text(content, encoding="utf-8")
        print(f"Prepared {len(files)} compatible wrappers and profiles; original skills preserved.")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
