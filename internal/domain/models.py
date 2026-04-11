"""Core data models for ppt-lint."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class FixAction:
    """Represents a fix that can be applied to a slide element."""

    def __init__(
        self,
        description: str,
        apply_fn: Callable[[], None],
    ) -> None:
        self.description = description
        self._apply_fn = apply_fn

    def apply(self) -> None:
        self._apply_fn()

    def __repr__(self) -> str:
        return f"FixAction({self.description!r})"


@dataclass
class LintIssue:
    """A single lint issue found in a presentation."""

    rule_id: str
    severity: Severity
    slide_index: int
    element_desc: str
    message: str
    fix: FixAction | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "rule_id": self.rule_id,
            "severity": self.severity.value,
            "slide_index": self.slide_index,
            "element_desc": self.element_desc,
            "message": self.message,
            "fixable": self.fix is not None,
        }
        if self.fix:
            d["fix_description"] = self.fix.description
        return d


@dataclass
class FontRule:
    family: str | None = None
    size_pt: float | None = None
    bold: bool | None = None
    color: str | None = None  # hex color


@dataclass
class ColorRules:
    allowed_text: list[str] = field(default_factory=list)
    allowed_background: list[str] = field(default_factory=list)
    accent: str | None = None


@dataclass
class AlignmentRules:
    title: str | None = None
    body: str | None = None
    slide_number: str | None = None


@dataclass
class SpacingRules:
    content_margin_pt: float | None = None
    line_spacing: float | None = None


@dataclass
class SlideNumberRules:
    visible: bool | None = None
    position: str | None = None
    font_size_pt: float | None = None


@dataclass
class ChartRules:
    require_title: bool | None = None
    title_font_size_pt: float | None = None
    require_axis_labels: bool | None = None


@dataclass
class AIRule:
    id: str
    description: str
    severity: Severity = Severity.WARNING


@dataclass
class RuleSet:
    """Complete rule configuration parsed from rules.yaml."""

    meta_name: str = ""
    meta_version: str = ""
    fonts: dict[str, FontRule] = field(default_factory=dict)
    colors: ColorRules = field(default_factory=ColorRules)
    alignment: AlignmentRules = field(default_factory=AlignmentRules)
    spacing: SpacingRules = field(default_factory=SpacingRules)
    slide_number: SlideNumberRules = field(default_factory=SlideNumberRules)
    charts: ChartRules = field(default_factory=ChartRules)
    ai_rules: list[AIRule] = field(default_factory=list)


@dataclass
class CompiledRuleSet:
    """Set of compiled checker functions ready to run against slides."""

    checkers: list[Callable] = field(default_factory=list)
