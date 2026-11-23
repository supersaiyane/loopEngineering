import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/discovery_score.py'


class DiscoveryScoreTests(unittest.TestCase):
    def score(self, answers, *extra):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'answers.json'
            path.write_text(json.dumps(answers))
            return subprocess.run([sys.executable, str(SCRIPT), '--input', str(path), *extra], text=True, capture_output=True)

    def test_scores_actual_options_and_keeps_selected_mode_separate(self):
        result = self.score({'platform': 'web', 'scale': 'saas', 'complexity': 'enterprise',
                             'deployment': 'cloud', 'revenue': 'subscription', 'design': 'polished',
                             'security': 'privacy'}, '--mode', '1')
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data['score'], 15)
        self.assertEqual(data['selected_mode'], 1)
        self.assertEqual(data['answers']['platform']['points'], 1)

    def test_unknown_answers_produce_range_and_cannot_be_forced_to_21(self):
        result = self.score({'platform': 'web', 'complexity': 'enterprise'}, '--mode', '1')
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertIsNone(data['score'])
        self.assertEqual(data['minimum'], 4)
        self.assertEqual(data['maximum'], 19)
        self.assertIn('security', data['unknown'])
        self.assertEqual(data['selected_mode'], 1)

    def test_rejects_unrecognized_answer_instead_of_guessing(self):
        result = self.score({'platform': 'backend plus web is multiple'})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('platform', result.stderr)


if __name__ == '__main__':
    unittest.main()
