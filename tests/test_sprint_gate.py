"""Exercise tracker and Git gates with disposable projects and real Git."""
import json
import csv
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/sprint_gate.py"
spec = importlib.util.spec_from_file_location("sprint_gate", SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class SprintGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        subprocess.run(["git", "-C", str(self.root), "config", "user.name", "Test"], check=True)
        subprocess.run(["git", "-C", str(self.root), "config", "user.email", "test@example.invalid"], check=True)
        stories = self.root / "docs/sprint-1/stories"
        stories.mkdir(parents=True)
        (stories / "S1-01.md").write_text("# S1-01: first story\nAcceptance criteria\n")
        (stories / "S1-02.md").write_text("# S1-02: second story\nAcceptance criteria\n")
        subprocess.run(["git", "-C", str(self.root), "add", "docs"], check=True)
        subprocess.run(["git", "-C", str(self.root), "commit", "-qm", "docs: initial story cards"], check=True)

    def run_gate(self, *args):
        env = os.environ.copy()
        for key in ("JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN"):
            env.pop(key, None)
        return subprocess.run(["python3", str(SCRIPT), "--root", str(self.root), *args],
                              text=True, capture_output=True, env=env)

    def test_real_jira_is_blocked_without_connection(self):
        result = self.run_gate("check-start", "1", "--mode", "jira")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Jira", result.stderr)

    def test_explicit_local_mode_creates_one_tracker_per_story_and_is_idempotent(self):
        self.assertEqual(self.run_gate("init-local", "1").returncode, 0)
        tracker = self.root / "docs/sprint-1/jira/S1-01.txt"
        self.assertIn("STATUS: To Do", tracker.read_text())
        self.assertTrue((tracker.parent / "S1-02.txt").is_file())
        self.assertEqual(self.run_gate("update-local", "1", "S1-01", "--status", "In Progress").returncode, 0)
        self.assertEqual(self.run_gate("init-local", "1").returncode, 0)
        self.assertEqual(json.loads(tracker.with_suffix(".local.json").read_text())["status"], "In Progress")
        self.assertEqual(self.run_gate("check-start", "1", "--mode", "local").returncode, 0)
        (tracker.parent / "S1-02.txt").unlink()
        (tracker.parent / "S1-02.local.json").unlink()
        self.assertNotEqual(self.run_gate("check-start", "1", "--mode", "local").returncode, 0)

    def test_story_completion_requires_reachable_story_commit(self):
        self.run_gate("init-local", "1")
        tracker = self.root / "docs/sprint-1/jira/S1-01.txt"
        self.run_gate("update-local", "1", "S1-01", "--status", "Done")
        self.assertNotEqual(self.run_gate("check-story", "1", "S1-01", "--mode", "local").returncode, 0)
        (self.root / "app.txt").write_text("implemented\n")
        subprocess.run(["git", "-C", str(self.root), "add", "app.txt"], check=True)
        subprocess.run(["git", "-C", str(self.root), "commit", "-qm", "feat: implement S1-01"], check=True)
        self.assertNotEqual(self.run_gate("check-story", "1", "S1-01", "--mode", "local").returncode, 0)
        self.assertEqual(self.run_gate("run-check", "1", "S1-01", "--", "python3", "-c", "print('ok')").returncode, 0)
        self.assertEqual(self.run_gate("check-story", "1", "S1-01", "--mode", "local").returncode, 0)
        self.assertNotEqual(self.run_gate("check-story", "1", "S1-02", "--mode", "local").returncode, 0)
        self.assertNotEqual(self.run_gate("check-sprint", "1", "--mode", "local").returncode, 0)
        other = tracker.parent / "S1-02.txt"
        self.run_gate("update-local", "1", "S1-02", "--status", "Done")
        (self.root / "another.txt").write_text("implemented\n")
        subprocess.run(["git", "-C", str(self.root), "add", "another.txt"], check=True)
        subprocess.run(["git", "-C", str(self.root), "commit", "-qm", "feat: implement S1-02"], check=True)
        self.assertEqual(self.run_gate("run-check", "1", "S1-02", "--", "python3", "-c", "print('ok')").returncode, 0)
        self.assertEqual(self.run_gate("check-sprint", "1", "--mode", "local").returncode, 0)

    def test_failed_verification_does_not_allow_story_completion(self):
        self.run_gate("init-local", "1")
        self.run_gate("update-local", "1", "S1-01", "--status", "Done")
        (self.root / "app.txt").write_text("work\n")
        subprocess.run(["git", "-C", str(self.root), "add", "app.txt"], check=True)
        subprocess.run(["git", "-C", str(self.root), "commit", "-qm", "feat: implement S1-01"], check=True)
        self.assertNotEqual(self.run_gate("run-check", "1", "S1-01", "--", "python3", "-c", "raise SystemExit(3)").returncode, 0)
        self.assertNotEqual(self.run_gate("check-story", "1", "S1-01", "--mode", "local").returncode, 0)

    def test_handoff_ledger_is_allowed_but_changed_code_blocks_completion(self):
        self.run_gate("init-local", "1")
        self.run_gate("update-local", "1", "S1-01", "--status", "Done")
        (self.root / "app.txt").write_text("work\n")
        subprocess.run(["git", "-C", str(self.root), "add", "app.txt"], check=True)
        subprocess.run(["git", "-C", str(self.root), "commit", "-qm", "feat: implement S1-01"], check=True)
        (self.root / ".loop").mkdir()
        (self.root / ".loop/team-flow.json").write_text('{}')
        (self.root / ".loop/foundation-sequence.json").write_text('{}')
        self.assertEqual(self.run_gate("run-check", "1", "S1-01", "--", "python3", "-c", "print('ok')").returncode, 0)
        (self.root / "app.txt").write_text("changed since verification\n")
        self.assertNotEqual(self.run_gate("check-story", "1", "S1-01", "--mode", "local").returncode, 0)

    def test_local_team_workflow_links_handoff_check_and_graph(self):
        self.assertEqual(self.run_gate("init-local", "1").returncode, 0)
        plan = {"tasks": [
            {"id": "design", "role": "architect", "depends_on": [], "outputs": ["design.md"]},
            {"id": "qa", "role": "qa_engineer", "depends_on": ["design"],
             "outputs": ["docs/sprint-1/evidence/S1-01.json"], "verification": "docs/sprint-1/evidence/S1-01.json"}]}
        (self.root / "team-plan.json").write_text(json.dumps(plan))
        (self.root / "design.md").write_text("API contract")
        graph = self.root / "docs/graph"
        graph.mkdir()
        (graph / "graph-patch-sprint1-S1-01.yaml").write_text(json.dumps({"sprint": 1, "story": "S1-01", "nodes_added": [{"id": "api", "type": "service", "label": "API", "file": "design.md"}]}))
        subprocess.run(["git", "-C", str(self.root), "add", "team-plan.json", "design.md", "docs/graph"], check=True)
        subprocess.run(["git", "-C", str(self.root), "commit", "-qm", "feat: implement S1-01"], check=True)
        def flow(*args):
            return subprocess.run(["python3", str(SCRIPT.parent / "team_flow.py"), "--root", str(self.root), *args], text=True, capture_output=True)
        for args in [("init", "team-plan.json"), ("start", "design", "--role", "architect"),
                     ("complete", "design", "--role", "architect", "--summary", "ready"),
                     ("start", "qa", "--role", "qa_engineer")]:
            result = flow(*args)
            self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_gate("run-check", "1", "S1-01", "--", "python3", "-c", "assert 2 + 2 == 4")
        self.assertEqual(result.returncode, 0, result.stderr)
        result = flow("complete", "qa", "--role", "qa_engineer", "--summary", "check passed")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.run_gate("update-local", "1", "S1-01", "--status", "Done").returncode, 0)
        self.assertEqual(self.run_gate("check-story", "1", "S1-01", "--mode", "local").returncode, 0)
        result = subprocess.run(["python3", str(SCRIPT.parent / "product_graph.py"), "--root", str(self.root), "merge", "1"], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((graph / "product-graph.html").is_file())

    def test_verification_does_not_pass_when_command_changes_committed_code(self):
        self.run_gate("init-local", "1")
        self.run_gate("update-local", "1", "S1-01", "--status", "Done")
        (self.root / "app.txt").write_text("work\n")
        subprocess.run(["git", "-C", str(self.root), "add", "app.txt"], check=True)
        subprocess.run(["git", "-C", str(self.root), "commit", "-qm", "feat: implement S1-01"], check=True)
        result = self.run_gate("run-check", "1", "S1-01", "--", "python3", "-c", "open('app.txt','w').write('changed')")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotEqual(self.run_gate("check-story", "1", "S1-01", "--mode", "local").returncode, 0)

    def test_jira_creation_requires_verified_readback_and_reuses_receipts(self):
        cards = [self.root / "docs/sprint-1/stories/S1-01.md"]
        calls = []
        def jira(host, credentials, path, payload=None):
            calls.append((path, payload))
            if payload is not None:
                self.assertEqual(payload["fields"]["project"]["key"], "PROJ")
                return {"key": "PROJ-1"}
            return {"key": "PROJ-1", "fields": {"summary": "[S1-01] first story",
                    "status": {"statusCategory": {"key": "new"}}}}
        env = {"JIRA_BASE_URL": "https://example.atlassian.net", "JIRA_EMAIL": "a@example.invalid", "JIRA_API_TOKEN": "test"}
        with mock.patch.dict(os.environ, env), mock.patch.object(gate, "jira_request", side_effect=jira):
            gate.create_jira(self.root, 1, cards, "PROJ", "Story")
            gate.create_jira(self.root, 1, cards, "PROJ", "Story")
        self.assertEqual(sum(payload is not None for _, payload in calls), 1)
        receipt = self.root / "docs/sprint-1/jira/S1-01.json"
        self.assertEqual(json.loads(receipt.read_text()), {"key": "PROJ-1"})

    def test_ambiguous_jira_creation_is_not_retried(self):
        cards = [self.root / "docs/sprint-1/stories/S1-01.md"]
        env = {"JIRA_BASE_URL": "https://example.atlassian.net", "JIRA_EMAIL": "a@example.invalid", "JIRA_API_TOKEN": "test"}
        with mock.patch.dict(os.environ, env), mock.patch.object(gate, "jira_request", side_effect=gate.Blocked("timeout")) as request:
            with self.assertRaises(gate.Blocked):
                gate.create_jira(self.root, 1, cards, "PROJ", "Story")
            with self.assertRaises(gate.Blocked):
                gate.create_jira(self.root, 1, cards, "PROJ", "Story")
            self.assertEqual(request.call_count, 1)

    def test_commit_story_only_commits_requested_files(self):
        (self.root / "story.txt").write_text("story work\n")
        (self.root / "unrelated.txt").write_text("do not commit\n")
        result = self.run_gate("commit-story", "1", "S1-01", "--message", "feat: implement S1-01", "story.txt")
        self.assertEqual(result.returncode, 0, result.stderr)
        committed = subprocess.run(["git", "-C", str(self.root), "show", "--format=", "--name-only", "HEAD"],
                                   text=True, capture_output=True, check=True).stdout.splitlines()
        self.assertEqual(committed, ["story.txt"])
        self.assertTrue((self.root / "unrelated.txt").exists())

    def test_commit_story_refuses_existing_staged_changes(self):
        (self.root / "other.txt").write_text("unrelated\n")
        (self.root / "story.txt").write_text("story\n")
        subprocess.run(["git", "-C", str(self.root), "add", "other.txt"], check=True)
        result = self.run_gate("commit-story", "1", "S1-01", "--message", "feat: implement S1-01", "story.txt")
        self.assertNotEqual(result.returncode, 0)
        staged = subprocess.run(["git", "-C", str(self.root), "diff", "--cached", "--name-only"],
                                text=True, capture_output=True, check=True).stdout.splitlines()
        self.assertEqual(staged, ["other.txt"])

    def test_offline_tracker_preserves_history_and_exports_without_overwriting(self):
        self.assertEqual(self.run_gate("init-local", "1").returncode, 0)
        result = self.run_gate("update-local", "1", "S1-01", "--status", "In Progress", "--note", "Started implementation")
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_gate("update-local", "1", "S1-01", "--status", "Blocked", "--note", "Awaiting database")
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads((self.root / "docs/sprint-1/jira/S1-01.local.json").read_text())
        self.assertIn("STATUS: Blocked", (self.root / "docs/sprint-1/jira/S1-01.txt").read_text())
        self.assertIn("Acceptance criteria", record["description"])
        self.assertEqual(record["status"], "Blocked")
        self.assertEqual([e["status"] for e in record["events"]], ["To Do", "In Progress", "Blocked"])
        self.assertEqual(self.run_gate("export-local", "1", "--output", "docs/export.json").returncode, 0)
        exported = json.loads((self.root / "docs/export.json").read_text())
        self.assertEqual(len(exported["issues"]), 2)
        self.assertEqual(exported["issues"][0]["events"][-1]["note"], "Awaiting database")
        self.assertNotEqual(self.run_gate("export-local", "1", "--output", "docs/export.json").returncode, 0)
        self.assertEqual(self.run_gate("export-local", "1", "--format", "csv", "--output", "docs/jira.csv").returncode, 0)
        with (self.root / "docs/jira.csv").open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 2)
        self.assertIn("S1-01", rows[0]["Summary"])
        self.assertIn("Awaiting database", rows[0]["Description"])
        self.assertEqual(self.run_gate("export-local", "1", "--format", "jira-json", "--project", "TEST", "--output", "docs/jira-import.json").returncode, 0)
        jira_export = json.loads((self.root / "docs/jira-import.json").read_text())
        self.assertEqual(jira_export["projects"][0]["key"], "TEST")
        issue = jira_export["projects"][0]["issues"][0]
        self.assertEqual(issue["externalId"], "S1-01")
        self.assertIn("Awaiting database", issue["description"])

    def test_offline_tracker_rejects_invalid_status_and_external_output_path(self):
        self.run_gate("init-local", "1")
        self.assertNotEqual(self.run_gate("update-local", "1", "S1-01", "--status", "invented").returncode, 0)
        self.assertNotEqual(self.run_gate("export-local", "1", "--output", "../escape.json").returncode, 0)


if __name__ == "__main__":
    unittest.main()
