import subprocess
import sys
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/design_audit.py'
HEADINGS = ['Product and actors', 'Requirements and scope', 'System context', 'Components and interfaces',
            'Architecture and deployment', 'Data model and tenancy', 'End-to-end flows',
            'Security and privacy', 'Reliability and recovery', 'Observability and operations',
            'Scalability and performance', 'Decisions and trade-offs', 'Traceability and verification']


class DesignAuditTests(unittest.TestCase):
    def test_missing_sections_and_diagrams_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / 'docs/foundation'
            folder.mkdir(parents=True)
            (folder / 'system_design.md').write_text('# System design\n\n## Product and actors\nBrief.\n')
            result = subprocess.run([sys.executable, str(SCRIPT), '--root', str(root), '--no-database', 'No persistent storage'], text=True, capture_output=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn('Components and interfaces', result.stdout)
            self.assertIn('mind map', result.stdout)

    def test_accepts_complete_structural_evidence_with_explicit_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / 'docs/foundation'
            folder.mkdir(parents=True)
            design = '# System design\n\n' + ''.join('## ' + heading + '\n\nA reviewed description with traceable implementation detail.\n\n' for heading in HEADINGS)
            design += '```text\nClient -> API -> database\n```\n\n```mermaid\nmindmap\n  root((Product))\n```\n\n```mermaid\nerDiagram\n  USER ||--o{ JOB : owns\n```\n\n```mermaid\nsequenceDiagram\n  Client->>API: request\n```\n'
            (folder / 'system_design.md').write_text(design)
            (root / 'schema.sql').write_text('CREATE TABLE example (id INTEGER PRIMARY KEY);\n')
            result = subprocess.run([sys.executable, str(SCRIPT), '--root', str(root), '--schema', 'schema.sql'], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('not verify', result.stdout.lower())

    def test_declared_missing_schema_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = subprocess.run([sys.executable, str(SCRIPT), '--root', str(root), '--schema', '../outside.sql'], text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('schema', result.stdout.lower())


if __name__ == '__main__':
    unittest.main()
