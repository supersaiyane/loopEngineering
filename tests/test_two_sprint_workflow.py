"""Exercise two offline sprints end to end in a disposable Git repository."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TwoSprintWorkflowTests(unittest.TestCase):
    def test_local_sprints_preserve_evidence_and_cumulative_graph(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp).resolve()
            env = dict(os.environ)
            for name in ('JIRA_BASE_URL', 'JIRA_EMAIL', 'JIRA_API_TOKEN'):
                env.pop(name, None)

            def run(*args):
                result = subprocess.run(args, cwd=project, env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                return result

            run('git', 'init', '-q')
            run('git', 'config', 'user.name', 'Fixture')
            run('git', 'config', 'user.email', 'fixture@example.invalid')
            for sprint in (1, 2):
                stories = project / f'docs/sprint-{sprint}/stories'
                stories.mkdir(parents=True)
                (stories / f'S{sprint}-01.md').write_text(f'# S{sprint}-01\nAcceptance criteria\n')
            run('git', 'add', 'docs')
            run('git', 'commit', '-qm', 'docs: plan disposable sprints')
            for sprint in (1, 2):
                story = f'S{sprint}-01'
                run('python3', str(ROOT / 'scripts/sprint_gate.py'), '--root', str(project), 'init-local', str(sprint))
                artifact = project / f'app{sprint}.txt'
                artifact.write_text(f'sprint {sprint}\n')
                graph = project / 'docs/graph'
                graph.mkdir(parents=True, exist_ok=True)
                patch = {'sprint': sprint, 'story': story,
                         'nodes_added': [{'id': f'service{sprint}', 'type': 'service', 'label': f'Service {sprint}', 'file': artifact.name}],
                         'edges_added': ([{'from': 'service2', 'to': 'service1', 'type': 'calls'}] if sprint == 2 else [])}
                (graph / f'graph-patch-sprint{sprint}-{story}.yaml').write_text(json.dumps(patch))
                run('git', 'add', artifact.name, f'docs/graph/graph-patch-sprint{sprint}-{story}.yaml')
                run('git', 'commit', '-qm', f'feat: implement {story}')
                run('python3', str(ROOT / 'scripts/sprint_gate.py'), '--root', str(project),
                    'run-check', str(sprint), story, '--', 'python3', '-c', f"assert open('app{sprint}.txt').read().strip() == 'sprint {sprint}'")
                run('python3', str(ROOT / 'scripts/sprint_gate.py'), '--root', str(project),
                    'update-local', str(sprint), story, '--status', 'Done')
                run('python3', str(ROOT / 'scripts/sprint_gate.py'), '--root', str(project),
                    'check-sprint', str(sprint), '--mode', 'local')
                run('python3', str(ROOT / 'scripts/product_graph.py'), '--root', str(project), 'merge', str(sprint), '--require-complete')
                run('python3', str(ROOT / 'scripts/sprint_report.py'), '--root', str(project), str(sprint))
                run('git', 'add', f'docs/sprint-{sprint}', 'docs/graph', 'docs/reports')
                run('git', 'commit', '-qm', f'docs: close sprint {sprint}')
            graph = json.loads((project / 'docs/graph/product-graph.yaml').read_text())
            self.assertEqual({node['id'] for node in graph['nodes']}, {'service1', 'service2'})
            self.assertEqual(len(graph['edges']), 1)
            for sprint in (1, 2):
                self.assertTrue((project / f'docs/sprint-{sprint}/evidence/S{sprint}-01.json').is_file())
                self.assertTrue((project / f'docs/reports/sprint-{sprint}-git-tracker.md').is_file())


if __name__ == '__main__':
    unittest.main()
