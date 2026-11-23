import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/migration_setup.py'


class MigrationSetupTests(unittest.TestCase):
    def test_scaffold_supports_real_upgrade_and_downgrade(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = subprocess.run([sys.executable, str(SCRIPT), '--root', str(root)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            revision = root / 'migrations/versions/001_create_example.py'
            revision.write_text('from alembic import op\nimport sqlalchemy as sa\nrevision = "001"\ndown_revision = None\nbranch_labels = None\ndepends_on = None\ndef upgrade():\n    op.create_table("example", sa.Column("id", sa.Integer, primary_key=True))\ndef downgrade():\n    op.drop_table("example")\n')
            env = dict(os.environ, LOOP_DATABASE_URL='sqlite:///' + str(root / 'test.db'))
            for action in [('upgrade', 'head'), ('downgrade', 'base'), ('upgrade', 'head')]:
                run = subprocess.run([sys.executable, '-m', 'alembic', *action], cwd=root, env=env, capture_output=True, text=True)
                self.assertEqual(run.returncode, 0, run.stderr)
            import sqlite3
            with sqlite3.connect(root / 'test.db') as conn:
                self.assertEqual(conn.execute('select version_num from alembic_version').fetchone()[0], '001')
                self.assertTrue(conn.execute("select name from sqlite_master where name='example'").fetchone())

    def test_does_not_overwrite_existing_configuration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'alembic.ini').write_text('existing')
            result = subprocess.run([sys.executable, str(SCRIPT), '--root', str(root)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((root / 'alembic.ini').read_text(), 'existing')
            self.assertFalse((root / 'migrations').exists())


if __name__ == '__main__':
    unittest.main()
