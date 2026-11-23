import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts/prepare_kiro_agents.py"


class NativeAgentTests(unittest.TestCase):
    def test_generation_preserves_original_skills_and_creates_role_profiles(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / "kiro", root / "kiro")
            original = (root / "kiro/skills/qa_engineer/SKILL.md").read_text()
            result = subprocess.run(["python3", str(GENERATOR), "--root", str(root)], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            wrapper = root / "kiro/skills/loop-qa-engineer/SKILL.md"
            self.assertIn("name: loop-qa-engineer", wrapper.read_text())
            self.assertEqual((root / "kiro/skills/qa_engineer/SKILL.md").read_text(), original)
            config = json.loads((root / "kiro/agents/loop-qa-engineer.json").read_text())
            self.assertIn("skill://.kiro/skills/loop-qa-engineer/SKILL.md", config["resources"])
            self.assertIn("mandatory", config["prompt"].lower())
            self.assertIn("exact skill", config["prompt"].lower())
            coordinator = json.loads((root / "kiro/agents/loop-coordinator.json").read_text())
            self.assertIn("subagent", coordinator["tools"])
            wrapper.write_text("user custom content\n")
            result = subprocess.run(["python3", str(GENERATOR), "--root", str(root)], text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(wrapper.read_text(), "user custom content\n")


if __name__ == "__main__":
    unittest.main()
