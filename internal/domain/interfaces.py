"""Abstract interfaces for rule checkers and fixers.

Domain layer — no python-pptx imports.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import LintIssue


class RuleChecker(ABC):
    """Interface for a rule that can check a slide for issues."""

    @abstractmethod
    def check(self, slide: object, slide_index: int) -> list[LintIssue]:
        """Check a slide and return a list of issues found."""
        ...


class RuleFixer(ABC):
    """Interface for a rule that can fix issues on a slide."""

    @abstractmethod
    def fix(self, slide: object, slide_index: int) -> list[LintIssue]:
        """Apply fixes to a slide and return remaining unfixed issues."""
        ...
