import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/usage_report.py'


class UsageReportTests(unittest.TestCase):
    def test_overlapping_records_are_not_summed_without_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            p = root / 'usage.json'
            p.write_text(json.dumps({'sprint': 1, 'records': [
                {'input_tokens': 100, 'credits': 2, 'credit_kind': 'estimate', 'source': 'session total'},
                {'input_tokens': 60, 'credits': 1, 'credit_kind': 'estimate', 'source': 'task in session'}]}))
            result = subprocess.run([sys.executable, str(SCRIPT), '--root', str(root), '--input', str(p)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = (root / 'docs/reports/sprint-1-usage.md').read_text()
            self.assertNotIn('Input tokens: 160', report)
            self.assertNotIn('Estimate credits: 3', report)
            self.assertIn('overlap', report.lower())

    def test_disjoint_records_can_be_summed_with_sourced_attestation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            p = root / 'usage.json'
            p.write_text(json.dumps({'sprint': 1, 'aggregation': {'non_overlapping': True, 'source': 'provider call IDs 1 and 2'}, 'records': [
                {'input_tokens': 100, 'source': 'call 1'}, {'input_tokens': 60, 'source': 'call 2'}]}))
            result = subprocess.run([sys.executable, str(SCRIPT), '--root', str(root), '--input', str(p)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = (root / 'docs/reports/sprint-1-usage.md').read_text()
            self.assertIn('Input tokens: 160', report)
            self.assertIn('provider call IDs 1 and 2', report)

    def test_reports_estimates_and_unknown_tokens_separately(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            p = root / 'usage.json'
            p.write_text(json.dumps({'sprint': 1, 'records': [
                {'agent': 'architect', 'story': 'S1-01', 'model': 'unknown',
                 'credits': 0.93, 'credit_kind': 'estimate', 'source': 'Kiro session display'},
                {'agent': 'qa', 'story': 'S1-01', 'input_tokens': 200, 'output_tokens': 50,
                 'source': 'provider export'}]}))
            result = subprocess.run([sys.executable, str(SCRIPT), '--root', str(root), '--input', str(p)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = (root / 'docs/reports/sprint-1-usage.md').read_text()
            self.assertIn('0.93', report)
            self.assertIn('Estimate', report)
            self.assertIn('Unknown', report)
            self.assertIn('provider export', report)
            self.assertIn('incomplete', report.lower())

    def test_rejects_missing_sources_and_negative_values(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            p = root / 'usage.json'
            for record in [{'input_tokens': -1, 'source': 'provider'}, {'input_tokens': 1}]:
                p.write_text(json.dumps({'sprint': 1, 'records': [record]}))
                result = subprocess.run([sys.executable, str(SCRIPT), '--root', str(root), '--input', str(p)], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((root / 'docs/reports/sprint-1-usage.md').exists())


if __name__ == '__main__':
    unittest.main()
