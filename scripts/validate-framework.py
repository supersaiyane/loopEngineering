#!/usr/bin/env python3
"""Validate the small, explicit offline framework contract.

This does not prove that host hooks run or that an LLM follows instructions.
Historical references and arbitrary prose links are outside its scope.
"""
import argparse
import json
from pathlib import Path
import re
import sys

EXPECTED_BANDS = [
    {"min": 0, "max": 4, "mode": 3},
    {"min": 5, "max": 9, "mode": 5},
    {"min": 10, "max": 14, "mode": 4},
    {"min": 15, "max": 21, "mode": 1},
]


def read_json(path, errors):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        errors.append(f"invalid JSON or unreadable file {path}: {exc}")
        return None


def validate(root):
    errors = []
    contract = read_json(root / "kiro/framework-contract.json", errors)
    hook = read_json(root / "kiro/hooks/elite-team-orchestrator.json", errors)
    if not isinstance(contract, dict):
        errors.append("contract must be a JSON object")
    else:
        if contract.get("score_bands") != EXPECTED_BANDS:
            errors.append("score bands do not match the canonical mapping")
        all_roles = []
        if not isinstance(contract.get("required_roles"), list) or not contract["required_roles"]:
            errors.append("required_roles must be a nonempty list")
        for group in ("required_roles", "optional_roles"):
            roles = contract.get(group, [])
            if not isinstance(roles, list):
                errors.append(f"{group} must be a list")
                continue
            for role in roles:
                if not isinstance(role, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", role):
                    errors.append(f"invalid role name: {role!r}")
                else:
                    if role in all_roles:
                        errors.append(f"duplicate role: {role}")
                    all_roles.append(role)
                    if not (root / "kiro/skills" / role / "SKILL.md").is_file():
                        errors.append(f"missing role skill: {role}/SKILL.md")
                    if role:
                        alias = "loop-" + role.replace("_", "-")
                        wrapper = root / "kiro/skills" / alias / "SKILL.md"
                        profile = root / "kiro/agents" / f"{alias}.json"
                        if not wrapper.is_file():
                            errors.append(f"missing role wrapper: {alias}/SKILL.md")
                        else:
                            try:
                                content = wrapper.read_text(encoding="utf-8")
                            except (OSError, UnicodeError):
                                content = ""
                            expected_role = f".kiro/skills/{role}/SKILL.md"
                            if (not re.match(r"\A---\s*\n", content)
                                    or not re.search(rf"^name:\s*{re.escape(alias)}\s*$", content, re.MULTILINE)
                                    or expected_role not in content):
                                errors.append(f"invalid role wrapper: {alias}/SKILL.md")
                        if role == "shared":
                            continue
                        if not profile.is_file():
                            label = "optional role" if group == "optional_roles" else "role"
                            errors.append(f"missing {label} profile: {alias}.json")
                        else:
                            agent = read_json(profile, errors)
                            expected = {f"skill://.kiro/skills/{alias}/SKILL.md",
                                        f"file://.kiro/skills/{role}/SKILL.md",
                                        "skill://.kiro/skills/loop-shared/SKILL.md",
                                        "file://.kiro/steering/skill-selection-matrix.md"}
                            resources = agent.get("resources") if isinstance(agent, dict) else None
                            tools = agent.get("tools") if isinstance(agent, dict) else None
                            prompt = agent.get("prompt") if isinstance(agent, dict) else None
                            if (not isinstance(agent, dict) or agent.get("name") != alias
                                    or not isinstance(resources, list) or not all(isinstance(item, str) for item in resources)
                                    or not expected.issubset(resources)
                                    or not isinstance(tools, list) or not all(isinstance(item, str) for item in tools)
                                    or "read" not in tools
                                    or not isinstance(prompt, str) or not prompt.strip()):
                                errors.append(f"invalid role profile resources: {alias}.json")
                            elif group == "optional_roles" and "file://.kiro/steering/optional-specialists.md" not in resources:
                                errors.append(f"optional role profile does not load catalog: {alias}.json")
        if all_roles:
            path = root / "kiro/agents/loop-coordinator.json"
            if not path.is_file():
                errors.append("missing coordinator profile: loop-coordinator.json")
            else:
                coordinator = read_json(path, errors)
                resources = coordinator.get("resources") if isinstance(coordinator, dict) else None
                tools = coordinator.get("tools") if isinstance(coordinator, dict) else None
                prompt = coordinator.get("prompt") if isinstance(coordinator, dict) else None
                expected = {"file://.kiro/steering/execution-contract.md",
                            "file://.kiro/steering/sprint-tracking-contract.md",
                            "file://.kiro/steering/team-orchestrator-core.md"}
                if (not isinstance(coordinator, dict) or coordinator.get("name") != "loop-coordinator"
                        or not isinstance(resources, list) or not all(isinstance(item, str) for item in resources)
                        or not expected.issubset(resources)
                        or not isinstance(tools, list) or not all(isinstance(item, str) for item in tools)
                        or not {"read", "subagent"}.issubset(tools)
                        or not isinstance(prompt, str) or not prompt.strip()):
                    errors.append("invalid coordinator profile: loop-coordinator.json")
                elif contract.get("optional_roles") and "file://.kiro/steering/optional-specialists.md" not in resources:
                    errors.append("coordinator does not load optional-specialists.md")
        files = contract.get("required_files")
        if not isinstance(files, list) or not files:
            errors.append("required_files must be a nonempty list")
        else:
            for item in files:
                if not isinstance(item, str):
                    errors.append("required file path must be a string")
                    continue
                path = (root / item).resolve()
                if not path.is_relative_to(root) or not path.is_file():
                    errors.append(f"missing required file or invalid path: {item}")
    if not isinstance(hook, dict) or not isinstance(hook.get("hooks"), list):
        errors.append("hook must contain a hooks array")
    else:
        routers = [h for h in hook["hooks"] if isinstance(h, dict) and h.get("name") == "Orchestrator Router"]
        if len(routers) != 1:
            errors.append("expected one Orchestrator Router")
        else:
            router = routers[0]
            if router.get("enabled") is not True:
                errors.append("Orchestrator Router must be enabled")
            if router.get("trigger") != "UserPromptSubmit":
                errors.append("Orchestrator Router must trigger on UserPromptSubmit")
            action = router.get("action")
            if not isinstance(action, dict) or action.get("type") != "agent":
                errors.append("Orchestrator Router action must be an agent action")
            else:
                prompt = str(action.get("prompt", ""))
                if "execution-contract.md" not in prompt:
                    errors.append("router does not reference execution-contract.md")
                bands = [(int(lo), int(hi), int(mode)) for lo, hi, mode in
                         re.findall(r"(\d+)–(\d+)\s*→\s*Mode\s+(\d+)", prompt)]
                expected = [(band["min"], band["max"], band["mode"]) for band in EXPECTED_BANDS]
                if bands != expected:
                    errors.append("router score mapping differs from canonical mapping")
        if any(isinstance(h, dict) and h.get("trigger") == "PreToolUse" and h.get("matcher") in ("spec", "user_input") for h in hook["hooks"]):
            errors.append("hook blocks general spec or user input")
    for name in ("chatgpt-system-prompt.md", "claude-system-prompt.md"):
        adapter = root / "kiro/adapters" / name
        if adapter.exists():
            expected = "0–4=Direct(3), 5–9=Lean(5), 10–14=Hybrid(4), 15–21=Full(1)"
            if expected not in adapter.read_text(encoding="utf-8"):
                errors.append(f"adapter mode mapping differs from canonical mapping: {name}")
    skills = root / "kiro/skills"
    steering = root / "kiro/steering"
    if skills.is_dir() and steering.is_dir():
        roles = {p.name for p in skills.iterdir() if p.is_dir()}
        for doc in steering.glob("*.md"):
            for role, filename in set(re.findall(r"(?<![\w])([a-z][a-z0-9_]*)/([a-z][a-z0-9_]*\.md)", doc.read_text(encoding="utf-8"))):
                if role in roles and not (skills / role / filename).is_file():
                    errors.append(f"missing skill reference in {doc.name}: {role}/{filename}")
        catalog = steering / "optional-specialists.md"
        if catalog.is_file():
            for role, filename in set(re.findall(r"`([a-z][a-z0-9_]*)/([a-z][a-z0-9_]*\.md)`", catalog.read_text(encoding="utf-8"))):
                if role not in roles or not (skills / role / filename).is_file():
                    errors.append(f"missing catalog skill reference: {role}/{filename}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Framework contract validation passed (offline checks only).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
