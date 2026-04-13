# Ppt linter — Context

Refined/extracted context for session continuity.
Update this file as work progresses.

## Current State

- Status: PR #3 open for review (feat/ppt-lint-core → main)
- Last updated: 2026-04-13
- Branch: feat/ppt-lint-core
- Latest commit: 8968a44

## Key Findings

- Python `cmd` package name conflicts with pytest internals — renamed to `cli/`
- python-pptx 1.0.2 API: `SlideMaster` doesn't have `slide_width` directly, need defensive access
- Setuptools editable install needs explicit package include for `cli*`
- `report_terminal` (rich console.print) pollutes JSON output — must only call when format is "terminal"
- Dry-run messages must go to stderr, not stdout, to avoid corrupting piped JSON
- **Heuristic classifiers are fundamentally limited** — every new template introduces edge cases. AI classification is the correct solution (PER-67 user feedback).
- `slide.background.fill.type` is BACKGROUND (5) even when no solid fill — accessing `.fore_color` raises TypeError. Must wrap in try/except.

## Architecture Decisions

- DDD: domain (pure Python, no pptx imports) / infrastructure (python-pptx wrappers)
- click for CLI, rich for terminal output
- AI rules compiled via Claude API, cached in `.ppt-lint-cache/`
- Test fixtures created programmatically via python-pptx
- Output format dispatch in CLI: only call report_terminal for terminal mode
- **Role classification: Direct HTTP API (Anthropic-compatible), heuristic fallback**
  - `role_classifier.py` calls Anthropic-compatible API directly (Z.AI proxy)
  - Shape metadata serialized via `extract_slide_summary()`
  - Batch mode: all slides in one API call
  - Per-slide content-hash caching in `.ppt-lint-cache/roles/`
  - Engine computes role_map once/slide, passes to all checkers via `role_map` kwarg
  - `--no-ai` flag disables AI entirely (tests, CI, offline use)
- **Background color checks slide.background.fill**, not individual shape fills
- **Slide number regex** supports plain digits and "N / M" format
- **Color text checking**: two modes — `whitelist` (exact match) and `contrast` (WCAG ratio ≥ 4.5:1)
- **Severity threshold**: `--severity-threshold error|warning|info` CLI flag to filter noise

## API Integration (role_classifier.py)

- **API**: Anthropic-compatible HTTP (e.g. Z.AI proxy)
- Direct urllib calls, no SDK dependency
- Model: configurable via `PPT_LINT_MODEL` env (default: glm-5.1)
- Timeout: 120s per batch call
- Retry: once on 429 with backoff
- Fallback: heuristic classifier when API unavailable
- Proxy: inherits HTTPS_PROXY/HTTP_PROXY env vars

## Test Results

- **pytest**: 29/29 passed (all use `use_ai=False`)
- **ruff**: all checks passed
- **AI classification verified**: Claude correctly classifies title/body shapes on test PPT
- **Contrast mode test**: detects poor contrast ratio (< 4.5:1)

## PER-67 Fix History (2026-04-12 ~ 2026-04-13)

### Commit d3ad382 — Heuristic improvements (still limited)
1. Role classifier rewrite with 6-signal heuristic
2. Background color: `get_slide_background_color()` checks slide background
3. Page number regex: "N / M" format support

### Commit 83160f4 — AI-powered classification (proper fix)
- New `role_classifier.py` with Claude CLI integration
- Engine refactored: role_map computed once per slide, passed to checkers
- Heuristic classifier retained as fallback
- `--no-ai` CLI flag for offline/CI mode

### Commit de104a3 — Batch mode + real PPT validation
- Batch all slides into one Claude call
- Validation: 833 → 786 issues (heuristic) with AI

### Commit 0cfe4cc — Switch to claude-glm (local Claude Code)
- Use claude-glm instead of claude CLI

### Commit 8968a44 — Contrast mode + severity filter + bg fix
- `colors.text_mode: "contrast"` — WCAG contrast ratio checking
- `--severity-threshold` CLI flag
- Fix `get_slide_background_color()` TypeError on no-fill backgrounds
- Default to white background in contrast mode
- ruff import sorting fixes

## GitHub Setup

- **Repo:** https://github.com/QiuYi111/ppt-lint (public)
- **Default branch:** main
- **PR #3:** feat/ppt-lint-core → main (open)

## Remaining Work

- [ ] User review and merge PR #3
- [ ] AI rule compilation end-to-end test (requires API key)
- [ ] Content margin checking (spacing.content_margin_pt)
- [ ] Slide number position checking
- [ ] Accent color detection
- [ ] More edge case tests (empty slides, corrupt files)
- [ ] Consider batch mode cost optimization for very large PPTs (100+ slides)
- [ ] Validate contrast mode against midterm_fixed.pptx for exact issue count
