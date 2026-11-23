import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/security_scan.py'


class SecurityScanTests(unittest.TestCase):
    def test_empty_image_results_are_not_counted_as_a_scan(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'requirements.txt').write_text('example==1\n')
            scanner = root / 'fake-trivy'
            scanner.write_text('''#!/usr/bin/env python3
import json,sys,datetime
print(json.dumps({"Version":"test", "VulnerabilityDB":{"UpdatedAt":datetime.datetime.now(datetime.timezone.utc).isoformat()}, "Results": [] if sys.argv[1] == "image" else [{"Target":"requirements.txt", "Vulnerabilities":[]}]}))
''')
            scanner.chmod(0o755)
            result = subprocess.run(['python3', str(SCRIPT), '--root', str(root), '--scanner', str(scanner), '--manifest', 'requirements.txt', '--image', 'local:test', '1'], text=True, capture_output=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn('NOT SCANNED', (root / 'docs/reports/sprint-1-security.md').read_text())

    def test_no_images_conflicts_with_discovered_dockerfile(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'requirements.txt').write_text('example==1\n')
            (root / 'Dockerfile').write_text('FROM scratch\n')
            scanner = root / 'fake-trivy'
            scanner.write_text('''#!/usr/bin/env python3
import json,datetime
print(json.dumps({"Version":"test", "VulnerabilityDB":{"UpdatedAt":datetime.datetime.now(datetime.timezone.utc).isoformat()}, "Results":[{"Target":"requirements.txt", "Vulnerabilities":[]}]}))
''')
            scanner.chmod(0o755)
            result = subprocess.run(['python3', str(SCRIPT), '--root', str(root), '--scanner', str(scanner), '--manifest', 'requirements.txt', '--no-images', '1'], text=True, capture_output=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn('Dockerfile', (root / 'docs/reports/sprint-1-security.md').read_text())

    def test_scans_dependencies_and_image_and_blocks_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'requirements.txt').write_text('example==1\n')
            fake = root / 'fake-trivy'
            fake.write_text('#!/usr/bin/env python3\nimport json,sys\nprint(json.dumps({"Results":[{"Target":"requirements.txt" if sys.argv[1]=="fs" else "image", "Vulnerabilities": [] if sys.argv[1]=="fs" else [{"VulnerabilityID":"CVE-TEST","Severity":"HIGH","PkgName":"example","InstalledVersion":"1","FixedVersion":"2"}]}]}))\n')
            fake.chmod(0o755)
            result = subprocess.run(['python3', str(SCRIPT), '--root', str(root), '--scanner', str(fake), '--manifest', 'requirements.txt', '--image', 'local:test', '1'], text=True, capture_output=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            report = (root / 'docs/reports/sprint-1-security.md').read_text()
            self.assertIn('CVE-TEST', report)
            self.assertIn('HIGH', report)
            self.assertIn('local:test', report)
            self.assertTrue((root / 'docs/reports/sprint-1-security.json').is_file())
            records = json.loads((root / 'docs/reports/sprint-1-security.json').read_text())
            self.assertEqual(records['status'], 'blocked')
            self.assertIn('local:test', records['scans'])

    def test_missing_scanner_still_writes_unscanned_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'requirements.txt').write_text('example==1\n')
            result = subprocess.run(['python3', str(SCRIPT), '--root', str(root), '--scanner', '/does/not/exist', '--manifest', 'requirements.txt', '--no-images', '1'], text=True, capture_output=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn('NOT SCANNED', (root / 'docs/reports/sprint-1-security.md').read_text())

    def test_scanner_that_omits_declared_manifest_cannot_report_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'requirements.txt').write_text('example==1\n')
            fake = root / 'fake-trivy'
            fake.write_text('#!/usr/bin/env python3\nprint(\'{"Results": []}\')\n')
            fake.chmod(0o755)
            result = subprocess.run(['python3', str(SCRIPT), '--root', str(root), '--scanner', str(fake), '--manifest', 'requirements.txt', '--no-images', '1'], text=True, capture_output=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn('NOT SCANNED', (root / 'docs/reports/sprint-1-security.md').read_text())

    def test_compose_images_are_discovered_and_scanned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'requirements.txt').write_text('example==1\n')
            (root / 'compose.yaml').write_text('services: {}\n')
            scanner = root / 'fake-trivy'
            scanner.write_text('#!/usr/bin/env python3\nimport json,sys,datetime\nprint(json.dumps({"Version":"test", "VulnerabilityDB":{"UpdatedAt":datetime.datetime.now(datetime.timezone.utc).isoformat()}, "Results":[{"Target":"requirements.txt" if sys.argv[1]=="fs" else "image", "Vulnerabilities":[]}]}))\n')
            scanner.chmod(0o755)
            docker = root / 'fake-docker'
            docker.write_text('#!/usr/bin/env python3\nprint("example:latest")\n')
            docker.chmod(0o755)
            result = subprocess.run(['python3', str(SCRIPT), '--root', str(root), '--scanner', str(scanner), '--docker', str(docker), '--manifest', 'requirements.txt', '--compose', 'compose.yaml', '1'], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = (root / 'docs/reports/sprint-1-security.md').read_text()
            self.assertIn('example:latest', report)

    def test_outdated_scanner_database_blocks_an_apparently_clean_scan(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'requirements.txt').write_text('example==1\n')
            scanner = root / 'fake-trivy'
            scanner.write_text('#!/usr/bin/env python3\nimport json\nprint(json.dumps({"Version":"test", "VulnerabilityDB":{"UpdatedAt":"2020-01-01T00:00:00.123456789Z"}, "Results":[{"Target":"requirements.txt", "Vulnerabilities":[]}]}))\n')
            scanner.chmod(0o755)
            result = subprocess.run(['python3', str(SCRIPT), '--root', str(root), '--scanner', str(scanner), '--manifest', 'requirements.txt', '--no-images', '1'], text=True, capture_output=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn('stale', (root / 'docs/reports/sprint-1-security.md').read_text().lower())

    def test_undeclared_dependency_manifest_blocks_incomplete_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'requirements.txt').write_text('example==1\n')
            (root / 'package-lock.json').write_text('{}\n')
            scanner = root / 'fake-trivy'
            scanner.write_text('#!/usr/bin/env python3\nimport json,datetime\nprint(json.dumps({"Version":"test", "VulnerabilityDB":{"UpdatedAt":datetime.datetime.now(datetime.timezone.utc).isoformat()}, "Results":[{"Target":"requirements.txt", "Vulnerabilities":[]}]}))\n')
            scanner.chmod(0o755)
            result = subprocess.run(['python3', str(SCRIPT), '--root', str(root), '--scanner', str(scanner), '--manifest', 'requirements.txt', '--no-images', '1'], text=True, capture_output=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn('package-lock.json', (root / 'docs/reports/sprint-1-security.md').read_text())

    def test_secret_findings_block_without_writing_the_secret(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'requirements.txt').write_text('example==1\n')
            scanner = root / 'fake-trivy'
            scanner.write_text('''#!/usr/bin/env python3
import json,sys,datetime
base={"Version":"test", "VulnerabilityDB":{"UpdatedAt":datetime.datetime.now(datetime.timezone.utc).isoformat()}}
if "secret" in sys.argv:
 base["Results"]=[{"Target":"app.py", "Secrets":[{"RuleID":"example-secret", "Severity":"HIGH", "Match":"sensitive-test-value", "StartLine":4}]}]
else:
 base["Results"]=[{"Target":"requirements.txt", "Vulnerabilities":[]}]
print(json.dumps(base))
''')
            scanner.chmod(0o755)
            result = subprocess.run(['python3', str(SCRIPT), '--root', str(root), '--scanner', str(scanner), '--manifest', 'requirements.txt', '--no-images', '--secrets', '1'], text=True, capture_output=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            report = (root / 'docs/reports/sprint-1-security.md').read_text()
            raw = (root / 'docs/reports/sprint-1-security.json').read_text()
            self.assertIn('example-secret', report)
            self.assertNotIn('sensitive-test-value', report + raw)


if __name__ == '__main__':
    unittest.main()
