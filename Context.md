# Ppt linter — Context

Refined/extracted context for session continuity.
Update this file as work progresses.

## Current State

- Status: Core implementation complete, false positive reduction applied
- Last updated: 2026-04-12
- Branch: feat/ppt-lint-core
- Latest commit: d3ad382

## Key Findings

- Python `cmd` package name conflicts with pytest internals — renamed to `cli/`
- python-pptx 1.0.2 API: `SlideMaster` doesn't have `slide_width` directly, need defensive access
- Setuptools editable install needs explicit package include for `cli*`
- `report_terminal` (rich console.print) pollutes JSON output — must only call when format is "terminal"
- Dry-run messages must go to stderr, not stdout, to avoid corrupting piped JSON
- Template PPTs generate ~833 false positives: decorative shapes misclassified as backgrounds, body text includes separators/headers/footers, page number format "N / M" not recognized (PER-67)

## Architecture Decisions

- DDD: domain (pure Python, no pptx imports) / infrastructure (python-pptx wrappers)
- click for CLI, rich for terminal output
- AI rules compiled via Claude API, cached in `.ppt-lint-cache/`
- Test fixtures created programmatically via python-pptx
- Output format dispatch in CLI: only call report_terminal for terminal mode
- **Role classifier uses multi-signal heuristic**: shape name → placeholder index → content/position → font size. Maps to user-defined roles when available.
- **Background color checks slide.background.fill**, not individual shape fills (decorative shapes are not slide backgrounds)
- **Slide number regex** supports both plain digits and "N / M" format

## Test Results

- **pytest**: 28/28 passed
- **ruff**: all checks passed
- **E2E manual tests**: all 8 scenarios passed
  - `bad.pptx`: 9 issues (3E/6W), 5 fixable
  - `good.pptx`: 0 issues, passed
  - `--fix --dry-run`: file unchanged
  - `--fix`: 9 → 2 issues (only non-fixable warnings remain)
  - HTML report: valid, self-contained
  - JSON output: clean, no pollution

## PER-67 Fix Details (2026-04-12)

Three root causes addressed:
1. **P0 - Role classifier** (`classify_text_role`): Complete rewrite with 6-signal heuristic. Placeholder idx >= 10 → footer/slide_number. Font >= 40pt → section_number. Bottom area + small text → footer. Top area requires font > 14pt for title. User-defined roles supported.
2. **P1 - Background color** (`get_slide_background_color`): New function checks `slide.background.fill` instead of all shape fills. Eliminates ~308 false positives from decorative shapes (purple sidebars, card backgrounds, etc.)
3. **P2 - Page number regex**: Both `get_slide_number_shapes()` and `classify_text_role()` now match `^\d+\s*/\s*\d+$` (e.g. "4 / 13").

## GitHub Setup

- **Repo:** https://github.com/QiuYi111/ppt-lint (public)
- **Default branch:** main
- **Feature branch:** feat/ppt-lint-core (pushed)

## Remaining Work

- [ ] AI rule compilation end-to-end test (requires ANTHROPIC_API_KEY)
- [ ] Content margin checking (spacing.content_margin_pt)
- [ ] Slide number position checking
- [ ] Accent color detection
- [ ] More edge case tests (empty slides, corrupt files)
- [ ] Create PR from feat/ppt-lint-core to main
- [ ] User review and merge
- [ ] Validate fix against real template PPT (midterm_fixed.pptx) to measure false positive reduction
