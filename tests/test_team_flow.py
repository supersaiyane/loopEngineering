import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/team_flow.py"


class TeamFlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        plan = {"tasks": [
            {"id": "design", "role": "architect", "depends_on": [], "outputs": ["design.md"]},
            {"id": "qa", "role": "qa_engineer", "depends_on": ["design"], "outputs": ["qa.json"], "verification": "qa.json"},
        ]}
        (self.root / "team-plan.json").write_text(json.dumps(plan))

    def flow(self, *args):
        return subprocess.run(["python3", str(SCRIPT), "--root", str(self.root), *args], text=True, capture_output=True)

    def test_dependencies_outputs_and_verification_are_required(self):
        self.assertEqual(self.flow("init", "team-plan.json").returncode, 0)
        self.assertNotEqual(self.flow("start", "qa", "--role", "qa_engineer").returncode, 0)
        self.assertNotEqual(self.flow("start", "design", "--role", "devops_engineer").returncode, 0)
        self.assertEqual(self.flow("start", "design", "--role", "architect").returncode, 0)
        self.assertNotEqual(self.flow("complete", "design", "--role", "architect", "--summary", "done").returncode, 0)
        (self.root / "design.md").write_text("API contract\n")
        self.assertEqual(self.flow("complete", "design", "--role", "architect", "--summary", "contract ready").returncode, 0)
        started = self.flow("start", "qa", "--role", "qa_engineer")
        self.assertEqual(started.returncode, 0, started.stderr)
        self.assertIn("design.md", started.stdout)
        (self.root / "qa.json").write_text('{"exit_code": 1}')
        self.assertNotEqual(self.flow("complete", "qa", "--role", "qa_engineer", "--summary", "tests").returncode, 0)
        (self.root / "qa.json").write_text('{"exit_code": 0, "command": ["pytest"], "commit": "abc"}')
        self.assertEqual(self.flow("complete", "qa", "--role", "qa_engineer", "--summary", "passed").returncode, 0)
        state = json.loads((self.root / ".loop/team-flow.json").read_text())
        self.assertEqual(state["tasks"]["qa"]["status"], "complete")
        self.assertTrue(state["tasks"]["design"]["outputs"]["design.md"])

    def test_cyclic_and_outside_project_plans_are_rejected(self):
        (self.root / "team-plan.json").write_text(json.dumps({"tasks": [
            {"id": "a", "role": "qa", "depends_on": ["b"], "outputs": ["../unsafe"]},
            {"id": "b", "role": "devops", "depends_on": ["a"], "outputs": ["ok"]}]}))
        self.assertNotEqual(self.flow("init", "team-plan.json").returncode, 0)

    def test_changed_upstream_output_blocks_handoff(self):
        self.assertEqual(self.flow("init", "team-plan.json").returncode, 0)
        self.assertEqual(self.flow("start", "design", "--role", "architect").returncode, 0)
        (self.root / "design.md").write_text("first version")
        self.assertEqual(self.flow("complete", "design", "--role", "architect", "--summary", "ready").returncode, 0)
        (self.root / "design.md").write_text("changed")
        self.assertNotEqual(self.flow("start", "qa", "--role", "qa_engineer").returncode, 0)

    def test_dependency_cycle_is_rejected(self):
        (self.root / "team-plan.json").write_text(json.dumps({"tasks": [
            {"id": "a", "role": "qa", "depends_on": ["b"], "outputs": ["a.txt"]},
            {"id": "b", "role": "devops", "depends_on": ["a"], "outputs": ["b.txt"]}]}))
        self.assertNotEqual(self.flow("init", "team-plan.json").returncode, 0)

    def test_changed_upstream_output_blocks_completion(self):
        self.assertEqual(self.flow("init", "team-plan.json").returncode, 0)
        self.assertEqual(self.flow("start", "design", "--role", "architect").returncode, 0)
        (self.root / "design.md").write_text("first version")
        self.assertEqual(self.flow("complete", "design", "--role", "architect", "--summary", "ready").returncode, 0)
        self.assertEqual(self.flow("start", "qa", "--role", "qa_engineer").returncode, 0)
        (self.root / "design.md").write_text("changed")
        (self.root / "qa.json").write_text('{"exit_code": 0, "command": ["pytest"], "commit": "abc"}')
        self.assertNotEqual(self.flow("complete", "qa", "--role", "qa_engineer", "--summary", "passed").returncode, 0)

    def test_completion_records_claimed_skill_paths_and_rejects_missing_files(self):
        self.assertEqual(self.flow("init", "team-plan.json").returncode, 0)
        self.assertEqual(self.flow("start", "design", "--role", "architect").returncode, 0)
        (self.root / "design.md").write_text("contract")
        self.assertNotEqual(self.flow("complete", "design", "--role", "architect", "--summary", "ready", "--skill", "missing.md").returncode, 0)
        (self.root / "skill.md").write_text("guidance")
        result = self.flow("complete", "design", "--role", "architect", "--summary", "ready", "--skill", "skill.md")
        self.assertEqual(result.returncode, 0, result.stderr)
        state = json.loads((self.root / ".loop/team-flow.json").read_text())
        self.assertTrue(state['events'][-1]['claimed_skills']['skill.md'])

    def test_declared_skills_are_required_for_completion(self):
        plan = json.loads((self.root / 'team-plan.json').read_text())
        plan['tasks'][0]['required_skills'] = ['skills/architect.md']
        (self.root / 'team-plan.json').write_text(json.dumps(plan))
        (self.root / 'skills').mkdir()
        (self.root / 'skills/architect.md').write_text('Architecture guidance')
        self.assertEqual(self.flow('init', 'team-plan.json').returncode, 0)
        self.assertEqual(self.flow('start', 'design', '--role', 'architect').returncode, 0)
        (self.root / 'design.md').write_text('design')
        blocked = self.flow('complete', 'design', '--role', 'architect', '--summary', 'ready')
        self.assertNotEqual(blocked.returncode, 0)
        complete = self.flow('complete', 'design', '--role', 'architect', '--summary', 'ready', '--skill', 'skills/architect.md')
        self.assertEqual(complete.returncode, 0, complete.stderr)

    def test_stalled_task_can_be_blocked_and_retried_without_faking_completion(self):
        self.assertEqual(self.flow('init', 'team-plan.json').returncode, 0)
        self.assertEqual(self.flow('start', 'design', '--role', 'architect').returncode, 0)
        blocked = self.flow('block', 'design', '--role', 'architect', '--reason', 'Host timed out; no completion observed')
        self.assertEqual(blocked.returncode, 0, blocked.stderr)
        state = json.loads((self.root / '.loop/team-flow.json').read_text())
        self.assertEqual(state['tasks']['design']['status'], 'blocked')
        self.assertEqual(state['tasks']['design']['outputs'], {})
        self.assertNotEqual(self.flow('start', 'qa', '--role', 'qa_engineer').returncode, 0)
        self.assertNotEqual(self.flow('retry', 'design', '--role', 'architect', '--reason', 'Earlier attempt ended').returncode, 0)
        self.assertEqual(self.flow('retry', 'design', '--role', 'architect', '--reason', 'Earlier attempt ended', '--confirmed-stopped').returncode, 0)
        self.assertEqual(self.flow('start', 'design', '--role', 'architect').returncode, 0)
        (self.root / 'design.md').write_text('reviewed design')
        self.assertEqual(self.flow('complete', 'design', '--role', 'architect', '--summary', 'ready').returncode, 0)
        state = json.loads((self.root / '.loop/team-flow.json').read_text())
        self.assertEqual([e['action'] for e in state['events']], ['init', 'start', 'block', 'retry', 'start', 'complete'])

    def test_status_identifies_old_in_progress_tasks_without_mutating_state(self):
        self.assertEqual(self.flow('init', 'team-plan.json').returncode, 0)
        self.assertEqual(self.flow('start', 'design', '--role', 'architect').returncode, 0)
        path = self.root / '.loop/team-flow.json'
        state = json.loads(path.read_text())
        state['events'][-1]['timestamp'] = '2020-01-01T00:00:00+00:00'
        path.write_text(json.dumps(state))
        before = path.read_text()
        result = self.flow('status', '--stale-after-minutes', '15')
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertTrue(data['tasks']['design']['stale'])
        self.assertEqual(data['tasks']['design']['status'], 'in_progress')
        self.assertEqual(path.read_text(), before)


if __name__ == "__main__":
    unittest.main()
