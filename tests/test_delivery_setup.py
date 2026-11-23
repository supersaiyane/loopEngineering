import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/delivery_setup.py'


class DeliverySetupTests(unittest.TestCase):
    def test_project_commands_run_and_missing_checks_block_preflight(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'requirements.txt').write_text('example==1\n')
            result = subprocess.run([sys.executable, str(SCRIPT), '--root', str(root),
                                     '--manifest', 'requirements.txt', '--no-images',
                                     '--test-command', 'python3 -c "print(123)"'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            run = subprocess.run([sys.executable, str(SCRIPT), '--root', str(root), '--run-command', 'test'], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn('123', run.stdout)
            missing = subprocess.run([sys.executable, str(SCRIPT), '--root', str(root), '--run-command', 'lint'], capture_output=True, text=True)
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn('not configured', missing.stderr)
            makefile = (root / 'Makefile').read_text()
            self.assertIn('preflight:', makefile)
            self.assertIn('test:', makefile)
            self.assertIn('lint:', makefile)
            (root / 'scripts').mkdir()
            shutil.copy(SCRIPT, root / 'scripts/delivery_setup.py')
            make_test = subprocess.run(['make', 'test'], cwd=root, capture_output=True, text=True)
            self.assertEqual(make_test.returncode, 0, make_test.stderr)
            self.assertIn('123', make_test.stdout)
            preflight = subprocess.run(['make', 'preflight'], cwd=root, capture_output=True, text=True)
            self.assertNotEqual(preflight.returncode, 0)
            self.assertIn('not configured', preflight.stderr)

    def test_generates_configured_ci_and_makefile(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'requirements.txt').write_text('example==1\n')
            (root / 'compose.yaml').write_text('services: {}\n')
            result = subprocess.run([sys.executable, str(SCRIPT), '--root', str(root), '--manifest', 'requirements.txt', '--compose', 'compose.yaml', '--sprint', '2'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads((root / '.loop/security-config.json').read_text())['sprint'], 2)
            workflow = (root / '.github/workflows/loop-security.yml').read_text()
            self.assertIn('docker compose -f compose.yaml build', workflow)
            self.assertIn('if: always()', workflow)
            self.assertIn('sprint-*-security.*', workflow)
            self.assertIn('security-scan:', (root / 'Makefile').read_text())
            again = subprocess.run([sys.executable, str(SCRIPT), '--root', str(root), '--manifest', 'requirements.txt', '--compose', 'compose.yaml'], capture_output=True, text=True)
            self.assertNotEqual(again.returncode, 0)

    def test_rejects_unsafe_paths_and_requires_image_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'requirements.txt').write_text('example==1\n')
            for options in [[], ['--compose', '../bad'], ['--compose', 'x;echo-bad']]:
                result = subprocess.run([sys.executable, str(SCRIPT), '--root', str(root), '--manifest', 'requirements.txt', *options], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((root / 'Makefile').exists())


if __name__ == '__main__':
    unittest.main()
