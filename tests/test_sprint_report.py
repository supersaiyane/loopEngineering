import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/sprint_report.py'


class SprintReportTests(unittest.TestCase):
    def test_project_without_repository_does_not_report_parent_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            subprocess.run(['git', 'init', '-q', str(parent)], check=True)
            subprocess.run(['git', '-C', str(parent), 'config', 'user.name', 'Test'], check=True)
            subprocess.run(['git', '-C', str(parent), 'config', 'user.email', 'test@example.invalid'], check=True)
            (parent / 'other.txt').write_text('other project')
            subprocess.run(['git', '-C', str(parent), 'add', 'other.txt'], check=True)
            subprocess.run(['git', '-C', str(parent), 'commit', '-qm', 'feat: S1-01 unrelated parent'], check=True)
            root = parent / 'new-project'
            stories = root / 'docs/sprint-1/stories'
            stories.mkdir(parents=True)
            (stories / 'S1-01.md').write_text('# Story\n')
            result = subprocess.run(['python3', str(SCRIPT), '--root', str(root), '1'], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = (root / 'docs/reports/sprint-1-git-tracker.md').read_text()
            self.assertNotIn('unrelated parent', report)
            self.assertIn('Unknown', report)

    def test_pending_planned_roles_and_completed_outputs_are_visible(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stories = root / 'docs/sprint-1/stories'
            stories.mkdir(parents=True)
            (stories / 'S1-01.md').write_text('# Story\n')
            (root / '.loop').mkdir()
            (root / '.loop/team-flow.json').write_text(json.dumps({
                'tasks': {'S1-01-design': {'role': 'architect', 'status': 'pending'},
                          'S1-01-build': {'role': 'backend', 'status': 'complete'}},
                'events': [{'task': 'S1-01-build', 'role': 'backend', 'action': 'complete',
                            'outputs': {'src/app.py': 'hash'}, 'summary': 'Built'}]}))
            result = subprocess.run(['python3', str(SCRIPT), '--root', str(root), '1'], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = (root / 'docs/reports/sprint-1-agents.md').read_text()
            self.assertIn('architect', report)
            self.assertIn('pending', report.lower())
            self.assertIn('src/app.py', report)

    def test_report_records_tracker_history_worktree_and_baseline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            folder = root / 'docs/sprint-1'
            for name in ('stories', 'jira'):
                (folder / name).mkdir(parents=True)
            (folder / 'stories/S1-01.md').write_text('# Story\n')
            (folder / 'jira/S1-01.local.json').write_text(json.dumps({
                'story_id': 'S1-01', 'status': 'Blocked', 'sync_state': 'pending',
                'events': [{'timestamp': '2026-11-23T10:00:00Z', 'status': 'Blocked', 'note': 'Waiting for QA'}]}))
            (root / 'uncommitted.txt').write_text('work in progress\n')
            result = subprocess.run(['python3', str(SCRIPT), '--root', str(root), '1'], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = (root / 'docs/reports/sprint-1-git-tracker.md').read_text()
            self.assertIn('Waiting for QA', report)
            self.assertIn('uncommitted.txt', report)
            self.assertIn('S1-01.local.json', report)
            baseline = (root / 'docs/reports/baseline.md').read_text()
            self.assertIn('Sprint 1', baseline)
            self.assertIn('unknown', baseline.lower())
            self.assertIn('0 / 1', baseline)

    def test_reports_distinguish_local_tracking_and_recorded_handoffs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            subprocess.run(['git', '-C', str(root), 'config', 'user.name', 'Test'], check=True)
            subprocess.run(['git', '-C', str(root), 'config', 'user.email', 'test@example.invalid'], check=True)
            folder = root / 'docs/sprint-1'
            for name in ('stories', 'jira', 'evidence'):
                (folder / name).mkdir(parents=True)
            (folder / 'stories/S1-01.md').write_text('# Story\n')
            (root / 'app.py').write_text('print(1)\n')
            subprocess.run(['git', '-C', str(root), 'add', 'app.py', 'docs/sprint-1/stories'], check=True)
            subprocess.run(['git', '-C', str(root), 'commit', '-qm', 'feat: S1-01'], check=True)
            sha = subprocess.run(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True, capture_output=True, check=True).stdout.strip()
            (folder / 'jira/S1-01.local.json').write_text(json.dumps({'story_id':'S1-01','status':'Done','sync_state':'pending','events':[{'status':'Done','note':'completed'}]}))
            (folder / 'evidence/S1-01.json').write_text(json.dumps({'story_id':'S1-01','commit':sha,'exit_code':0,'command':['pytest']}))
            (root / '.loop').mkdir()
            (root / '.loop/team-flow.json').write_text(json.dumps({'tasks': {'S1-01-build': {'role':'devops_engineer','status':'complete'}}, 'events':[{'action':'complete','task':'S1-01-build','role':'devops_engineer','summary':'built','claimed_skills':{'skills/devops.md':'hash'}}]}))
            result = subprocess.run(['python3', str(SCRIPT), '--root', str(root), '1'], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            tracking = (root / 'docs/reports/sprint-1-git-tracker.md').read_text()
            agents = (root / 'docs/reports/sprint-1-agents.md').read_text()
            self.assertIn('pending', tracking)
            self.assertIn(sha[:12], tracking)
            self.assertIn('devops_engineer', agents)
            self.assertIn('skills/devops.md', agents)
            self.assertIn('S1-01', agents)
            self.assertIn('not proof', agents.lower())
            self.assertTrue((root / 'docs/reports/discipline-dashboard.md').is_file())
            dashboard = (root / 'docs/reports/discipline-dashboard.md').read_text()
            self.assertIn('Sprint 1', dashboard)
            self.assertIn('1 / 1', dashboard)
            self.assertIn('unknown', dashboard.lower())

    def test_missing_evidence_is_unknown_and_user_report_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / 'docs/sprint-1/stories'
            folder.mkdir(parents=True)
            (folder / 'S1-01.md').write_text('# Story\n')
            out = root / 'docs/reports'
            out.mkdir()
            (out / 'sprint-1-agents.md').write_text('Personal notes\n')
            result = subprocess.run(['python3', str(SCRIPT), '--root', str(root), '1'], text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((out / 'sprint-1-agents.md').read_text(), 'Personal notes\n')

    def test_reports_elapsed_wall_time_only_when_matching_timestamps_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stories = root / 'docs/sprint-1/stories'
            stories.mkdir(parents=True)
            (stories / 'S1-01.md').write_text('# Story\n')
            (root / '.loop').mkdir()
            events = [
                {'action': 'start', 'task': 'S1-01-design', 'role': 'architect', 'timestamp': '2026-11-23T10:00:00+00:00'},
                {'action': 'complete', 'task': 'S1-01-design', 'role': 'architect', 'timestamp': '2026-11-23T11:30:00+00:00', 'summary': 'Design'},
                {'action': 'complete', 'task': 'S1-01-build', 'role': 'backend', 'summary': 'Build'}]
            (root / '.loop/team-flow.json').write_text(json.dumps({'events': events}))
            result = subprocess.run(['python3', str(SCRIPT), '--root', str(root), '1'], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = (root / 'docs/reports/sprint-1-agents.md').read_text()
            self.assertIn('90.0 min', report)
            self.assertIn('wall time', report.lower())
            self.assertIn('Unknown', report)

    def test_retry_reports_only_the_completed_attempts_elapsed_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stories = root / 'docs/sprint-1/stories'
            stories.mkdir(parents=True)
            (stories / 'S1-01.md').write_text('# Story\n')
            (root / '.loop').mkdir()
            def e(action, timestamp):
                return {'action': action, 'task': 'S1-01-design', 'role': 'architect', 'timestamp': timestamp}
            events = [e('start', '2026-11-23T09:00:00+00:00'),
                      e('block', '2026-11-23T10:00:00+00:00'),
                      e('retry', '2026-11-23T10:10:00+00:00'),
                      e('start', '2026-11-23T11:00:00+00:00'),
                      e('complete', '2026-11-23T11:20:00+00:00')]
            (root / '.loop/team-flow.json').write_text(json.dumps({'events': events}))
            result = subprocess.run(['python3', str(SCRIPT), '--root', str(root), '1'], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = (root / 'docs/reports/sprint-1-agents.md').read_text()
            self.assertIn('20.0 min', report)
            self.assertNotIn('140.0 min', report)


if __name__ == '__main__':
    unittest.main()
