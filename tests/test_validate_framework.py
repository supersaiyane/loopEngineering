"""Exercise the offline validator against isolated framework fixtures."""
import json
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/validate-framework.py"


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        (self.root / "kiro/hooks").mkdir(parents=True)
        (self.root / "kiro/steering").mkdir(parents=True)
        (self.root / "kiro/steering/execution-contract.md").write_text("contract")
        (self.root / "kiro/hooks/elite-team-orchestrator.json").write_text(json.dumps({
            "version": "v1", "hooks": [{"name": "Orchestrator Router", "trigger": "UserPromptSubmit",
              "enabled": True, "action": {"type": "agent", "prompt": (
                  "execution-contract.md; 0–4 → Mode 3; 5–9 → Mode 5; "
                  "10–14 → Mode 4; 15–21 → Mode 1")}}]}))
        (self.root / "kiro/framework-contract.json").write_text(json.dumps({
            "required_files": ["kiro/steering/execution-contract.md"],
            "score_bands": [{"min": 0, "max": 4, "mode": 3}, {"min": 5, "max": 9, "mode": 5},
                            {"min": 10, "max": 14, "mode": 4}, {"min": 15, "max": 21, "mode": 1}]}))

    def run_validator(self):
        return subprocess.run(["python3", str(SCRIPT), "--root", str(self.root)],
                              capture_output=True, text=True)

    def test_valid_fixture_passes(self):
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_reference_fails(self):
        (self.root / "kiro/steering/execution-contract.md").unlink()
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing required file", result.stderr)

    def test_invalid_hook_json_fails(self):
        (self.root / "kiro/hooks/elite-team-orchestrator.json").write_text("{")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid JSON", result.stderr)

    def test_disabled_router_is_rejected(self):
        path = self.root / "kiro/hooks/elite-team-orchestrator.json"
        data = json.loads(path.read_text())
        data["hooks"][0]["enabled"] = False
        path.write_text(json.dumps(data))
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("enabled", result.stderr)

    def test_router_score_mapping_drift_fails(self):
        path = self.root / "kiro/hooks/elite-team-orchestrator.json"
        data = json.loads(path.read_text())
        data["hooks"][0]["action"]["prompt"] = data["hooks"][0]["action"]["prompt"].replace("0–4 → Mode 3", "0–4 → Mode 5")
        path.write_text(json.dumps(data))
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("router score", result.stderr)

    def test_malformed_action_is_reported_without_traceback(self):
        path = self.root / "kiro/hooks/elite-team-orchestrator.json"
        data = json.loads(path.read_text())
        data["hooks"][0]["action"] = []
        path.write_text(json.dumps(data))
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("action", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_conflicting_score_mapping_fails(self):
        p = self.root / "kiro/framework-contract.json"
        data = json.loads(p.read_text())
        data["score_bands"][0]["mode"] = 5
        p.write_text(json.dumps(data))
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("score bands", result.stderr)

    def test_adapter_mode_drift_fails(self):
        adapters = self.root / "kiro/adapters"
        adapters.mkdir()
        (adapters / "chatgpt-system-prompt.md").write_text("0–4=Micro(5)")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("adapter mode mapping", result.stderr)

    def test_missing_qualified_skill_fails(self):
        (self.root / "kiro/skills/architect").mkdir(parents=True)
        (self.root / "kiro/steering/roles.md").write_text("architect/missing.md")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing skill reference", result.stderr)

    def test_missing_required_role_fails(self):
        path = self.root / "kiro/framework-contract.json"
        data = json.loads(path.read_text())
        data["required_roles"] = ["architect"]
        path.write_text(json.dumps(data))
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing role skill", result.stderr)

    def test_missing_optional_role_is_reported(self):
        path = self.root / "kiro/framework-contract.json"
        data = json.loads(path.read_text())
        data["optional_roles"] = ["data_analyst"]
        path.write_text(json.dumps(data))
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("data_analyst/SKILL.md", result.stderr)

    def test_optional_role_without_generated_profile_is_reported(self):
        path = self.root / "kiro/framework-contract.json"
        data = json.loads(path.read_text())
        data["optional_roles"] = ["data_analyst"]
        path.write_text(json.dumps(data))
        skill = self.root / "kiro/skills/data_analyst/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text('---\nname: Data Analyst\ndescription: Analyze data\n---\n')
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("loop-data-analyst.json", result.stderr)
