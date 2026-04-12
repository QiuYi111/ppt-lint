"""YAML rule parser with validation.

Domain layer — no python-pptx imports.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import (
    AIRule,
    AlignmentRules,
    ChartRules,
    ColorRules,
    FontRule,
    RuleSet,
    Severity,
    SlideNumberRules,
    SpacingRules,
)


class RuleParseError(Exception):
    """Raised when rule YAML is invalid."""


def parse_rules(path: str | Path) -> RuleSet:
    """Parse a rules.yaml file into a RuleSet."""
    p = Path(path)
    if not p.exists():
        raise RuleParseError(f"Rules file not found: {p}")

    with open(p, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise RuleParseError("Rules file must be a YAML mapping")

    return _parse_rule_dict(data)


def _parse_rule_dict(data: dict[str, Any]) -> RuleSet:
    rs = RuleSet()

    # Meta
    meta = data.get("meta", {})
    rs.meta_name = str(meta.get("name", ""))
    rs.meta_version = str(meta.get("version", ""))

    # Fonts
    fonts_raw = data.get("fonts", {})
    if isinstance(fonts_raw, dict):
        for role, fdict in fonts_raw.items():
            if isinstance(fdict, dict):
                rs.fonts[role] = FontRule(
                    family=fdict.get("family"),
                    size_pt=_to_float(fdict.get("size_pt")),
                    bold=_to_bool(fdict.get("bold")),
                    color=fdict.get("color"),
                )

    # Colors
    colors_raw = data.get("colors", {})
    if isinstance(colors_raw, dict):
        rs.colors = ColorRules(
            allowed_text=[str(c) for c in colors_raw.get("allowed_text", [])],
            allowed_background=[str(c) for c in colors_raw.get("allowed_background", [])],
            accent=colors_raw.get("accent"),
        )

    # Alignment
    align_raw = data.get("alignment", {})
    if isinstance(align_raw, dict):
        rs.alignment = AlignmentRules(
            title=align_raw.get("title"),
            body=align_raw.get("body"),
            slide_number=align_raw.get("slide_number"),
        )

    # Spacing
    spacing_raw = data.get("spacing", {})
    if isinstance(spacing_raw, dict):
        rs.spacing = SpacingRules(
            content_margin_pt=_to_float(spacing_raw.get("content_margin_pt")),
            line_spacing=_to_float(spacing_raw.get("line_spacing")),
        )

    # Slide number
    sn_raw = data.get("slide_number", {})
    if isinstance(sn_raw, dict):
        rs.slide_number = SlideNumberRules(
            visible=_to_bool(sn_raw.get("visible")),
            position=sn_raw.get("position"),
            font_size_pt=_to_float(sn_raw.get("font_size_pt")),
        )

    # Charts
    charts_raw = data.get("charts", {})
    if isinstance(charts_raw, dict):
        rs.charts = ChartRules(
            require_title=_to_bool(charts_raw.get("require_title")),
            title_font_size_pt=_to_float(charts_raw.get("title_font_size_pt")),
            require_axis_labels=_to_bool(charts_raw.get("require_axis_labels")),
        )

    # AI rules
    ai_raw = data.get("ai_rules", [])
    if isinstance(ai_raw, list):
        for ar in ai_raw:
            if isinstance(ar, dict):
                severity_str = str(ar.get("severity", "warning")).lower()
                severity = (
                    Severity(severity_str)
                    if severity_str in ("error", "warning", "info")
                    else Severity.WARNING
                )
                rs.ai_rules.append(
                    AIRule(
                        id=str(ar.get("id", "")),
                        description=str(ar.get("description", "")),
                        severity=severity,
                    )
                )

    return rs


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_bool(value: Any) -> bool | None:
    if value is None:
        return None
    return bool(value)
