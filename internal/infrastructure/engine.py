"""Lint engine — runs compiled rules against a presentation."""

from __future__ import annotations

import logging
from pathlib import Path

from pptx import Presentation

from internal.domain.models import CompiledRuleSet, LintIssue, Severity

logger = logging.getLogger(__name__)


class LintResult:
    """Result of a lint run."""

    def __init__(self, issues: list[LintIssue], file_path: str) -> None:
        self.issues = issues
        self.file_path = file_path

    @property
    def errors(self) -> list[LintIssue]:
        return [i for i in self.issues if i.severity == Severity.ERROR]

    @property
    def warnings(self) -> list[LintIssue]:
        return [i for i in self.issues if i.severity == Severity.WARNING]

    @property
    def infos(self) -> list[LintIssue]:
        return [i for i in self.issues if i.severity == Severity.INFO]

    @property
    def fixable(self) -> list[LintIssue]:
        return [i for i in self.issues if i.fix is not None]

    @property
    def total(self) -> int:
        return len(self.issues)

    @property
    def passed(self) -> bool:
        return self.total == 0


def lint_file(
    file_path: str | Path,
    compiled_rules: CompiledRuleSet,
) -> LintResult:
    """Lint a PPTX file using compiled rules."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    prs = Presentation(str(path))
    all_issues: list[LintIssue] = []

    for slide_index, slide in enumerate(prs.slides):
        for checker in compiled_rules.checkers:
            try:
                issues = checker(slide, slide_index)
                if issues:
                    all_issues.extend(issues)
            except Exception as e:
                logger.error(f"Error running checker on slide {slide_index}: {e}")

    return LintResult(issues=all_issues, file_path=str(path))


def fix_file(
    file_path: str | Path,
    compiled_rules: CompiledRuleSet,
    output_path: str | Path | None = None,
    dry_run: bool = False,
) -> LintResult:
    """Lint and fix a PPTX file.

    If dry_run is True, only reports what would be fixed without modifying the file.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    prs = Presentation(str(path))

    # First pass: check all slides to populate fixes
    all_issues: list[LintIssue] = []
    fix_actions: list[tuple[int, object, object]] = []  # (slide_index, issue, shape_ref)

    for slide_index, slide in enumerate(prs.slides):
        for checker in compiled_rules.checkers:
            try:
                issues = checker(slide, slide_index)
                for issue in issues:
                    if issue.fix and not dry_run:
                        fix_actions.append((slide_index, issue, slide))
                    all_issues.append(issue)
            except Exception as e:
                logger.error(f"Error running checker on slide {slide_index}: {e}")

    # Apply fixes (not dry_run)
    applied = 0
    if not dry_run:
        for slide_index, issue, slide in fix_actions:
            try:
                issue.fix.apply()
                applied += 1
            except Exception as e:
                logger.error(f"Failed to apply fix on slide {slide_index}: {e}")

    # Save if fixes were applied
    if not dry_run and applied > 0:
        out = Path(output_path) if output_path else path
        prs.save(str(out))
        logger.info(f"Applied {applied} fixes, saved to {out}")

    return LintResult(issues=all_issues, file_path=str(path))
