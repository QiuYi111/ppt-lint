# Ppt linter — Context

Refined/extracted context for session continuity.
Update this file as work progresses.

## Current State

- Status: Core implementation complete
- Last updated: 2026-04-12
- Branch: feat/ppt-lint-core
- Commit: a8780b2

## Key Findings

- Python `cmd` package name conflicts with pytest internals — renamed to `cli/`
- python-pptx 1.0.2 API: `SlideMaster` doesn't have `slide_width` directly, need defensive access
- Setuptools editable install needs explicit package include for `cli*`
- `openclaw system event` used for completion notification from coding agents

## Architecture Decisions

- DDD: domain (pure Python) / infrastructure (python-pptx wrappers)
- click for CLI, rich for terminal output
- AI rules compiled via Claude API, cached in `.ppt-lint-cache/`
- Test fixtures created programmatically via python-pptx

## Test Results

- 28/28 tests passing
- ruff lint: all checks passed
- Manual test: bad.pptx (9 issues detected, 5 auto-fixable, fix reduces to 2 issues)
- Output formats: terminal (rich tables), JSON, HTML — all verified

## Remaining Work

- [ ] AI rule compilation end-to-end test (requires ANTHROPIC_API_KEY)
- [ ] Content margin checking (spacing.content_margin_pt)
- [ ] Slide number position checking
- [ ] Accent color detection
- [ ] More edge case tests (empty slides, corrupt files)
- [ ] GitHub remote setup and PR creation
