from pathlib import Path
import json
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/project_index.py'


class ProjectIndexTests(unittest.TestCase):
    def test_indexes_foundation_and_sprints_without_inventing_durations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            f = root / 'docs/foundation'
            f.mkdir(parents=True)
            (f / 'prd.md').write_text('# PRD\n')
            (f / 'market-research.md').write_text('# Research\n')
            s = root / 'docs/sprint-1'
            (s / 'stories').mkdir(parents=True)
            (s / 'jira').mkdir()
            (s / 'stories/S1-01.md').write_text('# Build API\n- **Roles:** lead backend | engineer backend\n')
            (s / 'jira/S1-01.local.json').write_text(json.dumps({'story_id':'S1-01','status':'In Progress'}))
            result = subprocess.run(['python3', str(SCRIPT), '--root', str(root)], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            index = (f / 'INDEX.md').read_text()
            self.assertLess(index.index('market-research.md'), index.index('prd.md'))
            report = (f / 'project-work-report.md').read_text()
            self.assertIn('S1-01', report)
            self.assertIn('In Progress', report)
            self.assertIn('backend', report)
            self.assertIn('Unknown', report)
            self.assertTrue((f / 'prd.md').is_file())

    def test_preserves_user_authored_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            f = root / 'docs/foundation'
            f.mkdir(parents=True)
            (f / 'INDEX.md').write_text('User index\n')
            result = subprocess.run(['python3', str(SCRIPT), '--root', str(root)], text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((f / 'INDEX.md').read_text(), 'User index\n')

    def test_includes_future_sprints_with_role_effort_and_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            f = root / 'docs/foundation'
            f.mkdir(parents=True)
            (f / 'sprint-plan.json').write_text(json.dumps({'sprints': [
                {'number': 2, 'goal': 'Tenant isolation', 'stories': ['S2-01'],
                 'stages': [{'stage': 'Design', 'role': 'architect', 'planned_days': 2,
                             'actual_days': 1.5, 'evidence': 'meeting record'},
                            {'stage': 'Build', 'role': 'backend'}]}]}))
            result = subprocess.run(['python3', str(SCRIPT), '--root', str(root)], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = (f / 'project-work-report.md').read_text()
            for value in ['Tenant isolation', 'S2-01', 'architect', '1.5', 'meeting record', 'backend', 'Unknown']:
                self.assertIn(value, report)

    def test_records_document_creation_sequence_without_renaming(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            f = root / 'docs/foundation'
            f.mkdir(parents=True)
            (f / 'prd.md').write_text('# PRD\n')
            (f / 'research.md').write_text('# Research\n')
            def run(*args):
                return subprocess.run(['python3', str(SCRIPT), '--root', str(root), *args], text=True, capture_output=True)
            self.assertEqual(run('--record', 'research.md').returncode, 0)
            self.assertEqual(run('--record', 'prd.md').returncode, 0)
            self.assertEqual(run('--record', 'research.md').returncode, 0)
            index = (f / 'INDEX.md').read_text()
            self.assertIn('| 01 | [research.md]', index)
            self.assertIn('| 02 | [prd.md]', index)
            ledger = json.loads((root / '.loop/foundation-sequence.json').read_text())
            self.assertEqual([e['path'] for e in ledger['documents']], ['research.md', 'prd.md'])
            self.assertNotEqual(run('--record', '../unsafe.md').returncode, 0)


if __name__ == '__main__':
    unittest.main()
