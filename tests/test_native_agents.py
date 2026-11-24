import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts/prepare_kiro_agents.py"


class NativeAgentTests(unittest.TestCase):
    def test_legacy_catalog_does_not_reference_missing_optional_steering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / "kiro", root / "kiro")
            contract_path = root / "kiro/framework-contract.json"
            contract = json.loads(contract_path.read_text())
            contract.pop("optional_roles", None)
            contract_path.write_text(json.dumps(contract))
            (root / "kiro/steering/optional-specialists.md").unlink()
            coordinator = root / "kiro/agents/loop-coordinator.json"
            coordinator.unlink()
            result = subprocess.run(["python3", str(GENERATOR), "--root", str(root)], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            profile = json.loads(coordinator.read_text())
            self.assertNotIn("file://.kiro/steering/optional-specialists.md", profile["resources"])

    def test_requested_specialists_have_routed_existing_activity_skills(self):
        expected = {
            "analytics_engineer", "data_analyst", "data_quality_engineer", "data_governance",
            "bi_developer", "streaming_engineer", "data_platform_engineer", "ai_engineer",
            "agent_evaluator", "ai_safety_engineer", "ai_observability", "rag_engineer",
            "mlops_engineer", "llmops_engineer", "ai_governance", "knowledge_engineer",
            "multimodal_ai_engineer", "fine_tuning_engineer", "product_designer", "learning_designer",
            "privacy_engineer", "accessibility_specialist", "interactive_learning_engineer",
            "performance_engineer", "integration_engineer", "platform_engineer",
            "technical_researcher", "business_analyst",
        }
        contract = json.loads((ROOT / "kiro/framework-contract.json").read_text())
        self.assertTrue(expected.issubset(set(contract.get("optional_roles", []))))
        catalog = (ROOT / "kiro/steering/optional-specialists.md").read_text()
        references = re.findall(r"`([a-z][a-z0-9_]*)/([a-z][a-z0-9_]*\.md)`", catalog)
        for role in expected:
            with self.subTest(role=role):
                self.assertIn(f"`loop-{role.replace('_', '-')}`", catalog)
                files = [name for owner, name in references if owner == role]
                self.assertGreaterEqual(len(files), 2)
                for name in files:
                    self.assertTrue((ROOT / "kiro/skills" / role / name).is_file())

    def test_coordinator_profile_loads_specialist_catalog(self):
        coordinator = json.loads((ROOT / "kiro/agents/loop-coordinator.json").read_text())
        uri = "file://.kiro/steering/optional-specialists.md"
        self.assertIn(uri, coordinator["resources"])
        self.assertTrue((ROOT / "kiro/steering/optional-specialists.md").is_file())

    def test_optional_profiles_load_their_task_routing_catalog_directly(self):
        contract = json.loads((ROOT / "kiro/framework-contract.json").read_text())
        for role in contract["optional_roles"]:
            with self.subTest(role=role):
                profile = json.loads((ROOT / "kiro/agents" / f"loop-{role.replace('_', '-')}.json").read_text())
                self.assertIn("file://.kiro/steering/optional-specialists.md", profile["resources"])

    def test_each_specialist_profile_loads_its_role_definition(self):
        contract = json.loads((ROOT / "kiro/framework-contract.json").read_text())
        for role in contract["required_roles"] + contract["optional_roles"]:
            if role == "shared":
                continue
            with self.subTest(role=role):
                profile = json.loads((ROOT / "kiro/agents" / f"loop-{role.replace('_', '-')}.json").read_text())
                self.assertIn(f"file://.kiro/skills/{role}/SKILL.md", profile["resources"])

    def test_mode_two_points_to_relevant_skills_without_a_conflicting_cap(self):
        routing = (ROOT / "kiro/steering/orchestrator-routing.md").read_text()
        mode_two = routing.split("### MODE 2:", 1)[1].split("### MODE 3:", 1)[0]
        self.assertNotIn("(max 3)", mode_two)
        self.assertIn("optional-specialists.md", mode_two)

    def test_lean_mode_does_not_override_relevant_skill_reads(self):
        routing = (ROOT / "kiro/steering/orchestrator-routing.md").read_text()
        lean = routing.split("### MODE 5:", 1)[1].split("## PRIORITY:", 1)[0]
        self.assertNotIn("≤3 files", lean)
        self.assertIn("relevant", lean.lower())

    def test_optional_role_generates_a_selectable_profile_without_becoming_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / "kiro", root / "kiro")
            contract_path = root / "kiro/framework-contract.json"
            contract = json.loads(contract_path.read_text())
            contract["optional_roles"] = ["fixture_analyst"]
            contract_path.write_text(json.dumps(contract))
            skill = root / "kiro/skills/fixture_analyst/SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text('---\nname: Fixture Analyst\ndescription: Analyze test fixtures\n---\n')
            result = subprocess.run(["python3", str(GENERATOR), "--root", str(root)], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            profile_path = root / "kiro/agents/loop-fixture-analyst.json"
            self.assertTrue(profile_path.is_file(), "optional role must have a selectable profile")
            profile = json.loads(profile_path.read_text())
            self.assertIn("skill://.kiro/skills/loop-fixture-analyst/SKILL.md", profile["resources"])
            self.assertNotIn("fixture_analyst", contract["required_roles"])

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
