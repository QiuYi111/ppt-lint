# Ppt linter — Context

Refined/extracted context for session continuity.
Update this file as work progresses.

## Current State

- Status: Core implementation complete, fully tested
- Last updated: 2026-04-12
- Branch: feat/ppt-lint-core
- Latest commit: 2a2a41a

## Key Findings

- Python `cmd` package name conflicts with pytest internals — renamed to `cli/`
- python-pptx 1.0.2 API: `SlideMaster` doesn't have `slide_width` directly, need defensive access
- Setuptools editable install needs explicit package include for `cli*`
- `report_terminal` (rich console.print) pollutes JSON output — must only call when format is "terminal"
- Dry-run messages must go to stderr, not stdout, to avoid corrupting piped JSON

## Architecture Decisions

- DDD: domain (pure Python, no pptx imports) / infrastructure (python-pptx wrappers)
- click for CLI, rich for terminal output
- AI rules compiled via Claude API, cached in `.ppt-lint-cache/`
- Test fixtures created programmatically via python-pptx
- Output format dispatch in CLI: only call report_terminal for terminal mode

## Test Results (Final)

- **pytest**: 28/28 passed
- **ruff**: all checks passed
- **E2E manual tests**: all 8 scenarios passed
  - `bad.pptx`: 9 issues (3E/6W), 5 fixable
  - `good.pptx`: 0 issues, passed
  - `--fix --dry-run`: file unchanged
  - `--fix`: 9 → 2 issues (only non-fixable warnings remain)
  - HTML report: valid, self-contained
  - JSON output: clean, no pollution

## GitHub Setup

- **Repo:** https://github.com/QiuYi111/ppt-lint (public)
- **Default branch:** main
- **Feature branch:** feat/ppt-lint-core (pushed)
- README rewritten as enterprise-grade with badges, architecture diagram, roadmap

## Remaining Work

- [ ] AI rule compilation end-to-end test (requires ANTHROPIC_API_KEY)
- [ ] Content margin checking (spacing.content_margin_pt)
- [ ] Slide number position checking
- [ ] Accent color detection
- [ ] More edge case tests (empty slides, corrupt files)
- [ ] Create PR from feat/ppt-lint-core to main
- [ ] User review and merge
