# PRD: ppt-lint

## Overview

**ppt-lint** is a configuration-driven PowerPoint format checker and auto-fixer. Users describe formatting rules via YAML + natural language, and the tool compiles them into `python-pptx` checkers or Claude API calls, producing lint reports with one-click fix capability.

## Target Users

- Graduate students and researchers who need to comply with thesis committee formatting guidelines for presentations
- Anyone who needs consistent PPT formatting across a team

## Core Features

### 1. Rule Book (rules.yaml)

A YAML configuration file that defines formatting rules in two forms:

- **Primitive rules** (key-value): Cover 90% of common formatting rules — fonts, colors, alignment, spacing, slide numbers, charts
- **AI rules** (natural language): For complex/ambiguous rules that can't be expressed as primitives — compiled once via Claude API, cached as Python functions

### 2. Rule Compiler

- Parses `rules.yaml` and generates check/fix functions
- Primitive rules → direct `python-pptx` code generation
- AI rules → Claude API call (one-time), result cached in `.ppt-lint-cache/`
- Cache invalidation on rule description change (content hash)

### 3. Lint Engine

- Runs all compiled rules against a `.pptx` file
- Collects `LintIssue` objects with rule_id, severity, slide_index, element_desc, message, and optional fix callable
- Outputs report in multiple formats: terminal (colored), JSON, HTML

### 4. Auto-Fix

- `--fix` flag applies all safe fixes automatically
- `--fix --dry-run` previews changes without modifying the file
- Fixable primitives: font family/size/bold/color, background color, alignment, spacing, line spacing, slide number visibility/position
- Non-fixable: chart title/axis labels (report only)

### 5. CLI Interface

```bash
ppt-lint check presentation.pptx --rules rules.yaml
ppt-lint check presentation.pptx --rules rules.yaml --fix
ppt-lint check presentation.pptx --rules rules.yaml --fix --dry-run
ppt-lint check presentation.pptx --rules rules.yaml --output json
ppt-lint check presentation.pptx --rules rules.yaml --output html --report report.html
ppt-lint init                          # Scaffold a sample rules.yaml
```

## Architecture

```
rules.yaml
    ↓
Compiler (compiler.py)
    ↓
┌─────────────────────┐
│  Script rules (fast) │   → python-pptx direct execution
│  AI rules (cached)   │   → Compiled Python functions
└─────────────────────┘
    ↓
Lint Engine (engine.py)
    ↓
Report (terminal/json/html)  →  [confirm]  →  Fix
```

### Project Structure

```
ppt-lint/
├── cmd/
│   └── ppt_lint.py          # CLI entry point (click/typer)
├── internal/
│   ├── domain/
│   │   ├── models.py         # LintIssue, Rule, CompiledRuleSet, etc.
│   │   ├── interfaces.py     # Abstract rule checker/fixer interfaces
│   │   └── rules.py          # Rule parsing and validation
│   └── infrastructure/
│       ├── pptx_adapter.py   # python-pptx file operations
│       ├── compiler.py       # Rule compilation (primitive + AI)
│       ├── engine.py         # Lint engine orchestrator
│       ├── reporter.py       # Output formatting (terminal/json/html)
│       ├── fixer.py          # Auto-fix orchestrator
│       └── ai_cache.py       # Claude API + cache management
├── tests/
│   ├── test_models.py
│   ├── test_compiler.py
│   ├── test_engine.py
│   ├── test_fixer.py
│   ├── test_reporter.py
│   └── fixtures/             # Sample .pptx files for testing
├── scripts/
│   └── create_test_pptx.py   # Helper to create test presentations
├── rules.yaml                # Example rule book
├── pyproject.toml
└── Makefile
```

## Primitive Rules

| Key | Check Content | Auto-Fix |
|-----|--------------|----------|
| `fonts.*.family` | Font family match | ✅ |
| `fonts.*.size_pt` | Font size match | ✅ |
| `fonts.*.bold` | Bold state match | ✅ |
| `fonts.*.color` | Text color in whitelist | ✅ |
| `colors.allowed_background` | Background color compliance | ✅ |
| `colors.accent` | Accent color is the specified one | ✅ |
| `alignment.*` | Text alignment | ✅ |
| `spacing.content_margin_pt` | Content area margin | ✅ |
| `spacing.line_spacing` | Line spacing multiplier | ✅ |
| `slide_number.visible` | Slide number exists | ✅ |
| `slide_number.position` | Slide number position | ✅ |
| `charts.require_title` | Chart has title | ⚠️ report only |
| `charts.require_axis_labels` | Chart has axis labels | ⚠️ report only |

## AI Rule Compilation

- Prompt template generates a Python function from natural language description
- Function signature: `def check_{id}(slide, slide_index) -> list[LintIssue]`
- Cache stored in `.ppt-lint-cache/` keyed by rule ID + description hash
- Claude API call uses `ANTHROPIC_API_KEY` environment variable

## Technical Constraints

- Python 3.10+
- `python-pptx` for PPTX manipulation
- `click` or `typer` for CLI
- `pyyaml` for YAML parsing
- `anthropic` for Claude API (optional — only needed for AI rules)
- `rich` for terminal output formatting
- No external database needed

## Testing Strategy

- Unit tests for compiler, engine, fixer, reporter
- Integration tests with real .pptx fixtures
- Test fixtures created programmatically via `create_test_pptx.py`
- Cover: correct detection, false positives, fix accuracy, edge cases (empty slides, missing elements, etc.)

## Success Criteria

1. `ppt-lint check test.pptx --rules rules.yaml` runs and produces a report
2. Primitive rules correctly detect and fix formatting violations
3. AI rules compile and cache correctly
4. `--fix` mode modifies the file and subsequent check passes
5. JSON and HTML report output works
6. `ppt-lint init` generates a usable starter rules.yaml
