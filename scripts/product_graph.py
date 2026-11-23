#!/usr/bin/env python3
"""Merge story graph patches and render a standalone product graph."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


class GraphError(Exception):
    pass


def load(path):
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except ValueError:
        try:
            import yaml
            return yaml.safe_load(text)
        except ImportError:
            raise GraphError(f"{path}: use JSON-formatted YAML or install PyYAML to read YAML")
        except Exception as exc:
            raise GraphError(f"{path}: invalid YAML ({type(exc).__name__})")


def render(graph, provenance):
    data = json.dumps({"nodes": graph["nodes"], "edges": graph["edges"], "provenance": provenance}, ensure_ascii=False).replace("</", "<\\/")
    template = Path(__file__).with_name("product_graph_template.html").read_text(encoding="utf-8")
    return template.replace("__GRAPH_DATA__", data)


def merge(root, sprint, require_complete=False):
    folder = root / "docs" / "graph"
    if not folder.resolve().is_relative_to(root):
        raise GraphError("graph directory escapes the project")
    patches = sorted(folder.glob(f"graph-patch-sprint{sprint}-*.yaml"))
    if not patches:
        raise GraphError("no story graph patches found")
    stories_dir = root / "docs" / f"sprint-{sprint}" / "stories"
    if require_complete:
        if not stories_dir.is_dir():
            raise GraphError("sprint story directory is missing")
        if not stories_dir.resolve().is_relative_to(root):
            raise GraphError("story directory escapes the project")
        cards = sorted(stories_dir.glob("*.md"))
        if not cards:
            raise GraphError("sprint has no story cards")
        missing = [card.stem for card in cards
                   if not (folder / f"graph-patch-sprint{sprint}-{card.stem}.yaml").is_file()]
        if missing:
            raise GraphError("missing story graph patches: " + ", ".join(missing))
    output = folder / "product-graph.yaml"
    html_output = folder / "product-graph.html"
    if any(path.is_symlink() or not path.resolve().is_relative_to(root) for path in (output, html_output)):
        raise GraphError("refusing to overwrite symlinked or out-of-project graph output")
    graph = load(output) if output.exists() else {"nodes": [], "edges": [], "applied_patches": {}}
    if not isinstance(graph, dict) or not isinstance(graph.get("nodes"), list) or not isinstance(graph.get("edges"), list) or not isinstance(graph.get("applied_patches", {}), dict):
        raise GraphError("invalid product graph")
    graph.setdefault("applied_patches", {})
    existing = {node.get("id"): node for node in graph["nodes"] if isinstance(node, dict)}
    if len(existing) != len(graph["nodes"]) or None in existing:
        raise GraphError("invalid or duplicate existing nodes")
    pending = []
    for path in patches:
        if not path.resolve().is_relative_to(root):
            raise GraphError("patch path escapes the project")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        previous = graph["applied_patches"].get(path.name)
        if previous:
            if previous != digest:
                raise GraphError(f"applied patch changed: {path.name}; reconcile before merging")
            continue
        patch = load(path)
        if (not isinstance(patch, dict) or patch.get("sprint") != sprint
                or not isinstance(patch.get("story"), str)
                or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", patch["story"])):
            raise GraphError(f"invalid sprint or story in {path.name}")
        if path.name != f"graph-patch-sprint{sprint}-{patch['story']}.yaml":
            raise GraphError(f"story does not match patch filename: {path.name}")
        if patch.get("decisions"):
            raise GraphError("story patches cannot create decision nodes")
        pending.append((path, digest, patch))
        for node in patch.get("nodes_added", []) + patch.get("api_endpoints_added", []):
            if not isinstance(node, dict) or not all(isinstance(node.get(k), str) and node[k] for k in ("id", "type", "label")):
                raise GraphError(f"invalid node in {path.name}")
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", node["id"]) or node["id"] in existing:
                raise GraphError(f"duplicate or invalid node ID: {node['id']}")
            if node.get("file"):
                source = (root / node["file"]).resolve()
                if not source.is_relative_to(root) or not source.is_file():
                    raise GraphError(f"node source missing or outside project: {node['file']}")
            graph["nodes"].append(node)
            existing[node["id"]] = node
    for path, digest, patch in pending:
        for change in patch.get("nodes_modified", []):
            if not isinstance(change, dict) or change.get("id") not in existing or not isinstance(change.get("changes"), str):
                raise GraphError(f"invalid node modification in {path.name}")
            node = existing[change["id"]]
            node["description"] = (node.get("description", "") + "\n" + change["changes"]).strip()
        for edge in patch.get("edges_added", []):
            if not isinstance(edge, dict) or edge.get("from") not in existing or edge.get("to") not in existing or not edge.get("type"):
                raise GraphError(f"invalid or dangling edge in {path.name}")
            if edge not in graph["edges"]:
                graph["edges"].append(edge)
        graph["applied_patches"][path.name] = digest
    for edge in graph["edges"]:
        if not isinstance(edge, dict) or edge.get("from") not in existing or edge.get("to") not in existing:
            raise GraphError("existing graph has a dangling edge")
    provenance = {}
    for filename, digest in sorted(graph["applied_patches"].items()):
        path = folder / filename
        if not path.is_file() or not path.resolve().is_relative_to(folder.resolve()):
            raise GraphError(f"applied patch missing: {filename}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise GraphError(f"applied patch changed: {filename}; reconcile before merging")
        patch = load(path)
        story = patch.get("story")
        if not isinstance(story, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", story) or story in provenance:
            raise GraphError(f"duplicate or invalid story in {filename}")
        if type(patch.get("sprint")) is not int or filename != f"graph-patch-sprint{patch['sprint']}-{story}.yaml":
            raise GraphError(f"story or sprint does not match patch filename: {filename}")
        ids = {n["id"] for n in patch.get("nodes_added", []) + patch.get("api_endpoints_added", []) + patch.get("nodes_modified", [])}
        for edge in patch.get("edges_added", []):
            ids.update((edge["from"], edge["to"]))
        provenance[story] = {"sprint": patch.get("sprint"), "nodes": sorted(ids), "patch": filename}
    html = render(graph, provenance)
    output.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    html_output.write_text(html, encoding="utf-8")
    print(f"Merged graph: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges; patches preserved")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("command", choices=("merge",))
    parser.add_argument("sprint", type=int)
    parser.add_argument("--require-complete", action="store_true", help="Require a patch for each sprint story card before closure")
    args = parser.parse_args()
    try:
        if args.sprint < 1:
            raise GraphError("sprint must be positive")
        merge(args.root.resolve(), args.sprint, args.require_complete)
        return 0
    except (GraphError, OSError, TypeError, ValueError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
