#!/usr/bin/env python3
"""Check sprint tracker and Git evidence; a host must actually invoke this gate."""
import argparse
import base64
import csv
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


class Blocked(Exception):
    pass


def stories(root, sprint):
    folder = root / "docs" / f"sprint-{sprint}" / "stories"
    paths = sorted(folder.glob("*.md")) if folder.is_dir() else []
    if not paths:
        raise Blocked(f"no story cards found in {folder}")
    for path in paths:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", path.stem):
            raise Blocked(f"invalid story filename: {path.name}")
    return paths


def local_path(root, sprint, story_id):
    path = root / "docs" / f"sprint-{sprint}" / "jira" / f"{story_id}.txt"
    if not path.resolve().is_relative_to(root):
        raise Blocked("tracker path escapes the project")
    return path


def read_local(root, sprint, story_id):
    record = local_json_path(root, sprint, story_id)
    if record.exists():
        try:
            data = json.loads(record.read_text(encoding="utf-8"))
            if data["story_id"] != story_id or not data["status"] or not isinstance(data["events"], list):
                raise ValueError("invalid record")
            return data["status"]
        except (OSError, ValueError, KeyError, TypeError):
            raise Blocked(f"invalid local tracker record: {record}")
    path = local_path(root, sprint, story_id)
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        raise Blocked(f"missing local tracker record: {path}")
    fields = dict(line.split(":", 1) for line in content.splitlines() if ":" in line)
    if fields.get("STORY_ID", "").strip() != story_id or not fields.get("STATUS", "").strip():
        raise Blocked(f"invalid local tracker record: {path}")
    return fields["STATUS"].strip()


def local_json_path(root, sprint, story_id):
    path = root / "docs" / f"sprint-{sprint}" / "jira" / f"{story_id}.local.json"
    if not path.resolve().is_relative_to(root):
        raise Blocked("tracker path escapes the project")
    return path


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def update_local(root, sprint, story_id, status, note):
    path = local_json_path(root, sprint, story_id)
    lock = path.with_suffix(".lock")
    try:
        fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise Blocked(f"local tracker update already in progress: {story_id}")
    os.close(fd)
    try:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            if record["story_id"] != story_id or not isinstance(record["events"], list):
                raise ValueError("invalid record")
        except (OSError, ValueError, KeyError, TypeError):
            raise Blocked(f"missing or invalid local tracker record: {path}")
        record["status"] = status
        record["events"].append({"timestamp": timestamp(), "status": status, "note": note})
        temporary = path.with_suffix(".json.tmp")
        with temporary.open("x", encoding="utf-8") as out:
            json.dump(record, out, indent=2, ensure_ascii=False)
            out.write("\n")
        os.replace(temporary, path)
        legacy = local_path(root, sprint, story_id)
        if legacy.exists():
            content = legacy.read_text(encoding="utf-8")
            content, count = re.subn(r"^STATUS:.*$", lambda _: f"STATUS: {status}", content, count=1, flags=re.MULTILINE)
            if count:
                legacy.write_text(content, encoding="utf-8")
    finally:
        lock.unlink()
    print(f"Updated local tracker {story_id}: {status} (not synchronized to Jira)")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def jira_connection():
    base, email, token = (os.environ.get(key, "") for key in
                          ("JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN"))
    if not all((base, email, token)):
        raise Blocked("Jira connection unavailable: set JIRA_BASE_URL, JIRA_EMAIL and JIRA_API_TOKEN")
    url = urlsplit(base)
    try:
        port = url.port
    except ValueError:
        raise Blocked("invalid Jira base URL port")
    if (url.scheme != "https" or not url.hostname or not url.hostname.endswith(".atlassian.net")
            or url.username or url.password or url.path not in ("", "/") or url.query or url.fragment
            or port not in (None, 443)):
        raise Blocked("Jira base URL must be an HTTPS Atlassian Cloud site origin")
    credentials = base64.b64encode(f"{email}:{token}".encode()).decode()
    return url.hostname, credentials


def jira_request(host, credentials, path, payload=None):
    headers = {"Authorization": f"Basic {credentials}", "Accept": "application/json"}
    body = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload).encode("utf-8")
    request = Request(f"https://{host}{path}", data=body, headers=headers)
    try:
        with build_opener(NoRedirect).open(request, timeout=15) as response:
            return json.load(response)
    except (HTTPError, URLError, OSError, ValueError) as exc:
        raise Blocked(f"Jira request failed ({type(exc).__name__}); reconcile uncertain writes before retrying")


def read_jira(root, sprint, story_id):
    host, credentials = jira_connection()
    receipt = root / "docs" / f"sprint-{sprint}" / "jira" / f"{story_id}.json"
    if not receipt.resolve().is_relative_to(root):
        raise Blocked("Jira receipt path escapes the project")
    try:
        key = json.loads(receipt.read_text(encoding="utf-8"))["key"]
        if not isinstance(key, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]*-[1-9][0-9]*", key):
            raise ValueError("invalid issue key")
    except (OSError, ValueError, KeyError, TypeError):
        raise Blocked(f"missing or invalid Jira issue receipt: {receipt}")
    try:
        issue = jira_request(host, credentials, f"/rest/api/3/issue/{key}?fields=status,summary")
        if issue.get("key") != key:
            raise Blocked(f"Jira readback did not match {key}")
        summary = issue["fields"]["summary"]
        if not re.search(r"(?<![A-Za-z0-9_-])" + re.escape(story_id) + r"(?![A-Za-z0-9_-])", summary, re.I):
            raise Blocked(f"Jira issue {key} summary does not reference {story_id}")
        return key, issue["fields"]["status"]["statusCategory"]["key"]
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        raise Blocked(f"Jira issue {key} could not be verified ({type(exc).__name__})")


def create_jira(root, sprint, cards, project, issue_type):
    if not re.fullmatch(r"[A-Z][A-Z0-9_]*", project) or not issue_type.strip():
        raise Blocked("invalid Jira project key or issue type")
    host, credentials = jira_connection()
    for card in cards:
        receipt = root / "docs" / f"sprint-{sprint}" / "jira" / f"{card.stem}.json"
        if not receipt.resolve().is_relative_to(root):
            raise Blocked("Jira receipt path escapes the project")
        receipt.parent.mkdir(parents=True, exist_ok=True)
        if receipt.exists():
            key, _ = read_jira(root, sprint, card.stem)
            if not key.startswith(project + "-"):
                raise Blocked(f"existing Jira issue {key} is outside project {project}")
            continue
        content = card.read_text(encoding="utf-8")
        title = next((line.lstrip("# ").strip() for line in content.splitlines() if line.strip()), card.stem)
        summary = f"[{card.stem}] {title}"[:255]
        paragraphs = [{"type": "paragraph", "content": [{"type": "text", "text": line}]}
                      for line in content.splitlines() if line.strip()]
        if not paragraphs:
            raise Blocked(f"story card is empty: {card}")
        payload = {"fields": {"project": {"key": project}, "issuetype": {"name": issue_type},
                   "summary": summary, "description": {"type": "doc", "version": 1,
                   "content": paragraphs}}}
        try:
            with receipt.open("x", encoding="utf-8") as out:
                json.dump({"state": "pending", "story_id": card.stem}, out)
                out.flush()
                os.fsync(out.fileno())
        except FileExistsError:
            raise Blocked(f"concurrent or ambiguous Jira creation for {card.stem}; reconcile before retrying")
        issue = jira_request(host, credentials, "/rest/api/3/issue", payload)
        key = issue.get("key") if isinstance(issue, dict) else None
        if not isinstance(key, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]*-[1-9][0-9]*", key):
            raise Blocked(f"Jira create response missing a valid key for {card.stem}; reconcile before retrying")
        if not key.startswith(project + "-"):
            raise Blocked(f"Jira returned an issue outside project {project}; reconcile before retrying")
        receipt.write_text(json.dumps({"key": key}) + "\n", encoding="utf-8")
        read_jira(root, sprint, card.stem)
        print(f"Created and verified {key} for {card.stem}")


def verify_git(root):
    def git(*args):
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    top = git("rev-parse", "--show-toplevel")
    if top.returncode or Path(top.stdout.strip()).resolve() != root:
        raise Blocked("project must be its own initialized Git repository")
    for variable in ("GIT_AUTHOR_IDENT", "GIT_COMMITTER_IDENT"):
        if git("var", variable).returncode:
            raise Blocked(f"Git identity unavailable: {variable}")
    return git


def verify_commit(root, story_id):
    git = verify_git(root)
    history = git("log", "--format=%H")
    if history.returncode:
        raise Blocked("Git repository has no readable commits")
    pattern = re.compile(r"(?<![A-Za-z0-9_-])" + re.escape(story_id) + r"(?![A-Za-z0-9_-])", re.I)
    for sha in history.stdout.splitlines():
        message = git("show", "-s", "--format=%B", sha)
        files = git("diff-tree", "--root", "--no-commit-id", "--name-only", "-r", sha)
        if message.returncode == files.returncode == 0 and pattern.search(message.stdout) and files.stdout.strip():
            return sha
    raise Blocked(f"no reachable nonempty Git commit references story {story_id}")


def commit_story(root, story_id, message, paths):
    git = verify_git(root)
    pattern = re.compile(r"(?<![A-Za-z0-9_-])" + re.escape(story_id) + r"(?![A-Za-z0-9_-])", re.I)
    if not pattern.search(message) or "\n" in message:
        raise Blocked("commit subject must include the exact story ID and fit on one line")
    if git("diff", "--cached", "--quiet").returncode != 0:
        raise Blocked("existing staged changes require review before committing a story")
    relative = []
    for raw in paths:
        path = (root / raw).resolve()
        if not path.is_relative_to(root) or path == root or not path.is_file():
            raise Blocked(f"story path must be an existing file inside the project: {raw}")
        rel = path.relative_to(root)
        if rel.parts[0] == ".git" or str(rel).startswith(":"):
            raise Blocked("invalid story path")
        relative.append(str(rel))
    staged = git("add", "--", *relative)
    if staged.returncode:
        raise Blocked("Git could not stage story files; inspect the worktree")
    commit = git("commit", "-m", message)
    if commit.returncode:
        raise Blocked("Git commit failed; inspect Git output and staged files before retrying")
    return verify_commit(root, story_id)


def evidence_path(root, sprint, story_id):
    path = root / "docs" / f"sprint-{sprint}" / "evidence" / f"{story_id}.json"
    if not path.resolve().is_relative_to(root):
        raise Blocked("evidence path escapes the project")
    return path


def run_check(root, sprint, story_id, command):
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise Blocked("provide a verification command after --")
    git = verify_git(root)
    sha = verify_commit(root, story_id)
    head = git("rev-parse", "HEAD")
    if head.returncode or head.stdout.strip() != sha:
        raise Blocked("verify this story at its own HEAD commit before moving on")
    if git("diff", "--quiet").returncode or git("diff", "--cached", "--quiet").returncode:
        raise Blocked("commit or remove tracked worktree changes before verification")
    untracked = git("ls-files", "--others", "--exclude-standard")
    if untracked.returncode:
        raise Blocked("could not inspect untracked files before verification")
    allowed = (f"docs/sprint-{sprint}/jira/", f"docs/sprint-{sprint}/evidence/")
    metadata = {'.loop/team-flow.json', '.loop/foundation-sequence.json'}
    if any(not path.startswith(allowed) and path not in metadata for path in untracked.stdout.splitlines()):
        raise Blocked("untracked project files must be reviewed before verification")
    try:
        result = subprocess.run(command, cwd=root, text=True, capture_output=True, timeout=300)
        exit_code, stdout, stderr = result.returncode, result.stdout, result.stderr
    except (OSError, subprocess.TimeoutExpired) as exc:
        exit_code, stdout, stderr = -1, "", type(exc).__name__
    post_head = git("rev-parse", "HEAD")
    post_untracked = git("ls-files", "--others", "--exclude-standard")
    if (post_head.returncode or post_head.stdout.strip() != sha or git("diff", "--quiet").returncode
            or git("diff", "--cached", "--quiet").returncode or post_untracked.returncode
            or any(not path.startswith(allowed) and path not in metadata for path in post_untracked.stdout.splitlines())):
        exit_code = -1
        stderr += "\nVerification changed HEAD or the project worktree; review changes and rerun."
    target = evidence_path(root, sprint, story_id)
    target.parent.mkdir(parents=True, exist_ok=True)
    record = {"story_id": story_id, "commit": sha, "command": command, "timestamp": timestamp(),
              "exit_code": exit_code, "stdout": stdout, "stderr": stderr}
    target.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if exit_code != 0:
        raise Blocked(f"verification command failed (exit {exit_code}); see {target}")
    print(f"Verification passed for {story_id} at {sha}; evidence: {target}")


def verify_evidence(root, sprint, story_id, sha):
    path = evidence_path(root, sprint, story_id)
    try:
        evidence = json.loads(path.read_text(encoding="utf-8"))
        if (evidence["story_id"] != story_id or evidence["commit"] != sha
                or evidence["exit_code"] != 0 or not evidence["command"]):
            raise ValueError("verification evidence does not match")
    except (OSError, ValueError, KeyError, TypeError):
        raise Blocked(f"no passing verification evidence for {story_id} at {sha}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("init-local", "update-local", "export-local", "init-jira", "check-start", "check-story", "check-sprint", "commit-story", "run-check"):
        cmd = sub.add_parser(name)
        cmd.add_argument("sprint", type=int)
        if name in ("check-story", "commit-story", "update-local", "run-check"):
            cmd.add_argument("story")
        if name == "run-check":
            cmd.add_argument("command_args", nargs=argparse.REMAINDER)
        if name == "update-local":
            cmd.add_argument("--status", required=True, choices=("To Do", "In Progress", "Blocked", "Done"))
            cmd.add_argument("--note", default="")
        if name == "export-local":
            cmd.add_argument("--output", required=True)
            cmd.add_argument("--format", choices=("json", "csv", "jira-json"), default="json")
            cmd.add_argument("--project")
        if name == "commit-story":
            cmd.add_argument("--message", required=True)
            cmd.add_argument("paths", nargs="+")
        if name == "init-jira":
            cmd.add_argument("--project", required=True)
            cmd.add_argument("--issue-type", default="Story")
        if name in ("check-start", "check-story", "check-sprint"):
            cmd.add_argument("--mode", choices=("jira", "local"), default="jira")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.sprint < 1:
            raise Blocked("sprint must be a positive number")
        cards = stories(root, args.sprint)
        ids = {p.stem for p in cards}
        if args.command == "init-jira":
            verify_git(root)
            create_jira(root, args.sprint, cards, args.project, args.issue_type)
            return 0
        if args.command == "init-local":
            for card in cards:
                path = local_path(root, args.sprint, card.stem)
                path.parent.mkdir(parents=True, exist_ok=True)
                description = card.read_text(encoding="utf-8")
                title = next((line.lstrip("# ").strip() for line in description.splitlines() if line.strip()), card.stem)
                legacy = path.exists()
                try:
                    with path.open("x", encoding="utf-8") as out:
                        out.write(f"STORY_ID: {card.stem}\nTITLE: {title}\nSTATUS: To Do\nSPRINT: {args.sprint}\n")
                except FileExistsError:
                    pass
                record = local_json_path(root, args.sprint, card.stem)
                if not record.exists():
                    status = read_local(root, args.sprint, card.stem)
                    note = "Imported legacy status; earlier history unknown" if legacy else "Created locally"
                    payload = {"story_id": card.stem, "sprint": args.sprint, "title": title,
                               "description": description, "status": status, "jira_key": None,
                               "sync_state": "pending", "events": [{"timestamp": timestamp(), "status": status, "note": note}]}
                    try:
                        with record.open("x", encoding="utf-8") as out:
                            json.dump(payload, out, indent=2, ensure_ascii=False)
                            out.write("\n")
                    except FileExistsError:
                        pass
            print(f"Created or preserved local tracker records for {len(cards)} stories; these are not Jira issues.")
            return 0
        if args.command == "export-local":
            target = (root / args.output).resolve()
            if not target.is_relative_to(root) or target == root:
                raise Blocked("export path must be inside the project")
            if args.format == "jira-json" and (not args.project or not re.fullmatch(r"[A-Z][A-Z0-9_]*", args.project)):
                raise Blocked("Jira JSON export requires a valid --project key")
            records = []
            for story_id in sorted(ids):
                read_local(root, args.sprint, story_id)
                try:
                    records.append(json.loads(local_json_path(root, args.sprint, story_id).read_text(encoding="utf-8")))
                except (OSError, ValueError):
                    raise Blocked(f"JSON history unavailable for {story_id}; run init-local first")
            with target.open("x", encoding="utf-8", newline="") as out:
                if args.format == "json":
                    json.dump({"format": "loop-engineering-local-issues-v1", "issues": records}, out, indent=2, ensure_ascii=False)
                    out.write("\n")
                elif args.format == "jira-json":
                    issues = []
                    for record in records:
                        history = "\n".join(f"{e['timestamp']} | {e['status']} | {e['note']}" for e in record["events"])
                        issues.append({"externalId": record["story_id"], "issueType": "Story",
                                       "summary": f"[{record['story_id']}] {record['title']}",
                                       "description": f"{record['description']}\n\nLocal history:\n{history}",
                                       "status": record["status"]})
                    json.dump({"projects": [{"key": args.project, "issues": issues}]}, out, indent=2, ensure_ascii=False)
                    out.write("\n")
                else:
                    writer = csv.DictWriter(out, fieldnames=("Summary", "Issue Type", "Description", "Status"))
                    writer.writeheader()
                    for record in records:
                        history = "\n".join(f"{e['timestamp']} | {e['status']} | {e['note']}" for e in record["events"])
                        writer.writerow({"Summary": f"[{record['story_id']}] {record['title']}", "Issue Type": "Story",
                                         "Description": f"{record['description']}\n\nLocal history:\n{history}",
                                         "Status": record["status"]})
            print("Exported local issue history. Jira import formats require field mapping and live validation; ordinary JSON is an internal archive.")
            return 0
        if args.command in ("check-story", "commit-story", "update-local", "run-check") and args.story not in ids:
            raise Blocked(f"story card missing: {args.story}")
        if args.command == "run-check":
            run_check(root, args.sprint, args.story, args.command_args)
            return 0
        if args.command == "update-local":
            update_local(root, args.sprint, args.story, args.status, args.note)
            return 0
        if args.command == "commit-story":
            print(f"Created story commit: {commit_story(root, args.story, args.message, args.paths)}")
            return 0
        git = verify_git(root)
        if args.command in ("check-story", "check-sprint") and (git("diff", "--quiet").returncode or git("diff", "--cached", "--quiet").returncode):
            raise Blocked("tracked worktree changes must be reviewed before completion")
        selected = [args.story] if args.command == "check-story" else sorted(ids)
        seen = set()
        for story_id in selected:
            if args.mode == "jira":
                key, status = read_jira(root, args.sprint, story_id)
                if key in seen:
                    raise Blocked(f"Jira issue {key} is assigned to more than one story")
                seen.add(key)
            else:
                status = read_local(root, args.sprint, story_id)
            if args.command in ("check-story", "check-sprint"):
                if status.lower() != "done":
                    raise Blocked(f"tracker story {story_id} is not Done (status: {status})")
                sha = verify_commit(root, story_id)
                verify_evidence(root, args.sprint, story_id, sha)
                print(f"Verified story commit and command evidence: {sha}")
        print(f"PASS: {args.command} tracker={args.mode}; {len(selected)} story record(s) verified")
        return 0
    except (Blocked, OSError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
