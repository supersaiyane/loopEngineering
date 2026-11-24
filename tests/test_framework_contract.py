"""Regression checks for the public framework contract."""

import json
import os
import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class FrameworkContractTests(unittest.TestCase):
    def test_hook_does_not_block_general_user_input_or_specs(self):
        hook = json.loads((ROOT / "kiro/hooks/elite-team-orchestrator.json").read_text())
        blocked = [h.get("matcher") for h in hook["hooks"] if h.get("trigger") == "PreToolUse"]
        self.assertNotIn("user_input", blocked)
        self.assertNotIn("spec", blocked)

    def test_hook_describes_the_five_canonical_modes(self):
        hook = json.loads((ROOT / "kiro/hooks/elite-team-orchestrator.json").read_text())
        prompt = next(h["action"]["prompt"] for h in hook["hooks"] if h["name"] == "Orchestrator Router")
        for description in ("Mode 1 (Full)", "Mode 2 (Single Role)", "Mode 3 (Direct)",
                            "Mode 4 (Hybrid)", "Mode 5 (Lean)"):
            with self.subTest(description=description):
                self.assertIn(description, prompt)

    def test_hook_instructs_discovery_before_mode_and_model_selection(self):
        hook = json.loads((ROOT / "kiro/hooks/elite-team-orchestrator.json").read_text())
        prompt = next(h["action"]["prompt"] for h in hook["hooks"] if h["name"] == "Orchestrator Router")
        self.assertIn("all seven discovery questions", prompt)
        self.assertIn("model selection after discovery", prompt)
        doc = (ROOT / "kiro/steering/discovery-engine.md").read_text()
        self.assertIn("Present all seven questions", doc)
        self.assertIn("kiro-cli chat --list-models", doc)

    def test_model_recommendations_use_only_confirmed_options(self):
        hook = json.loads((ROOT / "kiro/hooks/elite-team-orchestrator.json").read_text())
        prompt = next(h["action"]["prompt"] for h in hook["hooks"] if h["name"] == "Orchestrator Router")
        guide = (ROOT / "kiro/steering/model-selection.md").read_text()
        self.assertIn("read model-selection.md", prompt)
        self.assertIn("Do not name or recommend unconfirmed models", guide)
        self.assertIn("Do not invent model capabilities", guide)
        self.assertIn("ask the user for the model picker list", guide)

    def test_discovery_examples_use_score_ranges_consistently(self):
        doc = (ROOT / "kiro/steering/discovery-engine.md").read_text()
        self.assertIn("**8 → Lean → Mode 5**", doc)
        self.assertIn("**14 → Standard → Mode 4**", doc)

    def test_website_discovery_scores_match_contract(self):
        html = (ROOT / "index.html").read_text()
        discovery = html.split('id="discovery"', 1)[1].split('<!-- PONYTAIL -->', 1)[0]
        rows = re.findall(r'<span class="score-range">([^<]+)</span>.*?<span class="score-mode"[^>]*>Mode (\d)', discovery)
        self.assertEqual(rows, [("15–21", "1"), ("10–14", "4"), ("5–9", "5"), ("0–4", "3")])
        for label in ("Platform", "Scale", "Complexity", "Deployment", "Revenue", "Design", "Security"):
            self.assertIn(label, discovery)

    def test_proxy_does_not_kill_unrelated_processes(self):
        launcher = (ROOT / "scripts/start-kiro-pxpipe.sh").read_text()
        self.assertNotIn("kill $(lsof", launcher)
        self.assertIn("Port $PORT is already in use", launcher)

    def test_proxy_starts_the_installed_binary_without_downloading(self):
        with tempfile.TemporaryDirectory() as tmp:
            bindir = pathlib.Path(tmp)
            for name, body in {"lsof": "exit 1", "npx": "echo unexpected-download; exit 12",
                               "pxpipe-proxy": "echo local-proxy-started"}.items():
                executable = bindir / name
                executable.write_text("#!/bin/sh\n" + body + "\n")
                executable.chmod(0o755)
            env = dict(os.environ, PATH=f"{tmp}:/usr/bin:/bin")
            result = subprocess.run(["bash", str(ROOT / "scripts/start-kiro-pxpipe.sh")],
                                    env=env, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("local-proxy-started", result.stdout)
            self.assertNotIn("unexpected-download", result.stdout)

    def test_pages_publishes_only_curated_site_files(self):
        workflow = (ROOT / ".github/workflows/deploy-pages.yml").read_text()
        self.assertIn("path: _site", workflow)
        for item in ("index.html", "loop-engineering-white-paper-v5.pdf",
                     "loop-engineering-white-paper-v5.docx", "GOAT.md"):
            with self.subTest(item=item):
                self.assertIn(item, workflow)

    def test_qualified_role_skill_references_exist(self):
        skill_root = ROOT / "kiro/skills"
        roles = {p.name for p in skill_root.iterdir() if p.is_dir()}
        missing = []
        for doc in (ROOT / "kiro/steering").glob("*.md"):
            for role, filename in re.findall(r"(?<![\w])([a-z][a-z0-9_]*)/([a-z][a-z0-9_]*\.md)", doc.read_text()):
                if role in roles and not (skill_root / role / filename).is_file():
                    missing.append(f"{doc.name}: {role}/{filename}")
        self.assertEqual(missing, [])

    def test_shell_scripts_have_valid_syntax(self):
        subprocess.run(["bash", "-n", str(ROOT / "scripts/bootstrap-project.sh"),
                        str(ROOT / "scripts/start-kiro-pxpipe.sh")], check=True)

    def test_bootstrap_refuses_to_overwrite_existing_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = pathlib.Path(tmp) / "existing"
            target.mkdir()
            marker = target / "keep.txt"
            marker.write_text("preserve")
            result = subprocess.run(["bash", str(ROOT / "scripts/bootstrap-project.sh"), "existing", tmp],
                                    input="y\n", text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(marker.read_text(), "preserve")
            self.assertFalse((target / ".kiro").exists())

    def test_bootstrap_rejects_unsafe_project_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = pathlib.Path(tmp) / "projects"
            parent.mkdir()
            for name in ("../escaped", "bad|name", ".", ".."):
                with self.subTest(name=name):
                    result = subprocess.run(["bash", str(ROOT / "scripts/bootstrap-project.sh"), name, str(parent)],
                                            text=True, capture_output=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("invalid project name", result.stderr.lower())
            self.assertFalse((pathlib.Path(tmp) / "escaped").exists())

    def test_bootstrap_rejects_dangling_target_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = pathlib.Path(tmp) / "sample"
            target.symlink_to(pathlib.Path(tmp) / "elsewhere")
            result = subprocess.run(["bash", str(ROOT / "scripts/bootstrap-project.sh"), "sample", tmp],
                                    text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(target.is_symlink())
            self.assertFalse((pathlib.Path(tmp) / "elsewhere").exists())

    def test_bootstrap_does_not_copy_unrelated_local_scripts_or_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(["bash", str(ROOT / "scripts/bootstrap-project.sh"), "sample", tmp],
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            target = pathlib.Path(tmp) / "sample"
            self.assertFalse((target / "scripts/sheet_generator.py").exists())
            self.assertTrue((target / "scripts/team_flow.py").is_file())
            self.assertTrue((target / "scripts/framework_upgrade.py").is_file())
            self.assertTrue((target / "scripts/sprint_report.py").is_file())
            self.assertTrue((target / "scripts/security_scan.py").is_file())
            self.assertTrue((target / "scripts/project_index.py").is_file())
            self.assertTrue((target / "scripts/product_graph_template.html").is_file())
            self.assertTrue((target / ".kiro/agents/loop-coordinator.json").is_file())
            catalog = json.loads((target / ".kiro/framework-contract.json").read_text())
            for role in catalog.get("optional_roles", []):
                alias = "loop-" + role.replace("_", "-")
                with self.subTest(role=role):
                    self.assertTrue((target / ".kiro/agents" / f"{alias}.json").is_file())
                    self.assertTrue((target / ".kiro/skills" / alias / "SKILL.md").is_file())
                    self.assertTrue((target / ".kiro/skills" / role / "SKILL.md").is_file())
            validation = subprocess.run(["python3", str(target / "scripts/validate-framework.py")],
                                        text=True, capture_output=True)
            self.assertEqual(validation.returncode, 0, validation.stderr)
            if catalog.get("optional_roles"):
                role = catalog["optional_roles"][0]
                (target / ".kiro/agents" / f"loop-{role.replace('_', '-')}.json").unlink()
                broken = subprocess.run(["python3", str(target / "scripts/validate-framework.py")],
                                        text=True, capture_output=True)
                self.assertNotEqual(broken.returncode, 0)
                self.assertIn("missing optional role profile", broken.stderr)
            head = subprocess.run(["git", "-C", str(target), "rev-parse", "--verify", "HEAD"],
                                  capture_output=True)
            self.assertNotEqual(head.returncode, 0)

    def test_bootstrap_reports_missing_required_reference_as_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = pathlib.Path(tmp) / "source"
            shutil.copytree(ROOT / "kiro", source / "kiro")
            shutil.copytree(ROOT / "scripts", source / "scripts", ignore=shutil.ignore_patterns("sheet_generator.py"))
            (source / "docs/research").mkdir(parents=True)
            result = subprocess.run(["bash", str(source / "scripts/bootstrap-project.sh"), "sample", tmp],
                                    text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("MISSING: reference", result.stdout)
            self.assertFalse((pathlib.Path(tmp) / "sample/.git").exists())


if __name__ == "__main__":
    unittest.main()
