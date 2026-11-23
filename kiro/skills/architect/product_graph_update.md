<!-- LOAD-TYPE: CHECKLIST -->
# Product Knowledge Graph Update — Architect

At sprint closure, the architect reviews the story patches and runs the merge
command. A patch is retained for every story, including stories with no
structural changes. The generated graph describes supplied records, not proof
that every component or relationship exists in code.

## Review the patches

1. Find `docs/graph/graph-patch-sprintN-<STORY-ID>.yaml` for every story in
   sprint N. Each must identify its `story` and numeric `sprint`. For a story
   without structural changes, use empty change lists and describe the work and
   reason in the patch; do not invent a component.
2. Check the story changes against code, schema, tests and reviewed ADRs. Confirm
   unique node IDs, existing source paths and valid relationship endpoints.
   Reconcile conflicts in the source patches before merging. Patches already
   recorded in the graph are immutable: the script blocks changes to their hashes.
3. Architectural decisions that affect product structure may be represented as
   `type: decision` entries in the appropriate story's `nodes_added` list and
   linked through `edges_added`. The architect reviews these entries before the
   first merge. Keep the separate `decisions` block empty: the merge script does
   not accept it. Do not manually edit the generated graph.

## Merge and verify

Run `python3 scripts/product_graph.py merge N --require-complete` from the project root. The script
validates and merges the sprint's patches into `docs/graph/product-graph.yaml`
then renders `docs/graph/product-graph.html`, a single interactive offline page
with an embedded SVG. Rerunning an unchanged merge is safe; changed or missing
previously applied patches block the operation. Report its actual output rather
than assuming it prints a particular log tag.

Inspect the graph, story filters, component details, source links and statuses.
Preserve every story patch and any historical HTML files. Create no additional
sprint or story HTML views. Include reviewed patches and generated graph files in
project history. Report missing patches, invalid links or merge errors as blocked.
For an entirely non-structural sprint, merge its empty story patches so story
provenance is still retained.
