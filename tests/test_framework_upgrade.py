"""Safe upgrades run only in isolated fixtures, never in an existing project."""
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/framework_upgrade.py'


class FrameworkUpgradeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.old, self.new, self.target = (self.root / p for p in ('old', 'new', 'project'))
        for source in (self.old, self.new):
            (source / 'kiro/steering').mkdir(parents=True)
            (source / 'kiro/skills').mkdir(parents=True)
        (self.target / '.kiro/steering').mkdir(parents=True)
        (self.old / 'kiro/steering/routing.md').write_text('old\n')
        (self.new / 'kiro/steering/routing.md').write_text('new\n')
        (self.new / 'kiro/steering/new.md').write_text('new file\n')
        (self.target / '.kiro/steering/routing.md').write_text('old\n')
        self.backup = self.root / 'backup'

    def run_upgrade(self, *args):
        return subprocess.run(['python3', str(SCRIPT), *map(str, args)], capture_output=True, text=True)

    def test_preview_is_read_only_and_apply_can_be_rolled_back(self):
        args = ('--source', self.new, '--baseline', self.old, '--target', self.target)
        preview = self.run_upgrade(*args)
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertEqual((self.target / '.kiro/steering/routing.md').read_text(), 'old\n')
        self.assertFalse((self.target / '.kiro/steering/new.md').exists())
        applied = self.run_upgrade(*args, '--apply', '--backup-dir', self.backup)
        self.assertEqual(applied.returncode, 0, applied.stderr)
        self.assertEqual((self.target / '.kiro/steering/routing.md').read_text(), 'new\n')
        self.assertEqual((self.target / '.kiro/steering/new.md').read_text(), 'new file\n')
        restored = self.run_upgrade('--target', self.target, '--restore', self.backup)
        self.assertEqual(restored.returncode, 0, restored.stderr)
        self.assertEqual((self.target / '.kiro/steering/routing.md').read_text(), 'old\n')
        self.assertFalse((self.target / '.kiro/steering/new.md').exists())

    def test_customized_existing_file_blocks_the_entire_upgrade(self):
        path = self.target / '.kiro/steering/routing.md'
        path.write_text('user customized\n')
        result = self.run_upgrade('--source', self.new, '--baseline', self.old, '--target', self.target,
                                  '--apply', '--backup-dir', self.backup)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('conflict', result.stderr.lower())
        self.assertEqual(path.read_text(), 'user customized\n')
        self.assertFalse((self.target / '.kiro/steering/new.md').exists())
        self.assertFalse(self.backup.exists())

    def test_customized_file_is_preserved_when_upstream_did_not_change_it(self):
        (self.new / 'kiro/steering/routing.md').write_text('old\n')
        path = self.target / '.kiro/steering/routing.md'
        path.write_text('user customized\n')
        result = self.run_upgrade('--source', self.new, '--baseline', self.old, '--target', self.target,
                                  '--apply', '--backup-dir', self.backup)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(path.read_text(), 'user customized\n')
        self.assertEqual((self.target / '.kiro/steering/new.md').read_text(), 'new file\n')

    def test_restore_refuses_to_overwrite_subsequent_user_edits(self):
        result = self.run_upgrade('--source', self.new, '--baseline', self.old, '--target', self.target,
                                  '--apply', '--backup-dir', self.backup)
        self.assertEqual(result.returncode, 0, result.stderr)
        (self.target / '.kiro/steering/routing.md').write_text('later edits\n')
        restored = self.run_upgrade('--target', self.target, '--restore', self.backup)
        self.assertNotEqual(restored.returncode, 0)
        self.assertIn('conflict', restored.stderr.lower())
        self.assertEqual((self.target / '.kiro/steering/routing.md').read_text(), 'later edits\n')
        self.assertTrue((self.target / '.kiro/steering/new.md').exists())

    def test_customized_permissions_survive_an_upstream_content_update(self):
        path = self.target / '.kiro/steering/routing.md'
        path.chmod(0o600)
        result = self.run_upgrade('--source', self.new, '--baseline', self.old, '--target', self.target,
                                  '--apply', '--backup-dir', self.backup)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(path.read_text(), 'new\n')

    def test_restore_refuses_a_subsequent_permission_change(self):
        result = self.run_upgrade('--source', self.new, '--baseline', self.old, '--target', self.target,
                                  '--apply', '--backup-dir', self.backup)
        self.assertEqual(result.returncode, 0, result.stderr)
        path = self.target / '.kiro/steering/routing.md'
        path.chmod(0o600)
        restored = self.run_upgrade('--target', self.target, '--restore', self.backup)
        self.assertNotEqual(restored.returncode, 0)
        self.assertIn('conflict', restored.stderr.lower())
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_upstream_mode_only_change_is_applied_and_can_be_reverted(self):
        old = self.old / 'kiro/steering/routing.md'
        new = self.new / 'kiro/steering/routing.md'
        new.write_bytes(old.read_bytes())
        old.chmod(0o644)
        new.chmod(0o755)
        (self.target / '.kiro/steering/routing.md').chmod(0o644)
        result = self.run_upgrade('--source', self.new, '--baseline', self.old, '--target', self.target,
                                  '--apply', '--backup-dir', self.backup)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.target / '.kiro/steering/routing.md').stat().st_mode & 0o777, 0o755)
        restored = self.run_upgrade('--target', self.target, '--restore', self.backup)
        self.assertEqual(restored.returncode, 0, restored.stderr)
        self.assertEqual((self.target / '.kiro/steering/routing.md').stat().st_mode & 0o777, 0o644)

    def test_conflicting_executable_bit_change_is_rejected(self):
        (self.old / 'kiro/steering/routing.md').chmod(0o644)
        (self.new / 'kiro/steering/routing.md').chmod(0o755)
        path = self.target / '.kiro/steering/routing.md'
        path.chmod(0o700)
        result = self.run_upgrade('--source', self.new, '--baseline', self.old, '--target', self.target,
                                  '--apply', '--backup-dir', self.backup)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('conflict', result.stderr.lower())
        self.assertEqual(path.read_text(), 'old\n')

    def test_symlinked_project_path_is_rejected(self):
        outside = self.root / 'outside'
        outside.mkdir()
        (self.target / '.kiro/steering/routing.md').unlink()
        (self.target / '.kiro/steering/routing.md').symlink_to(outside / 'routing.md')
        result = self.run_upgrade('--source', self.new, '--baseline', self.old, '--target', self.target,
                                  '--apply', '--backup-dir', self.backup)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('symlink', result.stderr.lower())
        self.assertFalse((outside / 'routing.md').exists())

    def test_unchanged_upstream_path_cannot_hide_a_project_symlink(self):
        for source in (self.old, self.new):
            (source / 'kiro/steering/stable.md').write_text('stable\n')
        outside = self.root / 'outside.md'
        outside.write_text('user data\n')
        (self.target / '.kiro/steering/stable.md').symlink_to(outside)
        result = self.run_upgrade('--source', self.new, '--baseline', self.old, '--target', self.target)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('symlink', result.stderr.lower())
        self.assertEqual(outside.read_text(), 'user data\n')

    def test_file_blocking_a_new_directory_fails_before_any_updates(self):
        (self.new / 'kiro/steering/z').mkdir()
        (self.new / 'kiro/steering/z/new.md').write_text('new\n')
        (self.target / '.kiro/steering/z').write_text('user file\n')
        result = self.run_upgrade('--source', self.new, '--baseline', self.old, '--target', self.target,
                                  '--apply', '--backup-dir', self.backup)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('not a directory', result.stderr.lower())
        self.assertEqual((self.target / '.kiro/steering/routing.md').read_text(), 'old\n')
        self.assertFalse(self.backup.exists())
