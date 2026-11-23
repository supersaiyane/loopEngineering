#!/usr/bin/env python3
"""Set up an opt-in Alembic revision chain for a Python project."""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ENVIRONMENT = '''"""Apply reviewed Alembic revisions to the explicitly selected database."""
import os
from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config
url = os.environ.get("LOOP_DATABASE_URL")
if not url:
    raise RuntimeError("Set LOOP_DATABASE_URL to the intended database before running migrations")
config.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
# Set this to the application's imported SQLAlchemy metadata before using autogenerate.
target_metadata = None

if context.is_offline_mode():
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = engine_from_config(config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    ini, migrations = root / 'alembic.ini', root / 'migrations'
    if ini.exists() or ini.is_symlink() or migrations.exists() or migrations.is_symlink():
        raise ValueError('existing Alembic configuration or migrations: refusing to overwrite')
    with tempfile.TemporaryDirectory(prefix='loop-alembic-') as temp:
        temp = Path(temp)
        result = subprocess.run([sys.executable, '-m', 'alembic', 'init', 'migrations'], cwd=temp, capture_output=True, text=True)
        if result.returncode:
            raise ValueError('Alembic initialization failed; install Alembic in the selected Python environment')
        (temp / 'migrations/env.py').write_text(ENVIRONMENT, encoding='utf-8')
        # Never retain Alembic's example URL in a real project's configuration.
        config = (temp / 'alembic.ini').read_text(encoding='utf-8')
        config = '\n'.join('sqlalchemy.url =' if line.startswith('sqlalchemy.url =') else line for line in config.splitlines()) + '\n'
        (temp / 'alembic.ini').write_text(config, encoding='utf-8')
        shutil.copytree(temp / 'migrations', migrations)
        shutil.copyfile(temp / 'alembic.ini', ini)
    print('Alembic scaffold created; write and review revisions and set LOOP_DATABASE_URL explicitly.')
    print('No schema or migration has been generated or executed.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as exc:
        print(f'BLOCKED: {exc}', file=sys.stderr)
        sys.exit(1)
