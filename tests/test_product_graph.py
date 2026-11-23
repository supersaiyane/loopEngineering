import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/product_graph.py"


class ProductGraphTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.folder = self.root / "docs/graph"
        self.folder.mkdir(parents=True)
        (self.root / "app.py").write_text("pass\n")

    def merge(self):
        return subprocess.run(["python3", str(SCRIPT), "--root", str(self.root), "merge", "1"],
                              text=True, capture_output=True)

    def write_patch(self, edges):
        patch = {"story": "S1-01", "sprint": 1,
                 "nodes_added": [{"id": "api", "type": "service", "label": "API", "file": "app.py"},
                                 {"id": "db", "type": "datastore", "label": "DB"}],
                 "edges_added": edges}
        (self.folder / "graph-patch-sprint1-S1-01.yaml").write_text(json.dumps(patch))

    def test_merge_is_repeatable_and_keeps_patches_and_offline_visualization(self):
        self.write_patch([{"from": "api", "to": "db", "type": "stores-in"}])
        first = self.merge()
        self.assertEqual(first.returncode, 0, first.stderr)
        graph = json.loads((self.folder / "product-graph.yaml").read_text())
        self.assertEqual(len(graph["nodes"]), 2)
        self.assertEqual(len(graph["edges"]), 1)
        self.assertTrue((self.folder / "graph-patch-sprint1-S1-01.yaml").is_file())
        html = (self.folder / "product-graph.html").read_text()
        self.assertIn("api", html)
        self.assertNotIn("cdn.jsdelivr.net", html)
        self.assertFalse((self.folder / "knowledge-graph-sprint1.html").exists())
        self.assertFalse((self.folder / "knowledge-graph-sprint-1-story-S1-01.html").exists())
        self.assertIn('S1-01', html)
        self.assertIn('Filter by story', html)
        self.assertIn('Reset view', html)
        self.assertEqual(self.merge().returncode, 0)
        self.assertEqual(len(json.loads((self.folder / "product-graph.yaml").read_text())["nodes"]), 2)

    def test_new_sprint_preserves_existing_graph_and_legacy_files(self):
        self.write_patch([{"from": "api", "to": "db", "type": "stores-in"}])
        self.assertEqual(self.merge().returncode, 0)
        legacy = self.folder / "knowledge-graph-sprint1.html"
        legacy.write_text('previous user snapshot')
        (self.folder / "graph-patch-sprint2-S2-01.yaml").write_text(json.dumps({
            "story": "S2-01", "sprint": 2,
            "nodes_added": [{"id": "worker", "type": "service", "label": "Worker"}],
            "edges_added": [{"from": "worker", "to": "api", "type": "calls"}]}))
        result = subprocess.run(["python3", str(SCRIPT), "--root", str(self.root), "merge", "2"], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(legacy.read_text(), 'previous user snapshot')
        self.assertFalse((self.folder / "knowledge-graph-sprint2.html").exists())
        html = (self.folder / "product-graph.html").read_text()
        self.assertIn('S1-01', html)
        self.assertIn('S2-01', html)
        self.assertEqual(len(json.loads((self.folder / "product-graph.yaml").read_text())["nodes"]), 3)

    def test_unknown_edge_blocks_merge_without_writing_graph(self):
        self.write_patch([{"from": "api", "to": "missing", "type": "calls"}])
        self.assertNotEqual(self.merge().returncode, 0)
        self.assertFalse((self.folder / "product-graph.yaml").exists())

    def test_symlinked_output_is_never_overwritten(self):
        self.write_patch([])
        outside = self.root / 'user-notes.html'
        outside.write_text('keep these notes')
        (self.folder / 'product-graph.html').symlink_to(outside)
        result = self.merge()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(outside.read_text(), 'keep these notes')
        self.assertFalse((self.folder / 'product-graph.yaml').exists())

    def test_sprint_story_cards_require_a_patch_for_each_story(self):
        stories = self.root / 'docs/sprint-1/stories'
        stories.mkdir(parents=True)
        (stories / 'S1-01.md').write_text('# First\n')
        (stories / 'S1-02.md').write_text('# Second\n')
        self.write_patch([])
        result = subprocess.run(["python3", str(SCRIPT), "--root", str(self.root), "merge", "1", "--require-complete"], text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('S1-02', result.stderr)
        self.assertFalse((self.folder / 'product-graph.yaml').exists())

    def test_nonstructural_story_patch_remains_in_graph_provenance(self):
        (self.folder / 'graph-patch-sprint1-S1-01.yaml').write_text(json.dumps({
            'story': 'S1-01', 'sprint': 1, 'description': 'Documentation only',
            'nodes_added': [], 'edges_added': []}))
        result = self.merge()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('S1-01', (self.folder / 'product-graph.html').read_text())
        self.assertEqual(len(json.loads((self.folder / 'product-graph.yaml').read_text())['nodes']), 0)

    def test_story_can_reference_node_added_by_a_later_patch(self):
        first = {"story": "S1-01", "sprint": 1,
                 "nodes_added": [{"id": "api", "type": "service", "label": "API"}],
                 "edges_added": [{"from": "api", "to": "db", "type": "stores-in"}]}
        second = {"story": "S1-02", "sprint": 1,
                  "nodes_added": [{"id": "db", "type": "datastore", "label": "DB"}]}
        (self.folder / "graph-patch-sprint1-S1-01.yaml").write_text(json.dumps(first))
        (self.folder / "graph-patch-sprint1-S1-02.yaml").write_text(json.dumps(second))
        result = self.merge()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(json.loads((self.folder / "product-graph.yaml").read_text())["edges"]), 1)

    def test_changed_applied_patch_is_not_silently_replayed(self):
        self.write_patch([{"from": "api", "to": "db", "type": "stores-in"}])
        self.assertEqual(self.merge().returncode, 0)
        before = (self.folder / "product-graph.yaml").read_text()
        self.write_patch([{"from": "api", "to": "db", "type": "calls"}])
        self.assertNotEqual(self.merge().returncode, 0)
        self.assertEqual((self.folder / "product-graph.yaml").read_text(), before)


if __name__ == "__main__":
    unittest.main()
