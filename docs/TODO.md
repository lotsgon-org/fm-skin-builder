# Development TODO

This is a living checklist for skin patching and bundle tooling.

- [x] Port standalone patcher into core module and CLI subcommand
- [x] Add CLI tests (patch), and unit tests for parser/patcher
- [x] Add sample skin `skins/test_skin` for docs and tests
- [x] Add `scan` subcommand to index bundles and export stylesheet maps
- [ ] Extend config model to support per-folder mappings or separate mapping files
  - Option A: root config references `mappings/*.json`
  - Option B: per-folder `config.json` with `target_bundle` and filtered mappings
- [ ] Cache mapping under `.cache/skins/<skin>/<bundle>_index.json` and auto-reuse
- [ ] Add conflict resolution strategies when the same selector appears in multiple assets
  - warn by default; support explicit asset pinning in mappings
- [ ] Add auto-discovery of standard install paths to locate bundles
- [ ] Expose a `--dry-run` patch mode to preview changes via index instead of modifying bundles
- [ ] Add docs: “Workflow: scan → map → patch”, with examples referencing the sample skin
