"""Release archives exclude the historical test project without deleting it."""
import io
from pathlib import Path
import subprocess
import tarfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReleaseArchiveTests(unittest.TestCase):
    def test_archive_excludes_test_project_and_contains_framework(self):
        archive = subprocess.run(['git', 'archive', '--worktree-attributes', 'HEAD'], cwd=ROOT,
                                 capture_output=True, check=True).stdout
        with tarfile.open(fileobj=io.BytesIO(archive)) as result:
            paths = result.getnames()
        self.assertIn('kiro/framework-contract.json', paths)
        self.assertFalse(any(path == 'healthguard-pro' or path.startswith('healthguard-pro/') for path in paths))
