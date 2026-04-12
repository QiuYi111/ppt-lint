# Ppt linter — Context

Refined/extracted context for session continuity.
Update this file as work progresses.

## Current State

- Status: AI-powered role classification implemented, ready for validation
- Last updated: 2026-04-12
- Branch: feat/ppt-lint-core
- Latest commit: 83160f4

## Key Findings

- Python `cmd` package name conflicts with pytest internals — renamed to `cli/`
- python-pptx 1.0.2 API: `SlideMaster` doesn't have `slide_width` directly, need defensive access
- Setuptools editable install needs explicit package include for `cli*`
- `report_terminal` (rich console.print) pollutes JSON output — must only call when format is "terminal"
- Dry-run messages must go to stderr, not stdout, to avoid corrupting piped JSON
- **Heuristic classifiers are fundamentally limited** — every new template introduces edge cases. AI classification is the correct solution (PER-67 user feedback).

## Architecture Decisions

- DDD: domain (pure Python, no pptx imports) / infrastructure (python-pptx wrappers)
- click for CLI, rich for terminal output
- AI rules compiled via Claude API, cached in `.ppt-lint-cache/`
- Test fixtures created programmatically via python-pptx
- Output format dispatch in CLI: only call report_terminal for terminal mode
- **Role classification: Claude CLI first, heuristic fallback**
  - `role_classifier.py` calls `claude --print --bare --output-format json` per slide
  - Shape metadata (text, font, position, placeholder type, name) serialized via `extract_slide_summary()`
  - Per-slide content-hash caching in `.ppt-lint-cache/roles/`
  - Engine computes role_map once/slide, passes to all checkers via `role_map` kwarg
  - Backward compatible: TypeError fallback for legacy checkers
- **Background color checks slide.background.fill**, not individual shape fills
- **Slide number regex** supports plain digits and "N / M" format

## Claude CLI Integration (role_classifier.py)

- `claude --print --bare --model claude-sonnet-4-20250514 --output-format json --dangerously-skip-permissions`
- `--bare` mode reduces system prompt (~44K vs 64K without)
- Cost: ~$0.015/slide with cache read, ~$0.20 cold (first call)
- Timeout: 45s per slide
- Response parsing: `{"type": "result", "result": "<json>"}` — strips markdown fences
- Fallback: heuristic classifier when Claude unavailable or times out
- `--no-ai` flag disables AI entirely (tests, CI, offline use)

## Test Results

- **pytest**: 28/28 passed (all use `use_ai=False`)
- **ruff**: all checks passed
- **AI classification verified**: Claude correctly classifies title/body shapes on test PPT
- **E2E manual tests**: all 8 scenarios passed (with `--no-ai`)

## PER-67 Fix History (2026-04-12)

### Commit d3ad382 — Heuristic improvements (still limited)
1. Role classifier rewrite with 6-signal heuristic
2. Background color: `get_slide_background_color()` checks slide background
3. Page number regex: "N / M" format support

### Commit 83160f4 — AI-powered classification (proper fix)
- New `role_classifier.py` with Claude CLI integration
- Engine refactored: role_map computed once per slide, passed to checkers
- Heuristic classifier retained as fallback
- `--no-ai` CLI flag for offline/CI mode

## GitHub Setup

- **Repo:** https://github.com/QiuYi111/ppt-lint (public)
- **Default branch:** main
- **Feature branch:** feat/ppt-lint-core (pushed)

## Remaining Work

- [ ] Validate against real template PPT (midterm_fixed.pptx) — measure false positive reduction from 833
- [ ] AI rule compilation end-to-end test (requires ANTHROPIC_API_KEY)
- [ ] Content margin checking (spacing.content_margin_pt)
- [ ] Slide number position checking
- [ ] Accent color detection
- [ ] More edge case tests (empty slides, corrupt files)
- [ ] Create PR from feat/ppt-lint-core to main
- [ ] User review and merge
- [ ] Consider batch mode: classify all slides in one Claude call for large PPTs (cost optimization)
