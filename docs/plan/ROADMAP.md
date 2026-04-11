# ppt-lint Implementation Roadmap

## Phase 1: Foundation (Domain Models + CLI Skeleton)
- [x] Project structure setup
- [ ] Domain models (LintIssue, Rule, CompiledRuleSet)
- [ ] CLI entry point with click
- [ ] `ppt-lint init` command (scaffold rules.yaml)
- [ ] Basic `ppt-lint check` command (parse args, load file)

## Phase 2: Rule Parsing + Primitive Checker
- [ ] YAML rule parser with validation
- [ ] Primitive rule checkers (fonts, colors, alignment, spacing, slide_number, charts)
- [ ] pptx_adapter (wrapping python-pptx for slide inspection)

## Phase 3: Lint Engine + Reporter
- [ ] Engine orchestrator (run all rules, collect issues)
- [ ] Terminal reporter with rich (colored output, summary)
- [ ] JSON reporter
- [ ] HTML reporter

## Phase 4: Auto-Fix
- [ ] Fixer module (apply fixes to pptx)
- [ ] Primitive rule fixers
- [ ] `--fix` and `--fix --dry-run` flags
- [ ] Output fixed file (overwrite or new file)

## Phase 5: AI Rules + Cache
- [ ] Claude API integration for rule compilation
- [ ] Cache manager (hash-based invalidation)
- [ ] AI rule loader in compiler

## Phase 6: Testing + Polish
- [ ] Test fixtures (programmatic .pptx creation)
- [ ] Unit tests for all modules
- [ ] Integration tests (end-to-end check + fix)
- [ ] Edge cases (empty slides, corrupt files, missing fonts)
- [ ] README with usage examples
